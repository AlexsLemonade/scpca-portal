from django.forms.models import model_to_dict
from django.test import TestCase

from scpca_portal.serializers import ProjectSummarySerializer
from scpca_portal.test.factories import ProjectSummaryFactory


class TestProjectSummarySerializer(TestCase):
    def setUp(self):
        self.project_summary_data = model_to_dict(ProjectSummaryFactory())

    # TODO(arkid15r): revisit after changing project field to not nullable.
    def test_serializer_with_empty_data(self):
        serializer = ProjectSummarySerializer(data={})
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_valid_data(self):
        serializer = ProjectSummarySerializer(data=self.project_summary_data)
        self.assertTrue(serializer.is_valid())
