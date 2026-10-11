#!/usr/bin/env python3
"""Mechanically check the T4 auditor's reconstruction against the sealed inputs and the arms' artifacts.

  python3 src/verify_audit.py --audit RUNS/audit --out results/audit_verification.json

For every Q1 field of each arm: does the cited source_path exist in the staged artifacts; does any
64-hex digest quoted in the value match the sha256 of a cited file or a sealed rule file; do the
article version id and in-force date match a sealed law snapshot (D131-6-1); does the snapshot named
contain that version. For Q2/Q3 it records whether the auditor's answer has the truthful shape
("not preserved" / "no approval found") and whether any approval claim exists. The judgement
VERIFIED / ASSERTED_ONLY / WRONG per field is then written by the orchestrator in AUDIT_REPORT.md
using this output plus the auditor's own `verification` labels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HEX = re.compile(r"\b[0-9a-f]{64}\b")
LEGI = re.compile(r"LEGIARTI\d{12}")
DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


def law_versions(stage: Path, article: str) -> dict:
    out = {}
    for d in sorted((stage / "inputs" / "law").iterdir()):
        j = json.load(open(d / "articles.json", encoding="utf-8"))
        rec = (j["articles"].get(article) or [None])[0]
        if rec:
            import datetime as dt
            out.setdefault(rec["id"], {"snapshots": [], "dateDebut": dt.datetime.fromtimestamp(rec["dateDebut"] / 1000, dt.timezone.utc).date().isoformat(), "text_sha256": rec["text_sha256"]})
            out[rec["id"]]["snapshots"].append(j["snapshot"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    stage = Path(a.audit).resolve()
    audit = json.load(open(stage / "output" / "audit.json", encoding="utf-8"))
    d131 = law_versions(stage, "D131-6-1")
    d613 = law_versions(stage, "D613-4")
    report = {"Q1": {}, "Q2": {}, "Q3": {}, "law_versions": {"D131-6-1": d131, "D613-4": d613}}
    for arm in ("A", "B"):
        q1 = (audit.get("Q1") or {}).get(arm) or {}
        rows = {}
        for field, f in (q1.get("fields") or {}).items():
            if not isinstance(f, dict):
                continue
            val = json.dumps(f.get("value"), ensure_ascii=False)
            row = {"auditor_label": f.get("verification"), "source_path": f.get("source_path")}
            sp = f.get("source_path")
            if sp:
                # the auditor cites several paths per field, with annotations: "arms/A/outputs/M2/answer.json (rules[*]); arms/A/work/README.md ('Key state')"
                cands = [c for c in re.findall(r"[A-Za-z0-9_./\-§]+/[A-Za-z0-9_.\-§]+", str(sp)) if "/" in c]
                checked = {}
                for c in dict.fromkeys(cands):
                    c2 = c.split("§")[0].rstrip(".,;:")
                    if not (stage / c2.split("/")[0]).is_dir():
                        continue  # a JSON path fragment such as "changed_articles[0].new/nota", not a file path
                    checked[c2] = (stage / c2).exists()
                row["source_paths_checked"] = checked
                row["source_exists"] = bool(checked) and all(checked.values())
                row["source_paths_missing"] = [c for c, ok in checked.items() if not ok]
            digests = HEX.findall(val + " " + json.dumps(f.get("how", ""), ensure_ascii=False))
            if digests:
                row["digests_quoted"] = digests
                known = set()
                for p in stage.rglob("*"):
                    if p.is_file() and "node_modules" not in p.parts:
                        h = hashlib.sha256(p.read_bytes()).hexdigest()
                        if h in digests:
                            known.add((h, str(p.relative_to(stage))))
                # also text hashes of articles
                for ver, info in {**d131, **d613}.items():
                    if info["text_sha256"] in digests:
                        known.add((info["text_sha256"], f"article text {ver}"))
                row["digests_resolved"] = sorted(known)
            ids = LEGI.findall(val)
            if ids:
                row["legiarti_ids"] = ids
                row["ids_in_D131-6-1_snapshots"] = {i: d131.get(i, {}).get("snapshots") for i in ids}
            dates = DATE.findall(val)
            if dates:
                row["dates"] = dates
            rows[field] = row
        report["Q1"][arm] = {"fields": rows, "summary": q1.get("summary")}
        q2 = (audit.get("Q2") or {}).get(arm) or {}
        report["Q2"][arm] = {"preserved": q2.get("preserved"), "cited_only": q2.get("cited_only"), "absent": q2.get("absent"), "mentions_D756_5": "D756-5" in json.dumps(q2, ensure_ascii=False), "mentions_urssaf_pdf": "pdf" in json.dumps(q2, ensure_ascii=False).lower()}
        q3 = (audit.get("Q3") or {}).get(arm) or {}
        report["Q3"][arm] = {"approval_found": q3.get("approval_found"), "what_exists_instead": q3.get("what_exists_instead"), "truthful_shape": q3.get("approval_found") is False}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(report, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"Q1_fields": {arm: {k: (v.get("auditor_label"), v.get("source_exists"), bool(v.get("digests_resolved"))) for k, v in report["Q1"][arm]["fields"].items()} for arm in ("A", "B")},
                      "Q3": {arm: report["Q3"][arm]["truthful_shape"] for arm in ("A", "B")}}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
