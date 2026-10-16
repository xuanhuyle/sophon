# R5 — reverse check of commit c14ee26d0c67 (decision date 2026-10-05)

**Verdict: UNRESOLVED (confidence medium).** Approval: none recorded.

## What the commit changes
`fix: n'applique pas de plancher ni de plafond à l'abattement sur l'assiette à Mayotte` (Alice Dahan, committed 2026-07-09 12:29:17 +0200). One rule file of **modele-ti** (plus a test file not included in the patch):

```
@@ -108,8 +108,12 @@ indépendant . cotisations et contributions . assiette CSG-CRDS:
   avec:
     abattement:
       valeur: 26% * revenu brut
-      plancher: 1.76% * plafond sécurité sociale . annuel
-      plafond: 130% * plafond sécurité sociale . annuel
+      plancher:
+        non applicable si: établissement . commune . département . outre-mer . Mayotte
+        valeur: 1.76% * plafond sécurité sociale . annuel
+      plafond:
+        non applicable si: établissement . commune . département . outre-mer . Mayotte
+        valeur: 130% * plafond sécurité sociale . annuel
       arrondi: oui
 
   références:
```
Both trees build (298 raw / 460 parsed rules, identical rule-name lists). The only rule whose body changes is `indépendant . cotisations et contributions . assiette CSG-CRDS . abattement`; `indépendant . cotisations et contributions . assiette CSG-CRDS` (= revenu brut − abattement after the reform) and `indépendant . cotisations et contributions . assiette sociale` (= assiette CSG-CRDS + … per L131-6 I) inherit the change.

## Governing text (law snapshot S10 = legi-data 2.572.0; same version ids and texts as S9)
- **L136-3 III** (v.LEGIARTI000051284498, in force 2025-02-28): « fait l'objet d'un abattement de 26 %. Toutefois, cet abattement ne peut être ni inférieur à un montant plancher, fixé par décret […] ni supérieur à un montant plafond fixé, également par décret ».
- **D136-5** (v.LEGIARTI000049899286, in force 2024-07-07): « Le montant plancher prévu au III de l'article L. 136-3 est fixé à 1,76 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3. » and « Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3. »
- **L131-6 I** (v.LEGIARTI000048683707, in force 2023-12-28): cotisations « sont assises sur l'assiette définie à l'article L. 136-3 ».
- Occurrences of « Mayotte » in the 12 bounded articles: **0** ({'L131-6': 0, 'L136-3': 0, 'L613-7': 0, 'D131-6-1': 0, 'D136-5': 0, 'D613-4': 0, 'D613-5': 0, 'D613-6': 0, 'D621-2': 0, 'D632-1': 0, 'D633-3': 0, 'D756-5': 0}).

## Engine before (G4pre_R5 = parent tree) / after (G4post_R5)
Situations: EI à l'IR, activité commerciale, créée 01/01/2020, `indépendant . revenu brut` set directly; Mayotte = `établissement . commune . département = 'Mayotte'`.

| case | territoire | date | revenu brut | PSS (lib) | abattement before -> after | assiette CSG-CRDS before -> after | assiette sociale before -> after | cotisations before -> after | changed |
|---|---|---|---|---|---|---|---|---|---|
| MAY_1000_2025 | Mayotte | 01/07/2025 | 1000 €/an | 33 852 | 596 -> 260 | 404 -> 740 | 404 -> 740 | 434 -> 455 | YES |
| MAY_2000_2025 | Mayotte | 01/07/2025 | 2000 €/an | 33 852 | 596 -> 520 | 1 404 -> 1 480 | 1 404 -> 1 480 | 501 -> 507 | YES |
| MAY_3000_2025 | Mayotte | 01/07/2025 | 3000 €/an | 33 852 | 780 -> 780 | 2 220 -> 2 220 | 2 220 -> 2 220 | 556 -> 556 |  |
| MAY_30000_2025 | Mayotte | 01/07/2025 | 30000 €/an | 33 852 | 7 800 -> 7 800 | 22 200 -> 22 200 | 22 200 -> 22 200 | 3 740 -> 3 740 |  |
| MAY_100000_2025 | Mayotte | 01/07/2025 | 100000 €/an | 33 852 | 26 000 -> 26 000 | 74 000 -> 74 000 | 74 000 -> 74 000 | 8 922 -> 8 922 |  |
| MAY_250000_2025 | Mayotte | 01/07/2025 | 250000 €/an | 33 852 | 44 008 -> 65 000 | 205 992 -> 185 000 | 205 992 -> 185 000 | 19 508 -> 17 824 | YES |
| MAY_300000_2025 | Mayotte | 01/07/2025 | 300000 €/an | 33 852 | 44 008 -> 78 000 | 255 992 -> 222 000 | 255 992 -> 222 000 | 23 518 -> 20 791 | YES |
| MAY_1000_2026 | Mayotte | 01/07/2026 | 1000 €/an | 36 264 | 638 -> 260 | 362 -> 740 | 362 -> 740 | 478 -> 506 | YES |
| MAY_300000_2026 | Mayotte | 01/07/2026 | 300000 €/an | 36 264 | 47 143 -> 78 000 | 252 857 -> 222 000 | 252 857 -> 222 000 | 25 349 -> 22 673 | YES |
| MAY_1000_2024 | Mayotte | 01/07/2024 | 1000 €/an | 33 852 | 596 -> 260 | — -> — | — -> — | — -> — | YES |
| MAY_300000_2024 | Mayotte | 01/07/2024 | 300000 €/an | 33 852 | 44 008 -> 78 000 | — -> — | — -> — | — -> — | YES |
| MET_1000_2025 | métropole | 01/07/2025 | 1000 €/an | 47 100 | 829 -> 829 | 171 -> 171 | 171 -> 171 | 1 133 -> 1 133 |  |
| MET_3000_2025 | métropole | 01/07/2025 | 3000 €/an | 47 100 | 829 -> 829 | 2 171 -> 2 171 | 2 171 -> 2 171 | 1 295 -> 1 295 |  |
| MET_30000_2025 | métropole | 01/07/2025 | 30000 €/an | 47 100 | 7 800 -> 7 800 | 22 200 -> 22 200 | 22 200 -> 22 200 | 6 696 -> 6 696 |  |
| MET_300000_2025 | métropole | 01/07/2025 | 300000 €/an | 47 100 | 61 230 -> 61 230 | 238 770 -> 238 770 | 238 770 -> 238 770 | 54 008 -> 54 008 |  |
| MET_1000_2026 | métropole | 01/07/2026 | 1000 €/an | 48 060 | 846 -> 846 | 154 -> 154 | 154 -> 154 | 1 147 -> 1 147 |  |
| GUA_1000_2025 | Guadeloupe | 01/07/2025 | 1000 €/an | 47 100 | 829 -> 829 | 171 -> 171 | 171 -> 171 | 1 153 -> 1 153 |  |
| GUA_300000_2025 | Guadeloupe | 01/07/2025 | 300000 €/an | 47 100 | 61 230 -> 61 230 | 238 770 -> 238 770 | 238 770 -> 238 770 | 54 008 -> 54 008 |  |

Only Mayotte changes, and only outside the band where 26 % × revenu brut lies between the floor and the ceiling. Before the commit the Mayotte floor/ceiling were computed on the library's **Mayotte PSS** (33852 €/an in 2025, 36264 in 2026 — an Urssaf value, not the L241-3 PSS of 47100 that D136-5 names). CSG-CRDS itself is non applicable at Mayotte in the library (null on both sides), so the abattement reaches Mayotte only through the cotisation base (L131-6 I).

## Why UNRESOLVED
1. Under a literal reading, L136-3 III and D136-5 impose the floor and the ceiling with no territorial exception, and the after-tree computes at Mayotte an abattement below the floor (260 < 829 on the L241-3 PSS, < 596 even on the Mayotte PSS) and above the ceiling (78000 > 61 230 / 44008). That reading would make the commit a **MISMATCH** (conditional expected values are in `expected_values_if_mismatch`).
2. But whether L136-3 / L131-6 govern Mayotte at all is not decidable from the bounded set: no bounded article mentions Mayotte; the CSG scope article (L136-1), the Mayotte social-security texts and the legal source of the Mayotte PSS are outside the set; the library's whole Mayotte branch rests on Urssaf/CSSM sources that are not in the corpus; the commit cites no source and its test file is not in the patch. If such a text excludes the floor/ceiling at Mayotte, the commit is a **LEGITIMATE_INDEPENDENT_CHANGE** resting on it.
3. It is not a HARMLESS_REFACTOR: computed values change for real situations.

## Sophon
- Snapshots: law `S10`; rules `G4pre_R5`, `G4post_R5` (multi-dir modele-ti + modele-commun). `G4` (pin) unchanged.
- Links (S10): 16 attempted — VERIFIED = the engine facts above; FAILED = the two *conditional* literal-reading checks for Mayotte, recorded deliberately; UNKNOWN = the scope abstention.

| tag | status | link id |
|---|---|---|
| R5-pre-L136-3-III-floor-MAY | VERIFIED | L0160 |
| R5-pre-L136-3-III-ceiling-MAY | VERIFIED | L0161 |
| R5-pre-D136-5-I-MET | VERIFIED | L0162 |
| R5-pre-D136-5-II-MET | VERIFIED | L0163 |
| R5-pre-L131-6-I-assiette-MAY | VERIFIED | L0164 |
| R5-post-L136-3-III-floor-MAY | VERIFIED | L0165 |
| R5-post-L136-3-III-ceiling-MAY | VERIFIED | L0166 |
| R5-post-L136-3-III-floor-MAY-2026 | VERIFIED | L0167 |
| R5-post-D136-5-I-MET | VERIFIED | L0168 |
| R5-post-D136-5-II-MET | VERIFIED | L0169 |
| R5-post-D136-5-I-GUA | VERIFIED | L0170 |
| R5-post-L131-6-I-assiette-MAY | VERIFIED | L0171 |
| R5-post-L131-6-I-assiette-MAY-300k | VERIFIED | L0172 |
| R5-post-D136-5-I-MAY-literal | FAILED | L0173 |
| R5-post-D136-5-II-MAY-literal | FAILED | L0174 |
| R5-UNRESOLVED-scope-Mayotte | UNKNOWN | L0175 |

- Revalidate counts — S10×G4: {'BROKEN': 39, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 15, 'RULE_CHANGED_CHECK_STILL_PASSES': 34, 'UNVERIFIED_NO_CHECK': 1}; S10×G4pre_R5: {'BROKEN': 71, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 16, 'RULE_CHANGED_CHECK_STILL_PASSES': 2}; S10×G4post_R5: {'BROKEN': 71, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 16, 'RULE_CHANGED_CHECK_STILL_PASSES': 2} (old modele-social links are RULE_FILE_ABSENT on the modele-ti trees; S10 == S9 so no law-side reassessment).
- Reports: work/sophon/reports/R5_asof_L136-3_2026-10-05.json, work/sophon/reports/R5_evidence.json, work/sophon/reports/R5_evidence.md, work/sophon/reports/R5_evidence_cmd.json, work/sophon/reports/R5_revalidate_DONE, work/sophon/reports/R5_revalidate_S10_G4.json, work/sophon/reports/R5_revalidate_S10_G4.md, work/sophon/reports/R5_revalidate_S10_G4_cmd.json, work/sophon/reports/R5_revalidate_S10_G4post_R5.json, work/sophon/reports/R5_revalidate_S10_G4post_R5.md, work/sophon/reports/R5_revalidate_S10_G4post_R5_cmd.json, work/sophon/reports/R5_revalidate_S10_G4pre_R5.json, work/sophon/reports/R5_revalidate_S10_G4pre_R5.md, work/sophon/reports/R5_revalidate_S10_G4pre_R5_cmd.json, work/sophon/reports/R5_verify_store.json

## Open items carried forward
- Mayotte: the scope question above (needs L136-1 and the Mayotte texts).
- Still open from earlier tasks: AE DROM BNC/CIPAV rates ≥ 07/2024, D756-5 II CA cap, D613-4 c) meublés 6 %, D613-6 shares, CIPAV ACRE leak, D632-1 2024 floor, L613-7 minimum option, D613-4 2025 version without text; AE side of S9/S10 (D613-4 v.LEGIARTI000052218738, D613-6 v.LEGIARTI000052218747, D131-6-1 v.LEGIARTI000053451315) not yet assessed against a rules tree that contains the AE rules.

Self-reported tool calls: 24.
