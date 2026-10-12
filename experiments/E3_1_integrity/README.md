# E3.1: temporal applicability and fresh evidence re-execution

**Verdict: PASS_INTEGRITY_HARDENING** (DECISION.md).

This is stacked on E3 (draft PR #8), which is stacked on #7, #6, #5 and #4. E3 and all earlier experiment files are
unchanged.

Read in this order:
1. `PRIOR.md`
2. `PROTOCOL.md` (frozen at `e0bf06f`, plus `FREEZE_MANIFEST.txt` in `a37ad65`; amendments at the end)
3. `cases/`
4. `evidence/reproduction/`
5. `RESULTS.md`
6. `DECISION.md`

## Layout

| Path | What |
|---|---|
| `cases/TRUSTED_MANIFEST.json` | trust anchors from E0's committed evidence and E3's frozen fixtures |
| `cases/CASES.json` | 13 temporal and 15 evidence cases with frozen expectations |
| `src/candidates.py` | harness: candidate record + approvals + receipts with in-memory tampering (frozen) |
| `src/build_cases.py`, `src/reproduce_e3_defects.py` | wrote the cases and anchors; reproduced F-TIME and F-FORGE on unmodified E3 (frozen) |
| `src/e31.py` | the E3.1 wrapper (applicability, precedence, fresh check) and runner |
| `src/fresh_verifier.py` | fresh rebuild, anchor checks, fresh native, reference and guards |
| `src/replay.py` | independent fresh-process rerun |
| `src/gate.py` | the verdict |
| `src/diagnostic_trust_boundary.py` | non-scored compromised-verifier diagnostic |
| `tests/test_e31.py` | applicability boundaries, precedence, meaning hash |
| `evidence/` | reproduction, run (case results, fresh build, fresh receipts with compiled SQL), replay, gate, pytest log, diagnostic |

## Commands actually run (Linux, bash, from `experiments/E3_1_integrity`)

```bash
# setup: pinned upstream, locked environment, E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# before the freeze (no corrected logic exists yet)
python3 src/build_cases.py
.upstream/.venv/bin/python src/reproduce_e3_defects.py --out evidence/reproduction
# (freeze e0bf06f, manifest a37ad65, pushed)

# after the freeze
.upstream/.venv/bin/python src/e31.py --upstream .upstream --out evidence/run      # fresh rebuild + 28 cases
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay   # 2nd rebuild
.upstream/.venv/bin/python src/diagnostic_trust_boundary.py --out evidence/diagnostics_nonscored.json
python3 src/gate.py --evidence evidence
```

`e31.py` deletes and rebuilds `.upstream/data/warehouse.duckdb` every time it runs; this is the fresh build.
Disposable control estates live under `runs/` (ignored).

## Windows PowerShell — UNTESTED

These commands were not executed on Windows.

```powershell
cd experiments\E3_1_integrity
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
Push-Location .upstream; uv sync --frozen; Pop-Location
.\.upstream\.venv\Scripts\python.exe src\e31.py --upstream .upstream --out evidence\run
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\ | Tee-Object evidence\pytest.log
python src\gate.py --evidence evidence
```

`fresh_verifier.py` assumes a POSIX virtualenv layout (`.venv/bin/python`) and a nonexistent POSIX path for the
runtime-unavailable control. `replay.py` sets a POSIX `PATH`. All three need adapting for Windows.
