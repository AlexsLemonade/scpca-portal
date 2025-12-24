import random
import sys
from pathlib import Path
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser
from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, FileFormats, Modalities
from scpca_portal.models import ComputedFile, Dataset, OriginalFile, Project
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import (
    DatasetFactory,
    LeafComputedFileFactory,
    LibraryFactory,
    OriginalFileFactory,
    SampleFactory,
)


class TestDataset(TestCase):
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

    def test_dataset_saved_to_db(self):
        dataset = DatasetFactory()
        self.assertEqual(Dataset.objects.count(), 1)

        returned_dataset = Dataset.objects.filter(pk=dataset.id).first()
        self.assertEqual(returned_dataset, dataset)

    def test_is_ccdl_default_set(self):
        dataset = DatasetFactory()
        self.assertFalse(dataset.is_ccdl)

    def test_get_or_find_ccdl_dataset(self):
        # Portal Dataset Check
        ccdl_portal_datasets_expected_values = [
            test_data.DatasetAllMetadata,
            test_data.DatasetSingleCellSingleCellExperiment,
            test_data.DatasetSingleCellSingleCellExperimentMerged,
            test_data.DatasetSingleCellAnndata,
            test_data.DatasetSingleCellAnndataMerged,
            test_data.DatasetSpatialSpatialSpaceranger,
        ]

        for ccdl_portal_dataset in ccdl_portal_datasets_expected_values:
            dataset, found = Dataset.get_or_find_ccdl_dataset(ccdl_portal_dataset.CCDL_NAME)
            dataset.save()
            self.assertFalse(found)

            for attribute, value in ccdl_portal_dataset.VALUES.items():
                msg = f"The actual and expected `{attribute}` values differ in {dataset}"
                if isinstance(value, list):
                    self.assertListEqual(getattr(dataset, attribute), value, msg)
                else:
                    self.assertEqual(getattr(dataset, attribute), value, msg)

            dataset_same, found_same = Dataset.get_or_find_ccdl_dataset(
                ccdl_portal_dataset.CCDL_NAME
            )
            self.assertEqual(dataset_same.pk, dataset.pk)
            self.assertTrue(found_same)

        # Project Dataset Check
        ccdl_project_dataset = (
            test_data.DatasetSingleCellSingleCellExperimentNoMultiplexedSCPCP999991
        )
        dataset, found = Dataset.get_or_find_ccdl_dataset(
            ccdl_project_dataset.CCDL_NAME, ccdl_project_dataset.PROJECT_ID
        )
        dataset.save()
        self.assertFalse(found)

        for attribute, value in ccdl_project_dataset.VALUES.items():
            msg = f"The actual and expected `{attribute}` values differ in {dataset}"
            if isinstance(value, list):
                self.assertListEqual(getattr(dataset, attribute), value, msg)
            else:
                self.assertEqual(getattr(dataset, attribute), value, msg)

        dataset, found = Dataset.get_or_find_ccdl_dataset(
            ccdl_project_dataset.CCDL_NAME, ccdl_project_dataset.PROJECT_ID
        )
        self.assertTrue(found)

    def test_create_or_update_ccdl_datasets(self):
        # There are 21 total datasets created
        #     CCDL DATASET TYPE              Total   Projects   Portal Wide
        #   - ALL_METADATA                   4       3          Yes
        #   - SINGLE_CELL_SCE                4       3          Yes
        #   - SINGLE_CELL_SCE_NO_MULTIPLEXED 1       1          No
        #   - SINGLE_CELL_SCE_MERGED         3       2          Yes
        #   - SINGLE_CELL_ANN_DATA           4       3          Yes
        #   - SINGLE_CELL_ANN_DATA_MERGED    3       2          Yes
        #   - SPATIAL_SCE                    2       1          Yes

        # Initial call
        created_datasets, updated_datasets = Dataset.create_or_update_ccdl_datasets()
        self.assertEqual(len(created_datasets), 21)
        self.assertEqual(len(updated_datasets), 0)

        # Call again
        created_datasets, updated_datasets = Dataset.create_or_update_ccdl_datasets()
        self.assertEqual(len(created_datasets), 0)
        self.assertEqual(len(updated_datasets), 0)

        # Call with ignore_hash
        created_datasets, updated_datasets = Dataset.create_or_update_ccdl_datasets(
            ignore_hash=True
        )
        self.assertEqual(len(created_datasets), 0)
        self.assertEqual(len(updated_datasets), 21)

    def test_create_or_update_ccdl_datasets_update_data_attr(self):
        """Assert that data attr updates when new samples and libraries are added."""
        # Create dataset
        dataset_expected_values = test_data.DatasetSingleCellSingleCellExperimentSCPCP999990
        dataset, _ = Dataset.get_or_find_ccdl_dataset(
            dataset_expected_values.CCDL_NAME, dataset_expected_values.PROJECT_ID
        )
        dataset.save()

        # Define original and expected values
        actual_old_data_attr = dataset.get_ccdl_data()
        expected_old_data_attr = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            }
        }
        expected_new_data_attr = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997", "SCPCS999999"],
                Modalities.SPATIAL: [],
            }
        }

        # Simulate the work of sync_original_files and load_metadata commands
        # with a new sample and library added to an existing project
        project_id, sample_id, library_id = "SCPCP999990", "SCPCS999999", "SCPCL999999"
        OriginalFileFactory(
            s3_key="SCPCP999990/SCPCS999999/SCPCL999999.rds",
            project_id=project_id,
            sample_ids=[sample_id],
            library_id=library_id,
            is_single_cell=True,
            is_single_cell_experiment=True,
            formats=[FileFormats.SINGLE_CELL_EXPERIMENT],
        )

        project = Project.objects.filter(scpca_id=project_id).first()
        sample = SampleFactory(scpca_id=sample_id, has_single_cell_data=True, project=project)
        sample.save()

        library = LibraryFactory(
            scpca_id=library_id, modality=Modalities.SINGLE_CELL, project=project
        )
        library.samples.add(sample)
        library.save()

        # Rerun create update ccdl datasets method
        _, updated_datasets = Dataset.create_or_update_ccdl_datasets()
        updated_dataset = updated_datasets[0]
        actual_new_data_attr = updated_dataset.data

        # Make assertions
        self.assertEqual(actual_old_data_attr, expected_old_data_attr)
        self.assertEqual(actual_new_data_attr, expected_new_data_attr)
        self.assertNotEqual(actual_old_data_attr, actual_new_data_attr)

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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
        dataset = Dataset(data=data, format=format)
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
            Dataset,
            "original_files",
            new_callable=PropertyMock,
            return_value=mock_original_files,
        ):
            dataset = Dataset()
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
        dataset = Dataset(data=data, format=format)

        # TODO: add to expected_values dataset file (along with other hash values)
        expected_metadata_hash = "bd32dc05b6dc4a20fdd510bd2d3f669b"
        self.assertEqual(dataset.current_metadata_hash, expected_metadata_hash)

    def test_current_readme_hash(self):
        data = {
            "SCPCP999990": {
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
                Modalities.SPATIAL: [],
            },
        }
        dataset = Dataset(
            data=data,
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
            ccdl_name=CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT,
        )
        expected_readme_hash = "cb0d4d6c2c8027276de69b78a5ac0629"
        self.assertEqual(dataset.current_readme_hash, expected_readme_hash)

    def test_get_metadata_file_contents(self):
        # one project, one modality
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        expected_values = [("SCPCP999990", Modalities.SINGLE_CELL, 1723)]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # one project, two modalities
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
            ("SCPCP999990", Modalities.SINGLE_CELL, 1723),
            ("SCPCP999990", Modalities.SPATIAL, 1000),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # two projects, multiple modalities
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
            ("SCPCP999990", Modalities.SINGLE_CELL, 1723),
            ("SCPCP999990", Modalities.SPATIAL, 1000),
            ("SCPCP999991", Modalities.SINGLE_CELL, 2342),
            ("SCPCP999992", Modalities.SINGLE_CELL, 1833),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # all metadata, single project dataset (project metadata)
        dataset = Dataset(format=DatasetFormats.METADATA)
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
            (None, None, 2680),
        ]
        for actual_values, expected_values in zip(transformed_content_values, expected_values):
            self.assertEqual(actual_values, expected_values)

        # all metadata, multi project dataset (portal wide metadata)
        dataset = Dataset(format=DatasetFormats.METADATA)
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
            (None, None, 5463),
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
        dataset = Dataset(data=data, format=format)
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

    def test_get_total_sample_count(self):
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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

    def test_contains_project_ids(self):
        dataset = Dataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )
        self.assertTrue(dataset.contains_project_ids(set(dataset.data.keys())))
        self.assertTrue(dataset.contains_project_ids({"SCPCP999990"}))
        self.assertTrue(dataset.contains_project_ids({"SCPCP999992"}))
        self.assertFalse(dataset.contains_project_ids({"SCPCP999991"}))

    def test_has_lockfile_projects_property(self):
        dataset = Dataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )

        # lockfile in test bucket is empty by default
        self.assertFalse(dataset.has_lockfile_projects)

        with patch("scpca_portal.lockfile.get_locked_project_ids", return_value=["SCPCP999990"]):
            self.assertTrue(dataset.has_lockfile_projects)

    def test_projects_property(self):
        dataset = Dataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )

        dataset_projects = dataset.projects
        self.assertIn(Project.objects.filter(scpca_id="SCPCP999990").first(), dataset_projects)
        self.assertNotIn(Project.objects.filter(scpca_id="SCPCP999991").first(), dataset_projects)
        self.assertIn(Project.objects.filter(scpca_id="SCPCP999992").first(), dataset_projects)

    def test_locked_projects_property(self):
        dataset = Dataset(
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
        dataset = Dataset(
            data=test_data.DatasetCustomSingleCellExperiment.VALUES["data"],
            format=test_data.DatasetCustomSingleCellExperiment.VALUES["format"],
        )
        self.assertFalse(dataset.has_locked_projects)

        locked_project = Project.objects.filter(scpca_id="SCPCP999990").first()
        locked_project.is_locked = True
        locked_project.save()
        self.assertTrue(dataset.has_locked_projects)

    def test_get_diagnoses_summary(self):
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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

        single_cell_dataset = Dataset(
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

        ann_data_dataset = Dataset(
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
            "SCPCP999990": "TBD",
            "SCPCP999991": "TBD",
            "SCPCP999992": "TBD",
        }

        actual_titles = dataset.get_project_titles()

        for project_id in actual_titles.keys():
            self.assertEqual(actual_titles[project_id], expected_titles[project_id])

    @patch("scpca_portal.models.computed_file.utils.get_today_string", return_value="2025-08-26")
    @patch("scpca_portal.s3.aws_s3.generate_presigned_url")
    def test_download_url_property(self, mock_generate_presigned_url, _):
        # ccdl project dataset
        dataset = DatasetFactory(
            is_ccdl=True,
            ccdl_project_id="SCPCP999990",
            format=DatasetFormats.SINGLE_CELL_EXPERIMENT,
        )
        dataset.computed_file = LeafComputedFileFactory(
            s3_key=ComputedFile.get_dataset_file_s3_key(dataset)
        )
        dataset.save()

        dataset.download_url
        expected_filename = "SCPCP999990_single-cell-experiment_2025-08-26.zip"
        mock_generate_presigned_url.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": "scpca-portal-local",
                "Key": f"{dataset.id}.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        # ccdl portal wide dataset
        dataset = DatasetFactory(
            is_ccdl=True, ccdl_project_id=None, format=DatasetFormats.SINGLE_CELL_EXPERIMENT
        )
        dataset.computed_file = LeafComputedFileFactory(
            s3_key=ComputedFile.get_dataset_file_s3_key(dataset)
        )
        dataset.save()

        dataset.download_url
        expected_filename = "portal-wide_single-cell-experiment_2025-08-26.zip"
        mock_generate_presigned_url.assert_called_with(
            ClientMethod="get_object",
            Params={
                "Bucket": "scpca-portal-local",
                "Key": f"{dataset.id}.zip",
                "ResponseContentDisposition": f"attachment; filename = {expected_filename}",
            },
            ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        # user dataset
        dataset = DatasetFactory(is_ccdl=False, format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
        dataset = DatasetFactory()
        self.assertIsNone(dataset.download_url)

    def test_get_includes_files_bulk(self):
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)

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
        dataset = Dataset(format=DatasetFormats.ANN_DATA)
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
        dataset = Dataset(format=DatasetFormats.SINGLE_CELL_EXPERIMENT)
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
