"""Reproduce the document-level IPSA source and language audit.

Keyword hits are navigation aids. They are not legal-effect classifications.
Run from any directory: python sophon_ipsa_followup/audit.py
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT.parent / "sophon_cases"
DOCS = json.loads((CORPUS / "corpus_inventory.json").read_text())["documents"]

PATTERNS = {
    "precedent_language": r"\bpreceden(?:t|ce|ts)\b",
    "other_case_or_practice": r"\b(?:similar claims?|previous claims?|other MPs?|another MP|other members?|previously paid|previous review|recent review|same subject|consistent|inconsistent)\b",
    "future_or_change": r"\b(?:future claims?|next edition|new edition|guidance|the Scheme)\b.{0,70}\b(?:chang(?:ed|es?|ing)|clarif(?:y|ied|ication)|updat(?:e|ed)|amend(?:ed|ment)?)\b|\b(?:chang(?:ed|es?|ing)|clarif(?:y|ied|ication)|updat(?:e|ed)|amend(?:ed|ment)?)\b.{0,70}\b(?:future claims?|next edition|new edition|guidance|the Scheme)\b",
    "later_evidence": r"\b(?:additional information|new information|further evidence|was not known|not known to IPSA|following the review)\b",
}


def main() -> None:
    rows = []
    for i, doc in enumerate(DOCS, 1):
        token = doc["local_text_token"]
        pdf = CORPUS / "data" / (token + ".pdf")
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == doc["sha256"], f"PDF changed: {token}"
        text_file = CORPUS / "data" / (token + ("_ocr.txt" if i == 45 else ".txt"))
        content = text_file.read_text(encoding="utf-8", errors="replace")
        if i == 45:
            assert len(content) > 20000, "The tribunal PDF requires OCR"
        else:
            assert len(content) >= 500, f"Text extraction is incomplete: {token}"
        pages = content.split("\f")
        if pages and not pages[-1].strip():
            pages.pop()
        hits = {}
        for label, pattern in PATTERNS.items():
            matches = []
            for page, body in enumerate(pages, 1):
                for match in re.finditer(pattern, body, re.IGNORECASE | re.DOTALL):
                    start, end = match.span()
                    snippet = " ".join(body[max(0, start - 90):min(len(body), end + 110)].split())
                    matches.append({"page": page, "snippet": snippet})
            hits[label] = matches
        kind = ("tribunal" if i == 45 else "provisional" if "Provisional" in doc["title"]
                else "short_summary" if i == 10 else "review_or_finding")
        rows.append({"index": i, "title": doc["title"], "url": doc["url"],
                     "sha256": doc["sha256"], "pdf_pages": len(pages),
                     "text_characters": len(content), "extraction": "ocr" if i == 45 else "pdftotext",
                     "document_kind": kind, "token": token, "hits": hits})
    payload = {"method": "All 46 links from frozen official completed-reviews index. Verified local PDF hashes; OCR of indexed tribunal PDF. Regex hits are not legal or policy classifications.", "documents": rows}
    (ROOT / "corpus_audit.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print("Documents:", len(rows), "Kinds:", dict(Counter(x["document_kind"] for x in rows)))
    for label in PATTERNS:
        positive = [x["index"] for x in rows if x["hits"][label]]
        print(label, "document hits:", len(positive), positive)


if __name__ == "__main__":
    main()
