"""
Building the generated types the spec expresses as discriminated variants.

Error kinds, gateways and links are `oneOf` lists of anonymous objects selected
by a discriminator property, so the generator has no name to give them and
numbers them instead: `ResponsesErrorKind9` is `NotFound` only because it is
ninth in the list. Referring to that number would keep working, silently, while
meaning something else the next time the spec inserts or reorders a variant.

So nothing here names a numbered class. Each variant is looked up by the
discriminator value the spec itself declares, which makes a renumbering a no-op,
and a variant the spec no longer offers a loud error naming what it does offer.
The unpleasant `typing` introspection is confined to this module.

"Variant" is the upstream term: the spec is generated from Rust, where these are
`#[serde(tag = "kind")]` enum variants. It is unrelated to "dataset variant",
which is a CCDL configuration.
"""

import types
from typing import Annotated, Any, Union, get_args, get_origin

from django.core.exceptions import ImproperlyConfigured

from scpca_portal.federation.ccdi.schema._models import ResponsesErrors


def _union_members(annotation: Any) -> tuple:
    """Strip `Annotated`, list and `Optional` wrappers to reach the variant union."""
    while True:
        origin = get_origin(annotation)

        if origin is Annotated:
            annotation = get_args(annotation)[0]
        elif origin in (list, set, tuple):
            annotation = get_args(annotation)[0]
        elif origin in (Union, types.UnionType):
            members = [member for member in get_args(annotation) if member is not type(None)]
            if len(members) == 1:
                annotation = members[0]
            else:
                return tuple(members)
        else:
            return (annotation,)


def variants_of(model: type, field: str = "root", discriminator: str = "kind") -> dict[str, type]:
    """
    The variants of one discriminated union, keyed by their discriminator value.

    `field` names where the union lives: a union generated as its own type is a
    `RootModel`, while one that only appears as somebody's attribute is read off
    that attribute.
    """
    members = _union_members(model.model_fields[field].annotation)
    found = {}

    for member in members:
        if not (isinstance(member, type) and hasattr(member, "model_fields")):
            continue

        declared = member.model_fields.get(discriminator)
        if declared is None:
            continue

        values = get_args(declared.annotation)
        if values:
            found[values[0]] = member

    # Every member must have yielded a value. A discriminator the generator
    # emits as something other than a `Literal` — an Enum, say — would otherwise
    # drop that variant here and surface as a 500 the first time something asks
    # for it, which is the opposite of what this module is for.
    if len(found) != len(members):
        raise ImproperlyConfigured(
            f"{model.__name__}.{field} has {len(members)} variants but only "
            f"{len(found)} resolve by '{discriminator}': {', '.join(sorted(found))}."
        )

    return found


def build(variants: dict[str, type], kind: str, label: str, discriminator: str = "kind", **fields):
    """
    Build one variant by its discriminator value.

    The discriminator is set from the variant that was resolved rather than
    passed in, so a variant cannot end up declaring a kind other than the one it
    was looked up by. A field the variant does not declare raises rather than
    being dropped: pydantic would ignore it, and an error body quietly missing
    the field that explains it is worse than no body at all.
    """
    variant = variants.get(kind)

    if variant is None:
        raise ImproperlyConfigured(
            f"The CCDI spec has no '{kind}' {label}; it offers {', '.join(sorted(variants))}."
        )

    if discriminator in fields:
        raise ImproperlyConfigured(
            f"The {label} discriminator '{discriminator}' is set from the variant that "
            f"was resolved, not passed in; drop it from the call."
        )

    undeclared = set(fields) - set(variant.model_fields)

    if undeclared:
        raise ImproperlyConfigured(
            f"The '{kind}' {label} does not take {', '.join(sorted(undeclared))}; "
            f"it takes {', '.join(sorted(set(variant.model_fields) - {discriminator}))}."
        )

    return variant(**{discriminator: kind, **fields})


# The errors a response can carry: InvalidRoute, InvalidParameters, NotFound,
# UnshareableData, UnsupportedField.
ERROR_KINDS = variants_of(ResponsesErrors, "errors")


def error_kind(kind: str, message: str, **fields):
    """One entry of an `errors` array, by the kind the spec names it."""
    return build(ERROR_KINDS, kind, "error kind", message=message, **fields)
