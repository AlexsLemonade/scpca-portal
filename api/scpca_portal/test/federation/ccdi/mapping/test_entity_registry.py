"""Tests for what every CCDI entity has in common."""

from django.test import SimpleTestCase

from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping.file import File
from scpca_portal.federation.ccdi.mapping.sample import Sample
from scpca_portal.federation.ccdi.mapping.subject import Subject
from scpca_portal.federation.ccdi.views.metadata_fields import FIELD_MAPS

ENTITIES = (Subject, Sample, File)


class DeclarationTests(SimpleTestCase):
    def test_each_entity_declares_the_generated_types_it_emits(self):
        for entity in ENTITIES:
            with self.subTest(entity=entity.__name__):
                name = entity.__name__
                self.assertIs(entity.ccdi_type, getattr(schema, name))
                self.assertIs(entity.identifier, getattr(schema, f"{name}Identifier"))
                self.assertIs(entity.FIELDS.metadata_type, getattr(schema, f"{name}Metadata"))

    def test_each_entity_has_its_own_field_map(self):
        # A shared one would register every entity's getters against one metadata
        # type and describe them all under one wiki page.
        self.assertEqual(len({id(entity.FIELDS) for entity in ENTITIES}), len(ENTITIES))

    def test_each_field_map_is_named_for_its_entity(self):
        self.assertEqual([entity.FIELDS.name for entity in ENTITIES], ["subject", "sample", "file"])

    def test_the_view_can_reach_every_entity_by_name(self):
        self.assertEqual(set(FIELD_MAPS), {"subject", "sample", "file"})


class ContractTests(SimpleTestCase):
    def test_an_entity_must_say_what_it_is_called_and_how_to_find_it(self):
        # File implements neither, which is the open decision made visible.
        self.assertEqual(File.__abstractmethods__, {"name", "from_records"})

    def test_a_fully_declared_entity_is_constructible(self):
        for entity in (Subject, Sample):
            with self.subTest(entity=entity.__name__):
                self.assertEqual(entity.__abstractmethods__, frozenset())
