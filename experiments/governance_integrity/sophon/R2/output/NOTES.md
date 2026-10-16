# R2 — reverse check of commit 1932d654cf7a (decision date 2024-09-02, law S4, rules G1)

## Verdict
**HARMLESS_REFACTOR** (confidence high). Commit `1932d654cf7a81dbac73df88487fc70553e52a19` — "docs(auto-entrepreneur): Rend publique la règle taux ACRE des auto-entrepreneurs" (authored 2024-09-02 11:50:20 +0200, committed 2024-09-02 12:25:29 +0200) —
deletes one line in one file of `modele-social/règles`: the attribute `privé: oui` of the rule
`dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE` (`dirigeant/auto-entrepreneur/exonérations.publicodes`).
`privé` only controls whether a rule is visible/evaluable/settable from outside its namespace (and shown in the documentation). No formula, unit,
default, threshold, date or applicability condition changes.

## Why not the other labels
- Not MISMATCH: nothing any bounded rule computes changed (197 (situation, rule) pairs identical, 0 differences; sophon revalidation identical on 113 links). The AE-rate
  misalignment with D613-4 v.LEGIARTI000049624068 (23,1 / 23,2 % since 2024-07-01, library 21,1 / 21,2) is pre-existing and identical on both sides; it is reported, not attributed to this commit.
- Not LEGITIMATE_INDEPENDENT_CHANGE: no implementation choice is made; the 50 % ACRE value that becomes visible already drove the public rates before.
- Not UNRESOLVED: the bounded text is not needed to settle a visibility-only edit; what is outside the set (the decree fixing the micro ACRE rate) concerns the pre-existing rule content, not this change.

## What the engine shows (BEFORE = G1, AFTER = G1 + patch)
- AFTER tree: `work/proposals/R2/after/modele-social` (copy of G1 + `patch -p1 -l`; the hunk is written against a 2-space re-indented file, G1 has 4 spaces; `diff -r` shows only the deleted line;
  file sha256 34a39fe9b3baafe3 -> dcf5e0c265aff7f7).
- `build`: 641 raw rules both; parsed 1220 -> 1227. `list` gains exactly these names (hidden before by `privé`):
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . CIPAV
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . notification calcul ACRE annuel
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . prestation de service
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . service BIC
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . service BNC
  - dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE . vente restauration hébergement
- `taux ACRE` itself (situation AE BNC, created 01/03/2024, `entreprise . durée d'activité` 180 jour, ACRE oui, date 01/09/2024): BEFORE `ERROR: La règle "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE" n'est pas accessible depuis "$EVALUATION".`; AFTER `50 %`.
  At 500 jours (created 01/03/2023) AFTER = null; with ACRE non AFTER = null; created 2018/2019 with 400 jours: null on both sides (applicability rule `dirigeant . exonérations . ACRE` evaluates non applicable).
- Public rules identical, e.g. BNC with ACRE at 180 jours: taux service BNC 10.6 % / 10.6 %, cotisations 106 €/mois / 106 €/mois, revenu net 10704 €/an / 10704 €/an;
  at 500 jours 21.1 % / 21.1 %; ACRE non 21.1 % / 21.1 %; vente with ACRE 6.2 % both; BIC with ACRE 21.2 % both (ACRE sub-rule `service BIC` copies the full rate, pre-existing);
  CIPAV created 2024: 12.1 % / 1452 €/an both (pre-existing leak). Regression set `cases_R1` (11 situations, salarié/AE/indépendant at 01/07/2024 and 01/12/2024): identical = True.
- Files: `work/evals/cases_R2_acre.json` (40 cases: 4 natures x 4 creation/duration regimes x public rules / `taux ACRE` probe + ACRE=non controls), outputs `R2_cases_*_before_G1.jsonl` / `_after_G1post.jsonl`, tables `R2_*_table.txt`.

## Law side
- S4 (legi-data 2.384.0, published 2024-09-01) vs S3: all 12 bounded articles have the same version ids and texts (dump diff = header only). Nothing on the law side moved.
- L613-7 v.LEGIARTI000048683570: "Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale" — the ACRE-period micro rate is fixed by a decree article that is NOT in the bounded set.
- D131-6-1 v.LEGIARTI000036475110: "est de douze mois à compter soit de la date d'effet d'affiliation de l'assuré" — 12-month duration; II gives the exemption formula for the non-micro regime only.
- D613-4 v.LEGIARTI000049624068: "10 000 euros 34 % 6 600 euros 23,1 %" / "35 076 euros 34 % 23 150 euros 23,2 %" — in force at the decision date; library still 21.1 / 21.2 (pre-existing).

## sophon (system of record)
- Snapshots: S4 registered; G1 re-registered (idempotent); AFTER tree registered as `G1post_R2` (build 641/1227). A first registration of `G1post_R2` was made on the still-unpatched copy by mistake; it was overwritten by re-registering the patched tree before any link referenced it.
- `revalidate S4/G1` and `S4/G1post_R2`: counts {"BROKEN": 29, "REASSESS_LAW_CHANGED": 36, "REASSESS_RULE_CHANGED": 10, "RULE_CHANGED_CHECK_STILL_PASSES": 15, "STILL_VERIFIED": 12, "UNVERIFIED_NO_CHECK": 11} on both, per-link rows identical (True); no bounded article without a link; articles_changed ['D613-4', 'D613-6', 'D621-2', 'D633-3'] are inherited from links recorded on older versions (T0/T1a).
- Links added: R2-G1-L613-7-tauxACRE=None:REJECTED, R2-G1post_R2-L613-7-tauxACRE=L0114:VERIFIED, R2-G1post_R2-D131-6-1-dans-les-12-mois=L0115:VERIFIED, R2-G1post_R2-D131-6-1-apres-12-mois=L0116:VERIFIED, R2-G1post_R2-D613-4-BNC=L0117:FAILED, R2-G1post_R2-D613-4-CIPAV=L0118:FAILED, R2-G1post_R2-D613-4-BIC=L0119:VERIFIED.
  The L613-7 pair documents the flip: on G1 the store REJECTED the link ("not a parsed rule of snapshot G1": a private rule is not in the parsed list; nothing written) -> VERIFIED on G1post_R2 (observed 50).
  (The stored claim of that link says "expected FAILED" for G1; the actual outcome was REJECTED, which is stronger: the rule is not even addressable before the commit.) D613-4 BNC/CIPAV FAILED = pre-existing gap; BIC VERIFIED.
- Reports: work/sophon/reports/R2_asof_D131-6-1_2024-09-02.json, work/sophon/reports/R2_asof_D613-4_2024-09-02.json, work/sophon/reports/R2_asof_L613-7_2024-09-02.json, work/sophon/reports/R2_evidence.json, work/sophon/reports/R2_evidence.md, work/sophon/reports/R2_report_cmd.json, work/sophon/reports/R2_revalidate_S4_G1.json, work/sophon/reports/R2_revalidate_S4_G1.md, work/sophon/reports/R2_revalidate_S4_G1_cmd.json, work/sophon/reports/R2_revalidate_S4_G1post_R2.json, work/sophon/reports/R2_revalidate_S4_G1post_R2.md, work/sophon/reports/R2_revalidate_S4_G1post_R2_cmd.json, work/sophon/reports/R2_verify-store.json. verify-store: ok=True, problems=[], links checked 119.

## Approval
none recorded (no sign-off, ratification or approval record exists in the corpus; a merge/commit/test is not an approval).

## Tool calls
self-reported: 24 (including reads).
