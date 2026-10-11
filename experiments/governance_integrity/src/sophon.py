#!/usr/bin/env python3
"""sophon: a very small provenance store for requirement <-> rule links.

What it is: a plain-JSON, append-only store keyed by (governing article version id, text hash)
on one side and (rule dotted name, rule file hash, rules snapshot) on the other, with an
executable check per link that is run through the organisation's own rule engine
(publicodes, via publicodes_eval.mjs). It can revalidate every link when either side
changes and print an evidence report or an as-of report.

What it is not: it does not interpret law, propose links or edit rules. A model (or a
person) proposes; this tool records only what it can verify, and it refuses evidence it
cannot find. A hash proves content is unchanged, not that it is correct or authorised.

Commands (run from the experiment directory; --store defaults to ./sophon/store):

  snapshot-law   --id S0 --articles inputs/law/S0_*/articles.json
  snapshot-rules --id G0 --rules-dir inputs/rules/G0_*/modele-social/règles [--rules-dir DIR2] --meta inputs/rules/G0_*/meta.json
  link add  --rule "<dotted name>" --rules-snapshot G0 --article D613-4 --law-snapshot S0 \
            --quote "<exact substring of the article text>" --claim "<what the quote requires>" \
            [--check-rule "<dotted name>" --check-situation '{"date":"01/06/2024", ...}' --expect 21.1 [--tolerance 1e-9]] \
            [--status INFERRED|UNKNOWN]   (without a check the link can only be INFERRED or UNKNOWN)
  revalidate --law-snapshot S8 --rules-snapshot G3 [--out sophon/reports/M1]
  report     [--out sophon/reports/evidence]
  asof       --date 2026-01-01 (--rule "<dotted>" | --article D613-4) [--out FILE]
  verify-store

Exit status 0 means the command ran; read the printed status. Nothing here is an approval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # PyYAML, for reading rule files
except ImportError:  # pragma: no cover
    yaml = None

HERE = Path(__file__).resolve().parent
EVAL = HERE / "publicodes_eval.mjs"


# ----------------------------------------------------------------------------- helpers
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def ms_to_date(ms) -> str | None:
    if ms is None:
        return None
    try:
        return dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


class Store:
    def __init__(self, root: Path):
        self.root = root
        (root / "law").mkdir(parents=True, exist_ok=True)
        (root / "rules").mkdir(parents=True, exist_ok=True)
        (root / "reports").mkdir(parents=True, exist_ok=True)
        self.links_path = root / "links.jsonl"

    # --- snapshots
    def law_path(self, sid: str) -> Path:
        return self.root / "law" / f"{sid}.json"

    def rules_path(self, gid: str) -> Path:
        return self.root / "rules" / f"{gid}.json"

    def load_law(self, sid: str) -> dict:
        p = self.law_path(sid)
        if not p.exists():
            sys.exit(f"law snapshot {sid} not in store ({p})")
        return json.load(open(p, encoding="utf-8"))

    def load_rules(self, gid: str) -> dict:
        p = self.rules_path(gid)
        if not p.exists():
            sys.exit(f"rules snapshot {gid} not in store ({p})")
        return json.load(open(p, encoding="utf-8"))

    def law_snapshots(self) -> list[dict]:
        return [json.load(open(p, encoding="utf-8")) for p in sorted((self.root / "law").glob("*.json"))]

    def rules_snapshots(self) -> list[dict]:
        return [json.load(open(p, encoding="utf-8")) for p in sorted((self.root / "rules").glob("*.json"))]

    # --- links (append-only, hash-chained)
    def links(self) -> list[dict]:
        if not self.links_path.exists():
            return []
        out = []
        for line in self.links_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def append_link(self, rec: dict) -> dict:
        prev = self.links()
        rec["prev_hash"] = prev[-1]["record_hash"] if prev else None
        rec["record_hash"] = sha256_text(canonical({k: v for k, v in rec.items() if k != "record_hash"}))
        with open(self.links_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec


# ----------------------------------------------------------------------------- engine
def run_eval(rules_dirs: list[str], situation: dict, rules: list[str]) -> dict:
    cmd = ["node", str(EVAL), "evaluate"]
    for d in rules_dirs:
        cmd += ["--rules", d]
    cmd += ["--situation", json.dumps(situation, ensure_ascii=False)]
    for r in rules:
        cmd += ["--rule", r]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": f"engine did not return JSON (exit {r.returncode}): {r.stdout[:300]} {r.stderr[:300]}"}


def run_list(rules_dirs: list[str]) -> dict:
    cmd = ["node", str(EVAL), "list"]
    for d in rules_dirs:
        cmd += ["--rules", d]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": f"engine did not return JSON (exit {r.returncode}): {r.stdout[:300]} {r.stderr[:300]}"}


def execute_check(check: dict, rules_dirs: list[str]) -> dict:
    """Run one stored executable check; return {passed, observed, expected, detail}."""
    res = run_eval(rules_dirs, check["situation"], [check["rule"]])
    if "error" in res:
        return {"passed": False, "observed": None, "expected": check["expect"], "detail": res["error"]}
    ev = res.get("evaluations", {}).get(check["rule"], {})
    if "error" in ev:
        return {"passed": False, "observed": None, "expected": check["expect"], "detail": ev["error"]}
    obs = ev.get("nodeValue")
    exp = check["expect"]
    tol = float(check.get("tolerance", 1e-9))
    if isinstance(exp, (int, float)) and isinstance(obs, (int, float)):
        passed = abs(float(obs) - float(exp)) <= tol
    else:
        passed = obs == exp
    return {"passed": passed, "observed": obs, "expected": exp, "unit": ev.get("unit"),
            "missing_variables": ev.get("missing_variables", []), "detail": None if passed else "observed != expected"}


# ----------------------------------------------------------------------------- rules indexing
def index_rules(rules_dirs: list[Path]) -> dict:
    """Index rule files: per file sha256; per top-level rule name -> file, references, LEGIARTI ids."""
    files, rules = {}, {}
    for base in rules_dirs:
        for p in sorted(base.rglob("*.publicodes")):
            rel = str(p.relative_to(base.parent)) if base.parent != base else str(p)
            files[rel] = sha256_file(p)
            if yaml is None:
                continue
            try:
                doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as e:  # keep going; the engine is the real syntax check
                rules[f"__yaml_error__:{rel}"] = {"file": rel, "error": str(e)[:200]}
                continue
            if not isinstance(doc, dict):
                continue
            for name, body in doc.items():
                refs = {}
                if isinstance(body, dict):
                    r = body.get("références") or body.get("references") or {}
                    if isinstance(r, dict):
                        refs = {str(k): str(v) for k, v in r.items()}
                ids = sorted(set(re.findall(r"LEGIARTI\d{12}", json.dumps(refs, ensure_ascii=False))))
                rules[str(name)] = {"file": rel, "references": refs, "legiarti_ids": ids,
                                    "body_sha256": sha256_text(canonical(body))}
    return {"files": files, "rules": rules}


# ----------------------------------------------------------------------------- commands
def cmd_snapshot_law(store: Store, a):
    src = json.load(open(a.articles, encoding="utf-8"))
    arts = {}
    for num, recs in src["articles"].items():
        rec = recs[0] if isinstance(recs, list) else recs
        arts[num] = {"id": rec["id"], "cid": rec.get("cid"), "etat": rec.get("etat"),
                     "dateDebut": ms_to_date(rec.get("dateDebut")), "dateFin": ms_to_date(rec.get("dateFin")),
                     "text": rec["text"], "text_sha256": sha256_text(rec["text"]),
                     "versions": [{"id": v.get("id"), "etat": v.get("etat"), "dateDebut": ms_to_date(v.get("dateDebut")), "dateFin": ms_to_date(v.get("dateFin"))} for v in (rec.get("articleVersions") or [])],
                     "modifications": [{"text": m.get("textTitle"), "jorf": m.get("datePubliTexte"), "effect": m.get("dateDebutCible")} for m in (rec.get("lienModifications") or []) if m.get("linkOrientation") in (None, "source", "cible")]}
    snap = {"snapshot": a.id, "recorded_at": now(), "source_file": str(Path(a.articles).resolve()),
            "source_sha256": sha256_file(Path(a.articles)), "legi_data_version": src.get("legi_data_version"),
            "published": src.get("published"), "tarball_sha256": src.get("tarball_sha256"), "articles": arts}
    json.dump(snap, open(store.law_path(a.id), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"ok": True, "snapshot": a.id, "articles": sorted(arts), "legi_data_version": snap["legi_data_version"]}, ensure_ascii=False))


def cmd_snapshot_rules(store: Store, a):
    dirs = [Path(d).resolve() for d in a.rules_dir]
    idx = index_rules(dirs)
    meta = json.load(open(a.meta, encoding="utf-8")) if a.meta else {}
    build = run_list([str(d) for d in dirs])
    snap = {"snapshot": a.id, "recorded_at": now(), "rules_dirs": [str(d) for d in dirs], "meta": meta,
            "engine_build": {k: build.get(k) for k in ("raw_rule_count", "parsed_rule_count", "error")},
            "parsed_names_sha256": sha256_text(canonical(build.get("names", []))),
            "files": idx["files"], "rules": idx["rules"]}
    json.dump(snap, open(store.rules_path(a.id), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"ok": "error" not in build, "snapshot": a.id, "files": len(idx["files"]), "top_level_rules": len(idx["rules"]), "engine_build": snap["engine_build"]}, ensure_ascii=False))


def find_rule(rules_snap: dict, name: str) -> dict | None:
    """Top-level rule record for a dotted name, or the closest ancestor that owns it (rules nested under `avec`)."""
    parts = name.split(" . ")
    for k in range(len(parts), 0, -1):
        cand = " . ".join(parts[:k])
        if cand in rules_snap["rules"]:
            rec = dict(rules_snap["rules"][cand])
            rec["owner"] = cand
            return rec
    return None


def cmd_link_add(store: Store, a):
    law = store.load_law(a.law_snapshot)
    rules = store.load_rules(a.rules_snapshot)
    problems = []
    art = law["articles"].get(a.article)
    if art is None:
        problems.append(f"article {a.article} not in law snapshot {a.law_snapshot}")
    elif a.quote not in art["text"]:
        problems.append("quote is not an exact substring of the article text in this snapshot")
    owner = find_rule(rules, a.rule)
    names = run_list(rules["rules_dirs"]).get("names", [])
    if a.rule not in names:
        problems.append(f"rule '{a.rule}' is not a parsed rule of snapshot {a.rules_snapshot}")
    if problems:
        print(json.dumps({"ok": False, "status": "REJECTED", "problems": problems}, ensure_ascii=False))
        return 1
    check = None
    status = (a.status or "INFERRED").upper()
    result = None
    if a.check_rule or a.expect is not None or a.check_situation:
        if not (a.check_rule and a.expect is not None and a.check_situation):
            print(json.dumps({"ok": False, "status": "REJECTED", "problems": ["a check needs --check-rule, --check-situation and --expect together"]}))
            return 1
        check = {"rule": a.check_rule, "situation": json.loads(a.check_situation), "expect": _num(a.expect), "tolerance": a.tolerance}
        result = execute_check(check, rules["rules_dirs"])
        status = "VERIFIED" if result["passed"] else "FAILED"
    elif status == "VERIFIED":
        print(json.dumps({"ok": False, "status": "REJECTED", "problems": ["VERIFIED requires an executable check; use INFERRED or UNKNOWN"]}))
        return 1
    rec = {
        "link_id": f"L{len(store.links()) + 1:04d}", "recorded_at": now(), "status": status,
        "rule": a.rule, "rules_snapshot": a.rules_snapshot, "rule_owner": owner["owner"] if owner else None,
        "rule_file": owner["file"] if owner else None, "rule_file_sha256": rules["files"].get(owner["file"]) if owner else None,
        "rule_body_sha256": owner.get("body_sha256") if owner else None,
        "article": a.article, "article_id": art["id"], "article_dateDebut": art["dateDebut"], "article_dateFin": art["dateFin"],
        "article_text_sha256": art["text_sha256"], "law_snapshot": a.law_snapshot,
        "quote": a.quote, "quote_offset": art["text"].find(a.quote), "claim": a.claim,
        "check": check, "check_result": result,
        "approval": {"status": "none recorded", "evidence_sha256": None} if not a.approval_file else _approval(a.approval_file),
        "note": a.note,
    }
    rec = store.append_link(rec)
    print(json.dumps({"ok": True, "link_id": rec["link_id"], "status": status, "check_result": result}, ensure_ascii=False))
    return 0


def _approval(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        sys.exit("approval evidence file does not exist; refusing to record an approval without evidence")
    return {"status": "recorded", "evidence_file": str(p.resolve()), "evidence_sha256": sha256_file(p)}


def _num(s: str):
    try:
        return float(s)
    except ValueError:
        return s


def cmd_revalidate(store: Store, a):
    law = store.load_law(a.law_snapshot)
    rules = store.load_rules(a.rules_snapshot)
    links = store.links()
    rows, touched_rules, touched_articles = [], set(), set()
    for L in links:
        if L["status"] == "REJECTED":
            continue
        row = {"link_id": L["link_id"], "rule": L["rule"], "article": L["article"], "prior_status": L["status"]}
        art = law["articles"].get(L["article"])
        if art is None:
            row["law"] = "ARTICLE_ABSENT"
        elif art["id"] != L["article_id"]:
            row["law"] = "LAW_CHANGED"
            row["law_detail"] = {"old_id": L["article_id"], "new_id": art["id"], "new_dateDebut": art["dateDebut"], "new_etat": art["etat"]}
        elif art["text_sha256"] != L["article_text_sha256"]:
            row["law"] = "LAW_TEXT_CHANGED"
        else:
            row["law"] = "LAW_SAME"
        if row["law"] in ("LAW_CHANGED", "LAW_TEXT_CHANGED", "ARTICLE_ABSENT"):
            row["quote_still_present"] = bool(art) and (L["quote"] in art["text"])
            touched_articles.add(L["article"])
        owner = find_rule(rules, L["rule"]) if L.get("rule_owner") else None
        new_file_hash = rules["files"].get(L["rule_file"]) if L.get("rule_file") else None
        if L.get("rule_file") and new_file_hash is None:
            row["rule"] = row.get("rule")  # keep name
            row["rules"] = "RULE_FILE_ABSENT"
        elif owner and owner.get("body_sha256") and L.get("rule_body_sha256") and owner["body_sha256"] != L["rule_body_sha256"]:
            row["rules"] = "RULE_CHANGED"
        elif new_file_hash and new_file_hash != L.get("rule_file_sha256"):
            row["rules"] = "RULE_FILE_CHANGED_OTHER_RULES"
        else:
            row["rules"] = "RULE_SAME"
        if L.get("check"):
            res = execute_check(L["check"], rules["rules_dirs"])
            row["check"] = "CHECK_PASS" if res["passed"] else "CHECK_FAIL"
            row["check_result"] = res
        else:
            row["check"] = "NO_CHECK"
        # status matrix
        if row["law"] != "LAW_SAME":
            row["status"] = "REASSESS_LAW_CHANGED"
        elif row["check"] == "CHECK_FAIL":
            row["status"] = "BROKEN"
        elif row["rules"] in ("RULE_CHANGED", "RULE_FILE_ABSENT"):
            row["status"] = "REASSESS_RULE_CHANGED" if row["check"] != "CHECK_PASS" else "RULE_CHANGED_CHECK_STILL_PASSES"
        elif row["check"] == "CHECK_PASS":
            row["status"] = "STILL_VERIFIED"
        else:
            row["status"] = "UNVERIFIED_NO_CHECK"
        if row["status"] not in ("STILL_VERIFIED", "UNVERIFIED_NO_CHECK"):
            touched_rules.add(L["rule"])
        rows.append(row)
    # articles that changed in the law snapshot relative to the latest link per article, or that have no link at all
    linked_articles = {L["article"] for L in links}
    unlinked = sorted(set(law["articles"]) - linked_articles)
    report = {"generated_at": now(), "law_snapshot": a.law_snapshot, "rules_snapshot": a.rules_snapshot,
              "links_total": len(rows), "rules_to_reassess": sorted(touched_rules), "articles_changed": sorted(touched_articles),
              "articles_without_any_link": unlinked, "rows": rows,
              "counts": {s: sum(1 for r in rows if r["status"] == s) for s in sorted({r["status"] for r in rows})}}
    out = Path(a.out) if a.out else store.root / "reports" / f"revalidate_{a.law_snapshot}_{a.rules_snapshot}"
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(report, open(str(out) + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = [f"# Revalidation: law {a.law_snapshot} x rules {a.rules_snapshot}", "", f"Generated {report['generated_at']}. Links: {len(rows)}.", "",
          "| link | rule | article | law | rules | check | status |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['link_id']} | `{r['rule']}` | {r['article']} | {r['law']} | {r['rules']} | {r['check']} | **{r['status']}** |")
    md += ["", f"Rules to reassess ({len(touched_rules)}): " + (", ".join(f"`{x}`" for x in sorted(touched_rules)) or "none"),
           f"Articles changed vs linked version: {', '.join(sorted(touched_articles)) or 'none'}",
           f"Articles in this snapshot with no link at all: {', '.join(unlinked) or 'none'}",
           "", "A hash proves content is unchanged, not that it is correct, complete or authorised."]
    Path(str(out) + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(out) + ".json", "counts": report["counts"], "rules_to_reassess": sorted(touched_rules), "articles_changed": sorted(touched_articles), "articles_without_any_link": unlinked}, ensure_ascii=False))


def cmd_report(store: Store, a):
    links = store.links()
    out = Path(a.out) if a.out else store.root / "reports" / "evidence"
    out.parent.mkdir(parents=True, exist_ok=True)
    md = ["# Evidence report", "", f"Generated {now()}. {len(links)} link records (append-only, hash-chained).", "",
          "| link | status | rule | rules snap | rule file sha256 | article | version id | in force | law snap | quote (start) | check | approval |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for L in links:
        chk = "-" if not L.get("check") else f"{L['check']['rule'].split(' . ')[-1]} @ {L['check']['situation'].get('date','?')} = {L['check']['expect']} -> {'pass' if L['check_result'] and L['check_result']['passed'] else 'FAIL'}"
        md.append(f"| {L['link_id']} | {L['status']} | `{L['rule']}` | {L['rules_snapshot']} | {str(L.get('rule_file_sha256'))[:12]} | {L['article']} | {L['article_id']} | {L['article_dateDebut']} | {L['law_snapshot']} | {L['quote'][:60].replace('|','/')}… | {chk} | {L['approval']['status']} |")
    md += ["", "Snapshots:", ""]
    for s in store.law_snapshots():
        md.append(f"- law {s['snapshot']}: legi-data {s.get('legi_data_version')} published {s.get('published')}, tarball sha256 {str(s.get('tarball_sha256'))[:16]}…, {len(s['articles'])} articles")
    for s in store.rules_snapshots():
        md.append(f"- rules {s['snapshot']}: commit {s['meta'].get('commit','?')[:12]} ({s['meta'].get('committed','?')}), {len(s['files'])} files, engine {s['engine_build']}")
    md += ["", "Every approval field above reads 'none recorded' unless an evidence file hash is attached. No approval was fabricated."]
    Path(str(out) + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    json.dump({"generated_at": now(), "links": links}, open(str(out) + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"ok": True, "report": str(out) + ".md", "links": len(links)}))


def cmd_asof(store: Store, a):
    date = a.date
    links = store.links()
    sel = [L for L in links if (a.rule and L["rule"] == a.rule) or (a.article and L["article"] == a.article)]
    law_snaps = store.law_snapshots()
    # which law snapshot(s) were published on or before the date, and what version of the article was in force at the date
    versions = []
    for s in law_snaps:
        for num, art in s["articles"].items():
            if a.article and num != a.article:
                continue
            if a.rule and num not in {L["article"] for L in sel}:
                continue
            in_force = (art["dateDebut"] or "0000") <= date and (art["dateFin"] is None or date < art["dateFin"])
            versions.append({"law_snapshot": s["snapshot"], "published": s.get("published"), "article": num, "id": art["id"], "etat": art["etat"],
                             "dateDebut": art["dateDebut"], "dateFin": art["dateFin"], "in_force_on_date": in_force, "text_sha256": art["text_sha256"]})
    rules_snaps = [{"snapshot": s["snapshot"], "commit": s["meta"].get("commit"), "committed": s["meta"].get("committed")} for s in store.rules_snapshots()]
    out = {"as_of": date, "question": {"rule": a.rule, "article": a.article}, "generated_at": now(),
           "links": [{k: L[k] for k in ("link_id", "recorded_at", "status", "rule", "rules_snapshot", "rule_file", "rule_file_sha256", "article", "article_id", "article_dateDebut", "article_dateFin", "article_text_sha256", "law_snapshot", "quote", "claim", "check", "check_result", "approval")} for L in sel],
           "article_versions_known": versions, "rules_snapshots_known": rules_snaps,
           "approvals": sorted({L["approval"]["status"] for L in sel}) or ["no link, so no approval evidence"],
           "limits": ["Only what was recorded in this store is reported; absence of a record is reported as absence, not inferred.",
                      "Snapshot publish dates are when the governing text was captured, not when it entered into force; both are listed.",
                      "A matching hash shows the preserved text is unchanged; it does not show the interpretation is correct or that anyone authorised it."]}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_verify_store(store: Store, a):
    problems = []
    prev = None
    for i, L in enumerate(store.links(), 1):
        body = {k: v for k, v in L.items() if k != "record_hash"}
        if sha256_text(canonical(body)) != L.get("record_hash"):
            problems.append(f"{L.get('link_id','?')} record hash mismatch (tampered or edited)")
        if L.get("prev_hash") != prev:
            problems.append(f"{L.get('link_id','?')} chain broken")
        prev = L.get("record_hash")
        # quote still in the stored law snapshot text?
        p = store.law_path(L["law_snapshot"])
        if p.exists():
            law = json.load(open(p, encoding="utf-8"))
            art = law["articles"].get(L["article"])
            if not art or art["id"] != L["article_id"] or art["text_sha256"] != L["article_text_sha256"] or L["quote"] not in art["text"]:
                problems.append(f"{L['link_id']} law snapshot {L['law_snapshot']} no longer matches the link (article/version/text/quote)")
            if art and sha256_text(art["text"]) != art["text_sha256"]:
                problems.append(f"law snapshot {L['law_snapshot']} article {L['article']} text does not match its own stored hash (tampered snapshot)")
        else:
            problems.append(f"{L['link_id']} law snapshot {L['law_snapshot']} missing")
        q = store.rules_path(L["rules_snapshot"])
        if q.exists() and L.get("rule_file"):
            rs = json.load(open(q, encoding="utf-8"))
            stored = rs["files"].get(L["rule_file"])
            if stored != L.get("rule_file_sha256"):
                problems.append(f"{L['link_id']} rules snapshot {L['rules_snapshot']} file hash differs from the link")
            # does the file on disk still match the snapshot?
            for d in rs["rules_dirs"]:
                fp = Path(d).parent / L["rule_file"]
                if fp.exists() and sha256_file(fp) != stored:
                    problems.append(f"{L['link_id']} rule file on disk differs from snapshot {L['rules_snapshot']} (edited after snapshot)")
    print(json.dumps({"ok": not problems, "problems": problems, "links_checked": len(store.links())}, ensure_ascii=False))
    return 0 if not problems else 2


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sophon", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", default="sophon/store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot-law"); s.add_argument("--id", required=True); s.add_argument("--articles", required=True)
    s = sub.add_parser("snapshot-rules"); s.add_argument("--id", required=True); s.add_argument("--rules-dir", action="append", required=True); s.add_argument("--meta")
    s = sub.add_parser("link"); s.add_argument("action", choices=["add"]); s.add_argument("--rule", required=True); s.add_argument("--rules-snapshot", required=True)
    s.add_argument("--article", required=True); s.add_argument("--law-snapshot", required=True); s.add_argument("--quote", required=True); s.add_argument("--claim", required=True)
    s.add_argument("--check-rule"); s.add_argument("--check-situation"); s.add_argument("--expect"); s.add_argument("--tolerance", type=float, default=1e-9)
    s.add_argument("--status", choices=["INFERRED", "UNKNOWN", "VERIFIED"]); s.add_argument("--approval-file"); s.add_argument("--note")
    s = sub.add_parser("revalidate"); s.add_argument("--law-snapshot", required=True); s.add_argument("--rules-snapshot", required=True); s.add_argument("--out")
    s = sub.add_parser("report"); s.add_argument("--out")
    s = sub.add_parser("asof"); s.add_argument("--date", required=True); s.add_argument("--rule"); s.add_argument("--article"); s.add_argument("--out")
    sub.add_parser("verify-store")
    a = ap.parse_args(argv)
    store = Store(Path(a.store))
    fn = {"snapshot-law": cmd_snapshot_law, "snapshot-rules": cmd_snapshot_rules, "link": cmd_link_add, "revalidate": cmd_revalidate,
          "report": cmd_report, "asof": cmd_asof, "verify-store": cmd_verify_store}[a.cmd]
    rc = fn(store, a)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
