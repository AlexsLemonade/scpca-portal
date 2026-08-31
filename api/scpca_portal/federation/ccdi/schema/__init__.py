"""
Pydantic response types for the CCDI node, generated from the vendored spec.

The generated models live in `_models.py` (regenerate with
`./manage.py generate_ccdi_types`). Re-export the ones the views use under clean
names here as endpoints are implemented.
"""

from scpca_portal.federation.ccdi.schema._models import ResponsesInformation as InfoResponse
