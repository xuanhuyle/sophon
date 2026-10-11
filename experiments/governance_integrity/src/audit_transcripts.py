#!/usr/bin/env python3
"""Audit solver transcripts for leakage and count their cost (PROTOCOL.md §7, §8).

  python3 src/audit_transcripts.py --transcript agent-<id>.jsonl --stage /path/to/stage [--out report.json]

Reads a Claude Code subagent transcript (JSONL). For every tool_use it records the tool name and,
for Bash, the command. It flags:
  NETWORK   : git clone/fetch/pull/ls-remote, curl, wget, npm (except `npm` inside the stage's src with no network verbs), pip, uv, fetch, ssh, scp
  OUTSIDE   : any absolute path in a command or file tool input that is not under the staging directory
              (system binaries /usr, /bin, /tmp/… inside stage, and /dev/null are allowed)
  GIT       : any `git` command at all (solvers have no repository to inspect)
  HELD_OUT  : the strings 'held_out', 'REFERENCE.json', 'COVERAGE.json', 'maintainers/'
A run with any NETWORK, GIT, HELD_OUT or OUTSIDE flag is CONTAMINATED unless the orchestrator
documents a benign cause (for example `node --version`). Counts: tool calls total and by tool,
assistant turns, and token usage where the transcript carries it.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NET = re.compile(r"\b(git\s+(clone|fetch|pull|ls-remote|remote|push)|curl|wget|pip3?\s+install|uv\s+pip|npm\s+(install|view|pack|i)\b|npx\b|ssh\b|scp\b|fetch\()", re.I)
# a git *command*: `git` at a command position (start of line/segment), followed by a subcommand.
# Prose such as "a git diff" or "git-quoted paths" inside heredocs does not match.
GIT = re.compile(r"(?:^|[;&|(\n`])\s*git\s+(?:-C\s+\S+\s+)?(clone|fetch|pull|push|log|show|diff|checkout|status|ls-remote|remote|rev-parse|archive|cat-file|ls-tree|ls-files|init|add|commit|grep|branch|tag|stash|worktree|blame|describe)\b", re.I)
HELD = re.compile(r"held_out|REFERENCE\.json|COVERAGE\.json|maintainers/", re.I)
# an absolute path starts at the beginning, after whitespace, a quote, '=', '(' or ',' — never after '*', '%', '€', a digit or a letter
ABS = re.compile(r"(?:(?<=^)|(?<=[\s'\"=(,]))(/[A-Za-z_.][^\s'\"`;|&)>]*)")
ALLOWED_PREFIXES = ("/usr/", "/bin/", "/sbin/", "/dev/", "/etc/", "/lib", "/opt/", "/proc/", "/sys/", "/root/.npm", "/root/.cache", "/root/.node")
ROOTS = ("/tmp", "/root", "/home", "/etc", "/usr", "/var", "/opt", "/mnt", "/srv", "/dev", "/proc", "/sys", "/bin", "/lib", "/boot", "/run", "/sbin", "/snap")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    stage = str(Path(a.stage).resolve())
    tools, flags, bash_cmds, turns, usage = {}, [], [], 0, {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for line in open(a.transcript, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "assistant":
            turns += 1
            u = m.get("usage") or {}
            for k in usage:
                usage[k] += int(u.get(k) or 0)
        content = m.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            name = c.get("name", "?")
            tools[name] = tools.get(name, 0) + 1
            inp = c.get("input") or {}
            text = json.dumps(inp, ensure_ascii=False)
            if name == "Bash":
                cmd = str(inp.get("command", ""))
                bash_cmds.append(cmd)
                if NET.search(cmd):
                    flags.append({"flag": "NETWORK", "command": cmd[:300]})
                if GIT.search(cmd):
                    flags.append({"flag": "GIT", "command": cmd[:300]})
            if HELD.search(text):
                flags.append({"flag": "HELD_OUT", "tool": name, "input": text[:300]})
            for p in ABS.findall(text):
                p = p.rstrip(".,:")
                if not p.startswith(ROOTS):
                    continue  # a relative fragment such as "$DIR"/règles/x.publicodes, not a root path
                if p.startswith(stage) or p in ("/", "/tmp"):
                    continue
                if ("/tasks/" in p and p.endswith(".output")) or "/tool-results/" in p:
                    continue  # the harness's own persisted tool output (the agent reading its own oversized shell result)
                if p.startswith(ALLOWED_PREFIXES):
                    continue
                flags.append({"flag": "OUTSIDE", "tool": name, "path": p[:300]})
    report = {"transcript": a.transcript, "stage": stage, "assistant_turns": turns, "tool_calls_total": sum(tools.values()), "tool_calls_by_tool": tools,
              "usage": usage, "flags": flags, "contaminated": bool(flags), "bash_commands": bash_cmds}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump(report, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "bash_commands"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
