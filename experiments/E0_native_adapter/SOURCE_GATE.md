# E0 — source and runtime gate

Recorded 2026-10-12 on a clean pinned checkout, before any data generation, dbt or MetricFlow command.
Machine-readable copy with the sha256 of 28 lineage files: `evidence/SOURCE_MANIFEST.json`. Installed package
set: `evidence/env_freeze.txt` (sha256 `db0a13e9…`). Install log: `evidence/uv_sync.log`.

## Upstream

| Item | Value |
|---|---|
| Repository | https://github.com/behramkorkut/Governed-Analytics-Agent |
| Revision | `312e97ad192dcef02f688e31edc0a08c6cf4345f` (2026-07-22, Behram Korkut; equals the default-branch HEAD on 2026-10-12) |
| Licence | MIT (`LICENSE` sha256 `693fac34…`). Upstream files are **not vendored** into Sophon; they are cloned at the pinned revision into the ignored `.upstream/` directory |
| Lock | `uv.lock` sha256 `abc18209…`; installed with `uv sync --frozen` (the upstream CI path) |
| Declared Python | 3.11 (`.python-version`); used CPython 3.11.17 |
| CI | `.github/workflows/ci.yml`: `uv sync --frozen` → generate data → load bronze → `dbt build` → `dbt parse` → pytest. No `mf` command is run in CI itself; MetricFlow is exercised by the upstream's integration tests |

## Native runtime as installed (from the lock, not from `requirements.txt`)

| Package | Version |
|---|---|
| dbt-core | 1.11.11 |
| dbt-duckdb | 1.10.1 |
| dbt-adapters | 1.24.5 |
| dbt-metricflow (provides the `mf` CLI) | 0.13.0 |
| metricflow | 0.211.0 |
| dbt-semantic-interfaces | 0.9.0 |
| duckdb | 1.5.4 |

Discrepancy recorded, not repaired: the upstream's `requirements.txt` (an older `uv export`) pins
`dbt-adapters==1.24.2` and `pandas==3.0.3`, while `uv.lock` resolves `dbt-adapters 1.24.5` and `pandas 2.3.3`.
E0 follows the lock, which is what the upstream CI uses. `dbt --version` reports the duckdb plugin as having an
update available; no upgrade was made.

## Semantic layer (pre-existing, independently authored)

- dbt project `dbt/retail_dwh`, DuckDB target `dev` with the warehouse path from `WAREHOUSE_DB`.
- Medallion layers: `bronze` (raw CSV loads) → `silver` views (`stg_*`) → `gold` tables (`fact_sales`,
  `fact_customer_orders`, `dim_*`); `dim_dates` is the declared MetricFlow time spine.
- Semantic models in `models/marts/semantic/_semantic_models.yml` (`sales`, `customers`, `products`, `stores`,
  `customer_orders`) and `models/streaming/_semantic_live.yml` (`sales_live`).
- Metrics: 15 batch metrics in `_metrics.yml` (simple, filtered simple, ratio, derived) and 4 live metrics.

## Selected metric: `completed_revenue`

| Field | Value at the pinned revision |
|---|---|
| Definition file | `dbt/retail_dwh/models/marts/semantic/_metrics.yml` (sha256 `0c9a4a16…`) |
| Type | `simple`, **filtered** |
| Measure | `revenue` (semantic model `sales`, `agg: sum`, `expr: revenue`) |
| Filter | `{{ Dimension('sales__status') }} = 'completed'` |
| Semantic model | `sales`, `model: ref('fact_sales')`, `agg_time_dimension: order_date` (day grain) |
| Physical expression | `fact_sales.revenue = cast(quantity * unit_price as decimal(12, 2))`, one row per order line; `status = lower(trim(orders.status))` from `stg_orders` |
| Lineage | `bronze.order_items` → `stg_order_items`; `bronze.orders` → `stg_orders`; `bronze.products` → `stg_products`; inner joins in `fact_sales.sql` (sha256 `720e1782…`) |
| Downstream consumer in source code | `governed_analytics_agent/reporting.py::kpis()` requests `completed_revenue` through `semantic_layer.run_query`, which shells out to `mf query`; `streamlit_app.py` displays it as the "Completed revenue" KPI. Declared exposures: `governed_dashboard`, `governed_agent` |

Why this metric: it is a declared, pre-existing metric with a filter (so the filter must be applied by the
engine, not just a column sum), it is the headline KPI an existing consumer requests, and its expected value can
be recomputed from the raw CSV rows without dbt or MetricFlow.

## Data classification

**SYNTHETIC.** Produced by `scripts/generate_raw_data.py` (sha256 `a8ddfc67…`) with `random.seed(42)` and
`Faker("fr_FR")` seeded 42: 500 customers, 100 products, 10 stores, 2 200 orders (dates 2024-01-01 to
2026-06-15), 1–4 lines per order, status mix about 82 % completed / 10 % returned / 8 % cancelled. Loaded into
DuckDB schema `bronze` by `scripts/load_bronze.py`. The streaming landing table `bronze.order_events` is created
empty; E0 does not run the streaming producer. These rows are not customer data and are not compliance evidence.

## Build path (from the upstream Makefile/CI), to be run after the protocol commit

```
uv sync --frozen
python scripts/generate_raw_data.py
python -m scripts.load_bronze
dbt build --project-dir dbt/retail_dwh --profiles-dir dbt/retail_dwh
dbt parse --project-dir dbt/retail_dwh --profiles-dir dbt/retail_dwh
(cwd dbt/retail_dwh; env DBT_PROFILES_DIR, WAREHOUSE_DB)  mf list metrics | mf query ... | mf query ... --explain
```

## Gate status before execution

Repository and revision exist; licence permits use; the lock installs cleanly offline-resolvable from PyPI;
pre-existing semantic models and metrics are present in source; a seeded data generator and a DuckDB profile
exist. **Runnable behaviour has not been observed yet** — README claims are not taken as evidence. No fallback
upstream has been needed.
