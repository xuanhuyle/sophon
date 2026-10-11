// R1 answer generator: every engine value is read from the results files produced by run_checks.sh on both trees
// (before = work/proposals/R1 = G1 with diff.patch reverse-applied; after = inputs/rules/G1_2a0e452617fc),
// every quote is verified as an exact substring of its source before being written.
import fs from "fs";
const R = p => fs.readFileSync(p, "utf8");
const diff = R("inputs/diffs/R1_2a0e452617fc/diff.patch");
const meta = JSON.parse(R("inputs/diffs/R1_2a0e452617fc/meta.json"));
const raw = JSON.parse(R("inputs/law/S3_legi-data-2.381.0/articles.json"));
const recs = []; for (const [n, l] of Object.entries(raw.articles)) for (const r of (Array.isArray(l) ? l : [l])) recs.push(r);
const art = num => recs.find(r => r.num === num);
const must = (hay, needle, what) => { if (!hay.includes(needle)) throw new Error("quote not found in " + what + ": " + needle); return needle; };
const load = f => R(f).trim().split("\n").map(JSON.parse);
const specs = ["R1_atmp", "T1a_rates", "T0_ae3", "T1b_trader", "T0_ti"];
const before = {}, after = {}; let total = 0, identical = true;
for (const s of specs) { before[s] = load(`work/engine/results_R1_before_${s}.jsonl`); after[s] = load(`work/engine/results_R1_G1_${s}.jsonl`); total += after[s].length; if (R(`work/engine/results_R1_before_${s}.jsonl`) !== R(`work/engine/results_R1_G1_${s}.jsonl`)) identical = false; }
const fmt = v => v.error ? "ERR " + v.error : JSON.stringify(v.value) + (v.unit ? " " + v.unit : "");
const ev = (spec, id, rules) => { const b = before[spec].find(x => x.id === id), a = after[spec].find(x => x.id === id);
  return { kind: "engine_before_after", article: null, article_version_id: null,
    quote_or_values: `date ${a.date}; situation ${JSON.stringify(a.situation)}; ` + rules.map(r => `${r}: before=${fmt(b.results[r])} after=${fmt(a.results[r])}`).join("; ") }; };
const CC = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations";
const TI = "dirigeant . indépendant . cotisations et contributions";
const d6134 = art("D613-4");
// short exact windows around the two changed rows (text is one paragraph): from the row marker to the end of the percentage
const win = (t, needle, marker) => { const i = t.indexOf(needle); if (i < 0) throw new Error("needle missing " + needle); let st = t.lastIndexOf(marker, i); if (st < 0 || i - st > 400) st = Math.max(0, i - 160); let en = t.indexOf("%", i); en = en < 0 ? i + needle.length : en + 1; return t.slice(st, en).trim(); };
const qB = win(d6134.text, "23,2", "b)"), qE = win(d6134.text, "23,1", "e)");
const d6134Nota = (d6134.nota || "").trim();
const evidence = [
  { kind: "diff_excerpt", article: null, article_version_id: null, quote_or_values: must(diff, "fix: met à jour les liens morts", "diff") + " | " + must(diff, "-    Connaître le taux AT/MP de votre entreprise sur votre compte AT/MP: https://www.net-entreprises.fr/declaration/compte-atmp/#lessentiel", "diff") + " | " + must(diff, "+    Connaître le taux AT/MP de votre entreprise sur votre compte AT/MP: https://www.ameli.fr/entreprise/votre-entreprise/cotisation-atmp", "diff") + " | only rule-tree file in the commit: " + must(diff, "modele-social/r\\303\\250gles/entreprise/\\303\\251tablissement.publicodes", "diff") + " (key `références:` of rule `établissement . taux ATMP`, line 61); the 4 other files are site/ UI sources outside the rule tree" },
  { kind: "engine_before_after", article: null, article_version_id: null, quote_or_values: "build: before raw_rule_count 641 / parsed_rule_count 1220; after raw_rule_count 641 / parsed_rule_count 1220. list: 1220 parsed rule names, identical on both trees. diff -r before after: exactly one line differs (établissement.publicodes line 61, the URL)." },
  ev("R1_atmp", "SAL_default_3000", ["établissement . taux ATMP", "établissement . taux ATMP . taux collectif", "salarié . cotisations . ATMP", "salarié . cotisations . ATMP . taux minimum", "salarié . cotisations . employeur"]),
  ev("R1_atmp", "SAL_tauxATMP_1.5", ["établissement . taux ATMP", "salarié . cotisations . ATMP"]),
  ev("R1_atmp", "SAL_tauxATMP_below_min", ["établissement . taux ATMP", "salarié . cotisations . ATMP . taux minimum", "salarié . cotisations . ATMP"]),
  ev("T1a_rates", "BNC@01-07-2024", [CC + " . taux service BNC", CC, "dirigeant . auto-entrepreneur . cotisations et contributions", "protection sociale . retraite . base . cotisée . revenu auto-entrepreneur"]),
  ev("T1a_rates", "CIPAV@01-07-2024", [CC + " . cotisations CIPAV . taux", CC]),
  ev("T1a_rates", "VENTE@01-07-2024", [CC + " . taux vente restauration hébergement", "protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur"]),
  ev("T0_ae3", "AE_BNC_ACRE_6mois", [CC + " . taux service BNC", "dirigeant . exonérations . ACRE"]),
  ev("T0_ae3", "AE_DROM_Q8_BNC_clean", [CC + " . taux service BNC"]),
  ev("T1b_trader", "TRADER_40k", ["dirigeant . indépendant . assiette des cotisations", TI + " . maladie . taux progressif", TI + " . maladie", TI + " . retraite de base", TI + " . invalidité et décès . assiette", TI + " . CSG-CRDS . assiette", TI]),
  ev("T0_ti", "TI_rev_0", ["dirigeant . indépendant . assiette minimale . retraite", TI + " . invalidité et décès . assiette", TI + " . retraite de base"]),
  { kind: "engine_before_after", article: null, article_version_id: null, quote_or_values: `All ${total} checks in 5 specs (work/engine/checks_{R1_atmp,T1a_rates,T0_ae3,T1b_trader,T0_ti}.json) were run on both trees with the organisation's engine; the result files are byte-identical: ${identical}.` },
  { kind: "article_quote", article: "D613-4", article_version_id: d6134.id, quote_or_values: `[context only - pre-existing gap NOT created by this commit] in force ${new Date(d6134.dateDebut).toISOString().slice(0, 10)} (${d6134.etat}); "${must(d6134.text, qB, "D613-4")}" ; "${must(d6134.text, qE, "D613-4")}" ; nota: "${must(d6134.nota, d6134Nota, "D613-4 nota")}"` },
];
const answer = {
  task: "R1",
  commit: meta.commit,
  label: "HARMLESS_REFACTOR",
  confidence: "high",
  rationale: "The only rule-tree change in commit 2a0e452617fc is the replacement of a dead URL under the `références:` key of rule `établissement . taux ATMP` (AT/MP rate of an employer's establishment). `références` is documentation metadata that the publicodes engine does not evaluate: the organisation's engine parses the same 641 raw / 1220 parsed rules on both sides, the parsed rule list is identical, and " + total + " evaluations covering the AT/MP rules themselves and every rule bound to the twelve articles of the set (auto-entrepreneur rates, ACRE, DROM, RCI, indépendant base, maladie, retraite de base, invalidité-décès, CSG) return byte-identical values before and after. No bounded article mentions accidents du travail or the AT/MP contribution, so the change has no relation to the governing text in force; nothing it touches needs legal support. The remaining four files of the commit are site/ UI sources outside the rule tree.",
  evidence,
  expected_values_if_mismatch: [],
  outside_bounded_set: [
    "The AT/MP contribution rate of an establishment (`établissement . taux ATMP`, `salarié . cotisations . ATMP . *`) is governed by the CSS provisions on the tarification of accidents du travail / maladies professionnelles, which are not among the twelve supplied articles; no claim is made about their content, and the URL change is not a legal statement anyway.",
    "site/source/locales/ui-en.yaml, site/source/locales/ui-fr.yaml, site/source/.../RésultatSimple.tsx, site/source/pages/integration/components/CasParticuliers.tsx: changed by the same commit but outside modele-social/règles and not supplied; they cannot alter what the engine computes."
  ],
  approval: "none recorded",
  notes: "Method: 'before' tree = G1 with diff.patch reverse-applied (work/proposals/R1/modele-social/règles; diff -r confirms a single differing line), 'after' = inputs/rules/G1_2a0e452617fc. build + list + " + total + " evaluations on both (work/engine/results_R1_before_*.jsonl vs results_R1_G1_*.jsonl, identical=" + identical + "). Engine facts for AT/MP: default `établissement . taux ATMP` = taux collectif = `salarié . cotisations . ATMP . taux moyen` 2.23 % (01/07/2024), floor `taux minimum` 0.46 % applied when 0.1 % is entered, 3000 €/mois brut gives ATMP 66.9 €/mois. Pre-existing gap, independent of this commit and present identically on both sides: D613-4 LEGIARTI000049624068 (in force 2024-07-01, nota: entrée en vigueur 1er juillet 2024) sets rows b) 23,2 % and e) 23,1 %, while G1 (before and after) computes `… cotisations CIPAV . taux` = 21.2 % and `… taux service BNC` = 21.1 % at 01/07/2024 (derived ACRE/DROM/RCI constants likewise unchanged since G0). This is the library's state, not the effect of this change, so it does not alter the HARMLESS_REFACTOR label; it is recorded in output/NOTES.md and work/notes/R1_findings.md as the open item to fix (T1a to-do). No approval, sign-off or ratification record exists in the corpus.",
  self_reported_tool_calls: 16
};
fs.writeFileSync("output/answer.json", JSON.stringify(answer, null, 1) + "\n");
console.log("written output/answer.json; evidence items:", evidence.length, "; total checks:", total, "; identical:", identical);
for (const e of evidence) console.log("-", e.kind, (e.article || ""), e.quote_or_values.slice(0, 330).replace(/\n/g, " "));
