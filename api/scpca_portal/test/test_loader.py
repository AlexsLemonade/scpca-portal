import re
import shutil
from functools import partial

from django.conf import settings
from django.test import TransactionTestCase

from scpca_portal import common, loader
from scpca_portal.models import Project
from scpca_portal.models.library import Library
from scpca_portal.models.sample import Sample


class TestGenerateComputedFiles(TransactionTestCase):
    def setUp(self):
        self.get_projects_metadata = partial(
            loader.get_projects_metadata, input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME
        )
        # When passing a project_id to get_projects_metadata, a list of one item is returned
        # This lambda creates a shorthand with which to access the single returned project_metadata
        self.get_project_metadata = lambda project_id: self.get_projects_metadata(
            filter_on_project_id=project_id
        )[0]
        self.create_project = partial(
            loader.create_project,
            submitter_whitelist={"scpca"},
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            reload_existing=True,
            update_s3=False,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def test_create_project_SCPCP999990(self):
        project_id = "SCPCP999990"
        returned_project = self.create_project(self.get_project_metadata(project_id))

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=project_id).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        self.assertEqual(project.abstract, "TBD")
        self.assertEqual(project.additional_restrictions, "Research or academic purposes only")
        self.assertIn(
            "SCPCP999990/merged/SCPCP999990_merged-summary-report.html", project.data_file_paths
        )
        self.assertIn("SCPCP999990/merged/SCPCP999990_merged.rds", project.data_file_paths)
        self.assertIn("SCPCP999990/merged/SCPCP999990_merged_rna.h5ad", project.data_file_paths)
        self.assertIn("SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv", project.data_file_paths)
        self.assertIn("SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv", project.data_file_paths)
        # why is the `diagnoses` value in the `project_metadata.csv` file
        # different than the aggregate of the `diagnosis` values
        # in the `sample_metadata.csv` with the test_data

        # This is the value in the projects_metadata.csv file
        # self.assertEqual(project.diagnoses, "Breast cancer")
        # These are the values in the sample_metadata.csv file
        self.assertIn("diagnosis1", project.diagnoses)
        self.assertIn("diagnosis2", project.diagnoses)
        self.assertIn("diagnosis5", project.diagnoses)
        self.assertIn("diagnosis8", project.diagnoses)

        # The following regex sequence pulls the diagnoses counts out of the project.diagnoses str,
        # which is formatted as follows: "diagnosis1 (1), diagnosis2 (1), diagnosis5 (1), ..."

        # Remove all words starting with 'diagnosis'
        reg_ex_diagnoses_counts = re.sub(r"\bdiagnosis\d+\b", "", project.diagnoses_counts)
        # Pull out all count totals left in regex string
        diagnoses_counts_str_list = re.findall(r"\d+", reg_ex_diagnoses_counts)
        # Cast them to ints and sum them up to arrive at a count
        diagnoses_counts = sum([int(element) for element in diagnoses_counts_str_list])
        self.assertEqual(diagnoses_counts, 4)

        self.assertEqual(project.disease_timings, "Initial diagnosis")
        # This value is not determined until after computed file generation
        self.assertEqual(project.downloadable_sample_count, 0)
        self.assertTrue(project.has_single_cell_data)
        self.assertTrue(project.has_spatial_data)
        self.assertEqual(project.human_readable_pi_name, "TBD")
        self.assertTrue(project.includes_anndata)
        self.assertFalse(project.includes_cell_lines)
        self.assertTrue(project.includes_merged_sce)
        self.assertTrue(project.includes_merged_anndata)
        self.assertFalse(project.includes_xenografts)

        self.assertIn(Sample.Modalities.NAME_MAPPING["BULK_RNA_SEQ"], project.modalities)
        self.assertIn(Sample.Modalities.NAME_MAPPING["SPATIAL"], project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 0)
        self.assertIn("Homo sapiens", project.organisms)
        self.assertEqual(project.pi_name, "scpca")
        self.assertEqual(project.s3_input_bucket, settings.AWS_S3_INPUT_BUCKET_NAME)

        # single_cell samples: SCPCS999990, SCPCS999997
        # spatial samples: SCPCS999991
        # single_cell sample SCPCS999994 is unavailable
        # As such, there should be 3 samples, but 4 are processed
        # Like we do for projects where we check if a dir exists with data before processing,
        # we should do the same for samples
        # The check should be as follows
        # single_cell, spatial = 2, 1
        # self.assertEqual(project.sample_count, single_cell + spatial)

        self.assertIn("cell", project.seq_units)
        self.assertIn("spot", project.seq_units)
        self.assertIn("10Xv3", project.technologies)
        self.assertIn("visium", project.technologies)
        self.assertEqual(project.title, "TBD")

        # single_cell sample SCPCS999994 is unavailable
        # The following evaluates to 0, whereas it should be one
        # self.assertEqual(project.unavailable_samples_count, 1)

        # CHECK SAMPLE VALUES
        sample0 = project.samples.filter(scpca_id="SCPCS999990").first()
        self.assertEqual(sample0.age, "2")
        self.assertEqual(sample0.age_timing, "diagnosis")
        self.assertIsNone(sample0.demux_cell_count_estimate)
        self.assertEqual(sample0.diagnosis, "diagnosis1")
        self.assertEqual(sample0.disease_timing, "Initial diagnosis")
        self.assertFalse(sample0.has_multiplexed_data)
        self.assertTrue(sample0.has_single_cell_data)
        self.assertFalse(sample0.has_spatial_data)
        self.assertTrue(sample0.includes_anndata)
        self.assertFalse(sample0.is_cell_line)
        self.assertFalse(sample0.is_xenograft)
        self.assertListEqual(sample0.multiplexed_with, [])
        self.assertEqual(sample0.sample_cell_count_estimate, 3432)
        self.assertEqual(sample0.seq_units, "cell")
        self.assertEqual(sample0.technologies, "10Xv3")
        self.assertEqual(sample0.tissue_location, "tissue1")
        self.assertEqual(sample0.treatment, "")

        # Now we must iterate over the following samples
        # SCPCS999991
        # SCPCS999994
        # SCPCS999997

        # CHECK LIBRARY VALUES
        library0 = project.libraries.filter(scpca_id="SCPCL999990").first()

        self.assertIn(
            "SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html", library0.data_file_paths
        )
        self.assertIn("SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds", library0.data_file_paths)
        self.assertIn(
            "SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad", library0.data_file_paths
        )
        self.assertIn("SCPCP999990/SCPCS999990/SCPCL999990_processed.rds", library0.data_file_paths)
        self.assertIn(
            "SCPCP999990/SCPCS999990/SCPCL999990_processed_rna.h5ad", library0.data_file_paths
        )
        self.assertIn("SCPCP999990/SCPCS999990/SCPCL999990_qc.html", library0.data_file_paths)
        self.assertIn(
            "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds", library0.data_file_paths
        )
        self.assertIn(
            "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered_rna.h5ad", library0.data_file_paths
        )

        self.assertIn(Library.FileFormats.SINGLE_CELL_EXPERIMENT, library0.formats)
        self.assertIn(Library.FileFormats.ANN_DATA, library0.formats)
        self.assertFalse(library0.has_cite_seq_data)
        self.assertFalse(library0.is_multiplexed)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertFalse(library0.metadata == {})
        self.assertEqual(library0.modality, Library.Modalities.SINGLE_CELL)
        self.assertEqual(library0.workflow_version, "development")

        # CHECK PROJECT SUMMARIES VALUES
        # CHECK CONTACTS
        # CHECK EXTERNAL ACCESSION VALUES
        # CHECK PUBLICATIONS VALUES

    def test_create_project_SCPCP999991(self):
        pass

    def test_create_project_SCPCP999992(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA_MERGED(self):
        pass

    def test_project_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_project_generate_computed_files_ALL_METADATA(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_sample_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass
