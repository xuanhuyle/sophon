# E0 — native MetricFlow adapter

**Gate result: PASS_NATIVE_RUNTIME** (see DECISION.md). Retires risk R1 only.

The pre-existing MetricFlow metric `completed_revenue` of
[behramkorkut/Governed-Analytics-Agent](https://github.com/behramkorkut/Governed-Analytics-Agent) at
`312e97ad192dcef02f688e31edc0a08c6cf4345f` (MIT) was enumerated, traced to its native definition and executed
through the native `mf` CLI on the DuckDB rows the upstream pipeline generates. The data are **synthetic**.

Read in order: `PRIOR.md` → `SOURCE_GATE.md` → `PROTOCOL.md` (+ `PROTOCOL.sha256`) → `RESULTS.md` → `DECISION.md`.

## Layout

| Path | What |
|---|---|
| `src/mf_adapter.py` | Thin read-only adapter over `mf` (list, inspect, query, explain, receipts). No metric arithmetic, no fallback values |
| `src/run_e0.py` | Runs the frozen procedure S1–S10 + D1 once and writes `run_receipt.json` |
| `src/verify_evidence.py` | Fresh-process re-check of a receipt (S11) |
| `src/crosscheck.py` | CROSS-CHECK from the raw CSVs with the Python standard library (not semantic execution) |
| `src/source_manifest.py` | Source/environment manifest (hashes of 28 lineage files, runtime versions) |
| `tests/test_e0_adapter.py` | T1–T6: live repeat, invalid input, stub executable, identity drift, row sensitivity, cross-check |
| `evidence/` | Receipts, logs, compiled SQL, query result, semantic manifest copy, fresh check, regeneration, consumer inspection, test log |
| `.upstream/`, `runs/` | Ignored: pinned upstream checkout, its virtualenv, generated CSVs and the DuckDB warehouse |

## Commands actually run (Linux, bash, from `experiments/E0_native_adapter`)

Requirements: git, [uv](https://docs.astral.sh/uv/) (0.11.32 used), CPython 3.11 (3.11.17 used), network access to
GitHub and PyPI for the first step only.

```bash
# 1. pinned upstream + its locked environment (upstream CI path)
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python src/source_manifest.py --upstream .upstream --out evidence/SOURCE_MANIFEST.json

# 2. the frozen procedure: generate data, load bronze, dbt build, dbt parse, mf list, identity,
#    mf query + --explain, repeat, negative control, cross-check, direct execution of the compiled SQL
.upstream/.venv/bin/python src/run_e0.py --upstream .upstream --out evidence/run

# 3. fresh-process re-check of the recorded receipt (re-runs the recorded argv with subprocess)
.upstream/.venv/bin/python src/verify_evidence.py --upstream .upstream \
    --receipt evidence/run/run_receipt.json --out evidence/fresh_check.json

# 4. clean regeneration in a second empty checkout
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git runs/regen/.upstream
git -C runs/regen/.upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd runs/regen/.upstream && uv sync --frozen --python /usr/bin/python3.11)
runs/regen/.upstream/.venv/bin/python src/run_e0.py --regen --upstream runs/regen/.upstream --out evidence/regen

# 5. adapter tests (need the warehouse built by step 2)
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e0_adapter.py
```

The native query without the adapter, for anyone who wants to check MetricFlow directly:

```bash
cd .upstream/dbt/retail_dwh
DBT_PROFILES_DIR="$PWD" WAREHOUSE_DB="$PWD/../../data/warehouse.duckdb" \
  ../../.venv/bin/mf query --metrics completed_revenue --group-by metric_time__year --order metric_time__year
```

Expected output (synthetic data, seed 42): 2024 → 1707052.80, 2025 → 1477833.96, 2026 → 792441.45.

## Windows PowerShell (NOT executed in this run)

No Windows machine was available. These are the equivalent commands; they have not been tested. The adapter
resolves `.venv\Scripts\mf.exe` and `python.exe` on Windows, but test T3 writes a POSIX shell stub and will need a
`.cmd` stub there. The upstream's own Makefile is bash-only.

```powershell
cd experiments\E0_native_adapter
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
Push-Location .upstream; uv sync --frozen --python 3.11; Pop-Location
.\.upstream\.venv\Scripts\python.exe src\run_e0.py --upstream .upstream --out evidence\run
.\.upstream\.venv\Scripts\python.exe src\verify_evidence.py --upstream .upstream --receipt evidence\run\run_receipt.json --out evidence\fresh_check.json
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_e0_adapter.py

# direct native query
Push-Location .upstream\dbt\retail_dwh
$env:DBT_PROFILES_DIR = (Get-Location).Path
$env:WAREHOUSE_DB = (Resolve-Path ..\..\data\warehouse.duckdb).Path
..\..\.venv\Scripts\mf.exe query --metrics completed_revenue --group-by metric_time__year --order metric_time__year
Pop-Location
```

## Replaying from a fresh clone of this branch

Run steps 1–3. `src/verify_evidence.py` compares file hashes against the committed receipt; the DuckDB file and
dbt manifest bytes differ between independent builds (RESULTS.md §5), so on a new build use step 4's comparison
instead: CSV hashes, semantic-manifest hash, compiled SQL and the query CSV must be byte-identical to
`evidence/run/`.
