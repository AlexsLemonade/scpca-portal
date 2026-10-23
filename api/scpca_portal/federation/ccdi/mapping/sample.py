"""
The CCDI Sample: a ScPCA Library, seen through one of its Samples.

Getters take the Sample as `scpca`, so a mapping reads `scpca.sample.metadata` or
`scpca.library.metadata` and it is always clear which "sample" is meant — the CCDI
entity this module maps, or the ScPCA record behind it — and `scpca.name` for the
fields that carry the Sample's own identifier. Sample-specific crosswalk tables
belong here, beside the getters that use them.
"""

import re
from typing import TYPE_CHECKING, Iterable

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping import NAMESPACE
from scpca_portal.federation.ccdi.mapping.entity import Entity
from scpca_portal.federation.ccdi.mapping.field_map import FieldMap
from scpca_portal.federation.ccdi.mapping.subject import Subject

if TYPE_CHECKING:
    from scpca_portal.models import Library, Sample as ScPCASample


# A CCDI Sample name joins a library id to the sample id it is seen through.
ID_SEPARATOR = "-"

# The sample ids a library id may already carry, at the end and nowhere else.
# Matched by shape rather than by splitting on the separator: a library id is
# allowed to contain a hyphen for its own reasons, and splitting on the first one
# would strip that too, collapsing two distinct libraries onto one CCDI name.
SAMPLE_SUFFIX = re.compile(rf"(?:{ID_SEPARATOR}SCPCS\d+)+$")

# One CCDI Sample name: a library id, then the sample id it is seen through.
CCDI_NAME = re.compile(rf"^(?P<library>.+){ID_SEPARATOR}(?P<sample>SCPCS\d+)$")


def library_id(scpca_id: str) -> str:
    """
    A library's own id, without a sample id it may already carry.

    Most ScPCA library ids are a bare `SCPCL…`, but some are stored as
    `SCPCL…-SCPCS…`. Both name the same library, so identity is built from the
    part before the sample id and the sample id is joined on after it —
    otherwise the same pair would get two different CCDI names depending on which
    form the database happened to hold.
    """
    return SAMPLE_SUFFIX.sub("", scpca_id)


class Sample(Entity):
    """The ScPCA records behind one CCDI Sample."""

    ccdi_type = schema.Sample
    identifier = schema.SampleIdentifier
    FIELDS = FieldMap("sample", schema.SampleMetadata)

    def __init__(self, library: "Library", sample: "ScPCASample"):
        self.library = library
        self.sample = sample

    @property
    def name(self) -> str:
        """
        This Sample's CCDI identifier.

        A CCDI Sample is a ScPCA Library, but a library can belong to more than
        one sample (multiplexing), so neither identifier alone is unique — the
        pair is. Joining a list rather than formatting two values is what lets a
        library seen through several samples name them all.
        """
        return ID_SEPARATOR.join([library_id(self.library.scpca_id), self.sample.scpca_id])

    @staticmethod
    def parse_name(name: str) -> tuple[str, str] | None:
        """
        The library and sample ids one CCDI Sample name was built from, or `None`.

        The inverse of `name`, for the show endpoint, and strict about it: a name
        this would not have minted resolves to nothing rather than to whichever
        record it happens to look like. The library half is checked against
        `library_id` for exactly that — a name whose library part still carries a
        sample id is not one we emit.
        """
        match = CCDI_NAME.match(name)

        if match is None:
            return None

        library, sample = match.group("library"), match.group("sample")

        return (library, sample) if library_id(library) == library else None

    @classmethod
    def from_records(cls, pairs: Iterable[tuple]) -> list["Sample"]:
        """
        The Samples for library/sample pairs an endpoint has already fetched.

        No grouping: a multiplexed library belongs to several samples, and each
        pair is its own CCDI Sample.
        """
        return [cls(library, sample) for library, sample in pairs]

    def emit(self) -> schema.Sample:
        return super().emit(
            subject=schema.SubjectIdentifier(namespace=NAMESPACE, name=Subject(self.sample).name)
        )


# ── mappings ──────────────────────────────────────────────────────────────────
