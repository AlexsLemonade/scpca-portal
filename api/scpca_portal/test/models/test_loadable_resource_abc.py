from unittest.mock import patch

from django.test import TestCase

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.test.factories import LeafProjectFactory, OriginalFileFactory


class TestLoadableResourceABC(TestCase):
    """
    Exercises logic that lives exclusively on LoadableResourceABC, via Project as
    a stand-in concrete model. Tests for logic overridden by derived models
    (e.g. sync_metadata) live on those models' own test classes instead.
    """

    def setUp(self):
        self.resource = LeafProjectFactory.build()
        for file_hash in ["1234567890ab", "cdefghijklmn", "opqrstuvwxyz"]:
            OriginalFileFactory(project_id=self.resource.scpca_id, hash=file_hash)

    def test_current_loaded_hash(self):
        expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
        self.assertEqual(self.resource.current_loaded_hash, expected_loaded_hash)

    def test_update_loaded_state(self):
        loaded_state = LoadableResourceStates.NEW
        resource = self.resource
        with patch.object(resource, "save") as mock_save:
            # test fresh object
            resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(resource.loaded_state, loaded_state)
            self.assertIsNotNone(resource.updated_at)
            self.assertIsNone(resource.loaded_hash)
            self.assertIsNone(resource.loaded_at)

            # test synced object
            loaded_state = LoadableResourceStates.SYNCED
            resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
            self.assertEqual(resource.loaded_state, LoadableResourceStates.SYNCED)
            self.assertEqual(resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(resource.updated_at)
            self.assertIsNotNone(resource.loaded_at)
            self.assertGreater(resource.loaded_at, resource.updated_at)

            # test existing object
            loaded_state = LoadableResourceStates.TAINTED
            resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(resource.loaded_state, loaded_state)
            self.assertEqual(resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(resource.updated_at)
            self.assertIsNotNone(resource.loaded_at)
            self.assertGreater(resource.updated_at, resource.loaded_at)

            # test save override
            resource.update_loaded_state(loaded_state, save=False)
            mock_save.assert_not_called()
