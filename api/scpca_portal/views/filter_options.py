from django.http import JsonResponse
from rest_framework import viewsets, serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse

from scpca_portal.models import Project

class FilterOptionsResponseSerializer(serializers.Serializer):
    diagnoses = serializers.ListField(child=serializers.CharField())
    modalities = serializers.ListField(child=serializers.CharField())
    seq_units = serializers.ListField(child=serializers.CharField())
    technologies = serializers.ListField(child=serializers.CharField())
    organisms = serializers.ListField(child=serializers.CharField())
    models = serializers.ListField(child=serializers.CharField())

class FilterOptionsViewSet(viewsets.ViewSet):
    @extend_schema(
        auth=False,
        responses={
            200: OpenApiResponse(response=FilterOptionsResponseSerializer),
        },
    )
    def list(self, request):
        """
           Provides a list of all options for project filters.
           This includes diagnoses, modalities, seq_units,
           technologies, organisms, and models.
        """
        diagnoses_options = set()
        modalities = set()
        seq_units_options = set()
        technologies_options = set()
        organisms_options = set()
        models_options = {"includes_xenografts", "includes_cell_lines"}

        for project in Project.objects.values(
            "diagnoses", "modalities", "seq_units", "technologies", "organisms"
        ):
            diagnoses_options.update((d for d in project["diagnoses"] if d))
            modalities.update(project["modalities"])
            seq_units_options.update(su for su in project["seq_units"] if su)
            technologies_options.update(t for t in project["technologies"] if t)
            organisms_options.update(o for o in project["organisms"] if o)

        return JsonResponse(
            {
                "diagnoses": sorted(diagnoses_options),
                "modalities": sorted(modalities),
                "seq_units": sorted(seq_units_options),
                "technologies": sorted(technologies_options),
                "organisms": sorted(organisms_options),
                "models": sorted(models_options),
            }
        )
