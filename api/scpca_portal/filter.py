from django.contrib.postgres.fields import ArrayField
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
def build_auto_filterset(model, include_fields=None, extra_filters=None):
    """
    Introspects a model and builds a FilterSet with sensible lookup expressions
    per field type. ArrayFields get icontains via ArrayFieldContainsFilter.

    Args:
        model:          The Django model class to build a FilterSet for.
        include_fields: Optional allowlist of field names. If omitted, all
                        supported field types are included. Always use this
                        to keep your public API surface intentional.
        extra_filters:  Optional dict of additional filter instances to mix in,
                        e.g. {"in_stock": MyCustomFilter(...)}.
    """

    declared_filters = {}
    meta_fields = {}

    for field in model._meta.get_fields():
        # Skip reverse relations and ManyToMany
        if field.is_relation and (field.one_to_many or field.many_to_many):
            continue
        if include_fields and field.name not in include_fields:
            continue

        # ArrayField: use custom filter, one filter per field
        if isinstance(field, ArrayField):
            declared_filters[field.name] = ArrayFieldContainsFilter(field_name=field.name)
            continue

        # Standard field types: use dict-style meta fields for multi-lookup support
        for field_type, lookups in FILTER_LOOKUPS.items():
            if isinstance(field, field_type):
                meta_fields[field.name] = lookups
                break

    if extra_filters:
        declared_filters.update(extra_filters)

    meta = type("Meta", (), {"model": model, "fields": meta_fields})
    attrs = {"Meta": meta, **declared_filters}

    return type(f"{model.__name__}AutoFilterSet", (filters.FilterSet,), attrs)
