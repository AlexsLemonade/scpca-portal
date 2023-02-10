import csv
import os
import shutil
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
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_DIR, ignore_errors=True)

    def assert_project(self, project):
        self.assertTrue(project.abstract)
        self.assertIsNotNone(project.contacts)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.diagnoses_counts)
        self.assertTrue(project.disease_timings)
        self.assertIsNotNone(project.seq_units)
        self.assertTrue(project.title)

        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)

        sample = project.samples.first()
        self.assertIsNotNone(sample.age_at_diagnosis)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.disease_timing)
        self.assertTrue(sample.scpca_id)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.treatment)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_load_data_from_s3(self):
        def assert_object_count():
            self.assertEqual(Project.objects.count(), 2)
            self.assertEqual(ProjectSummary.objects.count(), 6)
            self.assertEqual(Sample.objects.count(), 5)
            self.assertEqual(ComputedFile.objects.count(), 9)

        # First, just test that loading data works.
        load_data_from_s3(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            reload_all=False,
            reload_existing=False,
            update_s3_data=False,
        )
        assert_object_count()

        scpca_project_ids = ("SCPCP999990", "SCPCP999999")
        for scpca_project_id in scpca_project_ids:
            project = Project.objects.get(scpca_id=scpca_project_id)
            project_computed_files = project.computed_files
            project_summary = project.summaries.first()
            sample = project.samples.first()
            sample_computed_files = sample.computed_files

            self.assert_project(project)

            # Make sure that reload_existing=False won't add anything
            # new when there's nothing new.
            load_data_from_s3(
                allowed_submitters=ALLOWED_SUBMITTERS,
                input_bucket_name=INPUT_BUCKET_NAME,
                reload_all=False,
                reload_existing=False,
                update_s3_data=False,
            )
            assert_object_count()

            new_project = Project.objects.get(scpca_id=scpca_project_id)
            self.assertEqual(project, new_project)
            self.assertEqual(project_summary, new_project.summaries.first())

            new_sample = new_project.samples.first()
            self.assertEqual(sample, new_sample)
            self.assertEqual(list(project_computed_files), list(new_project.computed_files))
            self.assertEqual(list(sample_computed_files), list(new_sample.computed_files))

        # Make sure purging works as expected.
        for scpca_project_id in scpca_project_ids:
            Project.objects.get(scpca_id=scpca_project_id).purge()

        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Make sure reloading works smoothly.
        load_data_from_s3(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            reload_all=False,
            reload_existing=True,
            update_s3_data=False,
        )
        assert_object_count()

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_multiplexed_metadata(self):
        load_data_from_s3(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            reload_all=False,
            reload_existing=False,
            update_s3_data=True,
        )

        project = Project.objects.get(scpca_id="SCPCP999990")
        self.assert_project(project)
        self.assertEqual(project.downloadable_sample_count, 4)
        self.assertTrue(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_multiplexed_data)
        self.assertFalse(project.has_spatial_data)
        self.assertEqual(project.multiplexed_sample_count, 4)
        self.assertEqual(project.sample_count, 4)
        self.assertEqual(project.summaries.count(), 2)
        self.assertEqual(project.summaries.first().sample_count, 2)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(len(project.computed_files), 1)
        self.assertGreater(project.multiplexed_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.multiplexed_computed_file.workflow_version,
            "development",
        )

        # Check contacts.
        self.assertEqual(project.contacts.count(), 2)
        contact1, contact2 = project.contacts.all()
        self.assertEqual(contact1.name, "<contact 1>")
        self.assertEqual(contact1.email, "<email contact 1>")
        self.assertEqual(contact2.name, "<contact 2>")
        self.assertEqual(contact2.email, "<email contact 2>")

        # Check citations.
        self.assertEqual(project.publications.count(), 2)
        publication, publication2 = project.publications.all()
        self.assertEqual(publication.doi, "<doi 1>")
        self.assertEqual(publication.citation, "<formatted citation 1>")
        self.assertEqual(publication2.doi, "<doi 2>")
        self.assertEqual(publication2.citation, "<formatted citation 2>")

        expected_keys = [
            "scpca_sample_id",
            "scpca_library_id",
            "scpca_project_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter",
            "submitter_id",
            "alevin_fry_version",
            "cell_filtering_method",
            "demux_method",
            "demux_samples",
            "droplet_filtering_method",
            "filtered_cells",
            "has_cellhash",
            "is_multiplexed",
            "min_gene_cutoff",
            "normalization_method",
            "prob_compromised_cutoff",
            "salmon_version",
            "sample_cell_estimates",
            "transcript_type",
            "unfiltered_cells",
            "WHO_grade",
        ]

        project_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, project.output_multiplexed_computed_file_name
        )
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]

        self.assertEqual(len(sample_metadata_lines), 5)  # 4 items + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        library_sample_mapping = {
            "SCPCL999990": "SCPCS999990_SCPCS999991",
            "SCPCL999991": "SCPCS999992_SCPCS999993",
        }
        library_path_templates = (
            "{sample_id}/{library_id}_filtered.rds",
            "{sample_id}/{library_id}_processed.rds",
            "{sample_id}/{library_id}_qc.html",
            "{sample_id}/{library_id}_unfiltered.rds",
        )
        expected_filenames = {
            "README.md",
            "bulk_metadata.tsv",
            "bulk_quant.tsv",
            "single_cell_metadata.tsv",
        }
        for library_id, sample_id in library_sample_mapping.items():
            for library_path in library_path_templates:
                expected_filenames.add(
                    library_path.format(library_id=library_id, sample_id=sample_id)
                )
        self.assertEqual(set(project_zip.namelist()), expected_filenames)

        sample = project.samples.filter(has_multiplexed_data=True).first()
        self.assertIsNone(sample.sample_cell_count_estimate)
        self.assertEqual(sample.demux_cell_count_estimate, 2841)
        self.assertTrue(sample.has_multiplexed_data)
        self.assertEqual(sample.seq_units, "nucleus")
        self.assertEqual(sample.technologies, "10Xv3.1")

        expected_additional_metadata_keys = [
            "participant_id",
            "scpca_project_id",
            "submitter",
            "submitter_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        sample_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, sample.output_multiplexed_computed_file_name
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_single_cell_metadata(self):
        load_data_from_s3(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            reload_all=False,
            reload_existing=False,
            update_s3_data=True,
        )

        project = Project.objects.get(scpca_id="SCPCP999999")
        self.assert_project(project)
        self.assertEqual(project.downloadable_sample_count, 1)
        self.assertFalse(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertFalse(project.has_multiplexed_data)
        self.assertTrue(project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 0)
        self.assertEqual(project.sample_count, 1)
        self.assertEqual(project.seq_units, "nucleus, spot")
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(len(project.computed_files), 2)
        self.assertGreater(project.single_cell_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.single_cell_computed_file.workflow_version,
            "v0.2.7",
        )
        self.assertEqual(project.technologies, "10Xv3.1, visium")

        expected_keys = [
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "seq_unit",
            "technology",
            "sample_cell_count_estimate",
            "scpca_project_id",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "alevin_fry_version",
            "cell_filtering_method",
            "date_processed",
            "droplet_filtering_method",
            "filtered_cell_count",
            "genome_assembly",
            "has_cellhash",
            "is_multiplexed",
            "mapped_reads",
            "mapping_index",
            "min_gene_cutoff",
            "normalization_method",
            "participant_id",
            "prob_compromised_cutoff",
            "salmon_version",
            "submitter",
            "submitter_id",
            "total_reads",
            "transcript_type",
            "treatment",
            "unfiltered_cells",
            "upload_date",
            "workflow",
            "workflow_commit",
            "workflow_version",
        ]

        project_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, project.output_single_cell_computed_file_name
        )
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]

        self.assertEqual(len(sample_metadata_lines), 2)  # 1 item + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are 4 files for each sample, plus a README.md
        # and a single_cell_metadata.tsv file.
        # 6 = 1 * 4 + 2
        self.assertEqual(len(project_zip.namelist()), 6)

        sample = project.samples.filter(has_single_cell_data=True).first()
        self.assertEqual(len(sample.computed_files), 2)
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        self.assertFalse(project.has_multiplexed_data)
        self.assertTrue(sample.has_spatial_data)
        self.assertEqual(sample.sample_cell_count_estimate, 23751)
        self.assertEqual(sample.seq_units, "nucleus, spot")
        self.assertIsNotNone(sample.single_cell_computed_file)
        self.assertGreater(sample.single_cell_computed_file.size_in_bytes, 0)
        self.assertEqual(
            sample.single_cell_computed_file.workflow_version,
            "v0.2.7",
        )
        self.assertEqual(sample.technologies, "10Xv3.1, visium")

        expected_additional_metadata_keys = [
            "participant_id",
            "scpca_project_id",
            "submitter",
            "submitter_id",
            "upload_date",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        sample_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, sample.output_single_cell_computed_file_name
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_spatial_metadata(self):
        load_data_from_s3(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            reload_all=False,
            reload_existing=False,
            update_s3_data=True,
        )

        project = Project.objects.get(scpca_id="SCPCP999999")
        self.assert_project(project)
        self.assertEqual(project.downloadable_sample_count, 1)
        self.assertFalse(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertFalse(project.has_multiplexed_data)
        self.assertTrue(project.has_spatial_data)
        self.assertTrue(project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 0)
        self.assertEqual(project.sample_count, 1)
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(len(project.computed_files), 2)
        self.assertGreater(project.spatial_computed_file.size_in_bytes, 0)
        self.assertEqual(project.spatial_computed_file.workflow_version, "v0.2.7")

        expected_keys = [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "spaceranger_version",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "treatment",
            "participant_id",
            "submitter",
            "submitter_id",
            "upload_date",
        ]

        project_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, project.output_spatial_computed_file_name
        )
        with ZipFile(project_zip_path) as project_zip:
            spatial_metadata_file = project_zip.read(
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME
            )
            spatial_metadata = [
                sm for sm in spatial_metadata_file.decode("utf-8").split("\r\n") if sm
            ]

        self.assertEqual(len(spatial_metadata), 2)  # 1 item + header.

        spatial_metadata_keys = spatial_metadata[0].split(common.TAB)
        self.assertEqual(spatial_metadata_keys, expected_keys)

        # There are 17 files for each spatial library (including
        # subdirectories), plus a README.md and a spatial_metadata.tsv file.
        # 19 = 1 * 17 + 2
        self.assertEqual(len(project_zip.namelist()), 19)

        sample = project.samples.filter(has_spatial_data=True).first()
        self.assertEqual(len(sample.computed_files), 2)
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        self.assertFalse(sample.has_multiplexed_data)
        self.assertTrue(sample.has_spatial_data)
        self.assertEqual(sample.sample_cell_count_estimate, 23751)
        self.assertEqual(sample.seq_units, "nucleus, spot")
        self.assertIsNotNone(sample.spatial_computed_file)
        self.assertGreater(sample.spatial_computed_file.size_in_bytes, 0)
        self.assertEqual(
            sample.spatial_computed_file.workflow_version,
            "v0.2.7",
        )
        self.assertEqual(sample.technologies, "10Xv3.1, visium")

        expected_additional_metadata_keys = [
            "participant_id",
            "scpca_project_id",
            "submitter",
            "submitter_id",
            "upload_date",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        sample_zip_path = os.path.join(
            common.OUTPUT_DATA_DIR, sample.output_spatial_computed_file_name
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_ids = (rows[0]["scpca_library_id"],)
        expected_filenames = {
            "README.md",
            "spatial_metadata.tsv",
        }
        library_path_templates = {
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
        for library_id in library_ids:
            for library_path in library_path_templates:
                expected_filenames.add(library_path.format(library_id=library_id))
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)
