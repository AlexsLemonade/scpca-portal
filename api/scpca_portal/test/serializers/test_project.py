from django.forms.models import model_to_dict
from django.test import TestCase

from scpca_portal.test.factories import ProjectFactory
from scpca_portal.views.project import ProjectDetailSerializer, ProjectSerializer


class TestProjectSerializer(TestCase):
    def setUp(self):
        """Create a project to get a valid dict, then delete it so we don't
        have a collision on pi_name."""
        project = ProjectFactory()
        self.project_data = model_to_dict(project)
        project.delete()

    def test_serializer_with_empty_data(self):
        serializer = ProjectSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_detail_serializer_with_empty_data(self):
        serializer = ProjectDetailSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_serializer_with_valid_data(self):
        serializer = ProjectSerializer(data=self.project_data)
        self.assertTrue(serializer.is_valid())

    def test_detail_serializer_with_valid_data(self):
        serializer = ProjectDetailSerializer(data=self.project_data)
        self.assertTrue(serializer.is_valid())
