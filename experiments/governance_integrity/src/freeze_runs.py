#!/usr/bin/env python3
"""Freeze the arms' run outputs into the repository (baseline/ for arm A, sophon/ for arm B).

  python3 src/freeze_runs.py --runs-root RUNS --out .

Per (arm, task) it copies PROMPT.md, STAGE_MANIFEST.json, AUDIT.json, AGENT_ID.txt and output/, and stores each
proposal tree the arm built as a unified patch against the sealed rules pin of that task
(`proposal_<name>.patch`), so that the scorer's replay can be reproduced from the sealed inputs without storing
thousands of copied rule files. The arm's persistent `work/` directory is frozen once per arm, as it stood at the
end of the last task, minus the `proposals/` trees (covered by the patches) and minus any file above 2 MB (listed
by hash instead). The T4 audit stage's output/ and PROMPT.md go to audit/. Everything copied is hashed into
FROZEN_MANIFEST.json so later edits are detectable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM_DIR = {"A": "baseline", "B": "sophon"}
TASKS = ["T0", "T1a", "T1b", "R1", "R2", "R3", "R4", "R5", "M0", "M1", "M2"]
BIG = 2 * 1024 * 1024


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def copy_tree(src: Path, dst: Path, manifest: dict, skip_dirs=("node_modules", "proposals")):
    for p in sorted(src.rglob("*")):
        if not p.is_file() or any(part in skip_dirs for part in p.parts):
            continue
        rel = p.relative_to(src)
        if p.stat().st_size > BIG:
            manifest.setdefault("large_files_not_copied", {})[str(dst / rel)] = {"sha256": sha(p), "bytes": p.stat().st_size}
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / rel)


def proposal_patches(stage: Path, dst: Path, manifest: dict, key: str, task: str):
    """For every rule tree under work/proposals/<task>/, write a unified diff against the task's sealed pin tree.
    Trees from earlier tasks are already frozen in their own task directory and are skipped here."""
    props = stage / "work" / "proposals" / task
    if not props.exists():
        return
    pins = list((stage / "inputs" / "rules").iterdir())
    base = pins[0] / "modele-social" / "règles" if pins else None
    for tree in sorted(props.rglob("règles")):
        if not tree.is_dir() or base is None:
            continue
        rel_parts = tree.relative_to(props).parts[:-2]  # strip 'modele-social/règles'
        name = task + ("_" + "_".join(rel_parts) if rel_parts else "")
        if "modele-ti" in tree.parts or "modele-commun" in tree.parts:
            # context trees of R4/R5 are reconstructions of sealed diff context; record their hash only
            manifest.setdefault("proposal_trees_hash_only", {})[f"{key}/{tree.relative_to(stage)}"] = tree_hash(tree)
            continue
        out = dst / f"proposal_{name}.patch"
        r = subprocess.run(["diff", "-ruN", str(base), str(tree)], capture_output=True, text=True)
        header = f"# unified diff: sealed pin {pins[0].name} -> {tree.relative_to(stage)} (diff -ruN; exit {r.returncode})\n"
        out.write_text(header + r.stdout, encoding="utf-8")
        manifest.setdefault("proposal_patches", {})[f"{key}/{out.name}"] = {"base_pin": pins[0].name, "tree": str(tree.relative_to(stage)), "tree_sha256": tree_hash(tree), "lines": r.stdout.count("\n")}


def tree_hash(tree: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(tree.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(tree)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    runs, out = Path(a.runs_root).resolve(), Path(a.out).resolve()
    manifest = {"runs_root": str(runs), "copied": {}}
    for arm, dname in ARM_DIR.items():
        last = None
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
            proposal_patches(src, dst, manifest, f"{dname}/{t}", t)
            if (src / "work").exists():
                last = src / "work"
        if last is not None:
            copy_tree(last, out / dname / "final_work", manifest)
            (out / dname / "final_work" / "SOURCE.txt").write_text(f"persistent work/ of arm {arm} as it stood after the last task; copied from {last}; proposals/ trees are stored as patches in each task directory\n", encoding="utf-8")
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
    print(json.dumps({"files_frozen": len(manifest["copied"]), "proposal_patches": len(manifest.get("proposal_patches", {})), "large_files_not_copied": len(manifest.get("large_files_not_copied", {}))}))


if __name__ == "__main__":
    main()
