"""Build structural records from locally downloaded raw documents (never committed).

    python corpus.py --raw-dir <dir with ca/*.htm and sla/*.html> --split TRAIN   # writes data/records_train.json
    python corpus.py --raw-dir <dir> --split HELDOUT                                # only after frozen/freeze_receipt.json exists

A record keeps literal headings, source order, nesting, rule-assigned labels and SHA-256 receipts; no
full text. Heldout records are built only after the label rules, vocabulary and predictor are frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import extract
import labels

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "data" / "source_manifest.json"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_record(src: dict, raw_bytes: bytes) -> dict:
    raw = extract.decode(raw_bytes)
    rec = {"doc_id": src["doc_id"], "family": src["family"], "split": src["split"],
           "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(), "label_rules": labels.VERSION}
    if rec["raw_sha256"] != src["sha256"]:
        raise ValueError(f"{src['doc_id']}: raw file hash differs from frozen manifest")
    if src["family"] == "CREDIT_AGREEMENT":
        st = extract.credit_agreement_structure(raw)
        sections = []
        for u in st["units"]:
            subs = [{"path": f"Section {s['num']}", "heading": s["heading"], "provision_type": labels.ca_provision_type(s["heading"])}
                    for s in u["subunits"]]
            sections.append({"path": f"Article {u['num']}", "heading": u["heading"],
                             "functions": [labels.ca_section_function(u["heading"])], "subunits": subs})
    else:
        st = extract.sla_structure(raw)
        sections = [{"path": f"Unit {k + 1}", "heading": u["heading"], "kind": u["kind"],
                     "functions": labels.sla_unit_functions(u["heading"], u["text"]),
                     "unit_text_sha256": sha256_text(u["text"]), "subunits": []}
                    for k, u in enumerate(st["units"])]
    law = labels.evidenced_governing_law(st["full_text"])
    law_paths = [s["path"] for s in sections if any(p["provision_type"] == "GOVERNING_LAW_JURISDICTION" for p in s["subunits"])]
    rec.update({"segmentation": st["segmentation"], "segmentation_notes": st["notes"], "sections": sections,
                "governing_law": {"value": law["law"], "evidence_excerpt": law["evidence"], "evidence_section_paths": law_paths,
                                  "status": "EVIDENCED_CHOICE_OF_LAW_CLAUSE" if law["law"] != "UNKNOWN" else "UNKNOWN_NOT_IN_DOCUMENT"}})
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--split", choices=["TRAIN", "HELDOUT"], required=True)
    a = ap.parse_args()
    if a.split == "HELDOUT" and not (HERE / "frozen" / "freeze_receipt.json").exists():
        raise SystemExit("refusing to build heldout records before the freeze receipt exists")
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recs = []
    for src in man["documents"]:
        if src["split"] != a.split:
            continue
        sub = "ca" if src["family"] == "CREDIT_AGREEMENT" else "sla"
        recs.append(build_record(src, (Path(a.raw_dir) / sub / src["local_file"]).read_bytes()))
    out = HERE / "data" / f"records_{a.split.lower()}.json"
    out.write_text(json.dumps({"label_rules": labels.VERSION, "records": recs}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out.name}: {len(recs)} records")


if __name__ == "__main__":
    main()
