# R1 — reverse check of commit 2a0e452617fc (decision date 2024-07-17, law S3, rules G1)

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
  (sha256 before 3af0885d1808da735c14765e68af529ff0acc3e0abc7b193523cf0d77a6e46c8 / after f4bacbb822211a84e50ae0053be781aaff4c04c2addad51439f5c5199d553f98); 49 files each; `diff -ru` of the two règles trees shows only the URL line.
- `build`: raw 641 / parsed 1220 rules on both sides. `list`: identical rule names (diff = directory header only; `work/proposals/R1/list_*.txt`).
- `work/evals/cases_R1.json` (11 situations, 33 rule values) run on both trees -> `R1_before_G1pre.jsonl`, `R1_after_G1.jsonl`; summaries identical (True).

AFTER (G1) table — BEFORE is identical line for line:
```
   SAL@01/07/2024               établissement . taux ATMP=2.23% | salarié . cotisations . ATMP=66.9€/mois | taux minimum=0.46% | salarié . cotisations=1721.8274999999999€/mois | à payer avant impôt=2352.8525€/mois
   SAL_taux_saisi@01/07/2024    établissement . taux ATMP=3.5000000000000004% | salarié . cotisations . ATMP=105.00000000000001€/mois
   AE_BNC@01/07/2024            taux service BNC=21.1% | cotisations=211.00000000000003€/mois | dirigeant . auto-entrepreneur . cotisations et contributions=213.00000000000003€/mois | dirigeant . auto-entrepreneur . revenu net=9444€/an
   AE_BIC_service@01/07/2024    taux service BIC=21.2% | cotisations=212€/mois | revenu cotisé auto-entrepreneur=420€/an
   AE_vente@01/07/2024          taux vente restauration hébergement=12.3% | cotisations=123€/mois
   AE_CIPAV@01/07/2024          taux=21.2% | cotisations=2544€/an
   AE_DROM_BNC@01/07/2024       taux service BNC=14.1% | cotisations=141€/mois
   AE_BNC@01/12/2024            taux service BNC=21.1% | cotisations=211.00000000000003€/mois
   INDEP@01/07/2024             dirigeant . indépendant . cotisations et contributions=8020€/an | maladie=126€/an | indemnités journalières maladie=100€/an | retraite de base=3550€/an | retraite complémentaire=1400€/an | invalidité et décès=260€/an | CSG-CRDS=2468€/an | dirigeant . indépendant . assiette des cotisations=20000€/an
   INDEP_ACRE@01/07/2024        dirigeant . indépendant . cotisations et contributions=3592€/an | maladie=0€/an | retraite de base=0€/an
   INDEP_TRADER@01/12/2024      dirigeant . indépendant . cotisations et contributions=18025€/an | maladie=2168€/an | retraite de base=7100€/an | CSG-CRDS=5121€/an
```
Situations: SAL = {"date": "01/07/2024", "salarié . contrat . salaire brut": "3000 €/mois"}; AE BNC = {"date": "01/07/2024", "salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur": "oui", "entreprise . activité . nature": "'libérale'", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois", "entreprise . date de création": "01/01/2021", "dirigeant . exonérations . ACRE": "non", "établissement . commune . département . outre-mer": "non"} (BIC: nature 'artisanale' + service ou vente 'service'; vente: 'commerciale' + 'vente'; CIPAV: libérale réglementée oui, created 01/01/2019; DROM: outre-mer oui + durée overrides);
INDEP = EI / IR / commerciale / revenu professionnel 20000 €/an / created 01/01/2021 (ACRE: created 01/01/2024, ACRE oui; TRADER: 40000 €/an at 01/12/2024).

## sophon (system of record)
- Snapshots: S3 and G1 re-registered (idempotent); BEFORE tree registered as rules snapshot `G1pre_R1` (meta `work/proposals/R1/before/meta.json`).
- `revalidate S3/G1` and `S3/G1pre_R1`: same counts (BROKEN 27, REASSESS_LAW_CHANGED 36, REASSESS_RULE_CHANGED 10, RULE_CHANGED_CHECK_STILL_PASSES 15, STILL_VERIFIED 10, UNVERIFIED_NO_CHECK 11), reports byte-identical after normalising the snapshot id. No bounded article without a link.
  (The BROKEN/REASSESS statuses are inherited from T0/T1a/T1b links recorded against G0 / proposal snapshots and against the pre-July D613-4 texts; they are not caused by this commit.)
- Links added (D613-4 v.LEGIARTI000049624068, quotes extracted from the real text): R1-G1pre_R1-BIC=L0110:VERIFIED, R1-G1pre_R1-BNC=L0111:FAILED, R1-G1-BIC=L0112:VERIFIED, R1-G1-BNC=L0113:FAILED.
  BIC d) 46 300 euros 50 % 23 150 euros 21,2 % -> 21.2 VERIFIED on both snapshots; BNC e) 10 000 euros 34 % 6 600 euros 23,1 % -> library 21.1, FAILED on both snapshots = pre-existing gap.
- Reports: work/sophon/reports/R1_asof_D613-4_2024-07-17.json, work/sophon/reports/R1_evidence.json, work/sophon/reports/R1_evidence.md, work/sophon/reports/R1_report_cmd.json, work/sophon/reports/R1_revalidate_S3_G1.json, work/sophon/reports/R1_revalidate_S3_G1.md, work/sophon/reports/R1_revalidate_S3_G1_cmd.json, work/sophon/reports/R1_revalidate_S3_G1pre.json, work/sophon/reports/R1_revalidate_S3_G1pre.md, work/sophon/reports/R1_revalidate_S3_G1pre_cmd.json, work/sophon/reports/R1_verify-store.json. verify-store: 0 problems, 113 links checked.

## Pre-existing misalignment (NOT the subject of this commit, identical before/after)
D613-4 v.LEGIARTI000049624068 (in force 2024-07-01..2025-05-01) gives e) BNC 23,1 % and b) CIPAV 23,2 % (35 076 euros 34 % 23 150 euros 23,2 %); the library computes 21.1 / 21.2 at 01/07/2024 on both sides
(1000 €/mois CA -> 211 €/mois instead of 231). Also D613-6 v.LEGIARTI000049625264 shares are not transposed. These remain the main open items for the next change on the rules side.
Other open items from earlier tasks are listed in work/README.md.

## Approval
none recorded (no sign-off, ratification or approval record exists in the corpus; a merge/commit/test is not an approval).

## Tool calls
self-reported: 20 (including reads).
