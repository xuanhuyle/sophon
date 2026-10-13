"""POST-FREEZE SECONDARY RUN: segmentation repair only (written AFTER the frozen primary heldout run).

What changes vs the frozen primary run (results/heldout_run.json):
  * CA-MOTOROLA is excluded: its EX-10.1 is a *First Amendment* with a redlined conformed copy attached
    (corpus-screening error found post-freeze). It is replaced by the next unused EX-10 candidate in the
    original EDGAR full-text-search order that passes an amendment screen (3-candidate slot cap):
    Blue Owl Credit Income Corp. (rejected: amendment) -> Old Dominion Electric Cooperative (accepted).
  * SLA-CLOUDFLARE: frozen segmenter found no HTML heading naming the SLA. Fallback used ONLY when the frozen
    segmenter returns SLA_TITLE_NOT_FOUND: content starts at the first plain line naming a Service Level
    Agreement; units split at top-level numbered paragraphs "N. Heading".
Unchanged: label rules, vocabulary, predictor, target selection, masking, metrics and decision rule
(imported from the frozen modules, verified against frozen/freeze_receipt.json).

    python secondary.py --raw-dir <scratch corpus_dl>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import corpus
import extract
import labels
import predict

HERE = Path(__file__).resolve().parent
REPLACEMENT = {"doc_id": "CA-OLDDOMINION", "family": "CREDIT_AGREEMENT", "split": "HELDOUT_REPLACEMENT",
               "issuer": "Old Dominion Electric Cooperative", "source": "SEC EDGAR", "exhibit": "EX-10.1", "cik": "885568",
               "accession": "0000950170-23-069906", "url": "https://www.sec.gov/Archives/edgar/data/885568/000095017023069906/ck0000885568-ex10_1.htm",
               "filing_date": "2023-12-13", "sha256": "aac7e9d04b13e0f9d3a5ed43f5fd73099c46a7409551c50614cf50cd8eb07320",
               "local_file": "olddominion.htm", "title_observed": "SECOND AMENDED AND RESTATED CREDIT AGREEMENT"}
REJECTED = [{"doc": "CA-MOTOROLA 0001193125-23-032815", "reason": "First Amendment with redlined conformed copy (post-freeze finding)"},
            {"doc": "Blue Owl Credit Income Corp. 0001193125-23-282904 d938536dex101.htm",
             "sha256": "2f5769d159ccc099b65a8db9401ddca68fb15bd698eea1b90de9193e9c0337b9", "reason": "amendment screen positive"}]


def sla_numbered_fallback(raw: str) -> dict:
    lines = [extract.clean(l) for l in extract.html_lines(raw)]
    lines = [l for l in lines if l]
    start = next(k for k, l in enumerate(lines) if k > 0 and extract.SLA_TITLE.search(l) and len(l) < 80)
    units = [{"heading": "HEADING_ABSENT", "kind": "OPENING", "text": []}]
    for l in lines[start + 1:]:
        m = re.match(r"^(\d+)\.\s+([A-Z][^.]{2,80}?)(?:\s*\(\"[^\"]+\"\))?\.?(?:\s+(.*))?$", l)
        if m and not re.match(r"^\d+\.\d", l):
            units.append({"heading": f"{m.group(1)}. {m.group(2)}", "kind": "NUMBERED_PARAGRAPH", "text": [m.group(3) or ""]})
        else:
            units[-1]["text"].append(l)
    for u in units:
        u["text"] = " ".join(t for t in u["text"] if t)
    units = [u for u in units if u["text"]]
    last = max(k for k, u in enumerate(units) if extract.SLA_CONTENT.search(u["heading"] + " " + u["text"]))
    return {"units": units[: last + 1], "segmentation": "POST_FREEZE_NUMBERED_PARAGRAPH_FALLBACK",
            "notes": [f"dropped {len(units) - last - 1} trailing units"], "full_text": " ".join(lines[start:])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True)
    a = ap.parse_args()
    receipt = json.loads((HERE / "frozen" / "freeze_receipt.json").read_text(encoding="utf-8"))
    for name, digest in receipt["files"].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, f"{name} changed after freeze"
    frozen = {r["doc_id"]: r for r in json.loads((HERE / "data" / "records_heldout.json").read_text(encoding="utf-8"))["records"]}
    man = {d["doc_id"]: d for d in json.loads((HERE / "data" / "source_manifest.json").read_text(encoding="utf-8"))["documents"]}
    raw_dir = Path(a.raw_dir)
    test = [frozen["CA-MARKEL"], frozen["SLA-MONGODB"]]
    test.append(corpus.build_record(REPLACEMENT, (raw_dir / "ca" / REPLACEMENT["local_file"]).read_bytes()))
    cf = man["SLA-CLOUDFLARE"]
    raw_b = (raw_dir / "sla" / cf["local_file"]).read_bytes()
    assert hashlib.sha256(raw_b).hexdigest() == cf["sha256"]
    st = sla_numbered_fallback(extract.decode(raw_b))
    test.append({"doc_id": cf["doc_id"], "family": cf["family"], "split": "HELDOUT", "raw_sha256": cf["sha256"], "label_rules": labels.VERSION,
                 "segmentation": st["segmentation"], "segmentation_notes": st["notes"],
                 "sections": [{"path": f"Unit {k + 1}", "heading": u["heading"], "kind": u["kind"], "functions": labels.sla_unit_functions(u["heading"], u["text"]),
                               "unit_text_sha256": corpus.sha256_text(u["text"]), "subunits": []} for k, u in enumerate(st["units"])],
                 "governing_law": {"value": labels.evidenced_governing_law(st["full_text"])["law"], "evidence_excerpt": None, "evidence_section_paths": [],
                                   "status": "UNKNOWN_NOT_IN_DOCUMENT"}})
    test.sort(key=lambda r: r["doc_id"])
    (HERE / "data" / "records_heldout_secondary.json").write_text(json.dumps({"label_rules": labels.VERSION, "status": "POST_FREEZE_SEGMENTATION_REPAIR",
        "replacement": REPLACEMENT, "rejected_candidates": REJECTED, "records": test}, indent=1, ensure_ascii=False), encoding="utf-8")
    train = json.loads((HERE / "data" / "records_train.json").read_text(encoding="utf-8"))["records"]
    res = predict.run(train, test)
    res["mode"] = "SECONDARY_POST_FREEZE_SEGMENTATION_REPAIR (not the pre-registered primary)"
    res["decision"] = predict.decide(res)
    (HERE / "results" / "secondary_repaired_run.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for arm in predict.ARMS:
        x = res["summary"][arm]
        print(f"{arm:30s} targets={x['targets']:3d} hit@1={x['hit1']:6.2f} hit@3={x['hit3']:6.2f} falseExp@3={x['false_expectations_top3']:6.2f} "
              f"brier={x['brier_mean']:.4f} by_task={json.dumps(x['by_task'])}")
    print(json.dumps(res["decision"], indent=1))


if __name__ == "__main__":
    main()
