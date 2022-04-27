from django.http import JsonResponse
from rest_framework import status, viewsets

from scpca_portal.models import Project


class FilterOptionsViewSet(viewsets.ViewSet):
    def list(self, request):
        diagnoses_options = set()
        modalities = set()
        seq_units_options = set()
        technologies_options = set()

        for project in Project.objects.values(
            "diagnoses", "modalities", "seq_units", "technologies"
        ):
            diagnoses_options.update((project["diagnoses"] or "").split(", "))
            modalities.update((project["modalities"] or "").split(", "))
            seq_units_options.update((project["seq_units"] or "").split(", "))
            technologies_options.update((project["technologies"] or "").split(", "))

        return JsonResponse(
            {
                "diagnoses": sorted(diagnoses_options),
                "modalities": sorted(modalities),
                "seq_units": sorted(seq_units_options),
                "technologies": sorted(technologies_options),
            }
        )
