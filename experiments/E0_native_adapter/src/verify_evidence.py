#!/usr/bin/env python3
"""Fresh-process re-check of an E0 run receipt (PROTOCOL.md S11). Holds no state from the run.

    .upstream/.venv/bin/python src/verify_evidence.py --upstream .upstream --receipt evidence/run/run_receipt.json --out evidence/fresh_check.json

Checks, independently of src/run_e0.py: the upstream commit; the sha256 of the warehouse, semantic manifest and dbt
manifest against the receipt; that the `mf` entry point is the one recorded and matches its distribution RECORD;
that the committed copy of the semantic manifest equals the live one; then re-runs the recorded native argv with
subprocess (not through the adapter's query function) and compares the CSV byte-for-byte with the recorded result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mf_adapter as mfa  # noqa: E402  (used only for path resolution and the RECORD identity check)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rec = json.loads(Path(a.receipt).read_text(encoding="utf-8"))
    rdir = Path(a.receipt).parent
    p = mfa.open_project(a.upstream)
    checks: dict = {"pid": os.getpid(), "receipt": str(a.receipt)}
    checks["commit_matches"] = subprocess.run(["git", "-C", str(p.upstream), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() == rec["upstream_commit"]
    fp_rec = rec["S7_query"]["receipt"]["fingerprints_before"]
    fp_now = mfa.fingerprints(p)
    checks["fingerprints_match"] = {k: fp_now[k] == fp_rec[k] for k in fp_rec}
    ident = mfa.mf_identity(p)
    checks["mf_entry_point_matches"] = ident["mf_sha256"] == rec["mf_identity"]["mf_sha256"] and ident["record_hash"] == rec["mf_identity"]["record_hash"]
    checks["committed_semantic_manifest_matches_live"] = sha(rdir / "semantic_manifest.json") == fp_now["semantic_manifest_sha256"]
    argv = rec["S7_query"]["receipt"]["argv"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "fresh.csv"
        cmd = [str(p.mf), *[out.as_posix() if x == "<csv>" else x for x in argv[1:]]]
        proc = subprocess.run(cmd, cwd=str(p.dbt_dir), env=p.env(), capture_output=True, text=True)
        fresh = out.read_text(encoding="utf-8") if out.exists() else None
    recorded = (rdir / "query_result.csv").read_text(encoding="utf-8")
    checks["rerun"] = {"argv": argv, "exit_code": proc.returncode, "csv_written": fresh is not None,
                       "csv_identical_to_recorded": fresh == recorded, "recorded_csv_sha256": mfa.sha256_text(recorded),
                       "fresh_csv_sha256": mfa.sha256_text(fresh) if fresh is not None else None}
    checks["fingerprints_after_rerun_match"] = {k: v == fp_rec[k] for k, v in mfa.fingerprints(p).items()}
    checks["ok"] = bool(checks["commit_matches"] and all(checks["fingerprints_match"].values()) and checks["mf_entry_point_matches"]
                        and checks["committed_semantic_manifest_matches_live"] and proc.returncode == 0 and fresh == recorded)
    Path(a.out).write_text(json.dumps(checks, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=1))
    sys.exit(0 if checks["ok"] else 1)


if __name__ == "__main__":
    main()
