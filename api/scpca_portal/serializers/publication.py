from rest_framework import serializers

from scpca_portal.models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            "citation",
            "doi",
            "doi_url",
        )
