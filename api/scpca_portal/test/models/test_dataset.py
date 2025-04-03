from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag

from scpca_portal import loader
from scpca_portal.enums import DatasetFormats, Modalities
from scpca_portal.models import Dataset
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import DatasetFactory


class TestDataset(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        for project_metadata in loader.get_projects_metadata():
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
                reload_existing=True,
                update_s3=False,
            )

    def test_dataset_saved_to_db(self):
        dataset = DatasetFactory()
        self.assertEqual(Dataset.objects.count(), 1)

        returned_dataset = Dataset.objects.filter(pk=dataset.id).first()
        self.assertEqual(returned_dataset, dataset)

    @tag("is_data_valid")
    def test_is_data_valid_project_id(self):
        # Valid project id
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Incorrect project ids
        data = {
            "project_id": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Lack of SCPCP prefix
        data = {
            "SCPCA999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Incorrect number of digits
        data = {
            "SCPCP9999900": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

    @tag("is_data_valid")
    def test_is_data_valid_config(self):
        # Valid config
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Empty config (valid)
        data = {
            "SCPCP999990": {},
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - missing (valid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": "True",
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": "True",
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: "SCPCS999990",
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: [1, 2, 3],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["sample_id"],
                Modalities.SPATIAL.name: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - missing (valid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: "SCPCS999992",
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: [1, 2, 3],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL.name: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.name: ["sample_id"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

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
            test_data.DatasetSpatialSingleCellExperiment,
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

    def test_original_files_property(self):
        # SINGLE_CELL SCE
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
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
                "merge_single_cell": False,
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
                "merge_single_cell": True,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
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
                "merge_single_cell": True,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999997"],
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
        # SPATIAL SCE
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: ["SCPCS999991"],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
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
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: [],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        dataset = Dataset(data=data, format=format)
        expected_files = {
            Path("SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv"),
            Path("SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)

        # MIXED USAGE
        data = {
            "SCPCP999990": {
                "merge_single_cell": False,
                "includes_bulk": True,
                Modalities.SINGLE_CELL: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL: ["SCPCS999997"],
            },
            "SCPCP999991": {
                "merge_single_cell": False,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
            "SCPCP999992": {
                "merge_single_cell": True,
                "includes_bulk": False,
                Modalities.SINGLE_CELL: ["SCPCS999992", "SCPCS999993", "SCPCS999995"],
                Modalities.SPATIAL: [],
            },
        }
        format = DatasetFormats.SINGLE_CELL_EXPERIMENT
        dataset = Dataset(data=data, format=format)
        expected_files = {
            Path("SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_filtered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_processed.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_qc.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_unfiltered.rds"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_celltype-report.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_processed.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_celltype-report.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_processed.rds"),
            Path("SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_qc.html"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_qc.html"),
            Path("SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_unfiltered.rds"),
            Path("SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds"),
            Path("SCPCP999992/merged/SCPCP999992_merged.rds"),
            Path("SCPCP999991/SCPCS999995/SCPCL999995_filtered.rds"),
            Path("SCPCP999992/merged/SCPCP999992_merged-summary-report.html"),
        }
        self.assertEqual(dataset.original_file_paths, expected_files)
