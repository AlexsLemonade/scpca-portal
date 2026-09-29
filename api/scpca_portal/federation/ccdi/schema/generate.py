"""
Generate the CCDI node's Pydantic response types from the vendored spec.

Run via `./manage.py generate_ccdi_types`. The output (`_models.py`) is committed
and guarded by a drift test — regenerate whenever `swagger.yml` changes. The
flags collapse the spec's dotted schema names into one importable file with
readable names; modular output hits circular imports for this spec.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent
SPEC_PATH = SCHEMA_DIR.parent / "swagger.yml"
MODELS_PATH = SCHEMA_DIR / "_models.py"

# Matches `[tool.black] line-length` in the repo's pyproject.toml. Applied
# explicitly because the generator discovers black's config by walking up from
# the output file, and pyproject is out of reach in the Docker image (which
# mounts only `api/`) — without pinning it, formatting varies by environment.
LINE_LENGTH = 100

FLAGS = [
    "--input-file-type",
    "openapi",
    "--output-model-type",
    "pydantic_v2.BaseModel",
    "--no-treat-dot-as-module",
    "--naming-strategy",
    "primary-first",
    "--collapse-root-models",
    "--reuse-model",
    "--use-annotated",
    "--use-standard-collections",
    "--enum-field-as-literal",
    "all",
    # Without this, the spec's `nullable: true` is dropped on required fields and
    # every harmonized metadata field becomes non-nullable — which the mapping
    # layer needs, since an unmapped field emits its key with a null value.
    "--strict-nullable",
    "--disable-timestamp",
    "--formatters",
    "black",
    "isort",
]


def generate(output_path: Path = MODELS_PATH) -> None:
    """Regenerate the Pydantic models from the vendored spec into `output_path`."""
    # Without this the generator's own "No module named" message surfaces as a
    # CalledProcessError further up, which reads like the models drifted.
    if importlib.util.find_spec("datamodel_code_generator") is None:
        raise RuntimeError(
            "datamodel-code-generator is not importable, so the CCDI response types "
            "cannot be regenerated. It is pinned in requirements/local.txt; if this "
            "is the api container, a stale image is one place to start: "
            "`sportal docker:compose build api`."
        )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "datamodel_code_generator",
            "--input",
            str(SPEC_PATH),
            "--output",
            str(output_path),
            *FLAGS,
        ],
        check=True,
    )
    # The generator keeps single quotes, so match that here rather than churning
    # every string literal in the committed module.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "black",
            "--line-length",
            str(LINE_LENGTH),
            "--skip-string-normalization",
            "--quiet",
            str(output_path),
        ],
        check=True,
    )
