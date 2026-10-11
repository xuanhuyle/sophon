# M2 findings (decision date 2026-03-31, law S8 legi-data 2.489.0 (2026-01-01) → S9 legi-data 2.514.0 (2026-03-31), rules G4 a61b72947fec committed 2026-03-03, modele-social 10.0.1, OLD single-package layout `modele-social/règles/dirigeant/...`)

## Law delta S8 -> S9 (work/law/S9_*, M2_S8_S9_record_diff.json) — ONE article changed
- D131-6-1: LEGIARTI000036475110 (2018-01-01, MODIFIE) -> LEGIARTI000053451315 (VIGUEUR 2026-01-01 → 2999-01-01), décret n° 2026-69 du 6 février 2026 art. 1
  (JORF 2026-02-08, signé 2026-02-06, dateDebutCible 2026-02-09). Nota: « entrent en vigueur le 1 er janvier 2026 et s'appliquent aux créations et reprises
  d'entreprise intervenant à compter de cette date » -> criterion = date de création/reprise, NOT the period.
  Text: II « correspond au quart du montant total des cotisations » (was « au montant total »); degressive « 0,25 E/0,25 PSS × (PSS−R) » (was « E/0,25 PSS × (PSS-R) »);
  new « sans préjudice des dispositions de l'article L. 131-6-5 » (outside set); III marins paragraph removed; IV new 60-day filing deadline (« soixantième jour »).
  Unchanged: I douze mois; E defined at 3/4 PSS; III PSS annual value, prorata if affiliation < 1 year.
- 11 other records byte-identical (L131-6, L136-3, L613-7, D136-5, D613-4, D613-5, D613-6, D621-2, D632-1, D633-3, D756-5). S9 here == S9 of the R4 line (files identical).

## Pin G3 -> G4 (what upstream did since M1, from history_bounded_rules.patch + diff vs proposals/M1)
- 88cb2ce9 (2026-01-08) adopted exactly the M1 values: BNC 25,6 %, all 2026 shares, `arrondi: oui` on the 4 cotisation amounts. Engine: G4 == M1 proposal on every AE cell
  except: DROM BNC 2026 still 4,4/13,1/17,4 (26,1-based, WRONG vs ceil10 of 25,6 x 1/6,1/2,2/3 = 4,3/12,8/17,1 -> re-proposed in M2);
  55470937: DROM Cipav 7,8/11,6/15,5 from 07/2024 (= ceil10(1/3,1/2,2/3 x 23,2): pre-existing mismatch FIXED upstream);
  ea8f00f0 (2026-01-27): Acre Cipav 13,40 % from 01/2026 (no source in the set; 13,90 before). Stale LEGIARTI000043656780 reference still in `service BNC Cipav . répartition`.
- G4 TI retraite de base still 17,15 % + 0,60/0,72 % form (R4's d3e0cfe0 rewrite is after this pin). PSS 2026 = 4 005 €/mois in base.publicodes (48 060 €/an).
- bdfbd61c: versement libératoire plafond rule (CGI, outside set).

## Rules decision
- AFFECTED: `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux` (edit), `. ACRE` (+ children maladie / IJ / invalidité et décès / retraite de base /
  allocations familiales: dependency), `… cotisations`, `… CSG-CRDS` (base includes cotisations), `dirigeant . indépendant . cotisations et contributions`.
  Also (OUTSIDE bounded file set but cites D131-6-1): `salarié . cotisations . exonérations . Acre` (+ employeur / salarié) -> edited too (`Acre . quotité`).
- NEEDS_REVIEW: AE `Acre . taux Acre` 50 % and its 3 derived rates (decree under L613-7 I not in set; décret 2026-69 may have touched it), `Acre . taux CIPAV` 13,40 % (no source),
  `DROM . taux service BNC` (pre-existing derivation mismatch, M1 fix carried over).
- UNAFFECTED: everything else; AE rates/shares re-run on G4 (36 unique checks of the M1 specs) and equal to the law-aligned M1 proposal.
- Not re-examined: TI base rules (D621-2, D632-1, D633-3, L131-6, L136-3 records identical, no ref to D131-6-1); gaps D613-5 / row c / D756-5 II; versement libératoire.

## Proposal M2 (proposals/M2: apply_M2.mjs = 14 anchored edits, M2.diff 228 lines, build 654 raw / 1336 parsed vs G4 652 / 1334)
- `exonérations . ACRE . taux`: variations si `entreprise . date de création >= 01/01/2026` -> taux progressif 25 % (<= 75 % PSS) -> 0 % (PSS); sinon 100 % -> 0 %.
- `salarié . cotisations . exonérations . Acre . quotité` (25 % / 100 %) multiplying both grille tranches of `. employeur` and `. salarié`.
- AE: note on `taux Acre`, NEW notification `dirigeant . auto-entrepreneur . Acre . taux Acre 2026 à confirmer` (= date de création >= 01/01/2026), DROM BNC 2026 4.3/12.8/17.1 + note.
- Docs: notes/références D131-6-1 (…315 and …110) on `exonérations . ACRE`, `dirigeant . exonérations . ACRE` (historique 2026, 60-day deadline).

## Engine values worth remembering (TI commerciale EI, revenu professionnel = assiette, date 01/06/2026, PSS 48 060, création 01/01/2026, Acre)
- rev 20 000: taux 100 -> 25 %; retraite de base 0 -> 2 663 (droit commun 3 550); ID 0 -> 195 (260); IJ 0 -> 75 (100); maladie 0 (0 at this income even without Acre);
  cotisations 1 400 -> 4 333 (no Acre 5 310); CSG-CRDS 2 076 -> 2 361 (2 455); total 3 596 -> 6 814 (7 885).
- rev 42 000: taux 50,437 -> 12,609 %; maladie 1 037 -> 1 828 (2 092); RB 3 695 -> 6 515 (7 455); cotisations 8 047 -> 11 944 (13 243); total 13 021 -> 17 296 (18 722).
- rev >= 48 060 (55 000, 80 000): taux 0 % both. Création 01/07/2025 (prorata 50 %) and création 2025 @2025: identical before/after.
- Assimilé salarié (SAS, salaire brut 30 000 €/an, création 2026): Acre 10 863 -> 2 716 €/an (employeur 8 673 -> 2 168,25 ; salarié 2 190 -> 547,5); brut 40 000 (degressive zone): 8 756 -> 2 189.
- AE created 2026 (durée 5 mois): notification true; rates unchanged (BNC 12,8 / Cipav 13,4 / BIC 10,6 / vente 6,2 %; taux Acre 50 %).
- Situations: TI = {salarié: non, dirigeant . régime social: 'indépendant', EI, auto-entrepreneur: non, imposition 'IR', activité 'commerciale', date de création,
  `entreprise . durée d'activité . en début d'année` set explicitly ("0 an" / "6 mois"), dirigeant . exonérations . ACRE, dirigeant . indépendant . revenu professionnel}.
  Assimilé salarié = {dirigeant . régime social: 'assimilé salarié', SAS, salarié . contrat . salaire brut, date de création, durée en début d'année, ACRE}.
  `taux progressif` interpolates linearly between tranches (100 % at 75 % PSS -> 0 % at 100 % PSS gives (PSS-R)/0,25 PSS).

## Method notes
- record_diff.mjs needs ALL 5 args (old new OLDTAG NEWTAG out.json). compare_snapshots.mjs on S9 vs S8 index. G4 vs M1-proposal `diff -u` per file = fastest way to see
  whether upstream adopted a proposal. Generator make_answer_M2.mjs: whitespace-tolerant anchors (zero-width spaces in the S9 formula are skipped by `[\s\S]*?`),
  eq() with 0,01 tolerance to ignore `arrondi: oui` float noise, specs merged by check id (ae and drom specs share DROM ids -> 36 unique ids for 48 checks).
- Anchors with typographic apostrophes/narrow spaces (« L’Acre : une aide … ») fail silently in includes(): anchor on plain lines instead.

## TO DO when the next snapshot / pin arrives
1. Look for the decree fixing the micro-social Acre rate from 2026 (L613-7 I): any new/modified article in the set mentioning « taux global » / L. 613-7 and Acre; then replace the
   notification `taux Acre 2026 à confirmer` by the real rate (if the quart logic were transposed: 75 % of full rate -> BNC 19,2 / BIC 15,9 / vente 9,2 %; NOT supported today).
2. Check whether upstream adopts the 25 % branch for TI (`exonérations . ACRE . taux`) and for `salarié . cotisations . exonérations . Acre`; compare with proposals/M2.
3. L131-6-5 (new reference in D131-6-1 II) is outside the set: say so again if it stays out. D131-6-1 IV 60-day deadline is procedural (not modelled).
4. Still open: DROM BNC 2026 derivation (G4 4,4/13,1/17,4); Acre Cipav 13,40 %; stale LEGIARTI000043656780 ref; D613-4 row c / D613-5 / D756-5 II not implemented;
   E-at-3/4-PSS approximation in the degressive band (both TI and salarié rules use the actual-revenue cotisations in the TI rule; the salarié rule uses the 75 % PSS cotisations).
5. If the pin moves to the 2026 split layout (modele-ti + modele-commun), see R4 notes for names (`indépendant . …`, no `dirigeant .`).
