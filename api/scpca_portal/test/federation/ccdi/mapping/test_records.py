"""
The mapping layer against saved ScPCA records.

The rest of the mapping tests build unsaved instances with values written inline,
which is right for asking "given this source value, what CCDI value comes out" —
but it means a getter reading the wrong attribute passes anyway, because the test
author wrote both sides. These tests go through the factories and the database, so
the paths the layer reads are the paths the loader actually populates, and the
relations are traversed the way an endpoint will traverse them.
"""

from django.test import TestCase

from scpca_portal.federation.ccdi.mapping.sample import Sample as CCDISample
from scpca_portal.federation.ccdi.mapping.subject import Subject as CCDISubject
from scpca_portal.federation.ccdi.schema import SampleMetadata, SubjectMetadata, dump
from scpca_portal.test.factories import LibraryFactory, SampleFactory


class ScPCARecordTests(TestCase):
    def setUp(self):
        self.library = LibraryFactory()
        self.sample = SampleFactory()
        self.sample.libraries.add(self.library)

    def test_the_stores_the_layer_reads_exist_on_saved_records(self):
        # Both halves of a CCDI Sample carry a `metadata` JSON, and the layer
        # reads library-level and sample-level keys out of them by name.
        library = self.library.__class__.objects.get(pk=self.library.pk)
        sample = self.sample.__class__.objects.get(pk=self.sample.pk)

        self.assertIn("seq_unit", library.metadata)
        self.assertIn("submitter_id", sample.metadata)

    def test_a_ccdi_sample_is_built_from_a_traversed_pair(self):
        # An endpoint reaches the pair through the many-to-many, not by being
        # handed both halves.
        library = self.sample.libraries.first()

        built = CCDISample(library, self.sample).emit()

        self.assertEqual(built.id.name, f"{library.scpca_id}-{self.sample.scpca_id}")
        SampleMetadata.model_validate(built.metadata.model_dump(mode="json"))

    def test_a_ccdi_subject_is_built_from_a_saved_sample(self):
        built = CCDISubject(self.sample).emit()

        SubjectMetadata.model_validate(built.metadata.model_dump(mode="json"))

    def test_an_unreported_submitter_id_falls_back_to_the_sample(self):
        # The factories carry `NA`, which is what most ScPCA records carry today.
        self.assertEqual(
            CCDISubject(self.sample).name,
            f"{CCDISubject.DERIVED_PREFIX}{self.sample.scpca_id}",
        )

    def test_samples_sharing_a_submitter_id_are_one_subject(self):
        first = SampleFactory(metadata=dict(self.sample.metadata, submitter_id="1463"))
        second = SampleFactory(metadata=dict(self.sample.metadata, submitter_id="1463"))

        self.assertEqual(CCDISubject(first).name, CCDISubject(second).name)

    def test_a_dumped_response_omits_the_key_the_spec_does_not_allow_null(self):
        emitted = dump(CCDISample(self.library, self.sample).emit().metadata)

        self.assertNotIn("unharmonized", emitted)
        self.assertIn("diagnosis", emitted)
