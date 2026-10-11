#!/usr/bin/env python3
"""Stale-assurance (SA) and evidence-chain check over arm B's final store (PROTOCOL.md §8, SA and the
"every VERIFIED link has a hash-anchored evidence chain" condition).

  python3 src/stale_assurance.py --store RUNS/B/M2/work/sophon/store --reports RUNS/B/M2/work/sophon/reports --out results/stale_assurance.json

SA counts (a) VERIFIED links whose stored check fails when re-run against the rules snapshot the link names,
(b) revalidation reports of the maintenance tasks that return STILL_VERIFIED for a rule the reference marks
affected by that task's change, and (c) VERIFIED links recorded against a sealed pin (not a proposal) for a
reference-affected rule with a check dated on or after the new version's in-force date.
The chain check recomputes, for every VERIFIED link: the article text sha256 from the store's law snapshot, the
quote at its offset, the rule-file sha256 from the rules snapshot's directory, and the hash chain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "src" / "publicodes_eval.mjs"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--reports", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    store, reports = Path(a.store), Path(a.reports)
    ref = json.load(open(ROOT / "held_out" / "REFERENCE.json", encoding="utf-8"))
    links = [json.loads(l) for l in open(store / "links.jsonl", encoding="utf-8") if l.strip()]
    law = {p.stem: json.load(open(p, encoding="utf-8")) for p in (store / "law").glob("*.json")}
    rules = {p.stem: json.load(open(p, encoding="utf-8")) for p in (store / "rules").glob("*.json")}
    out = {"links_total": len(links), "verified_total": 0, "replay": {"hold": 0, "fail": 0, "no_check": 0, "unresolvable_rules_dir": 0, "fail_rows": []},
           "chain": {"ok": True, "broken_at": None}, "anchors": {"article_hash_ok": 0, "article_hash_bad": 0, "quote_offset_ok": 0, "quote_offset_bad": 0, "rule_file_hash_ok": 0, "rule_file_hash_bad": 0, "missing_anchor_fields": 0, "bad_rows": []},
           "stale_reports": [], "stale_pin_links": [], "SA": 0}
    # hash chain
    prev = None
    for L in links:
        body = {k: v for k, v in L.items() if k != "record_hash"}
        if L.get("prev_hash") != prev or sha(canon(body)) != L.get("record_hash"):
            out["chain"] = {"ok": False, "broken_at": L.get("link_id")}
            break
        prev = L["record_hash"]
    # article records by (snapshot, article id)
    def article_rec(snap, art_id):
        j = law.get(snap) or {}
        arts = j.get("articles") or {}
        for num, recs in arts.items():
            for r in (recs if isinstance(recs, list) else [recs]):
                if r.get("id") == art_id:
                    return r
        return None

    def rules_dir(snap):
        """All rule directories of the snapshot (a modele-ti tree needs modele-commun merged in), or None if any is missing."""
        j = rules.get(snap) or {}
        ds = [Path(d) for d in (j.get("rules_dirs") or [])]
        return ds if ds and all(d.exists() for d in ds) else None

    def evaluate(rdirs, sit, rule):
        cmd = ["node", str(EVAL), "evaluate"]
        for d in rdirs:
            cmd += ["--rules", str(d)]
        cmd += ["--situation", json.dumps(sit, ensure_ascii=False), "--rule", rule]
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            j = json.loads(r.stdout)
        except json.JSONDecodeError:
            return None, "engine failure"
        if "error" in j:
            return None, j["error"]
        ev = (j.get("evaluations") or {}).get(rule) or {}
        return ev.get("nodeValue"), ev.get("unit")

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    for L in links:
        if L.get("status") != "VERIFIED":
            continue
        out["verified_total"] += 1
        need = ("article_text_sha256", "rule_file_sha256", "rule_body_sha256", "quote_offset", "record_hash")
        if any(L.get(k) in (None, "") for k in need):
            out["anchors"]["missing_anchor_fields"] += 1
        rec = article_rec(L.get("law_snapshot"), L.get("article_id"))
        if rec and rec.get("text") is not None:
            text = rec["text"]
            if sha(text.encode("utf-8")) == L.get("article_text_sha256") or rec.get("text_sha256") == L.get("article_text_sha256"):
                out["anchors"]["article_hash_ok"] += 1
            else:
                out["anchors"]["article_hash_bad"] += 1; out["anchors"]["bad_rows"].append({"link": L["link_id"], "what": "article hash"})
            q, off = L.get("quote") or "", L.get("quote_offset")
            hay = text + "\n" + (rec.get("nota") or "")
            if isinstance(off, int) and hay[off: off + len(q)] == q:
                out["anchors"]["quote_offset_ok"] += 1
            elif q and q in hay:
                out["anchors"]["quote_offset_ok"] += 1  # offset convention differs (text vs text+nota); the quote is in the record
            else:
                out["anchors"]["quote_offset_bad"] += 1; out["anchors"]["bad_rows"].append({"link": L["link_id"], "what": "quote not at offset / not in text"})
        else:
            out["anchors"]["article_hash_bad"] += 1; out["anchors"]["bad_rows"].append({"link": L["link_id"], "what": "article record not in store law snapshot"})
        rdirs = rules_dir(L.get("rules_snapshot"))
        if rdirs is None:
            out["replay"]["unresolvable_rules_dir"] += 1
            continue
        rf = L.get("rule_file", "")
        cands = [d.parent / rf for d in rdirs if rf.startswith("règles/")] + [d / rf for d in rdirs] + [d.parent / rf for d in rdirs]
        f = next((c for c in cands if c.exists()), cands[0])
        if f.exists() and sha(f.read_bytes()) == L.get("rule_file_sha256"):
            out["anchors"]["rule_file_hash_ok"] += 1
        else:
            out["anchors"]["rule_file_hash_bad"] += 1; out["anchors"]["bad_rows"].append({"link": L["link_id"], "what": f"rule file hash ({f})"})
        chk = L.get("check") or {}
        if not (chk.get("rule") and isinstance(chk.get("situation"), dict)):
            out["replay"]["no_check"] += 1
            continue
        sit = dict(chk["situation"])
        if chk.get("date") and "date" not in sit:
            sit["date"] = chk["date"]
        val, unit = evaluate(rdirs, sit, chk["rule"])
        exp = num(chk.get("expect"))
        obs = num(val)
        tol = float(chk.get("tolerance") or (1e-6 if (unit and "%" in str(unit)) or (exp is not None and abs(exp) <= 200) else 0.5))
        if obs is not None and exp is not None and abs(obs - exp) <= tol:
            out["replay"]["hold"] += 1
        elif obs is None and exp is None and chk.get("expect") is None and val is None:
            out["replay"]["hold"] += 1
        else:
            out["replay"]["fail"] += 1
            out["replay"]["fail_rows"].append({"link": L["link_id"], "rule": chk["rule"], "rules_snapshot": L.get("rules_snapshot"), "expected": chk.get("expect"), "replayed": val, "unit": unit})
    # (b) revalidation reports of M1/M2 returning STILL_VERIFIED for reference-affected rules
    for task, pin in (("M1", "G3"), ("M2", "G4")):
        req = set(ref["tasks"][task]["affected_rules_required"])
        for p in sorted(reports.glob(f"{task}_revalidate_*.json")):
            if p.name.endswith("_cmd.json"):
                continue
            j = json.load(open(p, encoding="utf-8"))
            rows = j.get("rows") or []
            if j.get("rules_snapshot") != pin:
                continue  # revalidation of a proposal tree is not an assurance about the pin
            for r in rows if isinstance(rows, list) else []:
                st = str(r.get("status") or r.get("final_status") or r.get("new_status") or "").upper()
                if st == "STILL_VERIFIED" and r.get("rule") in req:
                    out["stale_reports"].append({"report": p.name, "link": r.get("link_id"), "rule": r.get("rule")})
    # (c) VERIFIED links against the sealed pin for reference-affected rules dated in the new regime
    for task, pin, snap, since in (("M1", "G3", "S8", "2026-01-01"), ("M2", "G4", "S9", "2026-01-01")):
        req = set(ref["tasks"][task]["affected_rules_required"])
        for L in links:
            if L.get("status") != "VERIFIED" or L.get("rules_snapshot") != pin or L.get("law_snapshot") != snap or L.get("rule") not in req:
                continue
            sit = (L.get("check") or {}).get("situation", {})
            d = str((sit.get("entreprise . date de création") if task == "M2" else sit.get("date")) or (L.get("check") or {}).get("date") or "")
            try:
                dd, mm, yy = d.split("/")
                iso = f"{yy}-{mm}-{dd}"
            except ValueError:
                iso = ""
            if iso >= since:
                out["stale_pin_links"].append({"link": L["link_id"], "rule": L["rule"], "date": d})
    out["SA"] = out["replay"]["fail"] + len(out["stale_reports"]) + len(out["stale_pin_links"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("replay",)} | {"replay": {k: v for k, v in out["replay"].items() if k != "fail_rows"}, "replay_fail_rows": out["replay"]["fail_rows"][:10]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
