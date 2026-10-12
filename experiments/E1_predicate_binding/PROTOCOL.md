# E1 — protocol (frozen before the evaluator and before any scored execution)

Frozen 2026-10-12 on branch `experiment/e1-known-binding-2026-10-12`, created from
`origin/experiment/e0-native-metricflow-2026-10-12` @ `a84c855`. Frozen together in the protocol commit:
`PRIOR.md`, `SOURCE_INVENTORY.md`, this file, `FROZEN_CASES.json`, `EXPECTED.json`, `src/oracle.py`,
`src/inventory.py`, `evidence/inventory_snapshot.json`. Their sha256 values and the protocol commit SHA are
recorded in `FREEZE_MANIFEST.txt`, committed **after** the protocol commit (a file cannot name its own commit).
Corrections, if any, are appended under "Amendments" with a date; original text stays.

Governing documents: SOPHON_CHARTER.md v1.1, CLAUDE.md, AGENTS.md, SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md
§5 E1, Claude_Code_Sophon_E1_Known_Predicate_Binding_2026-10-12.md.

## 1. Hypothesis (one)

H: With the LAB-REV-1 interpretation and bindings supplied, a small read-only evaluator reusing the E0 native
adapter classifies case A as FULLY_OBSERVABLE_FOR_THIS_CALCULATION (native `completed_revenue` equals the
independent raw-CSV oracle), case B1 as PRESENT_IN_SOURCE_NOT_EXPOSED and case B2 as NOT_FOUND_IN_BOUNDED_ESTATE,
and none of the adversarial mutations reaches full observability.

Primary uncertainty: R2/R3 mechanics under a human-supplied mapping. Not autonomous discovery, not interpretation.

## 2. Fixed inputs

- Upstream, environment, data and native path exactly as E0 (SOURCE_INVENTORY.md; E0 SOURCE_GATE.md), rebuilt
  under `experiments/E1_predicate_binding/.upstream` (ignored). The upstream and E0 files are not modified.
- E0 adapter `experiments/E0_native_adapter/src/mf_adapter.py` imported unmodified.
- `FROZEN_CASES.json`: policy family LAB-REV-1 (clauses A, B1, B2), predicates, supplied bindings, lab authority
  registry, bounded-estate fingerprint, three scored cases and the adversarial variants.
- `EXPECTED.json`: expected outcomes, written from the inventory before the evaluator existed. The evaluator
  never reads it.
- `src/oracle.py`: independent oracle (stdlib, raw CSVs only; delegates case A's predicate set to E0's
  crosscheck and must agree with its own loop).

## 3. Evaluator decision procedure (fixed now)

The evaluator receives a case (required predicate ids → binding or null) and a context giving: live warehouse
columns (`information_schema`, read-only), distinct values of a column (read-only), the live semantic manifest,
the native dimension list for the target metric (`mf list dimensions --metrics`, via the E0 adapter), native
queries (via the E0 adapter), the live estate fingerprint (as `src/inventory.py` computes it) and the oracle.

### 3.1 Predicate status, in this order

1. **No binding supplied.** If any field designated for the predicate's fact kind exists in the live warehouse →
   `MISSING_BINDING`. Otherwise → `NOT_FOUND_IN_BOUNDED_ESTATE`.
2. **Physical field** (`schema.table.column`) absent from the live warehouse → `INVALID_BINDING`.
3. Physical field present but **not designated** for the predicate's fact kind in the frozen authority registry
   → `NOT_AUTHORITATIVE_FOR_FACT` (an untrusted proxy; no equivalence rule exists in E1).
4. **Semantic object** of the binding:
   - `measure`: must exist in the named semantic model of the live semantic manifest; its `expr` (or name) must
     equal the physical column and the model's relation (`schema.alias`) must equal the physical table, else
     `INVALID_BINDING`.
   - `dimension` / `time_dimension` `<entity>__<name>`: if it is **not** in the live native dimension list for the
     target metric, scan every semantic model on the physical table for a dimension or measure whose `expr` (or
     name) equals the physical column: if one exists → `MISSING_BINDING` (exposed under another name); if none →
     `PRESENT_IN_SOURCE_NOT_EXPOSED`, and run a **native exposure probe** (`mf query --metrics <metric> --where
     "{{ Dimension('<binding>') }} <op> <value>"`) whose rejection or acceptance is recorded. If it **is** in the
     native list, it must resolve in the manifest to the semantic model whose primary entity is `<entity>`, with
     `expr` (or name) equal to the physical column on the same table, else `INVALID_BINDING`. A
     `time_dimension` must also have type `time` and be that model's `agg_time_dimension`, else `INVALID_BINDING`.
5. `categorical_equals`: the required value must occur among the live distinct values of the physical column,
   else `VALUE_NOT_OBSERVED`.
6. Otherwise → `BOUND_AND_EXPOSED`.

### 3.2 Case status, first matching rule wins

1. **Metric consistency** against the live semantic manifest, else `INVALID_BINDING`: the target metric exists;
   its input measure is the measure of a `BOUND_AND_EXPOSED` `measure_sum` predicate; every metric filter equals
   `{{ Dimension('<dim>') }} = '<value>'` for a `BOUND_AND_EXPOSED` `categorical_equals` predicate bound to
   `<dim>` with that value; the measure's semantic model `agg_time_dimension` is the bound time dimension of a
   `BOUND_AND_EXPOSED` `time_grain` predicate.
2. Any predicate `INVALID_BINDING` → `INVALID_BINDING`.
3. Live estate fingerprint ≠ frozen fingerprint → `INCONCLUSIVE` (the inventory no longer describes the estate).
4. Any `NOT_FOUND_IN_BOUNDED_ESTATE` → `NOT_FOUND_IN_BOUNDED_ESTATE`.
5. Any `PRESENT_IN_SOURCE_NOT_EXPOSED` → `PRESENT_IN_SOURCE_NOT_EXPOSED`.
6. Any other predicate not `BOUND_AND_EXPOSED` → `UNVERIFIED`.
7. Native query: metric, `--group-by metric_time__<grain>`, plus a `--where` for every categorical or threshold
   predicate not implemented by the metric's own filter. Native failure → `UNVERIFIED`. Oracle not computable →
   `UNVERIFIED`. Native ≠ oracle (exact per year, to the cent) → `UNVERIFIED` with counterexamples.
   Equal → `FULLY_OBSERVABLE_FOR_THIS_CALCULATION`.

`verified_for_recorded_checks` is true **only** for `FULLY_OBSERVABLE_FOR_THIS_CALCULATION`. Whenever rule 1
passes but the case is not fully observable, the native query for the **covered subset** (bound-and-exposed
predicates only) is also run and recorded as a diagnostic, labelled as not covering the uncovered predicates.
No status string from `EXPECTED.json` or the case id is ever read by the evaluator.

## 4. Scored run and tests

S1 Rebuild check: live semantic manifest sha256 and estate fingerprint recorded; the run continues regardless,
   and rule 3.2.3 handles any mismatch.
S2 Evaluate A, B1, B2 (scored) and write `evidence/run/case_results.json` with every context response, native
   receipt and oracle output.
S3 Adversarial and non-vacuity checks (E1 prompt §6), as automated tests in `tests/test_e1_binding.py`, results
   kept in `evidence/run/adversarial_results.json` and the pytest log:
   1. A positive (native = oracle; all predicates resolved).
   2. B1 field exposure (physical presence shown; native probe rejected; distinct status).
   3. B2 missing source (bounded inventory; NOT_FOUND, never universal absence).
   4. Binding mutations M4a–M4d.
   5. Predicate addition M5 (native number for the covered subset unchanged; full observability withdrawn).
   6. Proxy attack M6.
   7. Native identity drift M7 on a disposable copy of the dbt project with the metric filter changed in
      `target/semantic_manifest.json`; the drifted native query is also run to show it returns a different number.
   8. Oracle sanity M8a (native value +0.01 rejected) and M8b (oracle on a raw copy with one completed line's
      quantity +1 differs from native by exactly that line's unit price).
   9. Fresh-process replay: `src/replay.py` in a new interpreter re-derives every predicate and case status from
      the recorded context responses only (no `mf`, no DuckDB) and must equal the recorded statuses; trust limits
      declared.
   10. Windows: PowerShell instructions written and marked UNTESTED.
   D10 (diagnostic): B2 with a wrong frozen fingerprint must give INCONCLUSIVE.

## 5. Gate (exactly one)

- **PASS_KNOWN_BINDING**: A, B1 and B2 match `EXPECTED.json` (case and predicate statuses; A native = oracle;
  B1 native probe rejected) **and** tests 4–9 hold (no mutation reaches full observability; each matches its
  expected status; oracle sanity rejects; replay equal).
- **PARTIAL_KNOWN_BINDING**: A and B2 as expected, B1 genuinely unavailable or a noncritical evidence limitation
  prevents the full contrast, and no unsupported full-verification result occurs.
- **FAIL_KNOWN_BINDING**: any case or mutation with an unexposed, missing, wrong or proxy predicate is
  classified FULLY_OBSERVABLE / verified; or an identity or field change does not change the claim when it
  should; or A cannot be substantiated while native access works.
- **BLOCKED_RUNTIME_OR_INPUT**: the native environment or inventory cannot be executed or retrieved.
- **INCONCLUSIVE**: oracle, authority designation or evidence integrity invalid.

A mismatch between an observed status and `EXPECTED.json` that is **not** a false promotion to verified (for
example a different non-verified status) is reported as a deviation; it prevents PASS and is weighed under
PARTIAL / FAIL by whether the declared contrast still holds. No percentages, no accuracy claims.

## 6. Budget and stop

One upstream, one metric, cases A/B1/B2 plus the listed mutations, one inventory, no paid model, no new
framework. STOP after E1: E2–E8 and G1 are not executed.

## 7. Non-claims

Lab policy and approvals are SIMULATED; data are synthetic. PASS would show known-binding and observability
mechanics on this tiny stack only: not autonomous binding, not interpretation of ambiguous text, not that
`completed` means settled, not that any real settlement fact is absent anywhere outside the bounded estate.

## Amendments

(none)
