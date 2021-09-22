from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from scpca_portal.models import Project


@api_view(["GET"])
def project_filter_options_view(request):
    dicts = Project.objects.order_by().values("diagnoses", "seq_units", "technologies").distinct()

    diagnoses_options = set()
    seq_units_options = set()
    technologies_options = set()
    for value_set in dicts:
        if value_set["diagnoses"]:
            for value in value_set["diagnoses"].split(", "):
                diagnoses_options.add(value)

        if value_set["seq_units"]:
            for value in value_set["seq_units"].split(", "):
                seq_units_options.add(value)

        if value_set["technologies"]:
            for value in value_set["technologies"].split(", "):
                technologies_options.add(value)

    response_dict = {
        "diagnoses": list(diagnoses_options),
        "seq_units": list(seq_units_options),
        "technologies": list(technologies_options),
    }

    return JsonResponse(response_dict, status=status.HTTP_200_OK)
