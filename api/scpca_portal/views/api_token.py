from rest_framework import mixins, serializers, viewsets

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from scpca_portal.models import APIToken


class APITokenSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(write_only=True)

    class Meta:
        model = APIToken
        fields = ("id", "is_activated", "terms_and_conditions", "email")
        extra_kwargs = {
            "id": {"read_only": True},
            "is_activated": {"read_only": False},
            "terms_and_conditions": {"read_only": True},
            "email": {"write_only": True},
        }


@extend_schema(
    request=APITokenSerializer,
    auth=False,
    examples=[
        OpenApiExample("Example Token Response"),
    ],
)
@extend_schema_view(
    create=extend_schema(
        description="""Create an API token to confirm that Terms of Service are agreed.
        Used for adding a HTTP header to requests for any endpoint that requires token
        authentication. **Do not share your Token ID**"""
    ),
    retrieve=extend_schema(description="Retreive token status by Token ID."),
    update=extend_schema(description="Update the token's activation status."),
)
class APITokenViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Tokens for accessing restricted data from the portal.
    """

    model = APIToken
    lookup_field = "id"
    queryset = APIToken.objects.all()
    serializer_class = APITokenSerializer
