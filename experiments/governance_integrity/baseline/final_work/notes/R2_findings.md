# R2 findings (decision date 2024-09-02, law S4 legi-data 2.384.0 published 2024-09-01, rules G1 2a0e452617fc)

## Event
Commit 1932d654cf7a81dbac73df88487fc70553e52a19 "docs(auto-entrepreneur): Rend publique la règle taux ACRE des auto-entrepreneurs"
(Alice Dahan, authored 2024-09-02 11:50, committed 12:25). ONE deletion: `privé: oui` under
`dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE` (dirigeant/auto-entrepreneur/exonérations.publicodes).
Verdict HARMLESS_REFACTOR (high). Approval: none recorded.

## Caveat on the before-tree
The patch's `a` blob is a061b547e (2-space indentation, rule at l.62); G1's file blob is 8914c3ae (4-space, rule at l.65) -> the commit's parent is a
later pin (file reformatted between 2024-07-16 and 2024-09-02; unknown intermediate commits). Measured G1 vs G1-minus-that-line (work/proposals/R2).
git blob hash without git: sha1("blob <len>\0" + content).

## What `privé: oui` does in publicodes 1.10.4 (src/node_modules/publicodes/dist/index.js)
- l.1963: `privateRule = rawRule.privé === "oui" || nom.startsWith("[privé] ")`.
- l.1993-1997: a NON-private rule gets a `[privé] $SITUATION` child + `dans la situation`; a private rule has none -> cannot be set in the situation
  (l.5135: "La règle X est une règle privée." SituationError -> the WHOLE situation is rejected, everything evaluates null).
- l.4842: `publicParsedRules` = rules that are not private AND accessible from "" (isAccessible l.1856: every parent up to the common ancestor must be
  non-private) -> getParsedRules() hides the private rule AND all its descendants. Hence parsed_rule_count 1220 -> 1227 (+7).
- evaluate() from outside -> SyntaxError (l.1918) `La règle "X" n'est pas accessible depuis "$EVALUATION".`
- `remplace` from children of a private rule still works (the public rate rules showed the ACRE values before).
- l.2181 updateRuleMissingVariables skips private/inaccessible rules.

## Engine evidence (all in work/engine/)
- build: 641 raw / 1220 parsed (before) vs 641 / 1227 (after). list prefix "... taux ACRE": [] vs 7 names (list_R2_before/after_tauxACRE.json).
- 69 existing checks x 2 trees: results_R2_before_<spec>.jsonl == results_R2_after_<spec>.jsonl byte-identical (T0_ae3 16, T1a_rates 24, T0_ti 18,
  T1b_trader 7, R1_atmp 4). results_R2_before_* == results_R1_G1_* (same tree, reproducible).
- checks_R2_acre.json (10 checks, 15 rules): results_R2_before_acre / results_R2_after_acre. Public cells identical except the override case
  (situation rejected before). taux ACRE: ERROR -> 50 % (BNC ACRE 6 mois @01/07/2024 and @01/09/2024), . service BNC 10.6 %, . CIPAV 12.1 %,
  . vente 6.2 %, . service BIC 21.2 % (!), notification true. Public: service BNC . taux 10.6 %, cotisations 106 €/mois, revenu net 10704 €/an.
- Override "taux ACRE": "80 %" -> before SituationError (règle privée); after accepted: service BNC . taux 16.9 %, cotisations 169 €/mois.
- ORDER ARTIFACT (results_R2_adhoc.json): CIPAV ACRE situation, `cotisations . service BIC . taux` alone = null (missing 4) on both trees; after
  `taux ACRE . service BIC` is evaluated first in the same engine -> 21.2 %. Only reachable now that the replacing rule is public. Cache effect, not
  rule semantics. Keep ad-hoc multi-rule specs in mind: evaluate replaced rules in their own process when comparing.

## Law side (S4 == S3 on all 12 articles; compare_snapshots.mjs printed "same" everywhere)
- No bounded article gives the ACRE micro-social rate. L613-7 LEGIARTI000048683570 I al.2: "Un taux global différent peut être fixé par décret pour
  les périodes au cours desquelles le travailleur indépendant est éligible à une exonération..." -> the fixing decree article is OUTSIDE the set
  (rule cites Urssaf FAQ + service-public F32318). D131-6-1 LEGIARTI000036475110 = classic TI ACRE (12 months, full <= 0,75 PSS, linear to PSS).
- Still open (pre-existing, not this commit): D613-4 LEGIARTI000049624068 (2024-07-01) b 23,2 / e 23,1 % vs G1 21,2 / 21,1 %; ACRE BNC 10,6 % = 50 % x 21,1.
- NEW pre-existing anomaly spotted: `taux ACRE . service BIC: valeur: cotisations . service BIC . taux` (no `taux ACRE *` factor since the
  "cotisations . X . taux" renaming, history_bounded_rules.patch l.321-324, commit ffab95034/303adafde era). SBIC AE with ACRE 6 mois pays 21,2 % /
  212 €/mois on 1000 €/mois; BNC 10,6 %, vente 6,2 %. Internal inconsistency; legal expectation depends on the decree outside the set. Expect a fix.

## Files
checks_R2_acre.json, results_R2_{before,after}_{acre,T0_ae3,T1a_rates,T0_ti,T1b_trader,R1_atmp}.jsonl, log_R2_*.txt, list_R2_*_tauxACRE.json,
results_R2_adhoc.json, make_answer_R2.mjs (generator: engine values from files, quotes extracted from articles.json by window). proposals/R2 = after-tree.
