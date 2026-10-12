# E4: decision

**PASS_INDEPENDENT_VERIFICATION_SIGNAL.**

The verdict is applied mechanically from PROTOCOL.md §5 (`src/gate.py` → `evidence/gate.json`).

## Why

**Prerequisite.** E3.1 = PASS_INTEGRITY_HARDENING.

**Candidates really ran.** The checker executed each candidate's **own modified dbt/MetricFlow stack** with
genuine `mf`. That includes three semantic-YAML mutations and one dbt staging-model mutation. It compared each
stack, per year and per order line, with a frozen independent raw-CSV reference of the approved LAB meaning.

**Every planted wrong implementation was flagged NONCONFORMING with a source-row counterexample:**

| Variant | Mutation | Counterexample |
|---|---|---|
| M3 | `>` vs `>=` at exactly 100 | line 2 at 100.00, shown only by the controlled boundary fixture; the pinned totals agreed by accident |
| M4 | `!= 'cancelled'` vs `= 'completed'` | returned line 7 |
| M5 | store vs customer country | line 1: customer in France, store in Germany |
| M5B | dbt alias drop | line 45: customer raw `FR` |
| C3 | wrong implementation with a forged claim | the claim is contradicted by execution |

**Correct implementations were accepted:**
- the two baselines → VERIFIED_FOR_LAB_CHECKS;
- the two harmless changes → NO_MATERIAL_DRIFT_FOR_CHECKS. Their semantic-manifest hashes changed, which was
  correctly *not* treated as nonconformance.

**Controls abstained instead of asserting a mismatch or a verification:**

| Control | Result |
|---|---|
| unregistered source snapshot | NOT_VERIFIED |
| missing approval | NOT_VERIFIED |
| requirement not in force | NOT_APPLICABLE |
| broken candidate | NOT_VERIFIED, EXECUTION_FAILURE |
| guard-violating data | NOT_VERIFIED, DATA_GUARD_FAILURE |

**Totals:** 0 false assurances, 0 false alarms, and the fresh-process rerun was identical.

## What it does not show

- A detection rate, since every mutation was planted by the reference's author.
- Coverage beyond the registered snapshots. Without the boundary fixture, M3 would have passed on PINNED.
- Metrics without a line-grain entity.
- Legal compliance or real authority.
- Downstream BI or agent behaviour.
- Robustness against a compromised checker or reference.

## Next experiment (recommended, not executed)

**E5: forward governed change** (plan §5).
- Start on a new branch from this PR's head.
- Introduce one LAB-authored amendment to P1, e.g. a threshold change from 100 to 120 effective from a stated
  date, with a separate simulated approval.
- Have Sophon propose the native semantic edit (the M6B-style metric) in a disposable checkout.
- Then run the **E4 checker unchanged** against the amended approved reference: the new implementation must
  verify, the old one must be flagged against the new version, and an unrelated metric (P2 / `french_market_revenue`)
  must stay unaffected.

E4 supports continuing because it supplies the independent verifier that E5's proposed edits would need.

**STOP: E5–E8 were not started.**
