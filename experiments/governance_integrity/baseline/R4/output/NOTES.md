# R4 — reverse check of commit d3e0cfe0f12dcade20d5d1ea8bc51fee609bbc06 (decision date 2026-03-31)

"chore: remplace la formule de la retraite de base par celle de l'Urssaf" (Alice Dahan, authored 2026-02-13, committed 2026-03-30).
Law: snapshot S9 (legi-data 2.514.0). Rules: `inputs/diffs/R4_d3e0cfe0f12d/context_parent_tree` vs `context_tree_after`
(modele-ti + modele-commun). Verdict: **LEGITIMATE_INDEPENDENT_CHANGE** (confidence medium). Approval: **none recorded**.

## 1. What the commit changes (diff.patch, 3 rule files; tests, i18n and snapshots not provided)

1. `indépendant . cotisations et contributions . cotisations . retraite de base` (artisans, commerçants, PLNR au régime général):
   - before: `somme: [tranche 1, tranche 2]` with tranche 1 = 17.15 % (8.23/8.73 % CNAVPL) x base capped at PSS, tranche 2 = 0.60 %
     (0.72 % après réforme; 1.87 % CNAVPL capped at 5 PSS) x the whole base; each tranche `arrondi: oui`, parent `arrondi: oui`;
   - after: `barème` on `assiette` with `multiplicateur: PSS proratisé`: `taux T1` (17.75 %, 17.87 % après réforme) up to 1 PSS,
     `taux T2` (0.60 / 0.72 %) above; rounded once by the parent. New public rules `assiette`, `taux T1`, `taux T2`; removed
     `tranche 1`, `tranche 2`, `tranche 1 . assiette`, `tranche 1 . taux`, `tranche 2 . assiette`, `tranche 2 . taux`.
   - comment added by the author: "Le code de la sécurité sociale décrit un calcul identique à celui des PLR (taux T1 sur la part de
     l'assiette < PASS + taux T2 sur toute l'assiette) mais l'Urssaf calcule différemment (taux T2 sur la part de l'assiette > PASS
     uniquement) et a insisté pour que l'on reprenne leur méthode."
2. New `indépendant . profession libérale . CNAVPL . retraite de base` (tranche 1 = 8.23/8.73 % x base capped at PSS, tranche 2 = 1.87 %
   x base capped at 5 PSS, abattement participation CPAM CARMF) — the former CNAVPL branch moved out of the generic rule; the CNAVPL
   points rules now point to it.
3. `protection sociale . retraite . base . revenu cotisé` = retraite de base / `taux de cotisation`, where `taux de cotisation` is the
   CNAVPL tranche 1 rate (8.23/8.73 %) or `taux T1` (17.75/17.87 %) — before it divided by `tranche 1 . taux` (17.15 % for non-CNAVPL).
   Documentation changes (525 -> 557 points, références, long `note` removed).

Build: raw 296 / parsed 446 -> raw 295 / parsed 449 (6 public rules removed, 9 added; see answer.json).

## 2. The governing text (bounded set)

Only **D633-3** is engaged. S9 record LEGIARTI000049904636, VIGUEUR, in force 2024-07-07:
> "I.-Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %."
> "II.-Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %."
nota: applies "au titre des périodes courant à compter du 1er janvier 2025" (décret 2024-688 art. 6) — matches the library branch
`après réforme: date >= 01/2025`.

Algebra: with T1 = 17.15 %, T2 = 0.72 %, A = base, P = PSS: text amount = T1·min(A,P) + T2·A.
Library after = (T1+T2)·min(A,P) + T2·max(A−P,0) = T1·min(A,P) + T2·min(A,P) + T2·(A − min(A,P)) = T1·min(A,P) + T2·A. **Identical**;
the Urssaf presentation (17.87 % / 0.72 %) and the CSS wording (17.15 % / 0.72 %) are the same function. The author's comment that the
two "calculate differently" is wrong on the amount; the only possible difference is rounding, which D633-3 does not regulate.

Pre-2025 rates (library 17.75 % = 17.15 + 0.60, 0.60 %): the version in force then, LEGIARTI000041967101 (2020-05-25 -> 2024-07-07), has
no text in S9 (only the current version's text is given) -> **abstain**.

Everything else the commit touches rests on articles outside the bounded set: D642-3/D642-4 (CNAVPL rates and 5 PSS cap), R351-9,
R634-1, D634-1 (revenu cotisé, 150 SMIC h per trimestre), D633-2 (assiette minimale retraite = 450 SMIC h), L161-17-3 (pension),
and the Urssaf "Retraite de base" page cited in `références`.

## 3. Engine evidence (work/engine/checks_R4_rb.json: 81 checks x 25 rules; results_R4_parent_rb.jsonl vs results_R4_after_rb.jsonl)

Situations: EI, IR, création 01/01/2015 (PLNR -> CNAVPL/Cipav) or 01/01/2020 (PLNR -> régime général), `indépendant . revenu
professionnel` = `indépendant . revenu brut` = 0 … 300 000 €/an, micro-fiscal non; artisan, PLNR, Cipav, médecin S1 (CARMF),
commerçant débit de tabac (déduction 5 000 €/an); dates 01/12/2024 (PSS 3 864 €/mois), 01/06/2025 (3 925), 01/03/2026 (4 005).
Full table: work/engine/table_R4_rb.txt.

| check | `retraite de base` before -> after | revenu cotisé | trimestres | pension estimate |
|---|---|---|---|---|
| AC_0@24 (base floored to 5 243) | 930 -> **931** €/an (round(899.17)+round(31.46) vs round(930.63)) | 5 423 -> 5 245 | 3 -> 3 | 226 -> 219 €/mois |
| AC_6800@24 | 1 207 -> 1 207 | 7 038 -> 6 800 | **4 -> 3** | 293 -> 283 |
| AC_20000@24 | 3 550 -> 3 550 | 20 700 -> 20 000 | 4 -> 4 | 863 -> 833 |
| AC_100000@24 (base 100 000 > PSS 46 368) | 8 552 -> 8 552 | 3 864 €/mois (capped) both | 4 | 1 932 both |
| AC_0@25 (base floored to 5 346 = 450 SMIC h) | 955 -> 955 | 5 569 -> 5 344 | **3 -> 2** | 232 -> 223 |
| AC_60001@25 (base 44 401) | 7 935 -> **7 934** | 46 268 -> 44 398 | 4 | 1 928 -> 1 850 |
| AC_100000@25 (base 74 000, PSS 47 100) | 8 611 -> **8 610** | capped | 4 | 1 963 both |
| AC_300000@25 (base 238 770) | 9 797 -> 9 797 | capped | 4 | 1 963 both |
| CIPAV_100000@25 (CNAVPL) | 5 496 -> 5 496 (4 112 + 1 384) | capped | 4 | 31 -> 31; points 564.9 -> 564.9 |
| MED_60001@25 (CARMF S1) | 4 706 -> 4 706; total cotisations 7 374 both | | | |
| TABAC_60001@24 (base 55 001 after déduction) | 8 282 -> 8 282 | capped | 4 | |

Summary: `retraite de base` identical in 73/81 checks, ±1 € in 8 (all non-CNAVPL; rounding of each tranche before vs once after);
all 30 CNAVPL checks identical on retraite de base, tranches, points and pension; `revenu cotisé` differs in 30 checks, `trimestres` in 4,
pension estimate in 29, total `cotisations` in the 8 rounding cases. `taux T1` = 17.75 % (2024) / 17.87 % (2025, 2026) where
`tranche 1 . taux` was 17.15 %.

Worked check against D633-3 (AC_100000@25): 17.15 % x 47 100 = 8 077.65; 0.72 % x 74 000 = 532.80; total 8 610.45 -> 8 610 (after) ;
before gave 8 078 + 533 = 8 611. Both within rounding of the text; the text fixes no rounding rule.

## 4. Classification

- Not HARMLESS_REFACTOR: the engine's outputs changed — `taux T1` (published rate), `retraite de base` by 1 € in 10 % of cases, and
  every non-CNAVPL `revenu cotisé`, `trimestres` and pension estimate below the PSS (snapshot file in the stat changed accordingly).
- Not MISMATCH on the bounded set: after the change the cotisation equals the D633-3 amount (same function, rounding only);
  `taux T1 = 17.87 %` is 17.15 + 0.72 and the text's two components are recoverable; no bounded rule computes anything D633-3 forbids.
- Not UNRESOLVED: D633-3 settles the only bounded question (2025+). The unsettled parts are outside the set, listed in answer.json.
- LEGITIMATE_INDEPENDENT_CHANGE: a deliberate implementation choice (Urssaf presentation, adopted "at the Urssaf's insistence"),
  which the text does not forbid, whose downstream effects (revenu cotisé, trimestres, pension) rest on articles outside the set.
  Confidence medium: high on D633-3 itself, but the pre-2025 rates are unverifiable and the trimestres regression at the minimum base
  (3 -> 2 in 2025) cannot be adjudicated here.

## 5. Flags for the maintainers (outside the bounded set, not part of the verdict)

1. At the assiette minimale retraite (450 SMIC h, 5 346 € in 2025) the after tree validates **2 trimestres instead of 3** in 2025:
   round(17.87 % x 5 346) = 955; 955 / 17.87 % = 5 344 < 5 346 = 450 h. The minimum base exists to validate 3 trimestres (D633-2,
   R351-9 — outside the set). Dividing an already-rounded cotisation by the rate loses up to 0.5 € / rate.
2. `revenu cotisé` for non-CNAVPL is now cotisation / 17.87 %, i.e. the whole cotisation (including the 0.72 % part above the PSS)
   is divided by the plafonnée rate; R351-9/D634-1 (outside the set) should be checked for which rate is meant.
3. The author's comment about CSS vs Urssaf is inaccurate: the two formulations are algebraically identical.
4. `CNAVPL . retraite de base . tranche 2 . taux` (1.87 %) is defined but unused (the produit hard-codes 1.87%).
5. Pre-2025 D633-3 text (LEGIARTI000041967101) is not in the corpus; 17.75 / 0.60 % remain unverified.

Approval record: none in the corpus (commit, tests and snapshot updates are not approvals).
