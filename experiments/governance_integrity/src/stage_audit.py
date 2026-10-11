#!/usr/bin/env python3
"""Stage the T4 audit directory (fresh auditor context) after all solver runs.

  python3 src/stage_audit.py --runs-root RUNS --out RUNS/audit

Copies, for each arm, the final work/ directory (from the last task, M2) and every task's output/,
all sealed law snapshots and rule pins, the runtime adapter, sophon.py and USAGE.md (read-only use),
and writes PROMPT.md from inputs/prompts/T4_AUDIT.md. No held_out/ material is staged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ORDER = ["T0", "T1a", "T1b", "R1", "R2", "R3", "R4", "R5", "M0", "M1", "M2"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    runs, out = Path(a.runs_root).resolve(), Path(a.out).resolve()
    if out.exists():
        if not a.force:
            raise SystemExit(f"{out} exists")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for arm in ("A", "B"):
        last = None
        for t in TASK_ORDER:
            if (runs / arm / t / "work").exists():
                last = runs / arm / t / "work"
            if (runs / arm / t / "output").exists():
                shutil.copytree(runs / arm / t / "output", out / "arms" / arm / "outputs" / t)
        if last is None:
            raise SystemExit(f"no work dir for arm {arm}")
        shutil.copytree(last, out / "arms" / arm / "work")
        (out / "arms" / arm / "WORK_SOURCE.txt").write_text(f"copied from {last}\n", encoding="utf-8")
    shutil.copytree(ROOT / "inputs" / "law", out / "inputs" / "law")
    shutil.copytree(ROOT / "inputs" / "rules", out / "inputs" / "rules")
    (out / "src").mkdir()
    for f in ("publicodes_eval.mjs", "package.json", "package-lock.json", "sophon.py", "USAGE.md"):
        shutil.copy2(ROOT / "src" / f, out / "src" / f)
    shutil.copytree(ROOT / "src" / "node_modules", out / "src" / "node_modules", symlinks=True)
    (out / "output").mkdir()
    prompt = (ROOT / "inputs" / "prompts" / "T4_AUDIT.md").read_text(encoding="utf-8").replace("{STAGE}", str(out))
    (out / "PROMPT.md").write_text(prompt, encoding="utf-8")
    files = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob("*")) if p.is_file() and "node_modules" not in p.parts}
    json.dump({"files": files, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}, open(out / "STAGE_MANIFEST.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps({"stage": str(out), "files": len(files)}))


if __name__ == "__main__":
    main()
