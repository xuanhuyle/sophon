"""Retrieve and verify the original evidence for the V3 secondary adjudication (operator-run, local only).

For each of the 4 secondary heldout documents this script:
  1. obtains the raw bytes, either from an existing local copy (--raw-dir, layout ca/*.htm, sla/*.html as in the
     frozen run) or by downloading the manifest URL (--download; SEC requires --user-agent "<Name> <email>");
  2. refuses any file whose SHA-256 differs from the recorded hash (HASH_MISMATCH), so a changed page is never
     passed off as the frozen evidence;
  3. rebuilds the structure with the FROZEN code (corpus.build_record / extract.sla_structure /
     secondary.sla_numbered_fallback) and checks it is identical to ../data/records_heldout_secondary.json
     (headings, labels and, for SLAs, unit-text SHA-256), i.e. the reviewer sees exactly what the predictor saw;
  4. writes passages for every unit in review_units.csv into local_evidence/ (git-ignored; never commit full text):
     LOCAL_PASSAGES.md, review_units_with_passages.csv and verification_receipt.json (hashes only, no text).

It never modifies ../data, ../results or ../frozen and makes no model/provider call.

    python fetch_local_evidence.py --raw-dir <old corpus_dl>
    python fetch_local_evidence.py --download --user-agent "Jane Doe jane@example.com"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path.insert(0, str(V3))

import corpus     # noqa: E402  (frozen)
import extract    # noqa: E402  (frozen)
import labels     # noqa: E402  (frozen)
import secondary  # noqa: E402  (post-freeze secondary run; its REPLACEMENT and fallback are reused, not changed)

DOCS = ["CA-MARKEL", "CA-OLDDOMINION", "SLA-CLOUDFLARE", "SLA-MONGODB"]
OUT = HERE / "local_evidence"
MAX_PASSAGE = 6000


def sources() -> dict[str, dict]:
    man = {d["doc_id"]: d for d in json.loads((V3 / "data/source_manifest.json").read_text(encoding="utf-8"))["documents"]}
    src = {d: man[d] for d in DOCS if d in man}
    src["CA-OLDDOMINION"] = dict(secondary.REPLACEMENT)
    return src


def get_bytes(src: dict, raw_dir: Path | None, user_agent: str | None) -> bytes:
    if raw_dir is not None:
        sub = "ca" if src["family"] == "CREDIT_AGREEMENT" else "sla"
        return (raw_dir / sub / src["local_file"]).read_bytes()
    req = urllib.request.Request(src["url"], headers={"User-Agent": user_agent, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def body_after_toc(lines: list[str], pattern: re.Pattern, key) -> tuple[str, str]:
    """Text of the BODY heading matching `key` (the first match is normally the table of contents)."""
    hits = [i for i, l in enumerate(lines) if (m := pattern.match(l)) and key(m)]
    if not hits:
        return "", "PASSAGE_NOT_LOCATED"
    start = hits[1] if len(hits) > 1 else hits[0]
    status = "BODY_AFTER_TOC" if len(hits) > 1 else "ONLY_ONE_MATCH_MAY_BE_TOC"
    out = [lines[start]]
    for l in lines[start + 1:]:
        if extract.ART.match(l) or extract.SEC.match(l):
            break
        out.append(l)
    return " ".join(out), status


def ca_passages(raw: str, rec: dict) -> dict[str, tuple[str, str]]:
    lines = [extract.clean(l) for l in extract.html_lines(raw)]
    lines = [l for l in lines if l]
    out = {}
    for s in rec["sections"]:
        n = int(s["path"].split()[1])
        art_txt, st = body_after_toc(lines, extract.ART, lambda m, n=n: (int(m.group(1)) if m.group(1).isdigit() else extract.roman(m.group(1))) == n)
        toc = " · ".join(f"{p['path'].split()[-1]} {p['heading']}" for p in s["subunits"])
        out[s["path"]] = (f"[ARTICLE HEADING + SECTION LIST] {s['heading']} :: {toc} :: [ARTICLE OPENING TEXT] {art_txt[:800]}", st)
        for p in s["subunits"]:
            a, b = (int(x) for x in p["path"].split()[1].split("."))
            txt, st2 = body_after_toc(lines, extract.SEC, lambda m, a=a, b=b: (int(m.group(1)), int(m.group(2))) == (a, b))
            out[p["path"]] = (txt, st2)
    return out


def rebuild(doc: str, src: dict, raw_b: bytes) -> tuple[dict, dict]:
    """Rebuilt structure (frozen code) plus {path: (passage, status)}."""
    raw = extract.decode(raw_b)
    if src["family"] == "CREDIT_AGREEMENT":
        rec = corpus.build_record({**src, "split": "HELDOUT"}, raw_b)
        return rec, ca_passages(raw, rec)
    st = secondary.sla_numbered_fallback(raw) if doc == "SLA-CLOUDFLARE" else extract.sla_structure(raw)
    rec = {"sections": [{"path": f"Unit {k + 1}", "heading": u["heading"], "unit_text_sha256": corpus.sha256_text(u["text"]),
                         "functions": labels.sla_unit_functions(u["heading"], u["text"])} for k, u in enumerate(st["units"])]}
    return rec, {f"Unit {k + 1}": (f"{u['heading']} :: {u['text']}", "UNIT_TEXT") for k, u in enumerate(st["units"])}


def compare(committed: dict, rebuilt: dict) -> list[str]:
    diffs = []
    a, b = committed["sections"], rebuilt["sections"]
    if len(a) != len(b):
        return [f"unit count {len(a)} vs {len(b)}"]
    for x, y in zip(a, b):
        for k in ("path", "heading", "functions", "unit_text_sha256"):
            if x.get(k) != y.get(k):
                diffs.append(f"{x['path']}.{k}")
        for p, q in zip(x.get("subunits", []), y.get("subunits", [])):
            if (p["path"], p["heading"], p["provision_type"]) != (q["path"], q["heading"], q["provision_type"]):
                diffs.append(p["path"])
    return diffs


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--raw-dir", type=Path)
    g.add_argument("--download", action="store_true")
    ap.add_argument("--user-agent", help='required with --download, e.g. "Jane Doe jane@example.com" (SEC policy)')
    a = ap.parse_args()
    if a.download and not (a.user_agent and "@" in a.user_agent):
        raise SystemExit("--download needs --user-agent with a contact e-mail (SEC fair-access policy)")
    committed = {r["doc_id"]: r for r in json.loads((V3 / "data/records_heldout_secondary.json").read_text(encoding="utf-8"))["records"]}
    OUT.mkdir(exist_ok=True)
    receipt = {"run_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "mode": "raw-dir" if a.raw_dir else "download", "documents": {}}
    passages: dict[str, tuple[str, str]] = {}
    for doc, src in sources().items():
        entry = {"url": src["url"], "recorded_sha256": src["sha256"]}
        try:
            raw_b = get_bytes(src, a.raw_dir, a.user_agent)
        except Exception as e:   # record the exact failure; never substitute text
            entry.update(status="RETRIEVAL_FAILED", error=f"{type(e).__name__}: {e}")
            receipt["documents"][doc] = entry
            continue
        got = hashlib.sha256(raw_b).hexdigest()
        entry.update(observed_sha256=got, bytes=len(raw_b))
        if got != src["sha256"]:
            entry["status"] = "HASH_MISMATCH"
            receipt["documents"][doc] = entry
            continue
        rec, pas = rebuild(doc, src, raw_b)
        diffs = compare(committed[doc], rec)
        entry.update(status="VERIFIED" if not diffs else "STRUCTURE_DIFFERS", structure_diffs=diffs[:50],
                     passage_status_counts={s: sum(1 for _, (_, x) in pas.items() if x == s) for s in {x for _, x in pas.values()}})
        receipt["documents"][doc] = entry
        if not diffs:
            for path, v in pas.items():
                passages[f"{doc}|{path}"] = v
        if a.download:
            time.sleep(1.0)   # SEC rate limit courtesy
    (OUT / "verification_receipt.json").write_text(json.dumps(receipt, indent=1) + "\n", encoding="utf-8")
    rows = list(csv.DictReader((HERE / "review_units.csv").open(encoding="utf-8")))
    md = ["# LOCAL ONLY: original passages for V3 secondary adjudication (do not commit; see verification_receipt.json)", ""]
    for r in rows:
        txt, st = passages.get(r["unit_id"], ("", "NOT_AVAILABLE (see verification_receipt.json)"))
        r["body_passage"] = f"[{st}] {txt[:MAX_PASSAGE]}"
        md += [f"## {r['unit_id']} ({r['priority']}, {r['role']}, agent labels {r['agent_labels']})", "",
               f"Heading: {r['verbatim_heading']}  ", f"Passage status: `{st}`", "", (txt[:MAX_PASSAGE] or "_none_"), ""]
    with (OUT / "review_units_with_passages.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (OUT / "LOCAL_PASSAGES.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({d: e["status"] for d, e in receipt["documents"].items()}, indent=1))


if __name__ == "__main__":
    main()
