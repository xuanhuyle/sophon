#!/usr/bin/env python3
"""Run the ONE scored blind solver (PROTOCOL.md section 5), or a non-scored diagnostic with --diagnostic-prompt.

    python3 src/run_solver.py --input packet/solver_input.txt --out evidence/solver

Isolation: a fresh `claude -p` process (no --continue/--resume), started with `env -i` and only PATH, HOME, proxy
and CA variables; HOME is a new empty directory holding only the CLI login credential (so no prior transcripts,
memory, settings, skills or plugins of the orchestrating session are reachable); the working directory is a new
empty directory outside any git repository; all tools are disabled (`--tools ""`); `--safe-mode` disables
CLAUDE.md, skills, plugins, hooks, MCP; `--strict-mcp-config` loads no MCP server; `--no-session-persistence`.
The packet is the only user input (stdin). The raw stdout is saved byte-for-byte and never edited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

SYSTEM_PROMPT = "You are a careful data-governance analyst. Answer only from the evidence in the user's message."
MODEL = "claude-opus-5-5"
PASS_ENV = ["HTTPS_PROXY", "https_proxy", "NO_PROXY", "no_proxy", "NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE", "ANTHROPIC_BASE_URL"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--diagnostic-prompt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", default=os.environ.get("E2_SOLVER_SCRATCH", "/tmp/e2_solver"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stdin_bytes = Path(a.input).read_bytes() if a.input else a.diagnostic_prompt.encode()
    scratch = Path(a.scratch)
    if scratch.exists():
        shutil.rmtree(scratch)
    home, cwd = scratch / "home", scratch / "cwd"
    (home / ".claude").mkdir(parents=True)
    cwd.mkdir()
    shutil.copy2(Path.home() / ".claude" / ".credentials.json", home / ".claude" / ".credentials.json")
    os.chmod(home / ".claude" / ".credentials.json", 0o600)
    env = {"PATH": "/opt/node22/bin:/usr/bin:/bin", "HOME": str(home)}
    env.update({k: os.environ[k] for k in PASS_ENV if k in os.environ})
    argv = [shutil.which("claude") or "claude", "-p", "--tools", "", "--no-session-persistence", "--safe-mode", "--strict-mcp-config",
            "--output-format", "json", "--model", MODEL, "--system-prompt", SYSTEM_PROMPT, "--max-budget-usd", "25"]
    version = subprocess.run([argv[0], "--version"], capture_output=True, text=True, env=env, cwd=str(cwd)).stdout.strip()
    pre = sorted(str(p.relative_to(scratch)) for p in scratch.rglob("*"))
    t0 = time.time()
    proc = subprocess.run(argv, input=stdin_bytes, capture_output=True, env=env, cwd=str(cwd), timeout=3600)
    t1 = time.time()
    (out / "raw_output.json").write_bytes(proc.stdout)
    (out / "stderr.txt").write_bytes(proc.stderr)
    post = sorted(str(p.relative_to(scratch)) for p in scratch.rglob("*"))
    meta = {"argv": ["claude", *argv[1:]], "cli_version": version, "model_requested": MODEL,
            "env_variable_names_passed": sorted(env), "home": "<fresh empty dir containing only .claude/.credentials.json>",
            "cwd": "<fresh empty dir outside any git repository>", "stdin_sha256": sha(stdin_bytes), "stdin_bytes": len(stdin_bytes),
            "tools": "none (--tools \"\")", "files_before_run": pre, "files_after_run": post,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)), "wall_seconds": round(t1 - t0, 1),
            "exit_code": proc.returncode, "stdout_sha256": sha(proc.stdout), "stdout_bytes": len(proc.stdout), "stderr_bytes": len(proc.stderr)}
    try:
        env_json = json.loads(proc.stdout)
        meta["envelope"] = {k: env_json.get(k) for k in ("session_id", "total_cost_usd", "usage", "modelUsage", "num_turns", "is_error",
                                                         "stop_reason", "terminal_reason", "permission_denials", "duration_ms", "duration_api_ms")}
    except json.JSONDecodeError:
        meta["envelope"] = None
    (out / "run_meta.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    shutil.rmtree(scratch)  # removes the copied credential
    print(json.dumps({k: meta[k] for k in ("exit_code", "wall_seconds", "stdout_bytes", "stdin_sha256")} | {"cost": (meta["envelope"] or {}).get("total_cost_usd")}, indent=1))


if __name__ == "__main__":
    main()
