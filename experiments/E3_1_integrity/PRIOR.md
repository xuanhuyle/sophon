# E3.1: prior evidence, the two E3 defects, and scope

Written 2026-10-12, before the protocol freeze and before any corrected logic.

**Labels:**
- **OBSERVED**: measured, with committed evidence.
- **INFERRED**: reasoned from observations.
- **ASSUMED**: taken without test.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.**
   - Charter v1.1 §3 TRACE: temporal applicability; publication/observation time separate from effective time.
   - §3 VERIFY: test actual executed semantic behaviour; a passed hash does not prove anything.
   - §3 AUDIT: hashing verifies integrity against a trusted anchor, not correctness.
   - §5 Stage 1: infrastructure feasibility with adversarial controls.
   - Plan R4/R5 boundary: E3's IR guarantees must survive date applicability and forged evidence before E4 relies
     on them.
2. **Smallest uncertainty.** Can a thin wrapper around E3's unmodified validator do two things?
   - Refuse verification when the requirement is not in force at the evaluated effective date, keeping that
     separate from what was known when.
   - Refuse every promotion whose candidate receipts disagree with a **fresh** native MetricFlow run and a
     **fresh** raw-CSV reference calculation, both anchored outside the candidate receipts.
3. **Semantic layer and data.** The same pinned upstream `behramkorkut/Governed-Analytics-Agent` @ `312e97ad`
   (MIT), with dbt + MetricFlow 0.211.0 on DuckDB and seeded synthetic data. Everything else is lab-made:
   - the E3 clauses are LAB_AUTHORED;
   - roles and approvals are LAB_SIMULATED.
4. **Consistency with the architecture.** Verification still runs through the existing semantic layer's native
   engine. E3.1 adds no store, language or signing.
5. **Prior results.** Listed below.

## Branch topology

| PR | Branch | Head | State |
|---|---|---|---|
| #4 E0 | `experiment/e0-native-metricflow-2026-10-12` | `a84c855` | open draft |
| #5 E1 | `experiment/e1-known-binding-2026-10-12` | `e0dd474` | open draft |
| #6 E2 | `experiment/e2-blind-discovery-2026-10-12` | `39491cf` | open draft |
| #7 erratum | `experiment/e1-expressibility-erratum-2026-10-12` | `d8ad864` | open draft (CONFIRMED_E1_ERRATUM) |
| #8 E3 | `experiment/e3-governance-ir-2026-10-12` | `5130518` | open draft (PASS_IR_GUARD_VALUE) |

E3.1's branch `experiment/e3-1-integrity-2026-10-12` was created from `5130518`. PR #8 is unmerged.

## E3 (PR #8): what stands and what was wrong

**What stands (OBSERVED; E3's files are unchanged on this branch):**
- 54/54 frozen scenarios, with 0 false VERIFIED among them.
- Three bounded VERIFIED positives on fresh-at-the-time native receipts equal to raw-CSV oracles:

  | Positive | 2024 | 2025 | 2026 |
  |---|---|---|---|
  | S1 | 1 634 542.08 | 1 400 232.75 | 752 191.54 |
  | S2 customer | 310 780.14 | 261 972.06 | 155 221.02 |
  | S3 | 97 | 98 | 42 |

- A byte-identical consistency replay.

**What was wrong:** E3's own post-hoc diagnostics (`E3_formal_ir/evidence/diagnostics_nonscored.json`) found two
defects outside the frozen scenarios:
1. **F-TIME.** E3 checks only that `effective_to ≥ effective_from`. It never checks that the requirement is in
   force at `eval_effective_at`.
2. **F-FORGE.** E3's validator and replay trust the stored native and oracle receipts. A consistently rewritten
   pair is accepted. E3's `replay.py` is a **consistency replay**, not an independent verification.

**Reproduced here with the unmodified E3 validator** (OBSERVED, `evidence/reproduction/`, in memory only; E3's
receipts are untouched):
- **F-TIME** (case T1): S2 with `effective_from = 2027-01-01`, a valid approval, evaluated at effective date
  2026-06-30 → old E3 gives **VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS**.
- **F-FORGE** (case V5): on the approved S2 customer reading, the native rows and the oracle values are replaced
  with the **store-country** reading's values (366 057.38 / 288 072.98 / 138 501.23). The internal row hash is
  recomputed, and the claimed query, semantic and source identities are kept. Old E3 gives **VERIFIED**.
  - The forged pair is self-consistent.
  - It differs from the trusted frozen customer oracle.
  - It differs from E3's genuine customer native run (310 780.14 / 261 972.06 / 155 221.02).
- Old E3 also promotes these frozen E3.1 cases, all of which E3.1 expects to refuse:
  - T4, T8, T12 (not in force);
  - V5B (one-cent consistent forgery);
  - V7A and V7B (consistent fake semantic or raw-data revision);
  - V9A (negative-quantity snapshot with forged guards and amounts);
  - V10 (the approved reading's content rewritten to the store reading while keeping the approved reading id).

## Reused, unmodified

- E3 `validator.py`, `models.py`, `run_scenarios.py` (used as a library).
- E3 fixtures and receipts.
- E0 adapter and `run_e0.py --regen`.
- E1 `native_query_with_where`.
- The erratum's `oracle_b1.py` and guard functions.
- E2's `e2_oracle.py`.

The sha256 of each is in `cases/TRUSTED_MANIFEST.json`.

## What E3.1 cannot show

- That the raw source data, the pinned upstream or the lab approvals are genuine.
- Anything against an adversary who controls the verifier code, the trusted manifest or the pinned source.
- Cryptographic tamper-evidence or identity.
- Legal applicability rules beyond inclusive date windows. There is no supersession or conflict resolution.

**Design bias.** The same orchestrator wrote E0–E3 and this experiment. The cases are adversarial by design, not
blind.
