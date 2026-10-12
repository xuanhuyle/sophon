# E1 — known predicate binding and observability

**Gate result: PASS_KNOWN_BINDING** (DECISION.md), for known binding and observability mechanics on this tiny
synthetic stack only. Stacked on E0 (draft PR #4); reuses `experiments/E0_native_adapter/src/mf_adapter.py`
unmodified.

Read in order: `PRIOR.md` → `SOURCE_INVENTORY.md` → `PROTOCOL.md` + `FROZEN_CASES.json` + `EXPECTED.json`
(+ `FREEZE_MANIFEST.txt`) → `RESULTS.md` → `DECISION.md`.

## Layout

| Path | What |
|---|---|
| `FROZEN_CASES.json` | LAB-REV-1 clauses, predicates, supplied bindings, lab authority registry, cases A/B1/B2, adversarial variants |
| `EXPECTED.json` | Expected outcomes written before the evaluator; the evaluator never reads it |
| `src/evaluator.py` | Binding/observability evaluator (decision procedure of PROTOCOL §3); `LiveContext` and `SnapshotContext` |
| `src/oracle.py` | Independent oracle: stdlib over raw CSVs; reuses E0 `crosscheck.py` for case A |
| `src/inventory.py` | Bounded-estate snapshot and fingerprint |
| `src/run_e1.py` | Runs the scored cases and variants once, writes `evidence/run/` |
| `src/replay.py` | Fresh-process replay from recorded evidence (no `mf`, no DuckDB) |
| `tests/test_e1_binding.py` | 16 tests: A, B1, B2, ten variants, oracle sanity, registry diagnostic, replay |
| `evidence/` | Inventory snapshot, run results with full transcripts, replay report, B1 raw diagnostic, pytest log |

## Commands actually run (Linux, bash, from `experiments/E1_predicate_binding`)

Requirements as E0: git, uv (0.11.32 used), CPython 3.11 (3.11.17 used), network for step 1 only.

```bash
# 1. pinned upstream + locked environment, then E0's own build path (data, bronze, dbt build, dbt parse, Q)
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# 2. bounded-estate inventory (frozen before the evaluator existed)
.upstream/.venv/bin/python src/inventory.py --upstream .upstream --out evidence/inventory_snapshot.json

# 3. scored run: cases A, B1, B2 and adversarial variants
.upstream/.venv/bin/python src/run_e1.py --upstream .upstream --out evidence/run

# 4. fresh-process replay of the recorded evidence (+ oracle recomputation from raw CSVs)
.upstream/.venv/bin/python src/replay.py --evidence evidence/run --out evidence/replay.json --raw .upstream/data/raw

# 5. tests (re-execute everything live and compare with EXPECTED.json)
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e1_binding.py
```

## Windows PowerShell — UNTESTED

Not executed (no Windows machine). Equivalent commands:

```powershell
cd experiments\E1_predicate_binding
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
Push-Location .upstream; uv sync --frozen --python 3.11; Pop-Location
.\.upstream\.venv\Scripts\python.exe ..\E0_native_adapter\src\run_e0.py --regen --upstream .upstream --out runs\e0_rebuild
.\.upstream\.venv\Scripts\python.exe src\run_e1.py --upstream .upstream --out evidence\run
.\.upstream\.venv\Scripts\python.exe src\replay.py --evidence evidence\run --out evidence\replay.json --raw .upstream\data\raw
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_e1_binding.py
```

## Notes for replay on a fresh clone

The recorded evidence anonymizes local paths (`<upstream>`, `<e1>`). Step 4 needs only the committed evidence;
the `--raw` part needs step 1's regenerated CSVs, which are byte-identical to E0's (seed 42). Steps 3 and 5
re-execute natively and should give the same statuses; the DuckDB file itself differs between builds (E0 RESULTS §5).
