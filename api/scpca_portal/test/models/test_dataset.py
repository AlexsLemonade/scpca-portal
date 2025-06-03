import random
from pathlib import Path
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag

from scpca_portal import loader
from scpca_portal.enums import CCDLDatasetNames, DatasetFormats, Modalities
from scpca_portal.models import Dataset, OriginalFile
from scpca_portal.test import expected_values as test_data
from scpca_portal.test.factories import DatasetFactory, OriginalFileFactory


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
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Incorrect project ids
        data = {
            "project_id": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Lack of SCPCP prefix
        data = {
            "SCPCA999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Incorrect number of digits
        data = {
            "SCPCP9999900": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

    @tag("is_data_valid")
    def test_is_data_valid_config(self):
        # Valid config
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Empty config (valid)
        data = {
            "SCPCP999990": {},
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - missing (valid)
        data = {
            "SCPCP999990": {
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Includes bulk - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": "True",
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - missing (valid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "SCPCS999990",
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Merge single cell - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: "MERGED",  # should be ["MERGED"]
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }

        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: [1, 2, 3],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Single Cell - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["sample_id"],
                Modalities.SPATIAL.value: ["SCPCS999992"],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - missing (valid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
            },
        }
        self.assertTrue(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: "SCPCS999992",
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - wrong inner data type (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: [1, 2, 3],
            },
        }
        self.assertFalse(DatasetFactory(data=data).is_data_valid)

        # Spatial - invalid sample id (invalid)
        data = {
            "SCPCP999990": {
                "includes_bulk": True,
                Modalities.SINGLE_CELL.value: ["SCPCS999990", "SCPCS999991"],
                Modalities.SPATIAL.value: ["sample_id"],
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
                Modalities.SINGLE_CELL: ["MERGED"],
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
                Modalities.SINGLE_CELL: ["MERGED"],
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
                Modalities.SINGLE_CELL: ["MERGED"],
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
            expected_data_hash = "c60e50797610f0063688a0830b0a727e"
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
        expected_metadata_hash = "46ed5abd84c4b86ef348779b045b8cdf"
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
        expected_readme_hash = "93ce0b3571f15cd41db81d9e25dcb873"
        self.assertEqual(dataset.current_readme_hash, expected_readme_hash)

    def estimated_size_in_bytes(self):
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

        self.assertEqual(dataset.estimated_size_in_bytes, expected_file_size)
