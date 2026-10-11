# M1 findings (decision date 2026-01-01, law S7 legi-data 2.469.0 (2025-10-01) → S8 legi-data 2.489.0 (2026-01-01), rules G3 d6c374271727 = same pin as M0)

## Law delta S7 -> S8 (work/law/S8_*, M1_S7_S8_record_diff.json)
- D613-4: current = LEGIARTI000052218738 (VIGUEUR 2026-01-01 → 2999-01-01), décret n° 2025-943 du 8 sept. 2025 art. 1 (JORF 2025-09-09, cible 2025-09-10),
  nota "périodes courant à compter du 1er janvier 2026". …097 (2025) now MODIFIE. Rows: a) 89 776 € / 71 % / 26 035 € / 12,3 % ; b) 42 586 / 34 % / 28 107 / 23,2 % ;
  c) 31 115 / 87 % / 4 045 / 6 % ; d) 52 070 / 50 % / 26 035 / 21,2 % ; e) 23 609 / 34 % / 15 582 / **25,6 %** (was 24,6 %). Only row e's rate changed.
- D613-6: current = LEGIARTI000052218747 (same decree/nota). Splits (maladie + espèces / inv-décès / base / compl / CSG-CRDS):
  a+d 8,80 + 1,25 / 3,15 / 43,45 / 19,75 / 23,60 ; b 10,60 + 0,80 / 1,40 / 24,30 + 5,20 / 30,70 / 27,00 ; c 0,00 + 5,10 / 3,80 / 50,20 / 18,60 / 22,30 ;
  e 2,60 + 1,50 / 3,30 / 46,40 / 21,00 / 25,20. Every line now cites its article (L621-1, L621-2, L632-1/L644-2, D633-3/D642-3, L635-1/L644-1, L136-3).
- 10 other records byte-identical (L131-6, L136-3, L613-7, D131-6-1, D136-5, D613-5, D621-2, D632-1, D633-3, D756-5).
- The 2026 values G3 carried (BNC 26,1 %; shares 3/3,25/44,85/17,7/31,20; DROM 4,4/13,1/17,4; Acre 13,05) match NO text in S6/S7/S8 — they were wrong.

## Proposal M1 (proposals/M1: tree, M1.diff 320 lines, apply_M1.mjs = 19 anchored replacements, run ONCE on a fresh G3 copy)
- cotisations-et-contributions.publicodes: service BNC . taux 2026 = 25.6% ; BNC shares 2026 = 4.10/3.30/46.40/21.00/25.20 ; BIC + vente shares -> variations
  (01/2026: 10.05/3.15/43.45/19.75/23.60, sinon old constants) ; Cipav shares 2026 = 11.40/(1.40 unchanged)/29.50/30.70/27.00 ; notes + références (L613-7, D613-4/D613-6
  2025 and 2026 ids) ; stale LEGIARTI000043656780 removed.
- exonérations.publicodes: DROM . taux service BNC 2026 = 4.3/12.8/17.1 (ceil10 of 1/6, 1/2, 2/3 x 25,6) + note. Acre arrondi left (12.80 = 12.8).
- Merge convention (already G3's for block b): prestations maladie en espèces -> maladie-maternité ; 1° + 2° D642-3 -> retraite de base.
- build 722/1427 both trees. 672 cells: 153 differ, all @01/01/2026; 0 @01/12/2025 (compare_M1_summary.txt).

## Engine values worth remembering (CA 1 000 €/mois)
- BNC 2026 proposal: taux 25,6 %, cotisations 256 €/mois (+ CFP = 258), RCI revenu cotisé 645,12 €/an (G3 554,364; 2025 383,76), retraite base revenu 7 920 €/an (unchanged).
- Cipav 23,2 % / 232 €/mois unchanged; shares change -> aggregates 26,448 / 68,44 / 71,224 / 62,64 €/mois.
- SBIC 21,2 % / 212 ; VENTE 12,3 % / 123 unchanged ; RCI 502,44 / 291,51 €/an (2025: 419,76 / 243,54).
- Acre BNC 12,8 % (G3 13,05 ; 2025 12,3) ; Acre BIC 10,6 ; vente 6,2 ; Cipav 13,9 (constant) ; taux Acre 50 %.
- DROM BNC Q8/Q12/Y4 4,3/12,8/17,1 (G3 4,4/13,1/17,4 ; 2025 4,1/12,3/16,4) ; DROM Cipav 7,1 / BIC 3,6 / vente 2,1 unchanged.
- `DROM . taux service BNC` replaces `service BNC . taux` even in the Cipav/BIC/vente DROM situations (the replaced rule evaluates though not applicable) — harmless.

## Method notes
- compare_snapshots.mjs then record_diff.mjs (new, generic: old.json new.json OLDTAG NEWTAG out.json). make_checks_M1.mjs derives specs from the M0 ones (dates
  01/12/2025 + 01/01/2026 + the 5 aggregate répartition rules). make_answer_M1.mjs: whitespace-tolerant anchor quotes (regex, keeps the raw substring) — reuse Q().
- Output size: 82 evaluation entries x long quotes -> answer.json 265 KB; fine, but trim law_basis if a limit appears.

## TO DO when the next snapshot / pin arrives
1. New pin: check whether upstream fixed the 2026 branches (expect 25,6 %, the shares above, DROM 4,3/12,8/17,1, Acre 12,8 or a decree-fixed Acre rate). Diff against proposals/M1.
2. Law: watch for a decree fixing the Acre (exoneration-period) global rate under L613-7 al. 2, for D756-5 renumbering/DROM rates, for category c) (6 %) implementation,
   for D613-5 conjoint, for L136-3/D136-5 changes (TI side), and for any 2027 VIGUEUR_DIFF versions of D613-4/D613-6 (abstain until text).
3. Pre-existing still open: DROM Cipav 7,1/10,6/14,2 vs 7,8/11,6/15,5; Acre Cipav 13,90 source; D632-1 floor (T0-P1); L136-3 III / D136-5 at the pin in use (T1b/R5 lines).
4. S9/S10 in work/law are 2026-03/2026-10 snapshots from the R4/R5 lines — usable only when the world date allows.
