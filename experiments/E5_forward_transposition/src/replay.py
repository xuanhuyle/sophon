"""F8 fresh-process rerun: a second runner process (python -I, minimal environment, temporary cwd) re-runs the
isolated transposer, rebuilds every snapshot and native stack and re-executes every check. Its normalized results
must be byte-identical to the scored run's.

    python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

E5 = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": tmp}
        proc = subprocess.run([str(Path(a.python).absolute()), "-I", str(E5 / "src" / "run_e5.py"), "--upstream", str(E5 / ".upstream"),
                               "--out", str(out)], cwd=tmp, env=env, capture_output=True, text=True)
    s = (Path(a.scored) / "normalized.json").read_bytes()
    r = (out / "normalized.json").read_bytes() if (out / "normalized.json").exists() else b""
    rec = {"argv": ["<venv python>", "-I", "src/run_e5.py", "--upstream", ".upstream", "--out", "<replay>"], "env_keys": sorted(env),
           "cwd": "fresh temporary directory", "exit_code": proc.returncode, "wall_seconds": round(time.time() - t0, 1),
           "stdout": proc.stdout[-3000:], "stderr_tail": proc.stderr[-1500:],
           "normalized_scored_sha256": hashlib.sha256(s).hexdigest(), "normalized_replay_sha256": hashlib.sha256(r).hexdigest(),
           "normalized_identical": s == r,
           "note": "the transposer is re-run in its own isolated directory; every snapshot and native stack is rebuilt (runs/e5_replay); "
                   "no scored artefact is reused; the scorer (gate.py) is a separate step"}
    (out / "replay_record.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("exit_code", "normalized_identical", "wall_seconds")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
