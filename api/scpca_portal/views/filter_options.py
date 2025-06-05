from django.http import JsonResponse
from rest_framework import viewsets

from scpca_portal.models import Project


class FilterOptionsViewSet(viewsets.ViewSet):
    def list(self, request):
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
