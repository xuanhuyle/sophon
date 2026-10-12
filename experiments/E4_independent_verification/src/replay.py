"""Fresh-process rerun (Q5): a second checker process (python -I, minimal environment, temporary cwd) rebuilds every
fixture and candidate stack and re-executes everything; normalized variant results must be identical.

    python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

E4 = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": tmp}
        proc = subprocess.run([str(Path(a.python).absolute()), "-I", str(E4 / "src" / "checker.py"), "--upstream", str(E4 / ".upstream"),
                               "--out", str(out)], cwd=tmp, env=env, capture_output=True, text=True)
    s = (Path(a.scored) / "normalized.json").read_bytes()
    r = (out / "normalized.json").read_bytes() if (out / "normalized.json").exists() else b""
    rec = {"argv": ["<python>", "-I", "src/checker.py", "--upstream", ".upstream", "--out", "<replay>"], "env_keys": sorted(env),
           "cwd": "fresh temporary directory", "exit_code": proc.returncode, "stdout": proc.stdout[-3000:], "stderr_tail": proc.stderr[-1500:],
           "normalized_scored_sha256": hashlib.sha256(s).hexdigest(), "normalized_replay_sha256": hashlib.sha256(r).hexdigest(),
           "normalized_identical": s == r,
           "note": "every fixture and candidate stack is rebuilt in this process (runs/checker_replay); no scored artefact is reused"}
    (out / "replay_record.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("exit_code", "normalized_identical")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
