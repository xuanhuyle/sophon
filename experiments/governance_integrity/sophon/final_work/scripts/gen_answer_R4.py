#!/usr/bin/env python3
"""Build output/answer.json and output/NOTES.md for R4 from the recorded evidence.
usage: python3 -I work/scripts/gen_answer_R4.py <self_reported_tool_calls>   (from the staging dir)"""
import json, re, sys, os
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 0
raw = json.load(open('inputs/law/S9_legi-data-2.514.0/articles.json'))['articles']
art = raw['D633-3'][0]; V = art['id']
def flex(s): return ''.join(r'\s' if c == ' ' else (r"['’]" if c == "'" else re.escape(c)) for c in s)
QI = re.search(flex("Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %."), art['text']).group(0)
QII = re.search(flex("Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %."), art['text']).group(0)
meta = json.load(open('inputs/diffs/R4_d3e0cfe0f12d/meta.json'))
def load(p):
    d = {}
    for ln in open(p):
        r = json.loads(ln)
        try: d[r['id']] = json.loads(r['stdout'])['evaluations']
        except Exception: d[r['id']] = {}
    return d
B = load('work/evals/R4_before_G4pre.jsonl'); A = load('work/evals/R4_after_G4post.jsonl')
RB = "indépendant . cotisations et contributions . cotisations . retraite de base"
RC = "protection sociale . retraite . base . revenu cotisé"; TR = "protection sociale . retraite . base . trimestres"; PS = "protection sociale . retraite . base"
def v(E, cid, rule):
    e = E.get(cid, {}).get(rule);
    if not e or 'error' in e: return None
    x = e.get('nodeValue'); return round(x, 4) if isinstance(x, float) else x
def sit(cid): return next(c['situation'] for c in json.load(open('work/evals/cases_R4.json')) if c['id'] == cid)
links = [json.loads(l) for l in open('work/sophon/link_results_R4.jsonl')]
lid = {l['tag']: (l['result'].get('link_id'), l['result'].get('status')) for l in links}
def reval(name):
    p = f'work/sophon/reports/{name}_cmd.json'
    if not os.path.exists(p): return None
    lines = [l for l in open(p).read().splitlines() if l.startswith('{')]
    return json.loads(lines[-1]).get('counts') if lines else None
RV = {n: reval(n) for n in ('R4_revalidate_S9_G4', 'R4_revalidate_S9_G4pre_R4', 'R4_revalidate_S9_G4post_R4')}
grid_ids = ['AC_4000_2025', 'AC_6900_2025', 'AC_20000_2025', 'AC_23000_2025', 'AC_47100_2025', 'AC_60000_2025', 'AC_120000_2025', 'AC_250000_2025',
            'PLNR_20000_2025', 'PLNR_60000_2025', 'CNAVPL_20000_2025', 'CNAVPL_60000_2025', 'CNAVPL_250000_2025', 'AC_tabac_60000_2025', 'AC_60000_2026',
            'AC_4000_2024', 'AC_6900_2024', 'AC_20000_2024', 'AC_23000_2024', 'AC_60000_2024', 'AC_250000_2024']
def row(cid): return {'case': cid, 'date': sit(cid)['date'], 'assiette': sit(cid)['indépendant . cotisations et contributions . assiette sociale'],
                      'retraite_de_base_before': v(B, cid, RB), 'retraite_de_base_after': v(A, cid, RB),
                      'revenu_cotise_before': v(B, cid, RC), 'revenu_cotise_after': v(A, cid, RC),
                      'trimestres_before': v(B, cid, TR), 'trimestres_after': v(A, cid, TR), 'pension_before': v(B, cid, PS), 'pension_after': v(A, cid, PS)}
rows = [row(c) for c in grid_ids]
all_ids = list(B.keys())
rb_same_2025 = all(v(B, c, RB) == v(A, c, RB) for c in all_ids if '2024' not in c)
rb_diff_2024 = [(c, v(B, c, RB), v(A, c, RB)) for c in all_ids if '2024' in c and v(B, c, RB) != v(A, c, RB)]
rc_changed = [c for c in all_ids if v(B, c, RC) != v(A, c, RC)]
tr_changed = [(c, v(B, c, TR), v(A, c, TR)) for c in all_ids if v(B, c, TR) != v(A, c, TR)]
S60 = json.dumps(sit('AC_60000_2025'), ensure_ascii=False)
ev = [
 {"kind": "article_quote", "article": "D633-3", "article_version_id": V, "quote_or_values": QI + " [in force 2024-07-07 (Décret n°2024-688 du 5 juillet 2024, art. 3); nota: applies to periods from 2025-01-01]"},
 {"kind": "article_quote", "article": "D633-3", "article_version_id": V, "quote_or_values": QII},
 {"kind": "diff_excerpt", "article": "D633-3", "article_version_id": V, "quote_or_values": "cotisations.publicodes: '- somme: [tranche 1, tranche 2]' (tranche 1 = assiette plafonnée au PSS proratisé x taux 17.15% ; tranche 2 = assiette (non plafonnée hors CNAVPL) x taux 0.72%/0.60%) replaced by '+ barème: assiette, multiplicateur: PSS proratisé, tranches: [taux T1 (17.87% après réforme / 17.75%) plafond 1, taux T2 (0.72% / 0.60%)]' with the comment: 'Le code de la sécurité sociale décrit un calcul identique à celui des PLR (taux T1 sur la part de l'assiette < PASS + taux T2 sur toute l'assiette) mais l'Urssaf calcule différemment (taux T2 sur la part de l'assiette > PASS uniquement) et a insisté pour que l'on reprenne leur méthode.' CNAVPL moved to 'indépendant . profession libérale . CNAVPL . retraite de base' (8.73%/8.23% to PSS + 1.87% to 5 PSS). retraite-base.publicodes: 'revenu cotisé' = retraite de base / 'tranche 1 . taux' (17.15 %) -> / 'taux de cotisation' (= taux T1 17.87 % for non-CNAVPL)."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": f"rule '{RB}', situation {S60}: before (G4pre_R4) {v(B,'AC_60000_2025',RB)} €/an (tranche 1 {v(B,'AC_60000_2025',RB+' . tranche 1')} + tranche 2 {v(B,'AC_60000_2025',RB+' . tranche 2')}), after (G4post_R4) {v(A,'AC_60000_2025',RB)} €/an; text: 17,15 % x 47 100 + 0,72 % x 60 000 = 8 077,65 + 432 = 8 509,65 -> 8 510. Identical."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": "retraite de base before|after at 01/07/2025 (assiette set via 'indépendant . cotisations et contributions . assiette sociale', EI/IR commerciale unless stated): " + "; ".join(f"{r['case']}: {r['retraite_de_base_before']}|{r['retraite_de_base_after']}" for r in rows if '2025' in r['case'] or '2026' in r['case']) + f". All {sum(1 for c in all_ids if '2024' not in c)} 2025/2026 cases identical: {rb_same_2025}."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": f"rates: before 'tranche 1 . taux' = {v(B,'AC_60000_2025',RB+' . tranche 1 . taux')} % and 'tranche 2 . taux' = {v(B,'AC_60000_2025',RB+' . tranche 2 . taux')} % (textual, D633-3 I/II); after 'taux T1' = {v(A,'AC_60000_2025',RB+' . taux T1')} % (= 17,15 + 0,72, not a rate written in the text) and 'taux T2' = {v(A,'AC_60000_2025',RB+' . taux T2')} % (applied above the PSS only). At 01/07/2024: {v(B,'AC_60000_2024',RB+' . tranche 1 . taux')}/{v(B,'AC_60000_2024',RB+' . tranche 2 . taux')} before vs 17.75/0.6 after (version LEGIARTI000041967101 text not in S9: unverifiable)."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": "NOT identical (rules outside the bounded articles): 'protection sociale . retraite . base . revenu cotisé' before|after: " + "; ".join(f"{r['case']}: {r['revenu_cotise_before']}|{r['revenu_cotise_after']}" for r in rows if r['revenu_cotise_before'] != r['revenu_cotise_after']) + f" ({len(rc_changed)} of {len(all_ids)} cases changed; all below the PSS, non-CNAVPL). 'trimestres' changed: " + "; ".join(f"{c}: {b}|{a}" for c, b, a in tr_changed) + ". Pension estimate 'protection sociale . retraite . base' changes accordingly (e.g. AC_20000_2025 868|833 €/mois)."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": "2024 dates (pre-reform rates, governing version not in snapshot): 1 € rounding-path differences " + "; ".join(f"{c}: {b}|{a}" for c, b, a in rb_diff_2024) + " (before = round(T1)+round(T2), after = round(barème)). Other 2024 cases identical. CNAVPL cases: all identical before/after (D642-3, outside the set)."},
 {"kind": "engine_before_after", "article": "D633-3", "article_version_id": V, "quote_or_values": "build: before raw 296 / parsed 446 rules, after raw 295 / parsed 449; names: -6 (tranche 1/2 + assiette/taux) +3 (assiette, taux T1, taux T2) under retraite de base, +5 'indépendant . profession libérale . CNAVPL . retraite de base[. tranche 1/2[. taux]]', +1 'revenu cotisé . taux de cotisation'."},
]
answer = {
 "task": "R4", "commit": meta['commit'], "label": "LEGITIMATE_INDEPENDENT_CHANGE", "confidence": "high",
 "rationale": ("Commit d3e0cfe0 ('chore: remplace la formule de la retraite de base par celle de l'Urssaf') rewrites the artisan/commerçant/PLNR retraite de base from the "
   "CSS decomposition (tranche 1 = 17,15 % x assiette within the PSS + tranche 2 = 0,72 % x the whole assiette, a literal transcription of D633-3 I and II) into the Urssaf "
   "presentation (barème: 17,87 % = 17,15 + 0,72 on the part up to the PSS, 0,72 % on the part above only), explicitly because 'l'Urssaf ... a insisté pour que l'on reprenne "
   "leur méthode' - a source outside the bounded set. D633-3 v." + V + " does not forbid it: the two formulas are algebraically identical and the engine returns identical "
   "contribution amounts for every 2025/2026 situation tested on both trees (e.g. 3 574 at 20 000; 8 417 at 47 100 = PSS; 8 510 at 60 000; 9 878 at 250 000; 8 438 with the "
   "tabac deduction), and identical CNAVPL amounts. It is not a harmless refactor: what the engine computes did change - 'taux T1' now exposes 17,87 % (a folded rate the text does not state), "
   "'protection sociale . retraite . base . revenu cotisé' (now divided by 17,87 % instead of 17,15 %) falls for every assiette below the PSS (20 840 -> 20 000 at 20 000), the "
   "validated 'trimestres' change at the thresholds (4 -> 3 at 6 900; 3 -> 2 at 4 000 in 2025, where the after-value 5 344 falls 2 EUR short of the 450 h SMIC floor the library's "
   "own assiette minimale is meant to guarantee) and the pension estimate moves; those rules rest on R351-9 / R634-1 / D634-1, outside the bounded set, so they are reported, not judged. "
   "Not a mismatch: no bounded requirement is computed differently. At 2024 dates the trees differ by 1 EUR in three cases (rounding path) under the pre-reform rates 17,75/0,60, "
   "which cannot be checked because the D633-3 version then in force (LEGIARTI000041967101) has no text in S9: abstain."),
 "evidence": ev,
 "expected_values_if_mismatch": [],
 "outside_bounded_set": [
   "Urssaf calculation method ('taux T2 sur la part de l'assiette > PASS uniquement'): the commit's stated source; no legal text for it in the corpus",
   "R351-9, R634-1, D634-1 CSS: revenu cotisé and trimestres validés (the rules whose values actually change)",
   "D642-3 / D642-4 CSS: CNAVPL retraite de base rates 8,73 % / 8,23 % / 1,87 % and 5 PSS cap (moved, values identical)",
   "D633-2 CSS: assiette minimale retraite (450 h SMIC floor used in the 4 000 cases)",
   "D633-3 v.LEGIARTI000041967101 (2020-05-25..2024-07-07): text not in S9, so the 2024 rates 17,75 % / 0,60 % and the 1 EUR rounding differences are unverifiable",
   "PSS 2025 (47 100 €/an) and 2026 (48 060 €/an), SMIC 2024/2025: library parameters whose source (arrêtés) is not in the corpus"
 ],
 "approval": "none recorded",
 "notes": ("Law S9 = legi-data 2.514.0; D633-3 unchanged since S3 (same id and text hash). Trees evaluated: inputs/diffs/R4_d3e0cfe0f12d/context_parent_tree (sophon G4pre_R4, 446 parsed rules) "
   "and context_tree_after (G4post_R4, 449) with --rules modele-ti/règles --rules modele-commun/règles; the task's rules pin G4 (modele-social 10.0.1, 2026-03-03) is a different package layout "
   "(dirigeant . indépendant . ...) and does not contain the commit's rules. Situations set the assiette directly ('indépendant . cotisations et contributions . assiette sociale'); "
   "going through 'indépendant . revenu professionnel' is circular in modele-ti. 50 cases x 2 trees in work/evals/R4_*; grid in work/evals/R4_grid.txt. "
   f"Sophon: links L0146-L0159 (13 VERIFIED, 1 UNKNOWN = the 2024 abstention); revalidation counts S9xG4: {RV['R4_revalidate_S9_G4']}; S9xG4pre_R4: {RV['R4_revalidate_S9_G4pre_R4']}; "
   f"S9xG4post_R4: {RV['R4_revalidate_S9_G4post_R4']} (older links name modele-social rules, hence BROKEN/RULE_FILE_ABSENT on the modele-ti trees). "
   "Corroboration outside S9 (my sophon store's law snapshot S0 = legi-data 2.360.0, registered in T0, not part of this task's inputs): the pre-2024-07-07 version LEGIARTI000041967101 (2020-05-25) reads "
   "'I.-Le taux des cotisations assises sur le revenu d'activité dans la limite du plafond est fixé à 17,15 %. II.-Le taux des cotisations assises sur la totalité du revenu d'activité est fixé à 0,60 %.' "
   "- consistent with both trees' 2024 rates (17,15 + 0,60 = 17,75; the only 2024 difference is the rounding path), but since S9 does not carry that text the 2024 values stay an abstention here. "
   "Side finding for the maintainers (outside the bounded set): after the commit a minimal-assiette contributor (5 346) validates 2 trimestres instead of 3 because revenu cotisé = round(955) / 17,87 % = 5 344 < 5 346. "
   "Also still open from earlier tasks: S9 brings new D613-4 (LEGIARTI000052218738, 2026-01-01: BNC 25,6 %, vente 89 776 €/26 035 €... ), D613-6 (LEGIARTI000052218747), D131-6-1 (LEGIARTI000053451315), L136-3 (LEGIARTI000051284498) versions not assessed here (AE side, not touched by this commit)."),
 "sophon_reports": sorted('work/sophon/reports/' + f for f in os.listdir('work/sophon/reports') if f.startswith('R4_')),
 "self_reported_tool_calls": CALLS,
 "engine_grid": rows,
 "sophon_links": {t: lid[t] for t in lid},
}
os.makedirs('output', exist_ok=True)
json.dump(answer, open('output/answer.json', 'w'), ensure_ascii=False, indent=1)
md = []
md.append(f"# R4 — reverse check of commit {meta['commit'][:12]} (decision date 2026-03-31)\n")
md.append(f"**Verdict: LEGITIMATE_INDEPENDENT_CHANGE (high).** Approval: none recorded.\n")
md.append("## The change\n" + meta['subject'] + f" (authored {meta['authored']}, committed {meta['committed']}, {meta['author']}). Files: modele-ti/règles/indépendant/cotisations-et-contributions/cotisations/cotisations.publicodes, "
          "indépendant/professions-libérales/CNAVPL.publicodes, protection-sociale/retraite-base.publicodes (+ site tests/locales, not in the trees).\n\n"
          "- Before: `retraite de base` (non CNBF) = `tranche 1` (assiette plafonnée PSS proratisé × 17,15 %, or 8,73/8,23 % CNAVPL) + `tranche 2` (assiette × 0,72 %/0,60 %, uncapped; CNAVPL 1,87 % capped 5 PSS), each rounded.\n"
          "- After: CNAVPL gets its own rule `indépendant . profession libérale . CNAVPL . retraite de base` (same tranches); everyone else gets a `barème` on `assiette` with multiplier `PSS proratisé`: `taux T1` = 17,87 % (après réforme, i.e. date >= 01/2025) / 17,75 % up to 1 PSS, `taux T2` = 0,72 % / 0,60 % above; one rounding.\n"
          "- Comment in the diff: *Le code de la sécurité sociale décrit un calcul identique à celui des PLR (taux T1 sur la part de l'assiette < PASS + taux T2 sur toute l'assiette) mais l'Urssaf calcule différemment (taux T2 sur la part de l'assiette > PASS uniquement) et a insisté pour que l'on reprenne leur méthode.*\n"
          "- `protection sociale . retraite . base . revenu cotisé` = retraite de base / `tranche 1 . taux` (17,15 %) becomes / `taux de cotisation` (= `taux T1` 17,87 % non-CNAVPL; CNAVPL tranche 1 taux unchanged).\n")
md.append(f"## Governing text (S9, legi-data 2.514.0)\nD633-3 v.{V}, in force 2024-07-07 (Décret n°2024-688 du 5 juillet 2024, art. 3; nota: applies to periods from 2025-01-01; text identical to S3/S5):\n\n> {QI}\n> {QII}\n\n"
          "17,15 % × min(A, P) + 0,72 % × A  ≡  17,87 % × min(A, P) + 0,72 % × max(A − P, 0) for every A: the Urssaf presentation is algebraically the same contribution. The text says nothing about rounding. "
          "The version in force before 2024-07-07 (LEGIARTI000041967101) has no text in the snapshot: the 2024 library rates (17,15/0,60 before, 17,75/0,60 after) cannot be checked.\n")
md.append("## Engine (both trees, `--rules modele-ti/règles --rules modele-commun/règles`; assiette set directly)\n\n| case | date | assiette | RB before | RB after | revenu cotisé before | after | trimestres before | after | pension before | after |\n|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    md.append(f"| {r['case']} | {r['date']} | {r['assiette']} | {r['retraite_de_base_before']} | {r['retraite_de_base_after']} | {r['revenu_cotise_before']} | {r['revenu_cotise_after']} | {r['trimestres_before']} | {r['trimestres_after']} | {r['pension_before']} | {r['pension_after']} |")
md.append(f"\n- Retraite de base identical before/after in all {sum(1 for c in all_ids if '2024' not in c)} 2025/2026 cases (AC, PLNR, CNAVPL, tabac): {rb_same_2025}. 2024 (pre-reform) 1 € rounding-path differences: {rb_diff_2024}.\n"
          f"- `revenu cotisé` changed in {len(rc_changed)}/{len(all_ids)} cases (all non-CNAVPL below the PSS); `trimestres` changed: {tr_changed}; pension estimate follows. These rest on R351-9/R634-1/D634-1 (outside the set).\n"
          "- Rates: before `tranche 1 . taux` 17.15 % / `tranche 2 . taux` 0.72 % (2025), 17.15/0.6 (2024); after `taux T1` 17.87 % / `taux T2` 0.72 % (2025), 17.75/0.6 (2024).\n"
          "- Build: 296/446 → 295/449 rules (names diff in work/evals/list_R4_before.txt vs list_R4_after.txt).\n"
          "- Side finding (outside the set): minimal assiette 5 346 (450 h × 11,88) → RB 955 both trees, but revenu cotisé after = 955/17,87 % = 5 344 < 5 346 → 2 trimestres instead of the 3 the cotisation minimale is meant to guarantee (before: 955/17,15 % = 5 569 → 3).\n")
md.append("## Why LEGITIMATE_INDEPENDENT_CHANGE\n- Not MISMATCH: every bounded requirement (D633-3 I and II) yields the same engine amounts before and after for the period the version governs (2025+); 13 executable sophon checks pass on both trees.\n"
          "- Not HARMLESS_REFACTOR: the computation changed (new folded rate 17,87 % exposed as `taux T1`; `revenu cotisé`, `trimestres`, pension estimate change for incomes below the PSS; 1 € rounding differences at 2024 dates).\n"
          "- The maintainers' stated reason is the Urssaf's method (outside the bounded set); the text does not forbid an equivalent decomposition.\n- UNRESOLVED only for the 2024 rounding differences (no text for the pre-2024-07-07 version).\n")
md.append("## Sophon\n- Snapshots registered: law S9; rules G4 (modele-social pin, 1334 parsed), G4pre_R4 (446), G4post_R4 (449).\n"
          f"- Links L0146–L0159 (work/sophon/link_results_R4.jsonl; builder work/scripts/add_links_R4.py): {json.dumps(lid, ensure_ascii=False)}\n"
          f"- Revalidation counts: S9×G4 {RV['R4_revalidate_S9_G4']}; S9×G4pre_R4 {RV['R4_revalidate_S9_G4pre_R4']}; S9×G4post_R4 {RV['R4_revalidate_S9_G4post_R4']}. Older links name modele-social rules (`dirigeant . ...`) → RULE_FILE_ABSENT/BROKEN on the modele-ti trees; LAW_CHANGED for D131-6-1, D613-4, D613-6, L136-3 (new 2025/2026 versions in S9, AE side, not part of this commit) and for the T0 links recorded against the pre-2024 D633-3/D621-2 versions.\n"
          "- Reports: " + ", ".join(answer['sophon_reports']) + "\n- Approval: none recorded (no sign-off, ratification or approval file exists in the corpus).\n")
open('output/NOTES.md', 'w').write("\n".join(md) + "\n")
print('answer.json + NOTES.md written; label', answer['label'], 'rb_same_2025', rb_same_2025, 'rb_diff_2024', rb_diff_2024, 'tr_changed', tr_changed, 'RV', RV)
