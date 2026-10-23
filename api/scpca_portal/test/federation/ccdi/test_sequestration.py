"""
Architectural boundary checks for the CCDI federation node.

The node must not import the v1 API layer (views/serializers), and the v1 API
layer must not import the node. Reading shared models/enums/utils is allowed.
"""

import ast
from pathlib import Path

from django.test import SimpleTestCase

import scpca_portal.urls
from scpca_portal.federation import ccdi

# The v1 API layer the node must not couple to. Reading shared
# models/enums/utils read-only is allowed, so those are not forbidden.
FORBIDDEN_IMPORT_PREFIXES = (
    "scpca_portal.views",
    "scpca_portal.serializers",
)

SCPCA_PORTAL_DIR = Path(scpca_portal.urls.__file__).parent
CCDI_PACKAGE_DIR = Path(ccdi.__file__).parent


def imported_modules(source_path):
    """Yield the module target of every top-level absolute import in a file."""
    tree = ast.parse(source_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module


class CCDISequestrationTests(SimpleTestCase):
    def test_node_does_not_import_v1_api_layer(self):
        offenders = []
        for source_path in CCDI_PACKAGE_DIR.rglob("*.py"):
            for module in imported_modules(source_path):
                if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    offenders.append(f"{source_path.name} imports {module}")
        self.assertEqual(offenders, [], f"CCDI node leaks v1 imports: {offenders}")

    def test_v1_api_layer_does_not_import_the_node(self):
        offenders = []
        for layer in ("views", "serializers"):
            for source_path in (SCPCA_PORTAL_DIR / layer).rglob("*.py"):
                for module in imported_modules(source_path):
                    if module.startswith("scpca_portal.federation"):
                        offenders.append(f"{source_path.name} imports {module}")
        self.assertEqual(offenders, [], f"v1 API layer imports the node: {offenders}")
