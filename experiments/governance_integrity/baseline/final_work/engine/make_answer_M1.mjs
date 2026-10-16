// M1 answer generator. Quotes are cut out of inputs/law/S7|S8 articles.json by [start,end] anchors (whitespace-tolerant search, then the
// ACTUAL substring of the raw text is kept and re-verified with includes()) => exact substrings by construction.
// Engine values are read from work/engine/results_M1_{G3,proposal}_{ae,acre,drom}.jsonl (produced by run_checks.sh), never typed by hand.
// Usage: node work/engine/make_answer_M1.mjs [tool_calls] > output/answer.json
import fs from "fs";
const d = x => new Date(x).toISOString().slice(0, 10);
const load = p => { const raw = JSON.parse(fs.readFileSync(p, "utf8")); const m = {}; for (const [n, l] of Object.entries(raw.articles)) for (const r of (Array.isArray(l) ? l : [l])) m[n] = r; return { raw, m }; };
const S7 = load("inputs/law/S7_legi-data-2.469.0/articles.json"), S8 = load("inputs/law/S8_legi-data-2.489.0/articles.json");
const V = (S, n) => { const r = S.m[n]; return `${n} ${r.id} (etat ${r.etat}, in force ${d(r.dateDebut)} → ${d(r.dateFin)})`; };
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/ /g, "[\\s\\u00a0]+");
const Q = (S, n, start, end, field = "text") => {
  const t = S.m[n][field] || ""; const re = new RegExp(esc(start) + (end ? "[\\s\\S]*?" + esc(end) : ""), "u"); const m = t.match(re);
  if (!m) throw new Error(`anchor not found in ${n} (${S.raw.legi_data_version}) ${field}: ${start} … ${end}`);
  if (!t.includes(m[0])) throw new Error("quote not substring " + n); return m[0];
};
const cite = (S, n, q, field) => `${V(S, n)}${field ? " [" + field + "]" : ""}: "${q}"`;
// ---- law quotes (S8 = new in force 2026-01-01, S7 = versions in force up to 2025-12-31)
const D4n = "D613-4", D6n = "D613-6";
const q = {
  e26: Q(S8, D4n, "e) Travailleurs indépendants relevant à la fois", "25,6 %"), e25: Q(S7, D4n, "e) Travailleurs indépendants relevant à la fois", "24,6 %"),
  a26: Q(S8, D4n, "a) Travailleurs indépendants appartenant", "12,3 %"), a25: Q(S7, D4n, "a) Travailleurs indépendants appartenant", "12,3 %"),
  b26: Q(S8, D4n, "b) Travailleurs indépendants affiliés", "23,2 %"), b25: Q(S7, D4n, "b) Travailleurs indépendants affiliés", "23,2 %"),
  c26: Q(S8, D4n, "c) Travailleurs indépendant mentionnés", "4 045 euros 6 %"),
  d26: Q(S8, D4n, "d) Travailleurs indépendants appartenant", "21,2 %"), d25: Q(S7, D4n, "d) Travailleurs indépendants appartenant", "21,2 %"),
  nota4: Q(S8, D4n, "s'appliquent au titre des périodes courant à compter du 1 er janvier 2026", null, "nota"),
  nota6: Q(S8, D6n, "s'appliquent au titre des périodes courant à compter du 1 er janvier 2026", null, "nota"),
  ad26: Q(S8, D6n, "-pour les personnes relevant des a et d", "23,60 %"), ad25: Q(S7, D6n, "-pour les personnes relevant des a et d", "29,70 %"),
  bb26: Q(S8, D6n, "-pour les personnes relevant du b", "27,00 %"), bb25: Q(S7, D6n, "-pour les personnes relevant du b", "34,00 %"),
  cc26: Q(S8, D6n, "-pour les personnes relevant du c", "22,30 %"),
  ee26: Q(S8, D6n, "-pour les personnes relevant du e", "25,20 %"), ee25: Q(S7, D6n, "-pour les personnes relevant du e", "32,50 %"),
  drom1: Q(S8, "D756-5", "après arrondi au dixième de pour cent supérieur", "1/3 dans les autres cas"), drom2: Q(S8, "D756-5", "b) 1/2 pour la période", "c) 2/3 à compter de la quatrième année civile d'activité"),
  l6137: Q(S8, "L613-7", "Un taux global différent peut être fixé par décret", "exonération de cotisations et de contributions de sécurité sociale"),
  l6137b: Q(S8, "L613-7", "un taux global fixé par décret pour chaque catégorie d'activité"),
  acre: Q(S8, "D131-6-1", "La durée de l'exonération des cotisations dues", "est de douze mois"),
};
const lien = S8.m[D4n].lienModifications.find(l => l.textCid === "JORFTEXT000052211971");
const LIEN = `${lien.textTitle} (${lien.linkType}, JORF ${lien.datePubliTexte}, signé ${lien.dateSignaTexte}, dateDebutCible ${lien.dateDebutCible})`;
// ---- engine results
const rd = f => Object.fromEntries(fs.readFileSync(f, "utf8").trim().split("\n").map(JSON.parse).map(r => [r.id, r]));
const RES = {}; for (const t of ["G3", "proposal"]) { RES[t] = {}; for (const s of ["ae", "acre", "drom"]) for (const [id, r] of Object.entries(rd(`work/engine/results_M1_${t}_${s}.jsonl`))) RES[t][id] = RES[t][id] ? { ...RES[t][id], results: { ...RES[t][id].results, ...r.results } } : r; }
const cell = (t, id, rule) => { const r = RES[t][id]; if (!r) throw new Error("no check " + id); const c = r.results[rule]; if (!c) throw new Error(`rule ${rule} not in ${id}`); if (c.error) throw new Error(`error ${id} ${rule}: ${c.error}`); return c; };
const fmt = c => c.value === null ? "non applicable" : (typeof c.value === "number" ? `${+c.value.toFixed(4)}${c.unit ? " " + c.unit : ""}` : String(c.value));
const sit = id => RES.G3[id].situation;
const COT = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations";
const EV = (base, rule, law) => {
  const b = `${base}@01-12-2025`, a = `${base}@01-01-2026`;
  return { rule, situation_id: base, situation: Object.fromEntries(Object.entries(sit(a)).filter(([k]) => k !== "date")),
    values: { "G3 @ 01/12/2025": fmt(cell("G3", b, rule)), "G3 @ 01/01/2026": fmt(cell("G3", a, rule)), "proposal @ 01/12/2025": fmt(cell("proposal", b, rule)), "proposal @ 01/01/2026": fmt(cell("proposal", a, rule)) },
    changed_by_proposal_at_2026: fmt(cell("G3", a, rule)) !== fmt(cell("proposal", a, rule)), law_basis: law };
};
const evaluations = [];
const SH = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"];
const cat = { BNC: "service BNC", CIPAV: "service BNC Cipav", SBIC: "service BIC", VENTE: "vente restauration hébergement" };
const rowOf = { BNC: ["e", q.e26, q.e25], CIPAV: ["b", q.b26, q.b25], SBIC: ["d", q.d26, q.d25], VENTE: ["a", q.a26, q.a25] };
const shareOf = { BNC: ["e", q.ee26, q.ee25], CIPAV: ["b", q.bb26, q.bb25], SBIC: ["a et d", q.ad26, q.ad25], VENTE: ["a et d", q.ad26, q.ad25] };
for (const k of Object.keys(cat)) {
  const [row, q26, q25] = rowOf[k];
  evaluations.push(EV(k, `${COT} . ${cat[k]} . taux`, [cite(S8, D4n, q26), cite(S7, D4n, q25), cite(S8, D4n, q.nota4, "nota")]));
  evaluations.push(EV(k, `${COT} . ${cat[k]}`, [`amount = chiffre d'affaires x taux (row ${row} of D613-4)`, cite(S8, D4n, q26)]));
  const [blk, s26, s25] = shareOf[k];
  for (const s of SH) evaluations.push(EV(k, `${COT} . ${cat[k]} . répartition . ${s} . taux de répartition`, [`D613-6 block "${blk}"; the model merges the 'prestations maladie en espèces' line into maladie-maternité and the two D642-3 lines into retraite de base`, cite(S8, D6n, s26), cite(S7, D6n, s25), cite(S8, D6n, q.nota6, "nota")]));
  for (const s of SH) evaluations.push(EV(k, `${COT} . répartition . ${s}`, [`aggregate amount = cotisation x taux de répartition`, cite(S8, D6n, s26)]));
  evaluations.push(EV(k, "protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur", ["depends on répartition . retraite complémentaire (D613-6)", cite(S8, D6n, s26)]));
  evaluations.push(EV(k, "protection sociale . retraite . base . cotisée . revenu auto-entrepreneur", ["depends on the abattement (34 % / 50 % / 71 %) of D613-4, unchanged between the two versions", cite(S8, D4n, q26)]));
  evaluations.push(EV(k, `${COT}`, [cite(S8, D4n, q26)]));
  evaluations.push(EV(k, "dirigeant . auto-entrepreneur . cotisations et contributions", [cite(S8, D4n, q26)]));
}
for (const [k, r] of [["BNC_ACRE", "taux service BNC"], ["CIPAV_ACRE", "taux CIPAV"], ["SBIC_ACRE", "taux service BIC"], ["VENTE_ACRE", "taux vente restauration hébergement"]]) {
  evaluations.push(EV(k, `dirigeant . auto-entrepreneur . Acre . ${r}`, [cite(S8, "L613-7", q.l6137), cite(S8, "D131-6-1", q.acre), "the 50 % factor (taux Acre) has no source in the bounded set"]));
  evaluations.push(EV(k, "dirigeant . auto-entrepreneur . Acre . taux Acre", [cite(S8, "D131-6-1", q.acre)]));
  evaluations.push(EV(k, `${COT} . ${cat[k.replace("_ACRE", "")]} . taux`, ["rate after the Acre `remplace`"]));
}
for (const [k, r] of [["DROM_Q8_BNC", "taux service BNC"], ["DROM_Q12_BNC", "taux service BNC"], ["DROM_Y4_BNC", "taux service BNC"], ["DROM_Q8_CIPAV", "taux CIPAV"], ["DROM_Q8_SBIC", "taux service BIC"], ["DROM_Q8_VENTE", "taux vente restauration hébergement"]])
  evaluations.push(EV(k, `dirigeant . auto-entrepreneur . DROM . ${r}`, [cite(S8, "D756-5", q.drom1), cite(S8, "D756-5", q.drom2), "fraction x D613-4 row, rounded UP to 0.1 point: " + cite(S8, D4n, k.includes("CIPAV") ? q.b26 : k.includes("SBIC") ? q.d26 : k.includes("VENTE") ? q.a26 : q.e26)]));
// ---- rules classification
const rules = []; const notRe = [];
const AF = (rule, article, evidence, extra = {}) => rules.push({ rule, classification: "AFFECTED", confidence: "high", article, evidence, reassessed: true, ...extra });
const UN = (rule, article, evidence, extra = {}) => rules.push({ rule, classification: "UNAFFECTED", confidence: "high", article, evidence, reassessed: true, ...extra });
const vals = (base, rule) => `engine (${base}): G3 01/12/2025 = ${fmt(cell("G3", `${base}@01-12-2025`, rule))}; G3 01/01/2026 = ${fmt(cell("G3", `${base}@01-01-2026`, rule))}; proposal 01/01/2026 = ${fmt(cell("proposal", `${base}@01-01-2026`, rule))}`;
const V4 = V(S8, D4n), V6 = V(S8, D6n);
AF(`${COT} . service BNC . taux`, V4, [cite(S8, D4n, q.e26), cite(S7, D4n, q.e25), cite(S8, D4n, q.nota4, "nota"), LIEN, vals("BNC", `${COT} . service BNC . taux`)], { action: "edit: branch `date >= 01/2026` 26.1% -> 25.6%" });
for (const [s, v26, v25] of [["maladie-maternité", "2,60 % + 1,50 % = 4,10 %", "3,40 %"], ["invalidité-décès", "3,30 %", "3,50 %"], ["retraite de base", "46,40 %", "47,60 %"], ["retraite complémentaire", "21,00 %", "13,00 %"], ["autres contributions", "25,20 %", "32,50 %"]])
  AF(`${COT} . service BNC . répartition . ${s} . taux de répartition`, V6, [cite(S8, D6n, q.ee26), cite(S7, D6n, q.ee25), `2026 share for block e: ${v26} (2025: ${v25})`, vals("BNC", `${COT} . service BNC . répartition . ${s} . taux de répartition`)], { action: "edit: value of the `date >= 01/2026` branch" });
for (const [s, v26, v25] of [["maladie-maternité", "8,80 % + 1,25 % = 10,05 %", "8,90 %"], ["invalidité-décès", "3,15 %", "3,10 %"], ["retraite de base", "43,45 %", "41,80 %"], ["retraite complémentaire", "19,75 %", "16,50 %"], ["autres contributions", "23,60 %", "29,70 %"]]) {
  AF(`${COT} . service BIC . répartition . ${s} . taux de répartition`, V6, [cite(S8, D6n, q.ad26), cite(S7, D6n, q.ad25), `2026 share for block a et d: ${v26} (2025: ${v25})`, vals("SBIC", `${COT} . service BIC . répartition . ${s} . taux de répartition`)], { action: "edit: constant -> variations with a `date >= 01/2026` branch" });
  AF(`${COT} . vente restauration hébergement . répartition . ${s} . taux de répartition`, V6, [cite(S8, D6n, q.ad26), cite(S7, D6n, q.ad25), `2026 share for block a et d: ${v26} (2025: ${v25})`, vals("VENTE", `${COT} . vente restauration hébergement . répartition . ${s} . taux de répartition`)], { action: "edit: constant -> variations with a `date >= 01/2026` branch" });
}
for (const [s, v26, v25] of [["maladie-maternité", "10,60 % + 0,80 % = 11,40 %", "9,30 + 0,90 = 10,20 %"], ["retraite de base", "24,30 % + 5,20 % = 29,50 %", "23,45 + 5,35 = 28,80 %"], ["retraite complémentaire", "30,70 %", "25,60 %"], ["autres contributions", "27,00 %", "34,00 %"]])
  AF(`${COT} . service BNC Cipav . répartition . ${s} . taux de répartition`, V6, [cite(S8, D6n, q.bb26), cite(S7, D6n, q.bb25), `2026 share for block b: ${v26} (2025: ${v25})`, vals("CIPAV", `${COT} . service BNC Cipav . répartition . ${s} . taux de répartition`)], { action: "edit: new `date >= 01/2026` branch" });
UN(`${COT} . service BNC Cipav . répartition . invalidité-décès . taux de répartition`, V6, [cite(S8, D6n, q.bb26), cite(S7, D6n, q.bb25), "block b invalidité-décès: 1,40 % in both versions", vals("CIPAV", `${COT} . service BNC Cipav . répartition . invalidité-décès . taux de répartition`)]);
AF("dirigeant . auto-entrepreneur . DROM . taux service BNC", `${V(S8, "D756-5")} + ${V4}`, [cite(S8, "D756-5", q.drom1), cite(S8, "D756-5", q.drom2), cite(S8, D4n, q.e26), "derived: ceil10(25,6/6) = 4,3 %; 25,6/2 = 12,8 %; ceil10(2/3 x 25,6) = 17,1 % (G3 2026 branch was ceil10 of 26,1 %: 4,4/13,1/17,4)", vals("DROM_Q8_BNC", "dirigeant . auto-entrepreneur . DROM . taux service BNC"), vals("DROM_Q12_BNC", "dirigeant . auto-entrepreneur . DROM . taux service BNC"), vals("DROM_Y4_BNC", "dirigeant . auto-entrepreneur . DROM . taux service BNC")], { confidence: "medium", action: "edit: `date >= 01/2026` branches 4.4/13.1/17.4 % -> 4.3/12.8/17.1 %", caveat: "D756-5 still names 'l'article D. 131-6-1' and 'l'article L. 133-6-8' (pre-2018 numbering); the renumbering to D613-4 / L613-7 is not in the bounded set, and no text publishes the DROM 2026 rates themselves." });
// affected by dependency only (no edit)
const DEP = (rule, base, article, law, extra = {}) => AF(rule, article, [...law, vals(base, rule)], { action: "no edit (value changes through its dependencies)", ...extra });
DEP("dirigeant . auto-entrepreneur . Acre . taux service BNC", "BNC_ACRE", `${V(S8, "L613-7")} + ${V4}`, [cite(S8, "L613-7", q.l6137), cite(S8, D4n, q.e26), "= taux Acre (50 %) x 25,6 % = 12,80 % (G3: 50 % x 26,1 % = 13,05 %)"], { confidence: "medium", caveat: "L613-7 lets a decree fix a DIFFERENT global rate for exoneration periods; no such decree/text is in the set, and the 50 % factor of `taux Acre` has no source in the set. The 12,8 % is the rule's own computation, not a value read in the law: abstention on the legally fixed Acre rate for 2026." });
DEP(`${COT} . service BNC`, "BNC", V4, [cite(S8, D4n, q.e26)]);
DEP(`${COT}`, "BNC", V4, [cite(S8, D4n, q.e26)]);
DEP("dirigeant . auto-entrepreneur . cotisations et contributions", "BNC", V4, [cite(S8, D4n, q.e26)]);
for (const s of SH) DEP(`${COT} . répartition . ${s}`, "BNC", V6, [cite(S8, D6n, q.ee26)]);
DEP("protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur", "BNC", V6, [cite(S8, D6n, q.ee26), "= répartition . retraite complémentaire (contexte ACRE: non) -> changes for every category because every retraite complémentaire share changes", vals("SBIC", "protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur"), vals("VENTE", "protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur")]);
// unaffected, re-examined
UN(`${COT} . service BIC . taux`, V4, [cite(S8, D4n, q.d26), cite(S7, D4n, q.d25), "row d: 21,2 % in both versions", vals("SBIC", `${COT} . service BIC . taux`)]);
UN(`${COT} . vente restauration hébergement . taux`, V4, [cite(S8, D4n, q.a26), cite(S7, D4n, q.a25), "row a: 12,3 % in both versions", vals("VENTE", `${COT} . vente restauration hébergement . taux`)]);
UN(`${COT} . service BNC Cipav . taux`, V4, [cite(S8, D4n, q.b26), cite(S7, D4n, q.b25), "row b: 23,2 % in both versions", vals("CIPAV", `${COT} . service BNC Cipav . taux`)]);
for (const [k, c] of [["SBIC", "service BIC"], ["VENTE", "vente restauration hébergement"], ["CIPAV", "service BNC Cipav"]]) UN(`${COT} . ${c}`, V4, ["amount = CA x unchanged rate", vals(k, `${COT} . ${c}`)]);
UN("protection sociale . retraite . base . cotisée . revenu auto-entrepreneur", V4, [cite(S8, D4n, q.e26), cite(S7, D4n, q.e25), "abattement 34 % (row e), 50 % (d), 71 % (a) identical in both versions; engine identical on both trees at both dates", vals("BNC", "protection sociale . retraite . base . cotisée . revenu auto-entrepreneur"), vals("SBIC", "protection sociale . retraite . base . cotisée . revenu auto-entrepreneur")]);
UN("dirigeant . auto-entrepreneur . DROM . taux service BIC", `${V(S8, "D756-5")} + ${V4}`, [cite(S8, D4n, q.d26), "row d unchanged -> 1/6, 1/2, 2/3 of 21,2 % unchanged", vals("DROM_Q8_SBIC", "dirigeant . auto-entrepreneur . DROM . taux service BIC")]);
UN("dirigeant . auto-entrepreneur . DROM . taux vente restauration hébergement", `${V(S8, "D756-5")} + ${V4}`, [cite(S8, D4n, q.a26), "row a unchanged", vals("DROM_Q8_VENTE", "dirigeant . auto-entrepreneur . DROM . taux vente restauration hébergement")]);
UN("dirigeant . auto-entrepreneur . DROM . taux CIPAV", `${V(S8, "D756-5")} + ${V4}`, [cite(S8, D4n, q.b26), cite(S8, "D756-5", q.drom1), "row b unchanged (23,2 %) -> unaffected by S8. PRE-EXISTING discrepancy kept out of this change: G3 7,1 / 10,6 / 14,2 % vs ceil10 of 1/3, 1/2, 2/3 x 23,2 % = 7,8 / 11,6 / 15,5 %", vals("DROM_Q8_CIPAV", "dirigeant . auto-entrepreneur . DROM . taux CIPAV")], { confidence: "medium" });
UN("dirigeant . auto-entrepreneur . Acre . taux Acre", V(S8, "D131-6-1"), [cite(S8, "D131-6-1", q.acre), "D131-6-1 record byte-identical S7/S8; 50 % factor itself has no source in the set", vals("BNC_ACRE", "dirigeant . auto-entrepreneur . Acre . taux Acre")]);
UN("dirigeant . auto-entrepreneur . Acre . taux service BIC", V4, [cite(S8, D4n, q.d26), "50 % x 21,2 % = 10,6 %, row d unchanged", vals("SBIC_ACRE", "dirigeant . auto-entrepreneur . Acre . taux service BIC")]);
UN("dirigeant . auto-entrepreneur . Acre . taux vente restauration hébergement", V4, [cite(S8, D4n, q.a26), "50 % x 12,3 % = 6,15 -> 6,2 % (arrondi 1 décimale), row a unchanged", vals("VENTE_ACRE", "dirigeant . auto-entrepreneur . Acre . taux vente restauration hébergement")]);
UN("dirigeant . auto-entrepreneur . Acre . taux CIPAV", V4, [cite(S8, D4n, q.b26), "constant 13,90 % since 07/2024 (source outside the set); row b unchanged", vals("CIPAV_ACRE", "dirigeant . auto-entrepreneur . Acre . taux CIPAV")], { confidence: "medium" });
for (const r of ["dirigeant . auto-entrepreneur . Acre", "dirigeant . auto-entrepreneur . DROM", "dirigeant . auto-entrepreneur . Cipav", "dirigeant . exonérations . ACRE"]) UN(r, r.includes("ACRE") || r.endsWith("Acre") ? V(S8, "D131-6-1") : V(S8, "L613-7"), ["applicability switch only; identical on both trees at both dates", vals(r.includes("ACRE") || r.endsWith("Acre") ? "BNC_ACRE" : r.includes("DROM") ? "DROM_Q8_BNC" : "CIPAV", r)]);
// not re-examined: bound to records byte-identical in S7 and S8
const RD = JSON.parse(fs.readFileSync("work/law/M1_S7_S8_record_diff.json", "utf8")).articles;
const same = n => RD[n].record_identical && RD[n].text_sha256_S7 === RD[n].text_sha256_S8;
const NRE = (rule, art, where, quote) => { if (!same(art)) throw new Error(art + " not identical"); const a = RD[art]; rules.push({ rule, classification: "UNAFFECTED", confidence: "high", article: V(S8, art), evidence: [cite(S8, art, quote), `${art} record byte-identical S7/S8 (id ${a.id_S8}, text sha256 ${a.text_sha256_S8.slice(0, 16)}…, same versions/liens/nota) — work/law/M1_S7_S8_record_diff.json`, "Not re-evaluated in M1 (see not_reassessed_rules)."], reassessed: false }); notRe.push({ rule, reason: `Bound to ${art} only (${where}); the ${art} record is byte-identical in S7 and S8 (same id ${a.id_S8}, same text sha256, same articleVersions/lienModifications/nota). The only changed articles (D613-4, D613-6) set the micro-social global rates and their split under L613-7, which this rule does not implement or read. Re-running the engine would only re-test unchanged law against an unchanged pin (G3, same as M0).` }); };
NRE("dirigeant . indépendant . cotisations et contributions . maladie", "D621-2", "références: lines 206/252 of dirigeant/indépendant/cotisations-et-contributions.publicodes", Q(S8, "D621-2", "le taux de base de la cotisation d'assurance maladie et maternité des travailleurs indépendants", null));
NRE("dirigeant . indépendant . cotisations et contributions . invalidité et décès", "D632-1", "références: line 377", Q(S8, "D632-1", "La cotisation annuelle au régime d'assurance invalidité-décès prévue à l'article L. 632-1", null));
NRE("dirigeant . indépendant . assiette minimale . invalidité et décès", "D632-1", "références: dirigeant/indépendant/indépendant.publicodes line 117", Q(S8, "D632-1", "La cotisation annuelle au régime d'assurance invalidité-décès prévue à l'article L. 632-1", null));
NRE("dirigeant . indépendant . cotisations et contributions . retraite de base", "D633-3", "D633-3 barème (R4 line)", Q(S8, "D633-3", "Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %", null));
NRE("dirigeant . indépendant . cotisations et contributions . CSG-CRDS", "L136-3", "L136-3 III abattement 26 % / D136-5 floor-cap", Q(S8, "L136-3", "fait l'objet d'un abattement de 26 %", null));
NRE("dirigeant . indépendant . assiette des cotisations", "L131-6", "L131-6 revenu d'activité", Q(S8, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7", null));
NRE("bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire", "L131-6", "références: bénéficiaire.publicodes line 127", Q(S8, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7", null));
NRE("dirigeant . indépendant . cotisations et contributions . exonérations . ACRE", "D131-6-1", "ACRE exoneration for TI", q.acre);
NRE("salarié . cotisations . exonérations . Acre", "D131-6-1", "références: salarié/exonérations/acre.publicodes line 14", q.acre);
rules.push({ rule: "(none) — D613-4 row c) meublés de tourisme 6 % and D613-6 block c", classification: "NEEDS_REVIEW", confidence: "high", article: V4, evidence: [cite(S8, D4n, q.c26), cite(S8, D6n, q.cc26), "No rule in G3 implements category c (grep: no 'meublés de tourisme' rule); the new text gives it a 6 % rate and its own split. Not proposed here (new rule tree needed; no situation variable exists)."], reassessed: true, action: "none; gap recorded" });
rules.push({ rule: "(none) — D613-5 conjoint collaborateur", classification: "UNAFFECTED", confidence: "high", article: V(S8, "D613-5"), evidence: [cite(S8, "D613-5", Q(S8, "D613-5", "Les cotisations de sécurité sociale dues par le conjoint collaborateur du travailleur indépendant relevant des dispositions de l'article L. 613-7", null)), "record byte-identical S7/S8; no rule implements it at G3"], reassessed: false });
notRe.push({ rule: "(none) — D613-5 / D136-5 / D756-5 II (no implementing rule at G3)", reason: "Records byte-identical S7/S8 (work/law/M1_S7_S8_record_diff.json); nothing in the tree to re-examine." });
// ---- answer
const build = t => JSON.parse(fs.readFileSync(`work/engine/build_M1_${t}.json`, "utf8"));
const cmp = fs.existsSync("work/engine/compare_M1_summary.txt") ? fs.readFileSync("work/engine/compare_M1_summary.txt", "utf8").trim() : "see work/engine/compare_results.mjs output";
const abstentions = [
  { topic: "Acre (ACRE) 2026 global rate for category e (BNC)", value_shown: "12,8 % (= rule `taux Acre` 50 % x 25,6 %, engine on the proposal)", reason: `${cite(S8, "L613-7", q.l6137)}. The decree fixing that different rate (if any) and the source of the 50 % factor are outside the bounded set; the rule's result is reported as a computation, not as a value read in the law.` },
  { topic: "DROM 2026 rates for category e (4,3 / 12,8 / 17,1 %)", value_shown: "derived from D756-5 fractions and rounding", reason: `${cite(S8, "D756-5", q.drom1)}. D756-5 refers to 'D. 131-6-1' / 'L. 133-6-8' (old numbering); the renumbering to D613-4 / L613-7 is not in the set and no text publishes the 2026 DROM rates themselves -> medium confidence, not high.` },
  { topic: "DROM Cipav rates 7,1 / 10,6 / 14,2 % (pre-existing)", value_shown: "unchanged in the proposal", reason: "Not caused by S7->S8 (row b and D756-5 unchanged). ceil10(1/3, 1/2, 2/3 x 23,2 %) would give 7,8 / 11,6 / 15,5 %; left for a dedicated change." },
  { topic: "Category c (meublés de tourisme, 6 %) and D613-5 conjoint collaborateur", value_shown: "none", reason: "No rule exists at G3; implementing them is a new feature, not maintenance of an existing bounded rule." },
  { topic: "Split of 'prestations maladie en espèces' (1,25 / 0,80 / 1,50 %) and of the two D642-3 lines", value_shown: "merged into maladie-maternité and retraite de base", reason: "The model has five répartition buckets; the merge follows the convention G3 already used for block b in 2024/2025 (9,30 + 0,90 = 10,20 %; 23,45 + 5,35 = 28,80 %). Exact per-line amounts are not represented." },
  { topic: "Application in time", value_shown: "`date >= 01/2026` on the simulation date", reason: `${cite(S8, D4n, q.nota4, "nota")}: 'périodes courant à compter du 1er janvier 2026' is read as 'months from January 2026', the tree's existing convention; cotisations on December 2025 turnover declared in January 2026 are not modelled.` },
];
const answer = {
  task: "M1", decision_date: "2026-01-01",
  law_snapshots: { S7: `legi-data ${S7.raw.legi_data_version} published ${S7.raw.published}`, S8: `legi-data ${S8.raw.legi_data_version} published ${S8.raw.published}` },
  rules_pin: "G3 d6c374271727 (committed 2025-12-30 23:52:36 +0100, modele-social 10.0.0 in tree) — same pin as M0; build 722 raw / 1427 parsed rules",
  changed_articles: [
    { article: "D613-4", old: V(S7, D4n), new: V4, modifying_text: LIEN, nota: q.nota4, text_changes: ["row e: '10 000 euros 34 % 6 600 euros 24,6 %' -> '23 609 euros 34 % 15 582 euros 25,6 %' (rate 24,6 % -> 25,6 %)", "turnover thresholds re-indexed: a) 79 828 -> 89 776 euros (revenu 23 150 -> 26 035); b) 35 076 -> 42 586 (23 150 -> 28 107); c) 29 230 -> 31 115 (3 800 -> 4 045); d) 46 300 -> 52 070 (23 150 -> 26 035)", "rates a) 12,3 %, b) 23,2 %, c) 6 %, d) 21,2 % unchanged; abattements 71/34/87/50/34 % unchanged"], quotes: [cite(S8, D4n, q.e26), cite(S7, D4n, q.e25), cite(S8, D4n, q.a26), cite(S8, D4n, q.b26), cite(S8, D4n, q.c26), cite(S8, D4n, q.d26)], versions: "LEGIARTI000049624097 ABROGE_DIFF -> MODIFIE (2025-01-01 → 2026-01-01); LEGIARTI000052218738 VIGUEUR_DIFF -> VIGUEUR (2026-01-01 → 2999-01-01); lien 'Décret n°2024-484 art. 1, 3°' (source) dropped from the current record" },
    { article: "D613-6", old: V(S7, D6n), new: V6, modifying_text: LIEN, nota: q.nota6, text_changes: ["block a et d: 8,90 / 3,10 / 41,80 / 16,50 / 29,70 % -> maladie-maternité 8,80 % + NEW line prestations maladie en espèces 1,25 % / invalidité-décès 3,15 % / vieillesse de base 43,45 % / complémentaire 19,75 % / CSG-CRDS 23,60 %", "block b: 9,30 + 0,90 / 1,40 / 23,45 + 5,35 / 25,60 / 34,00 % -> 10,60 + 0,80 / 1,40 / 24,30 + 5,20 / 30,70 / 27,00 %", "block c: 4,90 / 3,50 / 48,30 / 15,10 / 28,20 % -> 0,00 + 5,10 / 3,80 / 50,20 / 18,60 / 22,30 %", "block e: 3,40 / 3,50 / 47,60 / 13,00 / 32,50 % -> 2,60 + 1,50 / 3,30 / 46,40 / 21,00 / 25,20 %", "every line now names its legal basis (L621-1, L621-2, L632-1/L644-2, D633-3/D642-3, L635-1/L644-1, L136-3)"], quotes: [cite(S8, D6n, q.ad26), cite(S8, D6n, q.bb26), cite(S8, D6n, q.cc26), cite(S8, D6n, q.ee26), cite(S7, D6n, q.ad25), cite(S7, D6n, q.bb25), cite(S7, D6n, q.ee25)], versions: "LEGIARTI000049625405 ABROGE_DIFF -> MODIFIE; LEGIARTI000052218747 VIGUEUR_DIFF -> VIGUEUR (2026-01-01 → 2999-01-01)" }],
  unchanged_articles: ["L131-6", "L136-3", "L613-7", "D131-6-1", "D136-5", "D613-5", "D621-2", "D632-1", "D633-3", "D756-5"].map(n => `${V(S8, n)} — record byte-identical S7/S8 (text sha256 ${RD[n].text_sha256_S8.slice(0, 16)}…)`),
  missing_articles: S8.raw.articles_missing_in_snapshot,
  summary: "Relevant change: YES. Between S7 (2025-10-01) and S8 (2026-01-01) the 2026-01-01 versions of D613-4 (LEGIARTI000052218738) and D613-6 (LEGIARTI000052218747), carried by décret n° 2025-943 du 8 septembre 2025 (JORF 2025-09-09), came into force with their text, applicable to periods from 1 January 2026. D613-4: only row e (BNC non-Cipav) changes rate, 24,6 % -> 25,6 %; rows a/b/c/d keep 12,3 / 23,2 / 6 / 21,2 % (thresholds re-indexed). D613-6: every split changes (a et d, b, c, e). G3 hard-coded unverified 2026 branches (BNC 26,1 %, BNC shares 3/3,25/44,85/17,7/31,20, DROM BNC 4,4/13,1/17,4, Acre BNC 13,05 %) and had NO 2026 branch for the a/d and b shares: all of these are wrong against the new text. The proposal fixes the 26 rate/share rules + DROM BNC; 10 other rules change through dependencies; values before 2026 are untouched (0 differing cells at 01/12/2025).",
  rules, reassessed_rules: rules.filter(r => r.reassessed !== false).map(r => r.rule), not_reassessed_rules: notRe,
  no_change_needed: false,
  no_change_needed_explanation: "Numeric changes are required from 01/01/2026: service BNC . taux 26,1 -> 25,6 %; 19 share rules (5 BNC corrected, 5 BIC + 5 vente given a 2026 branch, 4 Cipav given a 2026 branch); DROM . taux service BNC 2026 branches re-derived. Acre BNC follows (13,05 -> 12,8 %).",
  proposal_dir: "work/proposals/M1/modele-social/règles",
  proposal_summary: "Two files edited (diff work/proposals/M1/M1.diff, 320 lines; re-applicable to a fresh G3 copy with `node work/proposals/M1/apply_M1.mjs <règles>`): dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes (rates/shares, notes, références to L613-7 + D613-4/D613-6 2025 and 2026 versions, stale D613-6 citation LEGIARTI000043656780 replaced) and dirigeant/auto-entrepreneur/exonérations.publicodes (DROM . taux service BNC 2026 branches + note). Acre . taux service BNC `arrondi: 2 décimales` from 01/2026 left as is (12,80 = 12,8; no numeric effect). Build identical (1427 parsed). Engine: 672 cells compared on 48 checks x 2 trees; 153 differ, ALL at 01/01/2026; 0 differ at 01/12/2025.",
  build_ok: true, build: { G3: build("G3"), proposal: build("proposal") },
  engine_comparison: cmp,
  evaluations, abstentions, approval: "none recorded",
  notes: "Method: work/law/compare_snapshots.mjs (S8 vs stored S7 index) + work/law/record_diff.mjs (field-level deep compare, work/law/M1_S7_S8_record_diff.json). Checks: work/engine/checks_M1_{ae,acre,drom}.json (28 + 8 + 12 checks, dates 01/12/2025 and 01/01/2026), results_M1_{G3,proposal}_*.jsonl, compare_results.mjs. Every engine value in this file is read from those result files; every quote is cut from the S7/S8 articles.json records. The 2026 values G3 carried (26,1 % etc.) match no text in S6/S7/S8 — they were flagged NEEDS_REVIEW in M0 and are now shown wrong. Approval: none recorded (no sign-off, ratification or approval record exists in the corpus; a merge/commit/test is not approval). work/ also holds later-dated snapshots S9/S10 (2026-03/2026-10) from other task lines; NOT used here (world date 2026-01-01).",
  self_reported_tool_calls: Number(process.argv[2] || 0) };
fs.mkdirSync("output", { recursive: true });
fs.writeFileSync("output/answer.json", JSON.stringify(answer, null, 1));
console.error("rules:", rules.length, "classification counts:", JSON.stringify(rules.reduce((m, r) => (m[r.classification] = (m[r.classification] || 0) + 1, m), {})), "| reassessed:", answer.reassessed_rules.length, "| not reassessed:", notRe.length, "| evaluations:", evaluations.length, "| changed cells in evaluations:", evaluations.filter(e => e.changed_by_proposal_at_2026).length);
