import random
import sys
from pathlib import Path
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, FileFormats, Modalities
from scpca_portal.models import CCDLDataset, OriginalFile, Project, UserDataset
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import OriginalFileFactory


class TestDatasetABC(TestCase):
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

    def test_original_files_property(self):
        # SINGLE_CELL SCE
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        ccdl_name = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT
        dataset = CCDLDataset(data=data, format=format, ccdl_name=ccdl_name)

        expected_files = {
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_processed.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_qc.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_filtered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_processed.rds"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # SINGLE_CELL ANN_DATA
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.ANN_DATA
        ccdl_name = CCDLDatasetNames.SINGLE_CELL_ANN_DATA
        dataset = CCDLDataset(data=data, format=format, ccdl_name=ccdl_name)

        expected_files = {
            Path("SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_qc.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_processed_rna.h5ad"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_unfiltered_rna.h5ad"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_filtered_rna.h5ad"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_processed_rna.h5ad"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_unfiltered_rna.h5ad"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # SINGLE_CELL SCE MERGED
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        ccdl_name = CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED
        dataset = CCDLDataset(data=data, format=format, ccdl_name=ccdl_name)

        expected_files = {
            Path("SCPCP999990/merged/SCPCP999990_merged.rds"),
            Path("SCPCP999990/merged/SCPCP999990_merged-summary-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_qc.html"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # SINGLE_CELL ANN_DATA MERGED
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.ANN_DATA
        ccdl_name = CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED
        dataset = CCDLDataset(data=data, format=format, ccdl_name=ccdl_name)

        expected_files = {
            Path("SCPCP999990/SCPCS999997/SCPCL999997_qc.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html"),
            Path("SCPCP999990/merged/SCPCP999990_merged-summary-report.html"),
            Path("SCPCP999990/merged/SCPCP999990_merged_rna.h5ad"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # SPATIAL SPATIAL_SPACERANGER
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }
        format = FileFormats.SPATIAL_SPACERANGER
        ccdl_name = CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER
        dataset = CCDLDataset(data=data, format=format, ccdl_name=ccdl_name)

        expected_files = {
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz"
            ),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json"),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv"),
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz"  # noqa
            ),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz"),
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz"  # noqa
            ),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json"),
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz"
            ),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png"),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png"),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg"),
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz"  # noqa
            ),
            Path(
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html"
            ),
            Path("SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # BULK
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT.value
        dataset = UserDataset(data=data, format=format)

        expected_files = {
            Path("SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv"),
            Path("SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # MIXED USAGE
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999997"],
            },
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT.value
        dataset = UserDataset(data=data, format=format)

        expected_files = {
            Path("SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv"),
            Path("SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_processed.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_filtered.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_unfiltered.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_processed.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_qc.html"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_celltype-report.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_unfiltered.rds"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_processed.rds"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_celltype-report.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_qc.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_filtered.rds"),
            Path("SCPCP999992/merged/SCPCP999992_merged.rds"),
            Path("SCPCP999992/merged/SCPCP999992_merged-summary-report.html"),
            Path("SCPCP999992/SCPCS999996/SCPCL999996_celltype-report.html"),
            Path("SCPCP999992/SCPCS999996/SCPCL999996_qc.html"),
            Path("SCPCP999992/SCPCS999998/SCPCL999998_celltype-report.html"),
            Path("SCPCP999992/SCPCS999998/SCPCL999998_qc.html"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

    def test_current_data_hash(self):
        mock_file_hashes = {
            "SCPCP000000/SCPCS000000/SCPCL00003.txt": "d4adfj59xe4e1zf9tdgipefc38ihmesm",
            "SCPCP000000/SCPCS000000/SCPCL00002.txt": "feh8wcvjx9wxmbi9lvunep6n6sy8eekr",
            "SCPCP000000/SCPCS000000/SCPCL00005.txt": "at7n9m9cg3hev5evhrgev1y63tgzqhem",
            "SCPCP000000/SCPCS000000/SCPCL00001.txt": "8on83svty5lacm10nqavmqpz9zcoxq2d",
            "SCPCP000000/SCPCS000000/SCPCL00004.txt": "iekahu4fjio931yyiej5esqfizrunhkf",
        }
        for s3_key, file_hash in mock_file_hashes.items():
            OriginalFileFactory(s3_key=s3_key, hash=file_hash)
        mock_original_files = OriginalFile.objects.filter(s3_key__in=mock_file_hashes.keys())

        with patch.object(
            UserDataset,
            "original_files",
            new_callable=PropertyMock,
            return_value=mock_original_files,
        ):
            dataset = UserDataset()
            expected_data_hash = "2827e1b0bb8116cfd7f15e787d0d0dbc"
            self.assertEqual(dataset.current_data_hash, expected_data_hash)

    def test_current_metadata_hash(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT.value
        dataset = UserDataset(data=data, format=format)

        # TODO: add to expected_values dataset file (along with other hash values)
        expected_metadata_hash = "f7cba8927949b0d9e7c284501ae42de4"
        self.assertEqual(dataset.current_metadata_hash, expected_metadata_hash)

    def test_current_readme_hash(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        dataset = CCDLDataset(
            data=data,
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
            ccdl_name=CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT,
        )
        expected_readme_hash = "8b3c42fbb143b76dddd9548a3b23272d"
        self.assertEqual(dataset.current_readme_hash, expected_readme_hash)

    def test_get_metadata_file_contents(self):
        # one project, one modality
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [
                    "SCPCS999990",
                    "SCPCS999997",
                ],
                Modalities.SPATIAL: [],
            },
        }

        transformed_content_values = [
            (project_id, modality, len(content))
            for (project_id, modality, content) in dataset.get_metadata_file_contents()
        ]
        expected_values = [("SCPCP999990", Modalities.SINGLE_CELL, 1729)]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # one project, two modalities
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [
                    "SCPCS999990",
                    "SCPCS999997",
                ],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }

        transformed_content_values = [
            (project_id, modality, len(content))
            for (project_id, modality, content) in dataset.get_metadata_file_contents()
        ]
        expected_values = [
            ("SCPCP999990", Modalities.SINGLE_CELL, 1729),
            ("SCPCP999990", Modalities.SPATIAL, 1003),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # two projects, multiple modalities
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

        transformed_content_values = [
            (project_id, modality, len(content))
            for (project_id, modality, content) in dataset.get_metadata_file_contents()
        ]
        expected_values = [
            ("SCPCP999990", Modalities.SINGLE_CELL, 1729),
            ("SCPCP999990", Modalities.SPATIAL, 1003),
            ("SCPCP999991", Modalities.SINGLE_CELL, 2351),
            ("SCPCP999992", Modalities.SINGLE_CELL, 1839),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # all metadata, single project dataset (project metadata)
        dataset = UserDataset(format=DatasetFormats.METADATA)
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }

        transformed_content_values = [
            (project_id, modality, len(content))
            for (project_id, modality, content) in dataset.get_metadata_file_contents()
        ]
        expected_values = [
            (None, None, 2692),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # all metadata, multi project dataset (portal wide metadata)
        dataset = UserDataset(format=DatasetFormats.METADATA)
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

        transformed_content_values = [
            (project_id, modality, len(content))
            for (project_id, modality, content) in dataset.get_metadata_file_contents()
        ]
        expected_values = [
            (None, None, 5490),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

    def test_get_estimated_size_in_bytes(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        dataset = UserDataset(data=data, format=format)
        expected_files = {
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_processed.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_qc.html"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_filtered.rds"),
            Path("SCPCP999990/SCPCS999997/SCPCL999997_processed.rds"),
        }
        expected_file_size = 0
        for file in expected_files:
            original_file = OriginalFile.objects.filter(s3_key=str(file)).first()
            random_file_size = random.randint(1, 1000000000)
            original_file.size_in_bytes = random_file_size
            original_file.save()

            expected_file_size += original_file.size_in_bytes

        metadata_file_string = "".join(
            [file_content for _, _, file_content in dataset.get_metadata_file_contents()]
        )
        metadata_file_size = sys.getsizeof(metadata_file_string)
        readme_file_size = sys.getsizeof(dataset.readme_file_contents)
        expected_file_size += metadata_file_size + readme_file_size

        self.assertEqual(dataset.get_estimated_size_in_bytes(), expected_file_size)

    def test_contains_project_ids(self):
        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )
        self.assertTrue(dataset.contains_project_ids(set(dataset.data.keys())))
        self.assertTrue(dataset.contains_project_ids({"SCPCP999990"}))
        self.assertTrue(dataset.contains_project_ids({"SCPCP999992"}))
        self.assertFalse(dataset.contains_project_ids({"SCPCP999991"}))

    def test_has_lockfile_projects_property(self):
        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )

        with patch("scpca_portal.lockfile.get_locked_project_ids", return_value=["SCPCP999990"]):
            self.assertTrue(dataset.has_lockfile_projects)

        with patch("scpca_portal.lockfile.get_locked_project_ids", return_value=[]):
            self.assertFalse(dataset.has_lockfile_projects)

    def test_projects_property(self):
        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )

        dataset_projects = dataset.projects
        self.assertIn(Project.objects.filter(scpca_id="SCPCP999990").first(), dataset_projects)
        self.assertNotIn(Project.objects.filter(scpca_id="SCPCP999991").first(), dataset_projects)
        self.assertIn(Project.objects.filter(scpca_id="SCPCP999992").first(), dataset_projects)

    def test_locked_projects_property(self):
        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )

        locked_project = Project.objects.filter(scpca_id="SCPCP999990").first()
        locked_project.is_locked = True
        locked_project.save()

        dataset_locked_projects = dataset.locked_projects
        self.assertIn(
            Project.objects.filter(scpca_id="SCPCP999990").first(), dataset_locked_projects
        )
        self.assertNotIn(
            Project.objects.filter(scpca_id="SCPCP999991").first(), dataset_locked_projects
        )
        self.assertNotIn(
            Project.objects.filter(scpca_id="SCPCP999992").first(), dataset_locked_projects
        )

    def test_has_locked_projects_property(self):
        dataset = UserDataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )
        self.assertFalse(dataset.has_locked_projects)

        locked_project = Project.objects.filter(scpca_id="SCPCP999990").first()
        locked_project.is_locked = True
        locked_project.save()
        self.assertTrue(dataset.has_locked_projects)

    def test_get_includes_files_bulk(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

        # project with bulk, bulk requested
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }
        dataset.save()
        self.assertTrue(dataset.get_includes_files_bulk())

        # project with bulk, bulk not requested
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            }
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_bulk())

        # project without bulk
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999995"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_bulk())

    def test_get_includes_files_cite_seq(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

        # project with cite-seq data
        dataset.data = {
            "SCPCP999992": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999996", "SCPCS999998"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertTrue(dataset.get_includes_files_cite_seq())

        # project without cite-seq data
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: ["SCPCS999991"],
            }
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_cite_seq())

    def test_get_includes_files_merged(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

        # project with merged file, merged requested
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertTrue(dataset.get_includes_files_merged())

        # project with merged file, merged not requested
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            }
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_merged())

        # project without merged
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: "MERGED",
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_merged())

    def test_get_includes_files_multiplexed(self):
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

        # project with multiplexed
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertTrue(dataset.get_includes_files_multiplexed())

        # project without multiplexed
        dataset.data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            }
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_multiplexed())

        # project with multiplexed data but with ann data format
        dataset = UserDataset(format=DatasetFormats.ANN_DATA)
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_multiplexed())

        # dataset with subset of samples from project with multiplexed data
        # with multiplexed samples selected
        dataset = UserDataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertTrue(dataset.get_includes_files_multiplexed())

        # dataset with subset of samples from project with multiplexed dataset
        # with no multiplexed samples selected
        dataset.data = {
            "SCPCP999991": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999995"],
                Modalities.SPATIAL: [],
            },
        }
        dataset.save()
        self.assertFalse(dataset.get_includes_files_multiplexed())
