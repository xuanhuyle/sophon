# E3: minimal formal governance IR

**Verdict: PASS_IR_GUARD_VALUE** (DECISION.md; read it with RESULTS §6).

This is stacked on the E1 expressibility erratum (draft PR #7), which is itself stacked on E2 (#6), E1 (#5) and E0
(#4). Earlier experiment files are unchanged.

Read in this order:
1. `PRIOR.md`
2. `PROTOCOL.md` (frozen at `cbb0850`, plus `FREEZE_MANIFEST.txt`; amendments at the end)
3. `cases/`
4. `RESULTS.md`
5. `DECISION.md`

## Layout

| Path | What |
|---|---|
| `cases/sources/LAB_REVENUE_POLICY.md` | the LAB_AUTHORED governing source (clauses S1–S4) |
| `cases/records/S1..S4.json` | the four IR records (`E3-IR-0.1`) |
| `cases/approvals/` | LAB_SIMULATED approvals and one revocation, including the attack variants |
| `cases/roster.json`, `cases/fact_registry.json` | the lab authority roster; field origins, fact designations, metric units and the one derivation pattern |
| `cases/SCENARIOS.json` | 54 scenarios with frozen expected outcomes |
| `cases/RECEIPT_PLAN.json`, `cases/ORACLE_EXPECTED.json`, `cases/UNTYPED_BASELINE.json` | native queries to run; frozen independent oracle values; baseline cases |
| `schema/*.schema.json` | JSON Schema exported from the Pydantic models |
| `src/models.py`, `src/validator.py` | the typed IR and the read-only validator |
| `src/collect_evidence.py` | native receipts, guard and oracle receipts, catalog extract (the only part that runs MetricFlow) |
| `src/run_scenarios.py`, `src/untyped_baseline.py`, `src/replay.py`, `src/gate.py` | scenario run, plain-JSON comparison, fresh-process replay, verdict |
| `src/build_fixtures.py` | wrote `cases/` before the freeze |
| `evidence/` | identity, catalog, snapshots, receipts, validation results, baseline, replay, gate, pytest log, non-scored diagnostics |

## Commands actually run (Linux, bash, from `experiments/E3_formal_ir`)

```bash
# setup: pinned upstream, locked environment, E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# before the freeze
.upstream/.venv/bin/python src/build_fixtures.py --upstream .upstream
# (protocol, prior and fixtures committed and pushed: cbb0850; manifest d5b07c5)

# after the freeze
.upstream/.venv/bin/python src/collect_evidence.py --upstream .upstream --out evidence
.upstream/.venv/bin/python src/run_scenarios.py --out evidence/validation_results.json
.upstream/.venv/bin/python src/untyped_baseline.py --results evidence/validation_results.json --out evidence/untyped_baseline.json
.upstream/.venv/bin/python src/replay.py --python .upstream/.venv/bin/python --scored evidence/validation_results.json --out evidence/replay
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
python3 src/gate.py --evidence evidence
```

The JSON Schema export and the non-scored diagnostics were one-off inline commands; their outputs are in
`schema/` and `evidence/diagnostics_nonscored.json`.

**Re-validating from committed files only** (no MetricFlow needed): `run_scenarios.py`, `untyped_baseline.py`,
`replay.py` and `gate.py` need only Python ≥ 3.10 with pydantic 2. Re-collecting native evidence needs the
pinned build above. DuckDB files are not byte-reproducible across rebuilds, so warehouse sha256 values in new
receipts will differ; every compared value will not.

## Windows PowerShell — UNTESTED

These commands were not executed on Windows.

```powershell
cd experiments\E3_formal_ir
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
Push-Location .upstream; uv sync --frozen; Pop-Location
.\.upstream\.venv\Scripts\python.exe ..\E0_native_adapter\src\run_e0.py --regen --upstream .upstream --out runs\e0_rebuild
.\.upstream\.venv\Scripts\python.exe src\collect_evidence.py --upstream .upstream --out evidence
.\.upstream\.venv\Scripts\python.exe src\run_scenarios.py --out evidence\validation_results.json
.\.upstream\.venv\Scripts\python.exe src\untyped_baseline.py --results evidence\validation_results.json --out evidence\untyped_baseline.json
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\ | Tee-Object evidence\pytest.log
python src\gate.py --evidence evidence
```

`src/replay.py` passes a POSIX `PATH` to the child process. On Windows it would need an adapted environment.
