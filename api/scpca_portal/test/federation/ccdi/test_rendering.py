"""Every node response goes through one renderer."""

import ast
from pathlib import Path

from django.test import SimpleTestCase

import scpca_portal.federation.ccdi.views as views

VIEWS = Path(views.__file__).parent


class RenderingTests(SimpleTestCase):
    """
    `schema.dump` is the node's only renderer, and the views must not go around
    it.

    A plain `model_dump` emits keys the spec rejects: `metadata.unharmonized` is
    optional and never marked nullable, but the generated type defaults it to
    `None`, so it comes out as an explicit null. `exclude_unset` is what drops
    it, and `dump` is where that lives.

    Nothing enforces this at runtime, so it is asserted over the source: the
    failure mode is a view that renders correctly today and stops doing so when
    a key it emits becomes optional.
    """

    def view_modules(self):
        for path in sorted(VIEWS.glob("*.py")):
            if path.name != "__init__.py":
                yield path

    def test_no_view_renders_with_a_bare_model_dump(self):
        offenders = []

        for path in self.view_modules():
            tree = ast.parse(path.read_text())

            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "model_dump"
                ):
                    offenders.append(f"{path.name}:{node.lineno}")

        self.assertEqual(offenders, [], "these render around `schema.dump`")

    def test_every_view_that_builds_a_response_body_uses_dump(self):
        # The other direction: a module that returns a Response built from a
        # spec type should be calling the renderer, not hand-rolling a dict.
        rendering = []

        for path in self.view_modules():
            source = path.read_text()
            if "Response(" in source and "schema.dump(" in source:
                rendering.append(path.name)

        self.assertEqual(
            sorted(rendering),
            ["info.py", "metadata_fields.py", "namespace.py", "organization.py", "sample.py"],
        )
