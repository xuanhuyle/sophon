#!/usr/bin/env python3
"""Stage one (arm, task) run directory outside the repository, with only the inputs the protocol allows.

  python3 src/stage_task.py --arm A --task T1a --runs-root /path/outside/repo [--from-work PREV_RUN/work]

Creates <runs-root>/<arm>/<task>/ with:
  src/                 copy of the runtime adapter (+ node_modules) and, for arm B, sophon.py and USAGE.md
  inputs/law/<S>/      only the snapshot(s) the task allows
  inputs/rules/<G>/    only the pin the task allows
  inputs/diffs/<R>/    only for reverse tasks
  work/                the arm's persistent directory carried forward (copied from --from-work), or empty
  output/              empty, for the arm's deliverables
  PROMPT.md            the frozen prompt templates filled for this task
  STAGE_MANIFEST.json  sha256 of every staged file and of the prompt

The staged directory has no .git and no held_out/. Solvers are pointed only at it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_dir(base: Path, prefix: str) -> Path:
    cands = [d for d in base.iterdir() if d.name.startswith(prefix + "_")]
    if len(cands) != 1:
        raise SystemExit(f"expected one {prefix}_* under {base}, found {cands}")
    return cands[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["A", "B"])
    ap.add_argument("--task", required=True)
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--from-work", help="previous run's work/ directory to carry forward")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    tasks = {t["task"]: t for t in json.load(open(ROOT / "inputs" / "TASKS.json", encoding="utf-8"))}
    if a.task not in tasks:
        raise SystemExit(f"unknown task {a.task}; known: {sorted(tasks)}")
    t = tasks[a.task]
    stage = Path(a.runs_root).resolve() / a.arm / a.task
    if stage.exists():
        if not a.force:
            raise SystemExit(f"{stage} exists; refusing to overwrite a run")
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # src: adapter for both arms, store CLI only for B
    (stage / "src").mkdir()
    for f in ("publicodes_eval.mjs", "package.json", "package-lock.json"):
        shutil.copy2(ROOT / "src" / f, stage / "src" / f)
    shutil.copytree(ROOT / "src" / "node_modules", stage / "src" / "node_modules", symlinks=True)
    if a.arm == "B":
        shutil.copy2(ROOT / "src" / "sophon.py", stage / "src" / "sophon.py")
        shutil.copy2(ROOT / "src" / "USAGE.md", stage / "src" / "USAGE.md")

    # inputs
    law_dirs = []
    for s in t["law"]:
        d = find_dir(ROOT / "inputs" / "law", s)
        shutil.copytree(d, stage / "inputs" / "law" / d.name)
        law_dirs.append(f"inputs/law/{d.name}")
    rdir = find_dir(ROOT / "inputs" / "rules", t["rules"])
    shutil.copytree(rdir, stage / "inputs" / "rules" / rdir.name)
    rmeta = json.load(open(rdir / "meta.json", encoding="utf-8"))
    diff_section, diff_id, diff_ctx = "", "", ""
    if t["diff"]:
        ddir = find_dir(ROOT / "inputs" / "diffs", t["diff"])
        shutil.copytree(ddir, stage / "inputs" / "diffs" / ddir.name)
        diff_id = ddir.name
        has_ctx = (ddir / "context_parent_tree").exists()
        diff_section = (f"- `inputs/diffs/{ddir.name}/`: the semantic change under review (`diff.patch`, `stat.txt`, `meta.json`"
                        + (", plus `context_parent_tree/` and `context_tree_after/` with the rule trees of the packages the diff touches, before and after)" if has_ctx else ")") + ".")
        diff_ctx = (", plus `context_parent_tree/` and `context_tree_after/`: the `modele-ti` and `modele-commun` rule trees before and after, "
                    "which you can `build` and `evaluate` with `--rules <dir>/modele-ti/règles --rules <dir>/modele-commun/règles`") if has_ctx else ""

    # work, output
    if a.from_work:
        shutil.copytree(Path(a.from_work), stage / "work")
    else:
        (stage / "work").mkdir()
    (stage / "output").mkdir()

    # prompt
    P = ROOT / "inputs" / "prompts"
    common = (P / "COMMON.md").read_text(encoding="utf-8")
    kind = a.task if a.task in ("T0", "T1a", "T1b") else ("R" if a.task.startswith("R") else "M")
    task_tpl = (P / f"{kind}.md").read_text(encoding="utf-8")
    arm_tpl = (P / "ARM_B_ADDENDUM.md").read_text(encoding="utf-8") if a.arm == "B" else "## Your tools\n\nYou have the engine wrapper above and ordinary file tools. Keep whatever records you find useful in `work/`.\n"
    law_snaps = ", ".join(t["law"])
    fill = {
        "{STAGE}": str(stage), "{DECISION_DATE}": t["decision_date"], "{LAW_SNAPS}": law_snaps, "{RULES_PIN}": t["rules"],
        "{RULES_COMMIT}": rmeta["commit"][:12], "{RULES_DATE}": rmeta["committed"], "{DIFF_SECTION}": diff_section, "{TASK}": a.task,
        "{DIFF_ID}": diff_id, "{DIFF_CONTEXT_NOTE}": diff_ctx, "{LAW_PREV}": t["law"][0], "{LAW_NEW}": t["law"][-1],
    }
    task_text = task_tpl
    for k, v in fill.items():
        task_text = task_text.replace(k, v)
    prompt = common.replace("{TASK_SECTION}", task_text).replace("{ARM_SECTION}", arm_tpl)
    for k, v in fill.items():
        prompt = prompt.replace(k, v)
    (stage / "PROMPT.md").write_text(prompt, encoding="utf-8")

    files = {str(p.relative_to(stage)): sha256_file(p) for p in sorted(stage.rglob("*")) if p.is_file() and "node_modules" not in p.parts}
    manifest = {"arm": a.arm, "task": a.task, "decision_date": t["decision_date"], "law": t["law"], "rules": t["rules"], "diff": t["diff"],
                "from_work": a.from_work, "prompt_sha256": sha256_file(stage / "PROMPT.md"),
                "template_sha256": {f.name: sha256_file(f) for f in sorted(P.glob("*.md"))}, "files": files}
    json.dump(manifest, open(stage / "STAGE_MANIFEST.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({"stage": str(stage), "files": len(files), "prompt_sha256": manifest["prompt_sha256"], "law": t["law"], "rules": t["rules"], "diff": t["diff"]}))


if __name__ == "__main__":
    main()
