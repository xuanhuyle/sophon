"""Builds output/answer.json and output/NOTES.md for M0 from the eval jsonl, link results and report files. usage: gen_answer_M0.py <self_calls>"""
import json, os, sys, glob
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else None
def load(f):
    out = {}
    for line in open(f, encoding='utf-8'):
        r = json.loads(line); res = json.loads(r["stdout"])
        for k in ("results", "evaluations", "values"):
            if isinstance(res.get(k), dict): res = res[k]; break
        for k, v in res.items():
            if isinstance(v, dict) and "nodeValue" in v: out[(r["id"], k)] = (v.get("nodeValue"), v.get("unit"), r["situation"])
    return out
B = load("work/evals/M0_G3.jsonl"); A = load("work/evals/M0_proposal.jsonl")
names = [l.rstrip("\n") for l in open("work/evals/list_G3_all.txt", encoding="utf-8")]
links = [json.loads(l) for l in open("work/sophon/link_results_M0.jsonl", encoding="utf-8")]
spec = {s["id"]: s for s in json.load(open("work/sophon/links_M0.json", encoding="utf-8"))}
lk = {l["spec_id"]: l for l in links}
def LID(i): return lk[i].get("link_id") or lk[i].get("id")
def ev_link(ids): return [f"sophon {i} = link {LID(i)}: {lk[i].get('status')} observed={((lk[i].get('check_result') or {}).get('observed'))} expected={((lk[i].get('check_result') or {}).get('expected'))}" for i in ids]
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"; DR = "dirigeant . auto-entrepreneur . DROM"; AE = "dirigeant . auto-entrepreneur"
V4 = "LEGIARTI000049624097"; V6 = "LEGIARTI000049625405"; N4 = "LEGIARTI000052218738"; N6 = "LEGIARTI000052218747"; M4 = "LEGIARTI000049624125"; M6 = "LEGIARTI000049625445"
qa = spec["M0-03"]["quote"]; qb = spec["M0-04"]["quote"]; qc = spec["M0-10"]["quote"]; qd = spec["M0-02"]["quote"]; qe = spec["M0-01"]["quote"]
q6e = spec["M0-11"]["quote"]; q6ad = spec["M0-16"]["quote"]; q6b = spec["M0-22"]["quote"]; q7a = spec["M0-27"]["quote"]; q7b = spec["M0-28"]["quote"]; q7c = spec["M0-29"]["quote"]
LAW4 = f"D613-4 {V4} (in force 2025-01-01..2026-01-01, text in S6 = S7, sha256 8c3b3865c4873f63...)"
LAW6 = f"D613-6 {V6} (in force 2025-01-01..2026-01-01, text in S6 = S7, sha256 69b8e1b56c6185a7...)"
CHG = (f"S6->S7: the 2026-01-01 version of D613-4 announced as {M4} became MODIFIE_MORT_NE (dateFin 2025-09-10) and a new version {N4} (VIGUEUR_DIFF 2026-01-01..2999-01-01) appears WITHOUT text; "
       f"same for D613-6: {M6} MODIFIE_MORT_NE, new {N6} without text. Current texts unchanged.")
AB = "ABSTAIN on every value for dates >= 2026-01-01: no text available in S6/S7 for the new versions; G3's 2026 branches were transposed on 2024-08-01 (commit 1d2874c5 'Ajoute les taux de cotisation BNC pour 2025 et 2026') from the mort-ne versions and are therefore unsupported."
# ---- rules table
R = []; seen = set()
def rule(r, cl, conf, ev):
    if r in seen: return
    seen.add(r); R.append({"rule": r, "classification": cl, "confidence": conf, "evidence": ev})
def val(case, r):
    v = B.get((case, r)); return None if v is None else v[0]
SPLIT = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"]
# AFFECTED holders (own 2026 branch resting on the mort-ne version)
rule(f"{C} . service BNC . taux", "AFFECTED", "high", [
    f"{LAW4}: \"{qe}\" -> 24,6 % ; engine G3 = 24.6 % on 01/07/2025 (BNC situation); 23.1 % on 01/12/2024 (version LEGIARTI000049624068, text not in S6/S7); 26.1 % on 01/01/2026",
    "YAML (G3 cotisations-et-contributions.publicodes l.310-313): 'si: date >= 01/2026 alors: 26.1%' added by commit 1d2874c5 (2024-08-01) from the Décret 2024-484 schedule = version " + M4 + ", now MODIFIE_MORT_NE in S7; replacement " + N4 + " has no text -> the 2026 branch has lost its legal basis and no text supports any 2026 value",
    "proposal: documentation-only (références pinned to " + V4 + ", note recording the mort-ne basis); numeric value for 2026 ABSTAINED; engine before = after (26.1 on 01/01/2026, 24.6 on 01/07/2025)"] + ev_link(["M0-01", "M0-05", "M0-35"]))
for s, v in zip(SPLIT, [3.4, 3.5, 47.6, 13, 32.5]):
    rule(f"{C} . service BNC . répartition . {s} . taux de répartition", "AFFECTED", "high", [
        f"{LAW6} e): \"{q6e}\" -> {v} % ; engine G3 = {val('BNC@01/07/2025', f'{C} . service BNC . répartition . {s} . taux de répartition')} % on 01/07/2025; {val('BNC@01/01/2026', f'{C} . service BNC . répartition . {s} . taux de répartition')} % on 01/01/2026 (2026 branch from the mort-ne version {M6}; replacement {N6} has no text) -> abstain for 2026",
        "proposal: documentation-only at 'service BNC . répartition' (références " + V6 + ", note); no numeric change"] + ev_link([f"M0-{11 + SPLIT.index(s):02d}", "M0-36"]))
rule(f"{DR} . taux service BNC", "AFFECTED", "high", [
    f"D756-5 LEGIARTI000034726710 (unchanged S6->S7): \"{q7a}\" / \"{q7b}\" / \"{q7c}\" applied to the 2025 BNC rate 24,6 % ({LAW4}) -> 4,1 / 12,3 / 16,4 % ; engine G3 on 01/07/2025: {val('DROM_BNC_P1@01/07/2025', DR + ' . taux service BNC')} / {val('DROM_BNC_P2@01/07/2025', DR + ' . taux service BNC')} / {val('DROM_BNC_P3@01/07/2025', DR + ' . taux service BNC')} %",
    f"engine on 01/01/2026: {val('DROM_BNC_P1@01/01/2026', DR + ' . taux service BNC')} / {val('DROM_BNC_P2@01/01/2026', DR + ' . taux service BNC')} / {val('DROM_BNC_P3@01/01/2026', DR + ' . taux service BNC')} % = fractions of the unsupported 26,1 % -> abstain; proposal adds a note only"] + ev_link(["M0-27", "M0-28", "M0-29", "M0-37"]))
rule(f"{AE} . Acre . taux service BNC", "AFFECTED", "medium", [
    "YAML (G3 exonérations.publicodes l.141-147): 'arrondi: variations - si: date >= 01/2026 alors: 2 décimales' presupposes the 2026 BNC rate 26,1 % (13,05 % at 50 %), i.e. the mort-ne version " + M4 + "; the AE Acre rate article itself is outside the bounded set",
    "engine: not applicable (None) in the tested Acre situations (01/07/2025 creation 01/03/2025; 01/01/2026 creation 01/09/2025, durée 180 jours) -> no value asserted; proposal adds a note only"] + ev_link(["M0-41"]))
# NEEDS_REVIEW: governing article gets a textless 2026 version; 2025 values verified
for r, q, v, case, ids in [(f"{C} . service BIC . taux", qd, 21.2, "BIC", ["M0-02", "M0-07", "M0-38"]), (f"{C} . vente restauration hébergement . taux", qa, 12.3, "VENTE", ["M0-03", "M0-08", "M0-39"]), (f"{C} . service BNC Cipav . taux", qb, 23.2, "CIPAV", ["M0-04", "M0-09", "M0-40"])]:
    rule(r, "NEEDS_REVIEW", "high", [f"{LAW4}: \"{q}\" -> {v} % ; engine G3 = {val(case + '@01/07/2025', r)} % on 01/07/2025 and {val(case + '@01/01/2026', r)} % on 01/01/2026 (no 2026 branch)", f"the version in force from 2026-01-01 ({N4}) has no text in S7: whether this category's rate changes in 2026 is unknown -> review when the text arrives; 2025 value aligned"] + ev_link(ids))
for x, case, q, vals, base in [("service BIC", "BIC", q6ad, [8.9, 3.1, 41.8, 16.5, 29.7], 16), ("vente restauration hébergement", "VENTE", q6ad, [8.9, 3.1, 41.8, 16.5, 29.7], None), ("service BNC Cipav", "CIPAV", q6b, [10.2, 1.4, 28.8, 25.6, 34], 22)]:
    for i, (s, v) in enumerate(zip(SPLIT, vals)):
        r = f"{C} . {x} . répartition . {s} . taux de répartition"
        ids = ([f"M0-{base + i:02d}"] if base else (["M0-21"] if s == "retraite complémentaire" else []))
        rule(r, "NEEDS_REVIEW", "high", [f"{LAW6} {'b)' if x == 'service BNC Cipav' else 'a/d)'}: \"{q[:80]}...\" -> {v} % ; engine G3 = {val(case + '@01/07/2025', r)} % on 01/07/2025 and {val(case + '@01/01/2026', r)} % on 01/01/2026", f"2026 version {N6} without text -> review when the text arrives"] + ev_link(ids))
rule(f"{DR} . taux service BIC", "NEEDS_REVIEW", "high", [f"D756-5 a) 1/6 of 21,2 % = 3,53 -> 3,6 % (rounded up); engine G3 = {val('DROM_BIC_P1@01/07/2025', DR + ' . taux service BIC')} % on 01/07/2025 (P1); fractions of a D613-4 rate whose 2026 version has no text"] + ev_link(["M0-30"]))
rule(f"{DR} . taux vente restauration hébergement", "NEEDS_REVIEW", "high", [f"D756-5 a) 1/6 of 12,3 % = 2,05 -> 2,1 %; engine G3 = {val('DROM_VENTE_P1@01/07/2025', DR + ' . taux vente restauration hébergement')} % on 01/07/2025 (P1); 2026 unknown"] + ev_link(["M0-31"]))
rule(f"{DR} . taux CIPAV", "NEEDS_REVIEW", "high", [f"PRE-EXISTING MISMATCH (not caused by S6->S7): D756-5 fractions of the CIPAV rate 23,2 % ({LAW4} b) = 7,8 / 11,6 / 15,5 %, engine G3 = {val('DROM_CIPAV_P1@01/07/2025', DR + ' . taux CIPAV')} / {val('DROM_CIPAV_P2@01/07/2025', DR + ' . taux CIPAV')} / {val('DROM_CIPAV_P3@01/07/2025', DR + ' . taux CIPAV')} % (fractions of the superseded 21,2 %); open since 07/2024 (R3); not fixed here because the 2026 version is unknown and the fix belongs to a dedicated change"] + ev_link(["M0-32", "M0-33", "M0-34"]))
# NEEDS_REVIEW by propagation
PROP = [C, f"{C} . service BNC", f"{C} . service BIC", f"{C} . vente restauration hébergement", f"{C} . service BNC Cipav", f"{AE} . cotisations et contributions", f"{AE} . revenu net", f"{AE} . revenu net . après impôt", f"{AE} . Cipav . retraite complémentaire", f"{AE} . Acre . taux service BIC", f"{AE} . Acre . taux vente restauration hébergement", f"{AE} . Acre . taux CIPAV"]
for x in ["service BNC", "service BIC", "vente restauration hébergement", "service BNC Cipav"]:
    PROP.append(f"{C} . {x} . répartition"); PROP += [f"{C} . {x} . répartition . {s}" for s in SPLIT]
PROP += [f"{C} . répartition"] + [f"{C} . répartition . {s}" for s in SPLIT + ["retraite"]]
for r in PROP:
    ev = ["propagates the D613-4 rate / D613-6 shares (no own constant); current-period values follow verified inputs, 2026 values follow unsupported inputs -> no own edit, review with the holders"]
    if (("BNC@01/07/2025", r) in B): ev.append(f"engine G3: {val('BNC@01/07/2025', r)} on 01/07/2025, {val('BNC@01/01/2026', r)} on 01/01/2026 (BNC situation, CA 1 000 €/mois)")
    rule(r, "NEEDS_REVIEW", "medium", ev)
rule(f"{C} . répartition . formation professionnelle", "UNAFFECTED", "high", ["= CFP (code du travail, outside the bounded set); no bounded article governing it changed"])
rule(DR, "UNAFFECTED", "high", ["applicability (outre-mer, periods) governed by D756-5 LEGIARTI000034726710: identical in S6 and S7 (compare_S6_S7: UNCHANGED)"])
rule("dirigeant . exonérations . ACRE", "UNAFFECTED", "high", ["governed by L613-7 LEGIARTI000048683570 and D131-6-1 LEGIARTI000036475110: identical version id, dates and text hash in S6 and S7"])
rule("entreprise . imposition . régime . micro-entreprise . revenu abattu", "UNAFFECTED", "high", ["abattement forfaitaire (CGI 50-0/102 ter via L613-7, unchanged S6->S7); T0 link L0012 RULE_CHANGED_CHECK_STILL_PASSES on G3"])
# everything else bounded -> UNAFFECTED (not re-examined)
IND_REASON = ("governed (where a bounded article applies) by L131-6, L136-3, D131-6-1, D136-5, D613-5, D621-2, D632-1, D633-3: all 8 have identical version id, in-force dates and text sha256 in S6 and S7 (work/law/compare_S6_S7.txt = UNCHANGED; sophon snapshots S6/S7); the only S6->S7 changes (D613-4, D613-6 future versions) do not govern indépendant rules. "
              "Not re-examined in M0; their alignment with G3 was last checked on earlier pins (store links L0028-L0055, L0075-L0109: on G3 mostly RULE_FILE_ABSENT/RULE_CHANGED after the 2025-09-19 reorganisation commit c4c603f6) -> inherited status, not re-verified here.")
AE_REASON = "auto-entrepreneur rule not governed by D613-4/D613-6 (TFC, CFP, impôt, affiliation, chiffre d'affaires, Acre grille: texts outside the bounded set or L613-7, unchanged S6->S7); no bounded article governing it changed"
not_re = []
bounded = [n for n in names if n.startswith("dirigeant . auto-entrepreneur") or n.startswith("dirigeant . indépendant") or n.startswith("dirigeant . exonérations")] + ["entreprise . imposition . régime . micro-entreprise . revenu abattu"]
for n in bounded:
    if n in seen: continue
    reason = IND_REASON if n.startswith("dirigeant . indépendant") else AE_REASON
    rule(n, "UNAFFECTED", "high" if n.startswith("dirigeant . indépendant") else "medium", [reason])
    not_re.append({"rule": n, "reason": reason})
reassessed = sorted({r for r in seen if R[[x["rule"] for x in R].index(r)]["classification"] != "UNAFFECTED"} | {DR, "dirigeant . exonérations . ACRE", "entreprise . imposition . régime . micro-entreprise . revenu abattu", f"{C} . répartition . formation professionnelle"})
# ---- evaluations
evals = []; abst = []; seen_ab = set()
ART = lambda r: "D756-5" if r.startswith(DR) else ("D613-6" if "répartition" in r else "D613-4")
TXT = {"D613-4": (V4, {"BNC": qe, "BIC": qd, "VENTE": qa, "CIPAV": qb}), "D613-6": (V6, {"BNC": q6e, "BIC": q6ad, "VENTE": q6ad, "CIPAV": q6b}), "D756-5": ("LEGIARTI000034726710", {"P1": q7a, "P2": q7b, "P3": q7c})}
for (case, r), (vb, unit, sit) in B.items():
    va = A.get((case, r), (None,))[0]; d = sit["date"]; art = ART(r); cat = case.split("@")[0].replace("DROM_", "").replace("ACRE_", "").split("_")[0]
    e = {"rule": r, "date": d, "situation": sit, "value_before_G3": vb, "value_after_proposal": va, "unit": unit, "article": art}
    if d == "01/07/2025":
        vid, qs = TXT[art]; per = case.split("_")[2].split("@")[0] if case.startswith("DROM") else None
        e.update({"article_version_id": vid, "in_force": "2025-01-01..2026-01-01" if art != "D756-5" else "2017-05-12..", "text_available": True, "quote": qs.get(per or cat)})
        if r.startswith(DR) and "CIPAV" in case: e["comment"] = "pre-existing mismatch: expected 7,8 / 11,6 / 15,5 % (fractions of 23,2 %)"
    elif d == "01/01/2026":
        vid = N6 if art == "D613-6" else (N4 if art == "D613-4" else "LEGIARTI000034726710 (D756-5 unchanged) x D613-4 " + N4)
        e.update({"article_version_id": vid, "text_available": False, "abstain": True, "comment": "value shown is the G3/proposal engine value, NOT derived from any available text: " + AB})
        if (r, d) not in seen_ab: seen_ab.add((r, d)); abst.append({"rule": r, "date": d, "article": art, "announced_version_id": vid, "reason": AB})
    else:
        e.update({"article_version_id": "LEGIARTI000049624068 (D613-4 v5, 2024-07-01..2025-01-01) / LEGIARTI000049625264 (D613-6 v6)", "text_available": False, "abstain": True, "comment": "control date; the text of these superseded versions is not in S6/S7 (only the current version's text is included) -> not re-cited here (earlier tasks verified them against S3)"})
    evals.append(e)
ch = [{"article": "D613-4", "current_version_id": V4, "current_in_force": "2025-01-01..2026-01-01", "current_text_changed": False, "current_text_sha256_prefix": "8c3b3865c4873f63",
       "withdrawn_version": {"id": M4, "etat_S6": "VIGUEUR_DIFF 2026-01-01..2999-01-01", "etat_S7": "MODIFIE_MORT_NE 2026-01-01..2025-09-10"},
       "new_version": {"id": N4, "etat": "VIGUEUR_DIFF", "in_force_from": "2026-01-01", "in_force_to": "2999-01-01", "version": "8.0", "text_available": False},
       "modifying_text": "NOT NAMED in S7: lienModifications still lists only 'Décret n°2024-484 du 30 mai 2024 - art. 1, 3°' (JORFTEXT000049620955, JORF 2024-05-31); the mort-ne dateFin 2025-09-10 points to a text of early September 2025 whose reference is not in the snapshot -> abstain on naming it",
       "what_changed": "The 2026-01-01 step of the 2024 decree will never enter into force; it is replaced by a version whose content is unknown here. G3's 2026 BNC rate (26,1 %) rests on the withdrawn step."},
      {"article": "D613-6", "current_version_id": V6, "current_in_force": "2025-01-01..2026-01-01", "current_text_changed": False, "current_text_sha256_prefix": "69b8e1b56c6185a7",
       "withdrawn_version": {"id": M6, "etat_S6": "VIGUEUR_DIFF 2026-01-01..2999-01-01", "etat_S7": "MODIFIE_MORT_NE 2026-01-01..2025-09-10"},
       "new_version": {"id": N6, "etat": "VIGUEUR_DIFF", "in_force_from": "2026-01-01", "in_force_to": "2999-01-01", "version": "9.0", "text_available": False},
       "modifying_text": "NOT NAMED in S7 (lienModifications: only 'Décret n°2024-484 du 30 mai 2024 - art. 2, 3°')", "what_changed": "Same pattern: the 2026 split step of the 2024 decree is withdrawn; G3's 2026 BNC shares (3 / 3,25 / 44,85 / 17,7 / 31,20 %) rest on it."}]
reports = sorted(glob.glob("work/sophon/reports/M0_*"))
ans = {"task": "M0", "decision_date": "2025-10-01", "law_snapshots": {"S6": "legi-data 2.464.0 (published 2025-09-01)", "S7": "legi-data 2.469.0 (published 2025-10-01)"}, "rules_pin": "G3 d6c374271727 (modele-social 10.0.0; 722 raw / 1427 parsed rules)",
       "unchanged_articles": ["L131-6", "L136-3", "L613-7", "D131-6-1", "D136-5", "D613-5", "D621-2", "D632-1", "D633-3", "D756-5"], "articles_missing_in_snapshot": [],
       "changed_articles": ch, "law_change_summary": CHG, "rules": R, "reassessed_rules": reassessed, "not_reassessed_rules": not_re, "no_change_needed": False,
       "proposal_dir": "work/proposals/M0/modele-social/règles", "proposal_nature": "documentation-only: références pinned to the S7 current version ids (D613-4 " + V4 + ", D613-6 " + V6 + "), notes recording that the 2026 branches rest on the withdrawn (mort-ne) versions and that the replacement versions have no text; NO numeric value changed (none is supported by available text)",
       "proposal_diff": "work/proposals/M0/CHANGES.diff", "build_ok": True, "build_counts": {"raw_rule_count": 722, "parsed_rule_count": 1427}, "proposal_vs_G3_changed_values": 0,
       "evaluations": evals, "abstentions": abst, "approval": "none recorded",
       "notes": "See output/NOTES.md. Only D613-4 and D613-6 changed between S6 and S7, and only in their future-version metadata: the 2026-01-01 versions announced by Décret 2024-484 are now MODIFIE_MORT_NE (ended 2025-09-10) and replaced by new versions (" + N4 + ", " + N6 + ") whose text is not in S7 and whose modifying text is not named. Current texts (2025 versions) are unchanged and G3 reproduces them (31 VERIFIED links). G3 already carries 2026 values transposed in 2024 from the withdrawn versions: they are now unsupported -> AFFECTED with abstention; no numeric edit proposed. Pre-existing, unrelated: DROM CIPAV fractions still computed on 21,2 % (3 FAILED links); meublés de tourisme 6 % not implemented. No value from outside the corpus (including later snapshots held in the store) was used.",
       "sophon_reports": reports, "sophon_snapshots": {"law": ["S6", "S7"], "rules": ["G3", "P_M0 (proposal copy)"]},
       "sophon_links_added": [{"spec_id": l["spec_id"], "link_id": LID(l["spec_id"]), "status": l.get("status"), "rule": spec[l["spec_id"]]["rule"], "article": spec[l["spec_id"]]["article"]} for l in links],
       "sophon_revalidate_S7_G3_counts": json.load(open("work/sophon/reports/M0_revalidate_S7_G3_cmd.json"))["counts"] if os.path.exists("work/sophon/reports/M0_revalidate_S7_G3_cmd.json") else None,
       "self_reported_tool_calls": CALLS}
os.makedirs("output", exist_ok=True)
json.dump(ans, open("output/answer.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cnt = {}
for r in R: cnt[r["classification"]] = cnt.get(r["classification"], 0) + 1
st = {}
for l in links: st[l.get("status")] = st.get(l.get("status"), 0) + 1
N = f"""# M0 — change maintenance, decision date 2025-10-01 (arm B)

Law snapshots S6 (legi-data 2.464.0, published 2025-09-01) and S7 (legi-data 2.469.0, published 2025-10-01); rules pin G3 d6c374271727 (modele-social 10.0.0, 722 raw / 1427 parsed rules). Store: snapshots S6, S7, G3, P_M0 registered; revalidate S7xG3 run first (counts {ans['sophon_revalidate_S7_G3_counts']}).

## 1. What changed between S6 and S7
Only **D613-4** and **D613-6**, and only in their future-version metadata (work/law/compare_S6_S7.txt; the 10 other bounded articles have identical version id, dates and text sha256):
- D613-4: current version {V4} (2025-01-01..2026-01-01) unchanged (sha256 8c3b3865...). The 2026-01-01 version announced as {M4} is now **MODIFIE_MORT_NE** (dateFin 2025-09-10); a new version **{N4}** (v8.0, VIGUEUR_DIFF 2026-01-01..2999-01-01) appears **without text**.
- D613-6: current version {V6} unchanged (sha256 69b8e1b5...). {M6} -> MODIFIE_MORT_NE (2025-09-10); new **{N6}** (v9.0, 2026-01-01) without text.
- Modifying text: **not named** in S7 (lienModifications still lists only Décret n°2024-484 du 30 mai 2024 art. 1, 3° / art. 2, 3°). The mort-né date points to a text of early September 2025; I abstain from naming it.

## 2. Why this matters for G3
G3 already carries `date >= 01/2026` branches in the AE rules: BNC rate **26,1 %**, BNC split 3 / 3,25 / 44,85 / 17,7 / 31,20 %, DROM BNC 4,4 / 13,1 / 17,4 %, Acre BNC rounding to 2 decimals. They were added on 2024-08-01 by commit 1d2874c5 ("Ajoute les taux de cotisation BNC pour 2025 et 2026") from the Décret 2024-484 schedule, i.e. from the versions that S7 now marks mort-né. No snapshot available to me ever carried the text of those versions, and the replacement versions have no text: **every 2026 value is unsupported -> abstain**. The 2025 values (current text) are reproduced exactly.

## 3. Engine evidence (G3, CA 1 000 €/mois; work/evals/M0_G3.jsonl, cases_M0.json)
| rule | 01/12/2024 | 01/07/2025 (text {V4}/{V6}) | 01/01/2026 (no text) |
|---|---|---|---|
| service BNC . taux | 23.1 | **24.6** ("{qe}") | 26.1 (abstain) |
| service BIC . taux | 21.2 | **21.2** ("{qd[-40:]}") | 21.2 (abstain) |
| vente . taux | 12.3 | **12.3** ("{qa}") | 12.3 (abstain) |
| service BNC Cipav . taux | 23.2 | **23.2** ("...{qb[-35:]}") | 23.2 (abstain) |
| BNC split (5 shares) | 3.6/3.7/50.75/7.85/34.1 | **3.4/3.5/47.6/13/32.5** (D613-6 e) | 3/3.25/44.85/17.7/31.2 (abstain) |
| BIC & vente split | 8.9/3.1/41.8/16.5/29.7 | **same** (D613-6 a/d) | same (abstain) |
| Cipav split | 10.2/1.4/28.8/25.6/34 | **same** (D613-6 b: 9,30+0,90 ; 1,40 ; 23,45+5,35 ; 25,60 ; 34,00) | same (abstain) |
| DROM BNC P1/P2/P3 | - | **4.1 / 12.3 / 16.4** (D756-5 1/6, 1/2, 2/3 of 24,6 %) | 4.4 / 13.1 / 17.4 (abstain) |
| DROM BIC P1, vente P1 | - | **3.6**, **2.1** (rounded up to 0,1) | - |
| DROM CIPAV P1/P2/P3 | - | 7.1 / 10.6 / 14.2 — **pre-existing mismatch** (expected 7,8 / 11,6 / 15,5 from 23,2 %) | - |
Acre rules evaluated non applicable (None) in the tested situations; no value asserted.

## 4. Classification ({cnt})
- **AFFECTED (8)**: `service BNC . taux`, the 5 `service BNC . répartition . * . taux de répartition`, `DROM . taux service BNC`, `Acre . taux service BNC` — their own 2026 branch rests on the withdrawn versions. Edit proposed: documentation only (références pinned to {V4} / {V6}, notes), **numeric values abstained**.
- **NEEDS_REVIEW**: BIC / vente / Cipav rates and splits (2025 verified; 2026 version textless), DROM BIC/vente/CIPAV fractions (CIPAV also pre-existing FAILED), and all rules that merely propagate these values (amounts, totals, revenu net, Acre BIC/vente/CIPAV, Cipav points).
- **UNAFFECTED / not re-examined**: all 273 `dirigeant . indépendant . *` rules, `dirigeant . exonérations . ACRE`, DROM applicability, TFC/CFP/impôt/affiliation AE rules, `revenu abattu`: their governing bounded articles are byte-identical in S6 and S7 (compare_S6_S7.txt) or outside the set. Their alignment with G3 itself was not re-verified in M0 (links from earlier pins show RULE_FILE_ABSENT/RULE_CHANGED after the 2025-09-19 indépendant reorganisation) — an inherited status, stated as such.

## 5. Proposal
`work/proposals/M0/modele-social/règles` (script work/scripts/apply_proposal_M0.py, diff CHANGES.diff): build OK (722/1427, same as G3), 0 changed values over the 25 cases (work/evals/M0_grid.txt). Registered as P_M0; revalidate S7xP_M0 in work/sophon/reports/.

## 6. Sophon
41 links M0-01..M0-41 on S7xG3 ({st}): 31 VERIFIED (2025 rates, splits, DROM BNC/BIC/vente), 3 FAILED (DROM CIPAV, documented pre-existing), 7 UNKNOWN (abstentions: 2026 versions without text; meublés de tourisme 6 % not implemented). Reports: {', '.join(os.path.basename(p) for p in reports)}.

## 7. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 8. Still open (unchanged by this task)
DROM CIPAV fractions on 21,2 % instead of 23,2 %; meublés de tourisme 6 % (D613-4 c) not implemented; D756-5 II CA cap; L613-7 minimum-contribution option; D613-5 conjoint collaborateur of AE; AE Acre rate article outside the set; 2026 values for D613-4 / D613-6 pending the text of {N4} / {N6}.
"""
open("output/NOTES.md", "w", encoding="utf-8").write(N)
json.load(open("output/answer.json")); print("answer.json valid:", len(R), "rules", cnt, "|", len(evals), "evaluations,", len(abst), "abstentions,", len(not_re), "not reassessed,", len(reassessed), "reassessed,", len(reports), "reports")
