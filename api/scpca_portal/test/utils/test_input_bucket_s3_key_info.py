from pathlib import Path

from django.test import TestCase

from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.utils import InputBucketS3KeyInfo


class InputBucketS3KeyInfoTest(TestCase):
    def test_id_parsing(self):
        project_file = Path("SCPCP999999/file.txt")
        project_file_s3_key_info = InputBucketS3KeyInfo(project_file)
        self.assertEqual(project_file_s3_key_info.project_id, "SCPCP999999")
        self.assertIsNone(project_file_s3_key_info.sample_id)
        self.assertIsNone(project_file_s3_key_info.library_id)
        self.assertTrue(project_file_s3_key_info.is_project_file)

        library_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.txt")
        library_file_s3_key_info = InputBucketS3KeyInfo(library_file)
        self.assertEqual(library_file_s3_key_info.project_id, "SCPCP999999")
        self.assertEqual(library_file_s3_key_info.sample_id, "SCPCS999999")
        self.assertEqual(library_file_s3_key_info.library_id, "SCPCL999999")
        self.assertFalse(library_file_s3_key_info.is_project_file)

    def test_is_merged(self):
        merged_file = Path("SCPCP000001/merged/SCPCP999999_merged.txt")
        merged_file_s3_key_info = InputBucketS3KeyInfo(merged_file)
        self.assertTrue(merged_file_s3_key_info.is_merged)

        non_merged_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.txt")
        non_merged_file_s3_key_info = InputBucketS3KeyInfo(non_merged_file)
        self.assertFalse(non_merged_file_s3_key_info.is_merged)

    def test_modalities(self):
        single_cell_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.txt")
        spatial_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_spatial/SCPCL999999_file.txt")
        cite_seq_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file_adt.h5ad")
        bulk_file = Path("SCPCP999999/bulk/SCPCP999999_bulk.txt")

        single_cell_file_s3_key_info = InputBucketS3KeyInfo(single_cell_file)
        self.assertIn(Modalities.SINGLE_CELL, single_cell_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.SPATIAL, single_cell_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.CITE_SEQ, single_cell_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.BULK_RNA_SEQ, single_cell_file_s3_key_info.modalities)

        spatial_file_s3_key_info = InputBucketS3KeyInfo(spatial_file)
        self.assertNotIn(Modalities.SINGLE_CELL, spatial_file_s3_key_info.modalities)
        self.assertIn(Modalities.SPATIAL, spatial_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.CITE_SEQ, spatial_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.BULK_RNA_SEQ, spatial_file_s3_key_info.modalities)

        cite_seq_file_s3_key_info = InputBucketS3KeyInfo(cite_seq_file)
        self.assertIn(Modalities.SINGLE_CELL, cite_seq_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.SPATIAL, cite_seq_file_s3_key_info.modalities)
        self.assertIn(Modalities.CITE_SEQ, cite_seq_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.BULK_RNA_SEQ, cite_seq_file_s3_key_info.modalities)

        bulk_file_s3_key_info = InputBucketS3KeyInfo(bulk_file)
        self.assertNotIn(Modalities.SINGLE_CELL, bulk_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.SPATIAL, bulk_file_s3_key_info.modalities)
        self.assertNotIn(Modalities.CITE_SEQ, bulk_file_s3_key_info.modalities)
        self.assertIn(Modalities.BULK_RNA_SEQ, bulk_file_s3_key_info.modalities)

    def test_format(self):
        sce_single_cell_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.rds")
        sce_spatial_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_spatial/SCPCL999999_file.txt")
        anndata_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.h5ad")
        supplementary_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.html")
        csv_metadata_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.csv")
        json_metadata_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_file.json")

        sce_single_cell_file_s3_key_info = InputBucketS3KeyInfo(sce_single_cell_file)
        self.assertEqual(
            sce_single_cell_file_s3_key_info.format, FileFormats.SINGLE_CELL_EXPERIMENT
        )
        sce_spatial_file_s3_key_info = InputBucketS3KeyInfo(sce_spatial_file)
        self.assertEqual(sce_spatial_file_s3_key_info.format, FileFormats.SINGLE_CELL_EXPERIMENT)

        anndata_file_s3_key_info = InputBucketS3KeyInfo(anndata_file)
        self.assertEqual(anndata_file_s3_key_info.format, FileFormats.ANN_DATA)

        supplementary_file_s3_key_info = InputBucketS3KeyInfo(supplementary_file)
        self.assertEqual(supplementary_file_s3_key_info.format, FileFormats.SUPPLEMENTARY)

        csv_metadata_file_s3_key_info = InputBucketS3KeyInfo(csv_metadata_file)
        self.assertEqual(csv_metadata_file_s3_key_info.format, FileFormats.METADATA)

        json_metadata_file_s3_key_info = InputBucketS3KeyInfo(json_metadata_file)
        self.assertEqual(json_metadata_file_s3_key_info.format, FileFormats.METADATA)
