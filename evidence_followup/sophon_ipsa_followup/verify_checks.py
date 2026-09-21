"""Verify source identity and that every manually coded case points to source text.

This verifies traceability, not correctness of the analyst's interpretation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "sophon_cases" / "data"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).casefold()


def main() -> None:
    inventory = json.loads((ROOT / "corpus_audit.json").read_text())["documents"]
    checks = json.loads((ROOT / "case_checks.json").read_text())
    assert len(checks) == 13
    for c in checks:
        doc = inventory[c["document"] - 1]
        suffix = "_ocr.txt" if doc["extraction"] == "ocr" else ".txt"
        text = norm((DATA / (doc["token"] + suffix)).read_text(errors="replace"))
        for anchor in c["anchors"]:
            assert norm(anchor) in text, (doc["index"], anchor)
    print(f"Verified {len(checks)} curated source checks and {sum(len(c['anchors']) for c in checks)} trace anchors. Analyst classifications remain qualitative.")


if __name__ == "__main__":
    main()
