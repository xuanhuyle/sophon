# E0 — protocol (frozen before execution)

Frozen 2026-10-12 in its own commit on branch `experiment/e0-native-metricflow-2026-10-12`, before any data
generation, dbt command or MetricFlow command was run in this experiment. The commit SHA and this file's
sha256 are recorded in `PROTOCOL.sha256` (written in the same commit) and repeated in RESULTS.md and
DECISION.md. Any later correction is appended under "Amendments" with a date and leaves this text intact.

Governing documents: SOPHON_CHARTER.md v1.1, CLAUDE.md, SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md §5 E0,
Claude_Code_Sophon_E0_Native_Semantic_Adapter_2026-10-12.md. Source and runtime: SOURCE_GATE.md and
`evidence/SOURCE_MANIFEST.json`.

## 1. Hypothesis (one)

H: The pre-existing MetricFlow metric `completed_revenue` of `behramkorkut/Governed-Analytics-Agent` at
`312e97ad192dcef02f688e31edc0a08c6cf4345f` can be enumerated, traced to its native definition and executed
through the native `mf` CLI on the DuckDB warehouse rows the upstream pipeline produces, reproducibly, with
evidence that a fresh process can re-check.

Primary uncertainty: R1 only. No governing source, no LLM, no IR, no amendment, no approval, no audit store.

## 2. Fixed inputs

- Upstream at the pinned revision, cloned into `.upstream/` (ignored). Environment from `uv.lock` via
  `uv sync --frozen`, CPython 3.11.17, package versions as in SOURCE_GATE.md.
- Data from the upstream generator unchanged (seed 42), loaded by the upstream loader into
  `.upstream/data/warehouse.duckdb`. No upstream file is edited. All native commands run with
  `cwd = .upstream/dbt/retail_dwh`, `DBT_PROFILES_DIR = <abs>/.upstream/dbt/retail_dwh`,
  `WAREHOUSE_DB = <abs>/.upstream/data/warehouse.duckdb`, as the upstream Makefile/CI and its own
  `semantic_layer.py` do.
- One metric: `completed_revenue`. Expected native identity, taken from the source YAML before execution:
  name `completed_revenue`; type `simple`; input measure `revenue`; filter template
  `{{ Dimension('sales__status') }} = 'completed'`; measure `revenue` belongs to semantic model `sales`
  (`agg: sum`, `expr: revenue`); semantic model `sales` is defined on dbt model `fact_sales`.

## 3. Procedure (each step recorded with argv, exit code, elapsed time, stdout/stderr sha256 and file hashes)

S1. Generate data (`python scripts/generate_raw_data.py`); record row counts and sha256 of each CSV.
S2. Load bronze (`python -m scripts.load_bronze`); record bronze row counts.
S3. `dbt build`; record exit code, pass/warn/error counts, log.
S4. `dbt parse`; record exit code and sha256 of `target/semantic_manifest.json` and `target/manifest.json`.
S5. Native enumeration: `mf list metrics` and `mf list dimensions --metrics completed_revenue`.
S6. Identity: read `completed_revenue`, its measure and semantic model from the native semantic manifest
    written by S4; compare with §2; trace the semantic model to the dbt node in `target/manifest.json` and its
    upstream dependencies.
S7. **Scored native query Q:**
    `mf query --metrics completed_revenue --group-by metric_time__year --order metric_time__year --csv <file>`.
    Also `--explain` with the same arguments to capture the compiled SQL (compilation evidence only).
S8. Repeat Q identically against unchanged inputs (warehouse sha256 recomputed before and after).
S9. Negative control N, two invocations:
    N1 `mf query --metrics completed_revenue_e0_nonexistent --csv <file>`;
    N2 `mf query --metrics completed_revenue --group-by sales__e0_nonexistent_dimension --csv <file>`.
S10. Independent cross-check X (labelled CROSS-CHECK, not semantic execution): Python standard library only
    (`csv`, `decimal`), reading the raw CSV files from S1 — not DuckDB, not dbt, not MetricFlow. For every
    order line whose order has `lower(strip(status)) == "completed"` and whose `product_id` exists in
    `products.csv`, add `quantity × unit_price` as `Decimal`; group by the year of `order_date`.
S11. Fresh-process re-check F: a separate interpreter process (`src/verify_evidence.py`) with no state from the
    run reads the recorded receipt, recomputes the warehouse and manifest sha256, re-runs Q's argv natively and
    compares the result with the recorded one.
S12. Clean regeneration R: in a second, empty copy of the pinned checkout, run S1–S4 and Q again; compare CSV
    sha256 values and Q's result with the first run.
S13. Consumer inspection: read the upstream's own consumer code to decide whether a BI/AI consumer calls the
    same native metric and catalog. Report SUPPORTED_BY_SOURCE_CODE or NOT_VERIFIED. No new consumer is built,
    no LLM is called, the dashboard is not launched.

Diagnostics (recorded, never part of the gate): D1 execute the compiled SQL from `--explain` directly in DuckDB
read-only and compare with Q; D2 adapter tests (§6).

## 4. Gate criteria (fixed now; not to be changed after results)

**PASS_NATIVE_RUNTIME** iff all hold:

1. Source revision and environment recorded (SOURCE_GATE.md, SOURCE_MANIFEST.json, env freeze).
2. S3 `dbt build` exits 0 with zero ERROR results (warnings allowed and reported) and S4 writes
   `target/semantic_manifest.json`.
3. S7 exits 0 and returns at least one row with a numeric `completed_revenue` value, produced by the native `mf`
   executable of the locked environment.
4. S6 identity matches every field in §2, and the compiled SQL from `--explain` reads the `fact_sales` relation
   and applies a `status = 'completed'` condition.
5. Reproducibility: S8 returns byte-identical CSV output and the warehouse sha256 is unchanged; and S12 either
   reproduces identical CSV sha256 values and an identical Q result, or, if the generator is not byte-
   deterministic, the difference is isolated to the regenerated data (Q and X still agree with each other on
   the regenerated data) and disclosed.
6. Native negative control: N1 and N2 are each rejected by the native client — non-zero exit code, or no CSV
   written — with an error naming the invalid input; and the adapter surfaces both as errors with no rows.
   If `mf` exits 0 while writing no CSV, that counts as rejection and the exit-code behaviour is reported.
7. F succeeds: the fresh process reproduces the identical result from the retained receipt.

**Cross-check X** is required to run. Expected relation: exact equality per year to the cent (revenue is an
integer quantity times a two-decimal price, cast to `decimal(12, 2)`). A mismatch does not by itself fail the
gate, but it must be explained from source code and data; an unexplained mismatch makes the evidence
"contradictory" (see FAIL_E0).

**BLOCKED_NATIVE_RUNTIME:** S3, S4 or S7 cannot run after one focused environment repair (and, only if still
blocked, one disclosed fallback upstream). No SQL, CSV, Publicodes or invented YAML substitutes for native
execution. Exact errors and the smallest suspected blocker are preserved.

**FAIL_E0:** the purported native execution is shown to be a stub or fixture, cannot be associated with the
declared `completed_revenue` definition (criterion 4 fails), or native result and cross-check disagree without
an explanation from code and data.

**INCONCLUSIVE:** provenance cannot be established, or execution is unstable (criterion 5 fails without an
isolated cause) and cannot be reliably attributed.

Exactly one status is reported. A PASS retires R1 only.

## 5. Adapter scope

A thin, read-only Python module (`src/mf_adapter.py`) that: lists metrics through `mf list metrics`; reads one
metric's native identity from `target/semantic_manifest.json` and traces it to `target/manifest.json`; runs
`mf query` (and `--explain`) through the locked environment's `mf` executable; returns rows parsed from the CSV
file MetricFlow wrote, plus a receipt (argv, cwd, env keys, exit code, elapsed, stdout/stderr sha256, compiled
SQL, sha256 of the `mf` entry point, semantic manifest, dbt manifest and warehouse file). It raises on a
non-zero exit code or a missing CSV. It contains no metric arithmetic and no fallback values.

## 6. Adapter tests (diagnostic D2; expected to pass, do not decide the gate)

- T1 live: Q through the adapter twice gives identical rows and receipts with matching fingerprints.
- T2 negative: N1 and N2 through the adapter raise and return no rows.
- T3 anti-stub: pointing the adapter at a stub `mf` that prints a canned CSV is rejected by the executable
  identity check.
- T4 identity drift: a copy of the semantic manifest with the `completed_revenue` filter altered is rejected by
  the identity check against §2.
- T5 row sensitivity: on a disposable copy of the warehouse, raising the quantity of one completed order line by
  1 changes the native result for that line's year by exactly its `unit_price`, and leaves other years equal.
- T6 cross-check: X equals the native result per year.

## 7. Budget and stop

One upstream (fallback only if blocked), one metric, one native query plus its repeat, one negative control (two
invocations), one cross-check, one fresh-process re-check, one clean regeneration. No paid model calls, no
platform provisioning. STOP after E0: E1–E8 and the G1 prompt are not executed.

## 8. Non-claims

A PASS does not show: interpretation, binding or verification of any governing requirement; that the
dashboard or agent actually ran (only what their source code calls); Snowflake/Databricks behaviour (the
upstream has an untested-here Snowflake target); scale; customer value. The data are synthetic.

## Amendments

(none)
