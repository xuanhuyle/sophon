# E1 — bounded source inventory

Taken 2026-10-12, read-only, before the E1 freeze, on the pinned upstream
`behramkorkut/Governed-Analytics-Agent` @ `312e97ad192dcef02f688e31edc0a08c6cf4345f` rebuilt in the E1 worktree
with E0's locked environment and E0's build path. Machine-readable snapshot: `evidence/inventory_snapshot.json`
(written by `src/inventory.py`), **estate fingerprint `af2fd0215120425aa71c3a2075d2057e227d8f0f50824403c06c899ce17b6566`**,
semantic manifest sha256 `e8e9bfc7e1188bc3eb3f5ac551e8ed5350817af14a5471bdbcdfdca2bc01bd48` (equal to E0's).

## 1. Bounded inspected estate (exact scope)

| Part | Content |
|---|---|
| Raw landing files | `data/raw/{customers,products,stores,orders,order_items}.csv` from `scripts/generate_raw_data.py` (seed 42; sha256 `a8ddfc67…`); headers recorded |
| Warehouse | every relation in `data/warehouse.duckdb` built by the upstream: 20 relations, 155 columns (`bronze` 6 tables incl. the empty streaming table `order_events`; `silver` 6 views; `gold` 7 tables + 1 view) |
| dbt project | 14 models and 6 sources from `target/manifest.json` |
| Semantic catalog | `target/semantic_manifest.json`: 6 semantic models, 19 metrics |
| Native catalog | `mf list dimensions --metrics completed_revenue` (13 dimensions), through the E0 adapter |
| Source code read | generator, bronze loader, `governed_analytics_agent/streaming.py` (event schema and status enum), `_sources.yml`, `_staging.yml`, `_marts.yml`, staging and mart SQL, semantic YAML |

Not inspected and therefore not claimed about: any payment processor, ERP, bank feed, upstream system the synthetic
generator imitates, the Snowflake target, git history before the pin, or any organization's real data. A
NOT_FOUND result means **not found in this estate**, never "does not exist".

## 2. Facts used by LAB-REV-1 (OBSERVED unless marked)

| Fact | Physical location and lineage | Type / constraint evidence | Semantic exposure for `completed_revenue` |
|---|---|---|---|
| Order-line quantity | `bronze.order_items.quantity` (BIGINT) → `silver.stg_order_items.quantity` (`cast … as integer`) → `gold.fact_sales.quantity` (INTEGER) | not_null in source data (5 526 rows) | via measure `quantity_sold` (sum) only; not a dimension |
| Order-line charged unit price | `bronze.order_items.unit_price` (DOUBLE) → `silver.stg_order_items.unit_price` (`cast … as decimal(10, 2)`, `stg_order_items.sql` l.11) → `gold.fact_sales.unit_price` (DECIMAL(10,2), `fact_sales.sql` l.30). Range 11.48–1 083.32; 4 050 of 5 526 lines ≥ 100.00 | `fact_sales.sql` comment: "price actually charged" | **not exposed**: no dimension, measure or entity in any of the 6 semantic models has name or expr `unit_price` (`sales` dims: `order_date`, `channel`, `status`; measures: `revenue`, `cost`, `gross_profit`, `quantity_sold`, `discount`, `order_count`, `customer_count`); not in the native dimension list. `fact_sales_live.unit_price` exists but is also unexposed |
| Order-line amount | `gold.fact_sales.revenue = cast(i.quantity * i.unit_price as decimal(12, 2))` (`fact_sales.sql` l.32), inner joins orders and products | DECIMAL(12,2) | measure `revenue` (semantic model `sales`, agg sum, expr `revenue`); input measure of `completed_revenue` |
| Normalized order status | `bronze.orders.status` (VARCHAR) → `silver.stg_orders.status = lower(trim(status))` (`stg_orders.sql` l.14) → `gold.fact_sales.status` (`fact_sales.sql` l.28) | dbt `accepted_values: [completed, returned, cancelled]` (`_staging.yml` l.45–47); observed orders: completed 1 801, returned 216, cancelled 183; lines: 4 512 / 544 / 470 | dimension `sales__status` (native list: yes); used by the metric's own filter `{{ Dimension('sales__status') }} = 'completed'` |
| Order date | `bronze.orders.order_date` (VARCHAR) → `silver.stg_orders.order_date` (`cast … as date`) → `gold.fact_sales.order_date` (DATE) | dates 2024-01-01 … 2026-06-15 by generator | time dimension `sales__order_date` (day grain), the `sales` model's `agg_time_dimension`, so `metric_time` = order date |
| Sales channel (used only by a mutation) | `bronze.orders.channel` → `stg_orders.channel` → `gold.fact_sales.channel` | accepted_values `[online, in_store]` | dimension `sales__channel` |
| Line cost (used only by a mutation) | `gold.fact_sales.cost_amount = quantity * products.unit_cost` | DECIMAL(12,2) | measure `cost` |
| **Payment settlement confirmation** | **none found.** No column in the 155 warehouse columns or 5 raw CSV headers records payment, capture, clearing, settlement, refund or a processor reference. The only status vocabulary is `completed`/`returned`/`cancelled` (batch generator `STATUSES`; streaming `STATUS_WEIGHTS` "kept in sync with the batch status enum"), which the upstream generates at random as an order lifecycle label, not from any payment event. A text search of the upstream source for pay/settle/clear/capture/refund/invoice/transaction/processor/charge returned only HTTP payloads, process output capture and the "price charged" comment | — | — |

The full column list was read, not only the keyword search; the search is an aid, not the method.

## 3. Lab authority designation (ASSUMED by the experimenter, SIMULATED approval)

For synthetic data, "authoritative" means only *designated by the LAB-REV-1 definition*. The designation is
frozen in `FROZEN_CASES.json` (`authority_registry`):

| Fact kind | Designated fields |
|---|---|
| `order_line_amount` | `gold.fact_sales.revenue` |
| `order_status_label` (normalized) | `gold.fact_sales.status` |
| `order_date` | `gold.fact_sales.order_date` |
| `order_line_charged_unit_price` | `gold.fact_sales.unit_price` |
| `sales_channel` | `gold.fact_sales.channel` |
| `order_line_cost_amount` | `gold.fact_sales.cost_amount` |
| `payment_settlement_confirmation` | **none** (nothing in the estate qualifies; `status = 'completed'` is an order lifecycle label, not a processor confirmation) |

## 4. Consequences fixed before the evaluator exists

- Case A's three predicates are physically present, designated and natively exposed.
- **B1 is genuinely available**: `unit_price` is physically present with full lineage and designated, and the
  executable native catalog does not expose it for `completed_revenue`.
- **B2's settlement fact is not found in the bounded estate.** No credible settlement source exists, so the
  preregistered expectation is NOT_FOUND_IN_BOUNDED_ESTATE, not a manufactured gap.
- Executable identities and fingerprints reused from E0: `mf` entry point `a73c632c…` (RECORD-verified),
  semantic manifest `e8e9bfc7…`, raw CSV sha256 values as in E0 RESULTS §2.
