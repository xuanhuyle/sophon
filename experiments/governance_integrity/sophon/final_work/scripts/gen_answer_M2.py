"""Builds output/answer.json and output/NOTES.md (+ work/notes/M2_NOTES.md) for M2 from the eval jsonl, link results, store snapshots and report files.
usage: python3 -I work/scripts/gen_answer_M2.py <self_calls>"""
import json, os, sys, glob, collections
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else None
def load(f):
    out = {}
    if not os.path.exists(f): return out
    for line in open(f, encoding='utf-8'):
        r = json.loads(line)
        try: res = json.loads(r["stdout"])
        except Exception: continue
        for k in ("results", "evaluations", "values"):
            if isinstance(res.get(k), dict): res = res[k]; break
        for k, v in res.items():
            if isinstance(v, dict) and "nodeValue" in v: out[(r["id"], k)] = (v.get("nodeValue"), v.get("unit"), r["situation"])
    return out
B = load("work/evals/M2_G4.jsonl"); A = load("work/evals/M2_proposal.jsonl")
BA = load("work/evals/M2_AE_G4.jsonl"); AA = load("work/evals/M2_AE_proposal.jsonl")
names = [l.rstrip("\n") for l in open("work/evals/list_G4_all.txt", encoding="utf-8")]
BOUND = [n for n in names if n.startswith("dirigeant . auto-entrepreneur") or n.startswith("dirigeant . indépendant") or n.startswith("dirigeant . exonérations")]
spec = {s["id"]: s for s in json.load(open("work/sophon/links_M2.json", encoding="utf-8"))}
def LL(f): return {json.loads(l)["spec_id"]: json.loads(l) for l in open(f, encoding="utf-8")} if os.path.exists(f) else {}
LG = LL("work/sophon/link_results_M2_G4.jsonl"); LP = LL("work/sophon/link_results_M2_P.jsonl")
def LID(l): return l.get("link_id") or l.get("id")
def ev_link(ids):
    out = []
    for i in ids:
        for tag, L in (("G4", LG), ("P_M2", LP)):
            l = L.get(i)
            if l: cr = l.get("check_result") or {}; out.append(f"sophon {i} on {tag} = link {LID(l)}: {l.get('status')} observed={cr.get('observed')} expected={cr.get('expected')}")
    return out
S8 = {a["num"]: a for lst in json.load(open("inputs/law/S8_legi-data-2.489.0/articles.json"))["articles"].values() for a in lst}
S9 = {a["num"]: a for lst in json.load(open("inputs/law/S9_legi-data-2.514.0/articles.json"))["articles"].values() for a in lst}
V9, V8 = "LEGIARTI000053451315", "LEGIARTI000036475110"
q = {k: spec[i]["quote"] for k, i in [("quart", "M2-01"), ("form", "M2-03"), ("E", "M2-09"), ("old_total", "M2-10"), ("old_form", "M2-11"), ("I", "M2-15"), ("III", "M2-16"), ("s60", "M2-17"), ("l1365", "M2-19"), ("e", "M2-21"), ("d7a", "M2-26")]}
NOTA9 = S9["D131-6-1"]["nota"]; NOTA8 = S8["D131-6-1"]["nota"]
LAW9 = f"D131-6-1 {V9} (VIGUEUR 2026-01-01..2999-01-01, v8.0; Décret n°2026-69 du 6 février 2026 art. 1, JORF 2026-02-08; S9 text sha256 {S9['D131-6-1']['text_sha256'][:16]}...; nota: \"{NOTA9}\")"
LAW8 = f"D131-6-1 {V8} (in force 2018-01-01..2026-01-01 per S9 metadata, v7.0; Décret n°2017-1894 du 30 décembre 2017 art. 1; S8 text sha256 {S8['D131-6-1']['text_sha256'][:16]}...)"
LAW4 = "D613-4 LEGIARTI000052218738 (VIGUEUR 2026-01-01; Décret n°2025-943 du 8 septembre 2025 art. 1; identical in S8 and S9)"
LAW7 = "D756-5 LEGIARTI000034726710 (in force 2017-05-12; identical in S8 and S9)"
IND = "dirigeant . indépendant . cotisations et contributions"; EX = IND + " . exonérations . ACRE"; AE = "dirigeant . auto-entrepreneur"
C = AE + " . cotisations et contributions . cotisations"; DR = AE + " . DROM"
# ---- store: which bounded rule files changed between G3 and G4 (evidence for not re-examining)
g3 = json.load(open("work/sophon/store/rules/G3.json")); g4 = json.load(open("work/sophon/store/rules/G4.json"))
def fh(v): return v if isinstance(v, str) else (v.get("sha256") or v.get("hash") or json.dumps(v, sort_keys=True))
F3, F4 = g3["files"], g4["files"]
files_changed = sorted(k for k in F4 if k in F3 and fh(F3[k]) != fh(F4[k])); files_new = sorted(k for k in F4 if k not in F3); files_gone = sorted(k for k in F3 if k not in F4)
def rh(v):
    if isinstance(v, str): return v
    if isinstance(v, dict):
        for k in v:
            if "sha" in k or "hash" in k: return v[k]
        return json.dumps(v, sort_keys=True)
    return str(v)
R3, R4 = g3["rules"], g4["rules"]
def top(n):
    best = None
    for t in R4:
        if n == t or n.startswith(t + " . "):
            if best is None or len(t) > len(best): best = t
    return best
def body_same(n):
    t = top(n)
    if t is None or t not in R3: return None
    return rh(R3[t]) == rh(R4[t])
RF = {}
_root = "inputs/rules/G4_a61b72947fec/modele-social/règles"
for _dp, _dn, _fn in os.walk(_root):
    for _f in _fn:
        if not _f.endswith(".publicodes"): continue
        _rel = os.path.relpath(os.path.join(_dp, _f), _root).replace(os.sep, "/")
        for _line in open(os.path.join(_dp, _f), encoding="utf-8"):
            if _line and not _line[0].isspace() and not _line.startswith("#") and _line.rstrip().endswith(":"): RF[_line.rstrip()[:-1]] = _rel
def rule_file(n): return RF.get(top(n))
# ---- helpers
def vb(case, r): v = B.get((case, r)); return None if v is None else v[0]
def va(case, r): v = A.get((case, r)); return None if v is None else v[0]
def pair(case, r, Bx=None, Ax=None):
    Bx = Bx or B; Ax = Ax or A; b = Bx.get((case, r)); a = Ax.get((case, r))
    return f"engine {r.replace(IND, 'IND').replace(C, 'COT').replace(DR, 'DROM')} [{case}]: G4 = {None if b is None else b[0]}{(' ' + (b[1] or '')) if b and b[1] else ''}, proposal = {None if a is None else a[0]}"
R = []; seen = set()
def rule(r, cl, conf, ev):
    if r in seen or r not in names: return
    seen.add(r); R.append({"rule": r, "classification": cl, "confidence": conf, "evidence": ev})
N20, N36, N42, N60 = "AC_cre2026_R20000@01/07/2026", "AC_cre2026_R36045@01/07/2026", "AC_cre2026_R42052.5@01/07/2026", "AC_cre2026_R60000@01/07/2026"
O20, O42, C20, C41, PL = "AC_cre072025_R20000@01/07/2026", "AC_cre072025_R42052.5@01/07/2026", "AC_cre2025_R20000@01/07/2025", "AC_cre2025_R41212@01/07/2025", "PLNR_cre2026_R20000@01/07/2026"
NEWTXT = f"{LAW9} II: \"{q['quart']}\" and \"{q['form'][q['form'].index('Montant'):]}\" -> for créations/reprises from 2026-01-01 the exoneration is a quarter of the contributions up to 3/4 PSS, then 0,25·E/(0,25·PSS)×(PSS−R) = E×(PSS−R)/PSS (25 % decreasing linearly to 0 at the PSS)"
OLDTXT = f"{LAW8} II: \"{q['old_total']}\" / \"{q['old_form']}\" -> total exoneration up to 3/4 PSS, then E/0,25 PSS × (PSS-R); still governs créations before 2026-01-01 (S9 nota)"
# ---------- AFFECTED: own edit
rule(EX + " . taux", "AFFECTED", "high", [NEWTXT, OLDTXT,
    pair(N20, EX + " . taux") + " (création 01/01/2026, R 20 000 <= 3/4 of PSS 2026 48 060)", pair(N36, EX + " . taux") + " (R = 36 045 = 3/4 PSS)",
    pair(N42, EX + " . taux") + " (R = 42 052,5 = 87,5 % PSS: formula gives 12,5 %)", pair(N60, EX + " . taux") + " (R > PSS: 0 in both texts)",
    pair(O20, EX + " . taux") + " (création 01/07/2025: old text keeps 100 %)", pair(O42, EX + " . taux") + " (création 2025, 87,5 % PSS: 50 %)", pair(C20, EX + " . taux") + " (2025 control)",
    "proposal: `variations` on `entreprise . date de création >= 01/01/2026` -> tranches 25 % / 0 %, sinon the former 100 % / 0 %; références pinned to " + V9 + " and " + V8 + "; note on the pre-existing E-vs-R deviation",
    "limit kept (pre-existing, T0 finding 4): the library applies the rate to the contributions at R, the text to E = contributions at 3/4 PSS (\"" + q['E'][:80] + "...\")"] + ev_link(["M2-01", "M2-02", "M2-03", "M2-04", "M2-10", "M2-11", "M2-12", "M2-13"]))
# ---------- AFFECTED: propagation (amounts change for créations 2026)
for child, cid_ev in [("retraite de base", "M2-05"), ("invalidité et décès", "M2-06"), ("indemnités journalières maladie", "M2-07"), ("maladie", None), ("allocations familiales", None)]:
    rule(EX + " . " + child, "AFFECTED", "high", [f"{LAW9} II: exonerated contributions include 'maladie, maternité, veuvage, vieillesse de base, invalidité et décès et d'allocations familiales'; the rule's `abattement: taux * prorata sur l'année` now receives 25 % instead of 100 % for créations 2026",
        pair(N20, EX + " . " + child), pair(N36, EX + " . " + child), pair(N42, EX + " . " + child), pair(O20, EX + " . " + child) + " (création 2025: unchanged)"] + (ev_link([cid_ev]) if cid_ev else []))
    rule(IND + " . " + child, "AFFECTED", "high", [f"replaced by `exonérations . ACRE . {child}` while the Acre applies (remplace); {LAW9} II quarter", pair(N20, IND + " . " + child), pair(N42, IND + " . " + child), pair(C20, IND + " . " + child) + " (2025 control unchanged)"])
rule(EX, "AFFECTED", "medium", [f"parent rule (valeur oui, applicable si dirigeant . exonérations . ACRE) unchanged itself, but all its `avec` children change for créations 2026 ({LAW9}); références pinned to {V9} in the proposal", pair(N20, EX), pair(N20, EX + " . taux")] + ev_link(["M2-09"]))
rule(IND + " . cotisations", "AFFECTED", "high", [f"{LAW9} II: sum of the contributions after the quarter exoneration", pair(N20, IND + " . cotisations") + " (1 400 retraite complémentaire + 3/4 × (3 550 + 260 + 100))", pair(N36, IND + " . cotisations"), pair(N42, IND + " . cotisations"), pair(O20, IND + " . cotisations") + " (création 2025 unchanged)", pair(C20, IND + " . cotisations")] + ev_link(["M2-08", "M2-14"]))
rule(IND + " . CSG-CRDS", "AFFECTED", "medium", ["changes only through its base (cotisations are added back to the CSG-CRDS base in the library; L136-3 identical S8/S9)", pair(N20, IND + " . CSG-CRDS"), pair(N42, IND + " . CSG-CRDS"), pair(O20, IND + " . CSG-CRDS") + " (unchanged)"])
rule(IND, "AFFECTED", "high", [f"total cotisations et contributions, {LAW9} II", pair(N20, IND), pair(N36, IND), pair(N42, IND), pair(N60, IND) + " (R > PSS: unchanged)", pair(PL, IND) + " (profession libérale non réglementée, same effect)", pair(O20, IND) + " (création 2025 unchanged)", pair(C20, IND) + " (2025 control)"])
# ---------- AFFECTED (carried over, pre-existing): DROM BNC 2026 on the mort-né basis
DP = {"P1": "DROM_BNC_P1@01/01/2026", "P2": "DROM_BNC_P2@01/01/2026", "P3": "DROM_BNC_P3@01/01/2026"}
rule(DR + " . taux service BNC", "AFFECTED", "high", [f"{LAW7} a)/b)/c): \"{q['d7a']}\" × {LAW4} e) \"{q['e']}\" -> 1/6, 1/2, 2/3 of 25,6 % rounded up to 0,1 = 4,3 / 12,8 / 17,1 %; G4 still carries 4,4 / 13,1 / 17,4 % (1/6, 1/2, 2/3 of the withdrawn 26,1 %); not caused by S9 (D613-4/D756-5 identical S8/S9) but by the pin change G3 -> G4 which left this rule untouched (commit 55470937 fixed only the CIPAV fractions)",
    pair(DP["P1"], DR + " . taux service BNC", BA, AA), pair(DP["P2"], DR + " . taux service BNC", BA, AA), pair(DP["P3"], DR + " . taux service BNC", BA, AA), pair("DROM_BNC_P1@01/07/2025", DR + " . taux service BNC", BA, AA) + " (2025: 4,1 unchanged)"] + ev_link(["M2-26", "M2-27", "M2-28"]))
for r in [C + " . service BNC", C]:
    rule(r, "AFFECTED", "medium", ["DROM BNC amounts follow the replaced rate (remplace)", pair(DP["P1"], r, BA, AA), pair(DP["P2"], r, BA, AA), pair(DP["P3"], r, BA, AA), pair("BNC@01/01/2026", r, BA, AA) + " (métropole: 25,6 % x 1 000 = 256, unchanged, confirmed by " + LAW4 + ")"] + ev_link(["M2-21"]))
# ---------- NEEDS_REVIEW
rule("dirigeant . exonérations . ACRE", "NEEDS_REVIEW", "medium", [f"{LAW9} I unchanged: \"{q['I']}\" -> the 12-month applicability (durée d'activité en début d'année < 1 an) stays; engine: " + pair(O20, "dirigeant . exonérations . ACRE") + ", " + pair(N20, "dirigeant . exonérations . ACRE"),
    f"NEW IV: \"{q['s60']}\" -> a 60-day filing deadline for the request of II of L. 131-6-4 (L. 131-6-4 outside the set); the rule has no request-date input: cannot be modelled from the available text; documentation added in the proposal (notes + référence pinned to {V9})",
    f"NEW II last sentence: \"{q['l1365']}\" -> L. 131-6-5 is outside the set: effect unknown, abstain"] + ev_link(["M2-15", "M2-17"]))
for r in [AE + " . Acre", AE + " . Acre . taux Acre", AE + " . Acre . taux service BNC", AE + " . Acre . taux service BIC", AE + " . Acre . taux vente restauration hébergement", AE + " . Acre . taux CIPAV", AE + " . Acre . notification calcul ACRE annuel"]:
    rule(r, "NEEDS_REVIEW", "low", [f"micro-social Acre rate (50 % of the D613-4 rates in the library; CIPAV 13,40 % from 01/2026 per G4 commit ea8f00f0) is fixed by an article outside the bounded set; {LAW9} II addresses the contributions 'mentionnées au 1° ou au 2° du II de l'article L. 131-6-4' with a revenue test, not the micro-social flat rates; whether the 2026 quarter has a micro-social counterpart cannot be checked here -> abstain (no numeric edit)",
        "engine probes (ACRE_BNC@01/01/2026, ACRE_BIC@01/01/2026, création 01/09/2025): `dirigeant . exonérations . ACRE`, `Acre . taux Acre`, `Acre . taux service BNC` evaluate None (non applicable) in the tested situations - pre-existing (M0/M1), not caused by S9"] + (ev_link(["M2-20"]) if r.endswith("taux Acre") else []))
rule(AE + " . éligible à l'ACRE", "NEEDS_REVIEW", "low", [f"{LAW9} IV: \"{q['s60'][:120]}...\" -> the micro-entrepreneur's request must be filed within 60 days; the eligibility rule (demandeur d'emploi, RSA, âge, QPV) has no request-date input; L. 131-6-4 outside the set -> abstain, documentation only"] + ev_link(["M2-18"]))
for r in [IND + " . Urssaf", IND + " . non déductibles", IND + " . CSG-CRDS . déductible", IND + " . CSG-CRDS . non déductible", IND + " . maladie . total", "dirigeant . indépendant . revenu net", "dirigeant . indépendant . revenu net . après impôt", "dirigeant . indépendant . cotisations et contributions . PCV"]:
    rule(r, "NEEDS_REVIEW", "medium", ["downstream of the AFFECTED contributions (sums / net income), not evaluated in M2; expected to move with `cotisations` for créations 2026 only"])
# ---------- UNAFFECTED after re-examination
rule(EX + " . prorata sur l'année", "UNAFFECTED", "high", [f"{LAW9} III: \"{q['III'][:140]}...\" unchanged in substance (only the marins sentence of III was deleted: outside the library's scope); the rule (1 an - durée en début d'année)/1 an unchanged", pair(O20, EX + " . prorata sur l'année") + " (création 01/07/2025: 49 %)", pair(N20, EX + " . prorata sur l'année")] + ev_link(["M2-16"]))
rule(IND + " . exonérations . DROM", "UNAFFECTED", "high", ["rend non applicable exonérations . ACRE; D131-6-1 change does not touch the DROM exclusion; rule body unchanged G3 -> G4 (store hash)"])
rule(IND + " . exonérations", "UNAFFECTED", "medium", ["somme: ZFU only (ACRE acts through remplace, not through this sum); unchanged body"])
rule(DR + " . taux CIPAV", "UNAFFECTED", "high", [f"{LAW7} a) 1/3 of 23,2 % ({LAW4} b) = 7,8 % - G4 commit 55470937 (2026-01-08) fixed the fractions 7,8 / 11,6 / 15,5 for date >= 07/2024 (M1 pre-existing misalignment closed by the pin)", pair("DROM_CIPAV_P1@01/01/2026", DR + " . taux CIPAV", BA, AA), pair("DROM_CIPAV_P2@01/01/2026", DR + " . taux CIPAV", BA, AA), pair("DROM_CIPAV_P3@01/01/2026", DR + " . taux CIPAV", BA, AA)] + ev_link(["M2-25"]))
for r, cse, ids in [(C + " . service BNC . taux", "BNC@01/01/2026", ["M2-21"]), (C + " . service BIC . taux", "BIC@01/01/2026", []), (C + " . vente restauration hébergement . taux", "VENTE@01/01/2026", []), (C + " . service BNC Cipav . taux", "CIPAV@01/01/2026", [])]:
    rule(r, "UNAFFECTED", "high", [f"{LAW4} (identical S8 -> S9); G4 commit 88cb2ce9 (2026-01-08) transposed the 2026 values (BNC 26,1 -> 25,6 %; the M1 proposal values); AE grid G4 == M1 proposal for all 39 cases except DROM BNC 2026 (work/evals/M2_AE_grid_PM1_vs_G4.txt)", pair(cse, r, BA, AA), pair(cse.replace("01/01/2026", "01/12/2025"), r, BA, AA) + " (2025 control)", "revalidate S9xG4: the M1 links on this rule re-run on G4 -> RULE_CHANGED_CHECK_STILL_PASSES (work/sophon/reports/M2_revalidate_S9_G4.md)"] + ev_link(ids))
SPLIT = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"]
for cat, cse, ids in [("service BNC", "BNC@01/01/2026", ["M2-22"]), ("service BIC", "BIC@01/01/2026", ["M2-23"]), ("vente restauration hébergement", "VENTE@01/01/2026", []), ("service BNC Cipav", "CIPAV@01/01/2026", ["M2-24"])]:
    for s in SPLIT:
        r = f"{C} . {cat} . répartition . {s} . taux de répartition"
        rule(r, "UNAFFECTED", "high", ["D613-6 LEGIARTI000052218747 (identical S8 -> S9); 2026 share transposed by G4 commit 88cb2ce9 (values = M1 proposal)", pair(cse, r, BA, AA), "revalidate S9xG4: M1 link on this rule -> RULE_CHANGED_CHECK_STILL_PASSES"] + (ev_link(ids) if s == SPLIT[0] else []))
    for r in [f"{C} . {cat}"] + [f"{C} . répartition . {s}" for s in SPLIT]:
        if r == C + " . service BNC": continue
        rule(r, "UNAFFECTED", "high", ["amounts follow the (confirmed) 2026 rates/shares; `arrondi: oui` added by G4 commit 88cb2ce9 only rounds €/mois amounts (41.0 -> 41)", pair(cse, r, BA, AA)])
for r in [DR, DR + " . taux service BIC", DR + " . taux vente restauration hébergement", AE + " . cotisations et contributions"]:
    rule(r, "UNAFFECTED", "high", ["D756-5 / D613-4 identical S8 -> S9; BIC and vente fractions 3,6/10,6/14,2 and 2,1/6,2/8,2 unchanged", pair("DROM_BIC_P1@01/01/2026", DR + " . taux service BIC", BA, AA), pair("DROM_VENTE_P3@01/01/2026", DR + " . taux vente restauration hébergement", BA, AA), pair("BNC@01/01/2026", AE + " . cotisations et contributions", BA, AA)])
for r in [AE + " . impôt . versement libératoire . plafond", AE + " . impôt . versement libératoire . seuil dépassé", AE + " . impôt . versement libératoire"]:
    rule(r, "UNAFFECTED", "high", ["changed/added by G4 commit bdfbd61c (2026-01-08, versement libératoire 2026 plafond 29 315 € par part): income-tax rule, no governing article in the bounded CSS set; no CSS article changed for it"])
reassessed = sorted(seen)
# ---------- not re-examined (evidence per rule)
unchanged_arts = sorted(a for a in S9 if S9[a]["id"] == S8[a]["id"] and S9[a]["text_sha256"] == S8[a]["text_sha256"])
not_re = []
for n in BOUND:
    if n in seen: continue
    same = body_same(n); fchg = rule_file(n)
    if same is True: why = "governing bounded articles identical in S8 and S9 (11 of 12 articles: same LEGIARTI id and text sha256, work/law/compare_S8_S9.txt; only D131-6-1 changed and this rule is not an Acre rule) AND the top-level rule body hash is identical in the G3 and G4 store snapshots -> alignment status inherited from M0/M1/T-tasks"
    elif same is False:
        f = rule_file(n) or "?"
        if "professions-lib" in f: why = f"governing bounded articles identical in S8 and S9; the rule's file {f} changed G3 -> G4 (2026-01 commits: PAMC chirurgiens-dentistes fix 5e179027, PAM assistant decommissioning eb326bf2/4f388600, caisse base values d825585b/c044af4d) but the PL caisse rules are governed by articles outside the bounded set (CNAVPL sections) and no bounded article changed; not evaluated in M2"
        elif "auto-entrepreneur" in f: why = f"governing bounded articles identical in S8 and S9; the top-level rule body changed G3 -> G4 (file {f}; commits 88cb2ce9 / 55470937 / ea8f00f0 / bdfbd61c: 2026 D613-4/D613-6 constants, DROM CIPAV fractions, Acre CIPAV 13,40 %, versement libératoire), covered by the AE regression grid (39 cases, G4 == M1 proposal except DROM BNC 2026) and the revalidated M1 links; this specific sub-rule was not evaluated"
        else: why = f"governing bounded articles identical in S8 and S9; the top-level rule body changed G3 -> G4 (file {f}); not an Acre rule; not evaluated in M2"
    else: why = "rule not present as a top-level rule in the G3 store snapshot (new or nested name); governing bounded articles identical in S8 and S9"
    not_re.append({"rule": n, "reason": why})
# ---------- evaluations list
evals = []
def addev(case, r, Bx, Ax, law):
    b = Bx.get((case, r)); a = Ax.get((case, r))
    if b is None and a is None: return
    sit = (b or a)[2]
    evals.append({"rule": r, "case": case, "situation": sit, "date": sit.get("date"), "value_G4": None if b is None else b[0], "value_proposal": None if a is None else a[0], "unit": (b or a)[1], "law": law})
for case in [N20, N36, N42, N60, PL, O20, O42, C20, C41, "AC_cre2026_R20000_noACRE@01/07/2026"]:
    for r in [EX + " . taux", EX + " . prorata sur l'année", IND + " . retraite de base", IND + " . invalidité et décès", IND + " . indemnités journalières maladie", IND + " . maladie", IND + " . allocations familiales", IND + " . CSG-CRDS", IND + " . cotisations", IND, "dirigeant . indépendant . PSS proratisé", "dirigeant . exonérations . ACRE"]:
        addev(case, r, B, A, LAW9 if "cre2026" in case else LAW8)
for case in ["DROM_BNC_P1@01/01/2026", "DROM_BNC_P2@01/01/2026", "DROM_BNC_P3@01/01/2026", "DROM_BNC_P1@01/07/2025", "DROM_CIPAV_P1@01/01/2026", "BNC@01/01/2026", "BIC@01/01/2026", "CIPAV@01/01/2026", "VENTE@01/01/2026"]:
    for r in [DR + " . taux service BNC", DR + " . taux CIPAV", C + " . service BNC . taux", C + " . service BIC . taux", C + " . service BNC Cipav . taux", C + " . vente restauration hébergement . taux", C + " . service BNC", C, C + " . service BNC . répartition . maladie-maternité . taux de répartition", C + " . service BIC . répartition . maladie-maternité . taux de répartition", C + " . service BNC Cipav . répartition . maladie-maternité . taux de répartition"]:
        addev(case, r, BA, AA, LAW4 + " / D613-6 LEGIARTI000052218747 / " + LAW7)
abst = [
    {"topic": "L. 131-6-5 reservation", "why": f"\"{q['l1365']}\" - L. 131-6-5 is not in the bounded set; its effect on the quarter exoneration is unknown", "law": LAW9},
    {"topic": "60-day request deadline (IV)", "why": f"\"{q['s60'][:150]}...\" - procedural condition on the request of II of L. 131-6-4 (outside the set); no request-date input exists; documented, not modelled", "law": LAW9},
    {"topic": "micro-social Acre rate", "why": "the AE Acre rate (50 %, CIPAV 13,40 % in G4) is fixed by an article outside the set; whether the 2026 quarter has a micro-social counterpart cannot be checked; AE Acre rules evaluate None in the probes", "law": LAW9},
    {"topic": "E vs R in the degressive zone", "why": f"\"{q['E'][:100]}...\": the text applies the rate to E (contributions at 3/4 PSS), the library to the contributions at R; pre-existing structure kept, documented in the proposal note", "law": LAW9},
    {"topic": "transitional cases", "why": "the S9 nota ties the new text to créations/reprises from 2026-01-01; the proposal uses `entreprise . date de création >= 01/01/2026` (reprises are not distinguished in the library); affiliation-date nuances (I: 'date d'effet d'affiliation') are not modelled", "law": LAW9},
    {"topic": "salarié Acre rules", "why": "salarié . cotisations . exonérations . Acre . * (assimilés salariés) cite D131-6-1 LEGIARTI000036475110 and implement the former 100 % / degressive rule; they are outside the bounded rule files, so not classified here, but the same 2026 change applies to 'la rémunération' - flagged for the salarié maintainer", "law": LAW9},
    {"topic": "D613-4 c) meublés de tourisme, D756-5 II CA cap, L613-7 minimum option, D613-5 conjoint collaborateur AE", "why": "still not implemented (unchanged since T0/M1); texts identical S8 -> S9", "law": "S9"}]
ch = [{"article": "D131-6-1", "old_version_id": V8, "old_in_force": "2018-01-01..2026-01-01 (etat in S9: MODIFIE; VIGUEUR in S8)", "old_text_sha256_prefix": S8["D131-6-1"]["text_sha256"][:16], "old_modifying_text": "Décret n°2017-1894 du 30 décembre 2017 - art. 1 (JORFTEXT000036342439)", "old_nota": NOTA8,
       "new_version_id": V9, "new_etat": "VIGUEUR", "new_in_force": "2026-01-01..2999-01-01", "version": "8.0", "new_text_sha256_prefix": S9["D131-6-1"]["text_sha256"][:16], "text_available": True,
       "modifying_text": "Décret n°2026-69 du 6 février 2026 - art. 1 (JORFTEXT000053449085, JORF 2026-02-08, dateDebutCible 2026-02-09)", "new_nota": NOTA9,
       "text_changes": "II: 'correspond au montant total des cotisations' -> 'correspond au quart du montant total des cotisations'; formula 'E/0,25 PSS × (PSS-R)' -> '0,25 E/0,25 PSS×(PSS−R).'; new sentence 'Les dispositions du présent II s'appliquent sans préjudice des dispositions de l'article L. 131-6-5.'; III: marins sentence deleted; IV: new 60-day deadline for the request of II of L. 131-6-4 (word-level diff in work/law/compare_S8_S9.txt: 7 ops)"}]
CHG = (f"S8 -> S9 (decision date 2026-03-31): only D131-6-1 changed: {V8} -> {V9} (VIGUEUR 2026-01-01, v8.0, Décret n°2026-69 du 6 février 2026 art. 1; nota: applies to créations et reprises from 2026-01-01). The Acre exoneration of non-micro indépendants becomes a quarter of the contributions below 3/4 PSS and 0,25·E/(0,25·PSS)×(PSS−R) between 3/4 PSS and PSS; L. 131-6-5 reservation and a 60-day request deadline added; marins sentence deleted. "
       "The 11 other bounded articles are byte-identical (same LEGIARTI id and text sha256). Rules pin moved G3 -> G4 (commits of 2026-01-08/27 transposed the 2026 D613-4/D613-6 values and the DROM CIPAV fractions; DROM BNC 2026 left on the mort-né basis).")
reports = sorted(glob.glob("work/sophon/reports/M2_*"))
def cnt(L): c = {}; [c.__setitem__(l.get("status"), c.get(l.get("status"), 0) + 1) for l in L.values()]; return c
def counts(f):
    if not os.path.exists(f): return None
    first = open(f, encoding="utf-8").read().strip().splitlines()
    if not first or not first[0].startswith("{"): return None
    try: return json.loads(first[0]).get("counts")
    except Exception: return None
revc = counts("work/sophon/reports/M2_revalidate_S9_G4_cmd.json"); revp = counts("work/sophon/reports/M2_revalidate_S9_PM2_cmd.json")
rows = json.load(open("work/sophon/reports/M2_revalidate_S9_G4.json"))["rows"] if os.path.exists("work/sophon/reports/M2_revalidate_S9_G4.json") else []
d131 = collections.Counter((r.get("status")) for r in rows if r.get("article") == "D131-6-1"); d131_rules = sorted(set(r.get("rule") for r in rows if r.get("article") == "D131-6-1"))
cl = collections.Counter(r["classification"] for r in R)
ans = {"task": "M2", "decision_date": "2026-03-31", "law_snapshots": {"S8": "legi-data 2.489.0 (published 2026-01-01)", "S9": "legi-data 2.514.0 (published 2026-03-31)"}, "rules_pin": "G4 a61b72947fec (modele-social 10.0.1, committed 2026-03-03; 652 raw / 1334 parsed rules; previous task pin G3 d6c374271727)",
       "unchanged_articles": unchanged_arts, "articles_missing_in_snapshot": [], "changed_articles": ch, "law_change_summary": CHG,
       "rules_pin_change_G3_to_G4": {"bounded_files_changed": files_changed, "files_new": files_new, "files_gone": files_gone, "bounded_rule_names_added": [n for n in BOUND if n not in set(l.rstrip("\n") for l in open("work/evals/list_G3_all.txt", encoding="utf-8"))], "commits": ["88cb2ce9 2026-01-08 AE taux/répartition 2026 (BNC 25,6 %, splits, arrondi, références D613-4/D613-6 pinned)", "55470937 2026-01-08 DROM CIPAV 7,8/11,6/15,5 from 07/2024", "ea8f00f0 2026-01-27 Acre CIPAV 13,40 % from 01/2026", "bdfbd61c 2026-01-08 versement libératoire plafond", "34bb4f5d / f0df08a4 dirigeant.publicodes (résumé text, RGDU reference; not bounded rules)"]},
       "rules": R, "reassessed_rules": reassessed, "not_reassessed_rules": not_re, "no_change_needed": False,
       "proposal_dir": "work/proposals/M2/modele-social/règles", "proposal_script": "work/scripts/apply_proposal_M2.py", "proposal_diff": "work/proposals/M2/CHANGES.diff",
       "proposal_nature": f"indépendant Acre rate: `variations` on `entreprise . date de création >= 01/01/2026` -> taux progressif 25 % up to 75 % PSS then 0 % at 100 % (D131-6-1 {V9}), sinon former 100 %/0 % ({V8}); références pinned, note; `dirigeant . exonérations . ACRE` documentation (60-day deadline, L. 131-6-5, référence {V9}); DROM BNC 2026 fractions 4,3/12,8/17,1 (D613-4 LEGIARTI000052218738 x D756-5; carried-over M1 fix)",
       "build_ok": True, "build_counts": {"raw_rule_count": 652, "parsed_rule_count": 1334},
       "proposal_vs_G4_changed_values": sum(1 for k in B if A.get(k, (None,))[0] != B[k][0]) + sum(1 for k in BA if AA.get(k, (None,))[0] != BA[k][0]), "evaluations": evals, "abstentions": abst, "approval": "none recorded",
       "notes": "See output/NOTES.md. " + CHG + " G4 applies 100 % Acre exoneration to a création 2026 (R 20 000: cotisations 1 400 €/an) where the in-force text gives a quarter (proposal: 4 333 €/an); créations 2025 and 2025 controls unchanged. No value from outside S8/S9 was used; no approval exists in the corpus.",
       "sophon_reports": reports, "sophon_snapshots": {"law": ["S8 (re-registered, identical sha256 3c116e2d...)", "S9 (re-registered, identical sha256 3f5a99e1...)"], "rules": ["G4 (already registered in R4; 58/58 file hashes identical to the staged tree, not re-registered)", "P_M2 (proposal copy)"]},
       "sophon_links_added": [{"spec_id": i, "rules_snapshot": tag, "law_snapshot": spec[i].get("law", "S9"), "link_id": LID(l), "status": l.get("status"), "rule": spec[i]["rule"], "article": spec[i]["article"]} for tag, L in (("G4", LG), ("P_M2", LP)) for i, l in L.items()],
       "sophon_link_status_counts": {"G4": cnt(LG), "P_M2": cnt(LP)}, "sophon_revalidate_S9_G4_counts_before_M2_links": revc, "sophon_revalidate_S9_PM2_counts": revp,
       "sophon_revalidate_S9_G4_D131-6-1_links": {"statuses": dict(d131), "rules": d131_rules}, "self_reported_tool_calls": CALLS}
os.makedirs("output", exist_ok=True)
json.dump(ans, open("output/answer.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def fmt(v): return round(v, 4) if isinstance(v, float) else v
def g(case, r, Bx=B, Ax=A): b = Bx.get((case, r)); a = Ax.get((case, r)); return f"{None if b is None else fmt(b[0])} -> {None if a is None else fmt(a[0])}"
N = f"""# M2 — change maintenance, decision date 2026-03-31 (arm B)

Law snapshots S8 (legi-data 2.489.0, published 2026-01-01) and S9 (legi-data 2.514.0, published 2026-03-31); rules pin **G4 a61b72947fec** (modele-social 10.0.1, 2026-03-03; 652 raw / 1334 parsed) — the pin also moved from G3 (M1). Store: S8/S9 re-registered (identical hashes), G4 already registered (58/58 file hashes identical), P_M2 registered; revalidate S9×G4 run first: {revc}; D131-6-1 links in that report: {dict(d131)}.

## 1. What changed between S8 and S9 (work/law/compare_S8_S9.txt, work/law/S9_dump.txt)
Only **D131-6-1**: {V8} (2018-01-01..2026-01-01, now MODIFIE) -> **{V9}** (VIGUEUR 2026-01-01..2999-01-01, v8.0, sha256 {S9['D131-6-1']['text_sha256'][:12]}…). Modifying text: **Décret n°2026-69 du 6 février 2026, art. 1** (JORF 2026-02-08). Nota: "{NOTA9}"
- II: "{q['quart'][-120:]}" (was "…{q['old_total'][-60:]}"); formula "{q['form'][-70:]}" (was "{q['old_form']}"); new: "{q['l1365']}".
- III: the marins sentence is deleted (outside the library's scope). IV new: "{q['s60'][:170]}…".
The 11 other bounded articles have identical version ids and text sha256 ({', '.join(unchanged_arts)}).

## 2. Rules pin G3 -> G4 (inputs HISTORY / history_bounded_rules.patch; store file hashes)
Bounded files changed: {', '.join(files_changed) or 'none'}. Commits 88cb2ce9 + 55470937 (2026-01-08) and ea8f00f0 (2026-01-27) transposed the 2026 D613-4/D613-6 values (BNC 25,6 %, all splits, `arrondi`, références pinned to LEGIARTI000052218738/…747) and fixed the DROM CIPAV fractions (7,8/11,6/15,5 from 07/2024): G4 equals my M1 proposal on all 39 AE cases except **DROM BNC 2026 (4,4/13,1/17,4 kept, mort-né basis)** (work/evals/M2_AE_grid_PM1_vs_G4.txt). No dirigeant/indépendant/*.publicodes or dirigeant/exonérations* file changed; dirigeant/professions-libérales/CARCDSF, CAVP, CNBF, PAMC changed (caisse values / PAMC fixes; articles outside the set), plus non-bounded files (base.publicodes: Smic/PSS 2026, salarié, impôt). New bounded name: `dirigeant . auto-entrepreneur . impôt . versement libératoire . plafond` (tax, no CSS article).

## 3. Impact on G4 — indépendant Acre (D131-6-1 II)
`{EX} . taux` is a `taux progressif` 100 % up to 75 % of `PSS proratisé`, 0 % at 100 %, whatever the creation date. For créations/reprises from 2026-01-01 the text now gives a quarter: AFFECTED.

## 4. Engine evidence (work/evals/M2_G4.jsonl vs M2_proposal.jsonl, grid M2_grid.txt; PSS 2026 = 48 060 €/an, 2025 = 47 100)
| case (EI/IR commerciale, Acre oui) | ACRE . taux | retraite de base | invalidité-décès | IJ maladie | cotisations | total cot.+contrib. |
|---|---|---|---|---|---|---|
| création 01/01/2026, R 20 000, 01/07/2026 | {g(N20, EX + ' . taux')} | {g(N20, IND + ' . retraite de base')} | {g(N20, IND + ' . invalidité et décès')} | {g(N20, IND + ' . indemnités journalières maladie')} | {g(N20, IND + ' . cotisations')} | {g(N20, IND)} |
| création 2026, R 36 045 (= 3/4 PSS) | {g(N36, EX + ' . taux')} | {g(N36, IND + ' . retraite de base')} | {g(N36, IND + ' . invalidité et décès')} | {g(N36, IND + ' . indemnités journalières maladie')} | {g(N36, IND + ' . cotisations')} | {g(N36, IND)} |
| création 2026, R 42 052,5 (87,5 % PSS) | {g(N42, EX + ' . taux')} | {g(N42, IND + ' . retraite de base')} | {g(N42, IND + ' . invalidité et décès')} | {g(N42, IND + ' . indemnités journalières maladie')} | {g(N42, IND + ' . cotisations')} | {g(N42, IND)} |
| création 2026, R 60 000 (> PSS) | {g(N60, EX + ' . taux')} | {g(N60, IND + ' . retraite de base')} | - | - | {g(N60, IND + ' . cotisations')} | {g(N60, IND)} |
| PLNR création 2026, R 20 000 | {g(PL, EX + ' . taux')} | {g(PL, IND + ' . retraite de base')} | {g(PL, IND + ' . invalidité et décès')} | {g(PL, IND + ' . indemnités journalières maladie')} | {g(PL, IND + ' . cotisations')} | {g(PL, IND)} |
| création 01/07/2025, R 20 000, 01/07/2026 (old text, prorata {vb(O20, EX + " . prorata sur l'année")} %) | {g(O20, EX + ' . taux')} | {g(O20, IND + ' . retraite de base')} | {g(O20, IND + ' . invalidité et décès')} | {g(O20, IND + ' . indemnités journalières maladie')} | {g(O20, IND + ' . cotisations')} | {g(O20, IND)} |
| création 2025, R 42 052,5, 01/07/2026 | {g(O42, EX + ' . taux')} | {g(O42, IND + ' . retraite de base')} | - | - | {g(O42, IND + ' . cotisations')} | {g(O42, IND)} |
| 2025 control, création 01/01/2025, R 20 000 / 41 212,5 | {g(C20, EX + ' . taux')} / {g(C41, EX + ' . taux')} | - | - | - | {g(C20, IND + ' . cotisations')} / {g(C41, IND + ' . cotisations')} | {g(C20, IND)} |
Acre non (création 2026, R 20 000): retraite de base {vb('AC_cre2026_R20000_noACRE@01/07/2026', IND + ' . retraite de base')}, invalidité-décès {vb('AC_cre2026_R20000_noACRE@01/07/2026', IND + ' . invalidité et décès')}, IJ {vb('AC_cre2026_R20000_noACRE@01/07/2026', IND + ' . indemnités journalières maladie')}, cotisations {vb('AC_cre2026_R20000_noACRE@01/07/2026', IND + ' . cotisations')} €/an -> the proposal's 2 663 / 195 / 75 are 3/4 of these (quarter exonerated).
DROM BNC 01/01/2026 (AE grid): P1 {g(DP['P1'], DR + ' . taux service BNC', BA, AA)}, P2 {g(DP['P2'], DR + ' . taux service BNC', BA, AA)}, P3 {g(DP['P3'], DR + ' . taux service BNC', BA, AA)} %; everything else in the 39 AE cases identical G4 = proposal.

## 5. Classification ({dict(cl)}; {len(reassessed)} rules re-examined, {len(not_re)} not re-examined)
- **AFFECTED (own edit, high)**: `{EX} . taux`. **AFFECTED (propagation)**: `{EX}` and its 5 children, `IND . maladie / retraite de base / invalidité et décès / allocations familiales / indemnités journalières maladie / CSG-CRDS / cotisations`, `{IND}`; carried-over: `{DR} . taux service BNC` (+ BNC amount / cotisations in DROM).
- **NEEDS_REVIEW**: `dirigeant . exonérations . ACRE` (I unchanged; IV 60-day deadline and L. 131-6-5 not modelled, documentation added); the 7 AE `Acre` rules and `éligible à l'ACRE` (micro-social Acre article outside the set; probes evaluate None); 8 downstream indépendant sums/net not evaluated.
- **UNAFFECTED after re-examination**: `ACRE . prorata sur l'année` (III), `exonérations . DROM`, `exonérations`, the AE 2026 rates/splits/amounts (G4 == M1 proposal, revalidated M1 links RULE_CHANGED_CHECK_STILL_PASSES, fresh links M2-21..25 VERIFIED), DROM CIPAV/BIC/vente, versement libératoire rules (no CSS article).
- **Not re-examined** ({len(not_re)} rules): governing articles byte-identical S8 -> S9 and top-level rule body hash identical G3 -> G4 in the store (or body changed only by the AE 2026 constants covered by the regression grid) — reasons per rule in answer.json.

## 6. Proposal
`work/proposals/M2/modele-social/règles` (script work/scripts/apply_proposal_M2.py, diff CHANGES.diff, registered as P_M2): build OK 652/1334; {ans['proposal_vs_G4_changed_values']} changed values over the 10 + 39 cases, all for créations 2026 or DROM BNC 2026. Condition chosen: `entreprise . date de création >= 01/01/2026` (nota: créations et reprises à compter de cette date), not the evaluation date.

## 7. Abstentions
{chr(10).join('- ' + a['topic'] + ': ' + a['why'] for a in abst)}

## 8. Sophon
28 links M2-01..28 recorded twice: on G4 {cnt(LG)} (FAILED = the 2026-création quarter and DROM BNC 2026) and on P_M2 {cnt(LP)}. Revalidate S9×P_M2: {revp}. Reports: {', '.join(os.path.basename(p) for p in reports)}.

## 9. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 10. Still open
L. 131-6-5 and L. 131-6-4 texts; micro-social Acre rate article; 60-day request deadline; salarié Acre rules (outside bounded files) still on the 2018 text; E-vs-R structure of the degressive zone; meublés de tourisme 6 %; D756-5 II CA cap; L613-7 minimum option; D613-5 conjoint collaborateur AE; AE Acre rules non applicable in probes.
"""
open("output/NOTES.md", "w", encoding="utf-8").write(N); os.makedirs("work/notes", exist_ok=True); open("work/notes/M2_NOTES.md", "w", encoding="utf-8").write(N)
json.load(open("output/answer.json")); print("answer.json valid:", len(R), "rules", dict(cl), "|", len(evals), "evaluations,", len(abst), "abstentions,", len(not_re), "not reassessed,", len(reassessed), "reassessed,", len(reports), "reports; links G4", cnt(LG), "P", cnt(LP), "| files changed G3->G4:", files_changed, "| D131 rows:", dict(d131))
