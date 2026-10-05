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

    def test_every_view_that_returns_a_response_also_calls_the_renderer(self):
        """
        The positive direction, as a relationship rather than a list of
        filenames — a list would need editing whenever a view is added, which
        is noise rather than signal.

        A module that builds a response without ever calling `schema.dump` has
        gone around it, however the body was assembled. Matched on the call
        itself rather than on source text, so `HttpResponse` — which the schema
        view returns, and which carries a document rather than a spec type —
        is not mistaken for one.
        """
        offenders = []

        for path in self.view_modules():
            tree = ast.parse(path.read_text())
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            renders = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }

            if calls & {"Response", "JsonResponse"} and "dump" not in renders:
                offenders.append(path.name)

        self.assertEqual(offenders, [], "these return a response without `schema.dump`")

    def test_no_view_hand_rolls_a_response_body(self):
        """
        A body built as a literal has gone around the renderer, so nothing
        applies `exclude_unset` to it.

        Both the positional and the `data=` spellings are checked: `data` is
        `Response`'s own first parameter, so the keyword form is the natural
        way to write it and was missed by an earlier version of this test.
        """
        offenders = []
        literal = (ast.Dict, ast.List, ast.DictComp, ast.ListComp)

        for path in self.view_modules():
            for node in ast.walk(ast.parse(path.read_text())):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                    continue

                if node.func.id not in ("Response", "JsonResponse"):
                    continue

                given = list(node.args) + [
                    keyword.value for keyword in node.keywords if keyword.arg == "data"
                ]

                if any(isinstance(value, literal) for value in given):
                    offenders.append(f"{path.name}:{node.lineno}")

        self.assertEqual(offenders, [], "these build a response body without `schema.dump`")
