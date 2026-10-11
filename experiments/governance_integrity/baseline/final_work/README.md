# work/ — persistent engineer's directory (carried to later tasks)

Layout
- law/S0_index.json, law/S0_texts.md : S0 CSS snapshot (legi-data 2.360.0, 2024-05-25) — version/modification index + full texts.
- law/S1_index.json, law/S1_texts.md : S1 snapshot (legi-data 2.361.0, 2024-06-01), same format.
- law/S3_index.json, law/S3_texts.md : S3 snapshot (legi-data 2.381.0, 2024-07-17). NOTE: the compare script does not print the `nota` field — read it separately (it carries the application dates).
- law/compare_snapshots.mjs : `node work/law/compare_snapshots.mjs <new articles.json> <old_index.json> <old_texts.md> <TAG>`
    -> writes law/<TAG>_index.json + <TAG>_texts.md and prints every id/etat/date/version/lien/text change. USE THIS FIRST on a new snapshot.
- engine/run_checks.sh <rules_dir> <spec.json> [out.jsonl] : runs the organisation's engine over [{id, situation, rules}].
- engine/print_results.mjs <out.jsonl> : compact table of a results file.
- engine/checks_*.json / results_*.jsonl : every evaluation used in T0, T1a and T1b (baselines and proposals). engine/print_compact.mjs <jsonl> : compact table.
- engine/make_answer_T1a.mjs, make_answer_T1b.mjs : answer.json generators with exact-substring quote verification; T1b reads engine values from the results files (pattern to reuse).
- proposals/T0/ : D632-1 floor fix (T0-P1). proposals/T1a/ : D613-4 citation re-anchoring + `taux à confirmer` notification (T1a).
- proposals/T1b/ : reform of the indépendant base (26 % abattement, D136-5 floor/cap, D621-2 maladie points, D633-3 0,72 %) from 01/2025; apply_T1b.mjs re-applies it to any pin. Never edit inputs/.
- notes/T0_findings.md, notes/T1a_findings.md, notes/T1b_findings.md : binding table, engine pitfalls, open questions, TO-DO for the next snapshot.

Key state after T1a (2024-06-01): rules G0 unchanged; law S1 re-issued D613-4/D613-6 on 2024-06-01 with identical values and announced
text-less future versions at 2024-07-01, 2025-01-01, 2026-01-01 (ids in notes/T1a_findings.md). Abstained on those dates.

Key state after T1b (2024-07-17): rules G1 (2a0e452617fc) still pre-reform for indépendants AND out of date for auto-entrepreneurs (D613-4 b/e = 23,2/23,1 % from 2024-07-01).
Law S3: D136-5 created, D621-2 / D633-3 re-issued (décret 2024-688, in force 2024-07-07, applies to periods from 2025-01-01 per nota). Proposal T1b dated 01/2025.

Key state after R1 (2024-07-17, reverse check of commit 2a0e452617fc = G1 pin): HARMLESS_REFACTOR — one `références:` URL in `établissement . taux ATMP`;
build/list identical, 69 evaluations byte-identical before/after (engine/results_R1_before_* vs results_R1_G1_*). Method + salarié/AT-MP engine facts in notes/R1_findings.md;
answer generator engine/make_answer_R1.mjs (reads result files, verifies quotes). proposals/R1/ = reconstructed before-tree (not a proposal).
law/compare_snapshots.mjs is now v2: stores and compares `nota`; S3_texts.md regenerated with NOTA lines. Still open on the law side: D613-4 b/e 23,2/23,1 % from 2024-07-01
and D613-6 shares not in G1 (AE rules), reform 01/2025 (T1b proposal), D632-1 floor (T0-P1).

Key state after R2 (2024-09-02, reverse check of commit 1932d654cf7a, law S4 = S3 on all 12 articles): HARMLESS_REFACTOR (high) — deletion of
`privé: oui` on `… cotisations . taux ACRE` (AE). Visibility flag only: parsed 1220 -> 1227 (rule + 6 descendants now listed/evaluable, settable in
situation); 69 existing checks + ACRE checks byte-identical on public rules. Details, publicodes private-rule semantics (dist line numbers), an
evaluation-ORDER cache artifact and two pre-existing anomalies (D613-4 23,2/23,1 % since 07/2024 not in G1; `taux ACRE . service BIC` not halved =
21,2 % under ACRE) in notes/R2_findings.md. Generator engine/make_answer_R2.mjs (quotes extracted from articles.json by window = exact by construction).
law/S4_index.json + S4_texts.md added. proposals/R2/ = after-tree (G1 + the deletion), not a proposal. Still no text for D613-4/D613-6 future ids.

Key state after R3 (2024-10-19, reverse check of commit 9bb43d710094 "fix: correction des taux auto-entrepreneur DROM", rules G2 3a4091ae1caf = parent, law S5 = S4):
MISMATCH (high). The commit un-nests the four DROM replacement rules (`DROM . taux service BIC/BNC/vente/CIPAV`) that a 2024-09-02 re-indent had buried as unknown keys
inside the private `seconde période` (publicodes drops unknown rule-body keys silently -> parsed 1258 -> 1262). Before: DROM AE paid métropole rates (23.1/23.2/21.2/12.3 %);
after: 3.6/10.6/14.1 (BNC), 7.1/10.6/14.2 (CIPAV), 3.6/10.6/14.2 (SBIC), 2.1/6.2/8.2 (vente). D756-5 (1/6 or 1/3, 1/2, 2/3 of the D613-4 rates, rounded UP to 0.1)
x D613-4 v5 (23.1/23.2 since 2024-07-01) gives BNC 3.9/11.6/15.4 and CIPAV 7.8/11.6/15.5 -> still a mismatch for the two liberal categories; SBIC and vente exact.
Engine pitfalls: `durée d'activité . *` counts to the real clock (set trimestres/années civiles explicitly); see notes/R3_findings.md. Tools: engine/compare_results.mjs,
engine/make_answer_R3.mjs. law/S5_index.json + S5_texts.md added. proposals/R3 = after-tree.

Key state after R4 (2026-03-31, reverse check of commit d3e0cfe0f12d "chore: remplace la formule de la retraite de base par celle de l'Urssaf", law S9 legi-data 2.514.0):
LEGITIMATE_INDEPENDENT_CHANGE (medium). Non-CNAVPL retraite de base rewritten as a barème 17,75/17,87 % <= PSS + 0,60/0,72 % above (was 17,15 % <= PSS + 0,60/0,72 % on
the total): algebraically identical to D633-3 LEGIARTI000049904636; engine 73/81 identical, 8 differ by 1 € (rounding). CNAVPL branch moved (identical). `revenu cotisé`
now divides by taux T1 -> trimestres/pension estimates change (R351-9 etc. outside the set; 3 -> 2 trimestres at the minimum base in 2025 flagged).
REPO LAYOUT CHANGED in 2026: modele-ti + modele-commun, names without `dirigeant .`; run_checks.sh takes "dir1|dir2"; set `indépendant . revenu brut` for 2025+.
Law S9: D613-4 / D613-6 / D131-6-1 re-issued 2026-01-01 (décrets 2025-943, 2026-69), L136-3 2025-02-28 -> AE rules to re-check next. Details: notes/R4_findings.md,
law/S9_index.json + S9_texts.md, engine/make_answer_R4.mjs, engine/table_R4_rb.txt.

Key state after R5 (2026-10-05, reverse check of commit c14ee26d0c67 "fix: n'applique pas de plancher ni de plafond à l'abattement sur l'assiette à Mayotte", law S10 = S9):
UNRESOLVED (medium). `assiette CSG-CRDS . abattement` floor 1,76 % / cap 130 % PASS (D136-5) made non applicable at Mayotte -> post-reform Mayotte cotisations base
changes at RB < ~2 290 €/an and > ~169 000 €/an (118/850 cells; métropole identical; CSG-CRDS already non applicable at Mayotte). No bounded article mentions
Mayotte; applicability of L136-3/D136-5/L131-6 at Mayotte rests on ordonnance 96-1122 & decrees (outside set) -> abstained. Mayotte model of the tree, floor/cap
numbers and engine facts in notes/R5_findings.md; law/S10_index.json + S10_texts.md; engine/make_checks_R5.mjs, make_answer_R5.mjs, table_R5_mayotte.txt.
Still open: AE rules vs D613-4/D613-6/D131-6-1 2026 versions (see R4 TO DO).

Key state after M0 (2025-10-01, change maintenance, law S6 2.464.0 -> S7 2.469.0, rules G3 d6c374271727 = modele-social 10.0.0, old layout `dirigeant . auto-entrepreneur …`):
NO IN-FORCE CHANGE. Only D613-4 / D613-6 articleVersions moved: 2026-01-01 versions …624125 / …625445 became MODIFIE_MORT_NE (dateFin 2025-09-10), replaced by
LEGIARTI000052218738 / LEGIARTI000052218747 (VIGUEUR_DIFF 2026-01-01, NO TEXT, no lien). D633-3: version order swap only. 9 records byte-identical (law/M0_S6_S7_record_diff.json).
G3 matches the 2025 text exactly (24,6/23,2/21,2/12,3 %, D613-6 shares) but hard-codes unverifiable 2026 branches (BNC 26,1 %, shares, DROM 4,4/13,1/17,4, Acre 13,05 %) -> NEEDS_REVIEW, abstained.
Proposal M0 (proposals/M0, apply_M0.mjs, M0.diff): references + `… cotisations . taux 2026 à confirmer` notification (true from 01/2026) + notes; 0 numeric change (592 cells identical).
Checks: engine/checks_M0_ae.json (28) + checks_M0_acre.json (8); results_M0_*; table_M0.mjs; make_answer_M0.mjs. Notes: notes/M0_findings.md (G3 rule names, ACRE situation recipe, TO DO).
law/S6_* and S7_* added (S6 vs S5: L136-3 re-issued 2025-02-28 LEGIARTI000051284498; D613-4/D613-6 current = 2025 versions …097/…405).

Key state after M1 (2026-01-01, change maintenance, law S7 2.469.0 -> S8 2.489.0, rules still G3 d6c374271727):
RELEVANT CHANGE. D613-4 LEGIARTI000052218738 and D613-6 LEGIARTI000052218747 (décret n° 2025-943 du 8 sept. 2025, JORF 2025-09-09) are now VIGUEUR from
2026-01-01 with text + nota "périodes courant à compter du 1er janvier 2026". D613-4: only row e changes, 24,6 -> 25,6 % (a/b/c/d = 12,3/23,2/6/21,2 %, thresholds
re-indexed 89 776/42 586/31 115/52 070/23 609 €). D613-6: ALL splits change (a+d 8,80+1,25/3,15/43,45/19,75/23,60; b 10,60+0,80/1,40/24,30+5,20/30,70/27,00;
c 0+5,10/3,80/50,20/18,60/22,30; e 2,60+1,50/3,30/46,40/21,00/25,20). G3's 2026 branches (BNC 26,1 %, shares 3/3,25/44,85/17,7/31,2, DROM 4,4/13,1/17,4, Acre 13,05)
were WRONG and a/d + b shares had no 2026 branch. Proposal M1 (proposals/M1, apply_M1.mjs, M1.diff): BNC 25,6 %; shares e 4,10/3,30/46,40/21,00/25,20;
a/d 10,05/3,15/43,45/19,75/23,60; b 11,40/1,40/29,50/30,70/27,00 (merge convention: prestations en espèces -> maladie-maternité, 1°+2° D642-3 -> retraite de base);
DROM BNC 4,3/12,8/17,1 (ceil10 of 1/6,1/2,2/3 x 25,6); Acre BNC follows 12,8 %. 10 other records byte-identical (law/M1_S7_S8_record_diff.json, law/record_diff.mjs).
Engine: 48 checks x 2 trees (engine/checks_M1_*.json, results_M1_*, compare_M1_summary.txt): 153/672 cells differ, all at 01/01/2026, none at 01/12/2025.
Generator engine/make_answer_M1.mjs (whitespace-tolerant anchor quotes, exact by construction). Notes: notes/M1_findings.md (TO DO: category c 6 %, DROM Cipav
7,1 vs 7,8, Acre 2026 decree, next pin should be checked against these values). law/S8_index.json + S8_texts.md added.

Key state after M2 (2026-03-31, change maintenance, law S8 2.489.0 -> S9 2.514.0, rules G4 a61b72947fec = modele-social 10.0.1, still the OLD layout `dirigeant . …`):
RELEVANT CHANGE, one article: D131-6-1 -> LEGIARTI000053451315 (décret n° 2026-69 du 6 févr. 2026 art. 1, JORF 2026-02-08; nota: en vigueur 01/01/2026, « créations et
reprises d'entreprise intervenant à compter de cette date »). Acre exoneration of TI (hors micro-social) becomes « le quart » of the maladie/veuvage/vieillesse de base/
invalidité-décès/AF cotisations below 3/4 PSS, degressive « 0,25 E/0,25 PSS × (PSS−R) »; + ref to L131-6-5 (outside set), marins paragraph removed, 60-day filing deadline.
11 other records byte-identical (law/M2_S8_S9_record_diff.json). G4 adopted the M1 AE values (BNC 25,6 %, 2026 shares, `arrondi: oui`) and fixed DROM Cipav (7,8/11,6/15,5),
but still carries DROM BNC 2026 4,4/13,1/17,4 (re-proposed 4,3/12,8/17,1) and a new unsourced Acre Cipav 13,40 % (2026). Proposal M2 (proposals/M2, apply_M2.mjs 14 edits,
M2.diff): `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux` 25 % branch on `entreprise . date de création >= 01/01/2026`; new
`salarié . cotisations . exonérations . Acre . quotité` (outside bounded set, same article); AE `Acre . taux Acre 2026 à confirmer` notification (micro-social Acre rate
rests on a decree under L613-7 I not in the set -> abstained). Engine: 963 cells G4 vs proposal, 64 differ (checks_M2_{ti,acre26,sal}.json + M1 specs; results_M2_*).
Generator engine/make_answer_M2.mjs. Notes: notes/M2_findings.md (situations for TI and assimilé salarié, values, TO DO). law/S9_* regenerated (identical to the R4-line S9).
