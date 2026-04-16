from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models import ComputedFile, UserDataset
from scpca_portal.test.factories import LeafComputedFileFactory, UserDatasetFactory


class TestUserDataset(TestCase):
    @classmethod
    def setUpTestData(cls):
        bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        call_command("sync_original_files", bucket=bucket)

        loader.download_projects_metadata()
        project_ids = metadata_parser.get_projects_metadata_ids(bucket=bucket)

        loader.download_projects_related_metadata(project_ids)
        for project_metadata in metadata_parser.load_projects_metadata(project_ids):
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=bucket,
                reload_existing=True,
                update_s3=False,
            )

    def test_get_total_sample_count(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [
                    "SCPCS999990",
                    "SCPCS999991",
                    "SCPCS999994",
                    "SCPCS999997",
                ],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }

        expected_count = 9
        actual_count = dataset.get_total_sample_count()

        self.assertEqual(actual_count, expected_count)

    def test_get_diagnoses_summary(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }

        expected_counts = {
            "diagnosis1": {"samples": 1, "projects": 1},
            "diagnosis2": {"samples": 1, "projects": 1},
            "diagnosis3": {"samples": 1, "projects": 1},
            "diagnosis4": {"samples": 1, "projects": 1},
            "diagnosis5": {"samples": 1, "projects": 1},
            "diagnosis6": {"samples": 1, "projects": 1},
            "diagnosis7": {"samples": 2, "projects": 1},
        }

        summary = dataset.get_diagnoses_summary()

        # assert that that all diagnoses match exactly
        self.assertEqual(summary.keys(), expected_counts.keys())

        for key in expected_counts.keys():
            self.assertEqual(
                summary[key]["projects"],
                expected_counts[key]["projects"],
                f"Mismatch in {key} projects",
            )
            self.assertEqual(
                summary[key]["samples"],
                expected_counts[key]["samples"],
                f"Mismatch in {key} samples",
            )

    def test_get_files_summary(self):
        single_cell_dataset = UserDataset(
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
            data={
                "SCPCP999990": {
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL: ["SCPCS999991"],
                },
                "SCPCP999991": {
                    "includes_bulk": False,
                    Modalities.SINGLE_CELL: [
                        "SCPCS999992",
                        "SCPCS999993",
                        "SCPCS999995",
                    ],
                    Modalities.SPATIAL: [],
                },
                "SCPCP999992": {
                    "includes_bulk": False,
                    Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL: [],
                },
            },
        )

        # TODO: This test should cover all potential counts
        expected_single_cell = [
            {"samples_count": 4, "name": "Single-cell samples", "format": ".rds"},
            # Single-nuclei should be included here
            {"samples_count": 1, "name": "Single-cell samples with CITE-seq", "format": ".rds"},
            # Single-cell multiplexed should be included here
            {"samples_count": 2, "name": "Single-nuclei multiplexed samples", "format": ".rds"},
            {"samples_count": 1, "name": "Spatial samples", "format": "Spaceranger"},
            {"samples_count": 1, "name": "Bulk RNA-seq samples", "format": ".tsv"},
        ]

        single_cell_files_summary = single_cell_dataset.get_files_summary()

        self.assertEqual(len(single_cell_files_summary), len(expected_single_cell))

        for actual, expected in zip(single_cell_files_summary, expected_single_cell):
            self.assertEqual(actual["name"], expected["name"])
            self.assertEqual(
                actual["samples_count"], expected["samples_count"], f" in {actual['name']}"
            )
            self.assertEqual(actual["format"], expected["format"], f" in {actual['name']}")

        ann_data_dataset = UserDataset(
            format=DatasetFormats.ANN_DATA,
            data={
                "SCPCP999990": {
                    "includes_bulk": True,
                    Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                    Modalities.SPATIAL: [],
                },
                "SCPCP999991": {
                    "includes_bulk": False,
                    Modalities.SINGLE_CELL: [
                        "SCPCS999995",
                    ],
                    Modalities.SPATIAL: [],
                },
                "SCPCP999992": {
                    "includes_bulk": False,
                    Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                    Modalities.SPATIAL: [],
                },
            },
        )

        expected_ann_data = [
            {"samples_count": 4, "name": "Single-cell samples", "format": ".h5ad"},
            {"samples_count": 1, "name": "Single-cell samples with CITE-seq", "format": ".h5ad"},
            {"samples_count": 1, "name": "Bulk RNA-seq samples", "format": ".tsv"},
        ]

        ann_data_files_summary = ann_data_dataset.get_files_summary()

        for actual, expected in zip(ann_data_files_summary, expected_ann_data):
            self.assertEqual(actual["name"], expected["name"])
            self.assertEqual(
                actual["samples_count"], expected["samples_count"], f" in {actual['name']}"
            )
            self.assertEqual(actual["format"], expected["format"], f" in {actual['name']}")

    def test_get_project_diagnoses(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }

        expected_counts = {
            "SCPCP999990": {"diagnosis5": 1, "diagnosis1": 1, "diagnosis2": 1},
            "SCPCP999991": {"diagnosis4": 1, "diagnosis3": 1, "diagnosis6": 1},
            "SCPCP999992": {"diagnosis7": 2},
        }

        actual_counts = dataset.get_project_diagnoses()

        for project_id in actual_counts.keys():
            for diagnosis in actual_counts[project_id].keys():
                self.assertEqual(
                    actual_counts[project_id][diagnosis], expected_counts[project_id][diagnosis]
                )

    def test_get_project_modality_counts(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        # Dataset requesting single cell and spatial data containing a project with both
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }
        expected_counts = {
            "SCPCP999990": {
                Modalities.SINGLE_CELL: 2,
                Modalities.SPATIAL: 1,
                Modalities.BULK_RNA_SEQ: 1,
            },
        }
        self.assertEqual(dataset.get_project_modality_counts(), expected_counts)

        # Dataset requesting only single cell data containing a project that also has spatial
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        expected_counts = {
            "SCPCP999990": {
                Modalities.SINGLE_CELL: 2,
                Modalities.SPATIAL: 0,
                Modalities.BULK_RNA_SEQ: 1,
            },
        }
        self.assertEqual(dataset.get_project_modality_counts(), expected_counts)

        # Dataset requesting only single cell data containing a project without spatial
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
        }
        expected_counts = {"SCPCP999991": {Modalities.SINGLE_CELL: 3}}  # No spatial kv pair
        self.assertEqual(dataset.get_project_modality_counts(), expected_counts)

        # Dataset requesting single cell and spatial data containing some projects that
        # have both single cell and spatial and others that just have single cell
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }

        expected_counts = {
            "SCPCP999990": {
                Modalities.SINGLE_CELL: 2,
                Modalities.SPATIAL: 1,
                Modalities.BULK_RNA_SEQ: 1,
            },
            "SCPCP999991": {
                Modalities.SINGLE_CELL: 3,
            },
            "SCPCP999992": {
                Modalities.SINGLE_CELL: 2,
            },
        }
        self.assertEqual(dataset.get_project_modality_counts(), expected_counts)

    def test_modality_count_mismatch_projects(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: [],
            },
        }

        expected_mismatch_projects = ["SCPCP999990"]

        actual_mismatch_projects = dataset.get_modality_count_mismatch_projects()

        self.assertCountEqual(actual_mismatch_projects, expected_mismatch_projects)

    def test_project_sample_counts(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }

        expected_counts = {"SCPCP999990": 3, "SCPCP999991": 3, "SCPCP999992": 2}

        actual_counts = dataset.get_project_sample_counts()

        self.assertEqual(actual_counts, expected_counts)

    def test_get_project_titles(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [
                    "SCPCS999992",
                    "SCPCS999993",
                    "SCPCS999995",
                ],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }

        # TODO: Update so that fake project titles are unique.
        expected_titles = {
            "SCPCP999990": "Title1",
            "SCPCP999991": "Title2",
            "SCPCP999992": "Title3",
        }

        actual_titles = dataset.get_project_titles()

        for project_id in actual_titles.keys():
            self.assertEqual(actual_titles[project_id], expected_titles[project_id])

    @patch("scpca_portal.models.computed_file.utils.get_today_string", return_value="2025-08-26")
    @patch("scpca_portal.s3.aws_s3.generate_presigned_url")
    def test_download_url_property(self, mock_generate_presigned_url, _):
        dataset = UserDatasetFactory(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.computed_file = LeafComputedFileFactory(
            s3_key=ComputedFile.get_dataset_file_s3_key(dataset)
        )
        dataset.save()

        dataset.download_url
        expected_filename = f"{dataset.id}_single-cell-experiment_2025-08-26.zip"
        mock_generate_presigned_url.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": "scpca-portal-local",
                "Key": f"{dataset.id}.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        # no computed file
        dataset = UserDatasetFactory()
        self.assertIsNone(dataset.download_url)
