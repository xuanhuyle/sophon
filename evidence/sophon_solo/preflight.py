"""Validate immutable inputs and fail closed before the owner adopts the sandbox."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    policy = ROOT / "draft_policy.md"
    cases = ROOT / "cases.csv"
    if hashlib.sha256(policy.read_bytes()).hexdigest() != manifest["draft_policy_sha256"]:
        raise ValueError("Draft policy differs from frozen input")
    if hashlib.sha256(cases.read_bytes()).hexdigest() != manifest["cases_sha256"]:
        raise ValueError("Case corpus differs from frozen input")
    with cases.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != manifest["case_count"]:
        raise ValueError("Case count mismatch")
    if manifest["status"] != "DRAFT_UNADOPTED":
        raise ValueError("This preflight handles the unadopted fixture only")
    return {"cases": len(rows), "decision": "REQUEST_AUTHORITY", "count": len(rows),
            "reason": "sandbox owner has not adopted the draft policy; no normative root exists"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
