from unittest.mock import MagicMock

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

    class Meta:
        db_table = "concrete_loadable_resource"

    def __init__(self, original_files_qs=None):
        self.state = LoadableResourceStates.NEW
        self.hash = None
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
        self.qs = OriginalFile.objects.filter(pk__in=[of.pk for of in original_files])
        ConcreteLoadableResource.objects = MagicMock()

        self.loadable_resource = ConcreteLoadableResource(original_files_qs=self.qs)

    def test_current_hash(self):
        expected = "12345"
        self.assertEqual(self.loadable_resource.current_hash, expected)

    def test_update_loadable_state(self):
        # test fresh object
        state = LoadableResourceStates.NEW
        self.loadable_resource.update_loadable_state(state)

        self.assertEqual(self.loadable_resource.state, state)
        self.assertIsNotNone(self.loadable_resource.updated_at)
        self.assertIsNone(self.loadable_resource.hash)
        self.assertIsNone(self.loadable_resource.loaded_at)

        # test synced object
        state = LoadableResourceStates.SYNCED
        self.loadable_resource.update_loadable_state(state)

        expected_hash = "12345"
        self.assertEqual(self.loadable_resource.state, LoadableResourceStates.SYNCED)
        self.assertEqual(self.loadable_resource.hash, expected_hash)
        self.assertIsNotNone(self.loadable_resource.updated_at)
        self.assertIsNotNone(self.loadable_resource.loaded_at)
        self.assertGreater(self.loadable_resource.loaded_at, self.loadable_resource.updated_at)

        # test existing object
        state = LoadableResourceStates.TAINTED
        self.loadable_resource.update_loadable_state(state)

        self.assertEqual(self.loadable_resource.state, state)
        self.assertEqual(self.loadable_resource.hash, expected_hash)
        self.assertIsNotNone(self.loadable_resource.updated_at)
        self.assertIsNotNone(self.loadable_resource.loaded_at)
        self.assertGreater(self.loadable_resource.updated_at, self.loadable_resource.loaded_at)
