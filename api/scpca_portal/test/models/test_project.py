from datetime import datetime
from unittest.mock import patch

from django.test import TestCase, tag
from django.utils.timezone import make_aware

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models import Project
from scpca_portal.test.factories import LeafProjectFactory, ProjectFactory


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

    def test_sync_metadata(self):
        original_loaded_at_timestamp = make_aware(datetime.now())

        new_project = LeafProjectFactory(loaded_state=LoadableResourceStates.NEW)
        tainted_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.TAINTED, loaded_at=original_loaded_at_timestamp
        )
        # synced project should be left untouched
        synced_project = LeafProjectFactory(
            loaded_state=LoadableResourceStates.SYNCED, loaded_at=original_loaded_at_timestamp
        )

        updatable_projects = [new_project, tainted_project]

        metadata_by_id = {
            new_project.scpca_id: {
                "scpca_project_id": new_project.scpca_id,
                "abstract": "New Abstract",
                "human_readable_pi_name": "New Pi",
                "pi_name": "new_pi",
                "title": "New Title",
                "has_bulk_rna_seq": "True",
            },
            tainted_project.scpca_id: {
                "scpca_project_id": tainted_project.scpca_id,
                "abstract": "Tainted Abstract",
                "human_readable_pi_name": "Tainted Pi",
                "pi_name": "tainted_pi",
                "title": "Tainted Title",
                "has_bulk_rna_seq": "False",
            },
        }

        with patch.object(
            Project, "get_metadata_dicts_by_id", return_value=metadata_by_id
        ) as mock_get_metadata:
            Project.sync_metadata()

            # verify inputs (only NEW and TAINTED resources are passed through for metadata lookup)
            mock_get_metadata.assert_called_once()
            resources_arg = mock_get_metadata.call_args.kwargs["resources"]
            self.assertListEqual(
                sorted([project.scpca_id for project in resources_arg]),
                sorted([new_project.scpca_id, tainted_project.scpca_id]),
            )

            # verify outputs
            # (each project is updated from its own metadata dict, marked synced, and persisted)
            for project in updatable_projects:
                project.refresh_from_db()

            self.assertEqual(new_project.abstract, "New Abstract")
            self.assertEqual(new_project.human_readable_pi_name, "New Pi")
            self.assertEqual(new_project.pi_name, "new_pi")
            self.assertEqual(new_project.title, "New Title")
            self.assertTrue(new_project.has_bulk_rna_seq)

            self.assertEqual(tainted_project.abstract, "Tainted Abstract")
            self.assertEqual(tainted_project.human_readable_pi_name, "Tainted Pi")
            self.assertEqual(tainted_project.pi_name, "tainted_pi")
            self.assertEqual(tainted_project.title, "Tainted Title")
            self.assertFalse(tainted_project.has_bulk_rna_seq)

            for project in updatable_projects:
                self.assertEqual(project.loaded_state, LoadableResourceStates.SYNCED)
                self.assertGreater(project.loaded_at, original_loaded_at_timestamp)

            # verify synced project was not touched
            synced_project.refresh_from_db()
            self.assertEqual(synced_project.loaded_at, original_loaded_at_timestamp)

    def test_sync_metadata_no_updatable_resource(self):
        LeafProjectFactory(loaded_state=LoadableResourceStates.SYNCED)

        with patch.object(Project, "get_metadata_dicts_by_id") as mock_get_metadata:
            Project.sync_metadata()

        mock_get_metadata.assert_not_called()
