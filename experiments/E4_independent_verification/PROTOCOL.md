# E4: protocol (frozen before the checker is implemented and before any scored candidate run)

Frozen 2026-10-12 on `experiment/e4-independent-semantic-verify-2026-10-12`. It was created from E3.1's head
`9f6e02a` (PR #9, PASS_INTEGRITY_HARDENING).

**Freeze commit contents:**
- `PRIOR.md` and this file;
- `REFERENCE.json`;
- `VARIANTS.json`;
- `candidates/*.json`;
- `fixtures/reference_lines/`;
- `src/{reference,fixtures,candidate_stack,build_variants,build_reference}.py`;
- `evidence/prefreeze_feasibility/`.

Their sha256 values and the freeze SHA go in `FREEZE_MANIFEST.txt`, committed next.

**Written only after the freeze:** the checker (`src/checker.py`), the scorer, the gate and the tests.
Deviations go under "Amendments". Frozen expectations never change.

## 1. Question

For each variant, a candidate native implementation of an approved LAB policy, does the checker produce the
preregistered classification? Specifically:
- **VERIFIED_FOR_LAB_CHECKS** for the correct baselines;
- **NO_MATERIAL_DRIFT_FOR_CHECKS** for harmless changes;
- **NONCONFORMING_IMPLEMENTATION** with a source-row counterexample for wrong implementations;
- **NOT_VERIFIED** or **NOT_APPLICABLE** with a specific reason for the controls.

All of this must hold while **executing the candidate's own modified dbt/MetricFlow stack**.

## 2. What is fixed (`REFERENCE.json`)

**The approved specifications** are P1 and P2:
- they cite their E3 record, clause, reading, LAB_SIMULATED approval id, governing-source hash and E3.1
  approved-reading meaning hash;
- they list exact predicates, the amount, the period, the population and the row grain;
- P1 also lists the derivation guards that apply when it is implemented with metric filters.

**Registered snapshots:**
- verification snapshots: P1 → PINNED and BOUNDARY; P2 → PINNED;
- guard fixture: NEGQTY;
- each with its CSV sha256 values and exact edits;
- STALE is an *unregistered* example.

**Reference results** come from `src/reference.py` (stdlib Decimal over raw CSVs, using the pinned staging
normalisations):
- year totals, line counts and a line-membership hash for every policy and snapshot;
- the full membership in `fixtures/reference_lines/`.

On PINNED, P1 and P2 equal E3.1's trusted values.

## 3. Candidates and variants (`candidates/*.json`, `VARIANTS.json`)

Each candidate is:
- a text patch to the pinned project (semantic YAML and/or dbt SQL; every anchor must occur exactly once);
- the native query that implements the policy;
- its predecessor (`change_of`), or null for a first implementation.

| Variant | Candidate (patch) | Snapshots | Expected |
|---|---|---|---|
| M1 | none; approved derived query (revenue, status completed AND `Metric(revenue@sales) >= 100 * Metric(quantity_sold@sales)`) | PINNED, BOUNDARY | VERIFIED_FOR_LAB_CHECKS |
| M2 | new metric `french_market_revenue`: completed AND `customer__country = 'France'` | PINNED | VERIFIED_FOR_LAB_CHECKS |
| M6B (change of M1) | expose `unit_price` as a dimension; metric `premium_completed_revenue`: completed AND `unit_price >= 100` | PINNED, BOUNDARY | NO_MATERIAL_DRIFT_FOR_CHECKS |
| M6 (change of M2) | `IN ('France')` / `IN ('completed')`, reordered; new label and description; comment-only edit in `fact_sales.sql` | PINNED | NO_MATERIAL_DRIFT_FOR_CHECKS |
| **M3** (change of M6B) | `unit_price > 100` | PINNED, BOUNDARY | NONCONFORMING; agrees by accident on PINNED; counterexample line 2 (100.00) on BOUNDARY |
| **M4** (change of M6B) | `status != 'cancelled'` instead of `= 'completed'` | PINNED, BOUNDARY | NONCONFORMING |
| **M5** (change of M2) | `store__store_country = 'France'` | PINNED | NONCONFORMING |
| **M5B** (change of M2) | metric unchanged; **dbt** `stg_customers.sql` drops the `FR`/`FRA` aliases | PINNED | NONCONFORMING |
| C1 | M2 on the unregistered STALE snapshot | STALE | NOT_VERIFIED (SOURCE_SNAPSHOT_UNREGISTERED) |
| C2A | M2 with no approval supplied | PINNED | NOT_VERIFIED (APPROVAL_MISSING) |
| C2B | M2 with the requirement `effective_from` set to 2027-01-01 | PINNED | NOT_APPLICABLE (REQUIREMENT_NOT_IN_FORCE) |
| C3 | M5 plus a forged candidate claim of the approved customer values | PINNED | NONCONFORMING plus CANDIDATE_CLAIM_CONTRADICTED |
| C4 | filter on a nonexistent dimension | PINNED | NOT_VERIFIED (EXECUTION_FAILURE) |
| C5 | M1 on the NEGQTY guard fixture | NEGQTY | NOT_VERIFIED (DATA_GUARD_FAILURE) |

**Native mutations:** M3, M4 and M5 alter the semantic YAML; M5B alters a dbt model.

**Expected statuses** are read **only by the scorer** (`src/score.py`). The checker never reads `expected`.

## 4. Checker contract (`src/checker.py`, written after the freeze)

**Inputs per variant:**
- the candidate file;
- the variant's snapshots, authority/time context and optional candidate claim;
- `REFERENCE.json`;
- the pristine pinned project.

**Step A: authority and time (reused from E3/E3.1).** Validate the *approved* E3 record (not the candidate) with
the context's approvals, `record_patch` and times, using the unmodified E3 validator plus E3.1 `in_force`.

| Outcome | Reason |
|---|---|
| a structural error other than source-not-known | APPROVED_SPEC_INVALID |
| source not known | SOURCE_NOT_KNOWN |
| not in force | REQUIREMENT_NOT_IN_FORCE |
| the selected reading ≠ the policy's reading, or its meaning hash ≠ the trusted hash | APPROVAL_MISSING |

**Step B: build and execute the candidate per snapshot.**
1. Instantiate the candidate stack with `candidate_stack.build`: copy the project, apply the patch, load the
   snapshot's raw CSVs, then `dbt build` and `dbt parse` into its own DuckDB file.
2. If the stack's CSV hashes are not a registered snapshot for this policy (verification or guard fixture) →
   SOURCE_SNAPSHOT_UNREGISTERED.
3. A patch, build or `mf` failure → EXECUTION_FAILURE.
4. Execute the candidate's own query by year **and** at line grain (`group_by: [sales]`), through genuine `mf`.
   Record the compiled SQL, the candidate semantic-manifest sha256 and the patch diff.
5. If the candidate query contains a metric filter (`Metric(`), run the erratum guards on the candidate's own
   warehouse. Any failure → DATA_GUARD_FAILURE.

**Step C: independent reference.** Run `reference.compute(snapshot, policy)` on the snapshot's raw CSVs after
checking their hashes against `REFERENCE.json`. It must equal the frozen reference results.

**Step D: comparison.**

| Reason | Condition |
|---|---|
| TOTAL_MISMATCH | year totals differ |
| MEMBERSHIP_MISMATCH | the set of line ids differs |
| AMOUNT_MISMATCH | a shared line's amount differs |

**Counterexamples:** up to 5 lines in each direction. Each gives:
- `order_item_id`, `order_id`, order date, raw and normalised status, quantity, unit price, raw and normalised
  customer country, and store country;
- the expected inclusion and amount;
- the actual native inclusion and amount;
- lineage: the candidate patch diff and the compiled-SQL sha256.

**Step E: candidate claim.** If present, it is compared with the candidate's actual execution
(CANDIDATE_CLAIM_CONTRADICTED when different). A claim is never used to decide conformance.

**Aggregation.** Per snapshot: CONFORMS, MISMATCH, or NOT_VERIFIED(reason). A guard failure on a snapshot makes it
NOT_VERIFIED even if numbers also differ. Variant precedence:
1. Step-A NOT_APPLICABLE or NOT_VERIFIED.
2. Any MISMATCH snapshot → NONCONFORMING_IMPLEMENTATION.
3. Any NOT_VERIFIED snapshot → NOT_VERIFIED.
4. All snapshots CONFORMS → VERIFIED_FOR_LAB_CHECKS if `change_of` is null, otherwise
   NO_MATERIAL_DRIFT_FOR_CHECKS.

**A changed semantic-manifest hash is recorded, never a finding by itself.**

## 5. Gate (`src/gate.py`; mechanical; exactly one verdict)

| Criterion | Condition |
|---|---|
| Q0 | E3.1 committed gate = PASS_INTEGRITY_HARDENING. The pristine runtime and reference run: M1 and M2 stacks build. Reference results equal the frozen REFERENCE on every snapshot used. |
| Q1 | M1 and M2 = VERIFIED_FOR_LAB_CHECKS. M6 and M6B = NO_MATERIAL_DRIFT_FOR_CHECKS. |
| Q2 | M3, M4, M5, M5B and C3 = NONCONFORMING_IMPLEMENTATION, each with ≥ 1 counterexample carrying source facts, expected and actual. M3: PINNED totals equal (accidental agreement) and BOUNDARY gives a mismatch that includes line 2. C3: CANDIDATE_CLAIM_CONTRADICTED. |
| Q3 | ≥ 2 wrong variants are genuine native mutations: a non-empty YAML/dbt diff, candidate stack rebuilt, and evidence of effect. Either the candidate manifest sha ≠ pristine and the compiled SQL contains the mutated predicate, or (for a dbt model mutation) the diff is in the model SQL and the rebuilt rows differ. |
| Q4 | C1, C2A, C2B, C4 and C5 get their expected status and reason. None of them is VERIFIED or NO_MATERIAL_DRIFT. |
| Q5 | A fresh-process rerun (separate process, minimal environment, temporary cwd, all stacks rebuilt) gives identical normalized variant results. |
| Q6 | Frozen files unchanged (FREEZE_MANIFEST, except amended `PROTOCOL.md`). E0–E3.1 directories unchanged against `9f6e02a`. |
| Q7 | Unit tests pass. |

**Verdict mapping:**

| Verdict | Condition |
|---|---|
| BLOCKED | Q0's runtime/reference part fails, or E3.1 did not pass |
| INCONCLUSIVE | freeze integrity broken, or the reference differs from the frozen REFERENCE |
| FAIL_FALSE_ASSURANCE | any of M3, M4, M5, M5B, C3, C1, C2A, C2B, C4 or C5 is VERIFIED_FOR_LAB_CHECKS or NO_MATERIAL_DRIFT_FOR_CHECKS |
| FAIL_FALSE_ALARM | M6 or M6B is NONCONFORMING (and no false assurance) |
| PASS_INDEPENDENT_VERIFICATION_SIGNAL | Q0–Q7 all hold |
| PARTIAL_INDEPENDENT_VERIFICATION | otherwise, with ≥ 1 wrong variant detected and no unsafe result |

## Amendments

Added after the freeze. The frozen bytes are `PROTOCOL.md` at `6553fb3` (sha256 in `FREEZE_MANIFEST.txt`). No
reference, variant, candidate, expectation or gate changed.

1. **Code written after the freeze, as planned:**
   - `src/checker.py`, `src/gate.py` (scorer + verdict), `src/replay.py`;
   - `src/extract_evidence.py`, which writes readable compiled SQL, diffs and counterexamples from the run;
   - `tests/test_e4.py`.
2. **Replay environment.** The child process gets `PATH` and a temporary `HOME` (dbt needs a writable home), with
   `python -I` and a temporary cwd. It rebuilds every fixture and candidate stack under `runs/checker_replay`.
3. **Q3 evidence tokens.** The scorer looks for these strings in the compiled SQL: `sales__unit_price > 100`
   (M3), `!= 'cancelled'` (M4) and `store__store_country` (M5). M5B is evidenced by its `stg_customers.sql` diff
   plus mismatching rebuilt rows, as §5 specifies for dbt model mutations.
