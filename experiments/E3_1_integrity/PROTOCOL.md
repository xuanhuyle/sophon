# E3.1: protocol (frozen after reproducing the E3 defects, before any corrected logic exists)

Frozen 2026-10-12 on `experiment/e3-1-integrity-2026-10-12`, which was created from E3's head `5130518`.

**Freeze commit contents:**
- `PRIOR.md` and this file;
- `cases/CASES.json` (28 cases with expected outcomes);
- `cases/TRUSTED_MANIFEST.json`;
- `src/{candidates,build_cases,reproduce_e3_defects}.py`;
- `evidence/reproduction/`.

Their hashes and the freeze SHA go in `FREEZE_MANIFEST.txt`, committed next.

**Not yet written at freeze time:** the corrected wrapper, the fresh verifier, the gate and the tests. Deviations
go under "Amendments". Frozen cases, expectations, anchors and gates never change.

## 1. Hypothesis

A thin wrapper around E3's **unmodified** validator achieves both of the following:
- it adds date applicability on the effective-time axis, separately from knowledge time;
- for every would-be promotion, it requires a fresh native MetricFlow execution and a fresh raw-CSV reference
  calculation, anchored only in `TRUSTED_MANIFEST.json`, and checks that the candidate receipts agree with them.

With those two additions, all 28 frozen cases get their expected status, with zero false VERIFIED, while the
clean positives still verify.

## 2. Trust boundary (LAB)

**Trusted** (pinned before any candidate is checked, in `cases/TRUSTED_MANIFEST.json`):
- the upstream commit;
- env-freeze, semantic-manifest and raw-CSV sha256 values, taken from **E0's committed regen receipt**, not
  from any candidate;
- the governing source file hash;
- the *meaning* hash of each approved reading in E3's frozen records. This is the reading without its evidence
  pointers `native_receipt_id`, `oracle_id` and `guard_receipt_id`;
- the reference function for each approved reading (erratum `oracle_b1`, E2 `e2_oracle`);
- the guard code (erratum `run_erratum.guards`);
- the sha256 of every reused code file;
- the expected reference values (E3 `ORACLE_EXPECTED`);
- the verifier code itself, and the pinned generator and dbt project.

**Untrusted (candidate):**
- the IR record's verification request;
- every native, guard and oracle receipt;
- the evidence pointers inside a reading.

**Outside the threat model:**
- an attacker who replaces the trusted manifest, the verifier or reference code, the pinned upstream or the
  generator;
- whether the raw data or the lab approvals are genuine.

PASS does not mean tamper-proof.

## 3. Statuses and precedence (E3.1 output; computed, never input)

In order of precedence:

1. `STRUCTURALLY_INVALID`: any E3 structural error other than SOURCE_NOT_YET_KNOWN.
2. `NOT_KNOWN_AT_EVALUATION_TIME`: the only structural error is SOURCE_NOT_YET_KNOWN. The source is not known at
   `eval_known_at`.
3. `REQUIREMENT_NOT_IN_FORCE`: the requirement is well-formed and known, but `eval_effective_at` falls outside
   [`effective_from`, `effective_to`], **inclusive** on both ends; a null `effective_to` means no end. Uncovered
   atoms and the meaning state are still reported.
4. `MISSING_REQUIRED_FACT`, `MEANING_UNRESOLVED`, `NOT_VERIFIED`, as in E3.
5. `VERIFIED_FOR_LAB_ASSUMPTIONS_AND_FRESH_CHECKS`: only when all of the following hold:
   - E3's validator would promote the candidate;
   - the requirement is in force;
   - every fresh check in §4 passes.

**Separate machine-readable states** for every case:
- `known_at_eval_time`;
- `applicable_at_effective_date`;
- `approved_lab_meaning`;
- `technically_executable` (candidate);
- `fresh_reexecution_succeeded`;
- `fresh_reference_agreement`;
- `candidate_agrees_with_fresh`;
- the status, reasons, `trust_boundary` and the E3 (old) result.

## 4. Fresh verification (only for would-be promotions that are in force)

The verifier runs in its **own process**:

**V-a. Fresh rebuild.**
1. Delete the warehouse and run E0's `run_e0.py --regen` on E3.1's pinned upstream checkout.
2. Check the upstream commit and clean state, env freeze, semantic manifest and raw-CSV hashes against the
   trusted manifest. A mismatch gives FRESH_BUILD_ANCHOR_MISMATCH and nothing is promoted.
3. The control estate `CONTROL_NEGATIVE_QUANTITY` is a disposable copy of this fresh warehouse. The
   lowest-id completed line with unit price > 100 and the lowest-id completed line with unit price < 100 are set
   to quantity −1, with revenue = q × u.

**V-b. Anchor checks** on the candidate:

| Reason | Condition |
|---|---|
| TRUST_ANCHOR_MISMATCH | The record's `verification_request` manifest or CSV hashes, the selected native receipt's fingerprint manifest or CSV hashes, the oracle receipt's raw CSV hashes, or the record's governing-source hash differ from the trusted manifest. |
| UNTRUSTED_READING_CONTENT | The meaning hash of the selected reading ≠ the trusted approved meaning hash for (record, reading id). |

**V-c. Fresh native.** Execute the **trusted** reading's `native_query` with genuine `mf`, through E1's wrapper
over the E0 adapter, on the case's estate. If the runtime or execution fails → FRESH_RUNTIME_UNAVAILABLE.

**V-d. Fresh reference.** Verify the sha256 of the reference code against the manifest, then call the trusted
function on the freshly regenerated raw CSVs, whose hashes are equal to the anchors. If the code hash differs or
execution fails → FRESH_REFERENCE_UNAVAILABLE.

**V-e. Fresh guards.** For a DERIVED binding, run the erratum guards on the case's estate. Any failed guard →
FRESH_GUARD_FAILED.

**V-f. Comparisons:**

| Reason | Condition |
|---|---|
| FRESH_NATIVE_REFERENCE_MISMATCH | fresh native ≠ fresh reference |
| CANDIDATE_NATIVE_DISAGREES_WITH_FRESH | candidate native rows ≠ fresh native (per year, Decimal) |
| CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH | candidate oracle values ≠ fresh reference |

Any V-b to V-f reason → `NOT_VERIFIED`.

**Controls built into the verifier, selected by a case's `fresh_conditions`:**
- `runtime: UNAVAILABLE` points the verifier at a nonexistent `mf` executable.
- `reference_code: TAMPERED` points it at a disposable copy of `e2_oracle.py` with one appended comment line, so
  its hash differs.

## 5. Cases (`cases/CASES.json`; 13 temporal, 15 evidence)

Defaults: `eval_known_at` = 2026-10-06T00:00Z (after approvals); `eval_effective_at` = 2026-06-30.

**Temporal cases:**

| Case | Setup | Expected |
|---|---|---|
| T1 | `effective_from` 2027-01-01 | NOT_IN_FORCE |
| T2 | `effective_from` = evaluation date | VERIFIED |
| T3 | `effective_to` = evaluation date | VERIFIED |
| T4 | `effective_to` one day before | NOT_IN_FORCE |
| T5 | source not yet known | NOT_KNOWN |
| T6 | approval known later | MEANING_UNRESOLVED, not mentioned |
| T7A / T7B | retroactive rule at effective date 2024-06-30, as known before / after its observation | NOT_KNOWN / VERIFIED |
| T8 | approval in force, requirement ended | NOT_IN_FORCE |
| T9 | in force, no approval | MEANING_UNRESOLVED |
| T10 | corrupt source hash and not in force | STRUCTURALLY_INVALID (precedence) |
| T11 | S4 missing fact and not in force | NOT_IN_FORCE, uncovered kept |
| T12 | S3 approved equivalence, not in force | NOT_IN_FORCE |

**Evidence cases:**

| Case | Setup | Expected |
|---|---|---|
| V1 / V2 / V3 | clean S1 / S2 customer / S3 | VERIFIED with fresh values equal to the trusted expected values |
| V4 | S4 status proxy | MISSING |
| V5 | **F-FORGE** store-reading pair | NOT_VERIFIED; the fresh customer values must differ from the forged store values |
| V5B | one-cent consistent forgery | NOT_VERIFIED |
| V6 | single tampered receipt | NOT_VERIFIED |
| V7A / V7B | consistent fake semantic / raw-data revision | NOT_VERIFIED |
| V7C | stale receipt revision | NOT_VERIFIED |
| V8A / V8B | runtime / reference unavailable | NOT_VERIFIED |
| V9A | negative-quantity estate with forged guards and amounts | NOT_VERIFIED, FRESH_GUARD_FAILED |
| V9B | negative-quantity estate, honest receipts | NOT_VERIFIED |
| V10 | approved reading content swapped | NOT_VERIFIED |

## 6. Gate (mechanical, `src/gate.py`; exactly one verdict)

| Criterion | Condition |
|---|---|
| G0 | F-TIME and F-FORGE reproduced on unmodified E3 (`evidence/reproduction/e3_defect_reproduction.json`, frozen). |
| G1 | Each of the 28 cases has its expected status and every expected reason, uncovered set and no-mention condition. For expected-VERIFIED cases with `fresh_values`, the fresh native equals the trusted expected values. For V5, the fresh customer values ≠ the forged values. |
| G2 | Zero promotions among cases not expected VERIFIED. |
| G3 | The fresh rebuild's anchors equal the trusted manifest. Every VERIFIED case rests on a fresh native run (exit 0) and a fresh reference computed in the same verifier process. |
| G4 | A second, independent verifier process (its own rebuild, `env -i`, temporary cwd) gives identical normalized case results: status, reasons, states and fresh values. Run ids, timestamps and warehouse hashes are excluded. |
| G5 | `git diff 5130518 -- experiments/E0_native_adapter experiments/E1_predicate_binding experiments/E2_blind_discovery experiments/E1_expressibility_erratum experiments/E3_formal_ir` is empty. |
| G6 | E3.1 unit tests pass (applicability boundaries and wrapper precedence). |

**Verdict mapping:**

| Verdict | Condition |
|---|---|
| BLOCKED | the fresh runtime or reference cannot run for the clean positives after one repair, or G0 fails |
| INCONCLUSIVE | fresh-build anchors ≠ trusted, or freeze integrity broken |
| FAIL_UNSAFE_INTEGRITY | G2 fails |
| PASS_INTEGRITY_HARDENING | G0–G6 all hold |
| PARTIAL_INTEGRITY_HARDENING | otherwise |

## Amendments

Added after the freeze. The frozen bytes are `PROTOCOL.md` at `e0bf06f` (sha256 in `FREEZE_MANIFEST.txt`). No
case, expectation, anchor or gate changed.

1. **Replay environment.** The replay's child process gets `PATH` and a temporary `HOME` only. `uv`, `git` and
   dbt need a `PATH`, and dbt and uv need a writable `HOME`. In every other respect this is the specified
   `env -i`, with `python -I` and a temporary cwd.
2. **`gate.py` skips `PROTOCOL.md`** when re-hashing `FREEZE_MANIFEST.txt`, because of these amendments. Every
   other frozen file is re-hashed and matches.
3. **Code written after the freeze, as planned:**
   - `src/e31.py`, `src/fresh_verifier.py` and `src/gate.py`;
   - `src/replay.py`;
   - `tests/test_e31.py`;
   - `src/diagnostic_trust_boundary.py`, a non-scored diagnostic required by the prompt's "security boundary"
     note.
4. **Reporting caveat found after the scored run:** in V10 the state `approved_lab_meaning` is `true`, because it
   carries E3's view that an approval selects `R_CUSTOMER_COUNTRY` by id. The rewritten reading content is caught
   separately, as UNTRUSTED_READING_CONTENT, and the status is NOT_VERIFIED. The flag was left unchanged.
