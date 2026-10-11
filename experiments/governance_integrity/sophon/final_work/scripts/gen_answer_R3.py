#!/usr/bin/env python3
"""Build output/answer.json + output/NOTES.md for R3 and append the R3 section to work/README.md.
usage: python3 -I work/scripts/gen_answer_R3.py <self_reported_tool_calls>"""
import json, glob, sys, os
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 0
COMMIT = json.load(open('inputs/diffs/R3_9bb43d710094/meta.json'))
raw = json.load(open('inputs/law/S5_legi-data-2.385.0/articles.json'))['articles']; arts = {k: v[0] for k, v in raw.items()}
S0 = json.load(open('work/sophon/store/law/S0.json'))['articles']
V = {k: arts[k]['id'] for k in arts}; V0 = S0['D613-4']['id']
T = arts['D756-5']['text']
def sub(text, start, end):
    i = text.find(start); assert i >= 0, start; j = text.find(end, i); assert j >= 0, end; return text[i:j + len(end)]
Q = {
 'frac': sub(T, "le taux mentionné au premier alinéa", "à compter de la quatrième année civile d'activité."),
 'round': sub(T, "après arrondi", "D. 131-6-1"),
 'cap': sub(T, "II. – L'exonération", "code général des impôts."),
 'bnc23': sub(arts['D613-4']['text'], "e) Travailleurs indépendants relevant", "23,1 %"),
 'cipav23': sub(arts['D613-4']['text'], "b) Travailleurs indépendants affiliés", "23,2 %"),
 'bic': sub(arts['D613-4']['text'], "d) Travailleurs indépendants appartenant", "21,2 %"),
 'vente': sub(arts['D613-4']['text'], "a) Travailleurs indépendants appartenant", "12,3 %"),
 'bnc21': sub(S0['D613-4']['text'], "e) Travailleurs indépendants relevant", "21,1 %"),
 'cipav21': sub(S0['D613-4']['text'], "b) Travailleurs indépendants affiliés", "21,2 %"),
 'l6137': sub(arts['L613-7']['text'], "Un taux global différent", "sécurité sociale."),
}
# ---- engine artefacts
def load(p):
    d = {}
    for ln in open(p):
        r = json.loads(ln); d[r['id']] = json.loads(r['stdout'])['evaluations']
    return d
EB = load('work/evals/R3_drom_before_G2.jsonl'); EA = load('work/evals/R3_drom_after_G2post.jsonl'); EP = load('work/evals/R3_drom_proposal.jsonl')
C = 'dirigeant . auto-entrepreneur . cotisations et contributions . cotisations'
SUB = {'BNC': 'service BNC', 'CIPAV': 'cotisations CIPAV', 'BIC': 'service BIC', 'VENTE': 'vente restauration hébergement'}
def v(E, cid, rule):
    e = E[cid].get(rule, {})
    if 'error' in e: return 'ERR(introuvable)'
    x = e.get('nodeValue'); u = e.get('unit') or ''
    if isinstance(x, float): x = round(x, 3)
    return f"{x}{' ' + u if u else ''}"
cases = {c['id']: c['situation'] for c in json.load(open('work/evals/cases_R3_drom.json'))}
rows = []
for a in ('BNC', 'CIPAV', 'BIC', 'VENTE'):
    for p in ('P1', 'P2', 'P3'):
        for d in ('05-2024', '10-2024'):
            cid = f"DROM_{a}_{p}_{d}"; r = f"{C} . {SUB[a]}"
            rows.append((cid, a, p, cases[cid]['date'], v(EB, cid, r), v(EA, cid, r), v(EP, cid, r), v(EA, cid, f"{C} . {SUB[a]} . taux"), v(EB, cid, f"{C} . {SUB[a]} . taux")))
metro = [(cid, v(EB, cid, f"{C} . {SUB[a]}"), v(EA, cid, f"{C} . {SUB[a]}")) for a in SUB for cid in [f"METRO_{a}_P1_10-2024"]]
# ---- sophon
links = []
for ln in open('work/sophon/link_results_R3.jsonl'):
    rec = json.loads(ln)
    try: j = json.loads(rec['stdout'].splitlines()[-1])
    except Exception: j = {}
    cr = j.get('check_result') or {}
    links.append(dict(tag=rec['tag'], id=j.get('link_id'), status=j.get('status'), article=rec['article'], article_id=rec['article_id'], law=rec['law_snapshot'], rule=rec['rule'], snap=rec['snap'], check=rec['check_rule'], case=rec['case'], expected=rec['expect'], observed=cr.get('observed')))
reports = sorted(glob.glob('work/sophon/reports/R3_*'))
rv = {n: json.load(open(f'work/sophon/reports/R3_revalidate_S5_{n}_cmd.json'))['counts'] for n in ('G2', 'G2post_R3')}
P_ = f"D756-5 v.{V['D756-5']} (in force since 2017-05-12, Décret n°2017-972 du 9 mai 2017)"
D4 = f"D613-4 v.{V['D613-4']} (in force 2024-07-01..2025-05-01)"; D4o = f"D613-4 v.{V0} (in force 2022-12-10..2024-06-01; text available in store snapshot S0, not in S5)"
def ev(kind, art, vid, val): return {'kind': kind, 'article': art, 'article_version_id': vid, 'quote_or_values': val}
situ_bnc = json.dumps(cases['DROM_BNC_P1_10-2024'], ensure_ascii=False)
evidence = [
 ev('diff_excerpt', 'D756-5', V['D756-5'], "exonérations.publicodes: the four DROM rate rules (`service BIC` -> renamed `taux service BIC`, `taux service BNC`, `taux vente restauration hébergement`, `taux CIPAV`, each with `remplace: cotisations et contributions . cotisations . <x> . taux`) move from the BODY of the private rule `DROM . seconde période` (indent 6, before) to `DROM . avec` (indent 4, after); the misspelt duplicate key `references:` is merged into `références:`; dirigeant.publicodes: blank lines only. Engine `build`: parsed_rule_count 1258 (G2, before) -> 1262 (after); `list --prefix 'dirigeant . auto-entrepreneur . DROM'`: 1 name before (the 4 rate rules are not parsed at all), 5 after."),
 ev('article_quote', 'D756-5', V['D756-5'], Q['frac']),
 ev('article_quote', 'D756-5', V['D756-5'], Q['round']),
 ev('article_quote', 'D613-4', V['D613-4'], Q['bnc23'] + "  [in force 2024-07-01..2025-05-01]"),
 ev('article_quote', 'D613-4', V['D613-4'], Q['cipav23']),
 ev('article_quote', 'D613-4', V['D613-4'], Q['bic']),
 ev('article_quote', 'D613-4', V['D613-4'], Q['vente']),
 ev('article_quote', 'D613-4', V0, Q['bnc21'] + "  [superseded version, in force 2022-12-10..2024-06-01; text from store snapshot S0 (legi-data 2.360.0); S5 carries only the id/dates of this version]"),
 ev('article_quote', 'D613-4', V0, Q['cipav21'] + "  [same superseded version]"),
 ev('article_quote', 'L613-7', V['L613-7'], Q['l6137']),
 ev('article_quote', 'D756-5', V['D756-5'], Q['cap'] + "  [II: CA cap of the reduction -- not implemented before or after; pre-existing gap]"),
]
for cid, a, p, d, b, af, pr, ta, tb in rows:
    if d == '01/10/2024' or a in ('BNC', 'CIPAV'):
        tq = cases[cid]["entreprise . durée d'activité . trimestres civils"]; aq = cases[cid]["entreprise . durée d'activité . années civiles"]
        evidence.append(ev('engine_before_after', 'D756-5', V['D756-5'], f"rule `{C} . {SUB[a]}` ; case {cid} (AE DROM, CA 1 000 €/mois, {p}: trimestres civils={tq}, années civiles={aq}) ; date {d} ; BEFORE (G2) = {b} (full rate {tb}) ; AFTER (G2+commit) = {af} (rate {ta}) ; disposable proposal = {pr}"))
evidence.append(ev('engine_before_after', 'D613-4', V['D613-4'], "metropolitan controls (outre-mer: non), 01/10/2024, identical before/after: " + "; ".join(f"{cid}: {b} -> {a}" for cid, b, a in metro) + " -- the library already applies D613-4 v.LEGIARTI000049624068 (BNC 23,1 / CIPAV 23,2 since 07/2024) in metropole; the new DROM constants override it."))
evidence.append(ev('engine_before_after', 'D756-5', V['D756-5'], "situation used for the BNC checks (others differ only by nature/réglementée/service ou vente and the durée overrides): " + situ_bnc))
exp = []
def E(rule, found, expected, deriv, date='01/10/2024'): exp.append({'rule': rule, 'date': date, 'found': found, 'expected': expected, 'derivation': deriv})
DR = 'dirigeant . auto-entrepreneur . DROM . '
E(DR + 'taux service BNC', 3.6, 3.9, f"{P_} a) 1/6 x {D4} e) BNC 23,1 % = 3,85 -> 'arrondi au dixième de pour cent supérieur' = 3,9 %. Engine after: `{C} . service BNC` = 36 €/mois on 1 000 €/mois (expected 39). The 3,6 % is 1/6 x 21,1 % ({D4o}), correct only for dates before 2024-07-01 (engine 05/2024: 36 = aligned).")
E(DR + 'taux service BNC', 10.6, 11.6, f"{P_} b) 1/2 x 23,1 = 11,55 -> 11,6 %. Engine after: 106 €/mois (expected 116).")
E(DR + 'taux service BNC', 14.1, 15.4, f"{P_} c) 2/3 x 23,1 = 15,4 %. Engine after: 141 €/mois (expected 154).")
E(DR + 'taux CIPAV', 7.1, 7.8, f"{P_} a) '1/3 dans les autres cas' x {D4} b) CIPAV 23,2 % = 7,733 -> 7,8 %. Engine after: `{C} . cotisations CIPAV` = 852 €/an on 12 000 €/an (expected 936). 7,1 % = 1/3 x 21,2 % (superseded version).")
E(DR + 'taux CIPAV', 10.6, 11.6, f"{P_} b) 1/2 x 23,2 = 11,6 %. Engine after: 1 272 €/an (expected 1 392).")
E(DR + 'taux CIPAV', 14.2, 15.5, f"{P_} c) 2/3 x 23,2 = 15,467 -> 15,5 %. Engine after: 1 704 €/an (expected 1 860).")
E(C + ' . service BNC', 231, 39, f"BEFORE the commit (G2) the DROM reduction was not applied at all: 231 €/mois = full 23,1 %; D756-5 a) requires 1/6 (3,9 % = 39). The commit fixes the omission but with the superseded base rate (36).")
rationale = (f"Not a refactor: in G2 the four DROM rate rules were written inside the body of the private rule `DROM . seconde période` and publicodes silently dropped them (parsed rules 1258 -> 1262 after the move to `DROM . avec`), so before the commit an auto-entrepreneur in the DROM paid the full metropolitan rates (engine: BNC 231 €/mois, BIC 212, vente 123, CIPAV 1 452 €/an at 01/10/2024) and after it pays the reduced DROM rates (36 / 36 / 21 / 852). "
 f"The reduction itself is what {P_} requires (1/6 or 1/3, 1/2, 2/3 of the base rates, rounded up to 0,1 %), and for BIC services and vente the new constants equal D756-5 x {D4} (3,6/10,6/14,2 and 2,1/6,2/8,2: 9 VERIFIED sophon checks). "
 f"But for BNC and CIPAV the commit hard-codes 3,6/10,6/14,1 and 7,1/10,6/14,2, i.e. fractions of the superseded rates 21,1/21,2 % ({D4o}); the version in force at the decision date gives 23,1/23,2 % hence 3,9/11,6/15,4 and 7,8/11,6/15,5. The library already applies 23,1/23,2 in metropole since 07/2024, and the new DROM rules override that with date-less constants, so after the change the engine computes values the text in force does not support (8 FAILED checks, L0133-L0136, L0139-L0142). "
 "Caveat on the exact expected numbers: D756-5 still cites the pre-2020 numbering (D. 131-6-1, L. 133-6-8) and distinguishes 1/6 vs 1/3 by L. 611-1 2°, which are outside the bounded set; under any reading of the bounded texts, 3,6 % for BNC at 01/10/2024 cannot be derived from a rate table in force.")
notes = (f"Decision date 2024-10-19; law S5 (legi-data 2.385.0) is textually identical to S4/S3 for all 12 articles (dump diff: header only); rules pin G2 = 3a4091ae1caf (2024-10-10), the commit (authored 2024-10-03, committed 2024-10-11) is applied forward on a copy (work/proposals/R3/after; `patch -p1 -l`). "
 f"Period overrides used because `durée d'activité` follows the wall clock: P1 = 4 trimestres civils / 1 année civile (première période: trimestres civils <= 8), P2 = 10 / 3 (seconde période: années civiles <= 3), P3 = 20 / 5. "
 f"The maintainers' own fixture confirms the before-state: existing_tests snapshot 'DROM 1..4' at the G2 pin shows `service BNC . taux: 23`, `service BIC . taux: 21`, `vente . taux: 12` (full rates) and the commit rewrites 116 lines of that snapshot. "
 f"Disposable proposal (work/proposals/R3/proposal, script work/scripts/apply_proposal_R3.py, diff CHANGES_proposal.diff): add `date >= 07/2024` variations to `taux service BNC` (3,9/11,6/15,4) and `taux CIPAV` (7,8/11,6/15,5); build OK (1262 rules); engine at 01/10/2024: BNC 39/116/154 €/mois, CIPAV 936/1392/1860 €/an; 05/2024 and metropole unchanged. "
 f"Pre-existing gaps unchanged by the commit: D756-5 II CA cap (L0144 INFERRED), D613-4 c) meublés de tourisme 6 %, D613-6 répartition shares (v.LEGIARTI000049625264), D613-4/D613-6 versions dated 2025-01-01 and 2026-01-01 announced by id only (abstain), CIPAV ACRE leak, D632-1 2024 floor, L613-7 minimum-contribution option. "
 f"Sophon: snapshots S5, G2, G2post_R3 registered; revalidate S5/G2 counts {json.dumps(rv['G2'])}; S5/G2post_R3 {json.dumps(rv['G2post_R3'])} (the 9 T0 DROM links on G0 pass again after the commit because they expected the 05/2024 values); 26 new links L0120-L0145 (4 FAILED before, 9+3 VERIFIED after on BIC/vente/pre-07-2024 bases, 8 FAILED after on BNC/CIPAV >= 07/2024, 2 INFERRED); verify-store: 145 links, no problems. Approval: none recorded anywhere in the corpus.")
ans = {
 'task': 'R3', 'commit': COMMIT['commit'], 'label': 'MISMATCH', 'confidence': 'high', 'rationale': rationale, 'evidence': evidence, 'expected_values_if_mismatch': exp,
 'outside_bounded_set': [
  "L611-1 CSS (which travailleurs indépendants are '2°' -> 1/6, and 'autres cas' -> 1/3 in D756-5 a); the library's and URSSAF's reading '1/3 = CIPAV / libéral réglementé' is adopted but cannot be verified here)",
  "Recodification decree (2020) renumbering D131-6-1 -> D613-4 and L133-6-8 -> L613-7: D756-5 still cites the old numbers; the current D131-6-1 (ACRE) contains no rate table",
  "L751-1 CSS (list of the collectivités = DROM; library key `établissement . commune . département . outre-mer`)",
  "CGI articles 50-0 and 102 ter (micro thresholds for the D756-5 II cap)",
  "URSSAF guide 'Taux auto-entrepreneur dans les Drom' (PDF) and autoentrepreneur.urssaf.fr page cited by the rule `dirigeant . auto-entrepreneur . DROM`",
  f"Text of D613-4 versions LEGIARTI000046714712 (2022-12-10..2024-06-01) and LEGIARTI000049623867 (2024-06-01..2024-07-01): not in S5 (ids/dates only); the 21,1 / 21,2 % quotes come from the store's S0/S1 snapshots",
  "D613-4 versions LEGIARTI000049624097 (2025-01-01) and LEGIARTI000049624125 (2026-01-01): announced by id only, no text -> no DROM values derivable for those dates (abstain)",
 ],
 'approval': 'none recorded', 'notes': notes,
 'sophon_reports': reports, 'sophon_links': [l['id'] for l in links],
 'self_reported_tool_calls': CALLS,
}
os.makedirs('output', exist_ok=True)
json.dump(ans, open('output/answer.json', 'w'), ensure_ascii=False, indent=1)
# ---- NOTES.md
L = []
L.append(f"# R3 — reverse check of commit {COMMIT['commit'][:12]} « {COMMIT['subject']} » (decision date 2024-10-19)\n")
L.append(f"**Verdict: MISMATCH (confidence high).** Law S5 = legi-data 2.385.0 (identical texts to S4/S3). Rules pin G2 = 3a4091ae1caf; commit authored {COMMIT['authored']}, committed {COMMIT['committed']} by {COMMIT['author']}; applied forward on a copy (`work/proposals/R3/after`).\n")
L.append("## 1. What the commit changes (engine evidence)\n")
L.append("- `exonérations.publicodes`: the four DROM rate rules were nested in the BODY of the private rule `dirigeant . auto-entrepreneur . DROM . seconde période` (6-space indent, since the re-indentation commit 05334b12 of 2024-09-02); publicodes silently ignored them. The commit moves them to `DROM . avec` (and renames `service BIC` -> `taux service BIC`), merges the misspelt `references:` key into `références:`. `dirigeant.publicodes`: blank lines only.")
L.append("- `build`: parsed_rule_count **1258 -> 1262**; `list --prefix 'dirigeant . auto-entrepreneur . DROM'`: 1 name -> 5 names.")
L.append("- Before/after engine values (AE in the DROM, CA 1 000 €/mois, ACRE non; P1 = trimestres civils 4 / années civiles 1, P2 = 10 / 3, P3 = 20 / 5 — overrides needed because `durée d'activité` follows the wall clock):\n")
L.append("| case | activity | period | date | BEFORE G2 (full rate) | AFTER commit (rate) | proposal | law in force -> expected |")
L.append("|---|---|---|---|---|---|---|---|")
EXP = {('BNC', 'P1', '01/10/2024'): '23,1/6=3,85->3,9 % = 39 €/mois', ('BNC', 'P2', '01/10/2024'): '11,55->11,6 % = 116', ('BNC', 'P3', '01/10/2024'): '15,4 % = 154',
       ('BNC', 'P1', '01/05/2024'): '21,1/6->3,6 % = 36 (S0 version)', ('BNC', 'P2', '01/05/2024'): '10,55->10,6 % = 106', ('BNC', 'P3', '01/05/2024'): '14,07->14,1 % = 141',
       ('CIPAV', 'P1', '01/10/2024'): '23,2/3=7,73->7,8 % = 936 €/an', ('CIPAV', 'P2', '01/10/2024'): '11,6 % = 1 392', ('CIPAV', 'P3', '01/10/2024'): '15,47->15,5 % = 1 860',
       ('CIPAV', 'P1', '01/05/2024'): '21,2/3->7,1 % = 852', ('CIPAV', 'P2', '01/05/2024'): '10,6 % = 1 272', ('CIPAV', 'P3', '01/05/2024'): '14,13->14,2 % = 1 704',
       ('BIC', 'P1', '01/10/2024'): '21,2/6=3,53->3,6 % = 36', ('BIC', 'P2', '01/10/2024'): '10,6 % = 106', ('BIC', 'P3', '01/10/2024'): '14,13->14,2 % = 142',
       ('VENTE', 'P1', '01/10/2024'): '12,3/6=2,05->2,1 % = 21', ('VENTE', 'P2', '01/10/2024'): '6,15->6,2 % = 62', ('VENTE', 'P3', '01/10/2024'): '8,2 % = 82'}
for cid, a, p, d, b, af, pr, ta, tb in rows:
    e = EXP.get((a, p, d), '(same as 10/2024: D613-4 unchanged for this category)')
    flag = ' **MISMATCH**' if (a in ('BNC', 'CIPAV') and d == '01/10/2024') else ''
    L.append(f"| {cid} | {a} | {p} | {d} | {b} ({tb}) | {af} ({ta}) | {pr} | {e}{flag} |")
L.append("\nMetropolitan controls (outre-mer: non, 01/10/2024) identical before/after: " + "; ".join(f"{cid}: {b} -> {a}" for cid, b, a in metro) + ". The library already applies D613-4 v.LEGIARTI000049624068 (23,1 / 23,2 %) in metropole since 07/2024 (history commits 8d04dbb6 / 1d2874c5 / d0a49c3f per `history_bounded_rules.patch`); the new DROM constants override it.\n")
L.append("Maintainers' own fixture: `existing_tests/.../auto-entrepreneur.test.ts.snap` 'DROM 1..4' at the G2 pin shows `service BNC . taux: 23`, `service BIC . taux: 21`, `vente . taux: 12` (no reduction); the commit rewrites 116 lines of that snapshot.\n")
L.append("## 2. Governing text (exact quotes, S5)\n")
L.append(f"- **D756-5** `{V['D756-5']}` (VIGUEUR since 2017-05-12): « {Q['round']} » ; « {Q['frac']} » ; II: « {Q['cap']} ».")
L.append(f"- **D613-4** `{V['D613-4']}` (2024-07-01..2025-05-01): « {Q['vente']} » ; « {Q['cipav23']} » ; « {Q['bic']} » ; « {Q['bnc23']} ».")
L.append(f"- **D613-4** `{V0}` (2022-12-10..2024-06-01, text from store snapshot S0; S5 lists the id only): « {Q['bnc21']} » ; « {Q['cipav21']} ».")
L.append(f"- **L613-7** `{V['L613-7']}` (since 2023-12-28): « {Q['l6137']} » (D756-5 is such a decree provision).")
L.append("- D756-5 cites « D. 131-6-1 » and « L. 133-6-8 » = pre-2020 numbering of D613-4 / L613-7 (renumbering decree outside the set); the current D131-6-1 (ACRE) has no rate table. The 1/6 vs 1/3 split refers to L. 611-1 2° (outside the set); the library's reading (1/3 = CIPAV) is adopted for the expected numbers but flagged.\n")
L.append("## 3. Derivation and mismatch table (date >= 01/07/2024)\n")
L.append("| category | base D613-4 in force | 1/6 (1/3 CIPAV) | 1/2 | 2/3 | commit values | status |")
L.append("|---|---|---|---|---|---|---|")
L.append("| vente (a) | 12,3 % | 2,05 -> **2,1** | 6,15 -> **6,2** | **8,2** | 2,1 / 6,2 / 8,2 | aligned (L0129-L0132 VERIFIED) |")
L.append("| BIC services (d) | 21,2 % | 3,53 -> **3,6** | **10,6** | 14,13 -> **14,2** | 3,6 / 10,6 / 14,2 | aligned (L0124-L0128 VERIFIED) |")
L.append("| BNC (e) | 23,1 % | 3,85 -> **3,9** | 11,55 -> **11,6** | **15,4** | 3,6 / 10,6 / 14,1 | **MISMATCH** (L0133-L0136 FAILED); values = 1/6.. of superseded 21,1 % (L0137-L0138 VERIFIED at 01/05/2024) |")
L.append("| CIPAV (b) | 23,2 % | 7,73 -> **7,8** | **11,6** | 15,47 -> **15,5** | 7,1 / 10,6 / 14,2 | **MISMATCH** (L0139-L0142 FAILED); values = 1/3.. of superseded 21,2 % (L0143 VERIFIED at 01/05/2024) |")
L.append("| meublés de tourisme (c) 6 % | 6 % | 1,0 | 3,0 | 4,0 | not implemented | pre-existing gap (abstain on category mapping) |\n")
L.append("Before the commit (G2) none of the fractions applied (L0120-L0123 FAILED: 211/231/212/123 instead of 36/39/36/21).\n")
L.append("## 4. Why MISMATCH and not another label\n")
L.append("- Not HARMLESS_REFACTOR: engine values change for every DROM AE (e.g. BNC 231 -> 36 €/mois).\n- Not LEGITIMATE_INDEPENDENT_CHANGE: restoring the D756-5 reduction is required, but the BNC/CIPAV constants contradict the rate table in force (D613-4 v.LEGIARTI000049624068) which the library itself already applies in metropole; the rule cites the URSSAF DROM guide (outside the set) but no bounded text supports 3,6 % for BNC after 2024-07-01.\n- Not UNRESOLVED: the only open points (old numbering in D756-5, L. 611-1 classification, L. 751-1) affect which fraction/base applies, not whether 3,6 % is derivable — under every reading of the bounded texts it is not. Confidence on the label: high; on the exact expected numbers: medium-high (depends on the 1/6-for-BNC reading).\n")
L.append("## 5. Disposable proposal (traceability only, never applied to inputs/)\n")
L.append("`work/proposals/R3/proposal` = after-tree + `work/scripts/apply_proposal_R3.py`: `taux service BNC` and `taux CIPAV` get `date >= 07/2024` variations (3,90/11,60/15,40 and 7,80/11,60/15,50, with a `note:` giving the derivation). Build OK (1262 rules). Engine 01/10/2024: BNC 39/116/154 €/mois, CIPAV 936/1 392/1 860 €/an; 01/05/2024 and metropole unchanged (`work/evals/R3_drom_proposal.jsonl`). Still missing (abstain): values for 2025-01-01 / 2026-01-01 (D613-4 versions without text), the D756-5 II CA cap, category c).\n")
L.append("## 6. Sophon store\n")
L.append(f"- Snapshots: law S5; rules G2 (1258 parsed) and G2post_R3 (1262 parsed).\n- `revalidate S5/G2`: {json.dumps(rv['G2'])} ; `revalidate S5/G2post_R3`: {json.dumps(rv['G2post_R3'])} (9 T0 DROM links pass again after the commit — they were recorded on the 01/05/2024 base). Rules to reassess include the DROM rules and all AE rate rules; `articles_without_any_link`: none.")
L.append("- New links (law S5 unless noted; checks run against the engine now):\n")
L.append("| id | tag | article (version) | rules snapshot | check rule / case | expected | observed | status |")
L.append("|---|---|---|---|---|---|---|---|")
for l in links:
    L.append(f"| {l['id']} | {l['tag']} | {l['article']} ({l['article_id']}{', ' + l['law'] if l['law'] != 'S5' else ''}) | {l['snap']} | {(l['check'] or '-').replace('dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . ', 'COT . ')} / {l['case'] or '-'} | {l['expected'] or '-'} | {l['observed'] if l['observed'] is not None else '-'} | {l['status']} |")
L.append("\n- Reports: " + ", ".join(f"`{r}`" for r in reports) + f". `verify-store`: {open('work/sophon/reports/R3_verify-store.json').read().strip()}.")
L.append("\n## 7. Approval\n\nnone recorded (no sign-off, ratification or approval record exists in the corpus; a merge, a test snapshot or a package is not an approval).\n")
L.append(f"## 8. Budget\n\nSelf-reported tool calls: {CALLS}.\n")
open('output/NOTES.md', 'w').write("\n".join(L))
# ---- README section
R = f"""

## R3 (decision date 2024-10-19, law S5 = legi-data 2.385.0 (== S4 texts), rules G2 = 3a4091ae1caf; reverse check of commit 9bb43d710094) — what was added
- Verdict MISMATCH (high): commit "fix: correction des taux auto-entrepreneur DROM" moves the 4 DROM rate rules out of the BODY of the private rule `DROM . seconde période` (where publicodes silently DROPPED them since the re-indent commit 05334b12 of 2024-09-02) into `DROM . avec`; parsed rules 1258 -> 1262. Before: DROM AE paid full rates (BNC 231 €/mois at 10/2024); after: 3,6/10,6/14,1 (BNC), 7,1/10,6/14,2 (CIPAV), 3,6/10,6/14,2 (BIC), 2,1/6,2/8,2 (vente). BIC/vente = D756-5 x D613-4 in force; BNC/CIPAV = fractions of the SUPERSEDED 21,1/21,2 (expected 3,9/11,6/15,4 and 7,8/11,6/15,5 for date >= 07/2024).
- LESSON engine: unknown keys inside a rule body (a nested rule written without `avec:`) are silently ignored — no build error. Detector: `parsed_rule_count` and `list --prefix`. Always compare counts before/after.
- NEW at G2 (closes an old open item): metropolitan AE rates follow D613-4 v.LEGIARTI000049624068 for `date >= 07/2024` (BNC 23,1 / CIPAV 23,2; history commits 8d04dbb6, 1d2874c5, d0a49c3f). G2 `list` names: `COT . service BNC . taux`, `COT . taux service BNC` both exist; the DROM `remplace` targets `... . service BNC . taux`.
- DROM mechanics: `première période` = trimestres civils <= 8, `seconde période` = années civiles <= 3 (both privé). Overrides: P1 4/1, P2 10/3, P3 20/5 (+ `entreprise . durée d'activité` jours). CIPAV amounts are €/an (12 000 x rate), others €/mois.
- Files: `evals/cases_R3_drom.json` (28 cases: 4 activities x 3 periods x 2 dates + 4 metropole controls), `evals/R3_drom_{{before_G2,after_G2post,proposal}}.jsonl`; `scripts/grid_evals.py A.jsonl B.jsonl` (compact before|after grid, flags CHANGED); `proposals/R3/after` (= G2 + patch, registered as G2post_R3), `proposals/R3/proposal` (+ `CHANGES_proposal.diff`, script `scripts/apply_proposal_R3.py <root>`: date >= 07/2024 variations for BNC/CIPAV; build OK; 39/116/154 and 936/1392/1860 at 10/2024); `scripts/add_links_R3.py` (L0120-L0145; results `sophon/link_results_R3.jsonl`), `scripts/gen_answer_R3.py <calls>`; reports `sophon/reports/R3_*`. Store: 145 links, verify-store clean.
- LESSON sophon: `revalidate` over 120+ links takes > 2 min -> run it in the background or with a long timeout; `asof` prints the whole JSON to stdout (use `--out` and do not pipe to head: BrokenPipe traceback, file still written).
- LESSON YAML: a nested `variations:` under `alors:` must be indented 2 more than `alors` (an `alors:` with nothing deeper = "Une des valeurs de la formule est vide").
- Still open: DROM BNC/CIPAV for date >= 07/2024 (this task), DROM values for 2025/2026 D613-4 versions (no text: abstain), D756-5 II CA cap, D613-4 c) meublés 6 %, D613-6 shares (v.LEGIARTI000049625264 text available since S3 — check whether G2 transposed them), CIPAV ACRE leak, D632-1 2024 floor, L613-7 minimum option, micro ACRE rate article outside the set.
"""
open('work/README.md', 'a').write(R)
print("answer.json keys:", list(ans.keys())); print("evidence:", len(evidence), "expected:", len(exp), "links:", len(links), "reports:", len(reports)); print("NOTES.md lines:", len(L))
