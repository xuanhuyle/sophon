# E4: results

- Freeze `6553fb3`: protocol, REFERENCE, VARIANTS, candidates and fixtures. `FREEZE_MANIFEST.txt` is in
  `fe2c484`.
- The checker, scorer, gate and tests were written after the freeze.
- Labels: **OBSERVED**, **INFERRED**, **ASSUMED**.
- Clauses are LAB_AUTHORED (E3), approvals LAB_SIMULATED. The data is synthetic plus three controlled fixtures.

## 1. Verdict

**PASS_INDEPENDENT_VERIFICATION_SIGNAL** (mechanical, `evidence/gate.json`; criteria Q0–Q7 in §5).

## 2. Variant outcomes (OBSERVED, `evidence/run/variant_results.json`)

Each candidate was instantiated in its **own** disposable copy of the pinned project:
1. its patch was applied;
2. the snapshot's raw CSVs were loaded with the upstream loader;
3. `dbt build` and `dbt parse` wrote its own DuckDB file;
4. its own native query was executed by genuine `mf`, by year and at order-line grain (`group_by: sales`).

The reference is `src/reference.py` over the snapshot's raw CSVs. It never sees a candidate.

| Variant | Candidate change | Snapshot results | Checker | Expected |
|---|---|---|---|---|
| M1 | none; approved derived query | PINNED and BOUNDARY conform (guards true) | **VERIFIED_FOR_LAB_CHECKS** | same |
| M2 | new YAML metric: completed AND customer country France | PINNED conforms (840 lines) | **VERIFIED_FOR_LAB_CHECKS** | same |
| M6B (← M1) | YAML: expose `unit_price` dimension; metric `>= 100` | PINNED and BOUNDARY conform | **NO_MATERIAL_DRIFT_FOR_CHECKS** | same |
| M6 (← M2) | YAML `IN (...)` reordered, new label/description; comment-only `fact_sales.sql` edit | PINNED conforms | **NO_MATERIAL_DRIFT_FOR_CHECKS** | same |
| **M3** (← M6B) | YAML: `unit_price > 100` | PINNED **conforms by accident**; BOUNDARY mismatch | **NONCONFORMING** | same |
| **M4** (← M6B) | YAML: `status != 'cancelled'` | PINNED and BOUNDARY mismatch (+408 returned lines) | **NONCONFORMING** | same |
| **M5** (← M2) | YAML: `store__store_country = 'France'` | PINNED mismatch (669 expected lines missing, 718 unexpected lines added) | **NONCONFORMING** | same |
| **M5B** (← M2) | dbt `stg_customers.sql` drops the FR/FRA aliases; metric correct | PINNED mismatch (329 expected lines missing) | **NONCONFORMING** | same |
| C1 | M2 on unregistered STALE raw data | not verified | NOT_VERIFIED (SOURCE_SNAPSHOT_UNREGISTERED) | same |
| C2A | M2, no approval supplied | native conforms, but no approved reading | NOT_VERIFIED (APPROVAL_MISSING) | same |
| C2B | M2, requirement `effective_from` 2027-01-01 | native conforms | NOT_APPLICABLE (REQUIREMENT_NOT_IN_FORCE) | same |
| C3 | M5 plus a forged claim of the approved customer totals | PINNED mismatch | NONCONFORMING plus CANDIDATE_CLAIM_CONTRADICTED | same |
| C4 | filter on nonexistent `customer__residence_country` | `mf query` exit 1 | NOT_VERIFIED (EXECUTION_FAILURE) | same |
| C5 | M1 on the NEGQTY fixture | guard `quantity_positive` false (min q = −1) | NOT_VERIFIED (DATA_GUARD_FAILURE; the mismatch is also reported) | same |

**14/14 as frozen.**

- **Detected:** M3, M4, M5, M5B and C3, i.e. all wrong implementations.
- **Missed:** none.
- **False assurances:** 0.
- **False alarms:** 0. M6 and M6B changed the semantic manifest (`601204c6…`, `690689375907…` ≠ pristine `e8e9bfc7…`) and were still accepted.

## 3. Concrete counterexamples (OBSERVED, `evidence/run/counterexamples.json`)

**M3, the accidental-agreement case.**
- On PINNED, the candidate totals equal the reference exactly (1 634 542.08 / 1 400 232.75 / 752 191.54): no
  pinned line has a unit price of exactly 100.
- On BOUNDARY, order line **2** (order 1, 2025-09-08, completed, quantity 3, unit price **100.00**) is expected
  to be included with 300.00. The native candidate excludes it, so its 2025 total is 1 400 332.76 against the
  reference 1 400 632.76.
- Compiled SQL: `WHERE sales__status = 'completed' AND sales__unit_price > 100`.

**M4.** Line **7** (order 3, 2024-05-26, status **returned**, quantity 3, unit price 405.01) is included by the
native candidate with 1 215.03 but is not eligible. Line 8 is the same case. There are 408 such lines in total.
Compiled SQL: `WHERE sales__status != 'cancelled' AND sales__unit_price >= 100`.

**M5.** Line **1** (order 1, completed, customer country France, **store country Germany**, 1 104.90) is
expected but missing. 669 such lines are missing and 718 store-France lines are added. The candidate totals
equal the rejected store reading (366 057.38 / 288 072.98 / 138 501.23). Compiled SQL joins
`stores_src.country AS store__store_country`.

**M5B.** Line **45** (order 18, 2026-04-13, completed, customer raw country **`FR`**, normalised France, 4 × 665.42
= 2 661.68) is expected but missing; 329 lines in total. The MetricFlow SQL is identical to M2's. The defect sits
in the dbt model diff, `stg_customers.sql` minus the `FR`/`FRA` aliases, and shows up as rebuilt rows.

**C3.**
- The forged claim says 310 780.14 / 261 972.06 / 155 221.02.
- The checker **executed** the candidate and got 366 057.38 / 288 072.98 / 138 501.23, so
  CANDIDATE_CLAIM_CONTRADICTED.
- The claim is never used to decide conformance.

**C5 (control, not a nonconformity).**
- On NEGQTY, line **1** has quantity −1. The derived filter drops it, against a reference amount of −368.30.
- The erratum guard `quantity_positive` fails on the candidate's own warehouse, so the result is NOT_VERIFIED,
  not NONCONFORMING: the implementation's precondition is violated on this data.

## 4. Evidence that the candidates were really executed (Q3, `evidence/run/`)

- **`candidate_stacks.json`**, per stack: patch diff, build steps (loader, `dbt build`, `dbt parse` exit codes),
  raw CSV hashes, candidate semantic-manifest sha256, `mf` argv, exit codes, `mf` entry-point identity and
  compiled SQL.
- **`compiled_sql/*.sql`** and **`diffs/*.diff`**: the mutated predicates appear in the compiled SQL of M3, M4 and
  M5. M5B's diff is in the dbt model.
- **Candidate manifest sha256 values** all differ from pristine: M3 `c567ad40…`, M4 `62bd6cbe…`, M5 `c81c4935…`,
  M5B `3fe9482a…`. M1 equals pristine `e8e9bfc7…`, because its candidate is the unchanged project.
- **The reference** equals the frozen `REFERENCE.json` on every snapshot used. On PINNED it equals E3.1's trusted
  values.

## 5. Gate criteria (`evidence/gate.json`)

| Criterion | Result |
|---|---|
| Q0 | E3.1 = PASS_INTEGRITY_HARDENING; pristine M1 and M2 stacks build; reference equals the frozen one. |
| Q1 | Baselines VERIFIED; harmless changes NO_MATERIAL_DRIFT. |
| Q2 | All 5 wrong variants NONCONFORMING, each with row-level counterexamples. M3 conforms on PINNED and mismatches on BOUNDARY, including line 2. C3's claim is contradicted. |
| Q3 | 4 genuine native mutations evidenced: M3, M4, M5 (YAML) and M5B (dbt model). |
| Q4 | All controls classified as expected; none VERIFIED. |
| Q5 | Fresh-process rerun: all stacks rebuilt, normalized results identical. |
| Q6 | Frozen files unchanged; E0–E3.1 directories unchanged against `9f6e02a`. |
| Q7 | 5 unit tests passed. |

## 6. Limitations

- **Design bias.**
  - The same engineer wrote the approved reference, the fixtures, the mutations and the checker. Every wrong
    implementation was planted with knowledge of the reference. This shows the mechanism works on these
    variants; it gives no detection rate.
  - The BOUNDARY fixture was designed to expose `>` vs `>=`. A real estate could contain rows that no registered
    snapshot covers. The checker is only as discriminating as its registered snapshots: on PINNED alone, M3
    would have been accepted.
- **Grain.**
  - Row-level comparison relies on the candidate metric being queryable at the order-line entity (`sales`).
    Metrics without a line-grain entity would get totals-only evidence. That case was not tested.
  - Amounts are compared per line and per year only. Other groupings (channel, country breakdowns) were not
    checked.
- **What the reference encodes.**
  - The reference re-implements the pinned staging normalisations (status trim/lower, the country alias table).
    The approved meaning is "as normalised by the pinned upstream".
  - A change to that normalisation (M5B) is treated as a deviation. This is by design, but it is a LAB
    decision about what the approved meaning includes.
- **Authority and trust.**
  - Authority and time checks reuse E3/E3.1 on the approved record; approvals remain LAB_SIMULATED.
  - The checker and reference code, `REFERENCE.json` and the pinned upstream are trusted, as in E3.1.
- **Cost.** About 8 minutes per full run (15 candidate stacks rebuilt). No incremental build was attempted.
- **Not covered.** Downstream BI or agent consumption, legal compliance and production detection rates. No
  Windows run; PowerShell UNTESTED. The repository has no CI.
