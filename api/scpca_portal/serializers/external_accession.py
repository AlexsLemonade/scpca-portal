from rest_framework import serializers

from scpca_portal.models import ExternalAccession


class ExternalAccessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAccession
        fields = (
            "accession",
            "has_raw",
            "url",
        )
