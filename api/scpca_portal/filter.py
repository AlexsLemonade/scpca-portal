from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import FieldDoesNotExist
from django.db import models

import django_filters
from django_filters import rest_framework as filters

# Lookup expressions per field type
FILTER_LOOKUPS = {
    models.BigIntegerField: ["exact", "gte", "lte", "gt", "lt", "in"],
    models.BooleanField: ["exact"],
    models.CharField: ["exact", "icontains", "istartswith"],
    models.DateTimeField: ["exact", "gte", "lte", "date"],
    models.EmailField: ["exact", "icontains", "istartswith"],
    models.IntegerField: ["exact", "gte", "lte", "gt", "lt", "in"],
    models.JSONField: ["exact", "in"],
    models.PositiveIntegerField: ["exact", "gte", "lte", "gt", "lt", "in"],
    models.TextField: ["exact", "icontains"],
    # Relation fields
    models.ForeignKey: ["exact", "in"],
    models.ManyToManyField: ["exact", "in"],
    models.OneToOneField: ["exact", "in"],
}


# Custom filter for Postgres ArrayFields
class ArrayFieldContainsFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """
    Accepts comma-separated values and applies icontains per term (AND logic).
    e.g. ?diagnoses=Neuroblastoma,Glioma matches projects containing both.
    NOTE: Swap the loop for Q objects if you want OR logic instead.
    """

    def filter(self, qs, value):
        if not value:
            return qs
        for term in value:
            qs = qs.filter(**{f"{self.field_name}__icontains": term.strip()})
        return qs


# Filterset Factory
def build_auto_filterset(
    model,
    auto_fields: list[str] = [],
    extra_fields: dict[str, list[str]] = None,
    extra_filters: dict = None,
):
    """
    Introspects a model and builds a FilterSet with sensible lookup expressions
    per field type. ArrayFields get icontains via ArrayFieldContainsFilter.
    Args:
        model:          The Django base model class to build a FilterSet for.
        auto_fields:    Optional allowlist of field names, including relations
                        with ORM lookup separator (e.g., 'project__pi_name').
                        Use this to keep your public API surface intentional.
        extra_fields:   Override default lookup expressions of fields as needed.
                        e.g., {'project__scpca_id': ['exact']}.
        extra_filters:  Additional filter instances to mix in.
                        e.g. {"in_stock": MyCustomFilter(...)}.
    """
    declared_filters = {}
    meta_fields = {}
    LOOKUP_SEPARATOR = "__"

    base_model_fields = {field.name: field for field in model._meta.get_fields()}

    for field_name in auto_fields:
        # Handle relation fields using ORM lookup separator
        if LOOKUP_SEPARATOR in field_name:
            name_parts = field_name.split(LOOKUP_SEPARATOR)
            relation_field_name = name_parts[-1]

            # Traverse the relationship paths via related_name
            related_name_paths = name_parts[:-1]
            current_model = model
            current_model_fields = base_model_fields

            for related_name in related_name_paths:
                # Ensure the related_name and its related_model exists on the current model
                try:
                    related_name_field = current_model_fields[related_name]
                    # Update the model references for the next iteration
                    current_model = related_name_field.related_model
                    current_model_fields = {
                        field.name: field for field in current_model._meta.get_fields()
                    }
                except (KeyError, AttributeError):
                    raise KeyError(
                        f"{related_name} or its related_model does not exist on {current_model}."
                    )

            # Retrieve the field type of relation_field_name defined in its related_model
            try:
                field = current_model._meta.get_field(relation_field_name)
            except FieldDoesNotExist:
                raise FieldDoesNotExist(f"{relation_field_name} does not exist on {current_model}.")

        else:
            # Handle local fields define in the base model class
            try:
                field = base_model_fields[field_name]
            except KeyError:
                raise KeyError(f"{field_name} does not exist on {model}.")

        # ArrayField: use custom filter, one filter per field
        if isinstance(field, ArrayField):
            declared_filters[field_name] = ArrayFieldContainsFilter(field_name=field_name)
            continue

        # Assign default expressions to use dict-style meta fields for multi-lookup support
        for field_type, lookups in FILTER_LOOKUPS.items():
            if isinstance(field, field_type):
                meta_fields[field_name] = lookups
                break

    if extra_fields:
        meta_fields.update(extra_fields)

    if extra_filters:
        declared_filters.update(extra_filters)

    meta = type("Meta", (), {"model": model, "fields": meta_fields})
    attrs = {"Meta": meta, **declared_filters}

    return type(f"{model.__name__}AutoFilterSet", (filters.FilterSet,), attrs)
