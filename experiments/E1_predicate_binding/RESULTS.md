# E1 — results

Protocol frozen in commit `ee7db720f02131d69b33f2a6c6495ed8e0a9bd93` (PROTOCOL.md sha256 `34557fbf…`; all frozen
file hashes in `FREEZE_MANIFEST.txt`, committed in `502a2a1` and pushed at 2026-10-12T07:07:29Z, before any
evaluator code). Scored run 07:09–07:10Z (`evidence/run/console.log`). Labels: **OBSERVED**, **INFERRED**,
**ASSUMED**. LAB-REV-1 is LAB_AUTHORED with SIMULATED approval; data are synthetic.

## 1. Cases, by predicate (OBSERVED from `evidence/run/case_results.json`)

| Case | Predicate | Lab-designated field (ASSUMED designation) | Present in source | Natively exposed for `completed_revenue` | Predicate status |
|---|---|---|---|---|---|
| A, B1, B2 | P_LINE_AMOUNT | `gold.fact_sales.revenue` (= quantity × unit_price) | yes | measure `revenue` (`sales`, sum), the metric's input measure | BOUND_AND_EXPOSED |
| A, B1, B2 | P_STATUS_COMPLETED | `gold.fact_sales.status` ← `lower(trim(bronze.orders.status))` | yes; `completed` observed | dimension `sales__status`; the metric's own filter `= 'completed'` | BOUND_AND_EXPOSED |
| A, B1, B2 | P_YEAR_BY_ORDER_DATE | `gold.fact_sales.order_date` | yes | time dimension `sales__order_date` = `agg_time_dimension` → `metric_time__year` | BOUND_AND_EXPOSED |
| B1 | P_UNIT_PRICE_GE_100 | `gold.fact_sales.unit_price` | yes (DECIMAL(10,2), lineage to `bronze.order_items.unit_price`) | **no**: not in the native dimension list, no semantic object on `fact_sales` has expr/name `unit_price`; native probe `--where "{{ Dimension('sales__unit_price') }} >= 100.00"` **rejected by MetricFlow (exit 1)**, which names the unresolvable dimension | PRESENT_IN_SOURCE_NOT_EXPOSED |
| B2 | P_SETTLEMENT_CONFIRMED | **none** (nothing in the estate qualifies) | no designated field among 155 warehouse columns / 5 raw CSV headers | — | NOT_FOUND_IN_BOUNDED_ESTATE |

| Case | Case status | Verified for recorded checks | Uncovered predicates | Native result (covered predicates) |
|---|---|---|---|---|
| **A** | **FULLY_OBSERVABLE_FOR_THIS_CALCULATION** | yes | — | 2024 1 707 052.80 · 2025 1 477 833.96 · 2026 792 441.45 |
| **B1** | **PRESENT_IN_SOURCE_NOT_EXPOSED** | no | P_UNIT_PRICE_GE_100 | same three values, labelled COVERED SUBSET ONLY |
| **B2** | **NOT_FOUND_IN_BOUNDED_ESTATE** | no | P_SETTLEMENT_CONFIRMED | same three values, labelled COVERED SUBSET ONLY |

All three equal `EXPECTED.json` (case status, verified flag, every predicate status). **0 deviations.**

## 2. Native result and independent calculation for A (OBSERVED)

- Native: `mf query --metrics completed_revenue --group-by metric_time__year` through the E0 adapter (entry
  point RECORD-verified), exit 0. Live semantic manifest `e8e9bfc7…` (equal to E0 and to the frozen inventory);
  live estate fingerprint equal to the frozen `af2fd021…`.
- Oracle: `src/oracle.py` over the raw CSVs. Its own loop and E0's `crosscheck.compute` agree. Values
  2024 1 707 052.80, 2025 1 477 833.96, 2026 792 441.45. **Native = oracle per year to the cent.**
- E0 reuse: adapter imported unmodified (`git diff a84c855 -- experiments/E0_native_adapter` is empty); E0's
  `run_e0.py --regen` rebuilt the warehouse; E0's crosscheck is part of the oracle for A.
- B1 diagnostic (not native, `evidence/b1_raw_diagnostic.json`): the raw rows *can* compute the B1 amount
  (2024 1 634 542.08, 2025 1 400 232.75, 2026 752 191.54). This shows the gap is semantic exposure, not missing
  data. The evaluator did not treat that computability as verification.

## 3. Adversarial and non-vacuity checks (OBSERVED, `evidence/run/adversarial_results.json`)

| # | Variant | Observed | Expected | Verified? |
|---|---|---|---|---|
| 4a | Status binding removed | INVALID_BINDING (P_STATUS MISSING_BINDING; metric filter not implied by any bound predicate) | same | no |
| 4b | Status bound to existing `sales__channel` / `fact_sales.channel` | INVALID_BINDING (P_STATUS NOT_AUTHORITATIVE_FOR_FACT) | same | no |
| 4c | Line amount bound to existing measure `cost` / `cost_amount` | INVALID_BINDING (P_LINE_AMOUNT NOT_AUTHORITATIVE_FOR_FACT; metric measure `revenue` not bound) | same | no |
| 4d | Status: semantic `sales__channel`, physical `status` (inconsistent) | INVALID_BINDING (`sales__channel` does not resolve to `fact_sales.status`) | same | no |
| 5 | Settlement predicate added to A, no data added | NOT_FOUND_IN_BOUNDED_ESTATE; covered-subset native result **identical** to A's | same | no |
| 6 | `status = 'completed'` proposed as settlement evidence | UNVERIFIED (P_SETTLEMENT NOT_AUTHORITATIVE_FOR_FACT: untrusted proxy, no equivalence rule) | same | no |
| 7 | Disposable dbt project copy, metric filter changed to `'returned'` | INVALID_BINDING; the drifted native query returned 2024 199 946.94 · 2025 240 853.04 · 2026 61 881.95, while A's earlier recorded CSV still showed the completed values | same | no |
| 8a | Native 2025 value +0.01 | comparison rejects (counterexample 2025) | rejects | — |
| 8b | Raw copy, order line 1 (order 1, completed, 2025) quantity 4→5 | oracle 2025 rises by exactly 368.30 = that line's unit price; comparison rejects | rejects | — |
| 9 | Fresh-process replay from recorded evidence | all 11 statuses re-derived equal; all oracle responses recomputed equal from raw CSVs (`evidence/replay.json`) | equal | — |
| 10 | Windows PowerShell | instructions written, **UNTESTED** | — | — |
| D10 | B2 with a wrong frozen estate fingerprint (diagnostic) | INCONCLUSIVE | same | no |

No case or variant other than A reached FULLY_OBSERVABLE. Tests: **16 passed** in 71 s
(`evidence/pytest_e1.log`). The tests re-executed every case and variant live, independently of the recorded
evidence. They include a diagnostic in which removing `status` from the lab registry makes A fail, showing that
the registry, not the case, drives the result.

**Strongest negative control.** MetricFlow returns the same plausible revenue whether or not the requirement
adds "settled by a payment processor" (variant 5). Proposing `status = 'completed'` as that settlement evidence
is refused (variant 6). The semantic layer's `completed` is an order lifecycle label generated at random by the
upstream; it is not a payment-settlement oracle.

## 4. Deviations, limitations and corrections

1. **E0 adapter has no `--where`.** The B1 exposure probe needed one. E1's `native_query_with_where` mirrors
   the adapter's `query()` using the adapter's own identity check, runner and fingerprints, and adds `--where`. It
   calls the adapter's private `_run`. The adapter file is unmodified; a public `where` parameter would be a
   small E0 follow-up.
2. **Plan vs prompt.** The plan's ambiguous case C was deferred, as the E1 prompt instructs (PRIOR.md).
   Ambiguity and missing authority remain untested.
3. **Freeze manifest** is in the commit after the protocol commit, as the protocol states.
4. **Authority is lab designation.** "Authoritative" means listed in the frozen registry by the experimenter.
   The evaluator's correctness is relative to that designation; a wrong designation would propagate.
5. **Bounded estate.** NOT_FOUND means not among the inspected 155 columns and 5 CSV headers of this pinned
   synthetic project. The inventory was done by the experimenter reading the full column list, with a keyword
   search as an aid only.
6. **Design bias.** The experimenter chose the cases knowing the stack. Bindings were supplied, not discovered.
   This is not an independent or enterprise benchmark.
7. **Replay trust.** The offline replay trusts the recorded native responses as captured, with hashes in
   `replay.json`. It proves the statuses follow from that evidence by the frozen procedure, not that the evidence
   is true. Native re-execution is covered by the live test run.
8. No scored result was repaired or re-run after observation. The first run is the scored run.
9. PR #4 (E0) still has no CI checks in this repository; none ran for E1 either.
