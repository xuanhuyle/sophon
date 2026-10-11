#!/usr/bin/env python3
"""Rebuild a scorer-ready runs root from the frozen arm outputs and the sealed inputs, so that
`src/score.py` and `src/stale_assurance.py` can be re-run from the repository alone.

  python3 src/rehydrate_runs.py --out RUNS_DIR

For every frozen (arm, task) directory (baseline/ = arm A, sophon/ = arm B) it creates RUNS_DIR/<arm>/<task>/ with
the frozen output/, AUDIT.json, PROMPT.md and STAGE_MANIFEST.json, symlinks to the sealed law snapshots and rule
pin named in STAGE_MANIFEST.json, and rebuilds each proposal tree under work/proposals/<task>/modele-social/règles
by copying the pin tree and applying the frozen `proposal_*.patch` (paths are rewritten to a/ b/ and applied with
`patch -p1`). Every rebuilt tree's hash is compared with the hash recorded in FROZEN_MANIFEST.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM_DIR = {"A": "baseline", "B": "sophon"}


def tree_hash(tree: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(tree.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(tree)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def unquote(path: str) -> str:
    """diff quotes file names containing non-ASCII bytes and writes them as octal escapes ("r\303\250gles")."""
    if path.startswith('"') and path.endswith('"'):
        inner = path[1:-1]
        raw = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), inner).encode("latin-1", "backslashreplace")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return inner
    return path


def rewrite_patch(text: str) -> str:
    out = []
    for line in text.splitlines():
        if line.startswith("# unified diff"):
            continue
        m = re.match(r"^(---|\+\+\+) (\"[^\"]*\"|\S+)(.*)$", line)
        if m and "/dev/null" not in m.group(2):
            tag, path, rest = m.groups()
            path = unquote(path)
            rel = path.split("règles/", 1)[1] if "règles/" in path else path
            out.append(f"{tag} {'a' if tag == '---' else 'b'}/{rel}{rest}")
        elif line.startswith("diff -ruN"):
            continue
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    frozen = json.load(open(ROOT / "FROZEN_MANIFEST.json", encoding="utf-8"))
    patches = frozen.get("proposal_patches", {})
    report = {"tasks": 0, "trees_rebuilt": 0, "tree_hash_match": 0, "tree_hash_mismatch": [], "patch_failures": []}
    for arm, dname in ARM_DIR.items():
        for tdir in sorted((ROOT / dname).iterdir()):
            if not tdir.is_dir() or tdir.name in ("final_work",):
                continue
            task = tdir.name
            stage = out / arm / task
            stage.mkdir(parents=True, exist_ok=True)
            report["tasks"] += 1
            for f in ("PROMPT.md", "STAGE_MANIFEST.json", "AUDIT.json", "AGENT_ID.txt"):
                if (tdir / f).exists():
                    shutil.copy2(tdir / f, stage / f)
            if (tdir / "output").exists():
                shutil.copytree(tdir / "output", stage / "output", dirs_exist_ok=True)
            man = json.load(open(tdir / "STAGE_MANIFEST.json", encoding="utf-8"))
            (stage / "inputs" / "law").mkdir(parents=True, exist_ok=True)
            (stage / "inputs" / "rules").mkdir(parents=True, exist_ok=True)
            for snap in man.get("law") or []:
                src = next(ROOT.glob(f"inputs/law/{snap}_*"))
                dst = stage / "inputs" / "law" / src.name
                if not dst.exists():
                    os.symlink(src, dst)
            pin = man.get("rules")
            pin_src = next(ROOT.glob(f"inputs/rules/{pin}_*")) if pin else None
            if pin_src:
                dst = stage / "inputs" / "rules" / pin_src.name
                if not dst.exists():
                    os.symlink(pin_src, dst)
            for pf in sorted(tdir.glob("proposal_*.patch")):
                key = f"{dname}/{task}/{pf.name}"
                info = patches.get(key)
                if not info or not pin_src:
                    report["patch_failures"].append({"patch": key, "why": "no manifest entry or no pin"}); continue
                tree = stage / info["tree"]
                if tree.exists():
                    shutil.rmtree(tree)
                shutil.copytree(pin_src / "modele-social" / "règles", tree)
                rewritten = rewrite_patch(pf.read_text(encoding="utf-8"))
                r = subprocess.run(["patch", "-p1", "-s", "-E", "--no-backup-if-mismatch", "-d", str(tree)], input=rewritten, capture_output=True, text=True)
                report["trees_rebuilt"] += 1
                if r.returncode != 0:
                    report["patch_failures"].append({"patch": key, "why": r.stderr[:300] or r.stdout[:300]})
                h = tree_hash(tree)
                if h == info["tree_sha256"]:
                    report["tree_hash_match"] += 1
                else:
                    report["tree_hash_mismatch"].append({"patch": key, "expected": info["tree_sha256"], "got": h})
    # the audit stage output, for verify_audit.py (its inputs are the sealed inputs and the arms' artifacts)
    if (ROOT / "audit").exists():
        shutil.copytree(ROOT / "audit", out / "audit", dirs_exist_ok=True)
    json.dump(report, open(out / "REHYDRATE_REPORT.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
