from rest_framework import serializers

from scpca_portal.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "email",
            "name",
        )
