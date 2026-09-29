"""
The ScPCA→CCDI mapping layer: the swappable pieces every data-aware CCDI
response is built from.

One module per entity — `subject`, `sample`, `file` — each holding everything
about it: which ScPCA records back it, how its identity is derived, and the
getters that populate its metadata. `field_map` is the machinery that runs those
getters.

Everything this layer reads from the ScPCA models is read-only, and it issues no
queries: an endpoint hands it records it has already fetched.
"""

from django.db.models import Q

from scpca_portal.enums import Modalities
from scpca_portal.federation.ccdi import config
from scpca_portal.federation.ccdi.schema import NamespaceIdentifier

NAMESPACE = NamespaceIdentifier(**config.NAMESPACE["id"])

# What the node publishes, as one filter over the ScPCA Library↔Sample relation,
# where a row is one CCDI Sample.
#
# Spatial and multiplexed data are held back for now, and this is the switch:
# drop a clause to publish that data, and nothing else changes.
#
# - **Spatial** has no settled answer for which CCDL dataset holds it:
#   `ccdl_datasets.TYPES` records the spatial dataset's `format` as the download
#   format, not the library's, so a library cannot be joined to it the way
#   single-cell can.
# - **Multiplexed** is excluded at the sample level, not just the library level,
#   so a multiplexed sample does not reach the node through its other libraries.
#   `library__is_multiplexed` is then redundant — `Sample.has_multiplexed_data`
#   is defined as exactly that library existing — and is kept only because it
#   states the library-level half of the rule where a reader looks for it.

PUBLISHED_PAIRS = Q(
    library__modality=Modalities.SINGLE_CELL,
    library__is_multiplexed=False,
    sample__has_multiplexed_data=False,
)

# ScPCA writes NA for a value the submitter did not provide. This list is
# provisional: the fixtures are not representative of real submissions, so the
# vocabulary across projects is unconfirmed. Widen it against real data only —
# `unknown`, for instance, looks like a placeholder but is a legitimate
# `age_timing` value.
NOT_REPORTED = frozenset({"", "NA"})


def reported(value):
    """
    The value as the submitter gave it, or `None` if they gave none.

    Takes a value rather than fetching one, because ScPCA keeps metadata in two
    places — each model's `metadata` JSON and its columns — and neither is
    normalised on the way in. Wrap any read from either in this.
    """
    if not isinstance(value, str):
        return value

    value = value.strip()

    return None if value in NOT_REPORTED else value
