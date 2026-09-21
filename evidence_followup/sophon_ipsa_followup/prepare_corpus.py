"""Fetch frozen official PDFs, verify SHA-256, and extract text for the audit.

Requires pdftotext, pdftoppm and tesseract. Existing verified files are reused.
The source URLs and hashes come from the frozen inventory, not the live index.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "sophon_cases"
DATA = ROOT / "data"


def main() -> None:
    docs = json.loads((ROOT / "corpus_inventory.json").read_text())["documents"]
    assert len(docs) == 46
    DATA.mkdir(parents=True, exist_ok=True)
    for i, doc in enumerate(docs, 1):
        token = doc["local_text_token"]
        pdf = DATA / (token + ".pdf")
        if not pdf.exists():
            with urllib.request.urlopen(doc["url"], timeout=50) as response:
                pdf.write_bytes(response.read())
        actual = hashlib.sha256(pdf.read_bytes()).hexdigest()
        assert actual == doc["sha256"], f"Official PDF changed for document {i}; inspect before continuing"
        if i == 45:
            out = DATA / (token + "_ocr.txt")
            if not out.exists() or len(out.read_text(errors="replace")) < 20000:
                with tempfile.TemporaryDirectory() as directory:
                    stem = Path(directory) / "page"
                    subprocess.run(["pdftoppm", "-r", "130", "-gray", "-png", str(pdf), str(stem)], check=True, stdout=subprocess.DEVNULL)
                    pages = []
                    for image in sorted(Path(directory).glob("page-*.png")):
                        pages.append(subprocess.run(["tesseract", str(image), "stdout", "-l", "eng"], check=True, capture_output=True, text=True).stdout)
                    out.write_text("\n\f\n".join(pages), encoding="utf-8")
        else:
            txt = DATA / (token + ".txt")
            if not txt.exists():
                subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
        print(f"{i:02d} verified {doc['title']}")


if __name__ == "__main__":
    main()
