from rest_framework import serializers

from scpca_portal.models import Dataset, Project
from scpca_portal.serializers.computed_file import ComputedFileSerializer
from scpca_portal.serializers.contact import ContactSerializer
from scpca_portal.serializers.dataset import DatasetSerializer
from scpca_portal.serializers.external_accession import ExternalAccessionSerializer
from scpca_portal.serializers.project_summary import ProjectSummarySerializer
from scpca_portal.serializers.publication import PublicationSerializer
from scpca_portal.serializers.sample import SampleSerializer
from scpca_portal.enums.dataset_formats import DatasetFormats


class ProjectLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "abstract",
            "additional_metadata_keys",
            "additional_restrictions",
            "computed_files",
            "contacts",
            "created_at",
            "diagnoses_counts",
            "diagnoses",
            "disease_timings",
            "downloadable_sample_count",
            "external_accessions",
            "has_bulk_rna_seq",
            "has_cite_seq_data",
            "has_multiplexed_data",
            "has_single_cell_data",
            "has_spatial_data",
            "human_readable_pi_name",
            "includes_anndata",
            "includes_cell_lines",
            "includes_merged_anndata",
            "includes_merged_sce",
            "includes_xenografts",
            "metadata_dataset",
            "modalities",
            "multiplexed_sample_count",
            "organisms",
            "pi_name",
            "publications",
            "sample_count",
            "samples",
            "scpca_id",
            "seq_units",
            "summaries",
            "technologies",
            "title",
            "unavailable_samples_count",
            "updated_at",
        )

    # This breaks the general pattern of not using sub-serializers,
    # but we want these to always be included.
    computed_files = ComputedFileSerializer(read_only=True, many=True)
    contacts = ContactSerializer(read_only=True, many=True)
    metadata_dataset = serializers.SerializerMethodField()
    external_accessions = ExternalAccessionSerializer(read_only=True, many=True)
    publications = PublicationSerializer(read_only=True, many=True)
    samples = serializers.SlugRelatedField(many=True, read_only=True, slug_field="scpca_id")
    summaries = ProjectSummarySerializer(many=True, read_only=True)

    def get_metadata_dataset(self, obj):
        dataset = Dataset.objects.filter(
            is_ccdl=True, ccdl_project_id=obj.scpca_id, format=DatasetFormats.METADATA
        ).first()
        return DatasetSerializer(dataset).data


class ProjectSerializer(ProjectLeafSerializer):
    computed_files = ComputedFileSerializer(read_only=True, many=True)


class ProjectDetailSerializer(ProjectSerializer):
    samples = SampleSerializer(many=True, read_only=True)
