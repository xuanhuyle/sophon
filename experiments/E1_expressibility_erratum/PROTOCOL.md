# E1 expressibility erratum: protocol (frozen before the reproduction)

Frozen 2026-10-12 on branch `experiment/e1-expressibility-erratum-2026-10-12`. It was created from
`origin/experiment/e2-blind-discovery-2026-10-12` @ `39491cf`. The freeze commit contains this file and
`PRIOR.md`. Their sha256 and the freeze commit SHA go into `FREEZE_MANIFEST.txt`, committed next.

**Retrospective, not blind.** E2 already reported the expected values. Disclosed facts known before freezing are
listed in PRIOR.md. The scripts under `src/` are written **after** this freeze and implement the specification
below. They may not change a gate, the oracle definition or a threshold. Anything that deviates from this text
goes under "Amendments".

Before the freeze, the only thing run on the rebuilt estate was E0's `run_e0.py --regen`. That run rebuilds the
estate and queries `completed_revenue`. Neither the witness nor the oracle was run in this erratum before the
freeze.

## 1. Expected outcome (stated in advance)

CONFIRMED_E1_ERRATUM. The witness should return the E2-reported values. All lines should have quantity in
1..5. Revenue should equal quantity × unit_price exactly. The derivation should therefore be valid on the pinned
rows but not in general.

## 2. Reused, unmodified

- Pinned upstream `312e97ad192dcef02f688e31edc0a08c6cf4345f` in ignored `.upstream/`, built with:
  - `uv sync --frozen` (env-freeze sha256 `db0a13e9…`);
  - E0's `run_e0.py --regen`.
- E0 adapter `E0_native_adapter/src/mf_adapter.py` (sha256 `8a5f400b22a578f9…`): `open_project`, `explain`,
  `list_dimensions`, `fingerprints`, `mf_identity`.
- E1 `E1_predicate_binding/src/evaluator.py` (`14a083e41171721b…`): `native_query_with_where`.

Neither file is edited. When `--where` must be combined with `--explain`, the erratum calls the adapter's own
`_run` with the same argument shape. It does not monkey-patch anything.

## 3. Native queries (all through the installed `mf`; nothing computed outside MetricFlow is reported as native)

Shorthand:

| Name | Filter text |
|---|---|
| R | `{{ Metric('revenue', group_by=['sales']) }}` |
| Q | `{{ Metric('quantity_sold', group_by=['sales']) }}` |
| S | `{{ Dimension('sales__status') }} = 'completed'` |
| W | `R >= 100 * Q AND S` |

The queries:

| Id | Purpose | Command (`mf query` …) |
|---|---|---|
| N0 | source identity baseline | `--metrics completed_revenue --group-by metric_time__year`, must equal E0 |
| N1 | unfiltered baseline | `--metrics revenue --group-by metric_time__year` |
| N2 | status-only baseline | `--metrics revenue --group-by metric_time__year --where S` |
| **NW** | **witness** | `--metrics revenue --group-by metric_time__year --where W` (the exact E2 text) |
| NW-SQL | compiled SQL | NW plus `--explain` |
| NL | line-grain witness | `--metrics revenue --group-by sales --where W` |
| NV | non-gating variant | `--metrics completed_revenue --group-by metric_time__year --where "R >= 100 * Q"` |
| ND | direct-dimension probe | `--metrics revenue --where "{{ Dimension('sales__unit_price') }} >= 100"`; expected rejected |
| LD | dimension listing | `mf list dimensions --metrics revenue`; `unit_price` must be absent |

## 4. Independent oracle (stdlib only, raw CSVs, no warehouse, no native output)

Read `data/raw/orders.csv`, `order_items.csv` and `products.csv` from the pinned build. Join items to orders on
`order_id`, and require that the product exists. A line is in B1 when:
- `status == 'completed'`;
- `Decimal(unit_price) >= Decimal('100')`.

Its amount is `int(quantity) * Decimal(unit_price)`. Its year is the year of `order_date`. Sum by year and give
the result as two-decimal strings. Also produce the set of B1 `order_item_id`s with each line's amount.

## 5. Gates

| Gate | Requirement |
|---|---|
| **G1** source identity | Upstream commit, env-freeze hash, semantic-manifest sha256 `e8e9bfc7…` and the five CSV sha256 values equal E0. N0 equals E0 (2024 1707052.8, 2025 1477833.96, 2026 792441.45). |
| **G2** native witness runs | NW exits 0 through `mf` with the exact E2 `--where` text, and its receipt records the argv. NW-SQL contains a **line-grain metric subquery for each metric, grouped by the `sales` entity (sales_id)**, and a WHERE comparison between them. |
| **G3** oracle equality | NW per year equals the oracle per year **exactly** (Decimal; the same set of years). |
| **G4** line-grain equality | The `sales` ids returned by NL equal the oracle's B1 id set, and each line's native revenue equals the oracle amount. |
| **G5** guards on pinned data | All five must hold: (a) every order line has `quantity ≥ 1` in both the raw CSV and `gold.fact_sales`; (b) every `fact_sales.revenue` equals `quantity × unit_price` exactly; (c) every `fact_sales.unit_price` equals `Decimal(csv unit_price)`, and every CSV unit price has at most 2 decimal places; (d) `sales_id` is unique and `fact_sales` has as many rows as `order_items.csv` (no line lost or duplicated by joins); (e) the types in NW-SQL's comparison are exact (DECIMAL or integer, not FLOAT or DOUBLE). |
| **G6** anti-vacuity | (a) NW < N2 < N1 strictly for every year. (b) A specific completed line with unit price < 100 (the lowest-id one) is absent from NL. The lowest-id completed line with unit price ≥ 100 is present. (c) ND is rejected (nonzero exit) while NW is accepted. (d) LD lists no `unit_price`. |
| **G7** negative controls, disposable warehouse copy under ignored `runs/` | Each control rewrites `gold.fact_sales` rows consistently (`revenue = quantity × unit_price`) and reruns the native derived filter. Truth means applying `unit_price >= 100` to the copy's rows in Python. (a) **Negative quantity:** one completed line with u ≥ 100 and one with u < 100 get `quantity = −1`. The native derived result must **differ** from truth, and the capability check (§6) must refuse. (b) **Zero quantity:** one completed line with u < 100 gets `quantity = 0`. The native line-grain derived set must **contain** that line, though truth excludes it. Its effect on `orders` (distinct order count) under the derived filter must differ from truth. The capability check must refuse. (c) **Near threshold:** three completed lines get u = 99.99, 100.00 and 100.01 with quantity 3. The native derived filter must include exactly 100.00 and 100.01 and exclude 99.99, equal to truth for the yearly totals and the line set. |
| **G8** capability check | `src/capability.py` (pattern-specific) and its tests pass. On the pinned evidence it returns `NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS`. It returns a non-derivable class whenever a guard fails, the native filter was not accepted, or the native/oracle comparison failed. It returns `DIRECTLY_EXPOSED` if a direct dimension exists. |

## 6. Capability check (specification)

Input: an evidence record with these fields:
- direct dimension present;
- source column present;
- native witness accepted;
- native equals oracle (yearly and line-level);
- guard results G5 (a)–(e).

Output:
- one of DIRECTLY_EXPOSED, NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS,
  SOURCE_PRESENT_BUT_UNSUPPORTED_BY_NATIVE_SEMANTICS or NOT_FOUND_IN_BOUNDED_ESTATE;
- the list of failed guards.

The rules apply in this order:
1. If no source column: NOT_FOUND.
2. If a direct dimension exists: DIRECTLY_EXPOSED.
3. If the native witness was accepted, it matched the oracle and every guard holds: NATIVELY_DERIVABLE.
4. Otherwise: SOURCE_PRESENT_BUT_UNSUPPORTED.

It covers only this pattern. It is not a planner.

## 7. Decision (exactly one)

| Verdict | Condition |
|---|---|
| **CONFIRMED_E1_ERRATUM** | G1–G8 all hold. |
| **NOT_CONFIRMED** | The native runtime works (G1 holds and N1 runs), but G2, G3 or G4 fails, or any G5 guard is **observed false** on the pinned data. E2's claim is then qualified accordingly. |
| **BLOCKED** | The pinned upstream or the native runtime is unavailable after one narrow repair attempt. No SQL-only workaround. |
| **INCONCLUSIVE** | G1 fails (source identity), a guard cannot be evaluated, oracle independence is compromised, or a G6/G7 control does not behave as specified (a broken control cannot certify anything). |

Precedence: BLOCKED, then INCONCLUSIVE (G1 or an unevaluable guard), then NOT_CONFIRMED, then INCONCLUSIVE
(G6/G7/G8 failure), then CONFIRMED.

## 8. Consequences fixed in advance

These apply whatever the verdict.

- E1's files stay byte-identical; E1 is not re-scored.
- If CONFIRMED, ERRATUM.md will:
  - **withdraw** E1 DECISION line 10 ("B1 correctly classified") and line 14 ("Not PARTIAL: B1 was genuinely
    available");
  - **withdraw** E1's PASS_KNOWN_BINDING as a substantive verdict. It was produced mechanically by matching an
    EXPECTED.json whose B1 entry was wrong. The frozen gate itself defined B1 as the unavailable contrast case;
  - list every E1 observation that survives unchanged.
- If NOT_CONFIRMED, the E2 statements are qualified and the E1 B1 classification stands, pending other
  evidence.

## 9. Non-claims

- One pattern on one synthetic estate.
- The guards are data observations plus a generator reading. The semantic layer **does not enforce**
  `quantity > 0`, so the derivation is valid only for data meeting the guards.
- Not a semantic-logic solver.
- Not evidence about other predicates, metrics or estates.

## Amendments

These were added after the freeze. The frozen bytes are `PROTOCOL.md` at commit `6068e25` (sha256 `aeeb2c54…` in
`FREEZE_MANIFEST.txt`). No gate, threshold or oracle definition changed.

1. **Compiled SQL truncated in run 1.**
   - The first reproduction's `--explain` extraction cut at the first `SELECT`, the same way E0's `explain`
     does. That dropped the plan's opening `WITH sma_10002_cte AS (` line.
   - The extraction now starts at the first line beginning with `WITH` or `SELECT`. The whole reproduction was
     re-run.
   - The run-1 file equals the run-2 file minus that header. The run-1 gate summary is identical apart from
     timestamps.
   - Run 1 is kept in `evidence/run1_sql_truncated/`.
2. **How G7 picks its lines** (a refinement that the specification permits):
   - The negative-quantity control uses the lowest-id completed line with u **> 100** (368.30), so that the
     inequality flip is strict.
   - The zero-quantity and near-threshold controls use completed lines whose orders have no line with u ≥ 100.
     That way the `orders` count can only move through the touched line.
3. **G7 guard source.** In a control, `price_source_exact` compares against the copy's own rewritten rows. The
   control simulates an estate whose source carries those values.
4. **The gate was first computed inline, then saved** as `src/gate.py` with the same logic and re-run. The output
   is identical.
