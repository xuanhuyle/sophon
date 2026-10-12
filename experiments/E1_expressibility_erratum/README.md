# E1 expressibility erratum

**Verdict: CONFIRMED_E1_ERRATUM** (DECISION.md).

This is a chronological erratum to E1 (draft PR #5). It is stacked after E2 (draft PR #6) because the E0 → E1 → E2
PRs are unmerged drafts. It is a retrospective replication, not a blind experiment. E0, E1 and E2 files are
unchanged.

Read in this order:
1. `PRIOR.md`
2. `PROTOCOL.md` (frozen at `6068e25`, plus `FREEZE_MANIFEST.txt`; amendments at the end)
3. `ERRATUM.md`
4. `DECISION.md`

## Layout

| Path | What |
|---|---|
| `src/run_erratum.py` | the reproduction: G1 identity, the native queries N0/N1/N2/NW/NL/NV/ND/LD and compiled SQL, oracle, G5 guards, G6 anti-vacuity, capability check |
| `src/oracle_b1.py` | independent B1 oracle (stdlib, raw CSVs only) |
| `src/controls.py` | G7 negative and boundary controls on disposable warehouse copies (`runs/controls/`, ignored) |
| `src/capability.py` | pattern-specific four-class check (not a planner) |
| `src/gate.py` | mechanical verdict |
| `tests/` | capability-check tests and exact-arithmetic checks of the proof |
| `evidence/` | all receipts, native rows, compiled SQL, oracle, guards, anti-vacuity, controls, gate, pytest log; `run1_sql_truncated/` = the first run (Amendment 1) |

The native code reuses the E0 adapter (`mf_adapter.py`) and E1's `native_query_with_where`, imported
unmodified. One gap: the adapter has no `--where` with `--explain`, so `run_erratum.explain_with_where` calls
the adapter's own `_run` with the same argument shape.

## Commands actually run (Linux, bash, from `experiments/E1_expressibility_erratum`)

```bash
# setup: pinned upstream, locked environment, E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# (protocol frozen and pushed here)

.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_capability.py
.upstream/.venv/bin/python src/run_erratum.py --upstream .upstream --out evidence   # run 1, then re-run after Amendment 1
.upstream/.venv/bin/python src/controls.py --upstream .upstream --out evidence/controls
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
python3 src/gate.py --evidence evidence
```

The DuckDB warehouse file is not byte-reproducible across rebuilds. Every compared value is.

## Windows PowerShell — UNTESTED

These commands were not executed on Windows.

```powershell
cd experiments\E1_expressibility_erratum
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
Push-Location .upstream; uv sync --frozen; Pop-Location
.\.upstream\.venv\Scripts\python.exe ..\E0_native_adapter\src\run_e0.py --regen --upstream .upstream --out runs\e0_rebuild
.\.upstream\.venv\Scripts\python.exe src\run_erratum.py --upstream .upstream --out evidence
.\.upstream\.venv\Scripts\python.exe src\controls.py --upstream .upstream --out evidence\controls
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\ | Tee-Object evidence\pytest.log
python src\gate.py --evidence evidence
```
