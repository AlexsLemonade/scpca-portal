"""
The CCDI File: the files of a CCDL dataset.

The file source is settled (`CCDLDataset`), but which record backs a File and how
one is identified are the entity endpoints' call — so `File` is still abstract,
and the two methods it doesn't implement are exactly those open decisions. Note
the spec requires every file it returns to carry at least one gateway.
"""

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping.entity import Entity
from scpca_portal.federation.ccdi.mapping.field_map import FieldMap


class File(Entity):
    """The ScPCA records behind one CCDI File."""

    ccdi_type = schema.File
    identifier = schema.FileIdentifier
    FIELDS = FieldMap("file", schema.FileMetadata)


# ── mappings ──────────────────────────────────────────────────────────────────
