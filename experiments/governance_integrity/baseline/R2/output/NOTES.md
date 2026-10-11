# R2 — reverse check of commit 1932d654cf7a (decision date 2024-09-02)

## The change
`docs(auto-entrepreneur): Rend publique la règle taux ACRE des auto-entrepreneurs` (Alice Dahan, 2024-09-02). One file, one deletion:
the line `privé: oui` under `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE`
(modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes). No formula, constant, date or applicability condition is touched.

Before-tree caveat: the patch's `a` side (blob a061b547e, 2-space indentation, hunk @@ -62) is not the G1 file (blob 8914c3ae, 4-space, rule at l.65):
the commit's parent is a later pin whose intermediate commits are not supplied. The deletion was therefore applied semantically to G1
(work/proposals/R2/modele-social/règles; `diff -r` against G1 = exactly that line) and G1 vs G1-minus-the-line was measured.

## Verdict: HARMLESS_REFACTOR (confidence high). Approval: none recorded.

## What `privé` means in the organisation's engine (publicodes 1.10.4, src/node_modules/publicodes/dist/index.js)
- l.1963: `privé: oui` marks the rule private. l.4842: `getParsedRules()` keeps only non-private rules that are accessible from the root, and
  `isAccessible` (l.1856) requires every parent to be non-private -> the private rule AND its descendants are hidden.
- l.1918: evaluating it from outside throws `La règle "…" n'est pas accessible depuis "$EVALUATION".`
- l.1993-1997 / l.5135: a private rule has no `$SITUATION` child; setting it in the situation throws `La règle … est une règle privée.` and the whole
  situation is rejected.
So the flag governs documentation/API visibility and overridability, not the computed value.

## Engine evidence (commands: `node src/publicodes_eval.mjs …`; files in work/engine/)
- build: before 641 raw / 1220 parsed; after 641 / 1227. `list --prefix "… taux ACRE"`: before [] ; after 7 names (taux ACRE, . CIPAV,
  . prestation de service, . service BIC, . service BNC, . vente restauration hébergement, . notification calcul ACRE annuel). 1227 - 1220 = 7.
- 69 existing checks (specs T0_ae3 16, T1a_rates 24, T0_ti 18, T1b_trader 7, R1_atmp 4; dates 01/01/2024 … 01/01/2026; AE BNC/CIPAV/vente/BIC with
  and without ACRE, DROM, indépendant, salarié) run on both trees: result files byte-identical (results_R2_before_* vs results_R2_after_*).
- 10 ACRE-specific checks (checks_R2_acre.json, 15 rules each). Situation (BNC, ACRE, created 01/01/2024, durée 6 mois, CA 1000 €/mois), date 01/07/2024:
  `… cotisations . taux ACRE` before = ERROR "n'est pas accessible depuis "$EVALUATION"", after = 50 %; at 01/09/2024 after = 50 % (before: same error).
  Public rules identical on both trees: `… cotisations . service BNC . taux` 10.6 %, `… cotisations` 106 €/mois, `… cotisations et contributions`
  108 €/mois, `dirigeant . auto-entrepreneur . revenu net` 10704 €/an; CIPAV case `… cotisations CIPAV . taux` 12.1 %. After only: `taux ACRE . service BNC`
  10.6 %, `. CIPAV` 12.1 %, `. vente restauration hébergement` 6.2 %, `. service BIC` 21.2 %, `. notification calcul ACRE annuel` true.
- New situation surface: `"… taux ACRE": "80 %"` -> before SituationError (règle privée, everything null); after accepted: taux ACRE 80 %,
  `service BNC . taux` 16.9 %, cotisations 169 €/mois.
- Engine caveat (results_R2_adhoc.json): CIPAV ACRE situation, `… cotisations . service BIC . taux` evaluated alone = null (missing 4) on BOTH trees;
  evaluated after `… taux ACRE . service BIC` in the same engine instance (possible only after the change) = 21.2 %. An evaluation-order cache effect
  of publicodes 1.10.4 on a `remplace` target, not a change in the rule's semantics; the maintainers should cover it with a test.

## Law (S4 legi-data 2.384.0, published 2024-09-01; identical to S3 for all 12 bounded articles — work/law/S4_index.json, S4_texts.md)
- No bounded article states the ACRE micro-social rate. L613-7 LEGIARTI000048683570 (in force 2023-12-28) I: "Un taux global différent peut être fixé par
  décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité
  sociale." The fixing decree article is outside the bounded set (the rule cites the Urssaf FAQ and service-public.fr F32318) -> the now-visible
  50 % / 12,10 % / pre-2020 grids can be neither confirmed nor refuted here: abstain.
- D131-6-1 LEGIARTI000036475110 (2018-01-01): "I. – La durée de l'exonération des cotisations dues par les personnes bénéficiant de l'aide à la création
  et à la reprise d'entreprise prévue à l'article L. 131-6-4 est de douze mois …" — the classic travailleur indépendant exemption; unaffected.
- L131-6-4 (eligibility) outside the set.

## Pre-existing issues visible in both trees (not caused by this commit; recorded for the next task)
1. D613-4 LEGIARTI000049624068 (in force 2024-07-01): "b) … 23,2 %", "e) … 23,1 %" vs G1 cotisations CIPAV . taux 21,2 % / service BNC . taux 21,1 % at
   01/07/2024 (results_R2_before_T1a_rates.jsonl). The exposed taux ACRE . service BNC 10,6 % = 50 % x 21,1 % inherits this; 50 % x 23,1 % = 11,55 %
   would follow only if the (outside) 50 % holds -> no expected value asserted.
2. `taux ACRE . service BIC` is `valeur: cotisations . service BIC . taux` with no `taux ACRE *` factor: an artisanal service AE with ACRE (6 mois,
   1000 €/mois) pays service BIC . taux 21.2 % and cotisations 212 €/mois on both trees, while BNC (10,6 %) and vente (6,2 %) are halved.
   Internal inconsistency; the legal expectation depends on the decree article outside the set.

## Deliverables / records
output/answer.json (generated by work/engine/make_answer_R2.mjs: engine values read from result files, quotes extracted from articles.json by exact window),
work/notes/R2_findings.md, work/proposals/R2/ (after-tree), work/engine/{checks_R2_acre.json, results_R2_*, log_R2_*, list_R2_*, results_R2_adhoc.json}.
