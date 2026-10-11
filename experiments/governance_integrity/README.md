# Governance-integrity lifecycle experiment (2026-10-11)

One public law-to-executable-rules system (`betagouv/mon-entreprise` Publicodes rules governed by the
French Code de la sécurité sociale, consolidated article snapshots from `@socialgouv/legi-data`,
OpenFisca-France as the independent oracle), two arms (A: Claude Code with native tools and its own
notes; B: the same plus a tiny provenance store), eleven preregistered tasks per arm and a fresh-context
as-of audit. **Decision: STOP_KERNEL** (`DECISION.md`). Read in this order:

1. `PRIOR_EVIDENCE.md`: what earlier Sophon work did and did not establish, and the delta tested here.
2. `EVIDENCE_GATE.md`: the three candidate systems, the A–E checklist, and the gate outcome (**PARTIAL / LIMITED**).
3. `PROTOCOL.md` (+ `PROTOCOL.sha256`): the frozen preregistration. Everything downstream is scored against it.
4. `RUN_LOG.md`: every run (model, agent transcript id, tool calls, wall-clock, leakage flags, notes).
5. `RESULTS.md`, `AUDIT_REPORT.md`, `DECISION.md`: what happened, with exact counts, and the mapping to the decision.

Reproducible pieces: `SOURCES.json` (origins, hashes, dates, licences), `inputs/` (sealed, immutable;
`inputs/MANIFEST.json` hashes every file), `src/` and `tests/`, `baseline/` and `sophon/` (frozen outputs
of arm A and arm B, hashed in `FROZEN_MANIFEST.json`), `audit/` (the T4 auditor's prompt, answer and notes),
`held_out/` (scorer-only reference, unsealed after the runs), `results/` (mechanical scores and checks).

## Reproduce

Requirements: Python 3.12+ with `pyyaml`, Node 22+, GNU `patch` (ships with Git for Windows). Commands are
given for PowerShell; they are plain commands and run unchanged in bash.

```powershell
cd experiments/governance_integrity
# 1. runtime (publicodes 1.10.4, @publicodes/tools 1.0.7, js-yaml), pinned by package-lock.json
cd src; npm ci --no-audit --no-fund; cd ..
# 2. the native adapter reproduces the published package exactly at pin G0 (639 raw / 1172 parsed rules)
node src/publicodes_eval.mjs build --rules "inputs/rules/G0_d9242882f96b/modele-social/règles"
# 3. kernel tamper tests (7 tests)
python -B tests/test_tamper.py
# 4. verify the sealed inputs and the frozen outputs against their manifests
python -B -c "import json,hashlib,os; m=json.load(open('inputs/MANIFEST.json')); print('inputs mismatches:', [p for p,h in m['files'].items() if os.path.exists(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()!=h])"
python -B -c "import json,hashlib,os; m=json.load(open('FROZEN_MANIFEST.json')); print('frozen mismatches:', [p for p,h in m['copied'].items() if os.path.exists(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()!=h])"
# 5. rebuild the scorer-only reference from the sealed law texts (writes held_out/REFERENCE.json, COVERAGE.json)
python -B src/build_reference.py --out .
# 6. rebuild a scorer-ready runs root from the frozen outputs (proposal trees are re-created from the sealed
#    pins plus the frozen patches and hash-checked against FROZEN_MANIFEST.json: 18/18 identical)
python -B src/rehydrate_runs.py --out ..\..\runs_rehydrated
# 7. re-score (replays every executable claim and every reference requirement through the engine; ~2 min)
python -B src/score.py --runs-root ..\..\runs_rehydrated --out results_check
# 8. re-check the T4 auditor's answer against the sealed inputs
python -B src/verify_audit.py --audit ..\..\runs_rehydrated\audit --out results_check\audit_verification.json
```

The re-score from the rehydrated root was run once by the orchestrator and gave scores identical to
`results/scores.json` for all 22 (arm, task) cells. `src/stale_assurance.py` (stale-assurance metric and
hash-chain check over arm B's store) reads the store under `sophon/final_work/sophon/store` but re-runs the
stored checks against the rule directories the store names, which are absolute paths of the original run; to
re-run it, point those paths at the rehydrated root or re-register the snapshots.

Rebuilding the sealed inputs from the upstream sources needs network access to GitHub and the npm
registry (`src/build_inputs.py`; see its docstring). The legi-data snapshots are fetched with
`npm pack @socialgouv/legi-data@<version>`; the hashes to compare with are in `SOURCES.json`.

Running the arms again needs a fresh model context per task: `src/stage_task.py` stages each
(arm, task) directory with only the inputs the protocol allows and a frozen prompt; the solver is a
new agent pointed only at that directory; `src/audit_transcripts.py` audits its transcript for
leakage and counts cost; `src/stage_audit.py` stages the T4 auditor. Solver runs are not reproducible
bit for bit (model sampling); the frozen outputs under `baseline/` and `sophon/` are what was scored.

## Layout

| Path | What |
|---|---|
| `src/publicodes_eval.mjs` | Native Publicodes runtime adapter (build / list / evaluate) |
| `src/sophon.py`, `src/USAGE.md` | The minimal provenance store (arm B's only extra tool) |
| `src/build_inputs.py`, `src/build_reference.py` | Sealed-input builder; scorer-only reference builder |
| `src/stage_task.py`, `src/stage_audit.py`, `src/seal.sh`, `src/audit_transcripts.py`, `src/collect_run.sh` | Run harness: staging, sealing, transcript audit |
| `src/score.py`, `src/verify_audit.py`, `src/stale_assurance.py` | Mechanical scoring; audit re-check; stale-assurance and hash-chain replay |
| `src/freeze_runs.py`, `src/rehydrate_runs.py` | Freeze run outputs into the repository; rebuild a scorer-ready root from them |
| `tests/test_tamper.py` | Tamper tests (robustness diagnostics, not episodes) |
| `inputs/` | Sealed law snapshots S0–S10, rule pins G0–G4, reverse-case diffs, prompts, TASKS.json, MANIFEST.json |
| `held_out/` | Scorer-only: REFERENCE.json, COVERAGE.json, OpenFisca oracle files, maintainers' later commits (encrypted during the runs, plaintext now) |
| `baseline/`, `sophon/` | Frozen outputs of arm A and arm B per task (prompt, answer, notes, transcript audit, proposal patches) and each arm's final `work/` |
| `audit/` | T4 auditor stage: prompt, manifest, transcript audit, `output/audit.json`, `output/AUDIT_NOTES.md` |
| `results/` | `SCORES.md` / `scores.json` (second pass), `SCORES_firstpass.md` / `scores_firstpass.json` (first pass, kept), `audit_verification.json`, `stale_assurance.json` |
