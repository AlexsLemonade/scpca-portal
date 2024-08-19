import shutil
from functools import partial
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import common
from scpca_portal.models import Project, ProjectSummary, Sample

# NOTE: Test data bucket is defined in `scpca_portal/config/local.py`
# When INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.


class TestLoadMetadata(TransactionTestCase):
    def setUp(self):
        self.load_metadata = partial(call_command, "load_metadata")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def assertProjectData(self, project):
        self.assertTrue(project.abstract)
        self.assertIsNotNone(project.contacts)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.diagnoses_counts)
        self.assertTrue(project.disease_timings)
        self.assertIsNotNone(project.seq_units)
        self.assertTrue(project.title)
        self.assertEqual(project.additional_restrictions, "Research or academic purposes only")

        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)

        sample = project.samples.first()
        self.assertIsNotNone(sample.age)
        self.assertIsNotNone(sample.age_timing)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.disease_timing)
        self.assertTrue(sample.scpca_id)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.treatment)

    @patch("scpca_portal.management.commands.load_metadata.Command.clean_up_input_data")
    def test_data_clean_up(self, mock_clean_up_input_data):
        project_id = "SCPCP999990"
        self.load_metadata(
            clean_up_input_data=True,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        mock_clean_up_input_data.assert_called_once()

    def test_load_metadata(self):
        project_id = "SCPCP999990"

        def assert_object_count():
            self.assertEqual(Project.objects.count(), 1)
            self.assertEqual(ProjectSummary.objects.count(), 4)
            self.assertEqual(Sample.objects.count(), 4)

        # First, just test that loading data works.
        self.load_metadata(
            clean_up_input_data=False,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

        project = Project.objects.get(scpca_id=project_id)
        project_summary = project.summaries.first()
        sample = project.samples.first()

        self.assertProjectData(project)

        # Make sure that reload_existing=False won't add anything new when there's nothing new.
        self.load_metadata(
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

        new_project = Project.objects.get(scpca_id=project_id)
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())

        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)

        # Make sure purging works as expected.
        Project.objects.get(scpca_id=project_id).purge()

        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)

        # Make sure reloading works smoothly.
        self.load_metadata(
            clean_up_input_data=False,
            reload_all=False,
            reload_existing=True,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

    def test_single_cell_metadata(self):
        project_id = "SCPCP999990"
        self.load_metadata(
            clean_up_input_data=False,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertTrue(project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 0)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        # This project contains 3 samples
        single_cell = 2
        spatial = 1
        bulk = 1
        expected_samples = single_cell + spatial + bulk
        self.assertEqual(project.sample_count, expected_samples)
        self.assertFalse(project.has_multiplexed_data)
        self.assertEqual(project.sample_count, 4)
        self.assertEqual(project.seq_units, "cell, spot")
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.technologies, "10Xv3, visium")

        sample = project.samples.filter(has_single_cell_data=True).first()
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        # This line will probably fail when switching test data versions
        # The reason is that the filtered_cells attribute from the library json files,
        # from which sample_cell_count_estimate is calculated, changes from version to version
        self.assertEqual(sample.sample_cell_count_estimate, 3432)
        self.assertEqual(sample.seq_units, "cell")
        self.assertEqual(sample.technologies, "10Xv3")

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

    def test_multiplexed_metadata(self):
        project_id = "SCPCP999991"
        self.load_metadata(
            clean_up_input_data=False,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_multiplexed_data)
        self.assertEqual(project.multiplexed_sample_count, 2)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        self.assertEqual(project.sample_count, 3)
        self.assertEqual(project.summaries.count(), 3)
        self.assertEqual(project.summaries.first().sample_count, 1)

        # Check contacts.
        self.assertEqual(project.contacts.count(), 2)
        contact1, contact2 = project.contacts.all()
        self.assertEqual(contact1.name, "{contact 1}")
        self.assertEqual(contact1.email, "{email contact 1}")
        self.assertEqual(contact2.name, "{contact 2}")
        self.assertEqual(contact2.email, "{email contact 2}")

        # Check external accessions.
        self.assertEqual(project.external_accessions.count(), 2)
        accession1, accession2 = project.external_accessions.all()
        self.assertEqual(accession1.accession, "{SRA project accession}")
        self.assertTrue(accession1.has_raw)
        self.assertEqual(accession1.url, "{SRA Run Selector URL}")
        self.assertEqual(accession2.accession, "{GEO series accession}")
        self.assertFalse(accession2.has_raw)
        self.assertEqual(accession2.url, "{GEO Series URL}")

        # Check publications.
        self.assertEqual(project.publications.count(), 2)
        publication, publication2 = project.publications.all()
        self.assertEqual(publication.doi, "{doi 1}")
        self.assertEqual(publication.citation, "{formatted citation 1}")
        self.assertEqual(publication2.doi, "{doi 2}")
        self.assertEqual(publication2.citation, "{formatted citation 2}")

        sample = project.samples.filter(has_multiplexed_data=True).first()
        self.assertIsNone(sample.sample_cell_count_estimate)
        self.assertTrue(sample.has_multiplexed_data)
        self.assertEqual(sample.seq_units, "nucleus")
        self.assertEqual(sample.technologies, "10Xv3.1")

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

    def test_spatial_metadata(self):
        project_id = "SCPCP999990"
        self.load_metadata(
            clean_up_input_data=False,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_spatial_data)
        self.assertTrue(project.modalities)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        # Expected Samples
        single_cell = 2
        spatial = 1
        bulk = 1
        expected_samples = single_cell + spatial + bulk
        self.assertEqual(project.sample_count, expected_samples)
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)

        sample = project.samples.filter(has_spatial_data=True).first()
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        self.assertFalse(sample.has_multiplexed_data)
        self.assertTrue(sample.has_spatial_data)
        self.assertEqual(sample.seq_units, "spot")
        self.assertEqual(sample.technologies, "visium")

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )
