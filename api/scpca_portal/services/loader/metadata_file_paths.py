from scpca_portal import common
from scpca_portal.models import Sample


class MetadataFilePaths():
    # Input Data Paths
    @staticmethod
    def get_input_project_metadata_file_path():
        return common.INPUT_DATA_PATH / "project_metadata.csv"

    @staticmethod
    def input_data_path(scpca_project_id):
        return common.INPUT_DATA_PATH / scpca_project_id

    @staticmethod
    def input_bulk_metadata_file_path(scpca_project_id):
        return MetadataFilePaths.input_data_path(scpca_project_id) \
            / "{scpca_project_id}_bulk_metadata.tsv"

    @staticmethod
    def input_bulk_quant_file_path(scpca_project_id):
        return MetadataFilePaths.input_data_path(scpca_project_id) \
            / f"{scpca_project_id}_bulk_quant.tsv"

    @staticmethod
    def input_samples_metadata_file_path(scpca_project_id):
        return MetadataFilePaths.input_data_path(scpca_project_id) \
            / "samples_metadata.csv"

    @staticmethod
    def get_sample_input_data_dir(scpca_project_id, scpca_sample_id):
        """Returns an input data directory based on a sample ID."""
        return MetadataFilePaths.input_data_path(scpca_project_id) \
            / scpca_sample_id

    # Output Data Paths
    @staticmethod
    def output_multiplexed_metadata_file_path(scpca_project_id):
        return common.OUTPUT_DATA_PATH / f"{scpca_project_id}_multiplexed_metadata.tsv"

    @staticmethod
    def output_spatial_metadata_file_path(scpca_project_id):
        return common.OUTPUT_DATA_PATH / f"{scpca_project_id}_spatial_metadata.tsv"

    @staticmethod
    def output_single_cell_metadata_file_path(scpca_project_id):
        return common.OUTPUT_DATA_PATH / f"{scpca_project_id}_libraries_metadata.tsv"

    @staticmethod
    def get_output_metadata_file_path(scpca_sample_id, modality):
        return {
            Sample.Modalities.MULTIPLEXED: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_multiplexed_metadata.tsv",
            Sample.Modalities.SINGLE_CELL: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_libraries_metadata.tsv",
            Sample.Modalities.SPATIAL: common.OUTPUT_DATA_PATH
            / f"{scpca_sample_id}_spatial_metadata.tsv",
        }.get(modality)
