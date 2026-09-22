from django.test import TestCase, tag

from scpca_portal.models import Project
from scpca_portal.test.factories import ProjectFactory


class TestProject(TestCase):

    @tag("lock_projects")
    def test_lock_projects(self):
        projects = [ProjectFactory() for _ in range(3)]
        for project in projects:
            self.assertFalse(project.is_locked)

        project_ids = [p.scpca_id for p in projects]
        Project.lock_projects(project_ids)

        for project in Project.objects.filter(scpca_id__in=project_ids):
            self.assertTrue(project.is_locked)
