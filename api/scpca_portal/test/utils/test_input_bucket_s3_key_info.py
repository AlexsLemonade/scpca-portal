from pathlib import Path

from django.test import TestCase

from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.utils import InputBucketS3KeyInfo


class InputBucketS3KeyInfoTest(TestCase):
    def setUp(self):
        self.merged_file = Path("SCPCP999999/merged/SCPCP999999_merged.rds")
        self.single_cell_sce_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_filtered.rds")
        self.single_cell_anndata_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_filtered.h5ad")
        self.spatial_file = Path(
            "SCPCP999999/SCPCS999999/SCPCL999999_spatial/SCPCL999999_spaceranger-summary.html"
        )
        self.cite_seq_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_filtered_adt.h5ad")
        self.bulk_file = Path("SCPCP999999/bulk/SCPCP999999_bulk_quant.tsv")
        self.supplementary_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_qc.html")
        self.csv_metadata_file = Path("SCPCP999999/samples_metadata.csv")
        self.json_metadata_file = Path("SCPCP999999/SCPCS999999/SCPCL999999_metadata.json")

    def test_id_parsing(self):
        project_file_s3_key_info = InputBucketS3KeyInfo(self.merged_file)
        self.assertEqual(project_file_s3_key_info.project_id, "SCPCP999999")
        self.assertIsNone(project_file_s3_key_info.sample_id)
        self.assertIsNone(project_file_s3_key_info.library_id)
        self.assertTrue(project_file_s3_key_info.is_project_file)

        library_file_s3_key_info = InputBucketS3KeyInfo(self.single_cell_sce_file)
        self.assertEqual(library_file_s3_key_info.project_id, "SCPCP999999")
        self.assertEqual(library_file_s3_key_info.sample_id, "SCPCS999999")
        self.assertEqual(library_file_s3_key_info.library_id, "SCPCL999999")
        self.assertFalse(library_file_s3_key_info.is_project_file)

    def test_is_merged(self):
        merged_file_s3_key_info = InputBucketS3KeyInfo(self.merged_file)
        self.assertTrue(merged_file_s3_key_info.is_merged)

        non_merged_file_s3_key_info = InputBucketS3KeyInfo(self.single_cell_sce_file)
        self.assertFalse(non_merged_file_s3_key_info.is_merged)

    def test_modalities(self):
        single_cell_file_s3_key_info = InputBucketS3KeyInfo(self.single_cell_sce_file)
        self.assertIn(Modalities.SINGLE_CELL, single_cell_file_s3_key_info.modalities)
        self.assertEqual(1, len(single_cell_file_s3_key_info.modalities))

        spatial_file_s3_key_info = InputBucketS3KeyInfo(self.spatial_file)
        self.assertIn(Modalities.SPATIAL, spatial_file_s3_key_info.modalities)
        self.assertEqual(1, len(spatial_file_s3_key_info.modalities))

        cite_seq_file_s3_key_info = InputBucketS3KeyInfo(self.cite_seq_file)
        self.assertIn(Modalities.SINGLE_CELL, cite_seq_file_s3_key_info.modalities)
        self.assertIn(Modalities.CITE_SEQ, cite_seq_file_s3_key_info.modalities)
        self.assertEqual(2, len(cite_seq_file_s3_key_info.modalities))

        bulk_file_s3_key_info = InputBucketS3KeyInfo(self.bulk_file)
        self.assertIn(Modalities.BULK_RNA_SEQ, bulk_file_s3_key_info.modalities)
        self.assertEqual(1, len(bulk_file_s3_key_info.modalities))

    def test_format(self):
        sce_single_cell_file_s3_key_info = InputBucketS3KeyInfo(self.single_cell_sce_file)
        self.assertEqual(
            sce_single_cell_file_s3_key_info.format, FileFormats.SINGLE_CELL_EXPERIMENT
        )

        sce_spatial_file_s3_key_info = InputBucketS3KeyInfo(self.spatial_file)
        self.assertEqual(sce_spatial_file_s3_key_info.format, FileFormats.SINGLE_CELL_EXPERIMENT)

        anndata_file_s3_key_info = InputBucketS3KeyInfo(self.single_cell_anndata_file)
        self.assertEqual(anndata_file_s3_key_info.format, FileFormats.ANN_DATA)

        supplementary_file_s3_key_info = InputBucketS3KeyInfo(self.supplementary_file)
        self.assertEqual(supplementary_file_s3_key_info.format, FileFormats.SUPPLEMENTARY)

        csv_metadata_file_s3_key_info = InputBucketS3KeyInfo(self.csv_metadata_file)
        self.assertEqual(csv_metadata_file_s3_key_info.format, FileFormats.METADATA)

        json_metadata_file_s3_key_info = InputBucketS3KeyInfo(self.json_metadata_file)
        self.assertEqual(json_metadata_file_s3_key_info.format, FileFormats.METADATA)
