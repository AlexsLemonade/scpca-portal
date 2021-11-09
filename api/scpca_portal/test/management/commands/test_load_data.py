import csv
import os
from io import TextIOWrapper
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TestCase

from scpca_portal.management.commands.load_data import OUTPUT_DIR, load_data_from_s3
from scpca_portal.management.commands.purge_project import purge_project
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample


class MockS3Client:
    def __init__(self, *args, **kwargs):
        pass

    def upload_file(self, path, bucket, key):
        # Don't actually upload because this is a test.
        pass

    def list_objects(self, *args, **kwargs):
        return {"Contents": [{"Size": 1111}]}


class LoadDataTestCase(TestCase):
    def assert_project(self, scpca_project_id, upload_data):
        project = Project.objects.get(scpca_id=scpca_project_id)

        self.assertIsNotNone(project.title)
        self.assertIsNotNone(project.abstract)
        self.assertIsNotNone(project.contact)
        self.assertIsNotNone(project.disease_timings)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.seq_units)
        self.assertIsNotNone(project.technologies)
        self.assertEqual(project.sample_count, 38)
        self.assertEqual(project.summaries.count(), 1)

        self.assertEqual(ProjectSummary.objects.count(), 1)
        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)
        self.assertEqual(project_summary.sample_count, 38)

        self.assertEqual(Sample.objects.count(), 38)
        sample = project.samples.first()
        self.assertIsNotNone(sample.has_cite_seq_data)
        self.assertIsNotNone(sample.scpca_id)
        self.assertIsNotNone(sample.technologies)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.age_at_diagnosis)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.disease_timing)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.cell_count)
        self.assertIsNotNone(sample.seq_units)

        expected_keys = {
            "submitter",
            "treatment",
            "metastasis",
            "submitter_id",
            "vital_status",
            "participant_id",
            "relapse_status",
            "scpca_project_id",
        }
        self.assertEqual(set(sample.additional_metadata.keys()), expected_keys)

        self.assertEqual(ComputedFile.objects.count(), 39)
        project_computed_file = project.computed_file
        self.assertIsNotNone(project_computed_file)
        sample_computed_file = sample.computed_file
        self.assertIsNotNone(sample_computed_file)

        if upload_data:
            # The test files are empty, and this was recorded because
            # upload_data was true.
            self.assertEqual(project_computed_file.size_in_bytes, 0)
            self.assertEqual(sample_computed_file.size_in_bytes, 0)
        else:
            # These will have checked the bucket for local dev to get
            # the size of the files it contains.
            self.assertGreater(project_computed_file.size_in_bytes, 0)
            self.assertGreater(sample_computed_file.size_in_bytes, 0)

        return project, project_computed_file, project_summary, sample, sample_computed_file

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_load_data_from_s3_no_upload(self):
        scpca_project_id = "SCPCP000006"
        upload_data = False
        # First, just test that loading data works.
        load_data_from_s3(
            upload_data,
            False,
            False,
            "scpca-portal-public-test-inputs",
            "/home/user/code/test_data/",
        )

        # The whitelist currently allows 3 projects:
        self.assertEqual(Project.objects.count(), 3)

        (
            project,
            project_computed_file,
            project_summary,
            sample,
            sample_computed_file,
        ) = self.assert_project(scpca_project_id, upload_data)

        # Next, let's make sure that reload_existing=False won't add anything
        # new when there's nothing new.
        load_data_from_s3(
            False, False, False, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )
        self.assertEqual(Project.objects.count(), 3)
        self.assertEqual(ProjectSummary.objects.count(), 1)
        self.assertEqual(Sample.objects.count(), 38)
        self.assertEqual(ComputedFile.objects.count(), 39)

        # project, project_computed_file, project_summary, sample, and
        # sample_computed_file all still reference the what was loaded
        # in the first call.
        new_project = Project.objects.get(scpca_id="SCPCP000006")
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())
        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)
        self.assertEqual(project_computed_file, new_project.computed_file)
        self.assertEqual(sample_computed_file, new_sample.computed_file)

        # Next, this is a good place to test he purge command since we
        # have data to purge.
        purge_project(scpca_project_id)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Finally, let's make sure that loading, purging, and then
        # reloading works smoothly.
        load_data_from_s3(
            False, True, False, "scpca-portal-public-test-inputs", "/home/user/code/test_data/"
        )
        self.assertEqual(Project.objects.count(), 3)
        self.assertEqual(ProjectSummary.objects.count(), 1)
        self.assertEqual(Sample.objects.count(), 38)
        self.assertEqual(ComputedFile.objects.count(), 39)

    @patch("scpca_portal.management.commands.load_data.s3", MockS3Client())
    def test_load_data_from_s3_with_upload(self):
        # mock_boto3.client.return_value = MockS3Client()
        scpca_project_id = "SCPCP000006"
        upload_data = True
        # First, just test that loading data works.
        load_data_from_s3(
            upload_data,
            False,
            False,
            "scpca-portal-public-test-inputs",
            "/home/user/code/test_data/",
        )

        # The whitelist currently allows 3 projects:
        self.assertEqual(Project.objects.count(), 3)

        self.assert_project(scpca_project_id, upload_data)

        new_project = Project.objects.get(scpca_id=scpca_project_id)

        project_zip_path = os.path.join(OUTPUT_DIR, new_project.scpca_id + ".zip")
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read("libraries_metadata.csv")
            sample_metadata_lines = sample_metadata.decode("utf-8").split("\r\n")
            # 38 samples and a header.
            self.assertTrue(len(sample_metadata_lines), 39)
            sample_metadata_keys = set(sample_metadata_lines[0].split(","))
            expected_keys = {
                "seq_unit",
                "scpca_library_id",
                "salmon_version",
                "transcript_type",
                "project_title",
                "disease_timing",
                "workflow",
                "pi_name",
                "has_citeseq",
                "scpca_sample_id",
                "tissue_location",
                "date_processed",
                "subdiagnosis",
                "unfiltered_cells",
                "genome_assembly",
                "alevin_fry_version",
                "age",
                "vital_status",
                "submitter",
                "mapping_index",
                "scpca_project_id",
                "filtered_cell_count",
                "participant_id",
                "cell_count",
                "workflow_version",
                "submitter_id",
                "relapse_status",
                "technology",
                "treatment",
                "sex",
                "metastasis",
                "workflow_commit",
                "total_reads",
                "diagnosis",
                "mapped_reads",
            }

            self.assertEqual(sample_metadata_keys, expected_keys)

            # There are three files for each sample, plus a README.md
            # and a libraries_metadata.csv file.
            # 38 * 3 + 2 = 116
            self.assertEqual(len(project_zip.namelist()), 116)

        test_sample = new_project.samples.first()

        sample_zip_path = os.path.join(OUTPUT_DIR, test_sample.scpca_id + ".zip")

        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open("libraries_metadata.csv", "r") as sample_csv:
                csv_reader = csv.DictReader(TextIOWrapper(sample_csv, "utf-8"))
                rows = []
                for row in csv_reader:
                    rows.append(row)

            # sample_metadata = sample_zip.read("libraries_metadata.csv")
            # sample_metadata_lines = sample_metadata.decode("utf-8").split("\r\n")
            self.assertTrue(len(rows), 1)
            expected_keys = {
                "scpca_sample_id",
                "scpca_library_id",
                "diagnosis",
                "subdiagnosis",
                "seq_unit",
                "technology",
                "filtered_cell_count",
                "scpca_project_id",
                "pi_name",
                "project_title",
                "disease_timing",
                "age",
                "sex",
                "tissue_location",
                "unfiltered_cells",
                "treatment",
                "participant_id",
                "submitter_id",
                "genome_assembly",
                "relapse_status",
                "mapping_index",
                "total_reads",
                "metastasis",
                "date_processed",
                "vital_status",
                "workflow",
                "workflow_version",
                "submitter",
                "transcript_type",
                "workflow_commit",
                "salmon_version",
                "alevin_fry_version",
                "has_citeseq",
                "cell_count",
                "mapped_reads",
            }

            self.assertEqual(rows[0].keys(), expected_keys)
            scpca_library_id = rows[0]["scpca_library_id"]

            expected_filenames = {
                "libraries_metadata.csv",
                "README.md",
                f"{scpca_library_id}_unfiltered.rds",
                f"{scpca_library_id}_filtered.rds",
                f"{scpca_library_id}_qc.html",
            }
            self.assertEqual(set(sample_zip.namelist()), expected_filenames)
