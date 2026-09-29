"""Tests for the CCDI Sample: its identity and its shape."""

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi.mapping.sample import Sample, library_id
from scpca_portal.federation.ccdi.schema import SampleMetadata
from scpca_portal.test.federation.ccdi.mapping.helpers import build_library, build_sample


class IdentityTests(SimpleTestCase):
    def test_a_sample_is_a_library_seen_through_a_sample(self):
        self.assertEqual(
            Sample(build_library("SCPCL000001"), build_sample("SCPCS000001")).name,
            "SCPCL000001-SCPCS000001",
        )

    def test_a_multiplexed_library_yields_one_ccdi_sample_per_scpca_sample(self):
        library = build_library("SCPCL000001")
        names = {
            Sample(library, build_sample(each)).name for each in ("SCPCS000001", "SCPCS000002")
        }

        self.assertEqual(names, {"SCPCL000001-SCPCS000001", "SCPCL000001-SCPCS000002"})


class LibraryIdTests(SimpleTestCase):
    """Library ids reach the node in two forms; both name the same library."""

    def test_a_bare_library_id_is_its_own(self):
        self.assertEqual(library_id("SCPCL000001"), "SCPCL000001")

    def test_a_library_id_carrying_a_sample_id_drops_it(self):
        self.assertEqual(library_id("SCPCL000001-SCPCS000001"), "SCPCL000001")

    def test_both_forms_produce_the_same_ccdi_name(self):
        # Otherwise the same pair would be two different CCDI Samples depending
        # on which form the database happened to hold.
        sample = build_sample("SCPCS000001")

        self.assertEqual(
            Sample(build_library("SCPCL000001"), sample).name,
            Sample(build_library("SCPCL000001-SCPCS000001"), sample).name,
        )

    def test_a_library_id_hyphenated_for_its_own_reasons_is_left_alone(self):
        # Splitting on the first separator would strip this too, collapsing two
        # distinct libraries onto one CCDI name.
        self.assertEqual(library_id("SCPCL000001-rerun1"), "SCPCL000001-rerun1")

    def test_two_libraries_differing_after_the_prefix_keep_distinct_names(self):
        sample = build_sample("SCPCS000001")

        first = Sample(build_library("SCPCL000001-rerun1"), sample).name
        second = Sample(build_library("SCPCL000001-rerun2"), sample).name

        self.assertNotEqual(first, second)

    def test_several_trailing_sample_ids_are_all_stripped(self):
        self.assertEqual(library_id("SCPCL000001-SCPCS000001-SCPCS000002"), "SCPCL000001")

    def test_a_name_never_repeats_its_sample_id(self):
        built = Sample(build_library("SCPCL000001-SCPCS000001"), build_sample("SCPCS000001"))

        self.assertEqual(built.name, "SCPCL000001-SCPCS000001")


class NameParsingTests(SimpleTestCase):
    def test_a_name_parses_back_into_the_ids_it_was_built_from(self):
        self.assertEqual(
            Sample.parse_name("SCPCL000001-SCPCS000001"), ("SCPCL000001", "SCPCS000001")
        )

    def test_parsing_is_the_inverse_of_naming(self):
        built = Sample(build_library("SCPCL000001"), build_sample("SCPCS000002"))

        self.assertEqual(Sample.parse_name(built.name), ("SCPCL000001", "SCPCS000002"))

    def test_it_is_the_inverse_for_a_library_id_that_carries_a_hyphen(self):
        built = Sample(build_library("SCPCL000001-rerun1"), build_sample("SCPCS000002"))

        self.assertEqual(Sample.parse_name(built.name), ("SCPCL000001-rerun1", "SCPCS000002"))

    def test_a_name_this_would_not_mint_resolves_to_nothing(self):
        # Strict on purpose: a name we would not emit must resolve to nothing
        # rather than to whichever record it happens to resemble.
        for name in (
            "SCPCL000001",  # no sample half
            "SCPCL000001-SCPCS000001-SCPCS000002",  # library half still carries one
            "SCPCL000001-",
            "-SCPCS000001",
            "SCPCL000001-scpcs000001",  # wrong case
            "SCPCL000001-SCPCSABC",
            "",
        ):
            with self.subTest(name=name):
                self.assertIsNone(Sample.parse_name(name))


class ShapeTests(SimpleTestCase):
    def test_a_built_sample_is_namespaced(self):
        built = Sample(build_library("SCPCL000001"), build_sample("SCPCS000001")).emit()

        self.assertEqual(built.id.name, "SCPCL000001-SCPCS000001")
        self.assertEqual(built.id.namespace.organization, "alsf")

    def test_a_built_sample_points_at_its_subject(self):
        built = Sample(build_library(), build_sample(submitter_id="1463")).emit()

        self.assertEqual(built.subject.name, "1463")

    def test_a_context_carries_its_own_identifier(self):
        context = Sample(build_library("SCPCL000001"), build_sample("SCPCS000001"))

        self.assertEqual(context.name, "SCPCL000001-SCPCS000001")

    def test_a_built_sample_validates_against_the_spec_types(self):
        built = Sample(build_library(), build_sample(submitter_id="1463")).emit()

        SampleMetadata.model_validate(built.metadata.model_dump(mode="json"))

    def test_a_built_sample_leaves_gateways_unset(self):
        # Nothing sets them — they belong on File. Absent rather than null: the
        # spec's `gateways` is an optional array it never marks nullable, and
        # only `exclude_unset` tells those apart.
        built = Sample(build_library(), build_sample()).emit()

        self.assertNotIn("gateways", built.model_dump(exclude_unset=True))
