// Builds output/answer.json for R5 (commit c14ee26d0c67). Quotes are verified as exact substrings of the S10 record text/nota; engine values are read from the result files.
import fs from 'fs';
const S = JSON.parse(fs.readFileSync('inputs/law/S10_legi-data-2.572.0/articles.json', 'utf8'));
const rec = num => { const r = S.articles[num]; const a = Array.isArray(r) ? r.find(x => x.etat === 'VIGUEUR') || r[0] : r; return a; };
const iso = ms => new Date(ms).toISOString().slice(0, 10);
const rd = f => fs.readFileSync(f, 'utf8').trim().split('\n').map(JSON.parse);
const B = rd('work/engine/results_R5_parent_mayotte.jsonl'), A = rd('work/engine/results_R5_after_mayotte.jsonl');
const P = 'indépendant . cotisations et contributions';
const quote = (num, startMarker, endMarker, field = 'text') => {
  const r = rec(num); const t = String(r[field] ?? r.notas ?? ''); const i = t.indexOf(startMarker); if (i < 0) throw new Error(`start marker not found in ${num}.${field}: ${startMarker}`);
  const j = t.indexOf(endMarker, i); if (j < 0) throw new Error(`end marker not found in ${num}.${field}: ${endMarker}`);
  const q = t.slice(i, j + endMarker.length); if (!t.includes(q)) throw new Error('not substring'); 
  return { kind: 'article_quote', article: num + (field === 'text' ? '' : ' (nota)'), article_version_id: r.id, in_force: iso(r.dateDebut), quote_or_values: q };
};
const val = (R, id, rule) => { const row = R.find(x => x.id === id); const v = row.results[rule]; return v.error ? 'ERR' : (v.value === null ? 'null' : v.value) + (v.unit ? ' ' + v.unit : '') + (v.missing ? ' [missing ' + v.missing + ']' : ''); };
const sit = id => { const row = A.find(x => x.id === id); return JSON.stringify(row.situation); };
const eng = (id, rule, note) => ({ kind: 'engine_before_after', article: 'D136-5', article_version_id: rec('D136-5').id, rule, situation: sit(id), date: A.find(x => x.id === id).date, before: val(B, id, rule), after: val(A, id, rule), quote_or_values: `before=${val(B, id, rule)} ; after=${val(A, id, rule)}${note ? ' ; ' + note : ''}` });
const mayCount = Object.values(S.articles).flat().reduce((n, r) => n + ((String(r.text) + String(r.nota ?? '')).match(/Mayotte/gi) || []).length, 0);
const evidence = [
  { kind: 'diff_excerpt', article: 'D136-5', article_version_id: rec('D136-5').id, quote_or_values: "modele-ti/règles/indépendant/cotisations-et-contributions/cotisations-et-contributions.publicodes, rule `indépendant . cotisations et contributions . assiette CSG-CRDS . abattement` (valeur: 26% * revenu brut): `-      plancher: 1.76% * plafond sécurité sociale . annuel` / `-      plafond: 130% * plafond sécurité sociale . annuel` replaced by `plancher: { non applicable si: établissement . commune . département . outre-mer . Mayotte, valeur: 1.76% * plafond sécurité sociale . annuel }` and `plafond: { non applicable si: établissement . commune . département . outre-mer . Mayotte, valeur: 130% * plafond sécurité sociale . annuel }`. stat.txt also lists site/test/modele-ti/assiettes.test.ts (+26) which is not in diff.patch. The rule's `références:` still cite only L136-3 and D136-5; no Mayotte source was added." },
  quote('L136-3', "III.-L'assiette résultant", "l'article L. 241-3 ."),
  quote('D136-5', 'I. - Le montant plancher', "premier alinéa de l'article L. 241-3. II. - Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale mentionné au premier alinéa de l'article L. 241-3."),
  quote('D136-5', "ces dispositions s'appliquent au calcul des cotisations et des contributions dues par les travailleurs indépendants non agricoles", "1er janvier 2025", 'nota'),
  quote('L131-6', 'I.-Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles', "sont assises sur l'assiette définie à l'article L. 136-3."),
  { kind: 'article_quote', article: 'all 12 bounded articles (S10, legi-data 2.572.0)', article_version_id: Object.values(S.articles).flat().filter(r => r.etat === 'VIGUEUR').map(r => r.num + '=' + r.id).join(', '), quote_or_values: `Negative finding: the string "Mayotte" occurs ${mayCount} times in the text and nota of the 12 bounded records. None of them contains a territorial clause for Mayotte; the bounded set cannot say whether L136-3 III / D136-5 govern a travailleur indépendant established at Mayotte.` },
  eng('MAY_AC_1000@25', P + ' . assiette CSG-CRDS . abattement', 'floor 1,76 % x 33 852 €/an (Mayotte PSS 2 821 €/mois) = 596 €/an no longer applied; 26 % x 1 000 = 260'),
  eng('MAY_AC_1000@25', P + ' . assiette sociale'),
  eng('MAY_AC_1000@25', P + ' . cotisations'),
  eng('MAY_AC_300000@25', P + ' . assiette CSG-CRDS . abattement', 'cap 130 % x 33 852 = 44 008 €/an no longer applied; 26 % x 300 000 = 78 000'),
  eng('MAY_AC_300000@25', P + ' . assiette sociale'),
  eng('MAY_AC_300000@25', P + ' . cotisations'),
  eng('MAY_AC_300000@25', P + ' . cotisations . maladie-maternité-invalidité-décès-autonomie'),
  eng('MAY_AC_300000@25', P),
  eng('MAY_AC_2000@26', P + ' . assiette CSG-CRDS . abattement', 'floor 1,76 % x 36 264 (Mayotte PSS 2026 3 022 €/mois) = 638 no longer applied'),
  eng('MAY_AC_300000@26', P + ' . assiette sociale'),
  eng('MAY_AC_300000@26', P),
  eng('MAY_PLNR_300000@25', P + ' . cotisations . retraite de base'),
  eng('MAY_AC_1000@25', P + ' . CSG-CRDS', 'CSG-CRDS is non applicable at Mayotte in both trees: the carve-out only changes the cotisations base'),
  eng('MAY_AC_20000@25', P + ' . assiette sociale', 'middle revenue: floor and cap do not bind, identical'),
  eng('PARIS_AC_2000@25', P + ' . assiette CSG-CRDS . abattement', 'métropole control: floor 1,76 % x 47 100 = 829 still applied, identical'),
  eng('PARIS_AC_300000@25', P + ' . assiette CSG-CRDS . abattement', 'métropole control: cap 130 % x 47 100 = 61 230 still applied, identical'),
  eng('METRO_unset_AC_2000@25', P + ' . assiette sociale', 'commune not given (missing variable): identical, no regression for unanswered département'),
  eng('MAY_AC_2000@24', P + ' . assiette CSG-CRDS', 'pre-reform date: assiette unchanged (the `abattement` sub-rule is only consumed by the après-réforme branch)'),
];
const answer = {
  task: 'R5', commit: 'c14ee26d0c67bab90354db32ff1f51879ea3c5e8', label: 'UNRESOLVED', confidence: 'medium',
  rationale: "The commit is a real semantic change, not a refactor: for a travailleur indépendant whose établissement is at Mayotte, the 26 % abattement of `indépendant . cotisations et contributions . assiette CSG-CRDS` is no longer floored at 1,76 % nor capped at 130 % of the (Mayotte) PASS, so the post-reform cotisations base (`assiette sociale`, built on `assiette CSG-CRDS`) and every cotisation on it change at low revenue (floor) and above ~169 000 €/an (cap): engine 118/850 cells differ, all in Mayotte situations; métropole values are byte-identical and CSG-CRDS itself is non applicable at Mayotte in both trees. The bounded articles in force (L136-3 III LEGIARTI000051284498 and D136-5 LEGIARTI000049899286, L131-6 LEGIARTI000048683707) impose the floor and cap without any territorial exception, but none of the 12 bounded records mentions Mayotte: whether L136-3/D136-5 govern a TI established at Mayotte at all (the CSS applies there only through the Mayotte-specific texts, under which the tree already treats CSG-CRDS as non applicable and uses a separate PSS and separate rates) is decided by texts outside the set. The text available therefore neither supports nor forbids the carve-out, and the commit cites no source for it; I abstain from calling it a mismatch or a legitimate choice.",
  evidence,
  expected_values_if_mismatch: [],
  outside_bounded_set: [
    'The territorial applicability of CSS book I (L136-1 et seq., hence L136-3 and D136-5) and of L131-6 to travailleurs indépendants established at Mayotte: ordonnance n° 96-1122 du 20 décembre 1996 relative à l’amélioration de la santé publique à Mayotte and its application decrees (the Mayotte TI cotisations regime), as amended for the 2025 assiette reform if at all (loi n° 2023-1250 du 26 décembre 2023 art. 18 is only visible here through the nota of L131-6).',
    'Article L241-3 CSS (the national plafond annuel the floor and cap of D136-5 refer to) and the text fixing the separate Mayotte plafond de la sécurité sociale (2 821 €/mois in 2025, 3 022 €/mois in 2026 in the tree): needed to know which PSS the floor/cap should use at Mayotte if they apply.',
    'Article L633-1 CSS (last sentence, the upper bound of the floor named in L136-3 III).',
    'The maintainers’ factual source for “pas de plancher ni de plafond à Mayotte”: not cited in the commit; the tree’s Mayotte notification cites Urssaf “Taux de cotisations - Travailleur indépendant à Mayotte” (taux-cotisations-ti-mayotte.html) and a CSSM leaflet, neither available here.',
    'The added regression test site/test/modele-ti/assiettes.test.ts (+26 lines) is listed in stat.txt but not included in diff.patch.'
  ],
  approval: 'none recorded',
  notes: `Law S10 (legi-data 2.572.0) is identical to S9 on all 12 articles (compare_snapshots.mjs: all "same"). Build OK on both trees, 298 raw / 460 parsed rules on both sides, parsed rule lists identical; the floor/cap are mechanism keys, not rules, so they cannot be evaluated separately. Mayotte, 2025 (PSS 2 821 €/mois -> PASS 33 852 €/an): before, abattement = max(596, min(44 008, 26 % x RB)); after, abattement = 26 % x RB. Revenu brut 1 000 €/an: abattement 596 -> 260, assiette sociale 404 -> 740, cotisations 434 -> 455 €/an. Revenu brut 300 000: abattement 44 008 -> 78 000, assiette sociale 255 992 -> 222 000, cotisations 23 518 -> 20 791, total 23 616 -> 20 889 €/an. 2026 (PASS 36 264): floor 638 / cap 47 143 removed, e.g. RB 300 000: assiette 252 857 -> 222 000. Identical: all métropole checks (floor 829 / cap 61 230 in 2025, 846 / 62 478 in 2026 still applied), Mayotte middle revenues (2 300 to 169 000), pre-reform dates. If L136-3 III and D136-5 do apply to Mayotte TI as written, the after-state understates the abattement floor (expected 1,76 % PASS: 596 €/an with the Mayotte PSS, 829 €/an with the L241-3 national PSS, 2025) and ignores the cap (44 008 / 61 230) -> that would be a MISMATCH; if the Mayotte regime excludes them, the change is legitimate. The bounded text cannot decide, hence UNRESOLVED. Side observations for maintainers: (1) the before-state already used the Mayotte PSS for a floor/cap that D136-5 defines on the L241-3 plafond; (2) the changed rule's références still cite only L136-3 and D136-5, which contain no Mayotte exception, so the rule now contradicts its own citations; (3) the 26 % abattement itself is kept at Mayotte while CSG-CRDS (the contribution L136-3 defines the base of) is non applicable there, a combination the bounded text does not describe. No proposal made (nothing in the bounded set to anchor one). Approval: none recorded.`,
  self_reported_tool_calls: 0,
};
const n = Number(process.argv[2] || 0); answer.self_reported_tool_calls = n;
fs.mkdirSync('output', { recursive: true });
fs.writeFileSync('output/answer.json', JSON.stringify(answer, null, 1));
console.log('OK evidence items:', evidence.length, '| Mayotte occurrences in law:', mayCount);
for (const e of evidence) if (e.kind === 'article_quote' && !e.quote_or_values.startsWith('Negative')) console.log(e.article, e.article_version_id, e.in_force, '|', e.quote_or_values.slice(0, 90) + '...');
for (const e of evidence) if (e.kind === 'engine_before_after') console.log(e.rule.replace(P, 'P'), '@', e.date, ':', e.quote_or_values.slice(0, 70));
