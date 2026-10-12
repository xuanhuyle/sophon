# E4: prior evidence and scope

Written 2026-10-12, before the freeze and before the E4 checker exists.

**Labels:**
- **OBSERVED**: measured, with committed evidence.
- **INFERRED**: reasoned from observations.
- **ASSUMED**: taken without test.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** Charter v1.1 covers this directly:
   - §3 VERIFY, implementation → governing direction: "test actual compiled/executed semantic behaviour …
     distinguish implementation defects, data violations, harmless/equivalent refactors, ambiguous meaning,
     incomplete evidence and unknown coverage".
   - §5 Stage 1 → early Stage 2, with adversarial controls.
   - Plan **R5 / Critical Gate A**.
2. **Smallest uncertainty.** Given a frozen, LAB-approved meaning for two existing E3 clauses, can a checker do
   all of the following?
   - Execute an *actual* modified dbt/MetricFlow implementation in its own disposable stack.
   - Compare it with an independent raw-CSV reference at the order-line grain.
   - Flag every planted plausible wrong implementation with a source-row counterexample.
   - Accept harmless changes.
   - Abstain on execution, provenance, approval and data-guard failures.
3. **Semantic layer and data.**
   - The pinned upstream `behramkorkut/Governed-Analytics-Agent` @ `312e97ad` (MIT), with dbt + MetricFlow
     0.211.0 on DuckDB.
   - Seeded **synthetic** data, plus three controlled fixtures derived from it.
   - The clauses are LAB_AUTHORED (E3) and the approvals are LAB_SIMULATED.
4. **Consistency with the architecture.** The candidate is a change to the existing semantic layer, and is
   executed by its own native engine. Sophon's reference is anchored in the approved meaning and the raw
   sources, not in the candidate.
5. **Prior results.** Listed below.

## Prerequisite: E3.1 (PR #9, `experiment/e3-1-integrity-2026-10-12` @ `9f6e02a`)

**PASS_INTEGRITY_HARDENING** (OBSERVED, `E3_1_integrity/evidence/gate.json`, criteria G0–G6 all true):
- E3's F-TIME and F-FORGE defects were reproduced and corrected.
- 28/28 frozen cases, with zero false promotions.
- The positives were verified using fresh native and fresh raw-CSV results.
- An independent rerun was identical.

**What E4 reuses from E3.1:**
- applicability and meaning: the `in_force` window, E3's validator on the approved record, and the trusted
  reading-meaning hashes;
- the trusted anchors: upstream commit, CSV hashes, governing-source hash and approved reading hashes.

**Not reused as the detector.** E3.1's `fresh_check` re-runs the trusted *pristine* reading, so it cannot
inspect an altered implementation (prompt §5A). E4 builds and executes each candidate separately.

## Earlier results this rests on

| Experiment | Result |
|---|---|
| E0 (#4) | native MetricFlow runtime reproduced |
| E1 (#5) + erratum (#7) | E1 B1 (unit price ≥ 100) is natively derivable at line grain, only under the quantity/revenue guards; E1's substantive PASS was withdrawn |
| E2 (#6) | PARTIAL discovery signal. H3 ("French market": customer vs store country) is a genuine ambiguity. H6's field meaning needs authority. |
| E3 (#8) | typed IR and simulated approvals: the approved readings S1/R_SINGLE and S2/R_CUSTOMER_COUNTRY |

## Pre-freeze inventory and feasibility (disclosed; NOT scored)

**Data facts (OBSERVED on the pinned raw CSVs):**
- No order line has unit price exactly 100.00; the nearest are 99.25 and 101.0. A `> 100` mutation therefore
  **agrees by accident** with `>= 100` on the pinned data. The controlled BOUNDARY fixture is needed to tell them
  apart.
- 33 customers carry the raw country alias `FR` or `FRA`, which the pinned `stg_customers` maps to France.
- Order statuses: 1 801 completed, 216 returned, 183 cancelled.

**Feasibility run** (`evidence/prefreeze_feasibility/`): every candidate stack was built once and its native
query executed, to confirm each mutation runs:
- M1, M2, M3, M4, M5, M5B, M6 and M6B build and execute;
- C4 fails at `mf query`, as designed.

Line-grain row counts were visible during this run. The expected classifications follow from the mutation
designs and were not changed after it.

**Reference sanity check.** `src/reference.py` reproduces the E3.1 trusted values on the pinned data:
- P1: 1 634 542.08 / 1 400 232.75 / 752 191.54 (3 305 lines);
- P2: 310 780.14 / 261 972.06 / 155 221.02 (840 lines).

## Scope and what E4 cannot show

**Can show:** for two LAB clauses, nine candidate implementations and four raw snapshots, whether the checker
classifies each one as preregistered, with row-level counterexamples.

**Cannot show:**
- detection rates beyond these planted variants;
- legal compliance;
- that the data or the approvals are genuine;
- downstream BI or agent behaviour;
- resistance to a compromised checker or reference;
- independent authorship. The same engineer wrote the reference, the mutations and the checker. Independence
  here means only that the reference is frozen and does not depend on any candidate.
