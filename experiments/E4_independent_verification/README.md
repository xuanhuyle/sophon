# E4: independent native semantic verification

**Verdict: PASS_INDEPENDENT_VERIFICATION_SIGNAL** (DECISION.md).

This is stacked on E3.1 (draft PR #9), which is stacked on #8, #7, #6, #5 and #4. Earlier experiment files are
unchanged.

Read in this order:
1. `PRIOR.md`
2. `PROTOCOL.md` (frozen at `6553fb3`, plus `FREEZE_MANIFEST.txt` in `fe2c484`)
3. `REFERENCE.json`
4. `VARIANTS.json`
5. `candidates/`
6. `RESULTS.md`
7. `DECISION.md`

## Layout

| Path | What |
|---|---|
| `REFERENCE.json`, `fixtures/reference_lines/` | approved LAB specs P1 and P2, registered snapshots, frozen independent reference results (full line membership) |
| `VARIANTS.json`, `candidates/*.json` | 14 variants and 9 candidate implementations (text patches to the pinned project plus native query) with frozen expectations |
| `src/reference.py`, `src/fixtures.py` | independent raw-CSV reference; deterministic fixture construction (BOUNDARY, NEGQTY, STALE) |
| `src/candidate_stack.py` | builds and executes a candidate's own dbt/MetricFlow stack |
| `src/checker.py` | the E4 checker (written after the freeze; never reads `expected`) |
| `src/gate.py` | independent scorer and verdict |
| `src/replay.py` | fresh-process rerun |
| `src/extract_evidence.py` | compiled SQL, diffs and counterexamples as files |
| `src/build_variants.py`, `src/build_reference.py` | wrote the frozen inputs |
| `tests/test_e4.py` | reference predicates, patch-anchor uniqueness, authority controls, no use of `expected` |
| `evidence/` | pre-freeze feasibility, scored run (variant results, candidate stacks, compiled SQL, diffs, counterexamples), replay, gate, pytest log |

## Commands actually run (Linux, bash, from `experiments/E4_independent_verification`)

```bash
# setup: pinned upstream, locked environment, E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# before the freeze
python3 src/fixtures.py --pinned .upstream/data/raw --out runs/snapshots > runs/fixtures_registry.json
python3 src/build_variants.py
.upstream/.venv/bin/python runs/feasibility.py          # copied to evidence/prefreeze_feasibility/ (not scored)
python3 src/build_reference.py --snapshots runs/snapshots
# (freeze 6553fb3, manifest fe2c484, pushed)

# after the freeze
.upstream/.venv/bin/python src/checker.py --upstream .upstream --out evidence/run           # about 8 minutes
python3 src/extract_evidence.py --run evidence/run
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay   # rebuilds everything
python3 src/gate.py --evidence evidence
```

Candidate stacks and fixtures are built under `runs/` (ignored). Each stack is a copy of the pinned project with a
symlink to the locked virtualenv.

## Windows PowerShell — UNTESTED

These commands were not executed on Windows.

```powershell
cd experiments\E4_independent_verification
.\.upstream\.venv\Scripts\python.exe src\checker.py --upstream .upstream --out evidence\run
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\ | Tee-Object evidence\pytest.log
python src\gate.py --evidence evidence
```

`candidate_stack.py` symlinks `.venv`, which on Windows needs developer mode or a copy. The E0 adapter's Windows
paths (`Scripts\mf.exe`) were never exercised.
