"""
Generate the CCDI node's Pydantic response types from the vendored spec.

Run via `./manage.py generate_ccdi_types`. The output (`_models.py`) is committed
and guarded by a drift test — regenerate whenever `swagger.yml` changes. The
flags collapse the spec's dotted schema names into one importable file with
readable names; modular output hits circular imports for this spec.
"""

import subprocess
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent
SPEC_PATH = SCHEMA_DIR.parent / "swagger.yml"
MODELS_PATH = SCHEMA_DIR / "_models.py"

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
    "--disable-timestamp",
    "--formatters",
    "black",
    "isort",
]


def generate(output_path: Path = MODELS_PATH) -> None:
    """Regenerate the Pydantic models from the vendored spec into `output_path`."""
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
