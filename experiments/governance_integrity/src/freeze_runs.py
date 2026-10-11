#!/usr/bin/env python3
"""Freeze the arms' run outputs into the repository (baseline/ for arm A, sophon/ for arm B).

  python3 src/freeze_runs.py --runs-root RUNS --out .

For every (arm, task) run directory it copies PROMPT.md, STAGE_MANIFEST.json, AUDIT.json, AGENT_ID.txt,
output/ and work/ (the arm's persistent directory as it stood at the end of that task, minus
node_modules and minus any copied input trees larger than 2 MB, which are listed by hash instead).
It also copies the T4 audit stage's output/ and PROMPT.md into audit/. Everything copied is hashed
into FROZEN_MANIFEST.json so later edits are detectable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ARM_DIR = {"A": "baseline", "B": "sophon"}
TASKS = ["T0", "T1a", "T1b", "R1", "R2", "R3", "R4", "R5", "M0", "M1", "M2"]
BIG = 2 * 1024 * 1024


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def copy_work(src: Path, dst: Path, manifest: dict):
    for p in sorted(src.rglob("*")):
        if not p.is_file() or "node_modules" in p.parts:
            continue
        rel = p.relative_to(src)
        if p.stat().st_size > BIG:
            manifest.setdefault("large_files_not_copied", {})[str(dst / rel)] = {"sha256": sha(p), "bytes": p.stat().st_size}
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / rel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    runs, out = Path(a.runs_root).resolve(), Path(a.out).resolve()
    manifest = {"runs_root": str(runs), "copied": {}}
    for arm, dname in ARM_DIR.items():
        for t in TASKS:
            src = runs / arm / t
            if not src.exists():
                continue
            dst = out / dname / t
            dst.mkdir(parents=True, exist_ok=True)
            for f in ("PROMPT.md", "STAGE_MANIFEST.json", "AUDIT.json", "AGENT_ID.txt"):
                if (src / f).exists():
                    shutil.copy2(src / f, dst / f)
            if (src / "output").exists():
                shutil.copytree(src / "output", dst / "output", dirs_exist_ok=True)
            if (src / "work").exists():
                copy_work(src / "work", dst / "work", manifest)
    audit = runs / "audit"
    if audit.exists():
        dst = out / "audit"
        dst.mkdir(exist_ok=True)
        for f in ("PROMPT.md", "STAGE_MANIFEST.json", "AUDIT.json", "AGENT_ID.txt"):
            if (audit / f).exists():
                shutil.copy2(audit / f, dst / f)
        if (audit / "output").exists():
            shutil.copytree(audit / "output", dst / "output", dirs_exist_ok=True)
    for dname in list(ARM_DIR.values()) + ["audit"]:
        base = out / dname
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    manifest["copied"][str(p.relative_to(out))] = sha(p)
    json.dump(manifest, open(out / "FROZEN_MANIFEST.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({"files_frozen": len(manifest["copied"]), "large_files_not_copied": len(manifest.get("large_files_not_copied", {}))}))


if __name__ == "__main__":
    main()
