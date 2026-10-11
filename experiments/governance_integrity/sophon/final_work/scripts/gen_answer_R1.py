#!/usr/bin/env python3
"""Build output/answer.json + output/NOTES.md for R1 from the recorded artefacts (link results, reports, eval summaries)."""
import json, glob, re, os, hashlib
SELF_CALLS = 20
links = []
for ln in open('work/sophon/link_results_R1.jsonl'):
    rec = json.loads(ln)
    try: j = json.loads(rec['stdout'].splitlines()[-1])
    except Exception: j = {'raw': rec['stdout'][:300]}
    small = {k: (v if len(json.dumps(v, ensure_ascii=False)) < 220 else '...') for k, v in j.items()}
    small['id'] = j.get('link_id') or j.get('id')
    links.append({'tag': rec['tag'], **small})
reports = sorted(glob.glob('work/sophon/reports/R1_*'))
bt = json.load(open('work/proposals/R1/before_tree_summary.json'))
f = bt['files'][0]
before_sum = open('work/evals/R1_before_summary.txt').read().splitlines()[1:]
after_sum = open('work/evals/R1_after_summary.txt').read().splitlines()[1:]
evals_identical = before_sum == after_sum
raw = json.load(open('inputs/law/S3_legi-data-2.381.0/articles.json'))['articles']
d6134 = raw['D613-4'][0]; t = d6134['text']
def q(p): return re.search(p, t).group(0)
Q_BIC = q(r'46\s300 euros 50\s% 23\s150 euros 21,2\s%'); Q_BNC = q(r'10\s000 euros 34\s% 6\s600 euros 23,1\s%'); Q_CIPAV = q(r'35\s076 euros 34\s% 23\s150 euros 23,2\s%')
VID = d6134['id']  # LEGIARTI000049624068
AE_BNC_SIT = {"date":"01/07/2024","salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","entreprise . activité . nature":"'libérale'","dirigeant . auto-entrepreneur . chiffre d'affaires":"1000 €/mois","entreprise . date de création":"01/01/2021","dirigeant . exonérations . ACRE":"non","établissement . commune . département . outre-mer":"non"}
SAL_SIT = {"date":"01/07/2024","salarié . contrat . salaire brut":"3000 €/mois"}
def lid(tag):
    for l in links:
        if l['tag'] == tag: return l.get('id') or l.get('link_id') or '?'
    return '?'
answer = {
 "task": "R1",
 "commit": "2a0e452617fc33b955096f4bb7f7f305ec0670ad",
 "label": "HARMLESS_REFACTOR",
 "confidence": "high",
 "rationale": ("Commit 2a0e452617fc ('fix: met à jour les liens morts') changes, inside the rule library, exactly one line of one file: the URL of a "
   "'références' entry (documentation metadata) of the rule 'établissement . taux ATMP' (employer AT/MP rate for salaried staff), from net-entreprises.fr to ameli.fr. "
   "The other four files of the commit are site UI locale/TSX files outside modele-social. No formula, unit, default, threshold or applicability is touched. "
   "The rule concerns the AT/MP employer contribution, which no bounded article governs (0 occurrences of 'accident', 'AT/MP' or 'maladies professionnelles' in the 12 bounded S3 articles). "
   "Engine proof: a disposable BEFORE tree was built by reverse-applying the hunk on a copy of G1 (only that file differs; sha256 3af0885d... -> f4bacbb8...); "
   "build gives 641 raw / 1220 parsed rules on both sides, the parsed rule-name lists are identical, and 11 situations x 33 rule values (touched rule, its consumer salarié . cotisations . ATMP, "
   "all bounded AE and indépendant rules at 01/07/2024 and 01/12/2024) are identical before and after. sophon revalidate S3/G1pre_R1 and S3/G1 give byte-identical per-link results (113 links). "
   "This is documentation/metadata only: HARMLESS_REFACTOR. The pre-existing misalignment of the AE rates with D613-4 v." + VID + " (23,1 % BNC / 23,2 % CIPAV since 2024-07-01, library still 21,1 / 21,2) "
   "exists identically on both sides and is neither caused nor addressed by this commit; it is reported separately below, not as the label of this change."),
 "evidence": [
  {"kind": "diff_excerpt", "article": None, "article_version_id": None,
   "quote_or_values": "modele-social/règles/entreprise/établissement.publicodes @@ -58,7 +58,7 @@ (rule 'établissement . taux ATMP', key 'références'): "
     "-    Connaître le taux AT/MP de votre entreprise sur votre compte AT/MP: https://www.net-entreprises.fr/declaration/compte-atmp/#lessentiel  "
     "+    Connaître le taux AT/MP de votre entreprise sur votre compte AT/MP: https://www.ameli.fr/entreprise/votre-entreprise/cotisation-atmp ; stat: 5 files, only this one under modele-social/ (others: site/source/locales/ui-en.yaml, ui-fr.yaml, RésultatSimple.tsx, CasParticuliers.tsx). "
     f"sha256 before {f['sha_before'][:12]}... after {f['sha_after'][:12]}...; files differing between BEFORE and AFTER trees: {bt['files_differing_between_trees']} ({bt['n_files_before']} files each)."},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": "build BEFORE (work/proposals/R1/before/modele-social/règles) = AFTER (inputs/rules/G1_2a0e452617fc/modele-social/règles): raw_rule_count 641, parsed_rule_count 1220; `list` names identical (1220 names, diff = directory header only)."},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": "touched rule, situation " + json.dumps(SAL_SIT, ensure_ascii=False) + " date 01/07/2024: établissement . taux ATMP = 2.23 % (BEFORE) / 2.23 % (AFTER); salarié . cotisations . ATMP = 66.9 €/mois / 66.9 €/mois; salarié . cotisations . ATMP . taux minimum = 0.46 % both; salarié . cotisations = 1721.8275 €/mois both. With 'établissement . taux ATMP': '3.5 %' set: taux 3.5 % / ATMP 105 €/mois on both sides."},
  {"kind": "engine_before_after", "article": "D613-4", "article_version_id": VID,
   "quote_or_values": "AE BNC situation " + json.dumps(AE_BNC_SIT, ensure_ascii=False) + ": dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux service BNC = 21.1 % BEFORE / 21.1 % AFTER; . cotisations = 211 €/mois both; cotisations et contributions = 213 €/mois both; revenu net = 9444 €/an both. BIC service (artisanale/service): taux service BIC 21.2 %, cotisations 212 €/mois, RCI revenu cotisé 420 €/an both. Vente: 12.3 % / 123 €/mois both. CIPAV (réglementée, created 01/01/2019): taux 21.2 %, 2544 €/an both. DROM BNC (outre-mer oui, 4 années civiles): DROM . taux service BNC 14.1 %, 141 €/mois both. AE BNC at 01/12/2024: 21.1 % / 211 €/mois both."},
  {"kind": "engine_before_after", "article": "D621-2", "article_version_id": raw['D621-2'][0]['id'],
   "quote_or_values": "Indépendant EI/IR/commerciale, revenu professionnel 20000 €/an, date 01/07/2024: cotisations et contributions 8020 €/an, maladie 126, indemnités journalières 100, retraite de base 3550, retraite complémentaire 1400, invalidité et décès 260, CSG-CRDS 2468, assiette des cotisations 20000 €/an -- identical BEFORE/AFTER. ACRE (created 01/01/2024, ACRE oui): total 3592, maladie 0, retraite de base 0 both. Trader 40000 €/an at 01/12/2024: 18025 / maladie 2168 / retraite de base 7100 / CSG-CRDS 5121 both. Full tables: work/evals/R1_before_summary.txt vs R1_after_summary.txt (identical=" + str(evals_identical) + ")."},
  {"kind": "article_quote", "article": "D613-4", "article_version_id": VID,
   "quote_or_values": Q_BIC + "  (in force 2024-07-01..2025-05-01) -> library taux service BIC = 21.2 at 01/07/2024 on BOTH snapshots: sophon links " + lid('R1-G1pre_R1-BIC') + " (G1pre_R1) and " + lid('R1-G1-BIC') + " (G1), both VERIFIED."},
  {"kind": "article_quote", "article": "D613-4", "article_version_id": VID,
   "quote_or_values": Q_BNC + "  (in force 2024-07-01..2025-05-01) -> library taux service BNC = 21.1 at 01/07/2024 on BOTH snapshots (expected 23.1): sophon links " + lid('R1-G1pre_R1-BNC') + " (G1pre_R1) and " + lid('R1-G1-BNC') + " (G1), both FAILED. Pre-existing, unchanged by this commit."},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": "sophon revalidate --law-snapshot S3 --rules-snapshot G1pre_R1 vs --rules-snapshot G1: counts BROKEN 27, REASSESS_LAW_CHANGED 36, REASSESS_RULE_CHANGED 10, RULE_CHANGED_CHECK_STILL_PASSES 15, STILL_VERIFIED 10, UNVERIFIED_NO_CHECK 11 on both; the two reports are byte-identical after normalising the snapshot id (only generated_at differs). Bounded articles without any link: none."}
 ],
 "expected_values_if_mismatch": [],
 "pre_existing_gaps_not_caused_by_this_commit": [
  {"rule": "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux service BNC", "date": "01/07/2024", "found": 21.1, "text_value": 23.1, "article": "D613-4", "article_version_id": VID, "quote": Q_BNC, "status": "identical before and after; link FAILED on both snapshots"},
  {"rule": "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . cotisations CIPAV . taux", "date": "01/07/2024", "found": 21.2, "text_value": 23.2, "article": "D613-4", "article_version_id": VID, "quote": Q_CIPAV, "status": "identical before and after (engine value from cases_R1 AE_CIPAV; no new link recorded)"},
  {"note": "Other open items carried from T0/T1a/T1b (CIPAV ACRE leak, D632-1 2024 floor, D613-6 split, meublés de tourisme 6 %, L613-7 option, D756-5 II cap, 2024 unified base lines) are all untouched by this commit; see work/README.md."}
 ],
 "outside_bounded_set": [
  "The touched rule 'établissement . taux ATMP' (employer accidents du travail / maladies professionnelles rate) is governed by CSS provisions on AT/MP tarification that are not in the bounded set and not available here (no text quoted, none relied upon). None of the 12 bounded S3 articles mentions 'accident', 'AT/MP' or 'maladies professionnelles' (grep count 0). Classifying a URL-only metadata edit does not require them."
 ],
 "approval": "none recorded",
 "notes": ("BEFORE tree = reverse-applied hunk on a copy of G1 (work/scripts/make_before_tree.py -> work/proposals/R1/before, summary before_tree_summary.json), registered in sophon as rules snapshot G1pre_R1 (build 641/1220). "
   "The 'before' is a reconstruction, not a git checkout of the parent commit (git use forbidden); its only difference from G1 is the one URL line, as the full-tree diff shows. "
   "Non-règles files of the commit (site/ locales and TSX) are outside the executable library and were not evaluated. "
   "Decision date 2024-07-17; law snapshot S3 (legi-data 2.381.0) unchanged by this event. Approvals: none recorded anywhere in the corpus."),
 "sophon_reports": reports,
 "sophon_links_added": links,
 "self_reported_tool_calls": SELF_CALLS
}
def denone(o):   # stray "None" strings (from sophon stdout fields) -> null
    if isinstance(o, dict): return {k: denone(v) for k, v in o.items()}
    if isinstance(o, list): return [denone(v) for v in o]
    return None if o == 'None' else o
answer = denone(answer)
os.makedirs('output', exist_ok=True)
json.dump(answer, open('output/answer.json', 'w'), ensure_ascii=False, indent=1)
notes = f"""# R1 — reverse check of commit 2a0e452617fc (decision date 2024-07-17, law S3, rules G1)

## Verdict
**HARMLESS_REFACTOR** (confidence high). The commit "fix: met à jour les liens morts" (authored 2024-06-26, committed 2024-07-16 21:29:59 +0200, Fixes #2165)
changes, inside `modele-social/règles`, a single line: the URL of a `références` entry of the rule `établissement . taux ATMP`
(`https://www.net-entreprises.fr/declaration/compte-atmp/#lessentiel` -> `https://www.ameli.fr/entreprise/votre-entreprise/cotisation-atmp`).
`références` is documentation metadata; no formula, unit, default, plancher or applicability changes. The four other files are site UI files (locales, TSX), outside the library.

## Why not the other labels
- Not MISMATCH: nothing the library computes changed (see engine proof) and the touched rule is not governed by any bounded article.
- Not LEGITIMATE_INDEPENDENT_CHANGE: there is no implementation choice, only a link fix.
- Not UNRESOLVED: nothing in the bounded text is needed to settle a URL-only edit.

## Scope w.r.t. the bounded articles
The 12 bounded S3 articles contain 0 occurrences of "accident", "AT/MP", "ATMP" or "maladies professionnelles" (grep over inputs/law/S3_legi-data-2.381.0/articles.json).
The AT/MP employer contribution is governed by CSS provisions outside the bounded set (not available here; none quoted, none relied upon).

## Engine proof (before vs after)
- BEFORE tree: `work/proposals/R1/before/modele-social` = copy of G1 with the hunk reverse-applied by `work/scripts/make_before_tree.py`
  (context lines verified; `work/proposals/R1/before_tree_summary.json`). Only `règles/entreprise/établissement.publicodes` differs
  (sha256 before {f['sha_before']} / after {f['sha_after']}); 49 files each; `diff -ru` of the two règles trees shows only the URL line.
- `build`: raw 641 / parsed 1220 rules on both sides. `list`: identical rule names (diff = directory header only; `work/proposals/R1/list_*.txt`).
- `work/evals/cases_R1.json` (11 situations, 33 rule values) run on both trees -> `R1_before_G1pre.jsonl`, `R1_after_G1.jsonl`; summaries identical ({evals_identical}).

AFTER (G1) table — BEFORE is identical line for line:
```
{chr(10).join(after_sum)}
```
Situations: SAL = {json.dumps(SAL_SIT, ensure_ascii=False)}; AE BNC = {json.dumps(AE_BNC_SIT, ensure_ascii=False)} (BIC: nature 'artisanale' + service ou vente 'service'; vente: 'commerciale' + 'vente'; CIPAV: libérale réglementée oui, created 01/01/2019; DROM: outre-mer oui + durée overrides);
INDEP = EI / IR / commerciale / revenu professionnel 20000 €/an / created 01/01/2021 (ACRE: created 01/01/2024, ACRE oui; TRADER: 40000 €/an at 01/12/2024).

## sophon (system of record)
- Snapshots: S3 and G1 re-registered (idempotent); BEFORE tree registered as rules snapshot `G1pre_R1` (meta `work/proposals/R1/before/meta.json`).
- `revalidate S3/G1` and `S3/G1pre_R1`: same counts (BROKEN 27, REASSESS_LAW_CHANGED 36, REASSESS_RULE_CHANGED 10, RULE_CHANGED_CHECK_STILL_PASSES 15, STILL_VERIFIED 10, UNVERIFIED_NO_CHECK 11), reports byte-identical after normalising the snapshot id. No bounded article without a link.
  (The BROKEN/REASSESS statuses are inherited from T0/T1a/T1b links recorded against G0 / proposal snapshots and against the pre-July D613-4 texts; they are not caused by this commit.)
- Links added (D613-4 v.{VID}, quotes extracted from the real text): {', '.join(l['tag'] + '=' + str(l.get('id', '?')) + ':' + str(l.get('status')) for l in links)}.
  BIC d) {Q_BIC} -> 21.2 VERIFIED on both snapshots; BNC e) {Q_BNC} -> library 21.1, FAILED on both snapshots = pre-existing gap.
- Reports: {', '.join(reports)}. verify-store: 0 problems, 113 links checked.

## Pre-existing misalignment (NOT the subject of this commit, identical before/after)
D613-4 v.{VID} (in force 2024-07-01..2025-05-01) gives e) BNC 23,1 % and b) CIPAV 23,2 % ({Q_CIPAV}); the library computes 21.1 / 21.2 at 01/07/2024 on both sides
(1000 €/mois CA -> 211 €/mois instead of 231). Also D613-6 v.LEGIARTI000049625264 shares are not transposed. These remain the main open items for the next change on the rules side.
Other open items from earlier tasks are listed in work/README.md.

## Approval
none recorded (no sign-off, ratification or approval record exists in the corpus; a merge/commit/test is not an approval).

## Tool calls
self-reported: {SELF_CALLS} (including reads).
"""
open('output/NOTES.md', 'w').write(notes)
readme_add = f"""
## R1 (decision date 2024-07-17, law S3, rules G1 = 2a0e452617fc; reverse check of that commit) — what was added
- Verdict HARMLESS_REFACTOR (high): commit "fix: met à jour les liens morts" = one URL in `références` of `établissement . taux ATMP` (AT/MP, outside the bounded articles: 0 mentions of accident/AT-MP in S3) + site/ UI files. Engine identical before/after (641/1220 rules; 11 situations x 33 values).
- `scripts/make_before_tree.py DIFF AFTER_ROOT OUT_ROOT [--all]`: GENERIC reverse-apply of a commit's règles hunks onto a copy of the after-tree (handles git-quoted UTF-8 paths, verifies context, prints hashes + list of differing files). Use it for every future R-task to get the BEFORE tree without git. Output here: `proposals/R1/before/` (+ `before_tree_summary.json`, `list_before/after.txt`, `reval_before_norm.json`).
- `scripts/add_links_R1.py` (links on both snapshots; L-ids in `sophon/link_results_R1.jsonl`), `scripts/gen_answer_R1.py` (answer + NOTES generator; edit SELF_CALLS). `evals/cases_R1.json` = reusable regression set spanning salarié ATMP, AE (BNC/BIC/vente/CIPAV/DROM), indépendant (base/ACRE/trader) at 01/07/2024 and 01/12/2024; outputs `evals/R1_*`.
- Sophon: rules snapshot `G1pre_R1` (before tree) registered; links {', '.join(str(l.get('id','?')) for l in links)} (R1-G1pre_R1-BIC/BNC, R1-G1-BIC/BNC); reports `sophon/reports/R1_*` (revalidate S3/G1 and S3/G1pre_R1 identical; evidence; verify-store 113 links clean; asof D613-4 2024-07-17). Store: 113 links.
- Lesson: `inputs/law/<S>/articles.json` = {{"snapshot","legi_data_version",...,"articles": {{"D613-4": [record], ...}}}} — each article maps to a LIST of records (one, the current version with `text`, `text_sha256`, `articleVersions`, `lienModifications`). `evalbatch.py` usage: `python3 -I work/scripts/evalbatch.py cases.json rules_dir out.jsonl`; `summarize_evals.py out.jsonl` for the compact table (diff the tables for before/after).
- Lesson: a `list`/`build` JSON header contains the rules_dirs path -> diff the `names` only. Reading a big file with cat exceeds the tool output limit: use Read or head.
- Still open on the rules side (identical before/after this commit): AE rates for date >= 07/2024 (D613-4 v.LEGIARTI000049624068: BNC 23,1 / CIPAV 23,2; library 21,1 / 21,2 -> L-links FAILED), D613-6 v.LEGIARTI000049625264 shares, plus the T0/T1a/T1b list above.
"""
open('work/README.md', 'a').write(readme_add)
print('written: output/answer.json, output/NOTES.md, README appended; links:', [(l['tag'], l.get('id'), l.get('status')) for l in links]); print('reports:', reports)
