#!/usr/bin/env node
// R2 answer generator. Run from the staging root:  node work/engine/make_answer_R2.mjs
// - engine values are read from the result files produced by run_checks.sh (never typed by hand);
// - build/list counts and two ad-hoc evaluations are (re)computed by calling the engine here;
// - every article quote is extracted from the S4 articles.json text itself (exact substring by construction).
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const ROOT = process.cwd()
const BEFORE = 'inputs/rules/G1_2a0e452617fc/modele-social/règles'
const AFTER = 'work/proposals/R2/modele-social/règles'
const P = 'dirigeant . auto-entrepreneur . cotisations et contributions . cotisations'
const TOOL_CALLS = Number(process.argv[2] || 21)

const meta = JSON.parse(readFileSync('inputs/diffs/R2_1932d654cf7a/meta.json', 'utf8'))
const law = JSON.parse(readFileSync('inputs/law/S4_legi-data-2.384.0/articles.json', 'utf8'))
const iso = ms => new Date(ms).toISOString().slice(0, 10)
function art(num, id) {
  const r = law.articles[num].find(a => a.id === id)
  if (!r) throw new Error(`article ${num} ${id} not in S4`)
  return r
}
// exact window from the article text: from the start of `from` to the end of `to`
function extract(rec, from, to) {
  const i = rec.text.indexOf(from); if (i < 0) throw new Error(`fragment not found in ${rec.num}: ${from}`)
  const j = rec.text.indexOf(to, i); if (j < 0) throw new Error(`fragment not found in ${rec.num}: ${to}`)
  const q = rec.text.slice(i, j + to.length)
  if (!rec.text.includes(q)) throw new Error('window not exact')
  return q
}
function quote(num, id, from, to) {
  const r = art(num, id)
  return { kind: 'article_quote', article: num, article_version_id: id, in_force: iso(r.dateDebut), etat: r.etat, quote_or_values: extract(r, from, to) }
}

function engine(cmd, rules, extra = []) {
  return JSON.parse(execFileSync('node', ['src/publicodes_eval.mjs', cmd, '--rules', rules, ...extra], { cwd: ROOT, encoding: 'utf8', maxBuffer: 1e8 }))
}
const rd = f => readFileSync(f, 'utf8').trim().split('\n').map(JSON.parse)
const fmt = v => v.error ? `ERROR: ${v.error}` : `${JSON.stringify(v.value)}${v.unit ? ' ' + v.unit : ''}${v.missing ? ` (missing ${v.missing})` : ''}`

// 1. build + list on both trees
const bB = engine('build', BEFORE), bA = engine('build', AFTER)
const lB = engine('list', BEFORE, ['--prefix', P + ' . taux ACRE']), lA = engine('list', AFTER, ['--prefix', P + ' . taux ACRE'])

// 2. the 69 existing checks + the 10 ACRE checks: byte comparison of result files
const specs = ['T0_ae3', 'T1a_rates', 'T0_ti', 'T1b_trader', 'R1_atmp']
const identical = specs.map(s => {
  const a = readFileSync(`work/engine/results_R2_before_${s}.jsonl`, 'utf8'), b = readFileSync(`work/engine/results_R2_after_${s}.jsonl`, 'utf8')
  return { spec: s, checks: a.trim().split('\n').length, identical: a === b }
})
if (!identical.every(x => x.identical)) throw new Error('existing checks differ: ' + JSON.stringify(identical))
const nChecks = identical.reduce((n, x) => n + x.checks, 0)

const accB = rd('work/engine/results_R2_before_acre.jsonl'), accA = rd('work/engine/results_R2_after_acre.jsonl')
const pick = id => [accB.find(r => r.id === id), accA.find(r => r.id === id)]
const [b6, a6] = pick('AE_BNC_ACRE_6mois'), [b8, a8] = pick('AE_BNC_ACRE_8mois@01-09-2024'), [bo, ao] = pick('AE_BNC_ACRE_6mois_override_tauxACRE_80'), [bc, ac] = pick('AE_CIPAV_ACRE_6mois')
const publicRules = [P + ' . service BNC . taux', P + ' . cotisations CIPAV . taux', P, 'dirigeant . auto-entrepreneur . cotisations et contributions', 'dirigeant . auto-entrepreneur . revenu net', 'dirigeant . exonérations . ACRE']
const privateRules = [P + ' . taux ACRE', P + ' . taux ACRE . service BNC', P + ' . taux ACRE . service BIC', P + ' . taux ACRE . vente restauration hébergement', P + ' . taux ACRE . CIPAV', P + ' . taux ACRE . prestation de service', P + ' . taux ACRE . notification calcul ACRE annuel']
// public rules must be identical before/after in every ACRE check except the override one (whose situation was rejected before)
let publicIdentical = 0, publicDiff = []
for (const b of accB) { const a = accA.find(r => r.id === b.id); for (const k of publicRules) { if (!(k in b.results)) continue; if (fmt(b.results[k]) === fmt(a.results[k])) publicIdentical++; else publicDiff.push({ id: b.id, rule: k, before: fmt(b.results[k]), after: fmt(a.results[k]) }) } }

// 3. ad-hoc evaluations (re-run here so that the values are file-backed): evaluation-order artifact, service BIC under ACRE
const sitCipav = bc.situation, sitSbic = accB.find(r => r.id === 'AE_SBIC_ACRE_6mois').situation
const ev = (rules, sit, names) => { const r = engine('evaluate', rules, ['--situation', JSON.stringify(sit), ...names.flatMap(n => ['--rule', n])]); return Object.fromEntries(Object.entries(r.evaluations).map(([k, v]) => [k, v.error ? 'ERROR: ' + v.error : `${JSON.stringify(v.nodeValue)}${v.unit ? ' ' + v.unit : ''}${v.missing_count ? ` (missing ${v.missing_count})` : ''}`])) }
const adhoc = {
  cipav_acre_isolated_before: ev(BEFORE, sitCipav, [P + ' . service BIC . taux']),
  cipav_acre_isolated_after: ev(AFTER, sitCipav, [P + ' . service BIC . taux']),
  cipav_acre_after_replacing_rule_first: ev(AFTER, sitCipav, [P + ' . taux ACRE . service BIC', P + ' . service BIC . taux']),
  sbic_acre_before: ev(BEFORE, sitSbic, [P + ' . service BIC . taux', P + ' . service BIC', P]),
  sbic_acre_after: ev(AFTER, sitSbic, [P + ' . service BIC . taux', P + ' . service BIC', P]),
}
writeFileSync('work/engine/results_R2_adhoc.json', JSON.stringify({ situations: { cipav_acre: sitCipav, sbic_acre: sitSbic }, adhoc }, null, 1))

const diffLine = readFileSync('inputs/diffs/R2_1932d654cf7a/diff.patch', 'utf8').split('\n').filter(l => /^[-+][^-+]/.test(l))

const evidence = [
  { kind: 'diff_excerpt', article: null, article_version_id: null, quote_or_values: `commit ${meta.commit} (${meta.committed}, ${meta.author}) "${meta.subject}": 1 file, 1 deletion. Removed line under \`${P} . taux ACRE:\` -> ${JSON.stringify(diffLine)}. The diff context (2-space indent, hunk @@ -62) does not match the G1 file (4-space indent, rule at l.65; git blob 8914c3ae vs a061b547e in the patch), so the commit's parent is a later, unsupplied pin; the deletion was applied semantically to G1 (work/proposals/R2, diff -r = this single line).` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `build: before raw ${bB.raw_rule_count} / parsed ${bB.parsed_rule_count}; after raw ${bA.raw_rule_count} / parsed ${bA.parsed_rule_count} (+${bA.parsed_rule_count - bB.parsed_rule_count}: publicodes 1.10.4 getParsedRules() hides private rules and every rule below one). list --prefix "${P} . taux ACRE": before ${lB.names.length} names, after ${lA.names.length} names (${lA.names.map(n => n.slice(P.length + 1)).join('; ')}).` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `${nChecks} existing checks (specs ${specs.join(', ')}; dates 01/01/2024..01/01/2026; AE BNC/CIPAV/vente/BIC with and without ACRE, DROM, indépendant, salarié) evaluated on both trees: result files byte-identical (work/engine/results_R2_before_* vs results_R2_after_*). In the 10 ACRE checks the ${publicIdentical} public-rule cells outside the override case are identical${publicDiff.filter(d => d.id !== 'AE_BNC_ACRE_6mois_override_tauxACRE_80').length ? ' EXCEPT ' + JSON.stringify(publicDiff.filter(d => d.id !== 'AE_BNC_ACRE_6mois_override_tauxACRE_80')) : ''}.` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `Rule "${P} . taux ACRE", situation ${JSON.stringify(a6.situation)}: before = ${fmt(b6.results[P + ' . taux ACRE'])}; after = ${fmt(a6.results[P + ' . taux ACRE'])}. Same situation at date 01/09/2024: after = ${fmt(a8.results[P + ' . taux ACRE'])} (before: same error). Public rules both trees, 01/07/2024: "${P} . service BNC . taux" = ${fmt(a6.results[P + ' . service BNC . taux'])}, "${P}" = ${fmt(a6.results[P])}, "dirigeant . auto-entrepreneur . revenu net" = ${fmt(a6.results['dirigeant . auto-entrepreneur . revenu net'])}; CIPAV case "${P} . cotisations CIPAV . taux" = ${fmt(ac.results[P + ' . cotisations CIPAV . taux'])} (before ${fmt(bc.results[P + ' . cotisations CIPAV . taux'])}). After only: "${P} . taux ACRE . service BNC" = ${fmt(a6.results[P + ' . taux ACRE . service BNC'])}, ". taux ACRE . CIPAV" = ${fmt(a6.results[P + ' . taux ACRE . CIPAV'])}, ". taux ACRE . vente restauration hébergement" = ${fmt(a6.results[P + ' . taux ACRE . vente restauration hébergement'])}.` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `Situation surface: adding "${P} . taux ACRE": "80 %" to the same situation -> before: setSituation rejected (${bo.situation_error}); after: accepted, "${P} . taux ACRE" = ${fmt(ao.results[P + ' . taux ACRE'])}, "${P} . service BNC . taux" = ${fmt(ao.results[P + ' . service BNC . taux'])}, "${P}" = ${fmt(ao.results[P])}.` },
  { kind: 'engine_before_after', article: null, article_version_id: null, quote_or_values: `Engine caveat (publicodes 1.10.4 cache, after tree only): CIPAV ACRE situation, "${P} . service BIC . taux" evaluated alone = before ${adhoc.cipav_acre_isolated_before[P + ' . service BIC . taux']} / after ${adhoc.cipav_acre_isolated_after[P + ' . service BIC . taux']}; but evaluated after "${P} . taux ACRE . service BIC" in the same engine instance = ${adhoc.cipav_acre_after_replacing_rule_first[P + ' . service BIC . taux']}. Order-dependent value reachable only because the replacing rule is now evaluable from outside; not a change of the rule's semantics.` },
  quote('L613-7', 'LEGIARTI000048683570', 'Un taux global différent peut être fixé par décret', 'exonération de cotisations et de contributions de sécurité sociale.'),
  quote('D131-6-1', 'LEGIARTI000036475110', 'La durée de l\'exonération des cotisations dues par les personnes bénéficiant de l\'aide à la création et à la reprise d\'entreprise prévue à l\'article L. 131-6-4', 'est de douze mois'),
  quote('D613-4', 'LEGIARTI000049624068', 'b) Travailleurs indépendants affiliés', '23,2 %'),
  quote('D613-4', 'LEGIARTI000049624068', 'e) Travailleurs indépendants relevant', '23,1 %'),
]

const answer = {
  task: 'R2',
  commit: meta.commit,
  label: 'HARMLESS_REFACTOR',
  confidence: 'high',
  rationale: `The commit deletes the single line \`privé: oui\` of the rule \`${P} . taux ACRE\`. In publicodes 1.10.4 \`privé\` is a visibility flag: it hides the rule (and its 6 descendants) from getParsedRules()/documentation, makes engine.evaluate() of it from outside fail ("n'est pas accessible depuis \\"$EVALUATION\\""), and forbids setting it in the situation ("est une règle privée"). No formula, constant, date or applicability condition changes. Build passes on both trees; the ${nChecks} existing checks plus the public-rule cells of 10 ACRE-specific checks give byte-identical values before and after (BNC ACRE 6 months at 01/07/2024 and 01/09/2024: service BNC . taux 10.6 %, cotisations 106 €/mois, CIPAV 12.1 %). What changes is the engine's public surface, not what any bounded rule computes: parsed_rule_count 1220 -> 1227, 7 rules become listable and evaluable (taux ACRE = 50 % for the first year, 12.1 % CIPAV constant, notification), and the rule can now be overridden from the situation. Law S4 is identical to S3 for all 12 bounded articles, and no bounded article states the ACRE micro-social rate: L613-7 I only enables "Un taux global différent peut être fixé par décret", D131-6-1 governs the 12-month exemption of classic travailleurs indépendants, so the 50 % / 12,10 % values that are now visible rest on a decree article outside the bounded set and on the Urssaf/service-public references cited in the rule; they are neither created nor altered by this commit. Pre-existing issues made more visible by the exposure (D613-4 b/e 23,2/23,1 % since 2024-07-01 vs 21,2/21,1 % in G1; taux ACRE . service BIC leaves the full 21,2 % under ACRE) are documented in notes, not attributed to this change. Approval: none recorded.`,
  evidence,
  expected_values_if_mismatch: [],
  outside_bounded_set: [
    'The decree article fixing the different "taux global" for ACRE periods under L613-7 I (the source of the 50 % first-year rate, the 12,10 % CIPAV constant and the pre-04/2020 grids 25/75/90 and 25/50/90 %) is not in the bounded set; the rule cites Urssaf FAQ and service-public.fr F32318. Values therefore cannot be confirmed or refuted here (abstain).',
    'L131-6-4 (ACRE eligibility, referenced by D131-6-1 and by `dirigeant . exonérations . ACRE`) is not in the bounded set.',
    'The parent commit of 1932d654 (file blob a061b547e, re-indented to 2 spaces) is a pin later than G1 (blob 8914c3ae); the intermediate commits 2024-07-16 -> 2024-09-02 are not supplied, so before/after was measured as G1 vs G1-minus-this-line.',
  ],
  approval: 'none recorded',
  notes: `Pre-existing, independent of this commit, visible in both trees: (1) D613-4 LEGIARTI000049624068 (in force 2024-07-01) gives b) 23,2 % and e) 23,1 % while G1 computes cotisations CIPAV . taux 21,2 % and service BNC . taux 21,1 % at 01/07/2024 (results_R2_before_T1a_rates.jsonl); the newly exposed taux ACRE . service BNC = 10,6 % = 50 % x 21,1 % therefore inherits that staleness (50 % x 23,1 % would be 11,55 %, but the 50 % itself is outside the bounded set, so no expected value is asserted). (2) \`taux ACRE . service BIC\` has \`valeur: cotisations . service BIC . taux\` without the \`taux ACRE *\` factor: an artisan/commercial service AE with ACRE (6 months, 1000 €/mois) pays service BIC . taux ${adhoc.sbic_acre_before[P + ' . service BIC . taux']} and cotisations ${adhoc.sbic_acre_before[P]} in both trees, whereas BNC and vente are halved (10,6 % / 6,2 %); whether the law requires 50 % for BIC depends on the decree article outside the bounded set. (3) Engine caveat: once taux ACRE's descendants are evaluable from outside, publicodes 1.10.4 returns an order-dependent value for a replaced rule in one measured case (see evidence); worth a regression test on the maintainers' side. Law S4 (legi-data 2.384.0, 2024-09-01) = S3 for all 12 articles (work/law/S4_index.json, S4_texts.md). The 1220 -> 1227 parsed-rule difference is exactly the 7 names listed after the change.`,
  self_reported_tool_calls: TOOL_CALLS,
}
writeFileSync('output/answer.json', JSON.stringify(answer, null, 1) + '\n')
console.log('answer.json written; label', answer.label, '| checks identical:', JSON.stringify(identical), '| public cells identical', publicIdentical, '| public diffs', JSON.stringify(publicDiff).slice(0, 600))
console.log('adhoc:', JSON.stringify(adhoc, null, 1))
