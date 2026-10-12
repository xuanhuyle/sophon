#!/usr/bin/env python3
"""Packet leakage audit (PROTOCOL.md section 6.1).   python3 src/audit_packet.py --packet packet --out evidence/packet_audit.json

Checks the exact solver input and every packet file: (1) no forbidden identifier or answer-key structure from E0/E1
or the E2 reference/scorer; (2) no reference number (any expected or diagnostic value with a decimal point, and any
integer >= 1000) appears; (3) no packet file is byte-identical to any file under experiments/E0_native_adapter,
experiments/E1_predicate_binding or the E2 trusted area; (4) no .git entry or symlink; (5) every 10_upstream/ file
is byte-identical to the pinned upstream file (provenance). Manual review notes are recorded separately in PROTOCOL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
E2 = HERE.parent
EXP = E2.parent
FORBIDDEN = ["LAB-REV-1", "FROZEN_CASES", "EXPECTED.json", "authority_registry", "designated_fields", "P_SETTLEMENT", "P_UNIT_PRICE",
             "B_STATUS", "B_UNIT_PRICE", "REFERENCE.json", "E1_predicate_binding", "E0_native_adapter", "E2_blind_discovery", "Sophon",
             "sophon", "accepted_verdicts", "canonical_query", "expected_by_year", "stratum", "e2_oracle", "reference answer",
             "correct answer", "PASS_KNOWN_BINDING", "PASS_NATIVE_RUNTIME", "misleading_near_match", "representable_positive",
             "missing_fact_with_tempting_proxy", "source_present_not_natively_exposed", "semantic_ambiguity"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def numbers(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            numbers(v, out)
    elif isinstance(obj, str) and re.fullmatch(r"-?\d+(\.\d+)?", obj):
        if "." in obj or int(obj) >= 1000:
            out.add(obj)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pk = Path(a.packet)
    solver_input = (pk / "solver_input.txt").read_text(encoding="utf-8")
    files = [p for p in pk.rglob("*") if p.is_file()]
    rep = {"solver_input_sha256": sha(solver_input.encode()), "solver_input_bytes": len(solver_input.encode()), "packet_files": len(files)}
    rep["forbidden_strings_found"] = {s: solver_input.count(s) for s in FORBIDDEN if s in solver_input}
    ref = json.loads((E2 / "REFERENCE.json").read_text(encoding="utf-8"))
    nums: set[str] = set()
    for c in ref["cases"].values():
        numbers(c.get("expected_by_year", {}), nums)
    numbers({k: v for k, v in ref["validation"].items()}, nums)
    rep["reference_numbers_checked"] = len(nums)
    rep["reference_numbers_found"] = sorted(n for n in nums if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", solver_input))
    trusted = [p for d in (EXP / "E0_native_adapter", EXP / "E1_predicate_binding") for p in d.rglob("*")
               if p.is_file() and ".upstream" not in p.parts and "runs" not in p.parts]
    trusted += [E2 / "REFERENCE.json", E2 / "CASES.json"] + [p for p in (E2 / "src").glob("*.py")]
    th = {sha(p.read_bytes()): str(p.relative_to(EXP)) for p in trusted}
    rep["packet_files_identical_to_trusted_files"] = [str(f.relative_to(pk)) + " == " + th[sha(f.read_bytes())] for f in files if sha(f.read_bytes()) in th]
    rep["git_or_symlink_entries"] = [str(p) for p in pk.rglob("*") if p.is_symlink() or p.name == ".git"]
    up = E2 / ".upstream"
    prov = {}
    for f in (pk / "10_upstream").rglob("*"):
        if f.is_file():
            rel = f.relative_to(pk / "10_upstream")
            prov[str(rel)] = sha(f.read_bytes()) == sha((up / rel).read_bytes())
    rep["upstream_files_byte_identical_to_pin"] = all(prov.values())
    rep["upstream_files"] = len(prov)
    rep["ok"] = (not rep["forbidden_strings_found"] and not rep["reference_numbers_found"] and not rep["packet_files_identical_to_trusted_files"]
                 and not rep["git_or_symlink_entries"] and rep["upstream_files_byte_identical_to_pin"])
    Path(a.out).write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
