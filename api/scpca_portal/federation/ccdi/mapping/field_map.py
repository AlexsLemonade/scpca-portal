"""
The machinery that turns an entity's getters into a CCDI `metadata` object.

A `FieldMap` holds the getters for one entity, keyed by the CCDI field each one
populates. Getters return plain CCDI values; everything about the shape those
values are emitted in — which `field.unowned.*` wrapper, whether it holds a list
— is derived from the generated type, so no mapping ever names a generated class
or can drift from the spec.
"""

import inspect
import re
import types
from functools import cache
from types import MappingProxyType
from typing import Any, Callable, Union, get_args, get_origin, get_type_hints

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.federation.ccdi.schema import FieldStandard, HarmonizedFieldDescription, _models

logger = get_and_configure_logger(__name__)

WIKI = "https://github.com/CBIIT/ccdi-federation-api/wiki"

# Every mapping is named for the CCDI field it populates, behind this prefix, so
# the field is still derived from the name rather than looked up in a table that
# could drift from it.
#
# The prefix is there because a CCDI field name is not always a name Python can
# spare: `File.type` shadows the builtin and is a soft keyword on 3.12. It also
# keeps an entity's getters greppable as a set, apart from the crosswalk tables
# that sit beside them in the same module.
GETTER_PREFIX = "get_"


# The caDSR CDE a field follows, as the spec writes it into that field's
# description: a bold marker naming the CDE, and a `Link:` block holding its URL.
CDE_MARKER = re.compile(r"\*\*`(?P<authority>caDSR) CDE \d+ v?[\d.]+`\*\*")
CDE_LINK = re.compile(r"Link:\s*<(?P<url>https?://[^>]+)>")

# Either of these in a description means the spec is documenting a standard for
# that field. Deliberately broader than what `standard_of` parses, and kept
# separate from it: if CCDI restyles one marker the other still fires, so the
# field looks standardized here while failing to parse, which is what
# `test_field_map` trips on. A trigger that matched the parser exactly could only
# ever agree with it.
#
# Not the bare word "CDE": `associated_diagnosis_categories` says its vocabulary
# is "defined by the CCDI CDEs" as prose, with no standard of its own to emit.
STANDARD_MARKERS = ("caDSR", "Link:")


def description_of(wrapper: type) -> str:
    """The spec's prose for a harmonized field's value."""
    value = getattr(wrapper, "model_fields", {}).get("value")

    return (value.description or "") if value else ""


def standard_of(wrapper: type) -> FieldStandard | None:
    """
    The published standard the spec documents for a field, or `None`.

    Derived rather than declared, for the same reason the field's wrapper and its
    list-ness are: the CDE and its URL are already in the generated type, so a
    copy typed at a call site could only ever drift from the spec. A field the
    spec marks as standardized but writes in a shape this cannot read is caught
    by a test rather than silently losing its standard.
    """
    description = description_of(wrapper)
    marker = CDE_MARKER.search(description)
    link = CDE_LINK.search(description)

    if not (marker and link):
        return None

    return FieldStandard(name=marker.group("authority"), url=link.group("url"))


def without_none(hint: Any) -> Any:
    """The type behind an `X | None`, or the hint unchanged if it isn't one."""
    if get_origin(hint) not in (Union, types.UnionType):
        return hint

    members = [arg for arg in get_args(hint) if arg is not type(None)]

    return members[0] if len(members) == 1 else hint


def shape_of(hint: Any) -> tuple[type, bool]:
    """
    The shape a CCDI value is emitted in: its field wrapper, and whether the key
    holds a list of them.

    `X | None` → (X, False). `list[X] | None` → (X, True). `list[X]` → (X, True).
    """
    hint = without_none(hint)

    if get_origin(hint) is list:
        return get_args(hint)[0], True

    return hint, False


def is_field_wrapper(wrapper: type) -> bool:
    """Harmonized fields are `{"value": …}` objects; depositions and unharmonized aren't."""
    return "value" in getattr(wrapper, "model_fields", {})


# `get_type_hints` resolves every annotation against the 16,000-line generated
# module, at roughly half a millisecond a call. `build()` needs this once per
# entity, so a page of 500 samples would otherwise spend a quarter of a second
# re-deriving an answer that cannot change while the process runs. Cached, it
# happens once per entity type — and the result is handed out read-only, because
# a caller that mutated a cached dict would poison every build after it.
@cache
def field_shapes(metadata_type: type) -> MappingProxyType:
    """The shape of every CCDI key on one entity's metadata, keyed by field name."""
    return MappingProxyType(
        {
            name: shape_of(hint)
            for name, hint in get_type_hints(metadata_type, globalns=vars(_models)).items()
        }
    )


def wrap(value: Any, shape: tuple[type, bool]) -> Any:
    """
    Put a CCDI value inside the shape the spec emits it in.

    Only harmonized `{"value": …}` fields reach here, because those are the only
    ones the registration decorators will accept.

    Raises rather than coercing, so that a getter returning the wrong shape is
    contained and logged by `FieldMap.build` instead of reaching a response. A
    bare string is the case worth naming: iterating one would emit a field per
    character, and the spec's free-text list fields would accept it.
    """
    wrapper, many = shape

    if value is None:
        return None

    if many and not isinstance(value, (list, tuple)):
        raise TypeError(
            f"{wrapper.__name__} is a list field; got {type(value).__name__} {value!r}."
        )

    if many:
        return [wrapper(value=each) for each in value]

    return wrapper(value=value)


class FieldMap:
    """The getters that populate one CCDI entity's metadata."""

    def __init__(self, name: str, metadata_type: type):
        if name not in metadata_type.__name__.lower():
            raise ValueError(f"{metadata_type.__name__} is not the metadata for a CCDI {name}.")

        self.name = name
        self.metadata_type = metadata_type
        self.getters: dict[str, Callable] = {}

    def harmonized(self, getter: Callable) -> Callable:
        """
        Register a getter as the mapping for the CCDI field its name carries.

            @Sample.FIELDS.harmonized
            def get_disease_phase(scpca): ...

        A plain decorator, written without parentheses. It takes no optional
        argument, so there is exactly one correct spelling and the other is
        rejected on arity, before any of this runs — the version that took an
        optional `standard=` could be written bare, and silently registered
        nothing at all.

        Mapping a field also describes it on `/metadata/fields`, including the
        standard it follows, which is read off the spec rather than declared here.
        """
        field = self._field_for(getter)

        self._check_shape(getter)

        shape = field_shapes(self.metadata_type).get(field)

        if shape is None:
            raise ValueError(
                f"CCDI {self.name} has no '{field}' field. The spec's fields are: "
                f"{', '.join(field_shapes(self.metadata_type))}."
            )

        if not is_field_wrapper(shape[0]):
            raise ValueError(
                f"CCDI {self.name}'s '{field}' is not a harmonized field, so it has "
                "no wiki page and cannot be described as one."
            )

        if field in self.getters:
            raise ValueError(
                f"CCDI {self.name}'s '{field}' is already mapped by "
                f"{self.getters[field].__qualname__}. One field, one mapping — "
                "edit that one rather than registering a second."
            )

        self.getters[field] = getter

        return getter

    def _check_shape(self, getter: Callable) -> None:
        """
        That the getter can actually be run the way `build` runs it.

        A getter that cannot take one record does not fail loudly — `build`
        contains it, so the field degrades to null and logs, every time, for
        every record. It stays advertised on `/metadata/fields` as a field the
        node populates while emitting nothing, which is the same silent
        mapped-but-dead state the decorator's own spelling used to produce.
        """
        if not callable(getter):
            raise ValueError(
                f"A CCDI {self.name} mapping must be callable — {getter!r} is not. "
                "A `classmethod` object is the usual way to land here; a plain "
                "function or a `staticmethod` works."
            )

        try:
            inspect.signature(getter).bind(None)
        except TypeError as error:
            raise ValueError(
                f"A CCDI {self.name} mapping takes one argument, the entity its "
                f"getters are handed — {getattr(getter, '__name__', getter)!r} does not: {error}."
            )

    def _field_for(self, getter: Callable) -> str:
        """The CCDI field a getter's name carries, with the prefix taken off."""
        name = getattr(getter, "__name__", None)

        if name is None:
            raise ValueError(
                f"A CCDI {self.name} mapping must be a named function — "
                f"{getter!r} has no __name__ to map it to a field."
            )

        if not name.startswith(GETTER_PREFIX):
            raise ValueError(
                f"A CCDI {self.name} mapping is named for the field it populates, behind "
                f"'{GETTER_PREFIX}' — rename '{name}' to '{GETTER_PREFIX}{name}'."
            )

        return name.removeprefix(GETTER_PREFIX)

    def wiki_url(self, field: str) -> str:
        """Where the CCDI wiki documents this field."""
        return f"{WIKI}/{self.name.capitalize()}-Metadata-Fields#{field}"

    def build(self, scpca) -> Any:
        """
        Every CCDI key, from the getter registered for it or null.

        Only keys the spec requires are emitted when unmapped: a harmonized key is
        required-but-nullable, so a null is a legitimate "we have nothing", while
        an optional key like `unharmonized` is not nullable and has to be absent.
        """
        values = {}

        for field, shape in field_shapes(self.metadata_type).items():
            getter = self.getters.get(field)

            if getter is None:
                if self.metadata_type.model_fields[field].is_required():
                    values[field] = None
                continue

            try:
                values[field] = wrap(getter(scpca), shape)
            except Exception as error:
                # One unmappable record degrades its own field, not the response.
                # Logged without a traceback: a mapping that fails does so for
                # every record it touches, and a page of them should stay legible.
                logger.error(
                    "CCDI %s field %s could not be mapped: %r",
                    self.name,
                    field,
                    error,
                )
                values[field] = None

        return self.metadata_type(**values)

    def describe(self) -> list[HarmonizedFieldDescription]:
        """What `/metadata/fields` reports for this entity."""
        return [
            HarmonizedFieldDescription(
                harmonized=True,
                path=field,
                wiki_url=self.wiki_url(field),
                standard=standard_of(wrapper),
            )
            for field, (wrapper, _) in field_shapes(self.metadata_type).items()
            if field in self.getters
        ]
