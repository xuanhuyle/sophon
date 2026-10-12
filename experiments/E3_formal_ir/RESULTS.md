# E3: results

- Freeze commit `cbb0850` (protocol, prior, fixtures, expected outcomes); `FREEZE_MANIFEST.txt` in `d5b07c5`.
- The validator, models and evidence collector were written after the freeze.
- Labels: **OBSERVED**, **INFERRED**, **ASSUMED**.
- All clauses are LAB_AUTHORED, and all roles, approvals and times are LAB_SIMULATED. The data is synthetic.

## 1. Gate (OBSERVED, `evidence/gate.json`)

| Criterion | Result |
|---|---|
| C0 identity and runtime | Upstream `312e97ad`, env freeze `db0a13e9…`, manifest `e8e9bfc7…` and five CSV hashes are all equal to E0. Every oracle receipt equals the frozen `ORACLE_EXPECTED.json`. The pinned warehouse was unchanged by the copies. All frozen fixture hashes match. |
| C1 | **54/54** scenarios match their frozen expected status and every frozen reason, reading, alternative, uncovered set, executability, oracle-equality and no-mention expectation, on the first scored run. |
| C2 | **0 false VERIFIED.** |
| C3 | The three positive scenarios rest on fresh native receipts on the pinned snapshot (exit 0) that equal the independent oracles. |
| C4 | A naive reader of a plain JSON store promotes 6 of the 7 baseline states; E3 rejects all 6. Five of them rely on invariants E1 lacked or had only partly. |
| C5 | Fresh-process replay (`env -i`, `python -I`, temporary cwd) is byte-identical (sha256 `69065623…`). |
| C6 | `pytest`: 16 passed. |

Mechanical verdict: **PASS_IR_GUARD_VALUE**. Read it together with the post-hoc findings in §6.

## 2. Native evidence (OBSERVED, `evidence/receipts/native/`)

All runs are genuine `mf query` through E1's wrapper over the unmodified E0 adapter.

| Receipt | Query (abridged) | Snapshot | Exit | 2024 / 2025 / 2026 | Independent oracle |
|---|---|---|---|---|---|
| NR_S1 | revenue, status completed AND `Metric(revenue@sales) >= 100 * Metric(quantity_sold@sales)` | pinned | 0 | 1 634 542.08 / 1 400 232.75 / 752 191.54 | equal (erratum `oracle_b1`) |
| NR_S1_NO_QTY | `Metric(revenue@sales) >= 100` (corrupted) | pinned | 0 | 1 695 473.19 / 1 466 247.85 / 787 797.10 | ≠ |
| NR_S1_GRAIN_ORDER | the same derivation at `order` grain (corrupted) | pinned | **1** | — | — |
| NR_S1_NEGQTY | NR_S1 on a copy with lines 1 and 2 at q = −1 | copy | 0 | 1 634 542.08 / **1 399 083.79** / 752 191.54 | ≠ |
| NR_S2_CUSTOMER | revenue, completed, `customer__country = 'France'` | pinned | 0 | 310 780.14 / 261 972.06 / 155 221.02 | equal (E2 oracle) |
| NR_S2_STORE | revenue, completed, `store__store_country = 'France'` | pinned | 0 | 366 057.38 / 288 072.98 / 138 501.23 | equal (E2 oracle) |
| NR_S2_CUSTOMER_VALUE_CHANGED | NR_S2_CUSTOMER on a copy with line 1 revenue +100.00 | copy | 0 | 310 780.14 / **262 072.06** / 155 221.02 | ≠ |
| NR_S3 | orders, online, `customer__country = 'France'` | pinned | 0 | 97 / 98 / 42 | equal (E2 `h6`) |
| NR_S4_PROXY | revenue, status completed (proxy for settlement) | pinned | 0 | 1 707 052.80 / 1 477 833.96 / 792 441.45 | equal (proxy oracle) |
| NR_PROBE_UNIT_PRICE_DIMENSION | `Dimension('sales__unit_price') >= 100` | pinned | **1** | — | — |

Notes:
- **Corrupted order grain (OBSERVED).** MetricFlow 0.211 does not reject it as invalid semantics. It compiles
  SQL that DuckDB rejects ("Parser Error: syntax error at or near ','"). The E3 validator rejects it
  structurally (DERIVATION_GRAIN_INVALID) before any execution matters.
- **Guard receipts (erratum code, unmodified).**
  - GR_S1 (pinned): all five guards true.
  - GR_S1_NEGQTY (copy): `quantity_positive` false (min −1, lines 1 and 2); the other four true.

## 3. Meaning vs computability vs evidence, before and after simulated approvals

**Lab clock.**
- The source is observed at 2026-10-01T09:00Z.
- Approvals are known at 2026-10-05T10:00Z.
- The revocation is known at 2026-10-08T10:00Z.
- The effective date evaluated is 2026-06-30.

| Scenario | Eval known-at | Meaning (computed) | Executable natively | Native = oracle (selected or all readings) | Coverage | **Status** |
|---|---|---|---|---|---|---|
| S1, no approval | 10-06 | PROPOSED_NOT_APPROVED | yes | yes | complete | MEANING_UNRESOLVED |
| S1 + AP_S1_READ | 10-06 | LAB_APPROVED (R_SINGLE); DERIVED binding, guards true on the same snapshot | yes | yes | complete | **VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS** |
| S1 + approval, negative-quantity snapshot | 10-06 | LAB_APPROVED | yes | **no** | complete | NOT_VERIFIED (GUARD_FAILED, NATIVE_ORACLE_MISMATCH) |
| S2, no approval | 10-06 | UNRESOLVED_INTERPRETATION (2 candidates) | yes, both | yes, both | complete | MEANING_UNRESOLVED |
| S2 + AP_S2_CUSTOMER, as of 10-03 | 10-03 | UNRESOLVED (the approval is not yet known, and is not mentioned) | yes, both | yes, both | complete | MEANING_UNRESOLVED |
| S2 + AP_S2_CUSTOMER, as of 10-06 | 10-06 | LAB_APPROVED R_CUSTOMER_COUNTRY; R_STORE_COUNTRY **NOT_SELECTED** (kept, not "false") | yes | yes | complete | **VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS** |
| S2 + both choices | 10-06 | CONFLICTING_APPROVALS | yes | yes | complete | MEANING_UNRESOLVED |
| S3 + reading approval only | 10-06 | reading approved; `customers.country` ≡ residence **NOT_ESTABLISHED_SEMANTIC_EQUIVALENCE** | yes | yes (97/98/42) | complete | MEANING_UNRESOLVED |
| S3 + AP_S3_EQ | 10-06 | equivalence LAB_APPROVED (simulated) | yes | yes | complete | **VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS** |
| S3 + AP_S3_EQ, revocation known | 10-09 | APPROVAL_REVOKED → equivalence unapproved | yes | yes | complete | MEANING_UNRESOLVED |
| S4 + reading approval | 10-06 | LAB_APPROVED | no (no query) | — | **uncovered: settled_by_processor** | MISSING_REQUIRED_FACT |
| S4, status proxy as a DIRECT binding | 10-06 | LAB_APPROVED | yes | **yes** (1 707 052.80…) | uncovered (NOT_DESIGNATED_FOR_FACT) | MISSING_REQUIRED_FACT |
| S4, proxy + simulated equivalence approval (roster-valid steward) | 10-06 | equivalence **REFUSED_SOURCE_ORIGIN_MISMATCH** | yes | yes | uncovered (SOURCE_ORIGIN_MISMATCH, APPROVAL_CANNOT_CREATE_SOURCE) | MISSING_REQUIRED_FACT |

The S2, S3 and S4 rows show the central separation. In these cases the native query executes, and in S4 it
even matches its own oracle, yet no promotion happens without approved meaning and designated provenance.

## 4. All 54 scenarios (OBSERVED, `evidence/validation_results.json`)

| Test | Scenarios | Statuses obtained (all = frozen) |
|---|---|---|
| 1 S1 positive | 2 | VERIFIED; MEANING_UNRESOLVED (INTERPRETATION_NOT_APPROVED) |
| 2 S1 guards / derivation | 6 | missing guard receipt → NOT_VERIFIED GUARD_NOT_EVIDENCED. Guard undeclared, order grain and expression without quantity → STRUCTURALLY_INVALID (REQUIRED_GUARD_UNDECLARED / DERIVATION_GRAIN_INVALID / DERIVATION_QUERY_MISMATCH). Negative-quantity snapshot → NOT_VERIFIED GUARD_FAILED. Guard from another snapshot → NOT_VERIFIED GUARD_SNAPSHOT_MISMATCH. |
| 3 S2 no approval | 1 | MEANING_UNRESOLVED; both readings executed and oracle-equal |
| 4 S2 valid approval | 1 | VERIFIED R_CUSTOMER_COUNTRY; R_STORE_COUNTRY NOT_SELECTED |
| 5 approval attacks | 12 | Wrong clause, wrong version, wrong source hash and nonexistent reading → APPROVAL_SCOPE_MISMATCH. Also CONFLICTING_APPROVALS, APPROVER_NOT_IN_ROSTER, APPROVER_NOT_AUTHORIZED_FOR_CLAIM, SELF_APPROVAL, APPROVAL_BEFORE_SOURCE_OBSERVED and APPROVAL_NOT_EFFECTIVE. A future approval unclaimed → unresolved and not mentioned; claimed → STRUCTURALLY_INVALID APPROVAL_CLAIM_WITHOUT_EVIDENCE. All are non-verified. |
| 6 S3 no equivalence | 1 | MEANING_UNRESOLVED EQUIVALENCE_UNAPPROVED; executable and oracle-equal |
| 7 S3 equivalence | 6 | approved → VERIFIED; before the revocation is known → VERIFIED (revocation not mentioned); revoked → unresolved APPROVAL_REVOKED; removed → unresolved; flag flipped without an approval → STRUCTURALLY_INVALID; wrong steward → unresolved APPROVER_NOT_AUTHORIZED_FOR_CLAIM |
| 8 S4 | 4 | MISSING_REQUIRED_FACT ×3 (REQUIRED_FACT_ABSENT; NOT_DESIGNATED_FOR_FACT; APPROVAL_CANNOT_CREATE_SOURCE). `status: VERIFIED` in the record → STRUCTURALLY_INVALID STATUS_FIELD_FORBIDDEN. |
| 9 structural | 13 | All STRUCTURALLY_INVALID, with the frozen code each: UNIT_MISMATCH, UNKNOWN_SEMANTIC_OBJECT, UNKNOWN_PHYSICAL_FIELD, SEMANTIC_PHYSICAL_MISMATCH, UNDEFINED_PREDICATE, ATOM_UNBOUND, TEMPORAL_ORDER_INVALID, SOURCE_NOT_YET_KNOWN, SOURCE_HASH_MISMATCH, SOURCE_CLAUSE_MISMATCH, SPAN_TEXT_MISMATCH, APPROVAL_CLAIM_WITHOUT_EVIDENCE, SCHEMA_INVALID |
| 10 native / oracle | 6 | All NOT_VERIFIED. Re-hashed tamper → NATIVE_ORACLE_MISMATCH. Unhashed tamper → RECEIPT_INTEGRITY_FAILED. Changed warehouse value → NATIVE_ORACLE_MISMATCH. Other query → RECEIPT_QUERY_MISMATCH. Other reading's oracle → ORACLE_READING_MISMATCH. Wrong semantic revision → RECEIPT_REVISION_MISMATCH. |
| 11 as-of | 2 | Before: unresolved, approval invisible. After: VERIFIED. Both evaluate the identical record (same `record_sha256`). |
| 12 replay | all | byte-identical in a fresh process |

**Imprecision observed: extra, non-frozen reason codes; status unaffected.**
- An undefined-predicate binding also emits REQUIRED_FACT_ABSENT, because the coverage loop iterates over
  bindings that have no atom.
- Unknown or mismatched physical fields also emit NOT_DESIGNATED_FOR_FACT.

These are noise in the reason list, not wrong statuses.

## 5. Comparison with untyped recording and with E1 (OBSERVED, `evidence/untyped_baseline.json`)

The naive reader of a plain JSON note store (json.loads, take a stored status, else "verified if a recorded query
executed and matches a recorded expected value") was given the same documents:

| Case | False state a plain store holds | Naive | E3 | Invariant | Earlier coverage |
|---|---|---|---|---|---|
| U1 | metric executed ⇒ requirement verified (S2, both readings run) | VERIFIED | MEANING_UNRESOLVED | I6 unresolved alternatives | **none** in E1 |
| U2 | approval flag with no approval object | VERIFIED | STRUCTURALLY_INVALID | I1 claims need visible valid approvals | **none** |
| U3 | receipt from another semantic revision | VERIFIED | NOT_VERIFIED | I8 revision binding | **partly**: E1 estate fingerprint (D10) |
| U4 | status proxy executes and matches ⇒ settlement verified | VERIFIED | MISSING_REQUIRED_FACT | I7 designation | **yes**: E1 authority registry (variant 6). E3 adds that an *approved* equivalence still cannot create the source. |
| U5 | approval of clause version 2 used for version 1 | VERIFIED | MEANING_UNRESOLVED | I4 scope | **none** |
| U6 | derived filter on negative-quantity rows | NOT_VERIFIED | NOT_VERIFIED | I8 guards | The naive numeric comparison already catches this snapshot because the numbers change. Not counted. |
| U7 | `status: VERIFIED` written into the record | VERIFIED | STRUCTURALLY_INVALID | I1 computed status | **none** |

Honest scope of the "value added":
- These invariants are enforced by ordinary Pydantic models (162 lines) plus a 435-line validator. Any
  competent schema/validation implementation could enforce them. E3 shows that they **can be made mechanical
  and that they fail when violated**, not that they are novel.
- U4's core protection already existed in E1.

## 6. Post-hoc, NON-SCORED findings (after the scored run; `evidence/diagnostics_nonscored.json`)

1. **Requirement applicability is not enforced.**
   - A copy of S2 with `effective_from = 2027-01-01`, evaluated at effective date 2026-06-30 with a valid
     approval, computes **VERIFIED**.
   - I2 only checks that `effective_to ≥ effective_from`. It never checks that the requirement is in force at
     `eval_effective_at`.
   - In a second variant (evaluation date 2023-06-30) the record was refused only incidentally, through the
     approval's own effective window.
   - This is a real gap, relevant to charter TRACE (temporal applicability). It is outside the preregistered
     scenarios, so the mechanical verdict does not change. It is the first defect to fix. The proposed one-line
     rule, not applied: `if not (effective_from <= eval_effective_at <= effective_to or effective_to is None):
     REQUIREMENT_NOT_IN_FORCE`.
2. **Consistent forgery of receipts.** If both the native receipt and the oracle receipt are rewritten
   consistently (store-reading numbers labelled as customer reading), the validator returns VERIFIED. Receipts
   are trusted committed files; the replay re-validates them but does not re-execute them. Closing this needs a
   trust anchor or live re-execution of promoted cases, which is E4/E7 work.
3. **A revocation by an unauthorised role is ignored:** S3 stays VERIFIED. This is the intended behaviour.

## 7. Deviations

See PROTOCOL.md "Amendments":
- the receipt integrity hash is over canonical rows;
- `gate.py` skips the amended protocol hash;
- two extra output codes/states were added;
- extra post-freeze tests and diagnostics are labelled as such.

There were no changes to fixtures, expectations, oracles or gates. The harness's `apply_patch` contains two
inert lines; behaviour is as specified.

## 8. Limitations

- **Design bias.** Four LAB_AUTHORED clauses and 54 scenarios were written by the same orchestrator who wrote
  the validator, E0–E2 and the erratum. The test is mechanistic, not blind. Expectations were frozen before the
  validator existed, but the author knew the invariants being tested.
- **Lab authority and assumptions.**
  - The roster, approvals and fact registry (field origins, designations, metric units) are lab declarations.
    The validator is only as right as these declarations.
  - Roles stand in for people. Role-equality self-approval detection is not identity verification.
  - Currency is unspecified (ASSUMED).
- **Simulated meaning.** A simulated S3 equivalence approval says nothing about what `customers.country` really
  means. The S2 approval is a lab choice, not a market definition.
- **Snapshot-scoped guards.** The S1 derivation's guards are checked on one snapshot. Nothing re-checks them
  when the data changes; they are recorded as data assumptions (E7).
- **Bounded readings.** Only the two enumerated S2 readings exist; the IR cannot discover others.
- **Not covered:**
  - wrong-but-plausible implementations against an approved spec (E4);
  - transposition (E5);
  - reverse drift (E6);
  - durable history and tamper-proof receipts (E7);
  - authentic requirements (E8).
- No Windows run; the PowerShell commands are UNTESTED. The repository has no CI.
