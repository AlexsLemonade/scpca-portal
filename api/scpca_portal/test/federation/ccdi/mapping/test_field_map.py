"""Tests for the machinery that runs an entity's getters."""

from functools import partial

from django.test import SimpleTestCase

from pydantic import BaseModel, Field

from scpca_portal.federation.ccdi.mapping import reported
from scpca_portal.federation.ccdi.mapping.field_map import (
    STANDARD_MARKERS,
    FieldMap,
    description_of,
    field_shapes,
    is_field_wrapper,
    shape_of,
    standard_of,
    without_none,
)
from scpca_portal.federation.ccdi.schema import FileMetadata, SampleMetadata, SubjectMetadata, dump
from scpca_portal.test.federation.ccdi.mapping.helpers import build_context, build_library


def build_field_map():
    """A field map of this entity's shape, isolated from the registered mappings."""
    return FieldMap("sample", SampleMetadata)


class WrapperDerivationTests(SimpleTestCase):
    def test_wrappers_come_from_the_generated_type(self):
        # Nothing hand-declares these, so they cannot drift from the spec.
        shapes = field_shapes(SampleMetadata)

        self.assertEqual(shapes["diagnosis"][0].__name__, "FieldUnownedSampleDiagnosis")
        self.assertFalse(shapes["diagnosis"][1])

    def test_list_fields_are_recognised(self):
        self.assertTrue(field_shapes(SampleMetadata)["identifiers"][1])

    def test_fields_the_spec_does_not_wrap_are_recognised(self):
        wrapper, _ = field_shapes(SampleMetadata)["depositions"]

        self.assertNotIn("value", wrapper.model_fields)


class ShapeTests(SimpleTestCase):
    def test_an_optional_is_unwrapped(self):
        self.assertEqual(shape_of(int | None), (int, False))

    def test_a_list_is_recognised_with_or_without_an_optional(self):
        # A required list would silently lose its list-ness if `without_none`
        # stripped any single-argument generic rather than just a union.
        self.assertEqual(shape_of(list[int] | None), (int, True))
        self.assertEqual(shape_of(list[int]), (int, True))

    def test_a_plain_type_passes_through(self):
        self.assertIs(without_none(int), int)
        self.assertEqual(shape_of(int), (int, False))


class UnmappedFieldTests(SimpleTestCase):
    def test_a_field_with_no_getter_emits_null_under_a_present_key(self):
        emitted = build_field_map().build(build_context()).model_dump(mode="json")

        for field in field_shapes(SampleMetadata):
            with self.subTest(field=field):
                self.assertIn(field, emitted)
                self.assertIsNone(emitted[field])

    def test_metadata_with_nothing_mapped_still_validates(self):
        built = build_field_map().build(build_context())

        SampleMetadata.model_validate(built.model_dump(mode="json"))

    def test_optional_keys_are_absent_rather_than_null(self):
        # Harmonized keys are required-but-nullable, so a null is a legitimate
        # "we have nothing". `unharmonized` is optional and not nullable, so the
        # spec only accepts it absent.
        emitted = dump(build_field_map().build(build_context()))

        self.assertNotIn("unharmonized", emitted)
        self.assertIn("diagnosis", emitted)
        self.assertIsNone(emitted["diagnosis"])


class MappedFieldTests(SimpleTestCase):
    def test_a_getter_populates_the_field_it_is_named_after(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_diagnosis(scpca):
            return reported(scpca.sample.metadata.get("diagnosis"))

        emitted = field_map.build(build_context(diagnosis="Glioblastoma")).model_dump(mode="json")

        self.assertEqual(emitted["diagnosis"]["value"], "Glioblastoma")
        self.assertIsNone(emitted["tissue_type"])

    def test_a_getter_reads_either_half_of_the_pair(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_library_source_material(scpca):
            return {"cell": "Single-cells"}.get(reported(scpca.library.metadata.get("seq_unit")))

        context = build_context(library=build_library(seq_unit="cell"))
        emitted = field_map.build(context).model_dump(mode="json")

        self.assertEqual(emitted["library_source_material"]["value"], "Single-cells")

    def test_a_list_field_wraps_each_value(self):
        field_map = FieldMap("subject", SubjectMetadata)

        @field_map.harmonized
        def get_race(scpca):
            return ["White", "Asian"]

        emitted = field_map.build(None).model_dump(mode="json")

        self.assertEqual([entry["value"] for entry in emitted["race"]], ["White", "Asian"])


class RegistrationTests(SimpleTestCase):
    def test_a_field_the_spec_lacks_is_rejected(self):
        field_map = build_field_map()

        with self.assertRaises(ValueError) as raised:

            @field_map.harmonized
            def get_diagnosis_catgeory(scpca):  # typo
                return None

        self.assertIn("diagnosis_catgeory", str(raised.exception))

    def test_a_field_that_is_not_harmonized_is_rejected(self):
        # `depositions` and `unharmonized` are real CCDI keys but not `{"value": …}`
        # fields, so they have no wiki page and can't be described as harmonized.
        field_map = build_field_map()

        for field in ("depositions", "unharmonized"):
            with self.subTest(field=field):
                # A real function, so this exercises the harmonized-field check
                # rather than passing on the callability one.
                def getter(scpca):
                    return None

                getter.__name__ = f"get_{field}"

                with self.assertRaises(ValueError) as raised:
                    field_map.harmonized(getter)

                self.assertIn("not a harmonized field", str(raised.exception))

    def test_something_with_no_name_is_rejected_clearly(self):
        # A partial or callable object can't say which field it maps.
        field_map = build_field_map()

        with self.assertRaises(ValueError) as raised:
            field_map.harmonized(partial(lambda scpca: None))

        self.assertIn("__name__", str(raised.exception))

    def test_a_getter_that_cannot_take_a_record_is_rejected(self):
        # `build` contains a getter that raises, so a wrong signature would not
        # fail loudly — the field would degrade to null for every record while
        # staying advertised on /metadata/fields as one the node populates.
        field_map = build_field_map()

        def no_arguments():
            return None

        def too_many(self, scpca):
            return None

        for getter in (no_arguments, too_many):
            getter.__name__ = "get_diagnosis"
            with self.subTest(getter=getter):
                with self.assertRaises(ValueError) as raised:
                    field_map.harmonized(getter)

                self.assertIn("takes one argument", str(raised.exception))

    def test_a_getter_that_is_not_callable_is_rejected(self):
        # A `classmethod` object is the realistic way to land here.
        field_map = build_field_map()

        class Mappings:
            @classmethod
            def get_diagnosis(cls, scpca):
                return None

        with self.assertRaises(ValueError) as raised:
            field_map.harmonized(Mappings.__dict__["get_diagnosis"])

        self.assertIn("must be callable", str(raised.exception))

    def test_the_shapes_a_getter_may_legitimately_take_are_accepted(self):
        # The check must not narrow what a mapping is allowed to look like.
        class Mappings:
            @staticmethod
            def get_diagnosis(scpca):
                return None

        def with_defaults(scpca, fallback=None):
            return None

        def varargs(*records):
            return None

        for getter in (Mappings.__dict__["get_diagnosis"], with_defaults, varargs):
            with self.subTest(getter=getter):
                field_map = build_field_map()
                if not isinstance(getter, staticmethod):
                    getter.__name__ = "get_diagnosis"

                field_map.harmonized(getter)

                self.assertEqual([entry.path for entry in field_map.describe()], ["diagnosis"])

    def test_a_getter_not_named_for_its_field_is_rejected_with_the_rename(self):
        field_map = build_field_map()

        with self.assertRaises(ValueError) as raised:

            @field_map.harmonized
            def diagnosis(scpca):
                return None

        self.assertIn("rename 'diagnosis' to 'get_diagnosis'", str(raised.exception))

    def test_harmonized_written_with_parentheses_raises(self):
        # The spelling that used to register nothing at all. `harmonized` is a
        # plain decorator, so Python rejects the call before our code runs.
        field_map = build_field_map()

        with self.assertRaises(TypeError) as raised:

            @field_map.harmonized()
            def get_diagnosis(scpca):
                return None

        self.assertIn("getter", str(raised.exception))

    def test_mapping_one_field_twice_is_rejected(self):
        # Two getters for one field is a mistake, and the old behaviour was to
        # half-apply it: the second getter won while the first one's standard
        # stayed behind.
        field_map = build_field_map()

        @field_map.harmonized
        def get_diagnosis(scpca):
            return "FIRST"

        with self.assertRaises(ValueError) as raised:

            @field_map.harmonized
            def get_diagnosis(scpca):  # noqa: F811
                return "SECOND"

        self.assertIn("already mapped", str(raised.exception))

    def test_a_field_named_after_a_python_builtin_is_mappable(self):
        # `File.type` is a real harmonized field, and the prefix is why it can be
        # written as an ordinary function without shadowing `type`.
        field_map = FieldMap("file", FileMetadata)

        @field_map.harmonized
        def get_type(scpca):
            return None

        self.assertEqual([entry.path for entry in field_map.describe()], ["type"])

    def test_one_getter_can_serve_two_entities(self):
        # `identifiers` means the same thing on both, and registration keeps no
        # state on the function, so the same getter can be registered twice.
        subjects = FieldMap("subject", SubjectMetadata)
        samples = build_field_map()

        def get_identifiers(scpca):
            return None

        subjects.harmonized(get_identifiers)
        samples.harmonized(get_identifiers)

        self.assertEqual([d.path for d in subjects.describe()], ["identifiers"])
        self.assertEqual([d.path for d in samples.describe()], ["identifiers"])


class FailureContainmentTests(SimpleTestCase):
    def test_a_getter_that_raises_degrades_its_own_field(self):
        # ScPCA columns are free text, so a converter can hit something it cannot
        # parse. That must not take the whole response with it.
        field_map = build_field_map()

        @field_map.harmonized
        def get_age_at_diagnosis(scpca):
            return float(scpca.sample.metadata["age"]) * 365.25

        @field_map.harmonized
        def get_diagnosis(scpca):
            return "Glioblastoma"

        with self.assertLogs("scpca_portal.federation.ccdi.mapping.field_map", "ERROR"):
            emitted = field_map.build(build_context(age="Unknown")).model_dump(mode="json")

        self.assertIsNone(emitted["age_at_diagnosis"])
        self.assertEqual(emitted["diagnosis"]["value"], "Glioblastoma")

    def test_a_scalar_given_to_a_list_field_degrades_its_own_field(self):
        # Iterating a bare string would emit one entry per character, and the
        # spec's free-text list fields would accept every one of them.
        field_map = FieldMap("subject", SubjectMetadata)

        @field_map.harmonized
        def get_associated_diagnoses(scpca):
            return "Neuroblastoma"

        with self.assertLogs("scpca_portal.federation.ccdi.mapping.field_map", "ERROR"):
            emitted = field_map.build(None).model_dump(mode="json")

        self.assertIsNone(emitted["associated_diagnoses"])

    def test_a_value_outside_the_cde_enum_degrades_its_own_field(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_disease_phase(scpca):
            return "Initial diagnosis"  # the CDE spells it "Initial Diagnosis"

        with self.assertLogs("scpca_portal.federation.ccdi.mapping.field_map", "ERROR"):
            emitted = field_map.build(build_context()).model_dump(mode="json")

        self.assertIsNone(emitted["disease_phase"])


class DescribeTests(SimpleTestCase):
    def test_only_mapped_fields_are_described(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_diagnosis(scpca):
            return None

        described = field_map.describe()

        self.assertEqual([entry.path for entry in described], ["diagnosis"])
        self.assertTrue(described[0].harmonized)

    def test_a_description_links_the_field_s_wiki_page(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_diagnosis(scpca):
            return None

        self.assertEqual(
            field_map.describe()[0].wiki_url,
            "https://github.com/CBIIT/ccdi-federation-api/wiki/Sample-Metadata-Fields#diagnosis",
        )

    def test_a_known_field_carries_its_cadsr_identifier(self):
        # The anchor: one field, exact values, end to end through `describe()`.
        # A loop over every field can still pass with the name and url swapped,
        # or with the whole derivation wired to nothing.
        field_map = FieldMap("subject", SubjectMetadata)

        @field_map.harmonized
        def get_sex(scpca):
            return None

        standard = field_map.describe()[0].standard

        self.assertEqual(standard.name, "caDSR")
        self.assertIn("6343385", standard.url)

    def test_a_field_the_spec_does_not_standardize_has_no_standard(self):
        field_map = build_field_map()

        @field_map.harmonized
        def get_age_at_diagnosis(scpca):
            return None

        self.assertIsNone(field_map.describe()[0].standard)

    def test_nothing_is_described_before_anything_is_mapped(self):
        self.assertEqual(build_field_map().describe(), [])


class SpecStandardTests(SimpleTestCase):
    """
    The caDSR standard on `/metadata/fields` is read off the generated type, not
    declared at a call site, so it cannot drift from the spec. The cost is that
    it comes out of prose, and this is what notices a spec reformat.

    Coverage only — that every field the spec marks still parses. Whether the
    parser over-matches cannot be tested from the spec: `standard_of` needs both
    regexes to match, each contains a literal that is itself a marker, so
    "unmarked implies no standard" is true by construction here no matter what
    the corpus holds. `DerivedStandardTests` supplies its own input for that.
    """

    ENTITIES = (
        ("subject", SubjectMetadata),
        ("sample", SampleMetadata),
        ("file", FileMetadata),
    )

    def wrapped_fields(self):
        """Every harmonized field across the three entities, with its wrapper."""
        for entity, metadata_type in self.ENTITIES:
            for field, (wrapper, _) in field_shapes(metadata_type).items():
                if is_field_wrapper(wrapper):
                    yield entity, field, wrapper

    def test_every_field_the_spec_marks_with_a_standard_yields_one(self):
        # The trigger is broader than the parser on purpose: if CCDI restyles the
        # bold CDE marker but keeps the `Link:` block, a field still looks
        # standardized here while failing to parse, and this fails rather than
        # quietly dropping standards from the endpoint.
        unparsed = [
            f"{entity}.{field}"
            for entity, field, wrapper in self.wrapped_fields()
            if any(marker in description_of(wrapper) for marker in STANDARD_MARKERS)
            and standard_of(wrapper) is None
        ]

        self.assertEqual(unparsed, [], "the spec documents a standard these no longer parse")

    def test_the_spec_still_marks_the_fields_it_did(self):
        # A field losing its CDE upstream changes what the node advertises to
        # federated consumers. The drift test does not cover it: vendoring a new
        # swagger.yml and regenerating changes both sides together and passes.
        marked = {
            f"{entity}.{field}"
            for entity, field, wrapper in self.wrapped_fields()
            if standard_of(wrapper) is not None
        }

        self.assertEqual(len(marked), 17, sorted(marked))


def described(text):
    """A stand-in for a generated field wrapper carrying `text` as its prose."""

    class Wrapper(BaseModel):
        value: str = Field(description=text)

    return Wrapper


class DerivedStandardTests(SimpleTestCase):
    """
    What the parser does with input we control.

    This is where over-matching is caught. Scanning the real spec cannot do it:
    a derived standard requires both regexes to match, and each demands a literal
    that is also a `STANDARD_MARKERS` entry, so no field can be unmarked *and*
    carry a standard however the regexes are loosened — unless both are loosened
    at once, which is not how either would be edited. Supplying the description
    isolates each half.
    """

    WELL_FORMED = (
        "**`caDSR CDE 6343385 v1.00`**\n\nSex of the subject.\n\nLink:\n"
        "<https://cadsr.cancer.gov/onedata/dmdirect/NIH/NCI/CO/CDEDD?filter=ITEM_ID=6343385>"
    )

    def test_a_well_formed_description_yields_its_standard(self):
        standard = standard_of(described(self.WELL_FORMED))

        self.assertEqual(standard.name, "caDSR")
        self.assertIn("6343385", standard.url)

    def test_a_url_in_unrelated_prose_is_not_a_standard(self):
        # `sample.diagnosis` and two others really do carry a bare URL, so a
        # `CDE_LINK` loosened to match one would invent standards for them.
        standard = standard_of(
            described("The diagnosis. See https://example.org/guidance for how to pick one.")
        )

        self.assertIsNone(standard)

    def test_a_cde_marker_without_a_link_block_is_not_a_standard(self):
        # Fails if `CDE_LINK` stops requiring `Link:` — on its own, with
        # `CDE_MARKER` untouched, which is the realistic single-regex edit.
        standard = standard_of(
            described("**`caDSR CDE 6343385 v1.00`** https://cadsr.cancer.gov/x?ITEM_ID=6343385")
        )

        self.assertIsNone(standard)

    def test_a_link_block_without_a_cde_marker_is_not_a_standard(self):
        # The mirror: fails if `CDE_MARKER` stops requiring the authority.
        standard = standard_of(described("Link:\n<https://example.org/some/registry>"))

        self.assertIsNone(standard)

    def test_an_authority_other_than_cadsr_is_not_read(self):
        # Deliberate: only caDSR is parsed, so a standard body the spec starts
        # using shows up as a coverage failure — a decision to make — rather than
        # quietly appearing on /metadata/fields. Without this, loosening the
        # authority in `CDE_MARKER` changes what the node publishes silently.
        standard = standard_of(
            described(
                "**`NCIt CDE 6343385 v1.00`**\n\nA field.\n\nLink:\n"
                "<https://example.org/registry/6343385>"
            )
        )

        self.assertIsNone(standard)

    def test_prose_naming_the_authority_is_not_a_standard(self):
        standard = standard_of(described("Its vocabulary is defined by the CCDI caDSR CDEs."))

        self.assertIsNone(standard)

    def test_a_description_with_no_prose_at_all_is_not_a_standard(self):
        self.assertIsNone(standard_of(described("")))
