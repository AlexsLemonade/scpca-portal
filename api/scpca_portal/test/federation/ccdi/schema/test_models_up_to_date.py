"""The committed CCDI response types must match a fresh generation from the spec."""

import ast
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi.schema.generate import MODELS_PATH, generate


class ModelsUpToDateTests(SimpleTestCase):
    def test_committed_models_match_the_spec(self):
        # Compare parsed ASTs, not raw text. The formatter's line-length is
        # discovered from pyproject, which isn't reachable in every environment
        # (e.g. the Docker test image mounts only `api/`), so byte formatting can
        # differ run-to-run. The model *content* is what must stay in sync.
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "_models.py"
            generate(fresh)
            up_to_date = ast.dump(ast.parse(fresh.read_text())) == ast.dump(
                ast.parse(MODELS_PATH.read_text())
            )
            self.assertTrue(
                up_to_date,
                "CCDI response types are stale; run `./manage.py generate_ccdi_types`.",
            )
