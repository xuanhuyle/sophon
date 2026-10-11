#!/usr/bin/env python3
"""R5 links: law S10 (legi-data 2.572.0; texts identical to S9) <-> `indépendant . cotisations et contributions . assiette
CSG-CRDS . abattement` / `assiette sociale` on the two trees of commit c14ee26d0c67 ("fix: n'applique pas de plancher ni de
plafond à l'abattement sur l'assiette à Mayotte"): G4pre_R5 (parent tree) and G4post_R5 (after tree).
Articles: L136-3 III (v.LEGIARTI000051284498, 2025-02-28), D136-5 (v.LEGIARTI000049899286, 2024-07-07), L131-6 I
(v.LEGIARTI000048683707, 2023-12-28). None of the 12 bounded articles mentions Mayotte.
usage: python3 -I work/scripts/add_links_R5.py   (from the staging dir). Appends to work/sophon/link_results_R5.jsonl.
Situations are taken by id from work/evals/cases_R5.json (the same ones as the before/after evals)."""
import json, re, subprocess, sys
STORE, LAW = 'work/sophon/store', 'S10'
raw = json.load(open('inputs/law/S10_legi-data-2.572.0/articles.json'))['articles']
arts = {k: v[0] for k, v in raw.items()}
def flex(s): return ''.join(r'\s+' if c == ' ' else (r"['’]\s?" if c == "'" else re.escape(c)) for c in s)
def q(num, s):
    m = re.search(flex(s), arts[num]['text']); assert m, (num, s); return m.group(0)
Q_L136_FLOOR = q('L136-3', "fait l'objet d'un abattement de 26 %. Toutefois, cet abattement ne peut être ni inférieur à un montant plancher, fixé par décret")
Q_L136_CEIL = q('L136-3', "ni supérieur à un montant plafond fixé, également par décret")
Q_D136_I = q('D136-5', "Le montant plancher prévu au III de l'article L. 136-3 est fixé à 1,76 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3")
Q_D136_II = q('D136-5', "Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3")
Q_L131 = q('L131-6', "sont assises sur l'assiette définie à l'article L. 136-3")
V = {k: arts[k]['id'] for k in ('L131-6', 'L136-3', 'D136-5')}
print('versions', V, file=sys.stderr)
CASES = {c['id']: c['situation'] for c in json.load(open('work/evals/cases_R5.json'))}
P = "indépendant . cotisations et contributions . "
ABT, SOC = P + "assiette CSG-CRDS . abattement", P + "assiette sociale"
PRE, POST = 'G4pre_R5', 'G4post_R5'
SCOPE = (" SCOPE CAVEAT: none of the 12 bounded articles mentions Mayotte; whether L136-3 III / D136-5 govern Mayotte"
         " (CSG territorial scope L136-1, the Mayotte social-security texts, the Mayotte PSS the library uses) is outside the bounded set.")
specs = []
def add(tag, article, quote, rule, snap, check, case, expect, claim, status=None, tol=1.0):
    specs.append(dict(tag=tag, article=article, quote=quote, rule=rule, snap=snap, check=check, case=case, expect=expect, claim=claim, status=status, tol=tol))
# ---- BEFORE (G4pre_R5): floor and ceiling applied everywhere (Mayotte on the library's Mayotte PSS 33 852 €/an in 2025)
add("R5-pre-L136-3-III-floor-MAY", 'L136-3', Q_L136_FLOOR, ABT, PRE, ABT, "MAY_1000_2025", 596,
    f"L136-3 III v.{V['L136-3']}: the 26 % abattement cannot be below a floor fixed by decree. BEFORE the commit, Mayotte, revenu brut 1 000 €/an, 01/07/2025: abattement = 596 = 1,76 % x 33 852 (the library's Mayotte PSS, Urssaf source outside the set; 595,8 rounded) instead of 26 % x 1 000 = 260: a floor IS applied, but computed on a Mayotte PSS that D136-5/L241-3 do not know (national PSS 2025 in the library = 47 100 -> 829)." + SCOPE)
add("R5-pre-L136-3-III-ceiling-MAY", 'L136-3', Q_L136_CEIL, ABT, PRE, ABT, "MAY_300000_2025", 44008,
    f"L136-3 III v.{V['L136-3']}: the abattement cannot exceed a ceiling fixed by decree. BEFORE: Mayotte, revenu brut 300 000, 01/07/2025: abattement = 44 008 = 130 % x 33 852 (44 007,6 rounded) instead of 26 % x 300 000 = 78 000: a ceiling IS applied (on the Mayotte PSS; national PSS would give 61 230)." + SCOPE)
add("R5-pre-D136-5-I-MET", 'D136-5', Q_D136_I, ABT, PRE, ABT, "MET_1000_2025", 829,
    f"D136-5 I v.{V['D136-5']}: floor = 1,76 % of the annual PSS (L241-3). BEFORE, metropole, revenu brut 1 000, 01/07/2025: abattement 829 = 1,76 % x 47 100 (library PSS 2025; the arrete fixing the PSS is outside the set) = 828,96 rounded (aligned).")
add("R5-pre-D136-5-II-MET", 'D136-5', Q_D136_II, ABT, PRE, ABT, "MET_300000_2025", 61230,
    f"D136-5 II v.{V['D136-5']}: ceiling = 130 % of the annual PSS. BEFORE, metropole, revenu brut 300 000, 01/07/2025: abattement 61 230 = 130 % x 47 100 (aligned).")
add("R5-pre-L131-6-I-assiette-MAY", 'L131-6', Q_L131, SOC, PRE, SOC, "MAY_1000_2025", 404,
    f"L131-6 I v.{V['L131-6']}: cotisations are based on the L136-3 assiette. BEFORE, Mayotte, revenu brut 1 000, 01/07/2025: assiette sociale = assiette CSG-CRDS = 1 000 - 596 = 404 €/an. The library makes CSG-CRDS itself non applicable in Mayotte (source outside the set), so the abattement reaches Mayotte only through the cotisation base.")
# ---- AFTER (G4post_R5): floor and ceiling switched off for Mayotte only
add("R5-post-L136-3-III-floor-MAY", 'L136-3', Q_L136_FLOOR, ABT, POST, ABT, "MAY_1000_2025", 260,
    f"L136-3 III v.{V['L136-3']} (no territorial exception in the text). AFTER the commit, Mayotte, revenu brut 1 000, 01/07/2025: abattement = 26 % x 1 000 = 260 with NO floor (BEFORE 596; the literal D136-5 floor on the national PSS would be 829). Under a literal reading of L136-3 III this is below the floor; the text does not say whether it governs Mayotte." + SCOPE)
add("R5-post-L136-3-III-ceiling-MAY", 'L136-3', Q_L136_CEIL, ABT, POST, ABT, "MAY_300000_2025", 78000,
    f"L136-3 III v.{V['L136-3']}. AFTER, Mayotte, revenu brut 300 000, 01/07/2025: abattement = 26 % x 300 000 = 78 000 with NO ceiling (BEFORE 44 008; literal D136-5 ceiling on the national PSS 61 230)." + SCOPE)
add("R5-post-L136-3-III-floor-MAY-2026", 'L136-3', Q_L136_FLOOR, ABT, POST, ABT, "MAY_1000_2026", 260,
    f"L136-3 III v.{V['L136-3']}. AFTER, Mayotte, revenu brut 1 000, 01/07/2026: abattement 260 (BEFORE 638 = 1,76 % x 36 264, the library's 2026 Mayotte PSS).")
add("R5-post-D136-5-I-MET", 'D136-5', Q_D136_I, ABT, POST, ABT, "MET_1000_2025", 829,
    f"D136-5 I v.{V['D136-5']}. AFTER, metropole, revenu brut 1 000, 01/07/2025: abattement 829 = 1,76 % x 47 100: unchanged by the commit (aligned).")
add("R5-post-D136-5-II-MET", 'D136-5', Q_D136_II, ABT, POST, ABT, "MET_300000_2025", 61230,
    f"D136-5 II v.{V['D136-5']}. AFTER, metropole, revenu brut 300 000, 01/07/2025: abattement 61 230 = 130 % x 47 100: unchanged (aligned).")
add("R5-post-D136-5-I-GUA", 'D136-5', Q_D136_I, ABT, POST, ABT, "GUA_1000_2025", 829,
    f"D136-5 I v.{V['D136-5']}. AFTER, Guadeloupe (DROM other than Mayotte), revenu brut 1 000, 01/07/2025: abattement 829: the commit leaves the other DROM unchanged (aligned).")
add("R5-post-L131-6-I-assiette-MAY", 'L131-6', Q_L131, SOC, POST, SOC, "MAY_1000_2025", 740,
    f"L131-6 I v.{V['L131-6']}. AFTER, Mayotte, revenu brut 1 000, 01/07/2025: assiette sociale = 1 000 - 260 = 740 €/an (BEFORE 404): the cotisation base of a low-income Mayotte independant RISES because the floor no longer protects it (total cotisations 434 -> 455).")
add("R5-post-L131-6-I-assiette-MAY-300k", 'L131-6', Q_L131, SOC, POST, SOC, "MAY_300000_2025", 222000,
    f"L131-6 I v.{V['L131-6']}. AFTER, Mayotte, revenu brut 300 000, 01/07/2025: assiette sociale = 300 000 - 78 000 = 222 000 (BEFORE 255 992): the base of a high-income Mayotte independant FALLS because the ceiling no longer caps the abattement (total cotisations 23 518 -> 20 791).")
# ---- CONDITIONAL literal reading (recorded FAILED on purpose: documents the gap IF D136-5 governs Mayotte)
add("R5-post-D136-5-I-MAY-literal", 'D136-5', Q_D136_I, ABT, POST, ABT, "MAY_1000_2025", 829,
    f"CONDITIONAL literal reading of D136-5 I v.{V['D136-5']} for Mayotte (only if it governs Mayotte, which the bounded set does not settle): floor = 1,76 % x L241-3 PSS (library 47 100) = 829. Engine AFTER = 260 (BEFORE = 596, already computed on a Mayotte PSS). Recorded as a failing check to document the gap under that reading, not as an established violation." + SCOPE)
add("R5-post-D136-5-II-MAY-literal", 'D136-5', Q_D136_II, ABT, POST, ABT, "MAY_300000_2025", 61230,
    f"CONDITIONAL literal reading of D136-5 II v.{V['D136-5']} for Mayotte: ceiling = 130 % x 47 100 = 61 230. Engine AFTER = 78 000 (BEFORE = 44 008 on the Mayotte PSS). Recorded as a failing check for the same reason." + SCOPE)
# ---- ABSTENTION: scope not settled
add("R5-UNRESOLVED-scope-Mayotte", 'L136-3', Q_L136_FLOOR, ABT, POST, None, None, None,
    f"ABSTENTION. L136-3 III v.{V['L136-3']} and D136-5 v.{V['D136-5']} state the floor/ceiling with no territorial exception, and L131-6 I makes them the cotisation base; but none of the 12 bounded articles mentions Mayotte, the CSG territorial-scope article (L136-1), the Mayotte social-security texts and the legal source of the Mayotte PSS the library already uses (33 852 €/an in 2025) are outside the bounded set, and the commit adds no source (references unchanged: Urssaf reform page, L136-3, D136-5; its test file is not in the diff). The text available does not settle whether removing the floor/ceiling at Mayotte is required, permitted or forbidden.", status='UNKNOWN')
results = []
for s in specs:
    cmd = ['python3', 'src/sophon.py', '--store', STORE, 'link', 'add', '--rule', s['rule'], '--rules-snapshot', s['snap'],
           '--article', s['article'], '--law-snapshot', LAW, '--quote', s['quote'], '--claim', s['claim']]
    if s['check']:
        cmd += ['--check-rule', s['check'], '--check-situation', json.dumps(CASES[s['case']], ensure_ascii=False), '--expect', str(s['expect']), '--tolerance', str(s['tol'])]
    if s['status']:
        cmd += ['--status', s['status']]
    p = subprocess.run(cmd, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    res = json.loads(lines[-1]) if lines else {'error': (p.stdout[-300:] + p.stderr[-300:])}
    results.append({'tag': s['tag'], 'article': s['article'], 'snap': s['snap'], 'case': s['case'], 'expect': s['expect'], 'result': res})
    chk = res.get('check') if isinstance(res.get('check'), dict) else {}
    print(s['tag'], '|', res.get('status'), '|', res.get('link_id'), '| actual:', chk.get('actual', chk.get('value', '')), '|', res.get('error') or res.get('reason') or '')
with open('work/sophon/link_results_R5.jsonl', 'a') as f:
    for r in results: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(results), 'links attempted', file=sys.stderr)
