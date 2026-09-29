"""Unsaved ScPCA records for the mapping tests.

Values are written inline rather than taken from the fixtures, which are sparse
enough that they would over-exercise the "submitter reported nothing" path.
Tests that need the paths the loader actually populates live in `test_records.py`.
"""

from scpca_portal.federation.ccdi.mapping.sample import Sample as CCDISample
from scpca_portal.models import Library, Sample


def build_sample(scpca_id="SCPCS000001", **metadata):
    """A sample carrying just the metadata a getter would read."""
    return Sample(scpca_id=scpca_id, metadata=metadata)


def build_library(scpca_id="SCPCL000001", **metadata):
    return Library(scpca_id=scpca_id, metadata=metadata)


def build_context(library=None, sample=None, **sample_metadata):
    """The CCDI Sample a getter is handed — the entity is its own context."""
    return CCDISample(library or build_library(), sample or build_sample(**sample_metadata))
