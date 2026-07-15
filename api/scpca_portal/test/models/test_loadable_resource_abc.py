from unittest.mock import patch

from django.db.models import QuerySet
from django.test import TestCase

from scpca_portal.enums import LoadableResourceStates
from scpca_portal.models.loadable_resource_abc import LoadableResourceABC
from scpca_portal.models.original_file import OriginalFile
from scpca_portal.test.factories import OriginalFileFactory


class ConcreteLoadableResource(LoadableResourceABC):
    """
    Minimal test double for LoadableResourceABC.

    Delegates method calls directly to the ABC so its logic is exercised without
    coupling these tests to Project, Sample, or Library models.
    """

    def __init__(self, original_files_qs=None):
        super().__init__()
        self.loaded_state = LoadableResourceStates.NEW
        self.loaded_hash = None
        self.loaded_at = None
        self.updated_at = None
        self._original_files_qs = original_files_qs or OriginalFile.objects.none()

    @property
    def original_files(self) -> QuerySet[OriginalFile]:
        return self._original_files_qs


class TestLoadableResourceABC(TestCase):
    def setUp(self):
        original_files = [
            OriginalFileFactory(hash="1234567890ab"),
            OriginalFileFactory(hash="cdefghijklmn"),
            OriginalFileFactory(hash="opqrstuvwxyz"),
        ]
        qs = OriginalFile.objects.filter(pk__in=[of.pk for of in original_files])
        self.loadable_resource = ConcreteLoadableResource(original_files_qs=qs)

    def test_current_loaded_hash(self):
        expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
        self.assertEqual(self.loadable_resource.current_loaded_hash, expected_loaded_hash)

    def test_update_loaded_state(self):
        with patch.object(self.loadable_resource, "save") as mock_save:
            # test fresh object
            loaded_state = LoadableResourceStates.NEW
            self.loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(self.loadable_resource.loaded_state, loaded_state)
            self.assertIsNotNone(self.loadable_resource.updated_at)
            self.assertIsNone(self.loadable_resource.loaded_hash)
            self.assertIsNone(self.loadable_resource.loaded_at)

            # test synced object
            loaded_state = LoadableResourceStates.SYNCED
            self.loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
            self.assertEqual(self.loadable_resource.loaded_state, LoadableResourceStates.SYNCED)
            self.assertEqual(self.loadable_resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(self.loadable_resource.updated_at)
            self.assertIsNotNone(self.loadable_resource.loaded_at)
            self.assertGreater(self.loadable_resource.loaded_at, self.loadable_resource.updated_at)

            # test existing object
            loaded_state = LoadableResourceStates.TAINTED
            self.loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(self.loadable_resource.loaded_state, loaded_state)
            self.assertEqual(self.loadable_resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(self.loadable_resource.updated_at)
            self.assertIsNotNone(self.loadable_resource.loaded_at)
            self.assertGreater(self.loadable_resource.updated_at, self.loadable_resource.loaded_at)

            # test save override
            self.loadable_resource.update_loaded_state(loaded_state, save=False)
            mock_save.assert_not_called()
