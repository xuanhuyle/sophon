# E0 — results

Protocol: `PROTOCOL.md`, sha256 `6ec07bc30377a94ea4c829b2ea7de35de660735b2d3b5755bd771b82cb0a05f8`, frozen in commit
`2328c97fead90090da23acfa2695eebec65ff59f` and pushed to the remote at 2026-10-12T05:11:44Z. The first execution
step started at 05:13:43Z. Labels: **OBSERVED** (from a receipt or log), **INFERRED**, **ASSUMED**.

## 1. Receipts

| Step | Command (cwd `<upstream>` or `<upstream>/dbt/retail_dwh` for `mf`) | Exit | Elapsed (s) | Evidence |
|---|---|---|---|---|
| S1 | `python scripts/generate_raw_data.py` | 0 | 0.44 | `evidence/run/logs/S1_generate.log` |
| S2 | `python -m scripts.load_bronze` | 0 | 0.32 | `…/S2_load_bronze.log` |
| S3 | `dbt build --project-dir … --profiles-dir …` | 0 | 10.11 | `…/S3_dbt_build.log`: PASS 79, WARN 0, ERROR 0, SKIP 0, NO-OP 2 (the two declared exposures) |
| S4 | `dbt parse …` | 0 | 3.16 | `…/S4_dbt_parse.log`; `target/semantic_manifest.json` written |
| S5 | `mf list metrics`; `mf list dimensions --metrics completed_revenue` | 0; 0 | 3.57; 3.26 | `run_receipt.json` |
| S7 | `mf query --metrics completed_revenue --group-by metric_time__year --order metric_time__year --csv <csv>` | 0 | 3.24 | `evidence/run/query_result.csv` |
| S7 | same with `--explain` | 0 | 3.46 | `evidence/run/compiled_query.sql` |
| S8 | S7 repeated | 0 | 3.31 | `run_receipt.json` `S8_repeat` |
| S9 | N1 `--metrics completed_revenue_e0_nonexistent`; N2 `--group-by sales__e0_nonexistent_dimension` | 1; 1 | 3.33; 3.13 | `run_receipt.json` `S9_negative` |

All OBSERVED. Whole run 05:13:43Z–05:14:21Z.

## 2. Inputs and fingerprints (OBSERVED)

| File | Rows | sha256 |
|---|---|---|
| customers.csv | 500 | `e570cfec57af94ce…` |
| products.csv | 100 | `3783c0e35d83c571…` |
| stores.csv | 10 | `78d2cbff192a861f…` |
| orders.csv | 2 200 | `be942a616a816158…` |
| order_items.csv | 5 526 | `513de0a77e90c731…` |

Bronze row counts equal the CSV row counts; `bronze.order_events` has 0 rows (streaming lane not used).
Semantic manifest `e8e9bfc7e1188bc3…`; warehouse file `f1405d1ac9bf0931…` (3 420 160 bytes); `mf` entry point
`a73c632ca9ebc756…`, equal to its `dbt_metricflow-0.13.0` RECORD entry. Runtime: metricflow 0.211.0,
dbt-metricflow 0.13.0, dbt-core 1.11.11, dbt-duckdb 1.10.1, dbt-semantic-interfaces 0.9.0, duckdb 1.5.4.

## 3. Native enumeration and identity (OBSERVED)

- `mf list metrics` returned 19 metrics, the same 19 names as the semantic manifest (15 batch + 4 live).
- `mf list dimensions --metrics completed_revenue` returned 13 dimensions, including `sales__status` and
  `metric_time`.
- Native identity of `completed_revenue` from `target/semantic_manifest.json`: type `simple`; measure
  `revenue`; filter `{{ Dimension('sales__status') }} = 'completed'`; semantic model `sales`; measure
  `agg: sum`, `expr: revenue`; `agg_time_dimension: order_date`; relation `"warehouse"."gold"."fact_sales"`;
  dbt node `model.retail_dwh.fact_sales`. **0 mismatches** against the expected identity frozen in PROTOCOL §2.
  Metric definition sha256 `b8378e5a84e60f13…`, semantic model definition sha256 `5ddfb05ba90284df…`.
- Lineage traced through `target/manifest.json`: `fact_sales` ← `stg_order_items`, `stg_orders`,
  `stg_products` ← sources `bronze.order_items`, `bronze.orders`, `bronze.products`, each with file path and
  dbt checksum.
- Compiled SQL from `--explain` (verbatim in `evidence/run/compiled_query.sql`): reads
  `"warehouse"."gold"."fact_sales"`, `WHERE sales__status = 'completed'`, `SUM(revenue)` grouped by
  `DATE_TRUNC('year', order_date)`.

## 4. Native result (OBSERVED)

```
metric_time__year,completed_revenue
2024-01-01 00:00:00,1707052.8
2025-01-01 00:00:00,1477833.96
2026-01-01 00:00:00,792441.45
```

CSV sha256 `bdf143bce004ca7e…`. Total 3 977 328.21 over 4 512 completed order lines of 5 526.

## 5. Reproducibility

| Check | Result |
|---|---|
| S8 repeat, unchanged inputs | CSV byte-identical; warehouse, semantic manifest and dbt manifest sha256 unchanged before and after both queries (OBSERVED) |
| S11 fresh process (`verify_evidence.py`, new interpreter, re-runs the recorded argv with plain `subprocess`) | commit, all fingerprints and the `mf` entry point match; re-run exit 0; CSV byte-identical to the recorded one; fingerprints unchanged afterwards; `ok: true` (OBSERVED, `evidence/fresh_check.json`) |
| S12 clean regeneration in a second empty checkout | all five CSV sha256 values identical; semantic manifest sha256 identical; identity mismatches 0; compiled SQL byte-identical; query CSV byte-identical; cross-check equal (OBSERVED, `evidence/regen/`) |
| S12, files that differ | the DuckDB warehouse file (`b6f022dc…` vs `f1405d1a…`, same size) and `target/manifest.json` differ between the two builds (OBSERVED). INFERRED cause: DuckDB block layout and dbt run metadata (timestamps, invocation id). Consequence: a file hash identifies a build, not its content; a new build is compared by data CSV hashes, semantic manifest, compiled SQL and result |

## 6. Negative control (OBSERVED)

| Case | Native exit | CSV written | MetricFlow message | Adapter |
|---|---|---|---|---|
| N1 invalid metric `completed_revenue_e0_nonexistent` | 1 | no | "The given input does not exactly match any known metrics", lists suggestions, echoes the input | raised `NativeQueryError`, no rows |
| N2 invalid dimension `sales__e0_nonexistent_dimension` | 1 | no | resolution error listing available group-by items, echoes the input, issue location `SimpleMetric('completed_revenue')` | raised `NativeQueryError`, no rows |

## 7. Cross-check and diagnostics

- **S10 CROSS-CHECK** (Python `csv` + `decimal` over the raw CSVs; not DuckDB, dbt or MetricFlow):
  2024 → 1 707 052.80, 2025 → 1 477 833.96, 2026 → 792 441.45; **equal to the native result per year to the
  cent**. 0 orphan order lines, 0 lines with an unknown product. This shows the number MetricFlow returned is
  the filtered sum of the source rows; it is not evidence that MetricFlow executed (that comes from §1 and §5).
- **D1** the compiled SQL executed directly in DuckDB (read-only) returned the same three values.
- **D2 adapter tests**: 7 passed (T2 runs once per invalid input) in 27 s (`evidence/pytest_e0_adapter.log`).
  T3: a stub `mf` that writes a canned CSV is refused by the entry-point identity check before it runs.
  T4: a copy of the semantic manifest with the filter changed to `'returned'` is reported as an identity
  mismatch. T5: on a disposable copy of the warehouse, adding 1 to the quantity of one completed line changed
  that year's native result by exactly its unit price and left the other years unchanged. T6: cross-check
  equals native.

## 8. Downstream consumer (S13)

**SUPPORTED_BY_SOURCE_CODE.** In the upstream at the pinned revision, `reporting.kpis()` requests
`completed_revenue` (with `gross_margin_rate`, `orders`, `active_customers`) through
`semantic_layer.run_query`, which runs the venv's `mf query … --csv` with `cwd` = the dbt project and the same
`DBT_PROFILES_DIR`/`WAREHOUSE_DB` variables; `streamlit_app.py` shows it as the "Completed revenue" KPI; the
agent's catalog is loaded from the same `target/semantic_manifest.json`. Line references:
`evidence/consumer_inspection.md`. **NOT_VERIFIED at runtime**: the dashboard was not launched, the agent was
not called and the upstream's own tests were not run. The consumer's KPI query is ungrouped and multi-metric,
a different query shape from Q over the same metric definition.

## 9. Corrections and deviations (all after the protocol commit; none touched a criterion)

1. `PROTOCOL.md` says `PROTOCOL.sha256` is written "in the same commit". A file cannot name its own commit's
   SHA, so it was committed immediately after, in `1e8a44f`, before any execution. PROTOCOL.md was not edited.
2. After the scored run (S1–S10), `src/run_e0.py` gained a `--regen` flag so S12 would skip the repeat and the
   negative control, as the protocol's budget requires. The S12 receipt was produced with that flag.
3. After S11 and S12, `src/mf_adapter.py` was changed to verify the `mf` entry-point identity **before**
   invoking it rather than after (so a stub never runs). The scored run, S11 and S12 used the earlier order; in
   both versions the identity is checked on every query and recorded in the receipt, and it matched. Tests T1–T6
   ran on the final version.
4. No step failed; no environment repair or fallback upstream was needed. The `requirements.txt` vs `uv.lock`
   version discrepancy (SOURCE_GATE.md) was recorded and not repaired; the lock was used.

## 10. Not attempted or not verified

- Windows PowerShell execution (commands in README.md are untested).
- The upstream's Snowflake target, its streaming lane (`bronze.order_events` empty), its LLM agent, its
  dashboard and its own pytest suite.
- Any query shape beyond Q (for example the consumer's ungrouped multi-metric KPI query).
- Any governing requirement, binding, IR, amendment, approval or audit store (out of scope by protocol).
