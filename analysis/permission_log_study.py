"""PROPOSED next experiment - not yet run beyond a smoke test on this project's own session.

Question: in a real agent workload under a real authority holder, how fast does "settle each new kind of action once"
turn into autonomy, as a function of how far each settlement is allowed to generalize?

Why this corpus: Claude Code already is the Sophon loop in miniature. An agent proposes actions; a gateway mediates every
one; the human resolves an escalation either once ("allow") or as a standing, scoped grant ("always allow"); grants are
versioned in settings files. The transcripts record every action with its exact decision-time inputs.

Privacy: reads ~/.claude/projects/<project>/*.jsonl locally. It NEVER prints or stores a command, path, URL or prompt.
Every class key is reduced to a tool name plus, for Bash, the program name if it is on a short allowlist of common
programs (otherwise "other"), plus a salted hash for the finer levels. Output is counts only.

  python -B analysis/permission_log_study.py --project C--Claude-sophon        # smoke test: this project only
  python -B analysis/permission_log_study.py --all                             # needs the owner's go-ahead
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HOME = Path.home() / ".claude" / "projects"
OUT = Path(__file__).resolve().parents[1] / "results"
COMMON = {"git", "ls", "cd", "cat", "python", "python3", "py", "pip", "npm", "npx", "node", "pytest", "grep", "rg", "find", "sed",
          "awk", "head", "tail", "mkdir", "rm", "cp", "mv", "echo", "curl", "gh", "docker", "make", "cargo", "go", "uv", "which",
          "wc", "sort", "diff", "touch", "chmod", "tar", "unzip", "sha256sum", "pdftotext", "powershell", "pwsh"}
SALT = "sophon-permission-study-v1"


def h(s: str) -> str:
    return hashlib.sha256((SALT + s).encode()).hexdigest()[:10]


def classes(name: str, inp: dict) -> dict[str, tuple]:
    if name in ("Bash", "PowerShell"):
        cmd = str(inp.get("command", "")).strip()
        parts = [s.strip() for s in re.split(r"[;&|\n]+", cmd) if s.strip()]
        while len(parts) > 1 and re.match(r"(cd|Set-Location|pushd)\b", parts[0]):   # "cd X && real command"
            parts = parts[1:]
        first = parts[0] if parts else ""                              # the first simple command that is not a cd
        toks = first.split()
        while toks and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", toks[0]):   # skip VAR=x prefixes
            toks = toks[1:]
        prog = (toks[0].split("/")[-1].lower() if toks else "")
        prog = prog if prog in COMMON else "other"
        sub = toks[1] if len(toks) > 1 and not toks[1].startswith("-") else ""
        return {"L1 tool": (name,), "L2 tool+program": (name, prog), "L3 +subcommand(hashed)": (name, prog, h(sub)),
                "L4 exact command(hashed)": (name, h(cmd))}
    target = str(inp.get("file_path") or inp.get("url") or inp.get("path") or inp.get("pattern") or "")
    ext = Path(target).suffix.lower()[:6] if name in ("Read", "Write", "Edit") else ""
    return {"L1 tool": (name,), "L2 tool+program": (name, ext), "L3 +subcommand(hashed)": (name, ext, h(str(Path(target).parent))),
            "L4 exact command(hashed)": (name, h(json.dumps(inp, sort_keys=True, default=str)))}


def stream(files: list[Path]):
    events = []
    for f in files:
        for line in f.open(encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            msg = o.get("message")
            if o.get("type") != "assistant" or not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
                continue
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    events.append((o.get("timestamp") or "", b.get("name") or "?", b.get("input") or {}))
    events.sort(key=lambda e: e[0])
    return events


def curve(keys: list[tuple]) -> dict:
    seen, flags = set(), []
    for k in keys:
        flags.append(k in seen)
        seen.add(k)
    n, counts = len(keys), Counter(keys)
    q = max(1, n // 4)
    return {"actions": n, "distinct_classes(=settlements)": len(counts), "covered_overall": round(sum(flags) / n, 3),
            "covered_by_quarter": [round(sum(flags[i * q:(i + 1) * q]) / q, 3) for i in range(4)],
            "share_of_settlements_never_reused": round(sum(c == 1 for c in counts.values()) / len(counts), 3),
            "median_actions_per_settlement": sorted(counts.values())[len(counts) // 2]}


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--project")
    g.add_argument("--all", action="store_true")
    a = ap.parse_args()
    dirs = [d for d in HOME.iterdir() if d.is_dir()] if a.all else [HOME / a.project]
    files = [f for d in dirs for f in d.glob("*.jsonl")]
    ev = stream(files)
    if not ev:
        raise SystemExit("no tool calls found")
    per_level: dict[str, list] = {}
    for _, name, inp in ev:
        for level, key in classes(name, inp).items():
            per_level.setdefault(level, []).append(key)
    result = {"projects": len(dirs), "sessions": len(files), "scope": "all" if a.all else a.project,
              "tools": dict(Counter(n for _, n, _ in ev).most_common(12)),
              "levels": {lvl: curve(keys) for lvl, keys in per_level.items()}}
    OUT.mkdir(exist_ok=True)
    name = "permission_log_study_ALL.json" if a.all else "permission_log_study_smoke.json"
    (OUT / name).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{len(ev)} tool calls, {len(files)} session file(s), {len(dirs)} project(s)")
    for lvl, c in result["levels"].items():
        print(f"  {lvl:28s} settlements={c['distinct_classes(=settlements)']:5d} covered={c['covered_overall']:.3f} "
              f"by quarter={c['covered_by_quarter']} never reused={c['share_of_settlements_never_reused']:.2f}")


if __name__ == "__main__":
    main()
