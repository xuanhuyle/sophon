# E3: prior evidence, alignment and limits

Written 2026-10-12, before freezing the protocol and before implementing the validator. Labels used throughout:
- **OBSERVED**: measured in E0–E2 or the erratum, with committed evidence.
- **INFERRED**: reasoned from observations.
- **ASSUMED**: taken without test.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** The work sits under:
   - SOPHON_CHARTER.md v1.1 §3, TRACE (interpretation / decision / approval / unresolved question, kept as
     distinct links);
   - §3, AUDIT, where PROPOSED, APPROVED, LINKED, VERIFIED_FOR_RECORDED_CHECKS and NOT_VERIFIED must not be
     conflated;
   - §2 (unresolved, partially observable and out-of-scope requirements are tracked explicitly).

   The stage is §5 Stage 1, infrastructure feasibility, with mechanistic adversarial controls. Plan risk: **R4**
   (does a typed IR add enforceable guarantees?).
2. **Smallest uncertainty.** Can a small typed JSON record plus a read-only validator mechanically keep apart
   three things?
   - approved meaning;
   - technically executable native behaviour;
   - unresolved meaning or missing evidence.

   And can it refuse every invalid "verified" promotion in four bounded scenarios, while still allowing a
   bounded VERIFIED where native MetricFlow and an independent oracle agree under a valid simulated approval?
3. **Semantic layer, data and authority.**
   - Semantic layer: the same pinned upstream `behramkorkut/Governed-Analytics-Agent` @
     `312e97ad192dcef02f688e31edc0a08c6cf4345f` (MIT), with dbt + MetricFlow 0.211.0 on DuckDB.
   - Data: seeded **synthetic** rows.
   - Clauses: all **LAB_AUTHORED**.
   - Authority: every role, approval and revocation is **LAB_SIMULATED**. There are no real people, signatures
     or legal interpretations.
4. **Consistency with the architecture.** The IR is a Sophon-internal record that sits between the governing
   text and the customer's existing semantic layer (plan §2: normative model ≠ binding model ≠ execution model).
   E3 writes nothing to dbt/MetricFlow. It reads the native catalog and executes native queries only.
5. **Prior results built on.** Listed below. Negative and corrective findings are kept.

## Branch topology (resolved before branching)

| PR | Branch | Head | Base | State |
|---|---|---|---|---|
| #4 E0 | `experiment/e0-native-metricflow-2026-10-12` | `a84c855` | `main` | open draft, no CI, no reviews |
| #5 E1 | `experiment/e1-known-binding-2026-10-12` | `e0dd474` | E0 | open draft; erratum comment posted |
| #6 E2 | `experiment/e2-blind-discovery-2026-10-12` | `39491cf` | E1 | open draft |
| #7 erratum | `experiment/e1-expressibility-erratum-2026-10-12` | `d8ad864` | E2 | open draft |

E3's branch `experiment/e3-governance-ir-2026-10-12` was created from `d8ad864`. Nothing has merged.

## E0: native runtime (PASS_NATIVE_RUNTIME; OBSERVED)

Native `mf query` for `completed_revenue` ran on the synthetic DuckDB rows and equalled an independent raw-CSV
recomputation. The run is reproducible, with:
- semantic manifest `e8e9bfc7…`;
- env freeze `db0a13e9…`.

The adapter `E0_native_adapter/src/mf_adapter.py` is reused unmodified.

## E1: known binding (PASS_KNOWN_BINDING as originally recorded; substantively withdrawn by the erratum)

Mechanisms E1 already had, all OBSERVED and all of which E3 must not claim as new:
- a typed predicate/binding registry;
- an **authority registry**, where a field is authoritative for a fact kind only if listed. Example:
  `payment_settlement_confirmation: []`;
- detection of `status = 'completed'` offered as settlement evidence (NOT_AUTHORITATIVE_FOR_FACT, variant 6);
- detection of missing bindings and invalid physical fields;
- an estate-fingerprint check, where a wrong fingerprint gives INCONCLUSIVE;
- native vs raw-CSV oracle comparison for case A.

What E1 lacked:
- interpretation alternatives;
- approval objects (its authority registry is a fixed lab designation, not a time-scoped approval);
- known-at vs effective-at;
- a computed-only status;
- derived expressions.

**E1 flaw.** B1 was classified "present in source, not exposed" by a dimension-only check, which the erratum
withdrew.

## E2: blind discovery (PARTIAL_DISCOVERY_SIGNAL; OBSERVED)

Relevant here:
- **H3** ("French market"): both `customer__country` and `store__store_country` readings execute natively and
  differ. In 2024 they give 310 780.14 vs 366 057.38. The solver named the ambiguity correctly but was scored
  as missing a predicate.
- **H6** ("country of residence is France"): the solver proposed the exact native query (97 / 98 / 42). It
  declined to equate `customers.country` with residence because nothing in the packet documents that meaning.
- **Frozen reference flaw:** E2's reference author assumed `country` means residence, so H6 was scored as
  over-abstention. E2 RESULTS §5.2 records this as a defect in the clause and reference, not only in the solver.
  E3's S3 makes exactly this gap a first-class state.
- **H1:** no payment column among 155 warehouse columns.
- `src/e2_oracle.py` gives stdlib raw-CSV oracles for H3 (both readings), H6 and the H1 status proxy. It is
  reused unmodified.

## E1 expressibility erratum (CONFIRMED_E1_ERRATUM; OBSERVED; prerequisite gate for E3)

Confirmed from the erratum branch (`evidence/gate.json`, all eight gates true):
- Genuine native `mf` metric-filter witness for E1 B1 at sales-line grain: 1 634 542.08 / 1 400 232.75 /
  752 191.54. It equals an independent raw-CSV oracle per year and per line (3 305 lines).
- Guards hold on the pinned rows: quantity ≥ 1 on 5 526 lines; revenue = q × u exactly; prices exact; unique
  `sales_id`; exact DECIMAL/HUGEINT comparison.
- Negative and zero quantities on disposable copies break the derivation. The 99.99 / 100.00 / 100.01 boundary
  is exact.
- The semantic layer **does not enforce** `quantity > 0`; dbt tests only `not_null`.

The E3 prerequisite therefore holds. The erratum's `oracle_b1.py`, `run_erratum.guards` and `warehouse_lines`
are reused unmodified.

## What E3 can and cannot show

**Can show.** For four LAB_AUTHORED clauses on one synthetic stack:
- whether specific invariants are enforced mechanically, and fail when violated;
- whether a bounded VERIFIED is reachable only through valid simulated approvals plus native/oracle agreement.

**Cannot show:**
- legal or business correctness of any interpretation;
- that `customers.country` means residence anywhere real. A simulated equivalence approval is a lab hypothesis
  only;
- that no existing library or tool could enforce the same invariants;
- reliability on authentic requirements (E8);
- independent verification of wrong implementations (E4);
- transposition (E5) or reverse reconciliation (E6);
- durable bitemporal audit storage (E7).

**Design bias.** The orchestrator wrote E0–E2, the erratum, these clauses, the fixtures, the expected outcomes
and the validator. The test is mechanistic: expected outcomes are frozen before the validator exists. It is not
blinded.
