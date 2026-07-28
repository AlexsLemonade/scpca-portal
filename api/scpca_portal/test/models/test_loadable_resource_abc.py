from typing import Any, Dict
from unittest.mock import patch

from django.db import models
from django.db.models import QuerySet
from django.test import TestCase

from typing_extensions import Self

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

    scpca_id = models.TextField(unique=True)
    has_bulk_rna_seq = models.BooleanField(default=False)
    has_cite_seq_data = models.BooleanField(default=False)
    has_multiplexed_data = models.BooleanField(default=False)

    def __init__(
        self,
        scpca_id="SCPCX999999999",
        loaded_state=LoadableResourceStates.NEW,
        loaded_original_files_qs=None,
        **kwargs,
    ):
        # loaded_hash is forced to None here because CharField(null=True) with no explicit
        # default otherwise resolves to "", which would break the "no hash yet" assertions below
        super().__init__(scpca_id=scpca_id, loaded_state=loaded_state, loaded_hash=None, **kwargs)
        self._loaded_original_files_qs = loaded_original_files_qs or OriginalFile.objects.none()

    @property
    def loaded_original_files(self) -> QuerySet[OriginalFile]:
        return self._loaded_original_files_qs

    @classmethod
    def get_from_dict(cls, data: Dict, *args: Any, **kwargs: Any) -> Self:
        pass

    def update_from_dict(self, data: Dict) -> Self:
        self.has_bulk_rna_seq = data["has_bulk_rna_seq"]
        self.has_cite_seq_data = data["has_cite_seq_data"]
        self.has_multiplexed_data = data["has_multiplexed_data"]
        return self

    @classmethod
    def get_loaded_state_metadata_dicts_by_id(cls, loaded_states=[]) -> Dict[str, Dict]:
        pass


class TestLoadableResourceABC(TestCase):
    def setUp(self):
        loaded_original_files = [
            OriginalFileFactory(hash="1234567890ab"),
            OriginalFileFactory(hash="cdefghijklmn"),
            OriginalFileFactory(hash="opqrstuvwxyz"),
        ]
        self.loaded_original_files_qs = OriginalFile.objects.filter(
            pk__in=[of.pk for of in loaded_original_files]
        )

    def make_resource(self, scpca_id, loaded_state=LoadableResourceStates.NEW):
        return ConcreteLoadableResource(
            scpca_id=scpca_id,
            loaded_state=loaded_state,
            loaded_original_files_qs=self.loaded_original_files_qs,
        )

    def test_current_loaded_hash(self):
        expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
        loadable_resource = self.make_resource("SCPCX000001")
        self.assertEqual(loadable_resource.current_loaded_hash, expected_loaded_hash)

    def test_update_loaded_state(self):
        loaded_state = LoadableResourceStates.NEW
        loadable_resource = self.make_resource("SCPCX000001", loaded_state=loaded_state)
        with patch.object(loadable_resource, "save") as mock_save:
            # test fresh object
            loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(loadable_resource.loaded_state, loaded_state)
            self.assertIsNotNone(loadable_resource.updated_at)
            self.assertIsNone(loadable_resource.loaded_hash)
            self.assertIsNone(loadable_resource.loaded_at)

            # test synced object
            loaded_state = LoadableResourceStates.SYNCED
            loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            expected_loaded_hash = "928f7bcdcd08869cc44c1bf24e7abec6"
            self.assertEqual(loadable_resource.loaded_state, LoadableResourceStates.SYNCED)
            self.assertEqual(loadable_resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(loadable_resource.updated_at)
            self.assertIsNotNone(loadable_resource.loaded_at)
            self.assertGreater(loadable_resource.loaded_at, loadable_resource.updated_at)

            # test existing object
            loaded_state = LoadableResourceStates.TAINTED
            loadable_resource.update_loaded_state(loaded_state)
            mock_save.assert_called_once()
            mock_save.reset_mock()

            self.assertEqual(loadable_resource.loaded_state, loaded_state)
            self.assertEqual(loadable_resource.loaded_hash, expected_loaded_hash)
            self.assertIsNotNone(loadable_resource.updated_at)
            self.assertIsNotNone(loadable_resource.loaded_at)
            self.assertGreater(loadable_resource.updated_at, loadable_resource.loaded_at)

            # test save override
            loadable_resource.update_loaded_state(loaded_state, save=False)
            mock_save.assert_not_called()

    def test_sync_metadata(self):
        new_resource = self.make_resource("SCPCX000001", LoadableResourceStates.NEW)
        tainted_resource = self.make_resource("SCPCX000002", LoadableResourceStates.TAINTED)
        updatable_resources = [new_resource, tainted_resource]

        metadata_by_id = {
            "SCPCX000001": {
                "has_bulk_rna_seq": True,
                "has_cite_seq_data": True,
                "has_multiplexed_data": False,
            },
            "SCPCX000002": {
                "has_bulk_rna_seq": True,
                "has_cite_seq_data": False,
                "has_multiplexed_data": True,
            },
        }

        with (
            patch.object(ConcreteLoadableResource, "objects") as mock_manager,
            patch.object(
                ConcreteLoadableResource,
                "get_loaded_state_metadata_dicts_by_id",
                return_value=metadata_by_id,
            ) as mock_get_metadata,
        ):
            mock_manager.filter.return_value = updatable_resources

            ConcreteLoadableResource.sync_metadata()

            # verify inputs (correct states are queried for and passed through for metadata lookup)
            mock_manager.filter.assert_called_once_with(
                loaded_state__in=[LoadableResourceStates.NEW, LoadableResourceStates.TAINTED]
            )
            mock_get_metadata.assert_called_once_with(
                loaded_states=[LoadableResourceStates.NEW, LoadableResourceStates.TAINTED]
            )

            # verify outputs (each resource is updated from its own metadata dict and marked synced)
            self.assertTrue(new_resource.has_bulk_rna_seq)
            self.assertTrue(new_resource.has_cite_seq_data)
            self.assertFalse(new_resource.has_multiplexed_data)

            self.assertTrue(tainted_resource.has_bulk_rna_seq)
            self.assertFalse(tainted_resource.has_cite_seq_data)
            self.assertTrue(tainted_resource.has_multiplexed_data)

            for resource in updatable_resources:
                self.assertEqual(resource.loaded_state, LoadableResourceStates.SYNCED)
                self.assertIsNotNone(resource.loaded_hash)
                self.assertIsNotNone(resource.loaded_at)

            # verify outputs (persisted via a single bulk_update covering all non-pk fields)0
            mock_manager.bulk_update.assert_called_once()
            args, kwargs = mock_manager.bulk_update.call_args
            self.assertEqual(list(args[0]), updatable_resources)
            expected_fields = [
                f.name for f in ConcreteLoadableResource._meta.concrete_fields if not f.primary_key
            ]
            self.assertCountEqual(kwargs["fields"], expected_fields)

        # test no updatable resources
        with (
            patch.object(ConcreteLoadableResource, "objects") as mock_manager,
            patch.object(
                ConcreteLoadableResource, "get_loaded_state_metadata_dicts_by_id"
            ) as mock_get_metadata,
        ):
            mock_manager.filter.return_value = []

            ConcreteLoadableResource.sync_metadata()

            mock_get_metadata.assert_not_called()
            mock_manager.bulk_update.assert_not_called()
