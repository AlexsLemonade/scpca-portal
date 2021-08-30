from rest_framework import mixins, serializers, viewsets

from scpca_portal.models import APIToken


class APITokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = ("id", "is_activated", "terms_and_conditions")
        extra_kwargs = {
            "id": {"read_only": True},
            "is_activated": {"read_only": False},
            "terms_and_conditions": {"read_only": True},
        }


class APITokenViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Create, read, and modify Api Tokens.
    """

    model = APIToken
    lookup_field = "id"
    queryset = APIToken.objects.all()
    serializer_class = APITokenSerializer
