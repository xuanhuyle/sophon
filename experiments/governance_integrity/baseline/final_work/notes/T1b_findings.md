# T1b findings (decision date 2024-07-17, law S3 legi-data 2.381.0, rules G1 2a0e452617fc 2024-07-16, modele-social 2.1.0)

## Law delta S1 -> S3 (work/law/compare_snapshots.mjs; S3 kept in work/law/S3_index.json + S3_texts.md)
- D136-5 LEGIARTI000049899286 NEW (was missing), créé par décret n°2024-688 du 5 juillet 2024 art. 1 (JORF 2024-07-06), in force 2024-07-07:
  plancher abattement 1,76 % PASS annuel, plafond 130 % PASS annuel.
- D621-2 LEGIARTI000046714747 -> LEGIARTI000049904592 (2024-07-07, décret 2024-688 art. 2): maladie reduced rate < 3 PSS: nul < 20 %;
  1,5 % @40 %; 4 % @60 %; 6,5 % @110 %; 7,7 % @200 %; 8,5 % @300 % (linear formulas, a = assiette L131-6). Above 3 PSS: taux de base (L621-3/D621-1, outside set).
- D633-3 LEGIARTI000041967101 -> LEGIARTI000049904636 (2024-07-07, art. 3): 17,15 % within PSS; 0,72 % on total (was 0,60 %).
- L131-6 LEGIARTI000048683707 / L136-3 LEGIARTI000048683641 unchanged since S0 (LOI 2023-1250 art. 18, 2023-12-28).
- **`nota` field matters**: L131-6/L136-3/L613-7 nota = "VII de l'article 18 de la loi 2023-1250 ... périodes courant à compter du 1er janvier 2025";
  D136-5/D621-2/D633-3 nota = "article 6 du décret 2024-688 ... périodes courant à compter du 1er janvier 2025". ALWAYS read `nota` (compare script prints text only — TODO add nota).
- D613-4 LEGIARTI000049624068 (VIGUEUR_DIFF 2024-07-01 -> 2025-05-01, décret 2024-484 art. 1 2°): rows b) 23,2 % (was 21,2) and e) 23,1 % (was 21,1); a 12,3 / c 6 / d 21,2 unchanged.
  Later versions still text-less: LEGIARTI000049624097 (2025-01-01), LEGIARTI000049624125 (2026-01-01).
- D613-6 LEGIARTI000049625264 (ABROGE_DIFF 2024-07-01 -> 2025-01-01, art. 2 2°): b) maladie 9,30 / espèces 0,90 / ID 1,40 / VB1 23,45 / VB2 5,35 / RC 25,60 / CSG 34,00;
  e) maladie 3,60 / ID 3,70 / VB 50,75 / RC 7,85 (new line) / CSG 34,10; a+d and c unchanged (RC 16,50 % for a/d). Next: LEGIARTI000049625405 (2025-01-01), …445 (2026-01-01) text-less.
  => G1 auto-entrepreneur rules (taux service BNC 21,1 %, cotisations CIPAV . taux 21,2 %, RCI constants, ACRE/DROM derived) are OUT OF DATE from 07/2024. Not in T1b scope; T1a proposal notification `taux à confirmer` was right. Expect a task on this.

## Rules G1 vs G0 (HISTORY.txt): no indépendant change since 2024-04-05 (b18e1737); AE: distribution des cotisations added 2024-06-26 (ffab9503), links 2024-07-16. Reform NOT in G1.

## Decisions T1b (details in output/answer.json of T1b)
- Branch date `01/2025` (nota), not 07/2024 (consolidation date). At 01/12/2024 proposal == G1; change visible at 01/06/2025.
- Transposed: 26 % abattement + floor 1,76 % PSS + cap 130 % PSS on `assiette des cotisations`; CSG assiette = assiette des cotisations (no add-back);
  maladie taux progressif points 20/40/60/110/200/300 -> 0/1,5/4/6,5/7,7/8,5; retraite de base 17,87 % (17,15+0,72) + `taux déplafonné` 0,72 %.
- Abstained: pre-abattement income lines (`avant abattement` = G1 sans plancher placeholder), IS/dividends (L136-3 II), maladie > 3 PSS (notification added),
  assiette minimale . maladie, début activité forfaitaire bases, ACRE threshold base, PSS 2025, rounding.
- Classification: direct AFFECTED (assiette, CSG assiette, maladie taux progressif/total, retraite de base + taux); indirect AFFECTED (totals, CSG, RC, ID, IJ, AF);
  NEEDS_REVIEW (exonérations/ACRE, début activité, déduction tabac revenus déduits, assiette minimale . maladie); rest UNAFFECTED.

## Engine facts learned
- `plancher:`/`plafond:` and `unité: €/an` on a rule defined as `plafond sécurité sociale * x %` convert €/mois -> €/an correctly (816.0768 = 1,76 % x 46 368).
- `taux progressif`: below first plafond -> first taux; above last -> last taux; linear between (verified 0 % at 1 184, 4,19 % at 29 600, 8,02 % at 111 000, 8,5 % at 239 722).
- Comparison `assiette des cotisations > seuil` with seuil `unité: €/an` works for notifications. `variations` inside a child rule with nested `taux progressif` builds fine.
- `début activité` uses `contexte:` to override `assiette des cotisations` -> abattement not applied to forfaitaire bases (intended, flagged).
- run_checks.sh handles unknown rules per-rule (error field); undefined in results = rule absent in that tree.
- Trader values G1 (any 2024/2025 date): assiette 40 000; maladie 5,92 % / 2 168; RB 7 100; RC 2 800; ID 520; IJ 200; AF 0; CSG assiette 52 788; CSG 5 121; cotis 12 788; total 18 025.
  Proposal 2025: 29 600; 4,19 % / 1 092; 5 290; 2 072; 385; 148; 0; 29 600; 2 871; 8 987; 11 974.

## TO DO next
1. If a new rules pin implements the reform: compare its `assiette des cotisations` / CSG / maladie / retraite de base against these texts (dates 01/2025, 26 %, 1,76 %, 130 %, D621-2 points, 0,72 %) — and check what it chose for the pre-abattement lines.
2. AE side: D613-4 b/e 23,2/23,1 % from 2024-07-01 and D613-6 shares — check G1+ rules; T1a to-do list still applies (ACRE 50 %, DROM ceil10 fractions, RCI 16,50 % share).
3. Add `nota` printing to work/law/compare_snapshots.mjs. Watch for D621-1 / L621-3 (base rate), L633-1 (minimum base), D131-6-1 wording vs abattue base, PSS 2025.
4. Still open from T0/T1a: D632-1 floor mismatch; D613-4 c) meublés; D613-5 conjoint; D756-5 II cap.
