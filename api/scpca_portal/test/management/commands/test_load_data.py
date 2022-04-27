import csv
import os
from io import TextIOWrapper
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TestCase

from scpca_portal import common
from scpca_portal.management.commands.load_data import load_data_from_s3
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample

ALLOWED_SUBMITTERS = {"genomics_10X"}
INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs"


class MockS3Client:
    def __init__(self, *args, **kwargs):
        pass

    def list_objects(self, *args, **kwargs):
        return {"Contents": [{"Size": 1111}]}

    def upload_file(self, *args, **kwargs):
        pass


class TestLoadData(TestCase):
    def setUp(self):
        self.scpca_project_id = "SCPCP111111"

        self.expected_computed_file_count = 4
        self.expected_project_count = 1
        self.expected_sample_count = 1
        self.expected_summary_count = 4

    def assert_project(self, scpca_project_id):
        project = Project.objects.get(scpca_id=scpca_project_id)

        self.assertIsNotNone(project.abstract)
        self.assertIsNotNone(project.contact_email)
        self.assertIsNotNone(project.contact_name)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.disease_timings)
        self.assertIsNotNone(project.seq_units)
        self.assertIsNotNone(project.technologies)
        self.assertIsNotNone(project.title)

        self.assertEqual(project.summaries.count(), self.expected_summary_count)
        self.assertEqual(ProjectSummary.objects.count(), self.expected_summary_count)
        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)
        self.assertEqual(project_summary.sample_count, self.expected_sample_count)

        self.assertEqual(project.sample_count, self.expected_sample_count)
        self.assertEqual(Sample.objects.count(), self.expected_sample_count)
        sample = project.samples.first()
        self.assertIsNotNone(sample.age_at_diagnosis)
        self.assertIsNotNone(sample.cell_count)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.disease_timing)
        self.assertIsNotNone(sample.has_cite_seq_data)
        self.assertIsNotNone(sample.scpca_id)
        self.assertIsNotNone(sample.seq_units)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.technologies)
        self.assertIsNotNone(sample.tissue_location)

        expected_metadata_keys = {
            "metastasis",
            "participant_id",
            "relapse_status",
            "scpca_project_id",
            "submitter_id",
            "submitter",
            "vital_status",
        }
        self.assertEqual(set(sample.additional_metadata.keys()), expected_metadata_keys)

        self.assertIsNotNone(project.computed_file)
        self.assertGreater(project.computed_file.size_in_bytes, 0)

        self.assertIsNotNone(sample.computed_file)
        self.assertGreater(sample.computed_file.size_in_bytes, 0)

        self.assertEqual(ComputedFile.objects.count(), self.expected_computed_file_count)

        return (
            project,
            project.computed_file,
            project.summaries.first(),
            sample,
            sample.computed_file,
        )

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_load_data_from_s3(self):
        # First, just test that loading data works.
        load_data_from_s3(
            update_s3_data=False,
            reload_all=False,
            reload_existing=False,
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
        )
        self.assertEqual(Project.objects.count(), self.expected_project_count)

        (
            project,
            project_computed_file,
            project_summary,
            sample,
            sample_computed_file,
        ) = self.assert_project(self.scpca_project_id)

        # Next, let's make sure that reload_existing=False won't add anything
        # new when there's nothing new.
        load_data_from_s3(
            update_s3_data=False,
            reload_all=False,
            reload_existing=False,
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
        )
        self.assertEqual(Project.objects.count(), self.expected_project_count)
        self.assertEqual(ProjectSummary.objects.count(), self.expected_summary_count)
        self.assertEqual(Sample.objects.count(), self.expected_sample_count)
        self.assertEqual(ComputedFile.objects.count(), self.expected_computed_file_count)

        # project, project_computed_file, project_summary, sample, and
        # sample_computed_file all still reference the what was loaded
        # in the first call.
        new_project = Project.objects.get(scpca_id=self.scpca_project_id)
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())
        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)
        self.assertEqual(project_computed_file, new_project.computed_file)
        self.assertEqual(sample_computed_file, new_sample.computed_file)

        # Next, this is a good place to test the purge command since we
        # have data to purge.
        new_project.purge()
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Finally, let's make sure that loading, purging, and then
        # reloading works smoothly.
        load_data_from_s3(
            update_s3_data=False,
            reload_all=False,
            reload_existing=True,
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
        )
        self.assertEqual(Project.objects.count(), self.expected_project_count)
        self.assertEqual(ProjectSummary.objects.count(), self.expected_summary_count)
        self.assertEqual(Sample.objects.count(), self.expected_sample_count)
        self.assertEqual(ComputedFile.objects.count(), self.expected_computed_file_count)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_single_cell_metadata(self):
        expected_keys = {
            "age",
            "alevin_fry_version",
            "cell_count",
            "date_processed",
            "diagnosis",
            "disease_timing",
            "filtered_cell_count",
            "genome_assembly",
            "has_citeseq",
            "mapped_reads",
            "mapping_index",
            "metastasis",
            "participant_id",
            "pi_name",
            "project_title",
            "relapse_status",
            "salmon_version",
            "scpca_library_id",
            "scpca_project_id",
            "scpca_sample_id",
            "seq_unit",
            "sex",
            "subdiagnosis",
            "submitter_id",
            "submitter",
            "technology",
            "tissue_location",
            "total_reads",
            "transcript_type",
            "treatment",
            "unfiltered_cells",
            "vital_status",
            "workflow_commit",
            "workflow_version",
            "workflow",
        }

        # First, just test that loading data works.
        load_data_from_s3(
            update_s3_data=True,
            reload_all=False,
            reload_existing=False,
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
        )

        self.assertEqual(Project.objects.count(), self.expected_project_count)
        self.assert_project(self.scpca_project_id)
        new_project = Project.objects.get(scpca_id=self.scpca_project_id)

        with ZipFile(new_project.output_single_cell_data_file_path) as project_zip:
            sample_metadata = project_zip.read(
                ComputedFile.FileNames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = sample_metadata.decode("utf-8").split("\r\n")

        # 1 item + header.
        self.assertTrue(len(sample_metadata_lines), 2)
        sample_metadata_keys = set(sample_metadata_lines[0].split(common.TAB))

        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are three files for each sample, plus a README.md
        # and a single_cell_metadata.tsv file.
        # 1 * 3 + 2 = 5
        self.assertEqual(len(project_zip.namelist()), 5)

        sample = new_project.samples.first()
        with ZipFile(sample.output_single_cell_data_file_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.FileNames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].keys(), expected_keys)
        scpca_library_id = rows[0]["scpca_library_id"]

        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{scpca_library_id}_unfiltered.rds",
            f"{scpca_library_id}_filtered.rds",
            f"{scpca_library_id}_qc.html",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_spatial_metadata(self):
        # First, just test that loading data works.
        load_data_from_s3(
            update_s3_data=True,
            reload_all=False,
            reload_existing=False,
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
        )

        self.assertEqual(Project.objects.count(), 1)
        self.assert_project(self.scpca_project_id)
        new_project = Project.objects.get(scpca_id=self.scpca_project_id)

        expected_keys = {
            "age",
            "BRAF_status",
            "date_processed",
            "diagnosis",
            "disease_timing",
            "genome_assembly",
            "mapped_reads",
            "mapping_index",
            "metastasis",
            "participant_id",
            "pi_name",
            "project_title",
            "relapse_status",
            "scpca_library_id",
            "scpca_project_id",
            "scpca_sample_id",
            "seq_unit",
            "sex",
            "spaceranger_version",
            "spinal_leptomeningeal_mets",
            "subdiagnosis",
            "submitter_id",
            "submitter",
            "technology",
            "tissue_location",
            "total_reads",
            "treatment",
            "vital_status",
            "workflow_commit",
            "workflow_version",
            "workflow",
        }

        with ZipFile(new_project.output_spatial_data_file_path) as project_zip:
            spatial_metadata_file = project_zip.read(
                ComputedFile.FileNames.SPATIAL_METADATA_FILE_NAME
            )
            spatial_metadata = spatial_metadata_file.decode("utf-8").split("\r\n")
            # 2 items + header.
            self.assertTrue(len(spatial_metadata), 3)
            spatial_metadata_keys = set(spatial_metadata[0].split(common.TAB))

            self.assertEqual(spatial_metadata_keys, expected_keys)

            # There are 17 files for each spatial library (including
            # subdirectories), plus a README.md and a spatial_metadata.tsv file.
            # 2 * 17 + 2 = 36
            self.assertEqual(len(project_zip.namelist()), 36)

        sample = new_project.samples.first()
        with ZipFile(sample.output_spatial_data_file_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.FileNames.SPATIAL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        expected_library_count = 2
        self.assertEqual(len(rows), expected_library_count)
        self.assertEqual(rows[0].keys(), expected_keys)

        scpca_library_ids = (rows[0]["scpca_library_id"], rows[1]["scpca_library_id"])

        expected_filenames = {
            "README.md",
            "spatial_metadata.tsv",
        }

        library_filename_templates = {
            "{library_id}_spatial/{library_id}_metadata.json",
            "{library_id}_spatial/{library_id}_spaceranger_summary.html",
            "{library_id}_spatial/filtered_feature_bc_matrix/",
            "{library_id}_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/",
            "{library_id}_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
            "{library_id}_spatial/spatial/",
            "{library_id}_spatial/spatial/aligned_fiducials.jpg",
            "{library_id}_spatial/spatial/detected_tissue_image.jpg",
            "{library_id}_spatial/spatial/scalefactors_json.json",
            "{library_id}_spatial/spatial/tissue_hires_image.png",
            "{library_id}_spatial/spatial/tissue_lowres_image.png",
            "{library_id}_spatial/spatial/tissue_positions_list.csv",
        }
        for scpca_library_id in scpca_library_ids:
            for library_filename_template in library_filename_templates:
                expected_filenames.add(
                    library_filename_template.format(library_id=scpca_library_id)
                )

        self.assertEqual(set(sample_zip.namelist()), expected_filenames)
