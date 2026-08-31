"""The committed CCDI response types must match a fresh generation from the spec."""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi.schema.generate import MODELS_PATH, generate


class ModelsUpToDateTests(SimpleTestCase):
    def test_committed_models_match_the_spec(self):
        # Regenerate inside the repo tree so the formatter resolves the same
        # pyproject line-length (black's config discovery is relative to the
        # output path, not the cwd).
        with tempfile.TemporaryDirectory(dir=MODELS_PATH.parent) as tmp:
            fresh = Path(tmp) / "_models.py"
            generate(fresh)
            self.assertEqual(
                fresh.read_text(),
                MODELS_PATH.read_text(),
                "CCDI response types are stale; run `./manage.py generate_ccdi_types`.",
            )
