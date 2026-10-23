"""
The CCDI Subject: a group of ScPCA samples that share a participant identity.

Getters take the Subject as `scpca`, reading `scpca.samples` — fields like
`associated_diagnoses` are aggregates over all of them rather than facts about
one — and `scpca.name` for the fields that carry the Subject's own identifier.
Subject-specific crosswalk tables belong here, beside the getters that use them.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Iterable

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping import reported
from scpca_portal.federation.ccdi.mapping.entity import Entity
from scpca_portal.federation.ccdi.mapping.field_map import FieldMap

if TYPE_CHECKING:
    from scpca_portal.models import Sample as ScPCASample


class Subject(Entity):
    """
    The ScPCA samples behind one CCDI Subject.

    An endpoint groups the samples it fetched (see `from_records`) and emits each
    Subject from its own; the layer issues no queries.
    """

    ccdi_type = schema.Subject
    identifier = schema.SubjectIdentifier
    FIELDS = FieldMap("subject", schema.SubjectMetadata)

    # CCDI requires a kind on every Subject and offers no null, so this is the
    # one harmonized value the layer has to assert. TODO: derive Cell Line and
    # Patient Derived Xenograft from `is_cell_line` / `is_xenograft` when subject
    # content is mapped — see open question 18.
    KIND = "Participant"

    # What a Subject with no usable `submitter_id` is identified by. Tagged
    # rather than bare, because the two ways a name is minted otherwise share one
    # namespace: a submitter writing a ScPCA sample id into `submitter_id` — a
    # column they fill by hand, so this is plausible — would mint the same name
    # as some other sample's fallback, and the two would silently become one
    # participant. The spec's CDE asks for an identifier unique within the site,
    # and the namespace is the site.
    DERIVED_PREFIX = "scpca-sample-"

    def __init__(self, *samples: "ScPCASample"):
        self.samples = samples

    @property
    def name(self) -> str:
        """
        This Subject's CCDI identifier.

        A Subject is usually a participant, but ScPCA has no first-class donor
        entity, so one is derived: identifiers are minted from the submitter's
        own `submitter_id`, and the CCDI Participant Index replaces that when NCI
        provides it. Changing this property is the whole of that switch. (The
        spec also allows a Subject to be a cell line, xenograft or organoid — see
        `KIND` — which is why the class is named for the entity rather than for
        one of its kinds.)

        Identifiers are deliberately not scoped by project — the same
        `submitter_id` in two projects is the same participant contributing to
        both, which is a correct representation rather than a collision. A sample
        with no usable `submitter_id` falls back to per-sample identity under
        `DERIVED_PREFIX`, so an unpopulated column yields one Subject per Sample
        instead of collapsing unrelated samples into one participant.

        Every member of a Subject resolves to the same name — that is what makes
        them a group — so the first one answers for all of them.
        """
        sample = self.samples[0]
        submitter_id = reported(sample.metadata.get("submitter_id"))

        if submitter_id is not None:
            return str(submitter_id)

        return f"{self.DERIVED_PREFIX}{sample.scpca_id}"

    @classmethod
    def from_records(cls, samples: Iterable["ScPCASample"]) -> list["Subject"]:
        """
        The Subjects a set of ScPCA samples belongs to.

        Grouping is `name` applied, so an endpoint can't drift from the identity
        rule by grouping some other way. It stays a pure function over records the
        endpoint already fetched rather than a query per Subject.
        """
        groups = defaultdict(list)

        for sample in samples:
            groups[cls(sample).name].append(sample)

        return [cls(*members) for members in groups.values()]

    def emit(self) -> schema.Subject:
        return super().emit(kind=self.KIND)


# ── mappings ──────────────────────────────────────────────────────────────────
