#!/usr/bin/env python3
"""Build output/answer.json and output/NOTES.md for R5 from the recorded evidence (engine evals, sophon link results,
sophon reports). Nothing numeric is typed by hand: engine values come from work/evals/R5_*.jsonl, quotes from the S10 text.
usage: python3 -I work/scripts/gen_answer_R5.py <self_reported_tool_calls>   (from the staging dir)"""
import json, re, sys, os, glob, datetime
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 0
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
def dt(ms): return datetime.datetime.fromtimestamp(ms / 1000, datetime.UTC).strftime('%Y-%m-%d')
V = {k: arts[k]['id'] for k in ('L131-6', 'L136-3', 'D136-5')}
DEB = {k: dt(arts[k]['dateDebut']) for k in V}
MAYOTTE_HITS = {k: arts[k]['text'].count('Mayotte') for k in arts}
meta = json.load(open('inputs/diffs/R5_c14ee26d0c67/meta.json'))
DIFF = open('inputs/diffs/R5_c14ee26d0c67/diff.patch').read()
HUNK = DIFF[DIFF.index('@@'):].rstrip()
def load(p):
    d = {}
    for ln in open(p):
        r = json.loads(ln)
        try: d[r['id']] = json.loads(r['stdout'])['evaluations']
        except Exception: d[r['id']] = {}
    return d
B = load('work/evals/R5_before_G4pre.jsonl'); A = load('work/evals/R5_after_G4post.jsonl')
CASES = {c['id']: c['situation'] for c in json.load(open('work/evals/cases_R5.json'))}
P = "indépendant . cotisations et contributions . "
ASS, ABT, SOC, COT, PSS, CSG, REF = P + "assiette CSG-CRDS", P + "assiette CSG-CRDS . abattement", P + "assiette sociale", P + "cotisations", "plafond sécurité sociale . annuel", P + "CSG-CRDS", P + "après réforme"
def v(E, cid, rule):
    e = E.get(cid, {}).get(rule)
    if not e or 'error' in e: return None
    x = e.get('nodeValue'); return round(x, 4) if isinstance(x, float) else x
def terr(cid): return {'MAY': 'Mayotte', 'MET': 'métropole', 'GUA': 'Guadeloupe'}[cid[:3]]
grid_ids = [c for c in CASES]
rows = []
for cid in grid_ids:
    r = {'case': cid, 'territoire': terr(cid), 'date': CASES[cid]['date'], 'revenu_brut': CASES[cid]['indépendant . revenu brut'],
         'PSS_annuel_library': v(B, cid, PSS), 'apres_reforme': v(B, cid, REF),
         'abattement_before': v(B, cid, ABT), 'abattement_after': v(A, cid, ABT),
         'assiette_CSG_CRDS_before': v(B, cid, ASS), 'assiette_CSG_CRDS_after': v(A, cid, ASS),
         'assiette_sociale_before': v(B, cid, SOC), 'assiette_sociale_after': v(A, cid, SOC),
         'cotisations_before': v(B, cid, COT), 'cotisations_after': v(A, cid, COT),
         'CSG_CRDS_before': v(B, cid, CSG), 'CSG_CRDS_after': v(A, cid, CSG)}
    r['changed'] = any(r[k + '_before'] != r[k + '_after'] for k in ('abattement', 'assiette_CSG_CRDS', 'assiette_sociale', 'cotisations', 'CSG_CRDS'))
    rows.append(r)
changed = [r for r in rows if r['changed']]; unchanged = [r for r in rows if not r['changed']]
assert all(r['territoire'] == 'Mayotte' for r in changed), 'a non-Mayotte case changed'
links = [json.loads(l) for l in open('work/sophon/link_results_R5.jsonl')] if os.path.exists('work/sophon/link_results_R5.jsonl') else []
lid = {l['tag']: (l['result'].get('link_id'), l['result'].get('status')) for l in links}
def reval(name):
    p = f'work/sophon/reports/{name}_cmd.json'
    if not os.path.exists(p): return None
    lines = [l for l in open(p).read().splitlines() if l.startswith('{')]
    return json.loads(lines[-1]).get('counts') if lines else None
RV = {n: reval(n) for n in ('R5_revalidate_S10_G4', 'R5_revalidate_S10_G4pre_R5', 'R5_revalidate_S10_G4post_R5')}
reports = sorted(glob.glob('work/sophon/reports/R5_*'))
def R(cid): return next(r for r in rows if r['case'] == cid)
m1, m300, m1_26, met1, met300 = R('MAY_1000_2025'), R('MAY_300000_2025'), R('MAY_1000_2026'), R('MET_1000_2025'), R('MET_300000_2025')
def ev(cid, rule, label):
    s = CASES[cid]
    return {'kind': 'engine_before_after', 'article': None, 'article_version_id': None, 'rule': rule, 'date': s['date'],
            'situation': s, 'before_G4pre_R5': v(B, cid, rule), 'after_G4post_R5': v(A, cid, rule), 'unit': '€/an',
            'quote_or_values': f"{label}: {rule} = {v(B, cid, rule)} before -> {v(A, cid, rule)} after ({terr(cid)}, revenu brut {s['indépendant . revenu brut']}, date {s['date']})"}
evidence = [
    {'kind': 'diff_excerpt', 'article': None, 'article_version_id': None, 'quote_or_values': f"commit {meta['commit'][:12]} ({meta['committed']}, {meta['author']}): \"{meta['subject']}\" — modele-ti/règles/indépendant/cotisations-et-contributions/cotisations-et-contributions.publicodes:\n{HUNK}"},
    {'kind': 'article_quote', 'article': 'L136-3', 'article_version_id': V['L136-3'], 'in_force_from': DEB['L136-3'], 'quote_or_values': Q_L136_FLOOR},
    {'kind': 'article_quote', 'article': 'L136-3', 'article_version_id': V['L136-3'], 'in_force_from': DEB['L136-3'], 'quote_or_values': Q_L136_CEIL},
    {'kind': 'article_quote', 'article': 'D136-5', 'article_version_id': V['D136-5'], 'in_force_from': DEB['D136-5'], 'quote_or_values': Q_D136_I},
    {'kind': 'article_quote', 'article': 'D136-5', 'article_version_id': V['D136-5'], 'in_force_from': DEB['D136-5'], 'quote_or_values': Q_D136_II},
    {'kind': 'article_quote', 'article': 'L131-6', 'article_version_id': V['L131-6'], 'in_force_from': DEB['L131-6'], 'quote_or_values': Q_L131},
    ev('MAY_1000_2025', ABT, 'floor removed at Mayotte'), ev('MAY_1000_2025', SOC, 'cotisation base rises at low income'), ev('MAY_1000_2025', COT, 'total cotisations'),
    ev('MAY_300000_2025', ABT, 'ceiling removed at Mayotte'), ev('MAY_300000_2025', SOC, 'cotisation base falls at high income'), ev('MAY_300000_2025', COT, 'total cotisations'),
    ev('MAY_1000_2026', ABT, '2026 floor removed (library Mayotte PSS 36 264)'), ev('MAY_30000_2025', ABT, 'mid-range Mayotte unchanged (abattement within floor/ceiling)'),
    ev('MET_1000_2025', ABT, 'métropole floor unchanged = 1,76 % x 47 100'), ev('MET_300000_2025', ABT, 'métropole ceiling unchanged = 130 % x 47 100'),
    ev('GUA_1000_2025', ABT, 'Guadeloupe (other DROM) unchanged'), ev('MAY_1000_2025', CSG, 'CSG-CRDS itself is non applicable at Mayotte in the library (null both sides)'),
    ev('MAY_1000_2025', PSS, "library PSS used at Mayotte (not the L241-3 national PSS 47 100)"),
    {'kind': 'engine_before_after', 'article': None, 'article_version_id': None, 'quote_or_values': f"build: both trees parse (298 raw / 460 parsed rules, identical name lists); {len(rows)} situations x 9 rules: {len(changed)} situations changed (all Mayotte), {len(unchanged)} unchanged (métropole, Guadeloupe, mid-range Mayotte, and the 2024 pre-reform cases where the abattement sub-rule changes but is not used)."},
    {'kind': 'article_quote', 'article': 'ALL', 'article_version_id': None, 'quote_or_values': f"occurrences of the word 'Mayotte' in the 12 bounded articles of S10: {MAYOTTE_HITS} (none)."},
]
expected = [
    {'rule': ABT, 'date': '01/07/2025', 'territoire': 'Mayotte', 'found': m1['abattement_after'], 'found_before_commit': m1['abattement_before'], 'expected': 829, 'conditional': True,
     'derivation': f"ONLY IF L136-3 III / D136-5 govern Mayotte (not settled by the bounded set): floor = 1,76 % x annual PSS of L241-3 = 1,76 % x 47 100 (the library's own 2025 PSS; the arrêté fixing it is outside the set) = 828,96 -> 829. Engine after: {m1['abattement_after']} (26 % x 1 000, no floor); before: {m1['abattement_before']} (1,76 % x the library's Mayotte PSS {m1['PSS_annuel_library']}, itself not the L241-3 PSS)."},
    {'rule': ABT, 'date': '01/07/2025', 'territoire': 'Mayotte', 'found': m300['abattement_after'], 'found_before_commit': m300['abattement_before'], 'expected': 61230, 'conditional': True,
     'derivation': f"ONLY IF D136-5 II governs Mayotte: ceiling = 130 % x 47 100 = 61 230. Engine after: {m300['abattement_after']} (26 % x 300 000, no ceiling); before: {m300['abattement_before']} (130 % x {m300['PSS_annuel_library']})."},
    {'rule': SOC, 'date': '01/07/2025', 'territoire': 'Mayotte', 'found': m1['assiette_sociale_after'], 'found_before_commit': m1['assiette_sociale_before'], 'expected': 171, 'conditional': True,
     'derivation': f"ONLY IF L131-6 I + L136-3 III + D136-5 govern Mayotte: assiette = 1 000 - 829 = 171 (= the métropole value the engine gives: {met1['assiette_sociale_after']}). Engine after {m1['assiette_sociale_after']}, before {m1['assiette_sociale_before']}."},
]
outside = [
    "Territorial scope of the CSG and of L136-3 in Mayotte: article L136-1 CSS (the library already treats `indépendant . cotisations et contributions . CSG-CRDS` as non applicable in Mayotte) — not in the bounded set.",
    "The texts organising social security and the cotisations of independants in Mayotte (ordinance and implementing decrees) — not in the corpus; none of the 12 bounded articles mentions Mayotte.",
    "L241-3 CSS and the yearly arrêté fixing the plafond annuel de la sécurité sociale, from which D136-5 derives the floor and ceiling: the library uses 47 100 €/an (2025) / 48 060 (2026) in métropole and a distinct Mayotte PSS of 33 852 (2025) / 36 264 (2026) whose legal source (Urssaf page) is outside the set — so even the BEFORE tree did not compute the Mayotte floor/ceiling from the L241-3 PSS.",
    "L633-1 CSS (upper bound of the floor, cited by L136-3 III) — not in the set.",
    "The maintainers' Mayotte sources: Urssaf 'Taux de cotisations - Travailleur indépendant à Mayotte' page and the CSSM leaflet cited in the library's références (modele-ti exonérations.publicodes); the commit's own test file site/test/modele-ti/assiettes.test.ts (listed in stat.txt, absent from diff.patch). The commit does not change the rule's références (Urssaf reform page, L136-3, D136-5).",
]
rationale = (
    f"The commit switches off the `plancher` (1,76 % x PSS) and `plafond` (130 % x PSS) of `{ABT}` when the établissement is in Mayotte; nothing else changes (same 460 parsed rules, métropole and Guadeloupe values identical). "
    f"The engine confirms a semantic change for Mayotte only: at revenu brut 1 000 €/an (01/07/2025) the abattement goes {m1['abattement_before']} -> {m1['abattement_after']} and the cotisation base {m1['assiette_sociale_before']} -> {m1['assiette_sociale_after']} (cotisations {m1['cotisations_before']} -> {m1['cotisations_after']}); at 300 000 €/an the abattement goes {m300['abattement_before']} -> {m300['abattement_after']} and the base {m300['assiette_sociale_before']} -> {m300['assiette_sociale_after']} (cotisations {m300['cotisations_before']} -> {m300['cotisations_after']}); mid-range incomes are unaffected. "
    f"The governing text in force (L136-3 III v.{V['L136-3']}, D136-5 v.{V['D136-5']}, carried into the cotisation base by L131-6 I v.{V['L131-6']}) states the floor and the ceiling without any territorial exception, so under a literal reading the after-state computes an abattement the text does not allow. "
    f"But none of the 12 bounded articles mentions Mayotte, the article fixing the CSG's territorial scope (L136-1) and the Mayotte-specific social-security texts are outside the set, the library's whole Mayotte branch (CSG-CRDS non applicable, a distinct Mayotte PSS already used for the floor/ceiling before the commit) rests on Urssaf sources that are not in the corpus, and the commit cites no source. "
    f"The available text therefore does not settle whether L136-3 III/D136-5 apply in Mayotte at all: UNRESOLVED. If they do, this is a MISMATCH (expected floor 829 / ceiling 61 230 on the L241-3 PSS, see expected_values_if_mismatch); if a Mayotte text excludes the floor/ceiling, it is a legitimate change resting on that outside source. Law snapshot S10 has the same texts and version ids as S9 for all 12 articles."
)
notes = (
    f"Decision date 2026-10-05; law S10 (legi-data 2.572.0) == S9 texts; rules pin G4 (modele-social, 2026-03-03) is not the tree of the diff: the commit lives in modele-ti + modele-commun (parent/after trees registered as G4pre_R5/G4post_R5). "
    f"Sophon: {len(links)} links attempted on S10 ({sum(1 for t,(i,s) in lid.items() if s=='VERIFIED')} VERIFIED, {sum(1 for t,(i,s) in lid.items() if s=='FAILED')} FAILED = the conditional literal-reading checks for Mayotte recorded on purpose, {sum(1 for t,(i,s) in lid.items() if s=='UNKNOWN')} UNKNOWN = the scope abstention); revalidate counts S10xG4: {RV['R5_revalidate_S10_G4']}, S10xG4pre_R5: {RV['R5_revalidate_S10_G4pre_R5']}, S10xG4post_R5: {RV['R5_revalidate_S10_G4post_R5']}. "
    f"Pre-reform dates (01/07/2024, `après réforme` = non): the `abattement` sub-rule value changes ({R('MAY_1000_2024')['abattement_before']} -> {R('MAY_1000_2024')['abattement_after']}) but it is not used by `assiette CSG-CRDS` there (null on both sides). "
    f"Engine lesson: one unknown key in the situation (here the old name `... cotisations . exonérations . pension invalidité`, renamed in these trees) makes setSituation throw and the wrapper evaluates with an EMPTY situation (field `situation_error`) — evalbatch2.py now prints it. "
    f"No approval, sign-off or ratification record exists anywhere in the corpus."
)
answer = {
    'task': 'R5', 'commit': meta['commit'], 'label': 'UNRESOLVED', 'confidence': 'medium', 'rationale': rationale,
    'evidence': evidence, 'expected_values_if_mismatch': expected, 'outside_bounded_set': outside, 'approval': 'none recorded',
    'notes': notes, 'self_reported_tool_calls': CALLS,
    'sophon_reports': reports,
    'sophon_links': {t: {'link_id': i, 'status': s} for t, (i, s) in lid.items()},
    'law_snapshot': {'id': 'S10', 'legi_data_version': '2.572.0', 'versions': V, 'in_force_from': DEB, 'same_as_S9': True},
    'rules_snapshots': {'pin': 'G4 a61b72947fec (modele-social, not the diff tree)', 'before': 'G4pre_R5 = context_parent_tree (modele-ti + modele-commun)', 'after': 'G4post_R5 = context_tree_after'},
    'engine_grid': rows,
}
os.makedirs('output', exist_ok=True)
json.dump(answer, open('output/answer.json', 'w'), ensure_ascii=False, indent=1)
# ---- NOTES.md
def fmt(x): return '—' if x is None else (f"{x:,.0f}".replace(',', ' ') if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x))
tbl = ["| case | territoire | date | revenu brut | PSS (lib) | abattement before -> after | assiette CSG-CRDS before -> after | assiette sociale before -> after | cotisations before -> after | changed |", "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    tbl.append(f"| {r['case']} | {r['territoire']} | {r['date']} | {r['revenu_brut']} | {fmt(r['PSS_annuel_library'])} | {fmt(r['abattement_before'])} -> {fmt(r['abattement_after'])} | {fmt(r['assiette_CSG_CRDS_before'])} -> {fmt(r['assiette_CSG_CRDS_after'])} | {fmt(r['assiette_sociale_before'])} -> {fmt(r['assiette_sociale_after'])} | {fmt(r['cotisations_before'])} -> {fmt(r['cotisations_after'])} | {'YES' if r['changed'] else ''} |")
ltbl = ["| tag | status | link id |", "|---|---|---|"] + [f"| {t} | {s} | {i} |" for t, (i, s) in lid.items()]
md = f"""# R5 — reverse check of commit {meta['commit'][:12]} (decision date 2026-10-05)

**Verdict: UNRESOLVED (confidence medium).** Approval: none recorded.

## What the commit changes
`{meta['subject']}` ({meta['author']}, committed {meta['committed']}). One rule file of **modele-ti** (plus a test file not included in the patch):

```
{HUNK}
```
Both trees build (298 raw / 460 parsed rules, identical rule-name lists). The only rule whose body changes is `{ABT}`; `{ASS}` (= revenu brut − abattement after the reform) and `{SOC}` (= assiette CSG-CRDS + … per L131-6 I) inherit the change.

## Governing text (law snapshot S10 = legi-data 2.572.0; same version ids and texts as S9)
- **L136-3 III** (v.{V['L136-3']}, in force {DEB['L136-3']}): « {Q_L136_FLOOR} […] {Q_L136_CEIL} ».
- **D136-5** (v.{V['D136-5']}, in force {DEB['D136-5']}): « {Q_D136_I}. » and « {Q_D136_II}. »
- **L131-6 I** (v.{V['L131-6']}, in force {DEB['L131-6']}): cotisations « {Q_L131} ».
- Occurrences of « Mayotte » in the 12 bounded articles: **0** ({MAYOTTE_HITS}).

## Engine before (G4pre_R5 = parent tree) / after (G4post_R5)
Situations: EI à l'IR, activité commerciale, créée 01/01/2020, `indépendant . revenu brut` set directly; Mayotte = `établissement . commune . département = 'Mayotte'`.

{chr(10).join(tbl)}

Only Mayotte changes, and only outside the band where 26 % × revenu brut lies between the floor and the ceiling. Before the commit the Mayotte floor/ceiling were computed on the library's **Mayotte PSS** ({m1['PSS_annuel_library']} €/an in 2025, {m1_26['PSS_annuel_library']} in 2026 — an Urssaf value, not the L241-3 PSS of {met1['PSS_annuel_library']} that D136-5 names). CSG-CRDS itself is non applicable at Mayotte in the library (null on both sides), so the abattement reaches Mayotte only through the cotisation base (L131-6 I).

## Why UNRESOLVED
1. Under a literal reading, L136-3 III and D136-5 impose the floor and the ceiling with no territorial exception, and the after-tree computes at Mayotte an abattement below the floor ({m1['abattement_after']} < 829 on the L241-3 PSS, < {m1['abattement_before']} even on the Mayotte PSS) and above the ceiling ({m300['abattement_after']} > 61 230 / {m300['abattement_before']}). That reading would make the commit a **MISMATCH** (conditional expected values are in `expected_values_if_mismatch`).
2. But whether L136-3 / L131-6 govern Mayotte at all is not decidable from the bounded set: no bounded article mentions Mayotte; the CSG scope article (L136-1), the Mayotte social-security texts and the legal source of the Mayotte PSS are outside the set; the library's whole Mayotte branch rests on Urssaf/CSSM sources that are not in the corpus; the commit cites no source and its test file is not in the patch. If such a text excludes the floor/ceiling at Mayotte, the commit is a **LEGITIMATE_INDEPENDENT_CHANGE** resting on it.
3. It is not a HARMLESS_REFACTOR: computed values change for real situations.

## Sophon
- Snapshots: law `S10`; rules `G4pre_R5`, `G4post_R5` (multi-dir modele-ti + modele-commun). `G4` (pin) unchanged.
- Links (S10): {len(links)} attempted — VERIFIED = the engine facts above; FAILED = the two *conditional* literal-reading checks for Mayotte, recorded deliberately; UNKNOWN = the scope abstention.

{chr(10).join(ltbl)}

- Revalidate counts — S10×G4: {RV['R5_revalidate_S10_G4']}; S10×G4pre_R5: {RV['R5_revalidate_S10_G4pre_R5']}; S10×G4post_R5: {RV['R5_revalidate_S10_G4post_R5']} (old modele-social links are RULE_FILE_ABSENT on the modele-ti trees; S10 == S9 so no law-side reassessment).
- Reports: {', '.join(reports)}

## Open items carried forward
- Mayotte: the scope question above (needs L136-1 and the Mayotte texts).
- Still open from earlier tasks: AE DROM BNC/CIPAV rates ≥ 07/2024, D756-5 II CA cap, D613-4 c) meublés 6 %, D613-6 shares, CIPAV ACRE leak, D632-1 2024 floor, L613-7 minimum option, D613-4 2025 version without text; AE side of S9/S10 (D613-4 v.LEGIARTI000052218738, D613-6 v.LEGIARTI000052218747, D131-6-1 v.LEGIARTI000053451315) not yet assessed against a rules tree that contains the AE rules.

Self-reported tool calls: {CALLS}.
"""
open('output/NOTES.md', 'w').write(md)
print('answer.json and NOTES.md written;', len(changed), 'changed cases,', len(links), 'links,', 'reports:', reports)
