# Erratum to E1 (PR #5): native expressibility is not only direct dimensions

**Verdict: CONFIRMED_E1_ERRATUM** (DECISION.md).

- Protocol frozen at `6068e25`; manifest at `bc8bc00`.
- This is a retrospective replication of a discrepancy that E2 had already reported. It is not a blind
  experiment.
- Labels: **OBSERVED** (measured here), **INFERRED** (reasoned from observations), **ASSUMED** (taken without
  test).
- The data is synthetic. E1's files are byte-identical; E1 is **not** re-scored.

## 1. What was reproduced (OBSERVED, `evidence/`)

| Item | Value |
|---|---|
| Source identity (G1) | upstream `312e97ad`, env freeze `db0a13e9…`, semantic manifest `e8e9bfc7…` and five CSV hashes, all equal to E0. `completed_revenue` equals E0 (1 707 052.80 / 1 477 833.96 / 792 441.45). |
| Native witness (NW) | `mf query --metrics revenue --group-by metric_time__year --where "{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }} AND {{ Dimension('sales__status') }} = 'completed'"`. Exit 0; the `--where` text is byte-equal to E2's. |
| NW result | **2024 1 634 542.08 · 2025 1 400 232.75 · 2026 752 191.54** |
| Independent oracle | stdlib Decimal over raw `orders.csv` / `order_items.csv` / `products.csv`, no warehouse, no native output: **2024 1 634 542.08 · 2025 1 400 232.75 · 2026 752 191.54** (equal to the cent) |
| Line grain (NL) | `--group-by sales` with the same filter returns **3 305** lines. The oracle has **3 305** B1 lines. The id sets and every per-line amount are identical. |
| Variant (NV, non-gating) | `completed_revenue` with only the metric filter gives the same three values. |
| Compiled SQL (`evidence/native/NW_compiled.sql`) | One CTE over `gold.fact_sales`. Two subqueries `SUM(__revenue)` and `SUM(__quantity_sold)` are each `GROUP BY sales` (= `sales_id`) and LEFT JOINed on `sales`. The outer `WHERE sales__revenue >= 100 * sales__quantity_sold AND sales__status = 'completed'` comes before the yearly `SUM(revenue)`. |
| Comparison types | `SUM(revenue)` is DECIMAL(38,2); `100 * SUM(quantity)` is HUGEINT; there are no FLOAT or DOUBLE tokens in the SQL. |
| Baselines | unfiltered `revenue`: 2 083 998.02 / 1 866 567.68 / 944 513.09. Status only: 1 707 052.80 / 1 477 833.96 / 792 441.45. Witness: strictly smaller than both in every year. |
| Anti-vacuity | Order 1 contains line 2 (completed, u = 44.06, q = 3) and line 1 (completed, u = 368.30, q = 3). Line 2 is **excluded** natively; line 1 is **included**. The filter therefore acts per line, not per order. |
| Direct exposure | `Dimension('sales__unit_price') >= 100` is rejected by MetricFlow (exit 1, "does not match any of the available group-by-items"). `mf list dimensions --metrics revenue` lists 13 dimensions, none of them `unit_price`. |

## 2. Why the derivation is valid here, and only here

**Claim (INFERRED, proof).** Take a line with integer quantity `q`, a unit price `u` with at most two decimals,
and revenue `r` with `r = q·u` exactly. Then:

`r ≥ 100·q ⇔ q·(u − 100) ≥ 0`.

If `q > 0`, this is equivalent to `u ≥ 100`.

`Metric('revenue', group_by=['sales'])` evaluated for a line is the SUM over rows sharing that `sales_id`. If
`sales_id` is unique, that sum is the line's own `r`; the same holds for `quantity_sold` and `q`. The compiled
comparison uses exact types. So the native filter selects exactly the B1 lines, and the outer yearly SUM is the
B1 amount.

**Guards observed on the pinned rows (G5, `evidence/guards.json`):**

| Guard | What was observed |
|---|---|
| quantity positive | min quantity = 1 in both the CSV and `gold.fact_sales` (5 526 lines; none ≤ 0) |
| revenue exact | `Decimal(revenue) == quantity × Decimal(unit_price)` for all 5 526 rows |
| price source exact | warehouse `unit_price` equals the CSV value on every line; the CSV has at most 2 decimals |
| line entity unique | 5 526 fact rows = 5 526 distinct `sales_id` = 5 526 CSV lines; no orphan order or product |
| exact comparison | DECIMAL vs HUGEINT; no float |

**Why it cannot be authorised universally (G7, disposable warehouse copies, `evidence/controls/controls.json`):**

| Control | Mutation | Native derived filter | Truth (`u ≥ 100` on the copy's rows) | Capability check |
|---|---|---|---|---|
| negative quantity | line 1 (u 368.30) and line 2 (u 44.06) set to q = −1 | 2025 = 1 399 083.79. Line 2 (−44.06) is **admitted**; line 1 is **dropped**. | 2025 = 1 398 759.55. Line 1 (−368.30) is in; line 2 is out. | refuses: `quantity_positive` failed and the native/oracle comparison does not match |
| zero quantity | line 22 (u 77.36; no other ≥ 100 line in its order) set to q = 0 | line 22 **admitted** (0 ≥ 0). Revenue sums unchanged. **`orders` 2025 = 629** | line 22 out; **`orders` 2025 = 628** | refuses |
| near threshold | three lines from separate orders set to q = 3 with u = 99.99 / 100.00 / 100.01 | 99.99 (299.97 < 300) excluded; 100.00 and 100.01 included. Yearly totals, line set and `orders` all equal truth. | same | derivable (guards hold) |

The pinned warehouse hash was unchanged after each control. `tests/test_guard_math.py` checks the proof with
exact arithmetic:
- equivalence for q in 1..5;
- q = 0 admits every price;
- q < 0 reverses the inequality;
- a revenue rounded to whole units would let 99.99 pass.

**Scope (ASSUMED / limits).** Nothing in the semantic layer or the dbt tests enforces `quantity > 0`; dbt has
only `not_null`. The guard holds because the generator draws `randint(1, 5)` and because the rows were
observed. Future loads with zero or negative lines would break the equivalence silently. Returns encoded as
negative lines, a common real-world convention, are one example. The derivation is therefore
**VERIFIED_FOR_RECORDED_CHECKS on this snapshot**. It is not a property of the semantic model.

## 3. Corrected taxonomy (engineering distinctions, not a semantic-logic solver)

| Class | Meaning | Example in E0–E2 |
|---|---|---|
| **DIRECTLY_EXPOSED** | A declared dimension, time dimension or entity resolves to the field for the metric, and a `Dimension(...)` filter on it is natively accepted. | E1 A: `sales__status`, `metric_time` |
| **NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS** | No direct dimension exists. A native filter built from existing semantic objects (here, metric filters at the line entity's grain) is accepted, reproduces an independent oracle, and is proved equivalent under explicit guards that are observed to hold. | **E1 B1** (unit price ≥ 100) on the pinned rows |
| **SOURCE_PRESENT_BUT_UNSUPPORTED_BY_NATIVE_SEMANTICS** | The field exists physically, but there is neither direct exposure nor a proved, guarded native derivation. A failed guard also lands here. | E2 H5, customer e-mail domain. E2 chose it so that no dimension or metric reaches it; this erratum did not re-test that. Also B1 under a negative-quantity estate (G7a). |
| **NOT_FOUND_IN_BOUNDED_ESTATE** | No field for the fact exists in the inspected estate. | E1 B2 settlement, E2 H1 payment |

E1's label `PRESENT_IN_SOURCE_NOT_EXPOSED` merged two different things:
- "direct exposure absent", which is still true for B1;
- "unsupported by native semantics", which is false for B1 on this snapshot.

`src/capability.py` implements the four classes **for this one pattern only**. It returns the derivable class
only if the native filter was accepted, matched the oracle (yearly and per line) and every guard holds.

## 4. Status of E1's conclusions

**Superseded.** The E1 files stay unchanged; these readings no longer hold.

| E1 location | Original statement | Status |
|---|---|---|
| RESULTS.md line 15 | P_UNIT_PRICE_GE_100 → `PRESENT_IN_SOURCE_NOT_EXPOSED` | **Superseded.** The correct class is NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS on the pinned rows. The *observation* in that line, that the `Dimension('sales__unit_price')` probe is rejected with exit 1, is reproduced and remains true. |
| RESULTS.md line 21 | case B1 `PRESENT_IN_SOURCE_NOT_EXPOSED`, "COVERED SUBSET ONLY" | **Superseded** as a case status. The full B1 value is natively obtainable (NW). |
| RESULTS.md §2, B1 diagnostic | "the gap is semantic exposure, not missing data" | **Qualified.** The gap is *direct* exposure only; native expression is possible. |
| DECISION.md line 10 | "B1 correctly classified from real source and catalog evidence" | **Withdrawn.** |
| DECISION.md line 14 | "Not PARTIAL: B1 was genuinely available." | **Withdrawn.** B1 was not a genuine present-but-unexposed contrast case. |
| DECISION.md line 3 | **PASS_KNOWN_BINDING** | **Withdrawn as a substantive verdict.** It was produced mechanically: the observed statuses matched `EXPECTED.json`, and that match is a true historical fact. But the frozen PASS gate (PROTOCOL.md line 112) treats "B1 native probe rejected" as proof of the unexposed contrast, and that premise is false. Under E1's own frozen labels, the closest description is PARTIAL_KNOWN_BINDING, because the intended contrast was not genuinely available (INFERRED; E1 is not re-scored). It is not FAIL: the error was an under-claim, and no false verification occurred. |
| `tests/test_e1_binding.py` test 2 | asserts B1 is `PRESENT_IN_SOURCE_NOT_EXPOSED` | It still passes as a description of the dimension-only evaluator. It encodes the superseded expectation and must not be reused as a correctness oracle. |

**Surviving, unchanged.**
- Case A: bound and directly exposed. The native `completed_revenue` equals the independent oracle to the cent;
  this erratum re-observed it as N0.
- B2 (settlement): `NOT_FOUND_IN_BOUNDED_ESTATE`. Metric filters cannot create a missing field.
- Adversarial variants 4a–4d, 5, 6 and 7, oracle-sanity checks 8a and 8b, replay 9 and diagnostic D10. None of
  them involves unit price exposure.
- No E1 case or variant was falsely verified. E1's error was a conservative false negative.
- The fact that the authority registry drives the classification. The trust limits (lab designation, bounded
  estate, design bias).
- E1's evaluator logic is a correct check of **direct** exposure. It is **incomplete** as an expressibility check.

## 5. Impact on R2 / R3 and on E2

- **R2 (correct binding of known predicates).** E1's binding mechanics survive for directly exposed predicates.
  Any validator must stop equating "no dimension" with "not expressible". It needs the derivable class, plus
  recorded proofs and guards.
- **R3 (honest gaps).** E1 *overstated* a gap. False negatives in expressibility are a real failure mode: they
  cause needless escalation, custom SQL or "not verifiable" reports. Derivable claims bring a new obligation:
  their guards (here `quantity > 0`) are data assumptions that the semantic layer does not enforce. They must be
  recorded, and re-checked whenever the data changes.
- **E2.** Its PARTIAL_DISCOVERY_SIGNAL is unaffected. Its PRIOR.md witness and values are reproduced exactly.
  E2's packet already described metric filters, and E2's H5 was chosen to avoid this pattern.
