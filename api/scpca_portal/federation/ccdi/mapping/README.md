# The ScPCA→CCDI mapping layer

This package holds every decision about how ScPCA data becomes CCDI data: which
ScPCA column feeds which CCDI field, and what it converts to. This README is how
to add or change one.

This is the how-to for *doing* mapping work. For the node as a whole — what
answers today, and how to chase down a field that isn't showing up in a response
— see [`../README.md`](../README.md).

## What's where

- **`subject.py`, `sample.py`, `file.py`** — one class per CCDI entity, holding
  everything about it: you construct it with the ScPCA records behind it, and it
  knows its own CCDI identifier, how to find its peers in a set of records, and
  how to emit itself. The getters that populate its metadata sit below it in the
  same module, which is where mapping decisions get made; an entity's crosswalk
  tables live beside them.
- **`entity.py`** — what all three have in common: an identifier, a way to find
  its peers in a set of records, and `emit`. Each entity declares its own
  generated types and field map as class attributes, so the wiring is readable
  where the entity is defined.

Plus `field_map.py`, the machinery that runs the getters, and — in the package
root — `reported()`, the one rule every getter shares, and `PUBLISHED_PAIRS`,
the one filter that decides which ScPCA records the node serves at all.

## Map a field

Write a function named after the CCDI field, in that entity's module, and
register it. It takes the ScPCA records behind the entity and returns a plain CCDI
value — or `None`, which the spec renders as a null under a present key.

```python
# sample.py, below the Sample class
DISEASE_PHASES = {
    "Initial diagnosis": "Initial Diagnosis",
    "Relapse": "Relapse",
    "Autopsy": "Post-Mortem",
}


@Sample.FIELDS.harmonized
def get_disease_phase(scpca):
    timing = reported(scpca.sample.metadata.get("disease_timing"))

    if timing is None:
        return "Not Reported"

    return DISEASE_PHASES.get(timing, "Unknown")
```

*(Illustrative.)* That is the whole change — no serializer, no view, no wrapper
class. The function name is `get_` plus the CCDI key, so the field is derived
from the name rather than kept in a table that could drift from it, and
registering a field the spec doesn't have raises at import with the list of
fields it does have.

**Write `@…harmonized` without parentheses.** It is a plain decorator, and the
prefix is not optional — both mistakes raise at import, one naming the missing
argument and the other naming the rename you want:

```
A CCDI sample mapping is named for the field it populates, behind 'get_' —
rename 'disease_phase' to 'get_disease_phase'.
```

**A getter takes one argument** — the entity, as `scpca`. That is checked at
registration, because a getter that can't be run the way `build` runs it does not
fail loudly: `build` contains it, so the field would degrade to null for every
record while `/metadata/fields` kept advertising it as one the node populates.
A `classmethod` is the usual way to get this wrong; a plain function or a
`staticmethod` is fine.

**Why the prefix.** A CCDI field name is not always a name Python can spare:
`File.type` shadows the builtin and is a soft keyword on 3.12. The prefix also
keeps the getters in a module greppable as a set, separate from the crosswalk
tables beside them.

**What you get handed.** The entity itself, as `scpca` — not the records inside
it. A CCDI Sample is a ScPCA *Library* seen through one of its *Samples*, so a
sample getter reads `scpca.library.metadata` or `scpca.sample.metadata`, which
keeps it clear which "sample" is meant. A CCDI Subject is a *group* of ScPCA
samples, so a subject getter reads `scpca.samples` and aggregates over them —
there is no single sample to read. Both can use `scpca.name` for the entity's own
identifier.

**What you return.** A plain value the CCDI field accepts: a string from its CDE
enum, a number, a list. The wrapper the spec emits it inside is derived from the
generated type, so no mapping names a `FieldUnowned*` class or can drift from the
spec when it changes.

**Always read through `reported()`.** ScPCA keeps metadata in two places — each
model's `metadata` JSON and its columns — and neither is normalised on the way
in, so `NA` reaches you verbatim from both. `reported()` turns the submitter's
"no value" markers into `None`; forgetting it is how `"NA"` ends up in a
federated response.

**A getter may raise.** ScPCA columns are free text, so `float(...)` on an age can
blow up. That is contained per field: the field goes null, the failure is logged
with its name, and the rest of the record is unaffected. You do not need to guard
every getter, but returning `None` for what you can't map is clearer than raising.

## Choosing what a field emits when there's no value

Return the placeholder you mean, on the line where you decide it. Two situations
worth keeping distinct:

- **The submitter reported nothing** — `"Not Reported"` where the CDE offers it.
- **They reported something we can't map** — `"Unknown"`, which is the sensible
  fallback of a crosswalk lookup.

Which of those exist differs per field, so check the enum in `../swagger.yml`
before assuming either. `null` is always valid, and is what an unmapped field
emits on its own.

- The literal `Unknown` is valid on only eight keys: `disease_phase`,
  `preservation_method`, `tissue_type`, `tumor_classification`, `tumor_grade`,
  `race`, `ethnicity`, `vital_status`.
- `Not Reported` is valid on seven: `disease_phase`, `tissue_type`,
  `tumor_classification`, `library_source_material`, `preservation_method`,
  `tumor_grade`, `race`. A field offering neither takes `null`.
- `sex` spells unknown `U`.
- `age_at_diagnosis`, `age_at_collection` and `age_at_vital_status` are numbers
  (days; multiply years by 365.25), so they have no unknown member — use `null`.

## Finding out what a field accepts

Everything about the CCDI side — permissible values, whether the key holds a
list, the standard it follows — is one call away, rather than a trip into a
19,000-line spec and a 16,000-line generated module:

```python
from typing import get_args
from scpca_portal.federation.ccdi.mapping.field_map import field_shapes, standard_of
from scpca_portal.federation.ccdi.schema import SampleMetadata

wrapper, many = field_shapes(SampleMetadata)["disease_phase"]
get_args(wrapper.model_fields["value"].annotation)   # the permissible values
many                                                 # True if it holds a list
wrapper.model_fields["value"].description            # the caDSR id and URL
standard_of(wrapper)                                 # that, already parsed
```

Not every field has a caDSR CDE — `age_at_diagnosis` has none — and 17 of the 28
harmonized fields do. Nothing to do either way: the standard is read off the
field, not declared by the mapping.

**Some fields hold lists**, and nothing in a getter's signature says which:
`identifiers`, `race`, `associated_diagnoses` and `associated_diagnosis_categories`
all do. Return a list for those. A bare string is caught and logged rather than
emitted one character at a time, but it still nulls the field.

## Finding out what a column actually contains

The fixtures under `api/test_data/` show the *shape* of a record, not the *domain*
of a column: they are sparsely filled, so a column that is `NA` there may well
carry real values in production. Building a crosswalk from them will silently null
whatever they happen to omit. Get the real value set from the data team, and treat
anything you infer from fixtures as a guess worth confirming.

## Describe a field on `/metadata/fields`

Registering a mapping describes it, and that is the whole of it — there is no
second decorator and no argument to pass. The endpoint reports exactly the fields
with a getter; the path and wiki link come from the function name; and the caDSR
standard is read off the generated type, because the spec already writes each
field's CDE and its URL into that field's description.

So a standard cannot be typed wrongly at a call site, cannot disagree with the
spec, and does not have to be looked up when you map a field. It also isn't
something you can opt into: `age_at_diagnosis` has no CDE and gets no standard,
`disease_phase` has one and gets it, and neither is a decision the mapping makes.

The cost is that it is parsed out of prose, so two tests in `test_field_map.py`
hold it: every field the spec *marks* as standardized must parse, and every field
it doesn't mark must yield nothing. A CCDI reformat fails them by name rather
than quietly emptying the endpoint. If you are changing `STANDARD_MARKERS` or the
patterns, those two are the ones to watch.

One field, one mapping. Registering a second getter for a field already mapped
raises and names the one that has it, rather than half-replacing it.

## Change how a Subject is identified

A CCDI Subject is usually a participant, and ScPCA has no donor entity, so one
is derived in `Subject.name` — today from the submitter's `submitter_id`, with a
fallback to per-sample identity under `DERIVED_PREFIX` when that column carries
nothing. The prefix is what keeps the two minting paths from colliding: a
submitter writing a ScPCA sample id into `submitter_id` would otherwise produce
the same name as another sample's fallback, merging two participants into one.

That function is the whole seam. When the CCDI Participant Index arrives, it
replaces the body:

```python
@property
def name(self):
    return participant_index.lookup(self.samples[0])
```

Two samples that resolve to the same name are one Subject, so this is also where
the `subject` counts in `by/{field}/count` are decided.

## Choose which ScPCA records the node publishes

`PUBLISHED_PAIRS` in the package root is the whole switch — one filter over the
Library↔Sample relation, where a row is one CCDI Sample. It holds back spatial
and multiplexed data today; dropping a clause publishes it, and nothing else in
the layer changes.

Project locks are not part of this. `is_locked` marks a project whose underlying
files are being replaced or added for the first time, which blocks user dataset
generation, not the pre-generated CCDL datasets the node points consumers at.

Two things to check when you widen it:

- **Spatial cannot be joined to a CCDL dataset by format.** `ccdl_datasets.TYPES`
  records each dataset's *download* format, which for spatial is not the format
  its libraries carry, so a format-to-dataset join silently matches nothing.
  Whatever publishes spatial has to answer that first.
- **Multiplexed is excluded at the *sample* level**, not just the library level,
  so a multiplexed sample cannot reach the node through its other libraries.

`test_sample.SampleExclusionTests` is written so that flipping a clause turns the
matching test red, rather than leaving the exclusion silently untested.

## Tests

Tests live in `scpca_portal/test/federation/ccdi/mapping/`, in two tiers.

**Unit tests** — `SimpleTestCase` over unsaved model instances, with values
written inline. These answer "given this source value, what CCDI value comes
out": crosswalk coverage, the value that *doesn't* convert, placeholder choices,
failure containment. Write one per mapped field. Values go inline rather than
coming from fixtures, which are sparse enough that a fixture-driven test mostly
exercises the "submitter reported nothing" path.

**Record tests** — `test_records.py`, `TestCase` over factory-built, saved
records. These exist because a unit test can't catch a getter reading the wrong
attribute: the test author writes both sides, so `scpca.library.metadata["seq_unit"]`
passes whether or not the loader puts it there. Add a case here when a mapping
starts reading a new column or traverses a relation.

Anything about *which* records reach a response — the publish filter, paging —
is an endpoint concern and belongs in
`test/federation/ccdi/views/test_sample.py` instead, where it can go through a
real request.

`sportal api:test:ccdi` runs the node's tests; `sportal api:test` runs the whole
suite, which is what CI does.

`test_field_map.py` registers throwaway getters of every shape — scalar, list,
crosswalked, multi-column, failing — and is the quickest way to see a working one.

Registration checks itself — a getter named after a field the spec doesn't have
raises at import — so there is no coverage test to keep in sync.
