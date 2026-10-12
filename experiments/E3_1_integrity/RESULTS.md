# E3.1: results

- Freeze `e0bf06f`: protocol, 28 cases, trusted manifest and the reproductions. `FREEZE_MANIFEST.txt` is in
  `a37ad65`.
- The corrected wrapper, the fresh verifier, the tests and the gate were written after the freeze.
- Labels: **OBSERVED**, **INFERRED**, **ASSUMED**.
- Clauses are LAB_AUTHORED and approvals LAB_SIMULATED. The data is synthetic.

## 1. Gate (OBSERVED, `evidence/gate.json`): **PASS_INTEGRITY_HARDENING**

| Criterion | Result |
|---|---|
| G0 | F-TIME and F-FORGE were reproduced with the unmodified E3 validator before any fix (`evidence/reproduction/`). |
| G1 | 28/28 cases match their frozen expectations. For the positives, the fresh values equal the trusted expected values. In V5 the fresh customer result differs from the forged values. |
| G2 | **0 false promotions.** |
| G3 | The fresh rebuild matched every trusted anchor: upstream commit and clean state, env freeze `db0a13e9…`, semantic manifest `e8e9bfc7…`, five raw-CSV hashes, and seven code hashes. All 6 VERIFIED cases rest on fresh native runs (exit 0) and fresh reference calculations in the same verifier process. |
| G4 | A second, independent verifier process (`python -I`, minimal environment, temporary cwd) did its own rebuild. Its warehouse file hash differs (`ac2c9093…` vs `51fce99e…`), which is expected because DuckDB files are not byte-stable. The normalized case results are **identical**. |
| G5 | E0, E1, E2, erratum and E3 directories are unchanged against `5130518` (empty `git diff`). |
| G6 | Unit tests: 4 passed. |

## 2. What E3 got wrong, reproduced on unmodified E3 (OBSERVED)

| Defect | Configuration | Unmodified E3 | E3.1 |
|---|---|---|---|
| **F-TIME** (T1) | S2 approved; `effective_from` 2027-01-01; evaluated at 2026-06-30; source and approval known | **VERIFIED** | REQUIREMENT_NOT_IN_FORCE |
| **F-FORGE** (V5) | S2 customer reading approved. The native rows and oracle values are both replaced with the **store-country** result (366 057.38 / 288 072.98 / 138 501.23) and the row hash is recomputed. The claimed query and identities are unchanged. | **VERIFIED** | NOT_VERIFIED. The fresh native customer run gives 310 780.14 / 261 972.06 / 155 221.02, so CANDIDATE_NATIVE_DISAGREES_WITH_FRESH and CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH. |

**Anti-vacuity for F-FORGE:**
- the forged pair is self-consistent;
- its internal hash is valid;
- it claims the customer query;
- it equals the store reading, not the trusted customer oracle or E3's genuine customer native run.

**Other false promotions by unmodified E3, all now refused:**
- not in force: T4, T8, T12;
- one-cent consistent forgery: V5B;
- consistent fake semantic revision: V7A;
- consistent fake raw-data hash: V7B;
- forged guards and amounts on a negative-quantity estate: V9A;
- approved reading content rewritten to the store reading under the approved id: V10.

V8A and V8B were VERIFIED by E3 on *genuine* receipts. E3.1 refuses them because the fresh runtime or the trusted
reference was unavailable. That is a refusal to promote without fresh evidence, not a false promotion by E3.

## 3. Temporal cases (OBSERVED, `evidence/run/case_results.json`)

| Case | `eval_known_at` / `eval_effective_at` | Old E3 | **E3.1** |
|---|---|---|---|
| T1 start after the evaluation date | 10-06 / 2026-06-30 | VERIFIED | REQUIREMENT_NOT_IN_FORCE |
| T2 start = evaluation date (inclusive) | 10-06 / 2026-06-30 | VERIFIED | **VERIFIED** (fresh) |
| T3 end = evaluation date (inclusive) | same | VERIFIED | **VERIFIED** (fresh) |
| T4 end one day before | same | VERIFIED | REQUIREMENT_NOT_IN_FORCE |
| T5 source not yet known | 09-30 / 2026-06-30 | STRUCTURALLY_INVALID | NOT_KNOWN_AT_EVALUATION_TIME |
| T6 approval known later | 10-06 / 2026-06-30 | MEANING_UNRESOLVED | MEANING_UNRESOLVED (approval not mentioned) |
| T7A retroactive rule, as known before its observation | 09-30 / 2024-06-30 | STRUCTURALLY_INVALID | NOT_KNOWN_AT_EVALUATION_TIME |
| T7B retroactive rule, as known after its observation | 10-06 / 2024-06-30 | VERIFIED | **VERIFIED** (fresh) |
| T8 approval in force, requirement ended 2025-12-31 | 10-06 / 2026-06-30 | VERIFIED | REQUIREMENT_NOT_IN_FORCE |
| T9 in force, no approval | same | MEANING_UNRESOLVED | MEANING_UNRESOLVED |
| T10 corrupt source hash and not in force | same | STRUCTURALLY_INVALID | STRUCTURALLY_INVALID (not disguised as NOT_IN_FORCE) |
| T11 S4 missing fact and not in force | same | MISSING_REQUIRED_FACT | REQUIREMENT_NOT_IN_FORCE (uncovered `settled_by_processor` kept) |
| T12 S3 approved equivalence, not in force | same | VERIFIED | REQUIREMENT_NOT_IN_FORCE |

## 4. Evidence cases (OBSERVED)

| Case | Old E3 | **E3.1** | Fresh native (2024 / 2025 / 2026) | Fresh reference |
|---|---|---|---|---|
| V1 S1 derived, clean | VERIFIED | **VERIFIED** (5 fresh guards true, min q = 1) | 1 634 542.08 / 1 400 232.75 / 752 191.54 | equal (erratum `oracle_b1`) |
| V2 S2 customer, clean | VERIFIED | **VERIFIED** | 310 780.14 / 261 972.06 / 155 221.02 | equal (E2 oracle) |
| V3 S3 with simulated equivalence | VERIFIED | **VERIFIED** (`lab_simulated_equivalence_used: true`) | 97 / 98 / 42 | equal (E2 `h6`) |
| V4 S4 status proxy | MISSING | MISSING_REQUIRED_FACT | — | — |
| V5 forged store-reading pair | VERIFIED | NOT_VERIFIED | customer values (≠ forged) | customer values |
| V5B forged pair +0.01 | VERIFIED | NOT_VERIFIED | — | — |
| V6 single receipt +0.01 | NOT_VERIFIED | NOT_VERIFIED | — | — |
| V7A consistent fake semantic revision | VERIFIED | NOT_VERIFIED (TRUST_ANCHOR_MISMATCH) | — | — |
| V7B consistent fake raw-CSV hash | VERIFIED | NOT_VERIFIED (TRUST_ANCHOR_MISMATCH) | — | — |
| V7C stale receipt revision only | NOT_VERIFIED | NOT_VERIFIED | — | — |
| V8A runtime unavailable | VERIFIED | NOT_VERIFIED (FRESH_RUNTIME_UNAVAILABLE: the E0 adapter refused a non-installed `mf` entry point) | — | computed |
| V8B reference code altered | VERIFIED | NOT_VERIFIED (FRESH_REFERENCE_UNAVAILABLE: hash `804417df…` ≠ trusted `2bcfd2d2…`; not executed) | computed | — |
| V9A negative-quantity estate, forged guards and amounts | VERIFIED | NOT_VERIFIED (FRESH_GUARD_FAILED: `quantity_positive` false, min q = −1; fresh native 2025 = 1 399 083.79 ≠ reference) | — | — |
| V9B negative-quantity estate, honest receipts | NOT_VERIFIED | NOT_VERIFIED | — | — |
| V10 approved reading content swapped to store | VERIFIED | NOT_VERIFIED (UNTRUSTED_READING_CONTENT; the fresh trusted customer query disagrees with the candidate) | customer values | customer values |

**Separate states per case** (`states` in the results):
- `known_at_eval_time`;
- `applicable_at_effective_date`;
- `approved_lab_meaning`;
- `lab_simulated_equivalence_used`;
- `technically_executable_candidate`;
- `fresh_reexecution_succeeded`;
- `fresh_reference_agreement`;
- `candidate_agrees_with_fresh`.

Caveat: in V10, `approved_lab_meaning` is `true`, because it reflects E3's id-based approval. The content check is
the one that fails (Amendment 4).

## 5. What changed relative to E3

E3's code and files are unchanged; E3.1 imports E3's validator.

**`src/e31.py` (wrapper):**
- An **inclusive effective-window applicability** check (`in_force`), on the effective-time axis only.
- SOURCE_NOT_YET_KNOWN is separated out as its own status.
- Precedence:
  1. STRUCTURALLY_INVALID
  2. NOT_KNOWN_AT_EVALUATION_TIME
  3. REQUIREMENT_NOT_IN_FORCE
  4. MISSING_REQUIRED_FACT
  5. MEANING_UNRESOLVED
  6. NOT_VERIFIED
  7. VERIFIED
- Any E3 promotion that is in force is sent to the fresh verifier.

**`src/fresh_verifier.py`:**
- Rebuilds the estate from the pinned upstream in its own process and checks it against the trusted anchors.
- Executes the **trusted** reading's native query with genuine `mf`.
- Runs the hash-checked reference code on the regenerated raw CSVs, and the fresh guards.
- Compares the candidate receipts with these fresh results.
- Checks the candidate's claimed revisions and the approved reading's *meaning hash* against the trusted manifest.

## 6. Trust boundary and non-scored diagnostic

**What the evidence does and does not cover:**
- E3.1 trusts:
  - `cases/TRUSTED_MANIFEST.json`, whose anchors come from E0's committed regen receipt and E3's frozen
    fixtures;
  - its own verifier and reference code;
  - the pinned upstream and generator.
- `evidence/diagnostics_nonscored.json`: a verifier whose `native()` and `reference()` are replaced with canned
  store-reading answers promotes V5. This is **expected**: an adversary who controls the verifier code defeats
  the check.
- PASS means only that the frozen attacks are detected under the frozen trust boundary. It is not a
  tamper-proofing or security claim.
- Independent recomputation checks the lab formula on the pinned data. It does not check that the data or the
  simulated approvals are genuine.

## 7. Limitations

- One synthetic estate; three positive clauses and one missing-fact clause; 28 adversarial cases written by the
  same orchestrator who wrote E0–E3. The test is mechanistic, not blind.
- Applicability means inclusive date windows only. There is no supersession, no conflicting documents and no
  time zones beyond UTC dates.
- The approval still selects a reading **by id**. E3.1 detects a rewritten reading by comparing the reading's
  meaning hash with the trusted manifest, not through the approval object. Binding approvals to content hashes
  would be the cleaner fix and is left to a later design step.
- **Cost:** every promotion needs a full rebuild of the estate plus native runs (about 1.5 minutes here). Caching
  across runs is deliberately not trusted.
- The fresh guards are computed on the estate that is being checked. Here that is either the trusted rebuild or
  a declared disposable control. A production system would need its own estate-identity anchoring.
- No Windows run; the PowerShell commands are UNTESTED. The repository has no CI.
