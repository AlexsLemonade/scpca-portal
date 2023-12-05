from django.http import JsonResponse
from rest_framework import viewsets

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
            diagnoses_options.update((d for d in (project["diagnoses"] or "").split(", ") if d))
            modalities.update(project["modalities"])
            seq_units_options.update(su for su in (project["seq_units"] or "").split(", ") if su)
            technologies_options.update(t for t in (project["technologies"] or "").split(", ") if t)

        return JsonResponse(
            {
                "diagnoses": sorted(diagnoses_options),
                "modalities": sorted(modalities),
                "seq_units": sorted(seq_units_options),
                "technologies": sorted(technologies_options),
            }
        )
