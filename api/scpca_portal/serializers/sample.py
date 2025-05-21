from rest_framework import serializers

from scpca_portal.models import Sample
from scpca_portal.serializers.computed_file import ComputedFileSerializer


class SampleLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = (
            "additional_metadata",
            "age",
            "age_timing",
            "computed_files",
            "created_at",
            "demux_cell_count_estimate_sum",
            "diagnosis",
            "disease_timing",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
            "includes_anndata",
            "is_cell_line",
            "is_xenograft",
            "modalities",
            "multiplexed_with",
            "project",
            "sample_cell_count_estimate",
            "scpca_id",
            "seq_units",
            "sex",
            "subdiagnosis",
            "technologies",
            "tissue_location",
            "treatment",
            "updated_at",
        )

    computed_files = ComputedFileSerializer(read_only=True, many=True)
    project = serializers.SlugRelatedField(read_only=True, slug_field="scpca_id")


class SampleSerializer(SampleLeafSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)
