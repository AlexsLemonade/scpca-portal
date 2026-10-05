"""Resolving the spec's discriminated variants out of the generated types."""

import ast
import enum
import re
from pathlib import Path
from typing import Literal, Union

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

import pydantic

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.schema import _variants
from scpca_portal.federation.ccdi.schema._models import ModelsGatewayLink, ResponsesErrors


class VariantsOfTests(SimpleTestCase):
    def test_resolves_a_union_that_exists_as_an_attribute(self):
        self.assertEqual(
            set(_variants.variants_of(ResponsesErrors, "errors")),
            {
                "InvalidRoute",
                "InvalidParameters",
                "NotFound",
                "UnshareableData",
                "UnsupportedField",
            },
        )

    def test_resolves_a_union_generated_as_its_own_type(self):
        # A `RootModel`, reached through the default `root` field rather than a
        # named attribute — the other shape the generator produces.
        self.assertEqual(
            set(_variants.variants_of(ModelsGatewayLink)),
            {"Direct", "Approximate", "Informational", "MailTo"},
        )

    def test_no_numbered_generated_class_is_named_anywhere_in_the_node(self):
        """
        `ResponsesErrorKind9` is `NotFound` only because it is ninth in the
        spec's `oneOf`. Naming it would keep working, silently, while meaning
        something else after the spec inserts or reorders a variant — so the
        whole node is scanned, not just the module that resolves them.
        """
        numbered = re.compile(r"^(?:Models|Responses)[A-Za-z]+\d+$")
        node = Path(schema.__file__).parent.parent

        def referenced(tree):
            """Identifiers only — prose naming one as a warning is not a use."""
            for item in ast.walk(tree):
                if isinstance(item, ast.Name):
                    yield item.id, item.lineno
                elif isinstance(item, ast.Attribute):
                    yield item.attr, item.lineno
                elif isinstance(item, ast.alias):
                    yield item.name, getattr(item, "lineno", 0)

        offenders = [
            f"{path.relative_to(node)}:{line}: {name}"
            for path in sorted(node.rglob("*.py"))
            if path.name != "_models.py"
            for name, line in referenced(ast.parse(path.read_text()))
            if numbered.match(name)
        ]

        self.assertEqual(offenders, [], "resolve these by discriminator instead")


class BuildTests(SimpleTestCase):
    def test_the_caller_cannot_override_the_discriminator(self):
        """
        `build` sets the discriminator from the variant it resolved.

        Reaching that through `error_kind` is impossible — its signature
        captures `kind`. The case that can go wrong is a union discriminated by
        something else, which the spec has one of on `status`: there the
        discriminator is a declared field, so it survives the undeclared-field
        check and would otherwise win.
        """

        class Open(pydantic.BaseModel):
            status: Literal["Open"]

        class Shut(pydantic.BaseModel):
            status: Literal["Shut"]

        class Holder(pydantic.BaseModel):
            variants: Union[Open, Shut]

        variants = _variants.variants_of(Holder, "variants", discriminator="status")

        with self.assertRaises(ImproperlyConfigured) as raised:
            _variants.build(variants, "Open", "gate", discriminator="status", status="Shut")

        self.assertIn("set from the variant", str(raised.exception))

    def test_every_member_of_the_union_must_resolve(self):
        # A discriminator the generator emits as something other than a Literal
        # would otherwise drop that variant silently, and the kind would go
        # missing at import — surfacing as a 500 the first time it is needed.
        class Kinds(str, enum.Enum):
            first = "first"

        class First(pydantic.BaseModel):
            kind: Kinds = Kinds.first

        class Second(pydantic.BaseModel):
            kind: Kinds = Kinds.first

        class Holder(pydantic.BaseModel):
            variants: Union[First, Second]

        with self.assertRaises(ImproperlyConfigured) as raised:
            _variants.variants_of(Holder, "variants")

        self.assertIn("2 variants but only 0 resolve", str(raised.exception))

    def test_an_unknown_kind_names_the_kinds_the_spec_offers(self):
        with self.assertRaises(ImproperlyConfigured) as raised:
            schema.error_kind("Sideways", "...")

        self.assertIn("NotFound", str(raised.exception))

    def test_a_field_the_variant_does_not_declare_is_rejected(self):
        # Pydantic would ignore it, leaving an error body quietly missing the
        # field that explains it.
        with self.assertRaises(ImproperlyConfigured) as raised:
            schema.error_kind("NotFound", "...", entity="x", method="GET")

        self.assertIn("does not take method", str(raised.exception))

    def test_a_missing_required_field_is_rejected(self):
        with self.assertRaises(pydantic.ValidationError):
            schema.error_kind("NotFound", "...")
