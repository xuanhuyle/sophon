# E0 — decision

**PASS_NATIVE_RUNTIME.**

Protocol `PROTOCOL.md` (sha256 `6ec07bc3…`, frozen in commit `2328c97`, pushed before execution). Criteria applied as
written; none was changed after results.

| # | Criterion (PROTOCOL §4) | Result |
|---|---|---|
| 1 | Source revision and environment recorded | Met: `312e97ad…`, MIT, `uv sync --frozen`, CPython 3.11.17, metricflow 0.211.0 / dbt-metricflow 0.13.0 / dbt-core 1.11.11 / dbt-duckdb 1.10.1; 28 lineage files hashed |
| 2 | `dbt build` exit 0, zero ERROR; semantic manifest written | Met: PASS 79, WARN 0, ERROR 0, NO-OP 2 (exposures); `dbt parse` exit 0 |
| 3 | Native `mf query` exit 0 with numeric rows from the locked `mf` | Met: 3 rows; entry point equals its distribution RECORD |
| 4 | Identity equals PROTOCOL §2; compiled SQL reads `fact_sales` and filters `completed` | Met: 0 mismatches; SQL reads `"warehouse"."gold"."fact_sales"` with `WHERE sales__status = 'completed'` |
| 5 | Repeat byte-identical with unchanged warehouse; clean regeneration identical | Met: repeat identical; regeneration reproduced identical data CSVs, semantic manifest, compiled SQL and result. Warehouse file bytes differ between builds (disclosed; not part of the result) |
| 6 | Native negative control rejects both invalid inputs; adapter raises | Met: exit 1, no CSV, error names the input, `NativeQueryError` with no rows, for N1 and N2 |
| 7 | Fresh process reproduces the result from the receipt | Met: `evidence/fresh_check.json` `ok: true` |
| — | Cross-check (required to run) | Ran; equal to the native result per year to the cent |

Why not the other statuses: native execution ran without any repair (not BLOCKED); the executable is the
installed MetricFlow entry point, the metric identity matches its source definition and the native result
agrees with an independent recomputation (not FAIL_E0); repeat, fresh-process and clean-rebuild results are
byte-identical (not INCONCLUSIVE).

## What this retires and what it does not

Retires **R1 only**: Sophon can enumerate, inspect and execute an existing, independently authored dbt/MetricFlow
metric through MetricFlow's own CLI on its warehouse rows, with receipts a fresh process can re-check.

It does **not** show: interpretation or binding of any governing requirement; that a typed IR adds value;
independent verification against requirements; that the upstream dashboard or agent ran (only that their source
code calls the same `mf` path and manifest); behaviour on Snowflake, Databricks or a dbt Cloud Semantic Layer
API; behaviour at scale; any customer outcome. The data are synthetic retail rows from a seeded generator.

Technical findings worth carrying forward:

- Native identity is best taken from `target/semantic_manifest.json` (metric → measure → semantic model →
  `node_relation`) joined to `target/manifest.json` for lineage; `mf list metrics` agrees with it.
- The semantic manifest embeds the catalog name derived from the DuckDB file name (`"warehouse"`), so a copy of
  the warehouse must keep the file name `warehouse.duckdb` to be queryable with the same manifest.
- Warehouse-file and dbt-manifest hashes are build identities, not content identities; content reproducibility
  should be anchored on source data hashes, the semantic manifest, compiled SQL and results.
- `mf` returns exit code 1 with a structured message for unknown metrics and dimensions, so callers can rely on
  exit codes and need not parse output to detect rejection.
- Each `mf` invocation costs about 3 s here (process start and manifest load), relevant if later experiments
  run many checks.

## Next step (recommended, not executed)

**E1 — known predicate binding and observability**, as specified in the de-risking plan §5, reusing
`src/mf_adapter.py` against the same pinned upstream and the same metric. Suggested inputs, to be preregistered
separately: one LAB_AUTHORED requirement whose authorized interpretation is "revenue counted only for completed
orders" with a human-supplied binding to `completed_revenue` / `sales__status` (case A, fully observable); the
same kind of requirement needing a predicate the layer does not carry, for example whether an order was paid or
refunded (case B, MISSING_BINDING); and one materially ambiguous clause with no authorized interpretation, for
example whether partial returns count (case C, UNRESOLVED). E1 should not start until this E0 evidence has been
reviewed.
