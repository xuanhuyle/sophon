# E5: protocol (frozen before the transposer exists and before any scored run)

**Branch:** `experiment/e5-forward-transposition-2026-10-12`, from E4's head `d6fe13d` (PR #10).

**Freeze commit contents:**
- `PRIOR.md` and this file;
- `REFERENCE.json`, `SCENARIOS.json` and `TRANSPOSE_PACKET.json`;
- `sources/`, `ir/`, `approvals/`, `candidates/`, `controls/`, `fixtures/reference_lines/`;
- `src/{claim,snapshots,oracle,build_inputs,build_packet,build_reference}.py`;
- `evidence/prefreeze_feasibility/`.

Their sha256 values and the freeze SHA go in `FREEZE_MANIFEST.txt`, in the next commit.

**Written only after the freeze:**
- the transposer and its isolated launcher;
- the versioned authority/temporal check;
- the E4 adapter;
- the lifecycle-state function;
- the runner, scorer/gate, replay and tests.

Deviations go under "Amendments". Frozen expectations never change.

## 1. Question

Given one explicitly LAB-approved amendment (P1 v2: unit-price threshold `>= 100` → `>= 120` for order dates from
2025-01-01) and the existing executable native metric that implements P1 v1, does a small, separate,
deterministic transposer:
1. **propose** the correct minimal in-place MetricFlow edit;
2. **from the approved IR delta and the fixed binding alone**;
3. while leaving P2 untouched, refusing malformed or unauthorized inputs, and claiming no deployment?

And can independent native execution against an independent oracle substantiate all of that, with history kept
correct?

## 2. Frozen inputs

### 2.1 Requirement versions (`ir/`, E5-IR-0.1, LAB_AUTHORED)

**P1_v1** restates E3 record S1 (requirement atoms copied verbatim):
- source `LAB-REV-POLICY`, sha `20263fa5…`, `[S1 v1]`;
- observed 2026-10-01T09:00Z, effective from 2024-01-01;
- approval `AP_S1_READ` (E3, LAB_SIMULATED, known 2026-10-05T10:00Z), bound to the reading `R_SINGLE`;
- E3.1 trusted reading meaning `cc1af11b…`.

**P1_v2** is new:
- source `LAB-REV-POLICY-AMD-1` (`sources/LAB_REVENUE_POLICY_AMENDMENT_1.md`, sha `de6ed7dc…`), `[S1 v2]`;
- observed 2026-10-09T09:00Z, effective from 2025-01-01;
- `supersedes` P1_v1 (with v1's IR sha256) for order dates from 2025-01-01;
- it differs from v1 only in the `unit_price_threshold` atom value (`100` → `120`) and its source span.

**`ir/NATIVE_BINDING.json`** is the fixed binding, LAB_AUTHORED from E4 M6B and M2:
- **metrics:** `premium_completed_revenue` implements series S1; `french_market_revenue` implements series S2
  (reading `R_CUSTOMER_COUNTRY`);
- **fact kinds to dimensions:** `order_status_label` → `sales__status`, `order_line_charged_unit_price` →
  `sales__unit_price`, `customer_country` → `customer__country`;
- **rendering:** the operator rendering, literal styles, predicate template and description template;
- **supported delta kinds:** `PREDICATE_VALUE_CHANGE` only.

### 2.2 Approval of v2 (`approvals/AP_S1_V2.json`, LAB_SIMULATED)

- **Role:** `LAB_REVENUE_POLICY_OWNER` (from the E3 roster).
- **Known at:** 2026-10-10T10:00Z.
- **Effective from:** 2025-01-01.
- **Scope:** `source_id`, `document_id`, the source sha256, clause `S1` and clause version 2.
- **Claim:** the `normalized_claim_sha256` of P1_v2 (§2.3) together with the normalized claim itself.
- It authorizes the LAB meaning only. **It is not a deployment authorization.**
- E3's v1 source and approval are not modified.

### 2.3 Normalized claim (`src/claim.py`)

The claim is the canonical JSON of:
- the series, clause id and clause version;
- the effective window;
- the supersession (version id and from-date);
- every atom's `atom_id`, `kind`, `fact_kind`, `op`, `value` (numeric values in canonical plain decimal form),
  `unit`, `aggregation`, `period` and `grain`.

Its meaning hash is the sha256 of that JSON. **An approval counts for a version only if its claim hash equals the
version's recomputed meaning hash.**

### 2.4 Native baseline (`candidates/BASELINE.json`; revision `REV_P1_V1_BASELINE`)

- It is the E4 M6B patch (expose `sales__unit_price`; metric `premium_completed_revenue` with
  `status = 'completed' AND unit_price >= 100`) plus the E4 M2 patch (metric `french_market_revenue`).
- Both metrics are lab-added.
- Baseline semantic manifest `3532b0e6…`.

### 2.5 `TRANSPOSE_PACKET.json` (the transposer's only input)

**It contains:**
- both IR versions;
- both source texts with their sha256;
- `AP_S1_READ` and `AP_S1_V2`;
- the authorized role spec;
- the binding;
- the baseline `_metrics.yml` text, its sha256, the baseline semantic-manifest sha256 and catalog (metric and
  dimension names);
- the patch constraints: only `_metrics.yml` may change; the edit is in place on an existing metric; the anchor
  must be unique; no metric may be added or removed.

**It contains no oracle result, reference value, expected outcome or scoring data.**

It is an **engineered hold-out packet**: the same researcher authored it and the reference.

### 2.6 Snapshots (`src/snapshots.py`)

- **PINNED:** the E0 anchors.
- **BOUNDARY120:** ten exact edits to PINNED, listed in `REFERENCE.json`.

| Year | Status | Line | Edited unit price |
|---|---|---|---|
| 2025 | completed | 2 | 99.99 |
| 2025 | completed | 15 | 100.00 |
| 2025 | completed | 21 | 119.99 |
| 2025 | completed | 22 | 120.00 |
| 2025 | completed | 27 | 120.01 |
| 2024 | completed | 58 | 100.00 |
| 2024 | completed | 60 | 119.99 |
| 2025 | returned | 19 | 120.00 |
| 2025 | cancelled | 11 | 120.01 |
| 2024 | returned | 9 | 100.00 |

### 2.7 Oracle and reference (`src/oracle.py`, `REFERENCE.json`)

- The oracle is new code: stdlib Decimal over the raw CSVs, re-implementing the pinned staging normalisations.
- It hardcodes P1v1 `>= 100`, P1v2 `>= 120` and P2 customer France, as read by the reference author from the
  clause texts.
- **It does not read the IR, the packet or any candidate.**
- Its results are frozen with full line membership: the windows ALL, `<2025-01-01` and `>=2025-01-01`, and
  `ROUTED@K_POST` / `ROUTED@K_PRE`, on both snapshots.
- **Cross-check:** P1v1 ALL and P2 ALL on PINNED equal E4's frozen reference (by year and line hash).
- **Discriminating rows on BOUNDARY120:**

| Distinction | Lines |
|---|---|
| v1 vs v2 | 15, 21 (+69 more) |
| `>= 119` vs `>= 120` | 21 (+10) |
| `> 120` vs `>= 120` | 22 only |
| non-cancelled vs completed | returned line 19 (+244) |

### 2.8 Knowledge times and windows (`SCENARIOS.json`)

| Name | Knowledge time | Meaning |
|---|---|---|
| K_PRE | 2026-10-06T00:00Z | before the amendment is observed |
| K_MID | 2026-10-09T12:00Z | observed, approval not yet known |
| K_POST | 2026-10-11T00:00Z | after approval |

| Window | Order dates |
|---|---|
| HIST | < 2025-01-01 |
| AMD | ≥ 2025-01-01 |
| ALL | all |

## 3. Version selection rule (implemented after the freeze in `src/authority.py`; testable)

**Version state at knowledge time K:**

| State | Condition |
|---|---|
| NOT_KNOWN | the source `observed_at` is after K |
| NOT_APPROVED | observed, but no valid approval with `known_at` ≤ K |
| APPROVAL_INVALID | the approval exists but fails its checks (see below) |
| LAB_APPROVED | otherwise |

**Approval validity checks:**
- the role is authorized for the series' source and is not a never-approver;
- the scope matches the document id, source sha256 (recomputed from the file), clause id and version;
- for v2, the claim hash equals the recomputed meaning hash;
- `known_at` ≥ the source `observed_at`.

For P1_v1, LAB_APPROVED additionally requires **both**:
- E4's unmodified step-A path (the E3 validator on S1 with `AP_S1_READ`, plus E3.1 `in_force` and the trusted
  reading meaning) returns no refusal;
- the E5 P1_v1 atoms equal E3 S1's atoms.

**Governing version for order date D at K:**
1. Take the LAB_APPROVED versions whose effective window contains D, and whose approval's effective window
   contains D.
2. Remove any version superseded by another candidate whose `for_order_dates_from` ≤ D.
3. Exactly one must remain; zero → `NO_GOVERNING_VERSION`; more than one → `AMBIGUOUS`.

For a window, the governing version must be the same on every date of the window. It is checked at the window
start and at every effective or supersession date inside it. Otherwise the result is `WINDOW_SPANS_VERSIONS`.

**HISTORICAL_VERSION_ROUTING.**
- Split the data range from the earliest effective date at every governing-version change.
- Map each segment's version to a native revision from a declared registry.
- Execute that revision natively, restricted to the segment by a `metric_time__day` `where`.
- Verify each segment against the oracle.
- Combine the segments.

This is explicit version routing over separately preserved native revisions. **It is not a native bitemporal
capability of MetricFlow.**

## 4. Transposer contract (`src/transposer.py`, written after the freeze)

**Isolation.**
- Run by `src/run_transposer.py` in a fresh temporary directory containing only a copy of the transposer and of the
  packet.
- Command: `python3 -I`, with environment `PATH` plus a temporary `HOME`.
- An audit hook records every opened path. **No repository path may be opened.**
- The invocation, stdout/stderr, open log and output are saved.

**Checks.** Failures in the first group give **BLOCKED**, in the second **UNRESOLVED**; either way there is no
patch.

*Provenance and authority (BLOCKED):*

| Reason | Condition |
|---|---|
| SOURCE_HASH_MISSING / SOURCE_HASH_MISMATCH | each version's source sha256 is missing, or differs from the packet text |
| CLAUSE_NOT_IN_SOURCE | the clause `[S1 vN] text` is not in its source |
| SPAN_MISMATCH | an atom span ≠ its text |
| VALUE_NOT_GROUNDED_IN_SOURCE | a changed atom value does not occur in its span text |
| APPROVAL_MISSING / APPROVAL_SCOPE_MISMATCH | the approval is missing, or its scope does not match source, sha, clause and version |
| APPROVAL_MEANING_MISMATCH | v2's claim hash ≠ the transposer's own recomputation |
| APPROVER_NOT_AUTHORIZED | the approval's role is not authorized |
| PREDECESSOR_MISMATCH | v2 `supersedes` names v1 with v1's IR sha256, and it does not match |

*Semantics and binding (UNRESOLVED):*

| Reason | Condition |
|---|---|
| UNSUPPORTED_DELTA | the delta between v1 and v2 is not only a predicate value change: atoms added or removed, or fact kind, grain or operator changed |
| UNIT_CHANGED | the threshold unit changed |
| UNSUPPORTED_OPERATOR | the operator is not in the binding |
| BINDING_MISSING | a fact kind has no binding, or the bound dimension is not in the catalog |
| BINDING_UNIT_MISMATCH | the bound dimension's unit differs |
| BASELINE_DOES_NOT_IMPLEMENT_PREDECESSOR | the baseline metric's filter and description ≠ the v1 rendering |
| ANCHOR_NOT_UNIQUE | the anchor occurs other than exactly once |

**Rendering.** The filter is the conjunction (in atom order) of the bound predicate templates. The description
comes from the binding template. Both are rendered from the IR. The transposer must reproduce the baseline from
v1 before rendering v2.

**Output** (`proposal.json`):
- impacted and modified metrics, and NOT_AFFECTED metrics with a rationale;
- the clause-level delta;
- one `replace` patch op on the P1 metric block (unique anchor);
- old and new IR ids, sha256 and meaning hashes;
- observed and effective times, approval provenance;
- the baseline revision, file sha256 before and after, and the semantic-manifest sha256 before;
- `review_status: PROPOSED_NOT_DEPLOYED`, `deployment: null`, `reviewer_decision: PENDING`;
- `refusals`.

**No literal answer in the code.** The transposer source contains no threshold literal of the answer and never
reads files other than the packet.

## 5. Verification (adapter, after the freeze)

**`src/e4_adapter.py` subclasses E4's `checker.Checker`:**
- E4's `snapshot_eval` runs **unmodified from E4's file**: native year and line results, `TOTAL/MEMBERSHIP/AMOUNT_MISMATCH`
  and counterexamples.
- The adapter replaces:
  - `__init__` (E5 reference and snapshots);
  - `registered` (E5 snapshots);
  - `reference` (the E5 oracle by `policy|window`, checked against the frozen `REFERENCE.json`);
  - `stack` (one build per candidate and snapshot; one `mf` execution per query, so that windowed queries do not
    reuse another query's cached result; builds still use E4's unmodified `candidate_stack.build`/`execute`);
  - `evaluate` (E5 versioned authority instead of E4's hardcoded P1 ≥ 100 / E3-v1 step A).
- **E4 files are not edited. The E4 checker is NOT claimed to have run unchanged.**

**Check status:**

| Status | Condition |
|---|---|
| NOT_VERIFIED / NOT_APPLICABLE | the authority result for the requested version at K and window refuses (REQUIREMENT_VERSION_NOT_KNOWN / NOT_APPROVED / APPROVAL_INVALID / NOT_IN_FORCE) |
| NONCONFORMING_IMPLEMENTATION | otherwise, any MISMATCH snapshot |
| NOT_VERIFIED | otherwise, any NOT_VERIFIED snapshot |
| VERIFIED_FOR_LAB_CHECKS | otherwise |

Native execution happens in every case and is recorded.

**GENERATED** = BASELINE patch followed by the proposal's patch ops.

**P2 control (F6/N3):**
- the P2 YAML block text;
- the P2 node of the semantic manifest (`metadata` excluded);
- native P2 by-year and line results before vs after;
- the "after" stack against the P2 oracle.

Any difference gives `P2_CHANGED_DETECTED`, with row counterexamples.

**Lifecycle (`src/lifecycle.py`):**
- the states are `CHANGE_REQUIRED_NOT_PROPOSED`, `PROPOSED_NOT_DEPLOYED`, `PROPOSED_VERIFIED_NOT_DEPLOYED` and
  `PROPOSAL_REJECTED_BY_VERIFICATION`;
- a claimed state is never an input;
- DEPLOYED would need a deployment receipt and a role with `DEPLOYMENT` authority. **No such role exists in the
  roster, so E5 cannot produce DEPLOYED.**

## 6. Scenarios

All scenarios are in `SCENARIOS.json`, with frozen expectations read only by the scorer:
- F1, F1B, F2, F3, F4, F5, F6, F7 and F8;
- N1 (11 packet mutations), N2A (`>= 119`), N2B (`> 120`), N2C (`!= 'cancelled'`), N3 (P2 collateral) and
  N4A–N4D.

## 7. Gate (`src/gate.py`; mechanical; exactly one verdict)

| Criterion | Condition |
|---|---|
| G0 | E4 committed gate = PASS_INDEPENDENT_VERIFICATION_SIGNAL. The BASELINE builds and P1 and P2 query natively. The oracle equals the frozen REFERENCE. The E4 cross-check is true. |
| G1 | F3 as expected. The transposer opened no repository path. The packet sha equals the frozen value. The transposer source contains no `120` literal and no reference to `REFERENCE`, `SCENARIOS` or `oracle`. Non-scored sensitivity evidence: the same transposer on packet copies with threshold `135` (re-approved) emits `>= 135`, and `120.00` emits `>= 120`. |
| G2 | F1, F1B and F2 as expected (states, governing versions, statuses, counterexample band). |
| G3 | F4 and N2A–N2C as expected. |
| G4 | F5 as expected. |
| G5 | F6 and N3 as expected. |
| G6 | F7 and N4 as expected, and no value in `forbidden_state_values` appears as a state in any output. |
| G7 | All N1 controls as expected. |
| G8 | F8: a fresh process, temporary cwd, minimal env; transposer re-run, all stacks rebuilt; normalized outcomes identical. |
| G9 | Frozen files unchanged (FREEZE_MANIFEST, except an amended PROTOCOL.md). E0–E4 directories unchanged against `d6fe13d`. |
| G10 | Unit tests pass. |
| G11 | Cost log present (wall-clock; no paid calls). |

**Verdict, in precedence order:**

1. **FAIL_UNSAFE_TRANSPOSITION**, if any of the following:
   - the BASELINE is VERIFIED for P1 v2 on AMD;
   - any N2 candidate is VERIFIED;
   - N3 is not detected;
   - any N1 control yields a patch or PROPOSED;
   - GENERATED is VERIFIED against P1_v2 at K_PRE or K_MID;
   - a K_PRE routing includes P1_v2;
   - a K_POST routing assigns P1_v2 to 2024;
   - any forbidden state is produced.
2. **INCONCLUSIVE:** freeze integrity broken, oracle ≠ frozen, packet sha ≠ frozen, or the transposer opened a
   repository path.
3. **BLOCKED:** E4 not PASS, or the BASELINE fails to build or query.
4. **FAIL_NO_TRANSPOSITION:** no proposal on the valid packet, the proposal patch equals a frozen hand-written
   candidate, or the sensitivity check shows the output does not follow the IR threshold.
5. **PASS_FORWARD_TRANSPOSITION_SIGNAL:** G0–G11 all hold.
6. **PARTIAL_FORWARD_TRANSPOSITION_SIGNAL:** otherwise, listing the failed criteria.

A PASS retires **only R6 for one controlled native field-threshold amendment**.

## Amendments

(none yet)
