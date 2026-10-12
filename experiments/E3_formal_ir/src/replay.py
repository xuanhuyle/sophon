"""Fresh-process replay (test 12). Re-runs all scenarios in a new interpreter with an empty environment, isolated mode
and a temporary working directory, from committed files only, and compares the output byte-for-byte.

    python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/validation_results.json --out evidence/replay
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

E3 = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    replay_file = out / "validation_results_replay.json"
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.run([str(Path(a.python).absolute()), "-I", str(E3 / "src" / "run_scenarios.py"), "--out", str(replay_file)],
                              cwd=cwd, env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
    scored = Path(a.scored).read_bytes()
    replay = replay_file.read_bytes() if replay_file.exists() else b""
    rec = {"argv": ["<python>", "-I", "src/run_scenarios.py", "--out", "<replay>"], "env": {"PATH": "/usr/bin:/bin"},
           "cwd": "fresh temporary directory", "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr[-2000:],
           "scored_sha256": hashlib.sha256(scored).hexdigest(), "replay_sha256": hashlib.sha256(replay).hexdigest(),
           "byte_identical": scored == replay,
           "inputs": "cases/ (frozen), evidence/catalog.json, evidence/receipts/ (recorded native/guard/oracle receipts)",
           "trust_limit": "replay re-validates recorded receipts; it does not re-execute MetricFlow. Receipt integrity is "
                          "checked by hashes inside the receipts and by git history, not against a forger with write access."}
    (out / "replay_record.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("exit_code", "byte_identical", "scored_sha256")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
