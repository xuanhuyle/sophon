"""V4 corpus: frozen, content-blind selection of authentic SEC EDGAR credit agreements, and records.

    set SEC_USER_AGENT="<name> <contact email>"          # SEC requires a declared contact; never hard-coded
    python v4_corpus.py fetch --raw-dir <local dir>       # EDGAR full-text search -> 8 eligible EX-10 exhibits
    python v4_corpus.py build --raw-dir <local dir>       # views (ToC only, committed) + hidden bodies (local only)

Reuses V3 `extract.py` (HTML lines, ToC parser) and `labels.py` (frozen provision/section rules) unchanged.
Eligibility checks use document size, an amendment screen on the opening text, ToC/body segmentation
and ToC near-duplication only; no provision body, target or score is inspected during selection.
Raw documents and bodies stay local (gitignored); views keep headings, rule labels and hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent / "contract_structure_prediction_v3"
sys.path.insert(0, str(V3))
import extract  # noqa: E402  (V3, unchanged)
import labels   # noqa: E402  (V3, unchanged)

MANIFEST = HERE / "data" / "source_manifest.json"
VIEWS = HERE / "data" / "views"
SEARCH = {"q": '"credit agreement" "administrative agent"', "forms": "8-K", "dateRange": "custom",
          "startdt": "2024-01-01", "enddt": "2024-06-30"}
N_DOCS, N_SEEDS, MAX_HITS = 8, 2, 400
MIN_BYTES, MIN_ARTICLES, MIN_SECTIONS, MIN_BODY_FRACTION, TOC_DUP_JACCARD = 150_000, 6, 40, 0.8, 0.8
AMENDMENT = re.compile(r"(?i)\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|incremental)\s+amendment\b"
                       r"|\bamendment\s+no\.?\s*\d|\bjoinder\b|\bwaiver\b")
SEC_LINE = re.compile(r"^(?:SECTION|Section|§)\s+(\d+)\.(\d+)\.?\s*(.*)$")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ structure (V3 ToC + body spans)
def cleaned_lines(raw: str) -> list[str]:
    return [l for l in (extract.clean(x) for x in extract.html_lines(raw)) if l]


def toc_end(lines: list[str]) -> int:
    """First line that repeats a Section number or ARTICLE number already seen (V3's ToC stop rule)."""
    secs, arts = set(), set()
    for i, l in enumerate(lines):
        m, a = SEC_LINE.match(l), extract.ART.match(l)
        if m:
            k = (int(m.group(1)), int(m.group(2)))
            if k in secs:
                return i
            secs.add(k)
        elif a:
            n = extract.roman(a.group(1)) if not a.group(1).isdigit() else int(a.group(1))
            if n in arts:
                return i
            arts.add(n)
    return len(lines)


def bodies(lines: list[str], toc_keys: list[str]) -> dict[str, str]:
    """Body text per section number: the FIRST line after the ToC starting with 'Section n.mm',
    up to the next Section/ARTICLE line. Unlocated sections are absent."""
    starts = {}
    for i in range(toc_end(lines), len(lines)):
        m = SEC_LINE.match(lines[i])
        if m:
            starts.setdefault(f"{int(m.group(1))}.{int(m.group(2)):02d}", i)
    out = {}
    for key in toc_keys:
        i = starts.get(key)
        if i is None:
            continue
        j = i + 1
        while j < len(lines) and not SEC_LINE.match(lines[j]) and not extract.ART.match(lines[j]):
            j += 1
        out[key] = " ".join(lines[i:j])
    return out


def structure(raw_bytes: bytes) -> dict:
    raw = extract.decode(raw_bytes)
    st = extract.credit_agreement_structure(raw)
    lines = cleaned_lines(raw)
    keys = [s["num"] for u in st["units"] for s in u["subunits"]]
    return {"toc": st, "lines": lines, "bodies": bodies(lines, keys), "keys": keys}


def eligibility(raw_bytes: bytes, accepted_tocs: list[set]) -> tuple[bool, str, dict | None]:
    if len(raw_bytes) < MIN_BYTES:
        return False, f"size {len(raw_bytes)} < {MIN_BYTES}", None
    s = structure(raw_bytes)
    opening = " ".join(s["lines"])[:6000]
    m = AMENDMENT.search(opening)
    if m:
        return False, f"amendment screen: {m.group(0)!r} in opening text", None
    units = s["toc"]["units"]
    if len(units) < MIN_ARTICLES or len(s["keys"]) < MIN_SECTIONS:
        return False, f"segmentation: {len(units)} articles / {len(s['keys'])} sections", None
    frac = len(s["bodies"]) / len(s["keys"])
    if frac < MIN_BODY_FRACTION:
        return False, f"body located for {frac:.2f} of ToC sections", None
    toc = {re.sub(r"\W+", " ", x["heading"].lower()).strip() for u in units for x in u["subunits"]}
    for other in accepted_tocs:
        jac = len(toc & other) / max(1, len(toc | other))
        if jac >= TOC_DUP_JACCARD:
            return False, f"ToC near-duplicate of an accepted document (Jaccard {jac:.2f})", None
    return True, "eligible", {"toc_set": toc, "body_fraction": round(frac, 3)}


# ------------------------------------------------------------------ fetch (owner-local; SEC reachable)
def _get(url: str, ua: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    time.sleep(0.25)                      # SEC fair-access rate limit
    return data


def fetch(raw_dir: Path) -> dict:
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if "@" not in ua:
        raise SystemExit("BLOCKED_SOURCE_ACCESS: set SEC_USER_AGENT to '<name> <contact email>' (SEC fair-access policy)")
    v3 = json.loads((V3 / "data" / "source_manifest.json").read_text(encoding="utf-8"))
    excluded_ciks = {str(int(d["cik"])) for d in v3["documents"] if d.get("cik")}
    raw_dir.mkdir(parents=True, exist_ok=True)
    accepted, screened, tocs, searches = [], [], [], []
    for offset in range(0, MAX_HITS, 100):
        url = "https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode({**SEARCH, "from": offset})
        body = _get(url, ua)
        searches.append({"url": url, "sha256": sha256(body), "retrieved_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        (raw_dir / f"search_{offset}.json").write_bytes(body)
        hits = json.loads(body).get("hits", {}).get("hits", [])
        if not hits:
            break
        for hit in hits:                   # EDGAR's returned order; nothing about content is used to rank
            src = hit.get("_source", {})
            adsh, _, fname = hit.get("_id", "").partition(":")
            ftype = str(src.get("file_type", ""))
            cik = str(int(src["ciks"][0])) if src.get("ciks") else ""
            row = {"adsh": adsh, "file": fname, "file_type": ftype, "cik": cik, "file_date": src.get("file_date"),
                   "issuer": (src.get("display_names") or ["?"])[0]}
            if not ftype.upper().startswith("EX-10"):
                continue
            if cik in excluded_ciks or any(a["cik"] == cik for a in accepted):
                screened.append({**row, "decision": "excluded: issuer already used (V3 or this corpus)"}); continue
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fname}"
            data = _get(url, ua)
            ok, why, info = eligibility(data, tocs)
            screened.append({**row, "url": url, "sha256": sha256(data), "bytes": len(data), "decision": why})
            if ok:
                local = f"{cik}_{adsh}_{fname}"
                (raw_dir / local).write_bytes(data)
                tocs.append(info["toc_set"])
                accepted.append({**row, "url": url, "sha256": sha256(data), "bytes": len(data), "local_file": local,
                                 "body_fraction": info["body_fraction"]})
            if len(accepted) == N_DOCS:
                break
        if len(accepted) == N_DOCS:
            break
    accepted.sort(key=lambda d: (d["file_date"] or "", d["adsh"]))
    for k, d in enumerate(accepted):
        d["doc_id"] = f"CA4-{k + 1:02d}-{d['cik']}"
        d["role"] = "SEED" if k < N_SEEDS else "EVAL"
        d["sequence_index"] = k + 1
        d["rights"] = "Public SEC filing; full text NOT committed; only headings, rule labels, hashes, offsets."
    man = {"manifest_id": "V4-SEQUENTIAL-EDGAR-CREDIT-AGREEMENTS", "search": SEARCH, "searches": searches,
           "status": "OK" if len(accepted) == N_DOCS else "BLOCKED_INSUFFICIENT_CORPUS",
           "documents": accepted, "screened": screened}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(man, indent=1), encoding="utf-8")
    return man


# ------------------------------------------------------------------ records
def build_record(src: dict, raw_bytes: bytes) -> tuple[dict, dict]:
    """Returns (view, hidden). The view has the ToC only; hidden has each located section body."""
    if sha256(raw_bytes) != src["sha256"]:
        raise ValueError(f"{src['doc_id']}: raw file hash differs from manifest")
    s = structure(raw_bytes)
    sections = []
    for u in s["toc"]["units"]:
        subs = [{"path": f"Section {x['num']}", "num": x["num"], "heading": x["heading"],
                 "provision_type": labels.ca_provision_type(x["heading"]), "body_located": x["num"] in s["bodies"]}
                for x in u["subunits"]]
        sections.append({"path": f"Article {u['num']}", "heading": u["heading"],
                         "functions": [labels.ca_section_function(u["heading"])], "subunits": subs})
    law = labels.evidenced_governing_law(s["toc"]["full_text"])
    view = {"doc_id": src["doc_id"], "family": "CREDIT_AGREEMENT", "role": src["role"], "sequence_index": src["sequence_index"],
            "file_date": src["file_date"], "accession": src["adsh"], "raw_sha256": src["sha256"], "label_rules": labels.VERSION,
            "sections": sections, "governing_law": {"value": law["law"], "evidence_section_paths": []}}
    hidden = {"doc_id": src["doc_id"], "raw_sha256": src["sha256"],
              "bodies": {k: {"text": t, "sha256": sha256(t.encode())} for k, t in s["bodies"].items()}}
    return view, hidden


def build(raw_dir: Path, hidden_dir: Path) -> None:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if man.get("status") != "OK":
        raise SystemExit(f"manifest status {man.get('status')}; not building")
    VIEWS.mkdir(parents=True, exist_ok=True)
    hidden_dir.mkdir(parents=True, exist_ok=True)
    for src in man["documents"]:
        view, hidden = build_record(src, (raw_dir / src["local_file"]).read_bytes())
        (VIEWS / f"{src['doc_id']}.json").write_text(json.dumps(view, indent=1, ensure_ascii=False), encoding="utf-8")
        (hidden_dir / f"{src['doc_id']}.json").write_text(json.dumps(hidden, ensure_ascii=False), encoding="utf-8")
    print(f"built {len(man['documents'])} views in {VIEWS} and hidden bodies in {hidden_dir}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "build"])
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--hidden-dir", default=str(HERE / "local_hidden"))
    a = ap.parse_args()
    if a.cmd == "fetch":
        man = fetch(Path(a.raw_dir))
        print(f"{man['status']}: {len(man['documents'])} accepted, {len(man['screened'])} screened")
    else:
        build(Path(a.raw_dir), Path(a.hidden_dir))


if __name__ == "__main__":
    main()
