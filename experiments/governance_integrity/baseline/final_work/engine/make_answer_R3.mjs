#!/usr/bin/env node
// R3 answer generator. Run from the staging root:  node work/engine/make_answer_R3.mjs [tool_calls]
// - engine values are read from the result files produced by run_checks.sh (never typed by hand);
// - build counts and the list diff are (re)computed by calling the engine / reading the list files;
// - every article quote is extracted from the S5 articles.json text itself (exact substring by construction);
// - expected DROM rates are derived here from D756-5 fractions x D613-4 (v5, 2024-07-01) rates, rounded UP to 0.1 (D756-5: "arrondi au dixième de pour cent supérieur").
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const ROOT = process.cwd()
const BEFORE = 'inputs/rules/G2_3a4091ae1caf/modele-social/règles'
const AFTER = 'work/proposals/R3/modele-social/règles'
const P = 'dirigeant . auto-entrepreneur . cotisations et contributions . cotisations'
const TOOL_CALLS = Number(process.argv[2] || 0)

const meta = JSON.parse(readFileSync('inputs/diffs/R3_9bb43d710094/meta.json', 'utf8'))
const patch = readFileSync('inputs/diffs/R3_9bb43d710094/diff.patch', 'utf8')
const law = JSON.parse(readFileSync('inputs/law/S5_legi-data-2.385.0/articles.json', 'utf8'))
const iso = ms => new Date(ms).toISOString().slice(0, 10)
function art(num, id) { const r = law.articles[num].find(a => a.id === id); if (!r) throw new Error(`article ${num} ${id} not in S5`); return r }
function extract(rec, from, to, field = 'text') {
  const t = rec[field]; const i = t.indexOf(from); if (i < 0) throw new Error(`fragment not found in ${rec.num}: ${from}`)
  const j = t.indexOf(to, i); if (j < 0) throw new Error(`fragment not found in ${rec.num}: ${to}`)
  const q = t.slice(i, j + to.length); if (!t.includes(q)) throw new Error('window not exact'); return q
}
function quote(num, id, from, to, field = 'text', note) {
  const r = art(num, id)
  return { kind: 'article_quote', article: num, article_version_id: id, in_force: iso(r.dateDebut), etat: r.etat, field, quote_or_values: extract(r, from, to, field), ...(note ? { note } : {}) }
}
const must = (hay, s) => { if (!hay.includes(s)) throw new Error('excerpt not in source: ' + s); return s }

function engine(cmd, rules, extra = []) { return JSON.parse(execFileSync('node', ['src/publicodes_eval.mjs', cmd, '--rules', rules, ...extra], { cwd: ROOT, encoding: 'utf8', maxBuffer: 1e8 })) }
const rd = f => readFileSync(f, 'utf8').trim().split('\n').map(JSON.parse)
const fmt = v => !v ? 'n/a' : v.error ? `ERROR: ${v.error.split('\n')[0].slice(0, 90)}` : `${JSON.stringify(v.value)}${v.unit ? ' ' + v.unit : ''}${v.missing ? ` (missing ${v.missing})` : ''}`
const listOf = f => { const j = JSON.parse(readFileSync(f, 'utf8')); return Array.isArray(j) ? j : (j.rules || j.names || Object.keys(j)) }

// 1. build + list
const bB = engine('build', BEFORE), bA = engine('build', AFTER)
const lB = listOf('work/engine/list_R3_before.json'), lA = listOf('work/engine/list_R3_after.json')
const onlyA = lA.filter(x => !new Set(lB).has(x)), onlyB = lB.filter(x => !new Set(lA).has(x))

// 2. existing specs: which cells differ, and are they all DROM situations?
const specs = ['R1_atmp', 'T1a_rates', 'T0_ae3', 'T1b_trader', 'T0_ti', 'R2_acre']
const specSummary = specs.map(s => {
  const B = rd(`work/engine/results_R3_before_${s}.jsonl`), A = rd(`work/engine/results_R3_after_${s}.jsonl`)
  let cells = 0, diff = 0; const ids = new Set()
  B.forEach((b, i) => { const a = A[i]; for (const k of new Set([...Object.keys(b.results), ...Object.keys(a.results)])) { cells++; if (fmt(b.results[k]) !== fmt(a.results[k])) { diff++; ids.add(b.id) } } })
  return { spec: s, checks: B.length, cells, differing_cells: diff, differing_checks: [...ids] }
})
const nonDromDiff = specSummary.flatMap(s => s.differing_checks).filter(id => !/DROM/.test(id))
if (nonDromDiff.length) throw new Error('non-DROM checks differ: ' + nonDromDiff)

// 3. DROM spec values
const DB = rd('work/engine/results_R3_before_drom.jsonl'), DA = rd('work/engine/results_R3_after_drom.jsonl')
const pick = id => { const b = DB.find(r => r.id === id), a = DA.find(r => r.id === id); if (!b || !a) throw new Error('missing check ' + id); return [b, a] }
const val = (r, k) => r.results[k]?.value
const rateRule = { BNC: P + ' . service BNC . taux', CIPAV: P + ' . cotisations CIPAV . taux', SBIC: P + ' . service BIC . taux', VENTE: P + ' . vente restauration hébergement . taux' }
const row = (id, cat) => { const [b, a] = pick(id); return { id, date: b.date, situation_keys: { 'outre-mer': b.situation['établissement . commune . département . outre-mer'], trimestres_civils: b.situation["entreprise . durée d'activité . trimestres civils"], années_civiles: b.situation["entreprise . durée d'activité . années civiles"], activité: b.situation['entreprise . activité . nature'], réglementée: b.situation['entreprise . activité . nature . libérale . réglementée'] ?? null, CA: b.situation["dirigeant . auto-entrepreneur . chiffre d'affaires"] }, rule: rateRule[cat], before: fmt(b.results[rateRule[cat]]), after: fmt(a.results[rateRule[cat]]), cotisations_before: fmt(b.results[P]), cotisations_after: fmt(a.results[P]), revenu_net_before: fmt(b.results['dirigeant . auto-entrepreneur . revenu net']), revenu_net_after: fmt(a.results['dirigeant . auto-entrepreneur . revenu net']) } }
const table = []
for (const p of ['P1', 'P2', 'P3']) for (const c of ['BNC', 'CIPAV', 'SBIC', 'VENTE']) table.push(row(`DROM_${p}_${c}@01-10-2024`, c))
const metro = ['BNC', 'CIPAV', 'SBIC', 'VENTE'].map(c => row(`METRO_${c}@01-10-2024`, c))
if (!metro.every(m => m.before === m.after && m.cotisations_before === m.cotisations_after)) throw new Error('metropole controls moved')
const june = ['BNC', 'CIPAV'].map(c => row(`DROM_P1_${c}@01-06-2024`, c))
const dec = row('DROM_P1_BNC@19-10-2024', 'BNC')

// 4. the law: D756-5 fractions x D613-4 v5 rates, rounded up to the tenth
const ceil10 = x => Math.ceil(x * 10 - 1e-9) / 10
const d6134 = art('D613-4', 'LEGIARTI000049624068')
const inForce = { VENTE: 12.3, SBIC: 21.2, BNC: 23.1, CIPAV: 23.2 }   // a) d) e) b) of D613-4 v5 (quoted below)
for (const [k, v] of Object.entries({ VENTE: 'a) Travailleurs indépendants appartenant à la catégorie mentionnée au 1° du 1 de l\' article 50-0 du code général des impôts 79 828 euros 71 % 23 150 euros 12,3 %', SBIC: '46 300 euros 50 % 23 150 euros 21,2 %', BNC: '10 000 euros 34 % 6 600 euros 23,1 %', CIPAV: '35 076 euros 34 % 23 150 euros 23,2 %' })) must(d6134.text, v)
const frac = { a: { VENTE: 1 / 6, SBIC: 1 / 6, BNC: 1 / 6, CIPAV: 1 / 3 }, b: 1 / 2, c: 2 / 3 }
const expected = {}
for (const c of Object.keys(inForce)) expected[c] = { P1: ceil10(inForce[c] * frac.a[c]), P1_if_one_third: ceil10(inForce[c] / 3), P2: ceil10(inForce[c] * frac.b), P3: ceil10(inForce[c] * frac.c) }
// consistency check: the constants written in the rule equal the same derivation from the PRE-2024-07-01 base rates the engine gives at 01/06/2024 (21.1 / 21.2), whose D613-4 text is not in the snapshot
const pre = { VENTE: 12.3, SBIC: 21.2, BNC: val(DB.find(r => r.id === 'DROM_P1_BNC@01-06-2024'), rateRule.BNC), CIPAV: val(DB.find(r => r.id === 'DROM_P1_CIPAV@01-06-2024'), rateRule.CIPAV) }
const ruleConst = { VENTE: [2.1, 6.2, 8.2], SBIC: [3.6, 10.6, 14.2], BNC: [3.6, 10.6, 14.1], CIPAV: [7.1, 10.6, 14.2] }
const consistency = {}
for (const c of Object.keys(pre)) { const d = [ceil10(pre[c] * frac.a[c]), ceil10(pre[c] * frac.b), ceil10(pre[c] * frac.c)]; consistency[c] = { base_rate_used: pre[c], derived: d, rule_constants: ruleConst[c], equal: JSON.stringify(d) === JSON.stringify(ruleConst[c]) } }
// after-values from the engine for the mismatch list
const found = (p, c) => val(DA.find(r => r.id === `DROM_${p}_${c}@01-10-2024`), rateRule[c])
for (const c of ['SBIC', 'VENTE']) for (const [i, p] of ['P1', 'P2', 'P3'].entries()) if (found(p, c) !== expected[c][p]) throw new Error(`unexpected: ${c} ${p} engine ${found(p, c)} vs law ${expected[c][p]}`)

const mism = []
const der = (c, p, f, label) => `${label}: D756-5 I ${p === 'P1' ? 'a)' : p === 'P2' ? 'b)' : 'c)'} fraction ${f} x D613-4 (LEGIARTI000049624068, in force 2024-07-01) rate ${inForce[c]} % = ${(inForce[c] * eval(f)).toFixed(4)} %, "arrondi au dixième de pour cent supérieur" -> ${expected[c][p]} %. The rule constant ${found(p, c)} % equals the same derivation applied to the pre-2024-07-01 rate ${pre[c]} % (engine value at 01/06/2024; that older D613-4 text is not in the snapshot).`
for (const c of ['BNC', 'CIPAV']) for (const p of ['P1', 'P2', 'P3']) {
  const f = p === 'P1' ? (c === 'CIPAV' ? '1/3' : '1/6') : p === 'P2' ? '1/2' : '2/3'
  const label = c === 'BNC' ? 'profession libérale non réglementée (BNC, D613-4 e)' : 'profession libérale CIPAV (D613-4 b)'
  const period = p === 'P1' ? 'first period (trimestres civils = 4, années civiles = 1)' : p === 'P2' ? 'second period (trimestres civils = 12, années civiles = 3)' : 'from the 4th civil year (trimestres civils = 24, années civiles = 6)'
  const e = { rule: rateRule[c], date: '01/10/2024', situation: `DROM auto-entrepreneur, ${label}, ${period}, CA 1000 €/mois (check DROM_${p}_${c}@01-10-2024)`, found: found(p, c), expected: expected[c][p], before_change: val(DB.find(r => r.id === `DROM_${p}_${c}@01-10-2024`), rateRule[c]), derivation: der(c, p, f, label) }
  if (c === 'BNC' && p === 'P1') e.caveat = `1/6 applies to "travailleurs indépendants mentionnés au 2° de l'article L. 611-1" (L611-1 is outside the bounded set); the rule and its own description treat BNC like artisans/commerçants (1/6). Under the 1/3 reading the expected value would be ${expected.BNC.P1_if_one_third} %; under neither reading is 3.6 % supported at this date.`
  mism.push(e)
}
// amounts for one case
const [b1, a1] = pick('DROM_P1_BNC@19-10-2024')
mism.push({ rule: P, date: '19/10/2024', situation: 'same as DROM_P1_BNC, decision date', found: val(a1, P), expected: ceil10(23.1 / 6) * 10, unit: '€/mois', before_change: val(b1, P), derivation: '1000 €/mois x 3.9 % = 39 €/mois (engine after the change: 1000 x 3.6 % = 36 €/mois; before: 1000 x 23.1 % = 231 €/mois).' })

// 5. snapshot excerpt (the maintainers' own fixture at G2 recorded métropole rates for a DROM case)
const snap = readFileSync('inputs/rules/G2_3a4091ae1caf/existing_tests/site/test/regressions/__snapshots__/auto-entrepreneur.test.ts.snap', 'utf8')
const drom3 = snap.slice(snap.indexOf('> DROM 3`'), snap.indexOf('> DROM 4`'))
const snapLine = must(drom3, 'dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . service BNC . taux: 23')
const yaml = readFileSync('inputs/rules/G2_3a4091ae1caf/existing_tests/site/test/regressions/auto-entrepreneur.yaml', 'utf8')
must(yaml, "entreprise . durée d'activité . trimestres civils: 1")

const d7565 = art('D756-5', 'LEGIARTI000034726710')
const evidence = [
  { kind: 'diff_excerpt', article: null, article_version_id: null, quote_or_values: `modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes: the four replacement rules move from 6-space indentation (keys inside the body of the private rule \`seconde période\`) to 4-space (children of \`dirigeant . auto-entrepreneur . DROM\` under its \`avec:\`): ${must(patch, '-      service BIC:')} -> ${must(patch, '+    taux service BIC:')} (rule renamed), ${must(patch, '-      taux service BNC:')} -> ${must(patch, '+    taux service BNC:')}, same for \`taux vente restauration hébergement\` and \`taux CIPAV\`; the misspelt duplicate key ${must(patch, '-  references:')} is removed so the PDF link falls under \`références:\`; the rate constants themselves are unchanged (3.60/10.60/14.20 %, 3.60/10.60/14.10 %, 2.10/6.20/8.20 %, 7.10/10.60/14.20 %). dirigeant/dirigeant.publicodes: blank lines only. The third file of stat.txt (auto-entrepreneur.test.ts.snap, 116 lines) is not supplied.` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `build: before raw ${bB.raw_rule_count} / parsed ${bB.parsed_rule_count}; after raw ${bA.raw_rule_count} / parsed ${bA.parsed_rule_count}. list: only-after = ${JSON.stringify(onlyA)}; only-before = ${JSON.stringify(onlyB)}. Mechanism: publicodes 1.10.4 parseRule keeps only keys in mecanismKeys (dist/index.js l.1985-1987 \`for (const key in rawRule) { if (mecanismKeys.includes(key)) ...\`), so at G2 the four keys inside \`seconde période\` were silently dropped and no DROM replacement existed.` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `DROM rate rules at date 01/10/2024, CA 1000 €/mois, outre-mer: oui, ACRE: non (work/engine/checks_R3_drom.json -> results_R3_before_drom.jsonl / results_R3_after_drom.jsonl): ` + table.map(r => `[${r.id}] ${r.rule.replace(P, 'cotisations')}: ${r.before} -> ${r.after}; cotisations ${r.cotisations_before} -> ${r.cotisations_after}; revenu net ${r.revenu_net_before} -> ${r.revenu_net_after}`).join(' | ') },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `Decision-date check [${dec.id}] ${dec.rule}: ${dec.before} -> ${dec.after}; cotisations ${dec.cotisations_before} -> ${dec.cotisations_after}. Pre-07/2024 date: ` + june.map(r => `[${r.id}] ${r.rule.replace(P, 'cotisations')}: ${r.before} -> ${r.after}`).join('; ') + `. Métropole controls (outre-mer: non) identical before/after: ` + metro.map(r => `[${r.id}] ${r.rule.replace(P, 'cotisations')} = ${r.after}`).join('; ') },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `Existing check specs re-run on both trees (results_R3_before_<spec>.jsonl vs results_R3_after_<spec>.jsonl): ` + specSummary.map(s => `${s.spec}: ${s.checks} checks, ${s.cells} cells, ${s.differing_cells} differ${s.differing_checks.length ? ' (' + s.differing_checks.join(', ') + ')' : ''}`).join('; ') + `. Every differing check is a DROM situation; nothing else moved.` },
  quote('D756-5', 'LEGIARTI000034726710', 'le taux mentionné au premier alinéa de l\'article L. 133-6-8 correspond', 'à compter de la quatrième année civile d\'activité.', 'text', 'Only version in the snapshot (created by décret 2017-972, in force 2017-05-12). It still cites the pre-2018/2020 numbering L. 133-6-8 (now L613-7) and D. 131-6-1 (the micro-social rate table now sits in D613-4); the renumbering instruments are outside the bounded set.'),
  quote('D613-4', 'LEGIARTI000049624068', 'a) Travailleurs indépendants appartenant à la catégorie mentionnée au 1° du 1 de l\' article 50-0', '12,3 %'),
  quote('D613-4', 'LEGIARTI000049624068', 'b) Travailleurs indépendants affiliés à la section professionnelle mentionnée au 11° de l\'article R. 641-1', '23,2 %'),
  quote('D613-4', 'LEGIARTI000049624068', 'd) Travailleurs indépendants appartenant à la catégorie mentionnée au 2° du 1 de l\'article 50-0', '21,2 %'),
  quote('D613-4', 'LEGIARTI000049624068', 'e) Travailleurs indépendants relevant à la fois de l\'article L. 631-1', '23,1 %'),
  quote('D613-4', 'LEGIARTI000049624068', 'Conformément au 2° de l\'article 1 du décret n° 2024-484 du 30 mai 2024', '1er juillet 2024.', 'nota'),
  quote('L613-7', 'LEGIARTI000048683570', 'un taux global fixé par décret pour chaque catégorie d\'activité', 'mentionnée aux mêmes articles'),
  quote('D131-6-1', 'LEGIARTI000036475110', 'La durée de l\'exonération des cotisations dues par les personnes bénéficiant de l\'aide à la création et à la reprise d\'entreprise', 'douze mois', 'text', 'Shows that the article D756-5 names as the rate base no longer carries the micro-social rates in the bounded set.'),
  { kind: 'diff_excerpt', article: null, article_version_id: null, quote_or_values: `existing_tests at G2 (the before tree): regression case "DROM 3" (auto-entrepreneur.yaml: outre-mer: oui, "${"entreprise . durée d'activité . trimestres civils: 1"}", CA 20000 €/an, revenus mixtes) is recorded in auto-entrepreneur.test.ts.snap with "${snapLine}" and the same cotisations as the non-DROM case "DROM 1" (321), i.e. the maintainers' own fixture had captured the métropole rate for a first-period DROM auto-entrepreneur.` },
]

const answer = {
  task: 'R3',
  commit: meta.commit,
  label: 'MISMATCH',
  confidence: 'high',
  rationale: `The commit re-indents the four DROM replacement rules out of the body of the private rule \`seconde période\` into the \`avec:\` of \`dirigeant . auto-entrepreneur . DROM\` (and renames \`service BIC\` to \`taux service BIC\`). Because publicodes drops unknown rule-body keys, those rules did not exist at G2 (list: ${lB.length} -> ${lA.length} names): a DROM auto-entrepreneur was charged the métropole rates (23,1 % BNC, 23,2 % CIPAV, 21,2 % service BIC, 12,3 % vente at 01/10/2024) in every period, which D756-5 does not allow. After the change the D756-5 reductions apply again and, for vente (2,1/6,2/8,2 %) and service BIC (3,6/10,6/14,2 %), the engine values equal D756-5 fractions x the D613-4 rates in force rounded up to the tenth. But the BNC and CIPAV constants were not re-derived from the D613-4 version in force since 2024-07-01 (LEGIARTI000049624068: e) 23,1 %, b) 23,2 %): the engine gives 3,6/10,6/14,1 % (BNC) and 7,1/10,6/14,2 % (CIPAV) where the text gives 3,9/11,6/15,4 % and 7,8/11,6/15,5 %. The change is a genuine semantic fix in the right direction, yet the library still fails to compute what the text in force requires for the two liberal categories, so it is a MISMATCH, not a harmless refactor and not an implementation choice the text leaves open (the rule's own description says the DROM rates are fractions of the "taux pleins de métropole").`,
  evidence,
  expected_values_if_mismatch: mism,
  expected_values_table: { in_force_rates_D613_4_v5: inForce, expected_DROM_rates_after_rounding_up: expected, rule_constants_vs_pre_2024_07_rates: consistency },
  outside_bounded_set: [
    'L. 756-5 (legal basis of the DROM micro-social reduction; D756-5 only gives the fractions) and L. 751-1 (list of the collectivités covered) - not in the set.',
    "L. 611-1 2° (which categories get 1/6 rather than 1/3 in the first period; decides whether a BNC profession libérale non réglementée is at 3,9 % or 7,7 % in period a) - not in the set.",
    'The renumbering/transfer instruments that moved L. 133-6-8 to L. 613-7 and the micro-social rate table from D. 131-6-1 to D. 613-4 (D756-5 still cites the old numbers; in S5, D131-6-1 LEGIARTI000036475110 is the ACRE article) - not in the set; the derivation assumes the D613-4 rates are the base.',
    'D613-4 versions LEGIARTI000049624097 (2025-01-01) and LEGIARTI000049624125 (2026-01-01): ids and dates only, no text in S5 - abstain on the DROM rates expected from 2025 (the base rules already encode 24,6 / 26,1 % for BNC, while the DROM constants stay flat at 3,6 %).',
    'D613-4 versions before 2024-07-01 (LEGIARTI000046714712 etc.): no text in S5, so the statement that the rule constants derive from 21,1 / 21,2 % rests on the engine values at 01/06/2024, not on quoted law.',
    'The Urssaf DROM guide (PDF) and FAQ the rule cites as références - external sources, not in the corpus.',
  ],
  approval: 'none recorded',
  notes: `Before-tree = G2 3a4091ae1caf exactly (blob sha1 of both files = patch a-side f760e73cc / 741068f66); after-tree = G2 + diff.patch applied with patch -p1 in work/proposals/R3 (blobs = b-side 3d217c4d4 / a20c444d8; diff -rq shows only those two files). The 6-space nesting is absent at G1 2a0e452617fc (2024-07-16, 4-space file, rules siblings of \`seconde période\`), where the G1-era results (work/engine/results_R2_after_T1a_rates.jsonl, DROM_Q8_BNC@01-06-2024) show the reduced 3,6 %; HISTORY.txt lists 05334b12 "refactor(auto-entrepreneur): Corrige l'indentation des règles AE" (2024-09-02) between the two pins, so the regression most likely entered there and lived in the published library for ~5 weeks. Period conditions were not changed by the commit: \`première période\` = trimestres civils <= 8 matches D756-5 a) (quarter of affiliation + "septième trimestre civil qui suit"), \`seconde période\` = années civiles <= 3 matches b), sinon = c). Engine pitfall: \`entreprise . durée d'activité . *\` (mécanisme durée) counts up to the real clock, not the situation \`date\` (01/01/2024 gave 12 trimestres / 3 années at date 01/10/2024), so the checks set trimestres civils / années civiles explicitly. Floating artefacts (81.99999999999999 €/mois) are engine arithmetic, not rule semantics. No approval, review or ratification record exists in the corpus.`,
  self_reported_tool_calls: TOOL_CALLS,
}
mkdirSync('output', { recursive: true })
writeFileSync('output/answer.json', JSON.stringify(answer, null, 2) + '\n')
console.log('written output/answer.json;', 'evidence', evidence.length, 'mismatch rows', mism.length, 'list', lB.length, '->', lA.length)
console.log('expected table', JSON.stringify(expected))
console.log('consistency', JSON.stringify(consistency))
console.log('specs', JSON.stringify(specSummary.map(s => [s.spec, s.differing_cells, s.differing_checks.length])))
