from django.test import TestCase, tag

from scpca_portal.models import Library, Project, Sample
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

    def test_purge(self):
        project = ProjectFactory()
        sample_pks = list(project.samples.values_list("pk", flat=True))
        library_pks = list(project.libraries.values_list("pk", flat=True))
        # Ensure the factory created related objects to purge
        self.assertTrue(sample_pks)
        self.assertTrue(library_pks)

        project.purge()

        # Should delete the project and its samples and libraries
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())
        self.assertFalse(Sample.objects.filter(pk__in=sample_pks).exists())
        self.assertFalse(Library.objects.filter(pk__in=library_pks).exists())
