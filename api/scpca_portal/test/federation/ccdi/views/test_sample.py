"""Response tests for the /sample endpoints."""

from unittest import expectedFailure

from django.test import SimpleTestCase, TestCase
from rest_framework import status

from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.federation.ccdi.mapping.sample import Sample as CCDISample
from scpca_portal.federation.ccdi.schema import Sample as CCDISampleType, SamplesResponse
from scpca_portal.federation.ccdi.views.base import MAX_PER_PAGE
from scpca_portal.federation.ccdi.views.sample import FILTERS
from scpca_portal.test.factories import LeafProjectFactory, LibraryFactory, SampleFactory

LIST_URL = "/federation/ccdi/v1/sample"

# Routes the node answers. Kept alongside the pending ones so `test_urls` can
# assert the whole surface is mounted from one place.
ENDPOINTS = (
    LIST_URL,
    "/federation/ccdi/v1/sample/by/disease_phase/count",
    "/federation/ccdi/v1/sample/summary",
    "/federation/ccdi/v1/sample/alsf/scpca/SAMPLE1",
    "/federation/ccdi/v1/sample-diagnosis",
)

PENDING_ENDPOINTS = (
    "/federation/ccdi/v1/sample/by/disease_phase/count",
    "/federation/ccdi/v1/sample/summary",
    "/federation/ccdi/v1/sample-diagnosis",
)


def build_pair(
    *,
    formats=None,
    modality=Modalities.SINGLE_CELL,
    is_multiplexed=False,
    has_multiplexed_data=False,
    project=None,
    library_id=None,
    sample_id=None,
):
    """One ScPCA library/sample pair, defaulting to what the node publishes."""
    project = project or LeafProjectFactory()
    library = LibraryFactory(
        project=project,
        formats=formats if formats is not None else [FileFormats.SINGLE_CELL_EXPERIMENT],
        modality=modality,
        is_multiplexed=is_multiplexed,
        **({"scpca_id": library_id} if library_id else {}),
    )
    sample = SampleFactory(
        project=project,
        has_multiplexed_data=has_multiplexed_data,
        **({"scpca_id": sample_id} if sample_id else {}),
    )
    sample.libraries.add(library)

    return library, sample


def detail_url(name):
    return f"/federation/ccdi/v1/sample/alsf/scpca/{name}"


class SamplePendingEndpointTests(SimpleTestCase):
    def test_pending_endpoints_are_still_stubs(self):
        """
        The burndown marker for the `/sample` endpoints not yet built.

        Asserts the stub state, so it fails by name the moment one stops
        answering 501. See `test_subject.py` for why asserting 200 cannot.
        """
        for url in PENDING_ENDPOINTS:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_501_NOT_IMPLEMENTED)


class SampleListTests(TestCase):
    def test_a_published_pair_is_one_ccdi_sample(self):
        library, sample = build_pair()

        body = self.client.get(LIST_URL).json()

        self.assertEqual(
            [entity["id"]["name"] for entity in body["data"]],
            [f"{library.scpca_id}-{sample.scpca_id}"],
        )
        self.assertEqual(
            body["data"][0]["id"]["namespace"], {"organization": "alsf", "name": "scpca"}
        )

    def test_the_response_validates_against_the_spec(self):
        build_pair()

        SamplesResponse.model_validate(self.client.get(LIST_URL).json())

    def test_a_library_belonging_to_two_samples_is_two_ccdi_samples(self):
        project = LeafProjectFactory()
        library, first = build_pair(project=project)
        second = SampleFactory(project=project)
        second.libraries.add(library)

        body = self.client.get(LIST_URL).json()

        self.assertEqual(
            sorted(entity["id"]["name"] for entity in body["data"]),
            sorted(
                [f"{library.scpca_id}-{first.scpca_id}", f"{library.scpca_id}-{second.scpca_id}"]
            ),
        )

    def test_entities_are_ordered_by_identifier(self):
        build_pair(library_id="SCPCL000002", sample_id="SCPCS000002")
        build_pair(library_id="SCPCL000001", sample_id="SCPCS000001")

        body = self.client.get(LIST_URL).json()

        names = [entity["id"]["name"] for entity in body["data"]]
        self.assertEqual(names, sorted(names))

    def test_an_empty_node_still_answers(self):
        body = self.client.get(LIST_URL).json()

        self.assertEqual(body["data"], [])
        self.assertEqual(body["summary"]["counts"], {"current": 0, "all": 0})

    def test_an_entity_carries_no_gateways(self):
        # They belong on File — a CCDL dataset URL is an exact fit for a File
        # and a cohort link for a Sample. Absent rather than null, which is what
        # the spec requires of an optional array it never marks nullable.
        build_pair()

        entity = self.client.get(LIST_URL).json()["data"][0]

        self.assertNotIn("gateways", entity)

    def test_the_response_carries_no_named_gateway_list(self):
        # Named gateways exist to deduplicate one gateway across many entities.
        # With none on the entities there is nothing to name.
        build_pair()

        self.assertNotIn("gateways", self.client.get(LIST_URL).json())

    def test_an_entity_omits_the_optional_keys_the_spec_forbids_nulling(self):
        # `metadata.unharmonized` is an optional object the spec never marks
        # nullable, so it has to be absent rather than null. Asserted through a
        # real request, because only the view's renderer decides this.
        build_pair()

        entity = self.client.get(LIST_URL).json()["data"][0]

        self.assertNotIn("unharmonized", entity["metadata"])


class SampleExclusionTests(TestCase):
    """What `mapping.PUBLISHED_PAIRS` holds back. Flip a clause and these change."""

    def published_names(self):
        return [entity["id"]["name"] for entity in self.client.get(LIST_URL).json()["data"]]

    def test_spatial_libraries_are_not_published(self):
        build_pair(modality=Modalities.SPATIAL, formats=[FileFormats.SPATIAL_SPACERANGER])

        self.assertEqual(self.published_names(), [])

    def test_bulk_libraries_are_not_published(self):
        build_pair(modality=Modalities.BULK_RNA_SEQ, formats=[])

        self.assertEqual(self.published_names(), [])

    def test_multiplexed_libraries_are_not_published(self):
        build_pair(is_multiplexed=True)

        self.assertEqual(self.published_names(), [])

    def test_a_multiplexed_sample_is_not_published_through_its_other_libraries(self):
        # The library itself is not multiplexed, but the sample it belongs to
        # has multiplexed data, so the sample is withheld through every library
        # it owns rather than only its multiplexed ones.
        build_pair(has_multiplexed_data=True)

        self.assertEqual(self.published_names(), [])

    def test_a_published_pair_is_not_excluded_by_any_of_them(self):
        library, sample = build_pair()

        self.assertEqual(self.published_names(), [f"{library.scpca_id}-{sample.scpca_id}"])


class SamplePagingTests(TestCase):
    def setUp(self):
        for index in range(1, 4):
            build_pair(library_id=f"SCPCL00000{index}", sample_id=f"SCPCS00000{index}")

    def test_counts_report_the_page_and_the_whole_set(self):
        body = self.client.get(LIST_URL, {"per_page": 2}).json()

        self.assertEqual(body["summary"]["counts"], {"current": 2, "all": 3})

    def test_a_later_page_holds_the_rest(self):
        body = self.client.get(LIST_URL, {"per_page": 2, "page": 2}).json()

        self.assertEqual(body["summary"]["counts"], {"current": 1, "all": 3})

    def test_a_page_past_the_end_is_empty_rather_than_an_error(self):
        response = self.client.get(LIST_URL, {"per_page": 2, "page": 9})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["summary"]["counts"], {"current": 0, "all": 3})

    def test_the_link_header_always_carries_first_and_last(self):
        header = self.client.get(LIST_URL, {"per_page": 2}).headers["link"]

        self.assertIn('rel="first"', header)
        self.assertIn('rel="last"', header)

    def test_next_and_prev_appear_only_where_a_page_exists(self):
        first = self.client.get(LIST_URL, {"per_page": 2}).headers["link"]
        last = self.client.get(LIST_URL, {"per_page": 2, "page": 2}).headers["link"]

        self.assertIn('rel="next"', first)
        self.assertNotIn('rel="prev"', first)
        self.assertIn('rel="prev"', last)
        self.assertNotIn('rel="next"', last)

    def test_a_page_number_too_large_for_an_offset_does_not_reach_the_database(self):
        # Postgres cannot represent an OFFSET this big. Answering from the count
        # alone is what keeps it from becoming an uncaught DataError — a 500 with
        # a traceback, on a public unauthenticated endpoint.
        response = self.client.get(LIST_URL, {"page": 10**18})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["summary"]["counts"], {"current": 0, "all": 3})

    def test_a_page_past_the_end_links_back_to_one_that_exists(self):
        # An unbounded `prev` walks backwards through pages that are all empty.
        header = self.client.get(LIST_URL, {"per_page": 2, "page": 9}).headers["link"]

        self.assertIn('page=2>; rel="prev"', header)
        self.assertNotIn("page=8", header)

    def test_an_oversized_page_is_clamped_rather_than_rejected(self):
        # A public endpoint shouldn't let one request ask for everything. The
        # link header has to page at the size actually used, not the one asked
        # for, or a client following links would skip records.
        response = self.client.get(LIST_URL, {"per_page": 10_000})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(f"per_page={MAX_PER_PAGE}", response.headers["link"])

    def test_a_page_no_offset_can_be_calculated_from_is_rejected(self):
        for query in ({"page": 0}, {"per_page": 0}, {"page": "many"}):
            with self.subTest(query=query):
                response = self.client.get(LIST_URL, query)
                self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class SampleRetrieveTests(TestCase):
    def test_a_published_sample_is_served_by_name(self):
        library, sample = build_pair()
        name = f"{library.scpca_id}-{sample.scpca_id}"

        response = self.client.get(detail_url(name))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"]["name"], name)

    def test_the_response_validates_against_the_spec(self):
        library, sample = build_pair()

        body = self.client.get(detail_url(f"{library.scpca_id}-{sample.scpca_id}")).json()

        CCDISampleType.model_validate(body)

    def test_a_library_id_that_already_carries_its_sample_resolves_the_same_name(self):
        # Some library ids are stored as `SCPCL…-SCPCS…`. The CCDI name is built
        # from the library's own id either way, so the same URL has to resolve it.
        library, sample = build_pair(library_id="SCPCL000001-SCPCS000001", sample_id="SCPCS000001")

        response = self.client.get(detail_url("SCPCL000001-SCPCS000001"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"]["name"], "SCPCL000001-SCPCS000001")

    def test_an_unknown_name_is_not_found(self):
        response = self.client.get(detail_url("SCPCL999999-SCPCS999999"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_a_malformed_name_is_not_found(self):
        # The pair has to exist, or these 404 because the database is empty
        # rather than because the name was rejected — and a weakened guard would
        # then serve this record for a URL that does not name it.
        build_pair(library_id="SCPCL000001", sample_id="SCPCS000001")

        for name in ("SCPCL000001", "SCPCL000001-SCPCS000001-SCPCS000002"):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(detail_url(name)).status_code, status.HTTP_404_NOT_FOUND
                )

    def test_the_pair_those_malformed_names_are_built_from_does_resolve(self):
        # Keeps the test above honest: it is the names that are rejected, not
        # the record that is missing.
        build_pair(library_id="SCPCL000001", sample_id="SCPCS000001")

        response = self.client.get(detail_url("SCPCL000001-SCPCS000001"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_a_sample_the_node_does_not_publish_is_not_found(self):
        library, sample = build_pair(is_multiplexed=True)

        response = self.client.get(detail_url(f"{library.scpca_id}-{sample.scpca_id}"))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_another_namespace_is_not_found(self):
        library, sample = build_pair()
        name = f"{library.scpca_id}-{sample.scpca_id}"

        response = self.client.get(f"/federation/ccdi/v1/sample/other/elsewhere/{name}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SampleFilterTests(TestCase):
    """
    The spec declares 16 filters on `/sample`, all naming CCDI fields.

    None is implemented, and until a field has a getter none can be: the spec
    excludes a sample whose value for the filtered field is null, and every field
    the node emits is null. So the empty result below is conformant rather than a
    stand-in — and the expected-failures are what turn red when that stops being
    the case.
    """

    def test_a_filter_on_an_unmapped_field_matches_nothing(self):
        build_pair()

        body = self.client.get(LIST_URL, {"tissue_type": "Tumor"}).json()

        self.assertEqual(body["data"], [])
        self.assertEqual(body["summary"]["counts"], {"current": 0, "all": 0})

    def test_every_declared_filter_is_recognised(self):
        build_pair()

        for name in sorted(FILTERS):
            with self.subTest(filter=name):
                body = self.client.get(LIST_URL, {name: "anything"}).json()
                self.assertEqual(body["data"], [], f"{name} was ignored")

    def test_an_unharmonized_filter_is_recognised_by_its_prefix(self):
        # The spec cannot enumerate these: the field names are the server's own.
        build_pair()

        body = self.client.get(LIST_URL, {"metadata.unharmonized.seq_unit": "cell"}).json()

        self.assertEqual(body["data"], [])

    def test_a_parameter_the_spec_does_not_declare_is_not_a_filter(self):
        # Otherwise any stray query string would silently empty the response.
        library, sample = build_pair()

        body = self.client.get(LIST_URL, {"colour": "blue"}).json()

        self.assertEqual(
            [entity["id"]["name"] for entity in body["data"]],
            [f"{library.scpca_id}-{sample.scpca_id}"],
        )

    def test_a_filtered_response_is_still_paged(self):
        build_pair()

        response = self.client.get(LIST_URL, {"tissue_type": "Tumor"})

        self.assertIn('rel="first"', response.headers["link"])
        self.assertIn('rel="last"', response.headers["link"])

    def test_the_empty_result_stops_being_conformant_once_a_filter_field_is_mapped(self):
        """
        The tripwire that actually protects this.

        Returning nothing is only the spec's answer while every filterable field
        is null. The moment one has a getter, samples carrying a value for it
        must be returned, and this fails naming the fields that made it so — no
        `@expectedFailure`, because this has to be loud rather than silently
        green.
        """
        mapped = sorted(FILTERS & set(CCDISample.FIELDS.getters))

        self.assertEqual(mapped, [], "these are mapped, so /sample filtering must now be real")

    @expectedFailure
    def test_a_filter_returns_the_samples_carrying_that_value(self):
        """
        Expected-fails until fields are mapped and filtering is real.

        The value is read back off the node's own response rather than written
        in, so this cannot become an expected-failure that can never fire: it
        fails today on the assertion that *something* is emitted at all.

        For whoever implements it — matching is on the value a getter emits, not
        on a ScPCA column, so it cannot be pushed into the queryset, and it has
        to happen before paging for the counts and the link header to stay
        truthful. See the follow-ups.
        """
        build_pair()

        entity = self.client.get(LIST_URL).json()["data"][0]
        emitted = {
            field: wrapped["value"]
            for field, wrapped in entity["metadata"].items()
            if field in FILTERS and isinstance(wrapped, dict) and wrapped.get("value") is not None
        }

        self.assertTrue(emitted, "no filterable field carries a value yet")

        field, value = next(iter(emitted.items()))
        body = self.client.get(LIST_URL, {field: value}).json()

        self.assertEqual(len(body["data"]), 1)
