# E5: results

- Freeze `2edac2b`: protocol, amendment source/approval/IR, binding, baseline, controls, packet, oracle,
  reference and scenarios. `FREEZE_MANIFEST.txt` is in `8cd27dc`, pushed before the transposer existed.
- Post-freeze code `8bcbcf3`.
- Labels: **OBSERVED**, **INFERRED**, **ASSUMED**.
- Sources are LAB_AUTHORED and approvals LAB_SIMULATED. The data is synthetic upstream data plus one controlled
  fixture (BOUNDARY120). The metrics are lab-added (E4 M6B / M2).

## 1. Verdict

**PASS_FORWARD_TRANSPOSITION_SIGNAL** (mechanical, `evidence/gate.json`):
- G0–G11 are all true;
- no scenario failures;
- every unsafe condition is false.

## 2. The generated native change (OBSERVED, `evidence/run/generated/`, `evidence/run/transposer/main/`)

**Input.** The transposer ran in a fresh temporary directory that held only `transposer.py`, the packet and a
launcher. Invocation: `/usr/bin/python3 -I`, environment `PATH` + temporary `HOME`. An audit hook logged every
opened file.
- **Files opened:** `packet.json`, `transposer.py`, `proposal.json` and Python stdlib `.pyc` files. **No repository
  file.**
- **Run facts:** 0.05 s, exit 0, no model, 0 paid calls.
- **Hashes:** packet sha256 `b82a0e8e…` = frozen; transposer sha256 `6f9bbc98…`.

**Delta it computed from the two approved IR versions:**
- `unit_price_threshold`: `PREDICATE_VALUE_CHANGE`, fact kind `order_line_charged_unit_price`, `GE`, **`100` →
  `120`**, unit `CURRENCY_PER_UNIT`, grain `ORDER_LINE`;
- source spans "charged unit price is at least 100" → "… at least 120".

**Edit it emitted.** One `replace` op on the existing `premium_completed_revenue` block in `_metrics.yml`; patch
sha256 `bbc5a6b1…`:

```diff
   - name: premium_completed_revenue
-    description: "Completed revenue on lines with unit price at least 100."
+    description: "Completed revenue on lines with unit price at least 120."
     label: "Premium completed revenue"
     type: simple
     type_params:
       measure: revenue
-    filter: "{{ Dimension('sales__status') }} = 'completed' AND {{ Dimension('sales__unit_price') }} >= 100"
+    filter: "{{ Dimension('sales__status') }} = 'completed' AND {{ Dimension('sales__unit_price') }} >= 120"
```

The diff header reads `pristine/…`. That is E4 `apply_patch`'s label: the diff is against the **baseline** file,
since the op is applied after the baseline ops.

**How the edit was produced:**
1. The filter and description were rendered from each IR version through the fixed binding (predicate template,
   operator map, literal style, description template).
2. The transposer first checked that rendering **v1** reproduces the baseline block exactly. It then substituted
   the **v2** rendering.
3. Metric set unchanged; `french_market_revenue` NOT_AFFECTED. Rationale: it implements series S2, not S1, and
   its bound predicates use `customer_country` and `order_status_label`, not the changed fact kind.
4. The proposal records:
   - `review_status: PROPOSED_NOT_DEPLOYED`, `deployment: null`, reviewer decision `PENDING`;
   - both versions' IR and meaning hashes, source hashes, observed/effective times and approvals.

**Native result of the generated revision** (genuine `mf`, rebuilt stack):
- semantic manifest `fd26cecd…` (baseline `3532b0e6…`);
- compiled SQL `WHERE sales__status = 'completed' AND sales__unit_price >= 120`.

**Anti-tautology (non-scored sensitivity; G1).**
- The transposer source contains no `120` literal, and no `REFERENCE`, `SCENARIOS` or `oracle` name.
- On packet copies with the threshold re-approved at `135` and at `99.5`, it emitted `>= 135` and `>= 99.5`.
- With the IR value written `120.00` it emitted `>= 120`.

## 3. Approval and temporal evidence (OBSERVED, `results.json#authority`)

| Version | Source | Observed | Approval (LAB_SIMULATED) | Approval known | Effective |
|---|---|---|---|---|---|
| P1_v1 | LAB-REV-POLICY `20263fa5…` [S1 v1] | 2026-10-01T09:00Z | AP_S1_READ (E3, bound to reading R_SINGLE) | 2026-10-05T10:00Z | 2024-01-01 → |
| P1_v2 | LAB-REV-POLICY-AMD-1 `de6ed7dc…` [S1 v2] | 2026-10-09T09:00Z | AP_S1_V2 (bound to source sha, clause v2 and normalized-claim sha `9fa3bd2e…`) | 2026-10-10T10:00Z | 2025-01-01 →, supersedes v1 from 2025-01-01 |

**v1 is also confirmed through E4's unmodified step A:**
- the E3 validator selects R_SINGLE;
- the E3.1 trusted reading meaning matches;
- the E5 atoms equal E3 S1's atoms.

**Version states and governing versions:**

| Knowledge time | P1_v1 | P1_v2 | Governs 2024 | Governs 2025-01-01 and later |
|---|---|---|---|---|
| K_PRE 2026-10-06 | LAB_APPROVED | **NOT_KNOWN** | v1 | v1 |
| K_MID 2026-10-09T12:00 | LAB_APPROVED | **NOT_APPROVED** | v1 | v1 |
| K_POST 2026-10-11 | LAB_APPROVED | LAB_APPROVED | **v1** (2024-12-31 → v1) | **v2** (2025-01-01 → v2) |

## 4. Scored checks: native candidate vs independent oracle (OBSERVED, `evidence/run/results.json`)

Window AMD = order dates ≥ 2025-01-01. The candidate is executed natively, by year and at line grain. Format:
2025 / 2026 totals, with line counts in parentheses.

| Check | K | Candidate | Against | PINNED | BOUNDARY120 | Status |
|---|---|---|---|---|---|---|
| F1 | PRE | generated (≥120) | requested v2 | native ran; equals v2 oracle | same | **NOT_VERIFIED** (REQUIREMENT_VERSION_NOT_KNOWN) |
| F1 | PRE | generated | governing = v1 | 1 384 728.90 / 746 528.40 vs v1 1 400 232.75 / 752 191.54; 69 lines missing | 71 lines missing | **NONCONFORMING** |
| F1B | MID | generated | requested v2 | native ran | native ran | **NOT_VERIFIED** (REQUIREMENT_VERSION_NOT_APPROVED) |
| **F2** | POST | **baseline (≥100)** | governing = **v2** | 1 400 232.75 / 752 191.54 (1903) vs 1 384 728.90 / 746 528.40 (1834) | 1 401 292.74 / 752 191.54 vs 1 385 328.92 / 746 528.40 | **NONCONFORMING** |
| **F4** | POST | **generated** | governing = **v2** | equal (1834 lines) | equal (1836 lines) | **VERIFIED_FOR_LAB_CHECKS** |
| N2A | POST | `>= 119` | v2 | +10 lines | +11 lines | **NONCONFORMING** |
| N2B | POST | `> 120` | v2 | **CONFORMS (accidental: no 120.00 line)** | −1 line | **NONCONFORMING** |
| N2C | POST | `!= 'cancelled'` | v2 | +244 lines | +245 lines | **NONCONFORMING** |

**Boundary counterexamples (OBSERVED, `evidence/run/counterexamples.json`)**, each with the source facts:

| Check | Snapshot | Line | Order | Date | Status | Qty | Unit price | Expected | Native |
|---|---|---|---|---|---|---|---|---|---|
| F2 (≥100 vs v2) | BOUNDARY120 | 15 | 6 | 2025-07-29 | completed | 1 | **100.00** | excluded | included, 100.00 |
| F2 | BOUNDARY120 | 21 | 8 | 2025-06-04 | completed | 3 | **119.99** | excluded | included, 359.97 |
| F2 | PINNED | 169 | 66 | 2025-09-26 | completed | 4 | 112.62 | excluded | included, 450.48 |
| N2A (≥119) | BOUNDARY120 | 21 | 8 | 2025-06-04 | completed | 3 | **119.99** | excluded | included |
| N2A | PINNED | 454 | 174 | 2025-11-02 | completed | 1 | 119.28 | excluded | included |
| N2B (>120) | BOUNDARY120 | **22** | 9 | 2025-04-23 | completed | 3 | **120.00** | included, 360.00 | **excluded** |
| N2C | both | 16 | 7 | 2025-04-07 | **returned** | 3 | 630.92 | excluded | included, 1 892.76 |
| F1 (≥120 vs v1 at K_PRE) | BOUNDARY120 | 15, 21 | | | completed | | 100.00, 119.99 | included | excluded |

**Before/after P1** (native = oracle wherever conformance is reported):

| | 2024 | 2025 | 2026 |
|---|---|---|---|
| Baseline (v1 revision), PINNED | 1 634 542.08 | 1 400 232.75 | 752 191.54 |
| Generated (v2 revision), PINNED, all dates | 1 615 473.58 | 1 384 728.90 | 746 528.40 |
| Independent v2 oracle, AMD window, PINNED | — | 1 384 728.90 | 746 528.40 |

## 5. Historical continuity (F5, OBSERVED, `evidence/run/routing.json`)

This is **HISTORICAL_VERSION_ROUTING**: explicit selection of two separately preserved native revisions by a
`metric_time__day` window. It is not a bitemporal capability of MetricFlow.

| Routing | Segment | Version → revision | PINNED | BOUNDARY120 |
|---|---|---|---|---|
| K_POST | 2024-01-01 → 2025-01-01 | v1 → BASELINE | 2024 = **1 634 542.08**, CONFORMS | 1 635 322.04, CONFORMS |
| K_POST | 2025-01-01 → | v2 → GENERATED | 1 384 728.90 / 746 528.40, CONFORMS | 1 385 328.92 / 746 528.40, CONFORMS |
| K_PRE | 2024-01-01 → | v1 → BASELINE (v2 absent) | 1 634 542.08 / 1 400 232.75 / 752 191.54, CONFORMS | CONFORMS |

- **Combined results** equal the frozen `ROUTED@K_POST` and `ROUTED@K_PRE` references (by year and line-membership
  hash) on both snapshots. PINNED K_POST has 3 236 lines.
- **2024 is preserved** at E4's v1 value 1 634 542.08.
- **The naive alternative is wrong.** Querying the generated metric alone over all dates gives 2024 =
  **1 615 473.58** (2024 rows silently re-evaluated under v2). The gate records this as
  `naive_single_revision_rewrites_2024: true`.

## 6. Unrelated metric P2 (F6 / N3, OBSERVED, `evidence/run/p2_before_after.json`)

| | Baseline → generated (F6) | Baseline → N3 collateral |
|---|---|---|
| P2 YAML block (parsed) | identical | changed (`AND sales__unit_price >= 120` added) |
| P2 manifest node (metadata excluded) | identical | changed |
| Native P2 by year and lines, PINNED | identical: 310 780.14 / 261 972.06 / 155 221.02 | 294 969.89 / 244 220.96 / 146 856.83 |
| After vs independent P2 oracle | CONFORMS (PINNED and BOUNDARY120) | MISMATCH: 248 / 247 expected lines missing, e.g. line 2 (France, 44.06) and line 3 (France, 99.25) |
| Status | **P2_UNCHANGED_VERIFIED** | **P2_CHANGED_DETECTED** |

## 7. Refusals and state honesty (OBSERVED)

**N1: all 11 malformed or unauthorized packets were refused, with no patch**, each in its own isolated transposer
run:

| Status | Reasons |
|---|---|
| BLOCKED | SOURCE_HASH_MISMATCH (v1 hash), SOURCE_HASH_MISSING, APPROVAL_MISSING, APPROVAL_MEANING_MISMATCH (approval bound to a threshold-110 claim), APPROVER_NOT_AUTHORIZED (proposer role), PREDECESSOR_MISMATCH, VALUE_NOT_GROUNDED_IN_SOURCE (IR says 125, clause says 120) |
| UNRESOLVED | UNIT_CHANGED, UNSUPPORTED_OPERATOR (`APPROX_GE`), BINDING_MISSING, BASELINE_DOES_NOT_IMPLEMENT_PREDECESSOR (baseline already `>= 110`) |

**F7.** The state is `PROPOSED_VERIFIED_NOT_DEPLOYED`:
- `deployed: false`, deployment authorization `null`, reviewer decision `PENDING`;
- original and proposed manifest sha256 recorded.

**N4.**

| Case | Input | State | Reason |
|---|---|---|---|
| N4A | proposal only | PROPOSED_NOT_DEPLOYED | — |
| N4B | forged `DEPLOYED` claim | PROPOSED_NOT_DEPLOYED | CLAIM_WITHOUT_EVIDENCE |
| N4C | verified proposal | PROPOSED_VERIFIED_NOT_DEPLOYED | NO_DEPLOYMENT_RECEIPT |
| N4D | v2 meaning approval offered as a deployment authorization | PROPOSED_VERIFIED_NOT_DEPLOYED | DEPLOYMENT_AUTHORITY_NOT_RECOGNIZED |

No IMPLEMENTED, DEPLOYED or COMPLIANT state appears anywhere in the outputs.

## 8. Reproduction, integrity and cost

**F8 replay.** A second runner process (`python -I`, `PATH` + temporary `HOME`, temporary cwd):
- re-ran the isolated transposer and rebuilt every snapshot and native stack;
- normalized results were **byte-identical** (sha256 `c26ac856…`), exit 0, 384 s.

**G9 integrity.**
- Every frozen file matches `FREEZE_MANIFEST.txt`. PROTOCOL.md was amended only in its Amendments section.
- E0–E4 directories are unchanged against `d6fe13d`, and no file outside `experiments/E5_forward_transposition/`
  differs.
- **G10:** 14 unit tests passed.

**Cost.**

| Run | Time |
|---|---|
| Scored run | 6 min 55 s wall clock (transposer 0.7 s; native checks 229 s; P2 control 88 s) |
| Replay | 6 min 24 s |
| Development runs | about 7 min |

Builds are local only (dbt/DuckDB/MetricFlow). **No model calls and no paid calls.**

## 9. E4 reuse and adapter disclosure

**Unmodified, imported from E4's files:**
- `checker.Checker.snapshot_eval`: native year and line results vs reference, TOTAL/MEMBERSHIP/AMOUNT mismatch,
  counterexamples with source facts and lineage;
- `candidate_stack.build/execute`: disposable project copy, patch, loader, dbt build/parse, genuine `mf`, compiled
  SQL;
- the E4 step-A `authority()` for P1_v1.

**Replaced by `src/e4_adapter.py`:**
- `__init__` and `registered` (E5 snapshots and REFERENCE);
- `reference` (the E5 oracle by `policy|window`, checked against the frozen E5 reference);
- `stack` (one build per candidate and snapshot, one execution per distinct query; E4 cached a single query per
  stack);
- `evaluate` → `evaluate_check` (E5 versioned authority).

**The E4 checker as a whole did NOT run unchanged.** E4's frozen reference was not used as a v2 authority. No E4
file was edited.

## 10. Limitations

**Engineered hold-out.**
- One researcher authored the amendment, IR, binding, packet, oracle, fixture, negative controls, transposer and
  scorer.
- The transposer was mechanically isolated from the reference, but its author knew the answer.
- The PASS shows the mechanism works on this one planted amendment. It gives no rate, and says nothing about
  independently authored or unseen contracts (R9/E8).

**Narrow transposer.**
- It supports one delta kind, `PREDICATE_VALUE_CHANGE` on a bound atom.
- It renders through binding templates derived from the E4 M6B text, including a description template.
- Anything else is refused, not attempted: atom changes, operator changes, new predicates, metrics without a
  binding.
- This is a tiny deterministic renderer, not language-to-code automation.

**Fixed binding.**
- The fact-kind → dimension binding and the metric ↔ series mapping were taken from E4 (M6B
  NO_MATERIAL_DRIFT, M2 VERIFIED).
- They were **not** separately approved by a LAB steward.

**Discrimination depends on registered snapshots.**
- `> 120` agreed with v2 on PINNED, which has no 120.00 price. Only the BOUNDARY120 fixture (line 22) caught it.
- That fixture was designed by the same author.

**History.**
- The deployed metric is not version-aware. Correct history needs the preserved v1 revision plus explicit routing.
- A single new metric silently rewrites 2024.
- No event store, no persistent audit across process loss (E7).

**Authority.**
- LAB_SIMULATED roles. The approval is bound to content and meaning hashes; there is no identity authentication.
- Interpretation approval ≠ deployment authorization.
- The amendment is a hypothetical retroactive LAB amendment.

**Development runs.** The transposer and the full runner were run during development, after the freeze and
before the scored run. Two runner bugs were fixed (PROTOCOL Amendments 2a/2b).

**Not covered:**
- legal compliance;
- downstream BI or agent consumption;
- production deployment;
- the reverse direction (E6);
- a Windows run (PowerShell UNTESTED);
- CI (the repository has none).
