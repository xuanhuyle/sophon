"""Index and locally extract the official completed-review PDF corpus."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import html
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "https://www.ipsacompliance.org.uk/investigations/completed-reviews"
DATA = ROOT / "data"


def entries() -> list[dict]:
    page = urllib.request.urlopen(URL, timeout=25).read().decode("utf-8")
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S)
    out = []
    seen = set()
    for href, inner in links:
        title = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if "assets.ctfassets.net" not in href or ".pdf" not in href.lower() or "procedures" in title.lower():
            continue
        source = "https:" + href if href.startswith("//") else href
        if source in seen:
            continue
        seen.add(source)
        out.append({"title": title, "url": source})
    return out


def extract(item: dict) -> dict:
    token = hashlib.sha256(item["url"].encode()).hexdigest()[:16]
    pdf = DATA / f"{token}.pdf"
    txt = DATA / f"{token}.txt"
    try:
        if not pdf.exists():
            with urllib.request.urlopen(item["url"], timeout=35) as r:
                pdf.write_bytes(r.read())
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True, timeout=30, capture_output=True)
        content = txt.read_text(errors="replace")
        item.update({"sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pdf_bytes": pdf.stat().st_size,
                     "text_characters": len(content), "local_text_token": token,
                     "explicit_nonprecedent": bool(re.search(r'not a precedent|no precedent|cannot be used.*future', content, re.I | re.S)),
                     "mentions_exception": bool(re.search(r'exceptional circumstances', content, re.I)),
                     "mentions_scheme_edition": bool(re.search(r'\b(?:eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|19th|18th|17th|16th|15th)\s+edition', content, re.I))})
    except Exception as exc:
        item["error"] = str(exc)[:250]
    return item


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download and extract PDFs; otherwise only index source links")
    args = parser.parse_args()
    found = entries()
    DATA.mkdir(exist_ok=True)
    if args.download:
        with cf.ThreadPoolExecutor(max_workers=6) as pool:
            found = list(pool.map(extract, found))
    out = ROOT / "corpus_inventory.json"
    out.write_text(json.dumps({"index_source": URL, "documents": found}, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(found)} documents; {sum('sha256' in x for x in found)} extracted; {sum('error' in x for x in found)} errors")
