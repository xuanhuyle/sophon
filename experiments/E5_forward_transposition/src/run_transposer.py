"""Run the E5 transposer in isolation (PROTOCOL.md §4).

A fresh temporary directory receives ONLY a copy of src/transposer.py and the packet. A small launcher installs a
Python audit hook that records every file the process opens, then runs the transposer with `python3 -I`, a minimal
environment and that directory as cwd. The proposal, stdout/stderr, open log and invocation record are copied out.

    python3 src/run_transposer.py --packet TRANSPOSE_PACKET.json --out evidence/run/transposer
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
REPO = E5.parent.parent
PYTHON = "/usr/bin/python3"
LAUNCHER = r'''
import json, runpy, sys
opened = []
def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        opened.append(args[0] if isinstance(args[0], str) else args[0].decode("utf-8", "replace"))
sys.addaudithook(hook)
sys.argv = ["transposer.py", "packet.json", "proposal.json"]
try:
    runpy.run_path("transposer.py", run_name="__main__")
except SystemExit:
    pass
finally:
    log = list(opened)
    with open("open_log.json", "w") as f:
        json.dump(log, f)
'''


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(packet: dict | Path, out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = Path(packet).read_bytes() if isinstance(packet, Path) else (json.dumps(packet, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="e5_transposer_") as tmp:
        t = Path(tmp)
        shutil.copy(HERE / "transposer.py", t / "transposer.py")
        (t / "packet.json").write_bytes(raw)
        (t / "launch.py").write_text(LAUNCHER, encoding="utf-8")
        before = sorted(p.name for p in t.iterdir())
        argv = [PYTHON, "-I", "launch.py"]
        p = subprocess.run(argv, cwd=tmp, env={"PATH": "/usr/bin:/bin", "HOME": tmp}, capture_output=True, text=True)
        opened = json.loads((t / "open_log.json").read_text()) if (t / "open_log.json").exists() else None
        proposal = json.loads((t / "proposal.json").read_text()) if (t / "proposal.json").exists() else None
        if proposal is not None:
            shutil.copy(t / "proposal.json", out / "proposal.json")
        prefix = Path(sys.base_prefix).resolve()
        cls = {"isolated_dir": [], "python_runtime": [], "repository": [], "other": []}
        for o in opened or []:
            q = Path(o) if Path(o).is_absolute() else t / o
            q = Path(str(q))
            sq = str(q.resolve()) if q.exists() else str(q)
            if sq.startswith(str(t.resolve())) or sq.startswith(tmp):
                cls["isolated_dir"].append(str(Path(sq).relative_to(t.resolve())) if sq.startswith(str(t.resolve())) else sq)
            elif sq.startswith(str(REPO.resolve())):
                cls["repository"].append(sq)
            elif sq.startswith(str(prefix)) or sq.startswith("/usr/lib/python3") or sq.startswith("/usr/local/lib/python3"):
                cls["python_runtime"].append(sq)
            else:
                cls["other"].append(sq)
    rec = {"argv": ["/usr/bin/python3", "-I", "launch.py"], "launcher_runs": "transposer.py packet.json proposal.json",
           "cwd": "fresh temporary directory containing only: " + ", ".join(before), "env": {"PATH": "/usr/bin:/bin", "HOME": "<temporary dir>"},
           "python": subprocess.run([PYTHON, "--version"], capture_output=True, text=True).stdout.strip(),
           "transposer_sha256": sha_bytes((HERE / "transposer.py").read_bytes()), "packet_sha256": sha_bytes(raw),
           "exit_code": p.returncode, "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:], "wall_seconds": round(time.time() - t0, 3),
           "opened_files": {k: sorted(set(v)) for k, v in cls.items()},
           "no_repository_file_opened": opened is not None and not cls["repository"],
           "model": None, "paid_calls": 0}
    (out / "invocation.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return {"invocation": rec, "proposal": proposal}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r = run(Path(a.packet), Path(a.out))
    print(json.dumps({"exit": r["invocation"]["exit_code"], "status": (r["proposal"] or {}).get("status"),
                      "no_repo_read": r["invocation"]["no_repository_file_opened"], "opened": r["invocation"]["opened_files"]}, indent=1))
