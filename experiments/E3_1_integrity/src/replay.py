"""Independent fresh-process rerun (G4): a second verifier process with an empty environment, isolated Python and a
temporary cwd does its OWN fresh rebuild, native runs and reference calculations; normalized results are compared.

    python3 src/replay.py --python .upstream/.venv/bin/python --scored evidence/run --out evidence/replay
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

E31 = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        env = {"PATH": "/root/.local/bin:/usr/local/bin:/usr/bin:/bin", "HOME": tmp}
        proc = subprocess.run([str(Path(a.python).absolute()), "-I", str(E31 / "src" / "e31.py"), "--upstream", str(E31 / ".upstream"),
                               "--out", str(out)], cwd=tmp, env=env, capture_output=True, text=True)
    scored = (Path(a.scored) / "normalized.json").read_bytes()
    replay = (out / "normalized.json").read_bytes() if (out / "normalized.json").exists() else b""
    b1 = json.loads((Path(a.scored) / "fresh_build.json").read_text())
    b2 = json.loads((out / "fresh_build.json").read_text()) if (out / "fresh_build.json").exists() else {}
    rec = {"argv": ["<python>", "-I", "src/e31.py", "--upstream", ".upstream", "--out", "<replay>"],
           "env_keys": sorted(env), "cwd": "fresh temporary directory", "exit_code": proc.returncode,
           "stdout_head": proc.stdout[:400], "stderr_tail": proc.stderr[-1500:],
           "normalized_scored_sha256": hashlib.sha256(scored).hexdigest(),
           "normalized_replay_sha256": hashlib.sha256(replay).hexdigest(), "normalized_identical": scored == replay,
           "independent_rebuild": {"scored_run_id": b1.get("run_id"), "replay_run_id": b2.get("run_id"),
                                   "scored_warehouse_sha256": b1.get("warehouse_sha256"), "replay_warehouse_sha256": b2.get("warehouse_sha256"),
                                   "replay_build_ok": b2.get("ok")}}
    (out / "replay_record.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("exit_code", "normalized_identical")} | rec["independent_rebuild"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
