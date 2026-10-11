# Governance-integrity lifecycle experiment (2026-10-11)

One public law-to-executable-rules system (`betagouv/mon-entreprise` Publicodes rules governed by the
French Code de la sécurité sociale, consolidated article snapshots from `@socialgouv/legi-data`,
OpenFisca-France as the independent oracle), two arms (A: Claude Code with native tools and its own
notes; B: the same plus a tiny provenance store), eleven preregistered tasks and a fresh-context
as-of audit. Read in this order:

1. `PRIOR_EVIDENCE.md`: what earlier Sophon work did and did not establish, and the delta tested here.
2. `EVIDENCE_GATE.md`: the three candidate systems, the A–E checklist, and the gate outcome (**PARTIAL / LIMITED**).
3. `PROTOCOL.md` (+ `PROTOCOL.sha256`): the frozen preregistration. Everything downstream is scored against it.
4. `RESULTS.md`, `AUDIT_REPORT.md`, `DECISION.md`: what happened, with exact counts.

Reproducible pieces: `SOURCES.json` (origins, hashes, dates, licences), `inputs/` (sealed, immutable;
`inputs/MANIFEST.json` hashes every file), `src/` and `tests/`, `baseline/` and `sophon/` (frozen arm
outputs), `held_out/` (scorer-only reference), `results/` (mechanical scores).

## Reproduce

Requirements: Python 3.12+ with `pyyaml`, Node 22+, git. Commands are given for PowerShell; on bash
replace `;` line continuations as needed (they are plain commands).

```powershell
cd experiments/governance_integrity
# 1. runtime (publicodes 1.10.4, @publicodes/tools 1.0.7, js-yaml), pinned by package-lock.json
cd src; npm ci --no-audit --no-fund; cd ..
# 2. the native adapter reproduces the published package exactly at pin G0 (639 raw / 1172 parsed rules)
node src/publicodes_eval.mjs build --rules "inputs/rules/G0_d9242882f96b/modele-social/règles"
# 3. kernel tamper tests (7 tests)
python -B tests/test_tamper.py
# 4. verify the sealed inputs against the manifest
python -B -c "import json,hashlib,sys; m=json.load(open('inputs/MANIFEST.json')); bad=[p for p,h in m['files'].items() if __import__('os').path.exists(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()!=h]; print('mismatches:', bad)"
# 5. rebuild the scorer-only reference from the sealed law texts (writes held_out/REFERENCE.json, COVERAGE.json)
python -B src/build_reference.py --out .
# 6. re-score the frozen arm outputs (replays every executable claim through the engine)
python -B src/score.py --runs-root frozen_runs --out results
```

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
| `src/stage_task.py`, `src/stage_audit.py`, `src/seal.sh`, `src/audit_transcripts.py`, `src/score.py` | Run harness: staging, sealing, transcript audit, mechanical scoring |
| `tests/test_tamper.py` | Tamper tests (robustness diagnostics, not episodes) |
| `inputs/` | Sealed law snapshots S0–S10, rule pins G0–G4, reverse-case diffs, prompts, TASKS.json, MANIFEST.json |
| `held_out/` | Scorer-only: REFERENCE.json, COVERAGE.json, OpenFisca oracle files, maintainers' later commits |
| `baseline/`, `sophon/` | Frozen outputs of arm A and arm B per task, with transcript audits |
| `results/` | Mechanical scores |
