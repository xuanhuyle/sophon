# T1b — forward transposition of the self-employed contribution-base reform (decision date 2024-07-17)

Law: S3 (legi-data 2.381.0, published 2024-07-17). Rules: G1 2a0e452617fc (2024-07-16, modele-social 2.1.0). Engine: `src/publicodes_eval.mjs` (publicodes 1.10.4).
Everything below is backed by `output/answer.json` (exact-substring quotes checked by `work/engine/make_answer_T1b.mjs` against the S3 records; every engine value read from `work/engine/results_T1b_*.jsonl`).

## 1. Changed articles (S3 vs S1, `work/law/compare_snapshots.mjs`)

| Article | Version in S3 | In force | Modifying text | What it says |
|---|---|---|---|---|
| L131-6 | LEGIARTI000048683707 (unchanged since S0) | 2023-12-28 | LOI n°2023-1250 du 26 décembre 2023 - art. 18 (V) | cotisations "assises sur l'assiette définie à l'article L. 136-3"; épargne salariale deducted; revenus de remplacement included |
| L136-3 | LEGIARTI000048683641 (unchanged since S0) | 2023-12-28 | same | I: BIC/BNC base (produits − charges, CGI 36-40 / 93); II: IS base (rémunération + dividendes > 10 %); III: "abattement de 26 %" with a floor and a cap "fixé par décret"; IV: micro outside L613-7 |
| D136-5 | LEGIARTI000049899286 (NEW — missing in S0/S1) | 2024-07-07 | Décret n°2024-688 du 5 juillet 2024 - art. 1 [CREE] | floor "1,76 % de la valeur annuelle du plafond", cap "130 % de la valeur annuelle du plafond" |
| D621-2 | LEGIARTI000049904592 (was LEGIARTI000046714747) | 2024-07-07 | décret 2024-688 art. 2 | maladie-maternité reduced rate under 3 PSS: nul < 20 % PSS; T1 1,5 % @ 40 %; T2 4 % @ 60 %; T3 6,5 % @ 110 %; T4 7,7 % @ 200 %; T5 8,5 % @ 300 %; "a est l'assiette, telle que définie à l'article L. 131-6" |
| D633-3 | LEGIARTI000049904636 (was LEGIARTI000041967101) | 2024-07-07 | décret 2024-688 art. 3 (V) | 17,15 % within the PSS; 0,72 % on the whole base (was 0,60 %) |
| D613-4 / D613-6 | LEGIARTI000049624068 / LEGIARTI000049625264 | 2024-07-01 | décret 2024-484 art. 1 2° / art. 2 2° | out of T1b scope (micro-social): rows b) 23,2 % and e) 23,1 %; D613-6 shares for b)/e) changed — recorded for the next task |

**From when they apply.** Not in the article texts but in their `nota` field: L131-6/L136-3 — "Conformément au VII de l'article 18 de la loi n° 2023-1250 … au titre des périodes courant à compter du 1er janvier 2025"; D136-5/D621-2/D633-3 — "Conformément à l'article 6 du décret n° 2024-688 … au titre des périodes courant à compter du 1er janvier 2025". Hence the proposal's branches are `date >= 01/2025` (not the 2024-07-07 consolidation date). Unchanged: L613-7, D131-6-1, D613-5, D632-1, D756-5. Missing: none.

## 2. Classification (details and evidence per rule in `answer.json › rules`)

- **AFFECTED, direct** (own definition changed by the texts; confidence high): `dirigeant . indépendant . assiette des cotisations` (26 % abattement, floor, cap); `… CSG-CRDS . assiette` (same L136-3 base, no add-back of the cotisations); `… maladie . taux progressif` (+ `. assiette`, `maladie`, `maladie . total`); `… retraite de base` (+ `. taux`).
- **AFFECTED, indirect** (own text unchanged, output follows the new base; high unless noted): `cotisations et contributions`, `. cotisations`, `. CSG-CRDS` (+ déductible / non déductible), `. non déductibles`, `. retraite complémentaire`, `. invalidité et décès` (+ `. assiette`, D632-1 unchanged), `. indemnités journalières maladie`, `. allocations familiales` (medium; no change at 40 000, change at 150 000), `. maladie domiciliation fiscale étranger` (medium).
- **NEEDS_REVIEW** (medium unless noted): `. exonérations`, `. exonérations . ACRE` (+ `. taux`, `. prorata sur l'année`) — D131-6-1 compares "le revenu ou la rémunération" to 3/4 PSS, the G1 rule compares `assiette des cotisations` (now abattue); `. début activité` (+ forfaitaire bases, article outside the set); `. déduction tabac . revenus déduits` (low); `assiette minimale . maladie` (40 % PSS floor from an article outside the set vs the new nul rate under 20 % PSS).
- **UNAFFECTED** (high unless noted): `. PSS proratisé`, `. formation professionnelle`, `. PCV`, `. contributions spéciales`, `. régularisation`, `. déduction tabac`, `. maladie . taux progressif avant 2022`, `. maladie . réduction supplémentaire`, `. indemnités journalières maladie . taux` / `. assiette`, CSG-CRDS rates and revenus de remplacement, `. retraite complémentaire . plafond`, `. exonérations . {ZFU, âge, pension invalidité, DROM}` (medium), `assiette minimale`, `assiette minimale . retraite` (medium: L136-3 III only uses L633-1 as a cap on the abattement floor), `assiette minimale . retraite . en 2022`.

## 3. Proposal (`work/proposals/T1b/modele-social/règles`, diff `T1b.diff`, script `apply_T1b.mjs`)

One file: `dirigeant/indépendant.publicodes`. All branches `date >= 01/2025`; before that every rule reproduces G1 (checked at 01/06/2024 and 01/12/2024).
1. `assiette des cotisations` = `avant abattement` − `abattement forfaitaire`; abattement = 26 % × `avant abattement`, `plancher: montant plancher` (= PSS × 1,76 %, €/an), `plafond: montant plafond` (= PSS × 130 %); plancher 0 kept. `avant abattement` provisionally = G1 `sans plancher` (revenu professionnel + cotisations facultatives déductibles) — placeholder, see abstentions.
2. `CSG-CRDS . assiette` = `assiette des cotisations` (existing deductions revenus étrangers / IJSS imposable kept).
3. `maladie . taux progressif`: points 20/40/60/110/200/300 % PSS → 0/1,5/4/6,5/7,7/8,5 % (publicodes linear interpolation = the formulas of 2°-6°); new notification `maladie . taux au-delà de 3 PASS à confirmer` (rate above 3 PSS not in the corpus; G1 structure 5 PSS / 6,50 % kept).
4. `retraite de base . taux` 17,75 % → 17,87 % (17,15 + 0,72); new `taux déplafonné` 0,6 % → 0,72 %.
5. Note on `assiette minimale . maladie` (no value change).
Build OK: proposal 641 raw / 1228 parsed (G1 641 / 1220).

## 4. Before / after — trader EI, IR, commerciale, revenu professionnel 40 000 €/an (PSS 3 864 €/mois = 46 368 €/an)

| Rule | G1 2024-12-01 | Proposal 2024-12-01 | G1 2025-06-01 | Proposal 2025-06-01 |
|---|---|---|---|---|
| assiette des cotisations | 40 000 | 40 000 | 40 000 | **29 600** (abattement 10 400) |
| maladie . taux progressif | 5,92 % | 5,92 % | 5,92 % | **4,19 %** |
| maladie | 2 168 | 2 168 | 2 168 | **1 092** |
| retraite de base (taux 17,75 → 17,87 %) | 7 100 | 7 100 | 7 100 | **5 290** |
| retraite complémentaire | 2 800 | 2 800 | 2 800 | 2 072 |
| invalidité et décès | 520 | 520 | 520 | 385 |
| indemnités journalières maladie | 200 | 200 | 200 | 148 |
| CSG-CRDS . assiette | 52 788 | 52 788 | 52 788 | **29 600** |
| CSG-CRDS | 5 121 | 5 121 | 5 121 | **2 871** |
| cotisations | 12 788 | 12 788 | 12 788 | 8 987 |
| cotisations et contributions (total) | 18 025 | 18 025 | 18 025 | **11 974** |

The minimal situation of the task (without `date de création`, `auto-entrepreneur: non`, `ACRE: non`) gives the same values (check `TRADER_40k_minimal`). Floor and cap (2025-06-01): revenu 2 000 → abattement 816 (floor 816,08), base 1 184, maladie rate 0 %; revenu 0 → base 0; revenu 300 000 → abattement 60 278 (cap 60 278,40), base 239 722, maladie rate 8,5 % and the >3 PSS notification fires; revenu 150 000 → base 111 000, maladie rate 8,02 %.

## 5. Abstentions (why no number)

- Composition of the pre-abattement base (L136-3 I 1°/2° via CGI 36-40 / 93; L131-6 I épargne salariale / revenus de remplacement): the text does not say whether the social contributions are deductible charges; `avant abattement` keeps the G1 definition as a placeholder.
- IS branch (L136-3 II, dividends > 10 % of the reference amount): not transposed.
- Maladie rate above 3 PSS (L621-3 / D621-1 outside the set); minimum maladie base (40 % PSS, article outside the set); forfaitaire first-year bases (19 % / 40 % PSS); ACRE threshold base (D131-6-1 "revenu ou rémunération"); 2025 PSS (not in the corpus — floor/cap are coded as shares of `plafond sécurité sociale`); rounding of the abattement (none stated; proposal rounds to the euro).
- D613-4 / D613-6 versions in force 2024-07-01 (micro-social, out of scope): no edit here.

## 6. Approval

None recorded — the corpus contains no sign-off, ratification or approval of any kind (the G1 commits and the regression fixtures are not approvals).
