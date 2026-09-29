# The CCDI federation node

A read-only discovery API that republishes ScPCA data in the shapes the
[CCDI Federation API](https://cbiit.github.io/ccdi-federation-api/) defines, so a
federated aggregator can find ScPCA records and link users back here to download
them. It adds no models and changes nothing about v1 auth or downloads.

- **Mounted at** `/federation/ccdi/`, conditionally — `urls.py` decides whether
  the routes are added at all.
- **The contract** is a vendored, pinned copy of v1.3.0: `swagger.yml`. We
  conform to it; we don't generate it.
- **Populating fields** is a separate job with its own guide:
  [`mapping/README.md`](mapping/README.md).

## What's here

- `urls.py` — the node's own routing table, mirroring the spec's paths.
- `views/` — one module per endpoint group. `views/base.py` holds the shared
  entity viewset plus the paging every index response uses.
- `schema/` — Pydantic response types generated from `swagger.yml`
  (`_models.py`, committed), the clean aliases views use, and `dump`, which
  renders any of them into a response body (`__init__.py`).
- `config.py` — static content for the endpoints that read no data at all.
- `mapping/` — everything that turns ScPCA records into CCDI ones.

## Endpoints

The API lives under `/federation/ccdi/v1/`, mirroring the spec's paths:

- `v1/info`, `v1/namespace[/{org}/{ns}]`, `v1/organization[/{name}]` — served from
  `config.py`, no data reads.
- `v1/metadata/fields/{subject,sample,file}` — the described metadata fields,
  built from the field map.
- `v1/sample` and `v1/sample/{org}/{ns}/{name}` — the Sample index and show
  endpoints, paged. These are the only data-backed entity endpoints so far.
- `v1/subject`, `v1/file`, and every `by/{field}/count`, `summary` and
  `-diagnosis` — routed, answering `501`. Each entity's test module asserts that
  stub state over a `PENDING_ENDPOINTS` list, so the day one stops answering
  `501` the test fails and names the URL. (It asserts the stub rather than the
  finished endpoint on purpose: a detail route answers `404` for a name that does
  not exist both before and after it is built, so a test asserting `200` there
  would stay green forever.)
- `/federation/ccdi/docs/{schema,swagger,redoc}` — the vendored spec and its UIs.

## Looking at a mapped entity directly

The quickest way to see what a mapping produces:

```bash
sportal api:manage shell -c "
from scpca_portal.federation.ccdi import schema
from scpca_portal.federation.ccdi.mapping.sample import Sample
from scpca_portal.models import Library, Sample as ScPCASample

library = Library(scpca_id='SCPCL000001', metadata={'seq_unit': 'cell'})
scpca_sample = ScPCASample(scpca_id='SCPCS000001', metadata={'disease_timing': 'Initial diagnosis'})
print(schema.dump(Sample(library, scpca_sample).emit()))
"
```

Or against the running node, which also exercises the publish filter:

```bash
curl -s localhost:8000/federation/ccdi/v1/sample?per_page=1 | jq
```

Run the node's tests with:

```bash
sportal api:test:ccdi
```

`sportal api:test` runs the whole suite, which is what CI does.

---

# "A sample isn't in the response"

Before suspecting a mapping, check whether the node publishes that record at all.
`mapping.PUBLISHED_PAIRS` is the single filter both `/sample` endpoints go
through, and it currently holds back **spatial** and **multiplexed** data. A
record it excludes is absent from the index and answers `404` on show — it isn't
reachable by guessing its name, which is deliberate.

```python
from scpca_portal.federation.ccdi.mapping import PUBLISHED_PAIRS
from scpca_portal.models import Sample

Sample.libraries.through.objects.filter(
    PUBLISHED_PAIRS, sample__scpca_id="SCPCS000001"
)  # empty means the node is holding it back, not that it's missing
```

`mapping/README.md` has what to do when you want to widen that.

# "We added a field but it isn't showing up"

Work down this list; each step tells you which layer is responsible.

### 1. Is the field part of the CCDI spec at all?

CCDI only has the harmonized keys listed on `models.sample.Metadata` /
`models.subject.Metadata` / `models.file.Metadata` in `swagger.yml`. A ScPCA
column with no CCDI equivalent is not a missing mapping — it's an *unharmonized*
key, passed through under the response's `unharmonized` object.

If you register a getter named after a field the spec doesn't have, it raises at
import and lists the fields it does have, so a typo can't fail quietly.

### 2. Is there a getter for it?

Open the entity's module — `mapping/sample.py`, `subject.py` or `file.py`.
A CCDI field with no function named after it is deliberately unmapped and emits
`null`.

### 3. Is the getter reading the right record?

Getters are handed the entity, not the records inside it. A CCDI Sample is a
ScPCA *library* seen through a *sample*, so its getters must pick a half:
`scpca.library.metadata` or `scpca.sample.metadata`. A CCDI Subject is a *group*
of ScPCA samples, so its getters read `scpca.samples` and aggregate.

Also check which store: ScPCA keeps metadata both in each model's `metadata` JSON
and on its columns, and the same key can appear in both.

### 4. Does ScPCA actually have a value there?

`reported()` turns the submitter's "no value" markers into `None`, which becomes
a null in the response. A field that is mapped but null for one record usually
means exactly this. A getter that skips `reported()` has the opposite problem —
it will emit `"NA"` verbatim.

### 5. Did the getter decline the value?

A crosswalk lookup returns `None` for anything it doesn't cover unless the getter
supplies a fallback, so a value that is present but unmapped is silent.

### 6. Did the getter fail?

A getter that raises — `float()` on a free-text age, a value outside the field's
CDE enum — degrades that field to `null` and logs at ERROR with the field's name.
Check the log before assuming the mapping is missing:

```
ERROR CCDI sample field age_at_diagnosis could not be mapped
```

### Bisecting it

Call the getter directly; it takes the same records the builder hands it:

```python
from scpca_portal.federation.ccdi.mapping.sample import Sample as CCDISample
from scpca_portal.models import Library, Sample

scpca = CCDISample(
    Library(scpca_id="SCPCL000001", metadata={"seq_unit": "cell"}),
    Sample(scpca_id="SCPCS000001", metadata={"disease_timing": "Initial diagnosis"}),
)
field_map = CCDISample.FIELDS

print(field_map.getters.keys())                     # which fields are mapped at all
print(field_map.getters["disease_phase"](scpca))    # the raw CCDI value, unwrapped
print(field_map.build(scpca).disease_phase)         # what the response will carry
```

### A field missing from `/metadata/fields` is a different problem

Mapping a field describes it — `/metadata/fields` reports exactly the fields with
a registered getter, and the path and wiki link come from the function name. So a
field present in one and absent from the other means the two were built from
different code, not that a description is missing.

---

# "This field needs to convert differently"

One function changes. Nothing in `views/` or `field_map.py` knows
about individual fields.

1. **Edit the getter** in `mapping/<entity>.py`, or the crosswalk table
   beside it. Keep crosswalks as named module dicts so they stay inspectable.
2. **Re-check the placeholders.** `"Not Reported"` and `"Unknown"` are only legal
   on the fields whose CDE offers them — eight of the harmonized keys take
   `Unknown`, `sex` uses `U`, and the age fields are numbers. `mapping/README.md`
   has the full rule.
3. **Update its test**, including the value that *doesn't* convert — an untested
   crosswalk fallback is how a mapping quietly rots.
4. **Leave the standard alone** — it is read off the spec, not declared here.
5. **Verify** with `sportal api:test:ccdi` and the snippet above.

Remember that a conversion change is visible to every federated consumer, so a
change to a controlled-vocabulary mapping deserves a note in the team's CCDI
open-questions doc alongside the code change.

# Other things that go wrong

### A response fails validation

- `Input should be 'Post-Mortem', 'Not Reported', …` — a getter returned a value
  that isn't in the field's CDE enum. The permissible values are in `swagger.yml`;
  casing counts (`Initial diagnosis` is not `Initial Diagnosis`). This is caught
  per field and logged, so it shows up as a null plus an ERROR line rather than a
  failed response.
- `Input should be a valid dictionary or instance of FieldUnowned…` — a getter
  returned an already-wrapped value. Getters return plain values; the wrapper is
  applied for them.
- A missing-key error — every harmonized key is required (nullable, but present).
  The builder walks the generated type, so every key is always emitted; a missing
  one means the committed types are out of step with the spec.

### The node 404s

`urls.py` mounts the node's routes conditionally, and the condition is not
met. Note the URLconf is evaluated at import time, so a test can't flip the
routes with `override_settings` alone; it needs a URLconf reload.

### The drift test fails

The committed response types are stale relative to `swagger.yml`:

```bash
sportal api:manage generate_ccdi_types
```

The test compares parsed ASTs rather than bytes, because the formatter's config
isn't reachable inside the Docker image; `schema/generate.py` pins the formatting
so regenerating doesn't churn the diff.

### CCDI published a new spec version

Vendor the new `swagger.yml`, regenerate the types, then run the node's tests.
Wrappers and list-ness are derived, so added or reshaped fields need no mapping
change; a getter whose field the spec *dropped* raises at import and names it.
