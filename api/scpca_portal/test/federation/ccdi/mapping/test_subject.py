"""Tests for the CCDI Subject: its identity, its grouping, and its shape."""

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi.mapping.subject import Subject
from scpca_portal.federation.ccdi.schema import SubjectMetadata
from scpca_portal.test.federation.ccdi.mapping.helpers import build_sample


class IdentityTests(SimpleTestCase):
    def test_a_subject_is_identified_by_its_submitter_id(self):
        self.assertEqual(Subject(build_sample(submitter_id="1463")).name, "1463")

    def test_samples_sharing_a_submitter_id_are_one_subject(self):
        first = build_sample("SCPCS000010", submitter_id="1463")
        second = build_sample("SCPCS000011", submitter_id="1463")

        self.assertEqual(Subject(first).name, Subject(second).name)

    def test_an_unreported_submitter_id_falls_back_to_per_sample_identity(self):
        # Collapsing samples with no participant identifier into one Subject
        # would be wrong, so each becomes its own.
        for unreported in ("NA", "", "   ", None):
            with self.subTest(submitter_id=unreported):
                sample = build_sample("SCPCS000001", submitter_id=unreported)

                self.assertEqual(Subject(sample).name, f"{Subject.DERIVED_PREFIX}SCPCS000001")

    def test_a_missing_submitter_id_falls_back_to_per_sample_identity(self):
        self.assertEqual(
            Subject(build_sample("SCPCS000002")).name,
            f"{Subject.DERIVED_PREFIX}SCPCS000002",
        )


class FromRecordsTests(SimpleTestCase):
    def test_samples_are_grouped_by_the_identity_rule(self):
        # Grouping is `name()` applied, so an endpoint can't group by some other
        # rule and drift from what a Subject is.
        samples = [
            build_sample("SCPCS000010", submitter_id="1463"),
            build_sample("SCPCS000011", submitter_id="1463"),
            build_sample("SCPCS000012", submitter_id="1464"),
        ]

        groups = Subject.from_records(samples)

        self.assertEqual(sorted(group.name for group in groups), ["1463", "1464"])
        self.assertEqual(sorted(len(group.samples) for group in groups), [1, 2])

    def test_grouping_nothing_yields_nothing(self):
        self.assertEqual(Subject.from_records([]), [])


class ShapeTests(SimpleTestCase):
    def test_a_subject_is_identified_by_its_group(self):
        built = Subject(build_sample(submitter_id="1463")).emit()

        self.assertEqual(built.id.name, "1463")
        self.assertEqual(built.id.namespace.organization, "alsf")
        self.assertEqual(built.id.namespace.name, "scpca")

    def test_a_subject_declares_a_kind(self):
        # The one harmonized value the spec gives no null for.
        built = Subject(build_sample()).emit()

        self.assertEqual(built.kind, "Participant")

    def test_a_context_carries_its_own_identifier(self):
        context = Subject(build_sample(submitter_id="1463"))

        self.assertEqual(context.name, "1463")

    def test_a_built_subject_validates_against_the_spec_types(self):
        built = Subject(build_sample(submitter_id="1463")).emit()

        SubjectMetadata.model_validate(built.metadata.model_dump(mode="json"))


class DerivedIdentityTests(SimpleTestCase):
    """
    The two ways a Subject name is minted must not be able to produce the same
    one. `submitter_id` is a column submitters fill by hand, so one of them
    writing a ScPCA sample id into it is plausible — and without the tag that
    would silently merge their sample with whichever sample falls back to that
    same id.
    """

    def test_a_submitter_id_that_looks_like_a_sample_id_does_not_merge(self):
        reported_as_sample_id = build_sample("SCPCS000010", submitter_id="SCPCS000011")
        falls_back = build_sample("SCPCS000011", submitter_id="NA")

        self.assertNotEqual(Subject(reported_as_sample_id).name, Subject(falls_back).name)

    def test_those_two_samples_stay_two_subjects(self):
        subjects = Subject.from_records(
            [
                build_sample("SCPCS000010", submitter_id="SCPCS000011"),
                build_sample("SCPCS000011", submitter_id="NA"),
            ]
        )

        self.assertEqual(len(subjects), 2)

    def test_a_reported_submitter_id_is_left_exactly_as_given(self):
        # The tag marks derived identity only. When the Participant Index lands
        # it replaces the reported path, and a tagged value there would have to
        # be unpicked.
        self.assertEqual(Subject(build_sample(submitter_id="1463")).name, "1463")

    def test_samples_that_do_fall_back_are_still_one_subject_each(self):
        subjects = Subject.from_records([build_sample("SCPCS000001"), build_sample("SCPCS000002")])

        self.assertEqual(len(subjects), 2)
