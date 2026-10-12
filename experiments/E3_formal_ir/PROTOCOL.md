# E3: protocol (frozen before the validator is implemented and before any scored evaluation)

Frozen 2026-10-12 on branch `experiment/e3-governance-ir-2026-10-12`. It was created from
`origin/experiment/e1-expressibility-erratum-2026-10-12` @ `d8ad864`, after the erratum's CONFIRMED_E1_ERRATUM
was checked (PRIOR.md).

The freeze commit contains:
- this file and `PRIOR.md`;
- `cases/` (source, roster, fact registry, records, approvals, `SCENARIOS.json` with expected outcomes,
  `RECEIPT_PLAN.json`, `ORACLE_EXPECTED.json`, `UNTYPED_BASELINE.json`);
- `src/build_fixtures.py`.

Their sha256 values and the freeze commit SHA are recorded in `FREEZE_MANIFEST.txt`, committed next.

**No validator, model, runner or native E3 query exists at freeze time.** The only things run before the freeze:
- the pinned rebuild via E0's `run_e0.py --regen` (fingerprints equal to E0);
- `build_fixtures.py`, which wrote the fixtures and computed the independent raw-CSV oracles with the erratum's
  and E2's oracle code, unmodified.

Deviations go under "Amendments" and never change a frozen expectation.

## 1. Hypothesis (R4)

A single versioned typed JSON record, plus a small read-only validator, mechanically enforces the invariants of
§3 on S1–S4. Specifically:
- every invalid promotion in `SCENARIOS.json` gets the expected non-verified status, with the expected
  machine-readable reason;
- a bounded `VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS` is reached only in the three preregistered
  positive scenarios, backed by fresh native MetricFlow receipts that equal independent raw-CSV oracles;
- at least three states that a plain JSON store accepts as "verified" or "approved" are rejected.

Several of these are guarantees E1 did not have.

## 2. IR shape (`E3-IR-0.1`; implemented after the freeze as Pydantic v2 models with `extra="forbid"`; JSON Schema exported)

**Record** (one per clause version):

| Field | Content |
|---|---|
| `ir_version` | exactly `"E3-IR-0.1"` |
| `record_id` | — |
| `proposed_by_role` | the role that proposed the record; never an approver |
| `governing_source` | `source_id`, `path`, `content_sha256`, `clause_id`, `clause_version` (int ≥ 1), `observed_at` (UTC datetime), `effective_from` (date), `effective_to` (date or null), `provenance` ∈ {`LAB_AUTHORED`} |
| `requirement` | `text` (the exact clause text), `atoms`, `population`, `exceptions` (empty list; only operators used here) |
| `interpretation` | `claimed_state` ∈ {`PROPOSED`, `UNRESOLVED_INTERPRETATION`, `LAB_APPROVED`}, `claimed_approval_ids` (list), `readings` (≥ 1), `open_questions` |
| `lab_assumptions` | list of text |
| `verification_request` | `semantic_manifest_sha256`, `raw_csv_sha256` {file: sha256} |

There is **no input field for status.** The keys `status`, `verified` and `verification_status` are rejected
(STATUS_FIELD_FORBIDDEN).

**Atom fields:**
- `atom_id`;
- `span` [start, end] into `requirement.text`;
- `text`, which must equal `text[start:end]`;
- `kind` ∈ {`MEASURE`, `PREDICATE`, `GROUP_BY`};
- `fact_kind`, which may be null only when the readings supply it in `atom_fact_kinds`;
- `op` ∈ {`EQ`, `GE`, `IS_TRUE`} for predicates;
- `value`;
- `unit` ∈ {`CURRENCY`, `CURRENCY_PER_UNIT`, `UNIT`, `COUNT`, null};
- `aggregation` ∈ {`SUM`, `COUNT_DISTINCT`};
- `period` ∈ {`CALENDAR_YEAR`};
- `grain` ∈ {`ORDER_LINE`}.

**Reading fields:**
- `reading_id`, `statement`;
- `atom_fact_kinds` (optional map);
- `bindings`, a map from atom_id to Binding;
- `native_query`: {`metric`, `group_by` [..], `where` [..]} or null;
- `native_receipt_id`, `oracle_id`.

**Binding fields:**
- `kind` ∈ {`DIRECT`, `DERIVED`, `CANDIDATE_EQUIVALENCE`, `MISSING`};
- `semantic_object` {`type` ∈ {metric, dimension, time_dimension}, `name`} or null;
- `physical_lineage` [fields; first = the gold field];
- `value_override`;
- `derivation`: {`pattern`, `numerator_metric`, `denominator_metric`, `line_entity`, `threshold`,
  `guards_declared`, `guard_receipt_id`};
- `equivalence`: {`field`, `fact_kind`, `statement`, `claimed_approval_id`};
- `missing_fact`.

**Approval** (a separate file; never embedded in a record):
- `approval_id`;
- `provenance` = `LAB_SIMULATED`;
- `approver_role`;
- `claim`: {`kind` ∈ {`INTERPRETATION_CHOICE`, `SEMANTIC_EQUIVALENCE`}, `record_id`, `reading_id` | (`fact_kind`,
  `field`, `statement`)};
- `scope` {`source_id`, `source_sha256`, `clause_id`, `clause_version`};
- `known_at`, `effective_from`, `effective_to`.

**Revocation:** `revocation_id`, `provenance`, `revokes`, `approver_role`, `known_at`.

**Lab context:**
- `roster.json`: LAB_SIMULATED roles, each with the claim kinds it may approve and the source ids or field
  prefixes it covers; `never_approvers`.
- `fact_registry.json` extends E1's authority registry with:
  - `field_origins`;
  - fact kinds with `required_origin` and `designated_fields`;
  - `metric_units`, lab-declared because the upstream declares none (ASSUMED);
  - one derivation pattern, `LINE_GRAIN_RATIO_THRESHOLD`, with its where-template and required guards.

## 3. Invariants and reason codes (the validator's contract)

The validator is **read-only and pure**. Its inputs:
- the record;
- the visible approvals and revocations;
- the roster and registry;
- the semantic catalog extract;
- the native, guard and oracle receipts;
- `eval_known_at` and `eval_effective_at`.

It returns:
- `structural_errors` [{code, path, detail}];
- `meaning` (interpretation state, selected reading, alternatives' dispositions, equivalences);
- `computability` (per reading: native receipt exit / executable);
- `evidence` (guards, native = oracle per reading);
- `uncovered` atoms;
- `reasons` (sorted, unique codes);
- the computed `status`.

**I1. Status is computed, never input.**
- STATUS_FIELD_FORBIDDEN; SCHEMA_INVALID.
- A record that claims `LAB_APPROVED`, or claims an equivalence approval id, gets
  APPROVAL_CLAIM_WITHOUT_EVIDENCE unless every claimed id is a visible, valid approval of exactly that claim.
- In particular, a claimed state of `LAB_APPROVED` with no ids is invalid.

**I2. Source identity and time** (structural):
- SOURCE_HASH_MISMATCH: sha256 of the file at `path` ≠ `content_sha256`.
- SOURCE_CLAUSE_MISMATCH: the line `[clause_id vVERSION] text` is not in the source.
- SPAN_TEXT_MISMATCH.
- TEMPORAL_ORDER_INVALID: `effective_to < effective_from`.
- SOURCE_NOT_YET_KNOWN: `observed_at > eval_known_at`.

**I3. Binding consistency** (structural):
- UNDEFINED_PREDICATE: a binding for an absent atom.
- ATOM_UNBOUND.
- UNKNOWN_SEMANTIC_OBJECT: not in the native catalog extract.
- UNKNOWN_PHYSICAL_FIELD: not among the warehouse columns.
- SEMANTIC_PHYSICAL_MISMATCH: the semantic object does not resolve to `physical_lineage[0]`.
- UNIT_MISMATCH: measure unit ≠ metric unit; or derived threshold unit ≠ numerator unit / denominator unit.
- QUERY_BINDING_MISMATCH: `native_query` ≠ the conjunction rendered from the bindings.
- For DERIVED bindings:
  - DERIVATION_QUERY_MISMATCH: the rendered template is not in `where`;
  - DERIVATION_GRAIN_INVALID: `line_entity` ≠ the primary entity of the model defining both measures;
  - REQUIRED_GUARD_UNDECLARED.

**I4. Approval validity** (an invalid approval is ignored for promotion and reported):

| Code | Condition |
|---|---|
| APPROVER_NOT_IN_ROSTER | — |
| SELF_APPROVAL | role ∈ `never_approvers` or = `proposed_by_role` |
| APPROVER_NOT_AUTHORIZED_FOR_CLAIM | claim kind, source or field prefix not covered by the role |
| APPROVAL_SCOPE_MISMATCH | source id / hash / clause / version / record / reading do not exactly match the record |
| APPROVAL_BEFORE_SOURCE_OBSERVED | — |
| APPROVAL_NOT_EFFECTIVE | `eval_effective_at` outside [effective_from, effective_to] |
| APPROVAL_REVOKED | a visible revocation by an authorized role |

**I5. As-of visibility.** Approvals and revocations with `known_at > eval_known_at` are removed **before** any
processing. They never appear in the output (`must_not_mention`).

**I6. Meaning.**
- Exactly one reading must be selected by valid INTERPRETATION_CHOICE approvals; otherwise:
  - INTERPRETATION_UNRESOLVED (several readings);
  - INTERPRETATION_NOT_APPROVED (a single reading);
  - CONFLICTING_APPROVALS (two readings selected).
- The non-selected readings are kept with disposition `NOT_SELECTED`, never "false".
- A CANDIDATE_EQUIVALENCE binding in the selected reading needs a valid SEMANTIC_EQUIVALENCE approval for its
  exact `fact_kind` and `field`; otherwise EQUIVALENCE_UNAPPROVED.

**I7. Provenance cannot be approved into existence.** An atom is *uncovered* when:
- its binding is MISSING;
- a DIRECT binding's field is not designated for the atom's fact kind (NOT_DESIGNATED_FOR_FACT); or
- a candidate field's origin ≠ the fact kind's required origin (SOURCE_ORIGIN_MISMATCH). Any approval of such
  an equivalence additionally gives APPROVAL_CANNOT_CREATE_SOURCE.

REQUIRED_FACT_ABSENT applies when no field in the registry has the required origin.

**I8. Behavioural evidence for the selected reading:**

| Code | Condition |
|---|---|
| NATIVE_RECEIPT_MISSING | — |
| RECEIPT_INTEGRITY_FAILED | sha256 of the recorded CSV text ≠ the recorded hash |
| NATIVE_QUERY_FAILED | exit ≠ 0 |
| RECEIPT_QUERY_MISMATCH | receipt query ≠ reading query |
| RECEIPT_REVISION_MISMATCH | receipt manifest or CSV hashes ≠ `verification_request` |
| ORACLE_MISSING | — |
| ORACLE_READING_MISMATCH | `computes` ≠ (record, reading) |
| ORACLE_REVISION_MISMATCH | — |
| NATIVE_ORACLE_MISMATCH | the per-period Decimal values, or the period sets, differ |
| GUARD_NOT_EVIDENCED | — |
| GUARD_FAILED | any required guard false |
| GUARD_SNAPSHOT_MISMATCH | the guard receipt's warehouse sha256 ≠ the native receipt's |

These are evaluated for every reading as well, as *computability/evidence information*, but only the selected
reading can promote.

**Status precedence** (computed):
1. `STRUCTURALLY_INVALID`
2. `MISSING_REQUIRED_FACT`: any uncovered atom in the selected reading, or in every reading when none is
   selected.
3. `MEANING_UNRESOLVED`
4. `NOT_VERIFIED`
5. `VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS`

"Verified" means only:
- the recorded native query on the recorded semantic revision and snapshot equalled the independent oracle for
  the lab-approved meaning, under its declared lab assumptions and guards;
- not legal or business correctness, and not that `country` really means residence.

## 4. Behavioural evidence (after the freeze)

`src/collect_evidence.py` executes every query in `RECEIPT_PLAN.json` with genuine `mf` through E1's
`native_query_with_where` over the unmodified E0 adapter. It runs on:
- the pinned warehouse;
- two disposable copies under ignored `runs/`, described in `RECEIPT_PLAN.snapshots`.

Native receipts record:
- query, argv and exit code;
- the CSV text and its sha256, and parsed rows;
- `mf` identity;
- semantic manifest sha256, raw CSV sha256 values and warehouse sha256.

Guard receipts reuse the erratum's `guards()` and `warehouse_lines()` unmodified. Oracle receipts are recomputed
from the raw CSVs and must equal `ORACLE_EXPECTED.json`. A semantic catalog extract is written from the
semantic manifest and the warehouse column list: metrics, measures, dimensions → gold field, entities, metric
→ model.

Trust limit: the validator and the replay read *recorded* receipts. Their integrity is protected by hashes
against the committed files, not against a forger with write access. Freshness is established by this run.

## 5. Scenarios and frozen expectations (`cases/SCENARIOS.json`, 54 scenarios)

Each scenario names:
- a base record, plus `record_patch` (set/delete at a JSON path; a harness edit, not an IR feature);
- the approvals and revocations supplied;
- `eval_known_at` / `eval_effective_at`;
- optional `receipt_tamper`.

Each expectation gives the exact `status` and a list of codes that must appear in `reasons`. Optional
expectations:
- `selected_reading`, `alternatives`;
- `uncovered`;
- `technically_executable`;
- `readings_native_equals_oracle`;
- `must_not_mention`.

| Test | Scenarios | What it pins |
|---|---|---|
| 1 | S1 positive; S1 without interpretation approval | — |
| 2 | 6 S1 guard/derivation corruptions | including a negative-quantity disposable snapshot |
| 3 | S2 without approval | both readings executable and oracle-equal, still unresolved |
| 4 | S2 valid customer-country approval | VERIFIED; store reading NOT_SELECTED |
| 5 | 12 approval attacks | wrong clause / version / hash / reading; conflict; unknown, unauthorised or self approver; before source; not effective; future approval claimed or unclaimed |
| 6 | S3 without equivalence approval | — |
| 7 | equivalence approved | before / after revocation; removed; flag flipped without approval; wrong steward |
| 8 | S4 | missing settlement; status proxy executed and oracle-equal; proxy with a simulated equivalence approval; a status field set to VERIFIED |
| 9 | 13 structural negatives | — |
| 10 | 6 native/oracle controls | tampered receipt re-hashed or not; underlying warehouse value changed; receipt for another query; oracle for another reading; wrong semantic revision |
| 11 | as-of before vs after approval | the future approval invisible; the record unchanged |
| 12 | fresh-process replay of all 54 | from committed files only, outputs byte-identical |

## 6. Comparison with untyped recording and with E1 (frozen classification)

`cases/UNTYPED_BASELINE.json` lists seven states (U1–U7) that a plain JSON note store, read naively, would hold
as verified or approved. The run checks that the naive reader promotes each one and that the E3 validator
rejects each one.

| Invariant | Already enforced earlier? |
|---|---|
| I7 status proxy, as a direct binding (U4) | **Yes**: E1 authority registry, NOT_AUTHORITATIVE_FOR_FACT (variant 6). E3 reuses the idea. New in E3: an *approved* equivalence still cannot create the missing source. |
| I8 wrong revision / fingerprint (U3) | **Partly**: E1 estate fingerprint gives INCONCLUSIVE (D10). |
| Derived guards (U6) | **Partly**: the erratum's capability check covers this one pattern. New in E3: guards attached to a binding and tied to the receipt snapshot. |
| I1 computed status (U7, U2) | **No.** E1 computed its statuses internally but had no claimed-approval or approval objects. |
| I4/I5/I6 approval scope, roster, self-approval, effective window, as-of visibility, conflicting choices, alternatives kept (U1, U5) | **No.** E1 had no approval objects and no interpretation alternatives. |

## 7. Gates (applied mechanically by `src/gate.py`; one verdict)

| Criterion | Condition |
|---|---|
| C0 | Pinned identity equals E0: upstream commit, env freeze, semantic manifest, CSV hashes. Every oracle receipt equals `ORACLE_EXPECTED.json`. The native runtime ran: NR_S1, NR_S2_*, NR_S3 and NR_S4_PROXY exit 0, and the probe is rejected. |
| C1 | Every scenario's computed status equals its expected status, and every expected reason, reading, alternative, uncovered set, executability, oracle-equality and no-mention expectation holds. |
| C2 | Zero false VERIFIED: no scenario whose expected status is not VERIFIED computes VERIFIED. |
| C3 | The three positive scenarios (S1_T1_POSITIVE, S2_T4_APPROVED_CUSTOMER, S3_T7_EQUIVALENCE_APPROVED) rest on fresh native receipts on the pinned snapshot that equal the independent oracle. |
| C4 | At least three U-cases are promoted by the naive reader and rejected by E3, of which at least three involve invariants the §6 table marks "No" or "Partly". |
| C5 | Fresh-process replay of all scenarios (`env -i`, `python -I`, temporary cwd, committed files only) is byte-identical to the scored output. |
| C6 | `pytest` for models/validator unit tests passes. |

**Verdict mapping:**

| Verdict | Condition |
|---|---|
| BLOCKED | the native runtime is unavailable (C0 runtime part) after one narrow repair |
| INCONCLUSIVE | C0 identity/oracle fails, or fixture integrity is broken (a FREEZE_MANIFEST hash mismatch at run time) |
| FAIL_UNSAFE_IR | C2 fails |
| FAIL_NO_INCREMENTAL_VALUE | C4 fails |
| PASS_IR_GUARD_VALUE | C1–C6 all hold |
| PARTIAL_IR_GUARD_VALUE | otherwise, with C2 holding; the failing scenarios name the smallest missing property |

## 8. Non-claims

- Four LAB_AUTHORED clauses, one synthetic estate, one author.
- Simulated roles and approvals carry no real authority.
- A simulated equivalence does not show `customers.country` means residence.
- No proprietary language, parser, compiler, policy engine, event store or E4–E8 work.
- This does not show that existing schema or validation tooling could not enforce the same invariants. Pydantic
  and JSON Schema are themselves that tooling.

## Amendments

(none)
