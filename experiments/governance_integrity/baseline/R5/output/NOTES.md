# R5 — reverse check of commit c14ee26d0c67 (decision date 2026-10-05, law S10 legi-data 2.572.0)

Commit c14ee26d0c67bab90354db32ff1f51879ea3c5e8, Alice Dahan, authored 2026-07-06, committed 2026-07-09:
"fix: n'applique pas de plancher ni de plafond à l'abattement sur l'assiette à Mayotte".

## Verdict: UNRESOLVED (confidence medium). Approval: none recorded.

## 1. What the diff does (diff_excerpt)
File `modele-ti/règles/indépendant/cotisations-et-contributions/cotisations-et-contributions.publicodes`, rule
`indépendant . cotisations et contributions . assiette CSG-CRDS . abattement` (`valeur: 26% * revenu brut`):
the mechanism keys `plancher: 1.76% * plafond sécurité sociale . annuel` and `plafond: 130% * plafond sécurité sociale . annuel`
each receive `non applicable si: établissement . commune . département . outre-mer . Mayotte`. Nothing else changes in the two
context trees (`diff -rq`: one file). `stat.txt` lists a second file, `site/test/modele-ti/assiettes.test.ts` (+26), absent from
`diff.patch`. The rule's `références:` still cite only L136-3 (LEGIARTI000051284498) and D136-5 (LEGIARTI000049899286); no Mayotte source is added.

## 2. What the engine computes (engine_before_after)
Build OK on both trees; 298 raw / 460 parsed rules on both sides; parsed rule lists identical (floor/cap are mechanism keys, not rules).
34 situations x 25 rules (work/engine/checks_R5_mayotte.json), EI/IR, création 2015, `revenu professionnel` = `revenu brut` = RB, micro-fiscal non,
`établissement . commune . département = 'Mayotte'` vs 'Paris' vs unset. 850 cells compared, 118 differ, all in Mayotte situations
at post-reform dates (plus the unused `abattement` sub-rule at a pre-reform date).

Mayotte, artisan, date 01/06/2025 (PSS Mayotte 2 821 €/mois -> PASS 33 852 €/an; floor 1,76 % = 596, cap 130 % = 44 008):

| RB €/an | abattement before -> after | assiette sociale before -> after | cotisations before -> after | total before -> after |
|---|---|---|---|---|
| 0 | 596 -> 0 | 0 -> 0 | 406 -> 406 | 504 -> 504 |
| 1 000 | 596 -> 260 | 404 -> 740 | 434 -> 455 | 532 -> 553 |
| 2 000 | 596 -> 520 | 1 404 -> 1 480 | 501 -> 507 | 599 -> 605 |
| 2 290 | 596 -> 595 | 1 694 -> 1 695 | 521 -> 521 | 619 -> 619 |
| 2 300 … 169 000 | identical | identical | identical | identical |
| 170 000 | 44 008 -> 44 200 | 125 992 -> 125 800 | 13 092 -> 13 076 | 13 190 -> 13 174 |
| 300 000 | 44 008 -> 78 000 | 255 992 -> 222 000 | 23 518 -> 20 791 | 23 616 -> 20 889 |

Date 01/03/2026 (PSS Mayotte 3 022 -> PASS 36 264; floor 638, cap 47 143): RB 1 000: abattement 638 -> 260, assiette 362 -> 740, total 583 -> 611;
RB 300 000: abattement 47 143 -> 78 000, assiette 252 857 -> 222 000, total 25 454 -> 22 778 €/an.
PLNR (libérale non réglementée) Mayotte 2025, RB 300 000: retraite de base 8 516 -> 8 263, total 64 007 -> 61 027 €/an.
`indépendant . cotisations et contributions . CSG-CRDS` = null (non applicable) at Mayotte in BOTH trees: the carve-out only moves the
cotisations base (`assiette sociale` = `assiette CSG-CRDS` + … after the reform) and the cotisations computed on it (maladie-maternité-invalidité-décès-autonomie,
allocations familiales, retraite complémentaire, retraite de base for PLNR…). Métropole controls (Paris, and département unset): byte-identical
(floor 829 / cap 61 230 in 2025, 846 / 62 478 in 2026 still applied). Pre-reform date 01/12/2024 at Mayotte: `assiette CSG-CRDS` and
`assiette sociale` identical (the `abattement` sub-rule is only consumed by the après-réforme branch).
=> Not a HARMLESS_REFACTOR: what the engine computes changed for every post-reform Mayotte TI whose 26 % abattement is below the floor (RB < ~2 290 €/an)
or above the cap (RB > ~169 000 €/an).

## 3. What the governing text says (article_quote, S10 = S9 on all 12 articles)
- L136-3 LEGIARTI000051284498 (VIGUEUR 2025-02-28): "III.-L'assiette résultant de l'application des I et II du présent article fait l'objet d'un
  abattement de 26 %. Toutefois, cet abattement ne peut être ni inférieur à un montant plancher, fixé par décret, qui ne peut dépasser le montant
  mentionné à la dernière phrase de l' article L. 633-1 du présent code , ni supérieur à un montant plafond fixé, également par décret, à une valeur
  au moins égale au plafond annuel mentionné à l'article L. 241-3 ."
- D136-5 LEGIARTI000049899286 (VIGUEUR 2024-07-07; nota: periods from 2025-01-01 for non-agricultural TI): "I. - Le montant plancher prévu au III de
  l'article L. 136-3 est fixé à 1,76 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3.
  II. - Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale mentionné
  au premier alinéa de l'article L. 241-3."
- L131-6 LEGIARTI000048683707 (VIGUEUR 2023-12-28): "I.-Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne
  relevant pas du dispositif prévu à l'article L. 613-7 sont assises sur l'assiette définie à l'article L. 136-3."
- Negative finding: "Mayotte" occurs 0 times in the text and nota of the 12 bounded records. No bounded article states whether it applies at Mayotte.

## 4. Why UNRESOLVED and not MISMATCH / LEGITIMATE
Read on their face, L136-3 III and D136-5 make the floor and cap mandatory wherever the 26 % abattement applies, with no territorial exception; the
after-state then understates the floor and ignores the cap for Mayotte TI (that reading would give, for 2025, floor 596 €/an with the Mayotte PSS the tree
uses, or 829 €/an with the national PSS of L241-3, and cap 44 008 / 61 230 €/an -> a MISMATCH). But whether these CSS articles govern a TI established at
Mayotte at all is not decided by any bounded article: the CSS applies at Mayotte only through Mayotte-specific texts (ordonnance n° 96-1122 du
20 décembre 1996 and its decrees), and the tree already models Mayotte as a distinct regime on that basis (CSG-CRDS non applicable, separate PSS
2 821/3 022 €/mois and SMIC, separate rates, 50 % abattement on AF and maladie additionnelle, 24-month exemption, with Urssaf "Taux de cotisations -
Travailleur indépendant à Mayotte" and a CSSM leaflet as references). If that regime excludes the floor/cap, the commit is legitimate; the commit cites
no source and the decisive texts are outside the set. I therefore abstain: UNRESOLVED, medium. Missing: the Mayotte applicability provisions
(ordonnance 96-1122 and decrees; LFSS 2024 art. 18 Mayotte provisions), L241-3 and the Mayotte PSS text, L633-1 (last sentence), the maintainers' source,
and the commit's own test file.

## 5. Side observations for the maintainers (not scored as the verdict)
1. Before the change the floor/cap at Mayotte were computed on the Mayotte PSS (596 / 44 008 €/an in 2025), while D136-5 refers to the L241-3 national
   plafond (829 / 61 230 €/an): the before-state was not literally D136-5 either, if D136-5 applies there.
2. The changed rule's `références` (L136-3, D136-5) now contradict its own Mayotte behaviour; a Mayotte source should be cited on the rule.
3. The 26 % abattement is kept at Mayotte although CSG-CRDS (the contribution whose base L136-3 defines) is non applicable there: a combination the
   bounded text does not describe; needs the Mayotte texts.
4. No proposal was made: nothing in the bounded set anchors either direction.

## 6. Files
work/engine/make_checks_R5.mjs, checks_R5_mayotte.json, results_R5_{parent,after}_mayotte.jsonl, log_R5_*_mayotte.txt, diff_R5_mayotte.txt,
table_R5_mayotte.txt, list_R5_context_*.json, make_answer_R5.mjs (quotes verified as exact substrings of articles.json); work/law/S10_index.json + S10_texts.md;
work/notes/R5_findings.md.
