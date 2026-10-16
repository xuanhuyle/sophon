#!/usr/bin/env node
// R4 answer generator. Run from the staging root:  node work/engine/make_answer_R4.mjs [tool_calls]
// - engine values are read from the result files produced by run_checks.sh on the two context trees (never typed by hand);
// - build counts are recomputed by calling the engine; the list diff is read from the list files;
// - every article quote is extracted from the S9 articles.json itself (exact substring by construction);
// - the D633-3 expected amount is derived here from the text (17,15 % within PSS + 0,72 % on the total), rounded once.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const ROOT = process.cwd()
const D = 'inputs/diffs/R4_d3e0cfe0f12d'
const TOOL_CALLS = Number(process.argv[2] || 0)
const meta = JSON.parse(readFileSync(`${D}/meta.json`, 'utf8'))
const patch = readFileSync(`${D}/diff.patch`, 'utf8')
const law = JSON.parse(readFileSync('inputs/law/S9_legi-data-2.514.0/articles.json', 'utf8'))
const iso = v => typeof v === 'number' ? new Date(v).toISOString().slice(0, 10) : String(v).slice(0, 10)
function art(num, id) { const r = law.articles[num].find(a => a.id === id); if (!r) throw new Error(`article ${num} ${id} not in S9`); return r }
function extract(rec, from, to, field = 'text') {
  const t = rec[field]; const i = t.indexOf(from); if (i < 0) throw new Error(`fragment not found in ${rec.num}.${field}: ${from}`)
  const j = t.indexOf(to, i); if (j < 0) throw new Error(`fragment not found in ${rec.num}.${field}: ${to}`)
  const q = t.slice(i, j + to.length); if (!t.includes(q)) throw new Error('window not exact'); return q
}
function quote(num, id, from, to, field = 'text', note) {
  const r = art(num, id)
  return { kind: 'article_quote', article: num, article_version_id: id, in_force: iso(r.dateDebut), etat: r.etat, field, quote_or_values: extract(r, from, to, field), ...(note ? { note } : {}) }
}
const must = (hay, s) => { if (!hay.includes(s)) throw new Error('excerpt not in source: ' + s); return s }
const rd = f => readFileSync(f, 'utf8').trim().split('\n').map(JSON.parse)
const fmt = v => !v ? 'n/a' : v.error ? `ERROR: ${v.error.split('\n')[0].replace(/\s+/g, ' ').slice(0, 80)}` : `${JSON.stringify(v.value)}${v.unit ? ' ' + v.unit : ''}`
function engine(cmd, tree) {
  return JSON.parse(execFileSync('node', ['src/publicodes_eval.mjs', cmd, '--rules', `${D}/${tree}/modele-ti/règles`, '--rules', `${D}/${tree}/modele-commun/règles`], { cwd: ROOT, encoding: 'utf8', maxBuffer: 1e8 }))
}

// 1. build + list diff
const bB = engine('build', 'context_parent_tree'), bA = engine('build', 'context_tree_after')
const lB = JSON.parse(readFileSync('work/engine/list_R4_context_parent_tree.json', 'utf8')).names
const lA = JSON.parse(readFileSync('work/engine/list_R4_context_tree_after.json', 'utf8')).names
const removed = lB.filter(x => !lA.includes(x)), added = lA.filter(x => !lB.includes(x))

// 2. engine results
const B = rd('work/engine/results_R4_parent_rb.jsonl'), A = rd('work/engine/results_R4_after_rb.jsonl')
if (B.length !== A.length) throw new Error('result files differ in length')
const RB = 'indépendant . cotisations et contributions . cotisations . retraite de base'
const RC = 'protection sociale . retraite . base . revenu cotisé', TR = 'protection sociale . retraite . base . trimestres', PE = 'protection sociale . retraite . base'
const CN = 'indépendant . profession libérale . CNAVPL . retraite de base', PTS = 'protection sociale . retraite . base . CNAVPL . points acquis', COT = 'indépendant . cotisations et contributions . cotisations'
const byId = {}; B.forEach((b, i) => { byId[b.id] = { b, a: A[i] } })
const val = (r, k) => (r.results[k] || {}).value
const differ = k => B.map((b, i) => [b, A[i]]).filter(([b, a]) => fmt(b.results[k]) !== fmt(a.results[k]))
const nonCnavpl = B.map((b, i) => [b, A[i]]).filter(([, a]) => val(a, 'indépendant . profession libérale . CNAVPL') !== true)
const cnavpl = B.map((b, i) => [b, A[i]]).filter(([, a]) => val(a, 'indépendant . profession libérale . CNAVPL') === true)
const rbDiff = differ(RB), rcDiff = differ(RC), trDiff = differ(TR), peDiff = differ(PE), ptsDiff = differ(PTS), cotDiff = differ(COT)
const cnDiff = cnavpl.filter(([b, a]) => fmt(b.results[RB]) !== fmt(a.results[RB]) || fmt(b.results[PTS]) !== fmt(a.results[PTS]) || fmt(b.results[PE]) !== fmt(a.results[PE]))
const maxRbDelta = Math.max(...rbDiff.map(([b, a]) => Math.abs(val(a, RB) - val(b, RB))))
const sit = r => ({ date: r.situation.date, activité: r.situation['entreprise . activité'], réglementée: r.situation['entreprise . activité . libérale . réglementée'] || 'n/a', 'date de création': r.situation['entreprise . date de création'], 'revenu professionnel = revenu brut': r.situation['indépendant . revenu professionnel'], ...(r.situation['indépendant . cotisations et contributions . déduction tabac'] ? { 'déduction tabac': r.situation['indépendant . cotisations et contributions . déduction tabac'] } : {}) })
function eba(id, rule, note) {
  const { b, a } = byId[id]
  return { kind: 'engine_before_after', rule, check_id: id, date: b.date, situation: sit(b), before: fmt(b.results[rule]), after: fmt(a.results[rule]), ...(note ? { note } : {}) }
}

// 3. D633-3 derivation for the worked example (AC_100000@25): assiette 74 000, PSS 47 100
const ex = byId['AC_100000@25']
const assiette = val(ex.a, `${RB} . assiette`), pssM = val(ex.a, 'plafond sécurité sociale'), pss = pssM * 12
const t1 = 17.15 / 100, t2 = 0.72 / 100
const textAmount = t1 * Math.min(assiette, pss) + t2 * assiette
const derivation = `D633-3 I: 17,15 % x min(assiette ${assiette}, PSS ${pss}) = ${(t1 * Math.min(assiette, pss)).toFixed(2)}; II: 0,72 % x ${assiette} = ${(t2 * assiette).toFixed(2)}; total ${textAmount.toFixed(2)} €/an -> ${Math.round(textAmount)} rounded once; before = round(T1 part) + round(T2 part) = ${val(ex.b, RB)}; after (barème 17,87 % <= PSS + 0,72 % > PSS) = ${val(ex.a, RB)}. Algebra: (T1+T2)·min(A,P) + T2·max(A-P,0) = T1·min(A,P) + T2·A.`

const d6333 = art('D633-3', 'LEGIARTI000049904636')
const versions = (d6333.articleVersions || []).map(v => ({ id: v.id, etat: v.etat, dateDebut: iso(v.dateDebut), dateFin: iso(v.dateFin) }))

const evidence = [
  quote('D633-3', 'LEGIARTI000049904636', 'I.-Le taux des cotisations', '17,15 %', 'text', 'tranche within the PSS; the library now carries 17,87 % = 17,15 + 0,72 as `taux T1`'),
  quote('D633-3', 'LEGIARTI000049904636', 'II.-Le taux des cotisations', '0,72 %', 'text', 'rate on the TOTAL base; the library now applies 0,72 % only above the PSS and folds the rest into taux T1 (same amount)'),
  quote('D633-3', 'LEGIARTI000049904636', 'Conformément', '1er janvier 2025', 'nota', 'periods from 2025-01-01 = the library branch `après réforme: date >= 01/2025`'),
  { kind: 'article_quote', article: 'D633-3', article_version_id: 'LEGIARTI000041967101', quote_or_values: `no text in S9 (only the current version carries text): versions = ${JSON.stringify(versions)}`, note: 'pre-2025 rates 17,15 / 0,60 % (library) cannot be checked: abstain' },
  { kind: 'diff_excerpt', article: 'D633-3', article_version_id: 'LEGIARTI000049904636', quote_or_values: must(patch, "# Le code de la sécurité sociale décrit un calcul identique à celui des PLR\n+        # (taux T1 sur la part de l'assiette < PASS + taux T2 sur toute l'assiette)\n+        # mais l'Urssaf calcule différemment (taux T2 sur la part de l'assiette > PASS\n+        # uniquement) et a insisté pour que l'on reprenne leur méthode.") },
  { kind: 'diff_excerpt', article: 'D633-3', article_version_id: 'LEGIARTI000049904636', quote_or_values: must(patch, '+    taux T1:\n       variations:\n-        - si: profession libérale . CNAVPL\n-          alors:\n-            variations:\n-              - si: après réforme\n-                alors: 8.73%\n-              - sinon: 8.23%\n-        - sinon: 17.15%\n+        - si: après réforme\n+          alors: 17.87%\n+        - sinon: 17.75%') },
  { kind: 'diff_excerpt', article: 'n/a (R351-9 / R634-1 outside the set)', article_version_id: 'n/a', quote_or_values: must(patch, '-    base / indépendant . cotisations et contributions . cotisations . retraite\n-    de base . tranche 1 . taux\n+    base / taux de cotisation') + '  ...  ' + must(patch, "+        - sinon: indépendant . cotisations et contributions . cotisations . retraite\n+            de base . taux T1") },
  { kind: 'engine_before_after', rule: 'build / list', check_id: 'build', before: `raw ${bB.raw_rule_count} / parsed ${bB.parsed_rule_count}`, after: `raw ${bA.raw_rule_count} / parsed ${bA.parsed_rule_count}`, note: `removed: ${removed.join('; ')} | added: ${added.join('; ')}` },
  eba('AC_100000@25', RB, derivation),
  eba('AC_100000@25', `${RB} . assiette`), eba('AC_100000@25', 'plafond sécurité sociale'),
  eba('AC_100000@25', `${RB} . taux T1`, 'before: tranche 1 . taux = ' + fmt(ex.b.results[`${RB} . tranche 1 . taux`]) + ' (D633-3 I figure); after: 17,87 % = 17,15 + 0,72'),
  eba('AC_100000@25', `${RB} . taux T2`, 'before: tranche 2 . taux = ' + fmt(ex.b.results[`${RB} . tranche 2 . taux`])),
  eba('AC_0@24', RB, 'rounding: before round(899.17)+round(31.46)=930, after round(930.63)=931; pre-2025 rates unverifiable (no text)'),
  eba('AC_20000@24', RB, 'artisan below PSS: identical'), eba('AC_300000@25', RB, 'artisan at 5 PSS+: identical'),
  eba('AC_20000@24', RC, 'revenu cotisé = cotisation / taux: denominator 17,15 % -> 17,75 % (R351-9 / R634-1, outside the set)'),
  eba('AC_20000@24', PE, 'pension estimate = 50 % x revenu cotisé (L161-17-3 etc., outside the set)'),
  eba('AC_6800@24', TR, 'trimestres validés flip 4 -> 3 (R351-9, outside the set)'),
  eba('AC_0@25', TR, 'at the assiette minimale retraite (5 346 € = 450 SMIC h, D633-2 outside the set) the after tree validates 2 trimestres instead of 3: 955 / 17,87 % = 5 344 < 5 346 after rounding'),
  eba('AC_0@25', RC), eba('AC_0@25', `${RB} . assiette`),
  eba('CIPAV_100000@25', RB, 'CNAVPL (D642-3, outside the set): identical, rule moved to `profession libérale . CNAVPL . retraite de base`'),
  eba('CIPAV_100000@25', PTS), eba('MED_60001@25', COT, 'CARMF médecin S1 (participation CPAM moved into the CNAVPL rule): identical'),
  eba('TABAC_60001@24', RB, 'déduction tabac above PSS: identical (plafond/plancher order change is value-neutral)'),
  { kind: 'engine_before_after', rule: 'summary over work/engine/checks_R4_rb.json', check_id: 'all', before: `${B.length} checks x ${Object.keys(B[0].results).length} rules`, after: `retraite de base differs in ${rbDiff.length}/${B.length} checks (max |delta| ${maxRbDelta} €, all non-CNAVPL, rounding); CNAVPL checks differing (retraite de base / points / pension): ${cnDiff.length}/${cnavpl.length}; revenu cotisé differs in ${rcDiff.length}; trimestres in ${trDiff.length}; pension estimate in ${peDiff.length}; total cotisations in ${cotDiff.length} (the rounding cases)` },
]

const answer = {
  task: 'R4',
  commit: meta.commit,
  label: 'LEGITIMATE_INDEPENDENT_CHANGE',
  confidence: 'medium',
  rationale: `The commit (${meta.subject}) replaces, for artisans/commerçants/PLNR, the two-tranche formula (17,15 % of the base within the PSS + 0,60/0,72 % of the whole base) by a barème taking 17,75/17,87 % up to the PSS and 0,60/0,72 % above it, moves the CNAVPL two-tranche rule to \`profession libérale . CNAVPL . retraite de base\`, and changes the denominator of \`protection sociale . retraite . base . revenu cotisé\` from 17,15 % to taux T1. With respect to the only bounded article involved, D633-3 LEGIARTI000049904636 (periods from 2025-01-01), the new barème is algebraically the same amount: (17,15+0,72) % x min(A,PSS) + 0,72 % x max(A-PSS,0) = 17,15 % x min(A,PSS) + 0,72 % x A; the engine confirms it: identical \`retraite de base\` in ${B.length - rbDiff.length} of ${B.length} checks and a ${maxRbDelta} € rounding difference in ${rbDiff.length} (single rounding after vs rounding of each tranche before; D633-3 fixes no rounding). So it is not a mismatch; it is also not harmless, because what the engine computes did change: the published rate \`taux T1\` is now 17,87 % instead of the text's 17,15 % (0,72 % folded in, Urssaf presentation), and the derived \`revenu cotisé\`, \`trimestres\` and pension estimate change for every non-CNAVPL case below the PSS (e.g. revenu cotisé 20 700 -> 20 000 €/an, trimestres 4 -> 3 at 6 800 €/an in 2024, 3 -> 2 at the minimum base in 2025). Those derived rules rest on R351-9, R634-1, D634-1, D633-2 and L161-17-3, and the CNAVPL branch on D642-3/D642-4: all outside the bounded set, so I cannot adjudicate them. The commit itself says the method was adopted at the Urssaf's insistence (outside source). Pre-2025 rates (17,75 / 0,60 %) cannot be checked: D633-3 LEGIARTI000041967101 has no text in S9 (abstain).`,
  evidence,
  expected_values_if_mismatch: [],
  outside_bounded_set: [
    'D642-3 and D642-4 CSS (CNAVPL retraite de base rates 8,23/8,73 % and 1,87 %, base capped at 5 PSS) - the moved `profession libérale . CNAVPL . retraite de base` rule; engine shows identical values but the text is not in the set',
    'R351-9, R634-1 and D634-1 CSS (revenu cotisé = cotisation / taux de cotisation; 150 SMIC h per trimestre) - the changed denominator of `protection sociale . retraite . base . revenu cotisé` and the resulting `trimestres` flips (4->3 at 6 800 €/an in 2024; 3->2 at the minimum base in 2025)',
    'D633-2 CSS (assiette minimale retraite = 450 SMIC h, meant to validate 3 trimestres) - the after tree validates only 2 trimestres at that base in 2025 (955 €/an / 17,87 % = 5 344 < 5 346): flagged for review, not adjudicable here',
    'L161-17-3 CSS and the Assurance retraite rules behind `protection sociale . retraite . base` (pension estimate = 50 % x revenu cotisé): changes with revenu cotisé',
    'Urssaf "Retraite de base" page (urssaf.fr) - the source of the 17,87 % / 0,72 % presentation the commit adopts',
    'D633-3 version LEGIARTI000041967101 (2020-05-25 -> 2024-07-07): pre-2025 rates 17,15 / 0,60 % - text absent from S9, abstain',
  ],
  approval: 'none recorded',
  notes: `Trees evaluated: ${D}/context_parent_tree vs context_tree_after (modele-ti + modele-commun; the G4 pin a61b72947fec is the older single-package modele-social tree and does not contain this file layout). Build: ${bB.raw_rule_count}/${bB.parsed_rule_count} -> ${bA.raw_rule_count}/${bA.parsed_rule_count} rules. Removed public rules: ${removed.length} (tranche 1/2, their assiette/taux); added: ${added.length}. ${B.length} checks (artisan, PLNR created 2015 = CNAVPL and 2020 = régime général, Cipav, médecin S1 CARMF, débit de tabac; 0 to 300 000 €/an; dates 01/12/2024, 01/06/2025, 01/03/2026) x ${Object.keys(B[0].results).length} rules in work/engine/results_R4_{parent,after}_rb.jsonl. Law S9 (legi-data 2.514.0) vs S5: D633-3, D632-1, D136-5, D621-2, D613-5, D756-5 unchanged; D613-4 and D613-6 re-issued 2026-01-01 (décret 2025-943), D131-6-1 re-issued 2026-01-01 (décret 2026-69), L136-3 re-issued 2025-02-28 (loi 2025-199) - none of them touched by this commit. The commit's comment that the CSS and the Urssaf compute differently is mistaken on the amount (the two formulations are identical up to rounding) but the choice to display the Urssaf rates and to divide by them in revenu cotisé is a real semantic choice. Not a legal sign-off: none recorded.`,
  self_reported_tool_calls: TOOL_CALLS,
}
mkdirSync('output', { recursive: true })
writeFileSync('output/answer.json', JSON.stringify(answer, null, 1) + '\n')
console.log(`answer.json written: ${evidence.length} evidence items; rbDiff ${rbDiff.length}/${B.length} (max ${maxRbDelta} €); cnavpl identical: ${cnDiff.length === 0}; rc ${rcDiff.length}; tr ${trDiff.length}; pe ${peDiff.length}; cot ${cotDiff.length}`)
console.log('removed:', removed.length, 'added:', added.length)
console.log(derivation)
