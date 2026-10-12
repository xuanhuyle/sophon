# E5: one approved amendment → one native semantic change

**Verdict: PASS_FORWARD_TRANSPOSITION_SIGNAL** (DECISION.md).

This is stacked on E4 (draft PR #10, `d6fe13d`), which is stacked on #9, #8, #7, #6, #5 and #4. Earlier
experiment files are unchanged.

Read in this order:
1. `PRIOR.md`
2. `PROTOCOL.md` (frozen at `2edac2b`, plus `FREEZE_MANIFEST.txt` in `8cd27dc`; amendments at the end)
3. `TRANSPOSE_PACKET.json`
4. `SCENARIOS.json`
5. `RESULTS.md`
6. `DECISION.md`

## Layout

| Path | What |
|---|---|
| `sources/LAB_REVENUE_POLICY_AMENDMENT_1.md` | LAB_AUTHORED v2 amendment ([S1 v2], ≥ 120, effective 2025-01-01) |
| `approvals/AP_S1_V2.json` | LAB_SIMULATED v2 approval bound to source sha + clause version + normalized-claim sha |
| `ir/P1_v1.json`, `ir/P1_v2.json`, `ir/NATIVE_BINDING.json` | versioned requirement IR and the fixed native binding |
| `candidates/` | BASELINE (E4 M6B + M2) and the hand-written negative controls N2A/N2B/N2C/N3 |
| `controls/N1_PACKET_MUTATIONS.json` | 11 malformed or unauthorized packet mutations |
| `TRANSPOSE_PACKET.json` | the transposer's only input (no oracle or expected data) |
| `REFERENCE.json`, `fixtures/reference_lines/` | frozen independent oracle results (hidden from the transposer) |
| `SCENARIOS.json` | F1–F8 and N1–N4 with frozen expectations (scorer only) |
| `src/claim.py`, `src/snapshots.py`, `src/oracle.py`, `src/build_*.py` | frozen: meaning hash, fixtures, oracle, input builders |
| `src/transposer.py`, `src/run_transposer.py` | the transposer and its isolated launcher (audit hook on opened files) |
| `src/authority.py`, `src/lifecycle.py` | versioned authority/temporal check and routing; lifecycle state |
| `src/e4_adapter.py` | E4 checker adapter (E4 `snapshot_eval` and `candidate_stack` reused unmodified) |
| `src/run_e5.py`, `src/gate.py`, `src/replay.py`, `src/extract_evidence.py` | runner, scorer/verdict, fresh-process replay, evidence files |
| `tests/test_e5.py` | IR-driven emission, refusals, authority/no future leak, lifecycle, oracle boundaries |
| `evidence/` | pre-freeze feasibility, scored run (proposal, invocations, compiled SQL, counterexamples, P2, routing, cost), replay, gate, pytest log |

## Commands actually run (Linux, bash, from `experiments/E5_forward_transposition`)

```bash
# setup: pinned upstream, locked environment, E0's build path
git clone https://github.com/behramkorkut/Governed-Analytics-Agent.git .upstream
git -C .upstream checkout 312e97ad192dcef02f688e31edc0a08c6cf4345f
(cd .upstream && uv sync --frozen --python /usr/bin/python3.11)
.upstream/.venv/bin/python ../E0_native_adapter/src/run_e0.py --regen --upstream .upstream --out runs/e0_rebuild

# before the freeze
.upstream/.venv/bin/python runs/feasibility.py > runs/feasibility.json      # copied to evidence/prefreeze_feasibility/ (not scored)
python3 src/snapshots.py --pinned .upstream/data/raw --out runs/snapshots
python3 src/build_inputs.py
.upstream/.venv/bin/python src/build_packet.py
python3 src/build_reference.py --snapshots runs/snapshots
# (N1 mutations and SCENARIOS.json written by inline scripts; freeze 2edac2b, manifest 8cd27dc, pushed)

# after the freeze
.upstream/.venv/bin/python src/run_e5.py --upstream .upstream --out evidence/run        # about 7 minutes
python3 src/extract_evidence.py --run evidence/run
.upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay   # rebuilds everything
python3 src/gate.py --evidence evidence

# the transposer alone (isolated):
python3 src/run_transposer.py --packet TRANSPOSE_PACKET.json --out runs/transposer
```

**Runtime notes:**
- Native stacks and snapshots are built under `runs/` (ignored). Each stack is a copy of the pinned project with a
  symlink to the locked virtualenv.
- The transposer runs on `/usr/bin/python3 -I` (stdlib only) in a temporary directory that contains only itself
  and the packet.

## Windows PowerShell — UNTESTED

These commands were not executed on Windows.

```powershell
cd experiments\E5_forward_transposition
.\.upstream\.venv\Scripts\python.exe src\run_e5.py --upstream .upstream --out evidence\run
.\.upstream\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\ | Tee-Object evidence\pytest.log
python src\gate.py --evidence evidence
```

**Known Windows gaps:**
- `run_transposer.py` hardcodes `/usr/bin/python3`, so Windows needs another interpreter path.
- E4's `candidate_stack.py` symlinks `.venv`.
- The E0 adapter's Windows paths were never exercised.
