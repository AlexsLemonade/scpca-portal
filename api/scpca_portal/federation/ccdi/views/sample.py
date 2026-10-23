"""
Sample entity endpoints for the CCDI federation node.

A CCDI Sample is a ScPCA Library seen through one of its Samples, so the rows
these endpoints page over are the pairs in the Library↔Sample relation. What the
node publishes is declared once, in `mapping.PUBLISHED_PAIRS`.

See: https://cbiit.github.io/ccdi-federation-api/entities/primary/sample.html
"""

from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from scpca_portal.federation.ccdi import config, schema
from scpca_portal.federation.ccdi.mapping import PUBLISHED_PAIRS
from scpca_portal.federation.ccdi.mapping.sample import ID_SEPARATOR, Sample as CCDISample
from scpca_portal.federation.ccdi.views.base import (
    EndpointNotImplemented,
    EntityViewSet,
    page_link_header,
    paginate,
    requested_filters,
)
from scpca_portal.models import Sample as ScPCASample

# The filters the spec declares on `GET /sample`, verbatim. Every one names a
# *CCDI* field, so matching is against what a mapping emits — not against the
# ScPCA column behind it.
FILTERS = frozenset(
    {
        "age_at_collection",
        "age_at_diagnosis",
        "anatomical_sites",
        "depositions",
        "diagnosis",
        "diagnosis_category",
        "disease_phase",
        "library_selection_method",
        "library_source_material",
        "library_strategy",
        "preservation_method",
        "specimen_molecular_analyte_type",
        "tissue_type",
        "tumor_classification",
        "tumor_grade",
        "tumor_tissue_morphology",
    }
)


def published_pairs():
    """
    Every ScPCA library/sample pair the node publishes, in CCDI identifier order.

    Pairs come from the relation's through model because a CCDI Sample *is* the
    pair, and paging over rows is what lets the database do the paging. Ordering
    by the two ids is ordering by the name they emit, which is what the spec
    requires of an index with no sort given: namespace is constant for this node,
    so only the entity name is left to order by.
    """
    return (
        ScPCASample.libraries.through.objects.filter(PUBLISHED_PAIRS)
        .select_related("library", "library__project", "sample")
        .order_by("library__scpca_id", "sample__scpca_id")
    )


def find_pair(name: str):
    """
    The one published pair a CCDI Sample name refers to, or `None`.

    The library half is matched in both of the forms the database can hold it —
    its own id, or that id with a sample id already appended — so a name resolves
    the same either way. Filtering through `published_pairs` is deliberate: a pair
    the node does not publish is not found, rather than reachable by guessing its
    name.
    """
    parsed = CCDISample.parse_name(name)

    if parsed is None:
        return None

    library, sample = parsed

    return (
        published_pairs()
        .filter(
            # Either form the database can hold the library in. The suffix is
            # matched by shape, so a library id containing a hyphen of its own
            # cannot be mistaken for one carrying a sample id.
            Q(library__scpca_id=library)
            | Q(library__scpca_id__startswith=f"{library}{ID_SEPARATOR}SCPCS"),
            sample__scpca_id=sample,
        )
        .first()
    )


class SampleViewSet(EntityViewSet):
    """/sample endpoints."""

    def list(self, request):
        """GET /sample"""
        pairs = published_pairs()

        if requested_filters(request, FILTERS):
            # The spec excludes a sample whose value for the filtered field is
            # null, and every field the node emits is null until it has a getter.
            # So nothing can match, and an empty result is the spec's own answer
            # rather than a placeholder for one.
            #
            # That stops being true the moment a field is mapped. The
            # `/metadata/fields` burndown tests turn red at exactly that moment,
            # and `SampleFilterTests` says what has to replace this.
            pairs = pairs.none()

        page = paginate(request, pairs)

        # No gateways: the only URLs this node can build are per-CCDL-dataset,
        # which is a cohort link for a Sample rather than an exact one. They
        # belong on File, which a consumer reaches from the Samples it names.
        data = [
            ccdi.emit()
            for ccdi in CCDISample.from_records((row.library, row.sample) for row in page.rows)
        ]

        found = schema.SamplesResponse(
            summary=schema.EntitySummary(
                counts=schema.EntityCounts(current=len(data), all=page.total)
            ),
            data=data,
        )

        return Response(schema.dump(found), headers={"link": page_link_header(request, page)})

    def retrieve(self, request, organization=None, namespace=None, name=None):
        """GET /sample/{organization}/{namespace}/{name}"""
        identifier = config.NAMESPACE["id"]

        if organization != identifier["organization"] or namespace != identifier["name"]:
            raise NotFound()

        row = find_pair(name)

        if row is None:
            raise NotFound()

        # `responses.Sample` is `models.Sample` with nothing added, so the built
        # entity is already the response body.
        return Response(schema.dump(CCDISample(row.library, row.sample).emit()))

    def diagnosis(self, request):
        """GET /sample-diagnosis"""
        raise EndpointNotImplemented()
