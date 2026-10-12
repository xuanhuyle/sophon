# E2 — blind semantic relationship discovery

**Gate result: PARTIAL_DISCOVERY_SIGNAL** (DECISION.md). Stacked on E1 (draft PR #5), which is stacked on E0
(draft PR #4). E0 and E1 files are unchanged.

Read in order: `PRIOR.md` → `PROTOCOL.md` (+ `FREEZE_MANIFEST.txt`) → `CASES.json` → `RESULTS.md` → `DECISION.md`.
`REFERENCE.json` is the sealed key (never sent to the solver).

## Layout

| Path | What | Solver-visible? |
|---|---|---|
| `CASES.json` | six LAB_AUTHORED clauses H1–H6 | yes (inside the packet) |
| `packet/` | exact solver input (`solver_input.txt`) and its component files, `PACKET_MANIFEST.json` | yes, only `solver_input.txt` was sent |
| `REFERENCE.json` | sealed reference, rubric, native validation | no |
| `src/build_packet.py`, `src/task_text.md` | packet builder (pinned upstream only) | task text yes |
| `src/build_reference.py`, `src/e2_oracle.py` | reference builder + stdlib oracle | no |
| `src/audit_packet.py` | packet leakage audit | no |
| `src/run_solver.py` | the isolated blind run | no |
| `src/score.py`, `src/controls.py`, `tests/test_scorer_controls.py` | mechanical scorer, negative controls | no |
| `src/sensitivity_nonscored.py` | post-hoc NON-SCORED sensitivity | no |
| `evidence/` | packet audit, isolation diagnostics, raw solver output and run record, score report, replay, controls, sensitivity | no |

## Commands actually run (Linux, bash, from `experiments/E2_blind_discovery`)

```bash
# setup: pinned upstream + locked env, then E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# before the freeze
.upstream/.venv/bin/python src/build_reference.py --upstream .upstream --out REFERENCE.json
.upstream/.venv/bin/python src/build_packet.py --upstream .upstream --out packet
python3 src/audit_packet.py --packet packet --out evidence/packet_audit.json
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_scorer_controls.py
E2_SOLVER_SCRATCH=<scratch dir outside the repo> python3 src/run_solver.py \
    --diagnostic-prompt "Reply with exactly the word OK and nothing else." --out evidence/isolation_diagnostic

# after the freeze: the one scored run, scoring, replay, non-scored sensitivity
E2_SOLVER_SCRATCH=<scratch dir outside the repo> python3 src/run_solver.py --input packet/solver_input.txt --out evidence/solver
.upstream/.venv/bin/python src/score.py --reference REFERENCE.json --raw evidence/solver/raw_output.json \
    --upstream .upstream --out evidence/score/score_report.json --isolation-ok true --controls-ok true
.upstream/.venv/bin/python src/score.py --reference REFERENCE.json --raw evidence/solver/raw_output.json \
    --upstream .upstream --out evidence/score/score_report_replay.json --isolation-ok true --controls-ok true
cmp evidence/score/score_report.json evidence/score/score_report_replay.json
.upstream/.venv/bin/python src/sensitivity_nonscored.py
```

`run_solver.py` needs a logged-in Claude Code CLI (it copies only `~/.claude/.credentials.json` into a fresh
temporary HOME and deletes it afterwards). Re-running it creates a new, different sample; the scored sample is
the committed `evidence/solver/raw_output.json`. Re-scoring needs only the committed files plus the rebuilt
warehouse.

## Windows PowerShell — UNTESTED

Not executed. `run_solver.py` uses `env -i` semantics through Python's `subprocess` with an explicit environment
and `/opt/node22/bin` on PATH; on Windows, set PATH to the directory containing `claude.exe` and adapt the
scratch path. Scoring commands:

```powershell
cd experiments\E2_blind_discovery
.\.upstream\.venv\Scripts\python.exe src\score.py --reference REFERENCE.json --raw evidence\solver\raw_output.json --upstream .upstream --out evidence\score\score_report.json --isolation-ok true --controls-ok true
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_scorer_controls.py
```
