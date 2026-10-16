# M1 — change maintenance, decision date 2026-01-01 (law S7 legi-data 2.469.0 → S8 legi-data 2.489.0; rules pin G3 d6c374271727)

Approval: **none recorded** (the corpus holds no sign-off, ratification or approval record; a merge, commit, package or test is not approval).

## 1. What changed in the law (S7 → S8)

Tools: `work/law/compare_snapshots.mjs` (index/text/nota/version/lien diff) and `work/law/record_diff.mjs` (field-level deep compare,
`work/law/M1_S7_S8_record_diff.json`). 12 records; **10 byte-identical** (L131-6, L136-3, L613-7, D131-6-1, D136-5, D613-5, D621-2, D632-1, D633-3, D756-5 —
same id, same text sha256, same articleVersions / lienModifications / nota). **2 changed**:

| article | S7 current | S8 current | modifying text | nota (S8) |
|---|---|---|---|---|
| D613-4 | LEGIARTI000049624097, ABROGE_DIFF, 2025-01-01 → 2026-01-01 | **LEGIARTI000052218738, VIGUEUR, 2026-01-01 → 2999-01-01** | Décret n°2025-943 du 8 septembre 2025 - art. 1 (JORF 2025-09-09) | « s'appliquent au titre des périodes courant à compter du 1 er janvier 2026 » |
| D613-6 | LEGIARTI000049625405, ABROGE_DIFF, 2025-01-01 → 2026-01-01 | **LEGIARTI000052218747, VIGUEUR, 2026-01-01 → 2999-01-01** | same decree | same nota |

The version ids were already announced (text-less, VIGUEUR_DIFF) in S7 (M0 abstained on them); S8 brings their text.

D613-4 LEGIARTI000052218738, text: « e) Travailleurs indépendants relevant à la fois de l'article L. 631-1 et du régime prévu à l'article 102 ter du code général des impôts 23 609 euros 34 % 15 582 euros **25,6 %** »
(S7 version …097: « … 10 000 euros 34 % 6 600 euros **24,6 %** »). Rows a) « 89 776 euros 71 % 26 035 euros 12,3 % », b) « 42 586 euros 34 % 28 107 euros 23,2 % »,
c) « 31 115 euros 87 % 4 045 euros 6 % », d) « 52 070 euros 50 % 26 035 euros 21,2 % »: **rates unchanged**, turnover/revenue thresholds re-indexed.

D613-6 LEGIARTI000052218747, text (all four splits change; each line now names its legal basis):
- a et d: maladie-maternité 8,80 % + *new line* prestations maladie en espèces (L621-2) 1,25 % ; invalidité-décès 3,15 % ; vieillesse de base 43,45 % ; complémentaire 19,75 % ; CSG-CRDS 23,60 % (S7: 8,90 / 3,10 / 41,80 / 16,50 / 29,70).
- b: 10,60 % + 0,80 % ; 1,40 % ; 24,30 % (1° D642-3) + 5,20 % (2° D642-3) ; 30,70 % ; 27,00 % (S7: 9,30 + 0,90 / 1,40 / 23,45 + 5,35 / 25,60 / 34,00).
- c: 0,00 % + 5,10 % ; 3,80 % ; 50,20 % ; 18,60 % ; 22,30 %.
- e: 2,60 % + 1,50 % ; 3,30 % ; 46,40 % ; 21,00 % ; 25,20 % (S7: 3,40 / 3,50 / 47,60 / 13,00 / 32,50).

Exact quotes with version ids are in `output/answer.json` (`changed_articles[*].quotes`, `rules[*].evidence`).

## 2. Rule classification (61 entries: 31 AFFECTED, 29 UNAFFECTED, 1 NEEDS_REVIEW; 51 re-examined, 10 not)

G3 (committed 2025-12-30) already carried 2026 branches that **no text supported** (flagged NEEDS_REVIEW in M0). Against the S8 text they are wrong:

| rule (prefix `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations .`) | G3 @ 01/01/2026 | law 2026 | proposal |
|---|---|---|---|
| `service BNC . taux` | 26,1 % | **25,6 %** (D613-4 row e) | 25,6 % |
| `service BNC . répartition . * . taux de répartition` | 3 / 3,25 / 44,85 / 17,7 / 31,2 | 2,60+1,50 / 3,30 / 46,40 / 21,00 / 25,20 | 4,10 / 3,30 / 46,40 / 21,00 / 25,20 |
| `service BIC . répartition . *`, `vente restauration hébergement . répartition . *` | 8,90 / 3,10 / 41,80 / 16,50 / 29,70 (no 2026 branch) | 8,80+1,25 / 3,15 / 43,45 / 19,75 / 23,60 | 10,05 / 3,15 / 43,45 / 19,75 / 23,60 |
| `service BNC Cipav . répartition . *` | 10,20 / 1,40 / 28,8 / 25,60 / 34 (no 2026 branch) | 10,60+0,80 / 1,40 / 24,30+5,20 / 30,70 / 27,00 | 11,40 / 1,40 (unchanged) / 29,50 / 30,70 / 27,00 |
| `dirigeant . auto-entrepreneur . DROM . taux service BNC` | 4,4 / 13,1 / 17,4 | D756-5: ceil10 of 1/6, 1/2, 2/3 × 25,6 % | 4,3 / 12,8 / 17,1 (medium) |
| `dirigeant . auto-entrepreneur . Acre . taux service BNC` (dependency, no edit) | 13,05 % | 50 % × 25,6 % (Acre rate itself: abstain, see §4) | 12,8 % (medium) |

Merge convention for the five-bucket model (same as G3 already used for block b in 2024/2025): « prestations maladie en espèces » → `maladie-maternité`; the two D642-3 lines → `retraite de base`.

AFFECTED through dependencies only (no edit): `… cotisations . service BNC`, `… cotisations`, `dirigeant . auto-entrepreneur . cotisations et contributions`, the five
`… cotisations . répartition . <bucket>` aggregates, `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur`, `Acre . taux service BNC`.

UNAFFECTED, **re-examined with the engine** (identical on both trees at 01/12/2025 and 01/01/2026, and quoted against the new text): `service BIC . taux` 21,2 %,
`vente … . taux` 12,3 %, `service BNC Cipav . taux` 23,2 % (rows d/a/b unchanged), their amounts, `service BNC Cipav . répartition . invalidité-décès` 1,40 %,
`protection sociale . retraite . base . cotisée . revenu auto-entrepreneur` (7 920 / 6 000 / 3 480 €/an — abattements 34/50/71 % unchanged), `DROM . taux service BIC /
vente / CIPAV`, `Acre . taux Acre` 50 %, `Acre . taux service BIC` 10,6 %, `Acre . taux vente` 6,2 %, `Acre . taux CIPAV` 13,9 %, and the switches `Acre`, `DROM`, `Cipav`,
`dirigeant . exonérations . ACRE`.

**Not re-examined** (10 entries, `not_reassessed_rules`): `dirigeant . indépendant . cotisations et contributions . {maladie (D621-2), invalidité et décès (D632-1),
retraite de base (D633-3), CSG-CRDS (L136-3/D136-5), exonérations . ACRE (D131-6-1)}`, `dirigeant . indépendant . assiette minimale . invalidité et décès` (D632-1),
`dirigeant . indépendant . assiette des cotisations` (L131-6), `bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire` (L131-6),
`salarié . cotisations . exonérations . Acre` (D131-6-1), and the un-implemented D613-5 / D136-5 / D756-5 II. Evidence: each is bound only to a record that is
byte-identical in S7 and S8 (`work/law/M1_S7_S8_record_diff.json`: same id, same text sha256, same versions/liens/nota), the rule pin is the same G3 as in M0, and the
two changed articles govern the L613-7 micro-social regime these rules do not read. Re-running them would re-test unchanged law on an unchanged tree.

NEEDS_REVIEW (gap, not a rule): D613-4 row c) « 6 % » (meublés de tourisme) and D613-6 block c have no implementing rule at G3.

## 3. Proposal (`work/proposals/M1/modele-social/règles`, diff `work/proposals/M1/M1.diff`, re-applicable with `node work/proposals/M1/apply_M1.mjs <règles>`)

Two files: `dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes` (rates, shares, `note:` per rule quoting row/block + version id, `références` to
L613-7 and to the 2025 and 2026 versions of D613-4/D613-6; stale D613-6 citation LEGIARTI000043656780 replaced) and `dirigeant/auto-entrepreneur/exonérations.publicodes`
(`DROM . taux service BNC` 2026 branches + note). `build`: 722 raw / 1427 parsed on both trees. No change before 2026.

Engine (`work/engine/checks_M1_{ae,acre,drom}.json` = 48 checks × 2 dates, `results_M1_{G3,proposal}_*.jsonl`, `compare_M1_summary.txt`): 672 cells compared,
**153 differ, all at 01/01/2026, 0 at 01/12/2025**. Key before/after (situation: EI auto-entrepreneur, CA 1 000 €/mois, métropole, création 01/01/2019, no ACRE):

| situation / rule | G3 @ 01/12/2025 | G3 @ 01/01/2026 | proposal @ 01/01/2026 |
|---|---|---|---|
| BNC `service BNC . taux` | 24,6 % | 26,1 % | **25,6 %** |
| BNC `… cotisations` / `cotisations et contributions` | 246 / 248 €/mois | 261 / 263 | **256 / 258 €/mois** |
| BNC shares (mal / inv / RB / RC / autres) | 3,4 / 3,5 / 47,6 / 13 / 32,5 | 3 / 3,25 / 44,85 / 17,7 / 31,2 | **4,1 / 3,3 / 46,4 / 21 / 25,2** |
| BNC aggregates (€/mois) | 8,364 / 8,61 / 117,096 / 31,98 / 79,95 | 7,83 / 8,4825 / 117,0585 / 46,197 / 81,432 | **10,496 / 8,448 / 118,784 / 53,76 / 64,512** |
| BNC `RCI . revenu cotisé auto-entrepreneur` | 383,76 €/an | 554,364 | **645,12 €/an** |
| BNC `retraite . base . cotisée . revenu auto-entrepreneur` | 7 920 €/an | 7 920 | 7 920 (unchanged) |
| CIPAV `service BNC Cipav . taux` / cotisations | 23,2 % / 232 €/mois | same | same |
| CIPAV shares | 10,2 / 1,4 / 28,8 / 25,6 / 34 | same | **11,4 / 1,4 / 29,5 / 30,7 / 27** |
| CIPAV aggregates (mal / RB / RC / autres) | 23,664 / 66,816 / 59,392 / 78,88 | same | **26,448 / 68,44 / 71,224 / 62,64 €/mois** |
| SBIC `service BIC . taux` / cotisations | 21,2 % / 212 €/mois | same | same |
| SBIC shares | 8,9 / 3,1 / 41,8 / 16,5 / 29,7 | same | **10,05 / 3,15 / 43,45 / 19,75 / 23,6** |
| SBIC `RCI . revenu cotisé auto-entrepreneur` | 419,76 €/an | 419,76 | **502,44 €/an** |
| VENTE `vente … . taux` / cotisations | 12,3 % / 123 €/mois | same | same |
| VENTE shares; RCI | as SBIC; 243,54 €/an | same | **10,05 / 3,15 / 43,45 / 19,75 / 23,6; 291,51 €/an** |
| BNC_ACRE `Acre . taux service BNC` (création 01/04/2025, 6 mois) | 12,3 % | 13,05 % | **12,8 %** (cotisations 130,5 → 128 €/mois) |
| DROM BNC Q8 / Q12 / Y4 `DROM . taux service BNC` | 4,1 / 12,3 / 16,4 % | 4,4 / 13,1 / 17,4 | **4,3 / 12,8 / 17,1 %** |
| DROM `taux CIPAV` / `taux service BIC` / `taux vente` (Q8) | 7,1 / 3,6 / 2,1 % | same | same |
| Acre `taux Acre` / `taux CIPAV` / `taux service BIC` / `taux vente` | 50 % / 13,9 / 10,6 / 6,2 % | same | same |

Every number above is read from the result files by `work/engine/make_answer_M1.mjs` (82 evaluation entries with situations in `answer.json`).

## 4. Abstentions / caveats

1. **Acre 2026 rate (BNC)**: L613-7 « Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une
   exonération … ». No such decree text is in the set and the 50 % `taux Acre` factor has no source in the set: 12,8 % is the rule's computation, not a value read in the law (medium).
2. **DROM 2026 BNC rates**: derived from D756-5 (« après arrondi au dixième de pour cent supérieur, à une fraction des taux … a) 1/6 … b) 1/2 … c) 2/3 »); D756-5 still cites
   « D. 131-6-1 » / « L. 133-6-8 » (pre-2018 numbering) and no text publishes the 2026 DROM rates themselves (medium).
3. **Pre-existing, untouched**: DROM Cipav 7,1 / 10,6 / 14,2 % vs ceil10(1/3, 1/2, 2/3 × 23,2 %) = 7,8 / 11,6 / 15,5 %; Acre Cipav 13,90 % without source; category c) 6 % and
   D613-5 conjoint not implemented; `Acre . taux service BNC` keeps `arrondi: 2 décimales` from 01/2026 (12,80 = 12,8, no effect).
4. **Time semantics**: « périodes courant à compter du 1er janvier 2026 » is implemented as `date >= 01/2026` on the simulation date (tree convention); declarations in
   January 2026 of December 2025 turnover are not modelled.
5. Later-dated snapshots S9/S10 present in `work/law` from other task lines were NOT used (world date 2026-01-01).

## 5. Records kept for the next change (`work/`)

`law/S8_index.json`, `law/S8_texts.md`, `law/M1_S7_S8_record_diff.json`, `law/record_diff.mjs`; `engine/checks_M1_*.json`, `results_M1_*.jsonl`, `compare_M1_summary.txt`,
`make_checks_M1.mjs`, `make_answer_M1.mjs`, `build_M1_*.json`, `list_M1_G3.json`; `proposals/M1/` (tree, `M1.diff`, `apply_M1.mjs`, README); `notes/M1_findings.md`; `README.md` updated.
