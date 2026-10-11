// M2 answer generator (decision date 2026-03-31, law S8 -> S9, rules G4 a61b72947fec). Quotes are cut out of inputs/law/S8|S9 articles.json by
// whitespace-tolerant [start,end] anchors; the ACTUAL raw substring is kept and re-verified with includes() => exact substrings by construction.
// Engine values are read from work/engine/results_M2_{G4,proposal}_{ti,acre26,ae,acre,drom,sal}.jsonl (run_checks.sh), never typed by hand.
// Usage: node work/engine/make_answer_M2.mjs [tool_calls] > /dev/null   (writes output/answer.json)
import fs from "fs";
const d = x => new Date(x).toISOString().slice(0, 10);
const load = p => { const raw = JSON.parse(fs.readFileSync(p, "utf8")); const m = {}; for (const [n, l] of Object.entries(raw.articles)) for (const r of (Array.isArray(l) ? l : [l])) m[n] = r; return { raw, m }; };
const S8 = load("inputs/law/S8_legi-data-2.489.0/articles.json"), S9 = load("inputs/law/S9_legi-data-2.514.0/articles.json");
const V = (S, n) => { const r = S.m[n]; return `${n} ${r.id} (etat ${r.etat}, in force ${d(r.dateDebut)} → ${d(r.dateFin)})`; };
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/ /g, "[\\s\\u00a0]+");
const Q = (S, n, start, end, field = "text") => {
  const t = S.m[n][field] || ""; const re = new RegExp(esc(start) + (end ? "[\\s\\S]*?" + esc(end) : ""), "u"); const m = t.match(re);
  if (!m) throw new Error(`anchor not found in ${n} (${S.raw.legi_data_version}) ${field}: ${start} … ${end}`);
  if (!t.includes(m[0])) throw new Error("quote not substring " + n); return m[0];
};
const cite = (S, n, q, field) => `${V(S, n)}${field ? " [" + field + "]" : ""}: "${q}"`;
const A = "D131-6-1";
const q = {
  duree: Q(S9, A, "La durée de l'exonération des cotisations dues", "est de douze mois"), duree8: Q(S8, A, "La durée de l'exonération des cotisations dues", "est de douze mois"),
  quart: Q(S9, A, "Lorsque le revenu ou la rémunération est inférieur ou égal aux trois quarts", "au 1° ou au 2° du II de l'article L. 131-6-4"),
  total8: Q(S8, A, "Lorsque le revenu ou la rémunération est inférieur ou égal aux trois quarts", "au 1° ou au 2° du II de l'article L. 131-6-4."),
  degr: Q(S9, A, "Lorsque le revenu ou la rémunération est supérieur au trois quarts", "est calculé selon la formule suivante"),
  formule: Q(S9, A, "Montant de l'exonération = 0,25 E/0,25 PSS", "(PSS−R)"), formule8: Q(S8, A, "Montant de l'exonération = E/0,25 PSS", "(PSS-R)"),
  E: Q(S9, A, "E est le montant total des cotisations dues", "égal aux trois quarts de la valeur du plafond mentionné à l'article L. 241-3"),
  l13165: Q(S9, A, "Les dispositions du présent II s'appliquent sans préjudice des dispositions de l'article L. 131-6-5"),
  demande: Q(S9, A, "La demande d'exonérations de cotisations sociales mentionnée au II de l'article L. 131-6-4 est introduite au plus tard le soixantième jour", "délivré par l'organisme unique mentionné à l'article L. 123-33 du code de commerce"),
  marins8: Q(S8, A, "Pour les ressortissants du régime d'assurance des marins", "dans la limite du salaire de la 3e catégorie"),
  pss: Q(S9, A, "La valeur du plafond de la sécurité sociale mentionné à la présente section", "réduite au prorata de la durée d'affiliation"),
  nota: Q(S9, A, "entrent en vigueur le 1 er janvier 2026 et s'appliquent aux créations et reprises d'entreprise intervenant à compter de cette date", null, "nota"),
  nota8: Q(S8, A, "applicables aux cotisations et aux contributions de sécurité sociale dues au titre des périodes courant à compter du 1er janvier 2018", null, "nota"),
  l6137: Q(S9, "L613-7", "Un taux global différent peut être fixé par décret", "exonération de cotisations et de contributions de sécurité sociale"),
  l6137b: Q(S9, "L613-7", "un taux global fixé par décret pour chaque catégorie d'activité"),
  e26: Q(S9, "D613-4", "e) Travailleurs indépendants relevant à la fois", "25,6 %"), b26: Q(S9, "D613-4", "b) Travailleurs indépendants affiliés", "23,2 %"),
  nota4: Q(S9, "D613-4", "s'appliquent au titre des périodes courant à compter du 1 er janvier 2026", null, "nota"),
  drom1: Q(S9, "D756-5", "après arrondi au dixième de pour cent supérieur", "1/3 dans les autres cas"), drom2: Q(S9, "D756-5", "b) 1/2 pour la période", "c) 2/3 à compter de la quatrième année civile d'activité"),
};
const lien = S9.m[A].lienModifications.find(l => l.textCid === "JORFTEXT000053449085");
const LIEN = `${lien.textTitle} (${lien.linkType}, JORF ${lien.datePubliTexte}, signé ${lien.dateSignaTexte}, dateDebutCible ${lien.dateDebutCible})`;
const RD = JSON.parse(fs.readFileSync("work/law/M2_S8_S9_record_diff.json", "utf8")).articles;
const same = n => RD[n].record_identical && RD[n].text_sha256_S8 === RD[n].text_sha256_S9;
// ---- engine results
const rd = f => fs.existsSync(f) ? fs.readFileSync(f, "utf8").trim().split("\n").filter(Boolean).map(JSON.parse) : [];
const RES = {}; const SPECS = ["ti", "acre26", "ae", "acre", "drom", "sal"];
for (const t of ["G4", "proposal"]) { RES[t] = {}; for (const s of SPECS) for (const r of rd(`work/engine/results_M2_${t}_${s}.jsonl`)) RES[t][r.id] = RES[t][r.id] ? { ...RES[t][r.id], results: { ...RES[t][r.id].results, ...r.results } } : r; }
const M1P = {}; for (const s of ["ae", "acre", "drom"]) for (const r of rd(`work/engine/results_M1_proposal_${s}.jsonl`)) M1P[r.id] = r;
const cell = (t, id, rule) => { const r = RES[t][id]; if (!r) throw new Error("no check " + id); const c = r.results[rule]; if (!c) throw new Error(`rule ${rule} not in ${id}`); return c; };
const fmt = c => c.error ? `ERROR (rule absent in this tree): ${c.error.replace(/\s+/g, " ").slice(0, 70)}…` : c.value === null ? "non applicable" : (typeof c.value === "number" ? `${+c.value.toFixed(4)}${c.unit ? " " + c.unit : ""}` : String(c.value));
const num = c => c && !c.error && typeof c.value === "number" ? c.value : null;
const eq = (a, b) => { const x = num(a), y = num(b); if (x !== null && y !== null) return Math.abs(x - y) < 0.01; return fmt(a) === fmt(b); };
const sit = id => Object.fromEntries(Object.entries((RES.G4[id] || RES.proposal[id]).situation).filter(([k]) => k !== "date"));
const EV = (id, rule, law, extra = {}) => { const g = cell("G4", id, rule), p = cell("proposal", id, rule); return { rule, situation_id: id, date: RES.G4[id].situation.date, situation: sit(id), values: { "G4 (pin)": fmt(g), "proposal M2": fmt(p) }, changed_by_proposal: !eq(g, p), law_basis: law, ...extra }; };
const EX = "dirigeant . indépendant . cotisations et contributions . exonérations . ACRE", CC = "dirigeant . indépendant . cotisations et contributions";
const COT = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations";
const NEWLAW = [cite(S9, A, q.quart), cite(S9, A, q.formule), cite(S9, A, q.nota, "nota"), LIEN];
const OLDLAW = [cite(S8, A, q.total8), cite(S8, A, q.formule8), cite(S8, A, q.nota8, "nota")];
const evaluations = [];
// (a) travailleur indépendant hors micro-social
const TI_IDS = Object.keys(RES.G4).filter(i => i.startsWith("TI_"));
for (const id of TI_IDS) {
  const crea26 = /crea2026/.test(id), acre = !/noACRE/.test(id);
  const basis = !acre ? ["Acre not requested: exonérations . ACRE non applicable; cotisations de droit commun (baseline)"] : crea26 ? NEWLAW : [...OLDLAW, "création antérieure au 01/01/2026 -> version LEGIARTI000036475110 still governs (" + cite(S9, A, q.nota, "nota") + ")"];
  evaluations.push(EV(id, `${EX} . taux`, basis, { note: crea26 && acre ? "25 % up to 3/4 PSS (quart), then 0,25 E/0,25 PSS x (PSS-R) read as linear 25 % -> 0 % between 3/4 PSS and PSS" : acre ? "100 % up to 3/4 PSS, linear to 0 % at PSS (text of the 2018 version)" : undefined }));
  evaluations.push(EV(id, `${EX} . prorata sur l'année`, [cite(S9, A, q.duree), "I unchanged (douze mois)"]));
  evaluations.push(EV(id, "dirigeant . exonérations . ACRE", [cite(S9, A, q.duree)]));
  for (const c of ["maladie", "indemnités journalières maladie", "invalidité et décès", "retraite de base", "allocations familiales"]) evaluations.push(EV(id, `${EX} . ${c}`, [...basis, "exonerated cotisation (D131-6-1 II: « maladie, maternité, veuvage, vieillesse de base, invalidité et décès et d'allocations familiales ») = cotisation x (1 - taux x prorata)"]));
  for (const c of ["maladie", "retraite de base", "invalidité et décès", "CSG-CRDS", "cotisations"]) evaluations.push(EV(id, `${CC} . ${c}`, [...basis, c === "CSG-CRDS" ? "CSG-CRDS not exonerated; changes only through its base (revenu + cotisations) — base rule L136-3/D136-5 unchanged S8/S9" : "value after the `remplace` of exonérations . ACRE"]));
  evaluations.push(EV(id, CC, basis));
  evaluations.push(EV(id, "dirigeant . indépendant . PSS proratisé", [cite(S9, A, q.pss)]));
  evaluations.push(EV(id, "dirigeant . indépendant . assiette des cotisations", ["L131-6 record byte-identical S8/S9"]));
}
// (b) auto-entrepreneur créé en 2026 (notification, rates unchanged)
const AE26 = Object.keys(RES.G4).filter(i => i.includes("_crea2026@"));
for (const id of AE26) {
  const law = [cite(S9, "L613-7", q.l6137), cite(S9, A, q.quart), cite(S9, A, q.nota, "nota"), "the decree fixing the micro-social Acre rate under L613-7 I is NOT in the bounded set -> abstain on any numeric change; notification only"];
  evaluations.push(EV(id, "dirigeant . auto-entrepreneur . Acre . taux Acre 2026 à confirmer", law, { note: "new notification rule (absent in G4 -> engine error there); true for entreprise . date de création >= 01/01/2026" }));
  evaluations.push(EV(id, "dirigeant . auto-entrepreneur . Acre . taux Acre", law));
  for (const r of ["taux service BNC", "taux CIPAV", "taux service BIC", "taux vente restauration hébergement"]) evaluations.push(EV(id, `dirigeant . auto-entrepreneur . Acre . ${r}`, law));
  for (const c of ["service BNC", "service BNC Cipav", "service BIC", "vente restauration hébergement"]) evaluations.push(EV(id, `${COT} . ${c} . taux`, ["rate after the Acre `remplace`", cite(S9, "D613-4", q.e26)]));
  evaluations.push(EV(id, COT, [cite(S9, "D613-4", q.e26)]));
}
// (c) dirigeant assimilé salarié (outside the bounded set; same article)
const SAL = Object.keys(RES.G4).filter(i => i.startsWith("AS_"));
for (const id of SAL) for (const r of ["salarié . cotisations . exonérations . Acre . quotité", "salarié . cotisations . exonérations . Acre", "salarié . cotisations . exonérations . Acre . employeur", "salarié . cotisations . exonérations . Acre . salarié", "salarié . cotisations . exonérations . Acre . coefficient dégressif", "salarié . cotisations . assiette", "salarié . cotisations"])
  if (RES.G4[id].results[r] && RES.proposal[id] && RES.proposal[id].results[r]) evaluations.push(EV(id, r, /crea2026/.test(id) && !/noACRE/.test(id) ? NEWLAW : OLDLAW, { scope: "outside bounded file set (salarié/exonérations/acre.publicodes cites D131-6-1)" }));
// (d) regression of the AE rules (M1 specs: 48 checks) on G4 vs the law-aligned M1 proposal, and G4 vs M2 proposal
const AE_IDS = Object.keys(M1P).filter(i => RES.G4[i]);
const diffM1 = [], diffM2 = []; let ncells = 0;
for (const id of AE_IDS) for (const [rule, c] of Object.entries(RES.G4[id].results)) {
  ncells++; const m = M1P[id].results[rule], p = RES.proposal[id].results[rule];
  if (m && !eq(m, c)) diffM1.push({ check: id, rule, "M1 proposal (law-aligned, G3 base)": fmt(m), "G4": fmt(c) });
  if (p && !eq(c, p)) diffM2.push({ check: id, rule, "G4": fmt(c), "proposal M2": fmt(p) });
}
const rulesDiffM1 = [...new Set(diffM1.map(x => x.rule))], rulesDiffM2 = [...new Set(diffM2.map(x => x.rule))];
const aeRulesChecked = [...new Set(AE_IDS.flatMap(id => Object.keys(RES.G4[id].results)))];
const aeSameAsM1 = aeRulesChecked.filter(r => !rulesDiffM1.includes(r));
// ---- rules classification
const rules = []; const notRe = [];
const push = (classification, confidence, rule, article, evidence, extra = {}) => rules.push({ rule, classification, confidence, article, evidence, reassessed: true, ...extra });
const VA9 = V(S9, A), VA8 = V(S8, A);
const tiVals = (rule) => TI_IDS.map(id => `${id}: G4 ${fmt(cell("G4", id, rule))} | proposal ${fmt(cell("proposal", id, rule))}`);
push("AFFECTED", "high", `${EX} . taux`, VA9, [cite(S9, A, q.quart), cite(S8, A, q.total8), cite(S9, A, q.formule), cite(S8, A, q.formule8), cite(S9, A, q.nota, "nota"), LIEN, ...tiVals(`${EX} . taux`)],
  { action: "edit: `variations` on `entreprise . date de création >= 01/01/2026` -> taux progressif 25 % (<= 75 % PSS) to 0 % (PSS); otherwise the former 100 % -> 0 %", caveat: "E is defined at 3/4 PSS in both versions; the model applies the degressive rate to the cotisations of the actual revenue (pre-existing approximation, not changed)" });
push("AFFECTED", "high", EX, VA9, [cite(S9, A, q.quart), "parent of the five `remplace` rules; value (oui) unchanged, note + références added", ...tiVals(EX)], { action: "documentation edit (note, références 2018/2026 versions); its children change value" });
for (const c of ["maladie", "indemnités journalières maladie", "invalidité et décès", "retraite de base", "allocations familiales"])
  push("AFFECTED", "high", `${EX} . ${c}`, VA9, [cite(S9, A, q.quart), `abattement = taux x prorata: changes for créations/reprises >= 01/01/2026`, ...tiVals(`${EX} . ${c}`)], { action: "no edit (value changes through `taux`)" });
for (const c of ["cotisations", "CSG-CRDS"]) push("AFFECTED", c === "CSG-CRDS" ? "medium" : "high", `${CC} . ${c}`, VA9, [cite(S9, A, q.quart), c === "CSG-CRDS" ? "CSG-CRDS itself is not in the exonerated list; its base (revenu + cotisations) grows when the exoneration shrinks — L136-3 / D136-5 records byte-identical S8/S9" : "sum of the replaced cotisations", ...tiVals(`${CC} . ${c}`)], { action: "no edit (dependency)" });
push("AFFECTED", "high", CC, VA9, [cite(S9, A, q.quart), ...tiVals(CC)], { action: "no edit (dependency)" });
push("UNAFFECTED", "high", `${EX} . prorata sur l'année`, VA9, [cite(S9, A, q.duree), cite(S8, A, q.duree8), "I (douze mois) identical in both versions", ...tiVals(`${EX} . prorata sur l'année`)]);
push("UNAFFECTED", "high", "dirigeant . exonérations . ACRE", VA9, [cite(S9, A, q.duree), "applicability (durée d'activité en début d'année < 1 an) unchanged; new IV adds a 60-day filing deadline, procedural: " + cite(S9, A, q.demande), ...tiVals("dirigeant . exonérations . ACRE")], { action: "documentation edit only (historique 2026, référence)" });
push("UNAFFECTED", "high", "dirigeant . indépendant . PSS proratisé", VA9, [cite(S9, A, q.pss), "III first two sentences identical; only the marins paragraph was removed: " + cite(S8, A, q.marins8), ...tiVals("dirigeant . indépendant . PSS proratisé")]);
// auto-entrepreneur Acre
const aeVals = (rule, ids = AE26) => ids.map(id => `${id}: G4 ${fmt(cell("G4", id, rule))} | proposal ${fmt(cell("proposal", id, rule))}`);
push("NEEDS_REVIEW", "medium", "dirigeant . auto-entrepreneur . Acre . taux Acre", `${V(S9, "L613-7")} + ${VA9}`, [cite(S9, "L613-7", q.l6137), cite(S9, A, q.quart), cite(S9, A, q.nota, "nota"), "The 50 % factor is fixed by a decree taken under L613-7 I which is NOT in the bounded set; décret n° 2026-69 (art. 1 seen here) halves the TI exoneration to a quarter for créations >= 2026 — whether another article of the same decree changed the micro-social rate cannot be seen. Abstain; notification added.", ...aeVals("dirigeant . auto-entrepreneur . Acre . taux Acre")], { action: "no numeric edit; note + new notification `taux Acre 2026 à confirmer`" });
for (const r of ["taux service BNC", "taux service BIC", "taux vente restauration hébergement"]) push("NEEDS_REVIEW", "medium", `dirigeant . auto-entrepreneur . Acre . ${r}`, `${V(S9, "L613-7")} + ${V(S9, "D613-4")}`, ["= taux Acre x full rate (D613-4 rows e/d/a, unchanged S8/S9); inherits the uncertainty of taux Acre", ...aeVals(`dirigeant . auto-entrepreneur . Acre . ${r}`)], { action: "none" });
push("NEEDS_REVIEW", "low", "dirigeant . auto-entrepreneur . Acre . taux CIPAV", `${V(S9, "L613-7")} + ${V(S9, "D613-4")}`, [cite(S9, "D613-4", q.b26), "G4 (commit ea8f00f0, 2026-01-27) hard-codes 13,40 % from 01/2026 (13,90 % 07/2024-2025): matches no text in the set (neither 50 % x 23,2 % = 11,6 % nor any D613-6 split). Abstain.", ...aeVals("dirigeant . auto-entrepreneur . Acre . taux CIPAV"), ...aeVals("dirigeant . auto-entrepreneur . Acre . taux CIPAV", ["CIPAV_ACRE@01-12-2025", "CIPAV_ACRE@01-01-2026"])], { action: "none" });
push("UNAFFECTED", "high", "dirigeant . auto-entrepreneur . Acre", VA9, [cite(S9, A, q.duree), ...aeVals("dirigeant . auto-entrepreneur . Acre")]);
// auto-entrepreneur rates/shares/DROM: articles identical S8/S9, re-run on G4 and compared with the law-aligned M1 proposal
const dromVals = (rule) => ["DROM_Q8_BNC@01-01-2026", "DROM_Q12_BNC@01-01-2026", "DROM_Y4_BNC@01-01-2026"].map(id => `${id}: G4 ${fmt(cell("G4", id, rule))} | proposal ${fmt(cell("proposal", id, rule))} | M1 proposal ${fmt(M1P[id].results[rule])}`);
push("NEEDS_REVIEW", "high", "dirigeant . auto-entrepreneur . DROM . taux service BNC", `${V(S9, "D756-5")} + ${V(S9, "D613-4")}`, [cite(S9, "D756-5", q.drom1), cite(S9, "D756-5", q.drom2), cite(S9, "D613-4", q.e26), "NOT caused by S8->S9 (both articles byte-identical). Pre-existing since M1: G4 still carries 4,4 / 13,1 / 17,4 % for 2026 (= fractions of the never-enacted 26,1 %); ceil10 of 1/6, 1/2, 2/3 x 25,6 % = 4,3 / 12,8 / 17,1 %.", ...dromVals("dirigeant . auto-entrepreneur . DROM . taux service BNC")], { action: "edit carried over from M1: 2026 branches 4.3 / 12.8 / 17.1 %" });
push("UNAFFECTED", "high", "dirigeant . auto-entrepreneur . DROM . taux CIPAV", `${V(S9, "D756-5")} + ${V(S9, "D613-4")}`, [cite(S9, "D613-4", q.b26), cite(S9, "D756-5", q.drom1), "G4 (commit 55470937) now gives 7,8 / 11,6 / 15,5 % from 07/2024 = ceil10 of 1/3, 1/2, 2/3 x 23,2 %: the pre-existing mismatch noted in R3/M0/M1 is resolved upstream; articles unchanged S8/S9", ...["DROM_Q8_CIPAV@01-01-2026", "DROM_Q8_BNC@01-12-2025"].map(id => `${id}: G4 ${fmt(cell("G4", id, "dirigeant . auto-entrepreneur . DROM . taux CIPAV"))} (M1 proposal/G3: ${fmt(M1P[id].results["dirigeant . auto-entrepreneur . DROM . taux CIPAV"])})`)]);
for (const r of ["dirigeant . auto-entrepreneur . DROM . taux service BIC", "dirigeant . auto-entrepreneur . DROM . taux vente restauration hébergement", "dirigeant . auto-entrepreneur . DROM"]) push("UNAFFECTED", "high", r, `${V(S9, "D756-5")} + ${V(S9, "D613-4")}`, ["D756-5 and D613-4 records byte-identical S8/S9; G4 value identical to the law-aligned M1 proposal on every check", ...["DROM_Q8_SBIC@01-01-2026", "DROM_Q8_VENTE@01-01-2026"].map(id => `${id}: G4 ${fmt(cell("G4", id, r))}`)]);
const SH = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"];
const cats = { BNC: "service BNC", CIPAV: "service BNC Cipav", SBIC: "service BIC", VENTE: "vente restauration hébergement" };
for (const [k, c] of Object.entries(cats)) {
  const ev = (rule) => [`D613-4 / D613-6 records byte-identical S8/S9 (text sha256 ${RD["D613-4"].text_sha256_S9.slice(0, 12)}… / ${RD["D613-6"].text_sha256_S9.slice(0, 12)}…)`, `G4 re-run: ${["01-12-2025", "01-01-2026"].map(dt => `${k}@${dt} = ${fmt(cell("G4", `${k}@${dt}`, rule))}`).join("; ")}`, aeSameAsM1.includes(rule) ? "equal to the law-aligned M1 proposal on all 48 checks (M1 verified these against D613-4 LEGIARTI000052218738 / D613-6 LEGIARTI000052218747)" : "differs from the M1 proposal only in the cells listed under engine_regression (DROM BNC 2026 replacement / rounding)"];
  push("UNAFFECTED", "high", `${COT} . ${c} . taux`, V(S9, "D613-4"), ev(`${COT} . ${c} . taux`));
  push("UNAFFECTED", "high", `${COT} . ${c}`, V(S9, "D613-4"), ev(`${COT} . ${c}`));
  for (const s of SH) push("UNAFFECTED", "high", `${COT} . ${c} . répartition . ${s} . taux de répartition`, V(S9, "D613-6"), ev(`${COT} . ${c} . répartition . ${s} . taux de répartition`));
}
for (const s of SH) push("UNAFFECTED", "high", `${COT} . répartition . ${s}`, V(S9, "D613-6"), [`records byte-identical S8/S9`, `G4 BNC@01-01-2026 = ${fmt(cell("G4", "BNC@01-01-2026", `${COT} . répartition . ${s}`))}`, aeSameAsM1.includes(`${COT} . répartition . ${s}`) ? "equal to the M1 proposal on all checks" : "see engine_regression"]);
for (const r of [COT, "dirigeant . auto-entrepreneur . cotisations et contributions", "protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur", "protection sociale . retraite . base . cotisée . revenu auto-entrepreneur", "dirigeant . auto-entrepreneur . Cipav"])
  push("UNAFFECTED", "high", r, `${V(S9, "D613-4")} + ${V(S9, "D613-6")}`, ["records byte-identical S8/S9", `G4 BNC@01-01-2026 = ${fmt(cell("G4", "BNC@01-01-2026", r))}; BNC@01-12-2025 = ${fmt(cell("G4", "BNC@01-12-2025", r))}`, aeSameAsM1.includes(r) ? "equal to the M1 proposal on all checks" : "differs from the M1 proposal only in DROM BNC 2026 cells / `arrondi: oui` rounding (see engine_regression)"]);
// outside the bounded set, same article
const salVals = (rule) => SAL.filter(id => RES.G4[id].results[rule] && RES.proposal[id] && RES.proposal[id].results[rule]).map(id => `${id}: G4 ${fmt(cell("G4", id, rule))} | proposal ${fmt(cell("proposal", id, rule))}`);
for (const r of ["salarié . cotisations . exonérations . Acre", "salarié . cotisations . exonérations . Acre . employeur", "salarié . cotisations . exonérations . Acre . salarié"])
  push("AFFECTED", "high", r, VA9, [cite(S9, A, q.quart), cite(S9, A, q.formule), "rule cites D131-6-1 (salarié/exonérations/acre.publicodes); « revenu ou la rémunération » / « régime de salariés » -> dirigeants assimilés salariés", ...salVals(r)], { scope: "OUTSIDE the bounded file set (auto-entrepreneur / indépendant / exonérations files) — flagged and edited in the proposal for completeness", action: "edit: new `Acre . quotité` (25 % for créations/reprises >= 01/01/2026, 100 % otherwise) multiplying both grille tranches" });
// not re-examined: bound to records byte-identical in S8 and S9 and not referencing D131-6-1
const NRE = (rule, art, where, quote) => { if (!same(art)) throw new Error(art + " not identical"); const a = RD[art]; rules.push({ rule, classification: "UNAFFECTED", confidence: "high", article: V(S9, art), evidence: [cite(S9, art, quote), `${art} record byte-identical S8/S9 (text sha256 ${a.text_sha256_S9.slice(0, 16)}…, same id/etat/dates/liens/nota)`, "no reference to D131-6-1 / L131-6-4 in the rule (grep of the G4 tree); its own formula was therefore not re-examined", where], reassessed: false }); notRe.push({ rule, reason: `${art} record byte-identical S8/S9 (work/law/M2_S8_S9_record_diff.json) and the rule does not depend on D131-6-1; ${where}` }); };
NRE(`${CC} . maladie`, "D621-2", "its value in an Acre situation changes only through the `remplace` of exonérations . ACRE . maladie (shown in evaluations)", Q(S9, "D621-2", "le taux de base de la cotisation d'assurance maladie et materni"));
NRE(`${CC} . indemnités journalières maladie`, "D621-2", "replaced by exonérations . ACRE . indemnités journalières maladie in Acre situations", Q(S9, "D621-2", "le taux de base de la cotisation d'assurance maladie et materni"));
NRE(`${CC} . invalidité et décès`, "D632-1", "replaced by exonérations . ACRE . invalidité et décès in Acre situations", Q(S9, "D632-1", "La cotisation annuelle au régime d'assurance invalidité-décès prévue à l'article L. 632-1"));
NRE("dirigeant . indépendant . assiette minimale . invalidité et décès", "D632-1", "assiette minimale", Q(S9, "D632-1", "La cotisation annuelle au régime d'assurance invalidité-décès prévue à l'article L. 632-1"));
NRE(`${CC} . retraite de base`, "D633-3", "replaced by exonérations . ACRE . retraite de base in Acre situations; G4 still carries the 17,15 % + 0,60/0,72 % form (the R4 rewrite d3e0cfe0 is later than this pin)", Q(S9, "D633-3", "Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %"));
NRE(`${CC} . allocations familiales`, "L131-6", "not in the bounded article set beyond the L131-6 base; replaced by exonérations . ACRE . allocations familiales", Q(S9, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7"));
NRE(`${CC} . CSG-CRDS . assiette`, "L136-3", "L136-3 III abattement / D136-5 floor-cap (T1b/R5 lines)", Q(S9, "L136-3", "fait l'objet d'un abattement de 26 %"));
NRE("dirigeant . indépendant . assiette des cotisations", "L131-6", "L131-6 revenu d'activité", Q(S9, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7"));
NRE("bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire", "L131-6", "références: bénéficiaire.publicodes line 131", Q(S9, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7"));
NRE(`${CC} . exonérations . ZFU`, "L131-6", "ZFU exoneration (own legal basis outside the set); unrelated to D131-6-1", Q(S9, "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles"));
rules.push({ rule: "(none) — D613-5 conjoint collaborateur / D613-4 row c) meublés de tourisme / D756-5 II", classification: "UNAFFECTED", confidence: "high", article: `${V(S9, "D613-5")}; ${V(S9, "D613-4")}; ${V(S9, "D756-5")}`, evidence: ["records byte-identical S8/S9; no implementing rule at G4 (pre-existing gaps, see M1)"], reassessed: false });
notRe.push({ rule: "(none) — D613-5 / D613-4 row c / D756-5 II (no implementing rule at G4)", reason: "Records byte-identical S8/S9 (work/law/M2_S8_S9_record_diff.json); nothing in the tree to re-examine." });
notRe.push({ rule: "dirigeant . auto-entrepreneur . impôt . versement libératoire . * (G4 commit bdfbd61c)", reason: "Impôt sur le revenu (CGI art. 151-0), no bounded CSS article; outside the law set." });
notRe.push({ rule: "dirigeant . indépendant . cotisations et contributions . retraite complémentaire / exonérations . âge / pension invalidité / DROM (TI)", reason: "Legal bases (D635-*, D621-4, LODEOM texts) outside the bounded set; records of the 12 bounded articles other than D131-6-1 byte-identical S8/S9; no dependency on D131-6-1 (the `non applicable si: prorata < ACRE . prorata sur l'année` guards use the unchanged prorata rule)." });
// ---- abstentions
const abstentions = [
  { topic: "Micro-social (auto-entrepreneur) Acre rate from 2026 (taux Acre 50 %; Acre . taux service BNC 12,8 %, BIC 10,6 %, vente 6,2 %)", value_shown: "unchanged G4 values + notification `taux Acre 2026 à confirmer`", reason: `${cite(S9, "L613-7", q.l6137)}. That decree is not in the bounded set (D131-6-1 II speaks of « revenu ou la rémunération » and of the cotisations of L131-6-4 II 1°/2°, not of the taux global of L613-7); décret n° 2026-69 may have other articles than the art. 1 that modified D131-6-1. No supported number -> abstain.` },
  { topic: "Acre . taux CIPAV 13,40 % from 01/2026 (G4 commit ea8f00f0)", value_shown: "left as in G4", reason: "No text in the set gives 13,40 % (or the former 13,90 %); row b of D613-4 is 23,2 % in S8 and S9." },
  { topic: "Article L131-6-5 (« sans préjudice des dispositions de l'article L. 131-6-5 »)", value_shown: "none", reason: `${cite(S9, A, q.l13165)} — L131-6-5 is outside the bounded set; whatever interaction it creates cannot be modelled from this corpus.` },
  { topic: "E at 3/4 PSS in the degressive formula", value_shown: "model keeps its pre-existing approximation (degressive rate applied to the cotisations of the actual revenue)", reason: `${cite(S9, A, q.E)} — identical definition in both versions; changing it is not required by S9 and is left to a dedicated change.` },
  { topic: "Application in time", value_shown: "`entreprise . date de création >= 01/01/2026` (not the simulation date)", reason: `${cite(S9, A, q.nota, "nota")} — the criterion is the création/reprise date; the lien gives dateDebutCible ${lien.dateDebutCible} (décret published ${lien.datePubliTexte}) while the nota makes the text apply from 2026-01-01. 'Reprise' is not distinguished from 'création' in the tree (date de création used for both).` },
  { topic: "DROM 2026 rates for category e (4,3 / 12,8 / 17,1 %)", value_shown: "derived from D756-5 fractions and rounding, carried over from M1", reason: `${cite(S9, "D756-5", q.drom1)}; D756-5 cites the old numbering (D. 131-6-1 / L. 133-6-8); not published as such in the corpus.` },
  { topic: "Dirigeants assimilés salariés (salarié . cotisations . exonérations . Acre)", value_shown: "edited in the proposal (quotité 25 %) but OUTSIDE the bounded file set", reason: "Same article D131-6-1 II; included for completeness, flagged separately." },
];
const build = t => JSON.parse(fs.readFileSync(`work/engine/build_M2_${t}.json`, "utf8"));
const nTI = TI_IDS.length, nAE = AE_IDS.length, nAE26 = AE26.length, nSAL = SAL.length;
const totalCells = Object.values(RES.G4).reduce((n, r) => n + Object.keys(r.results).length, 0);
const diffAll = []; for (const [id, r] of Object.entries(RES.G4)) for (const [rule, c] of Object.entries(r.results)) { const p = RES.proposal[id] && RES.proposal[id].results[rule]; if (p && !eq(c, p)) diffAll.push(`${id} :: ${rule} : ${fmt(c)} -> ${fmt(p)}`); }
const answer = {
  task: "M2", decision_date: "2026-03-31",
  law_snapshots: { S8: `legi-data ${S8.raw.legi_data_version} published ${S8.raw.published}`, S9: `legi-data ${S9.raw.legi_data_version} published ${S9.raw.published}` },
  rules_pin: "G4 a61b72947fec (committed 2026-03-03 09:30:36 +0100, modele-social 10.0.1 in tree, old single-package layout); build 652 raw / 1334 parsed rules",
  changed_articles: [{ article: A, old: VA8, new: VA9, modifying_text: LIEN, nota: q.nota,
    text_changes: [`II first sentence: exoneration below 3/4 PSS now « au quart du montant total des cotisations » (S8: « au montant total des cotisations »): S9 "${q.quart}" / S8 "${q.total8}"`,
      `II degressive formula: S9 "${q.formule}" (S8: "${q.formule8}")`, `II new sentence: "${q.l13165}" (L131-6-5 outside the set)`, `III: marins paragraph removed (S8: "${q.marins8}")`, `IV new sentence: "${q.demande}"`,
      `unchanged: I (douze mois): "${q.duree}"; definition of E: "${q.E}"; III PSS: "${q.pss}"`],
    versions: RD[A].versions_S9 }],
  unchanged_articles: ["L131-6", "L136-3", "L613-7", "D136-5", "D613-4", "D613-5", "D613-6", "D621-2", "D632-1", "D633-3", "D756-5"].map(n => `${V(S9, n)} — record byte-identical S8/S9 (text sha256 ${RD[n].text_sha256_S9.slice(0, 16)}…)`),
  missing_articles: S9.raw.articles_missing_in_snapshot,
  summary: `Relevant change: YES, one article. Between S8 (2026-01-01) and S9 (2026-03-31) D131-6-1 was re-issued as ${VA9} by ${LIEN}; nota: « ${q.nota} ». For créations/reprises from 2026-01-01 the Acre exoneration of travailleurs indépendants (hors micro-social) drops from the whole to a quarter of the maladie-maternité / veuvage / vieillesse de base / invalidité-décès / allocations familiales cotisations below 3/4 PSS, and the degressive band becomes 0,25 E/0,25 PSS x (PSS-R). G4 still exonerates 100 %: rule \`${EX} . taux\` is AFFECTED and edited (25 % branch on date de création >= 01/01/2026). The micro-social Acre rate (taux Acre 50 %) rests on a decree outside the set -> NEEDS_REVIEW, abstention, notification added. The 11 other articles are byte-identical: the auto-entrepreneur rates/shares were re-run on the new pin G4 (which adopted the M1 values: BNC 25,6 %, 2026 shares, DROM Cipav 7,8/11,6/15,5) and found UNAFFECTED, except the pre-existing DROM BNC 2026 derivation (4,4/13,1/17,4 vs 4,3/12,8/17,1) carried over as NEEDS_REVIEW + edit. Dirigeants assimilés salariés (salarié Acre rules, outside the bounded set) are affected by the same text and flagged/edited for completeness.`,
  rules, reassessed_rules: rules.filter(r => r.reassessed !== false).map(r => r.rule), not_reassessed_rules: notRe,
  no_change_needed: false,
  no_change_needed_explanation: `A numeric change is required for travailleurs indépendants created/reprises from 01/01/2026 (exonérations . ACRE . taux 100 % -> 25 % below 3/4 PSS, degressive x 0,25). Engine on the proposal (${nTI} TI checks): e.g. ${TI_IDS.slice(0, 2).map(id => `${id}: taux ${fmt(cell("G4", id, `${EX} . taux`))} -> ${fmt(cell("proposal", id, `${EX} . taux`))}, cotisations ${fmt(cell("G4", id, `${CC} . cotisations`))} -> ${fmt(cell("proposal", id, `${CC} . cotisations`))}`).join("; ")}. Créations before 2026 unchanged on every cell.`,
  proposal_dir: "work/proposals/M2/modele-social/règles",
  proposal_summary: "Applied by `node work/proposals/M2/apply_M2.mjs <règles>` on a fresh copy of G4 (diff: work/proposals/M2/M2.diff). dirigeant/exonérations.publicodes: `exonérations . ACRE . taux` variations (25 % branch for date de création >= 01/01/2026), note + références on `exonérations . ACRE`; dirigeant/exonérations/ACRE.publicodes: historique 2026 + référence; dirigeant/auto-entrepreneur/exonérations.publicodes: note on `taux Acre`, new notification `Acre . taux Acre 2026 à confirmer`, DROM BNC 2026 4.3/12.8/17.1 % (M1 carry-over) + note; salarié/exonérations/acre.publicodes (outside bounded set): new `Acre . quotité` + référence.",
  build_ok: true, build: { G4: build("G4"), proposal: build("proposal") },
  engine_comparison: `Checks: ${nTI} TI (checks_M2_ti.json), ${nAE26} AE créés 2026 (checks_M2_acre26.json), ${nAE} AE M1 specs (checks_M1_{ae,acre,drom}.json), ${nSAL} assimilé salarié (checks_M2_sal.json); ${totalCells} cells on G4 vs proposal: ${diffAll.length} differ (all in Acre situations with création >= 2026, in DROM BNC 2026 cells, or the new notification rule). Against the law-aligned M1 proposal (G3 base), G4 differs on ${diffM1.length}/${ncells} AE cells (rules: ${rulesDiffM1.join("; ")}).`,
  engine_regression: { G4_vs_M1_proposal: diffM1, G4_vs_M2_proposal_AE_specs: diffM2, all_cell_changes_G4_to_proposal: diffAll },
  evaluations, abstentions, approval: "none recorded",
  notes: "Method: work/law/compare_snapshots.mjs (S9 vs stored S8 index/texts) + work/law/record_diff.mjs (work/law/M2_S8_S9_record_diff.json). Checks: work/engine/make_checks_M2.mjs -> checks_M2_ti.json / checks_M2_acre26.json; checks_M2_sal.json hand-written; M1 specs reused. Runs: work/engine/run_checks.sh -> results_M2_{G4,proposal}_*.jsonl + log_M2_*.txt. Diffs: work/engine/compare_results.mjs. This file: work/engine/make_answer_M2.mjs (quotes exact by construction, values read from the result files).",
  self_reported_tool_calls: Number(process.argv[2] || 0) };
fs.mkdirSync("output", { recursive: true });
fs.writeFileSync("output/answer.json", JSON.stringify(answer, null, 1));
console.error("rules:", rules.length, JSON.stringify(rules.reduce((m, r) => (m[r.classification] = (m[r.classification] || 0) + 1, m), {})), "| reassessed:", answer.reassessed_rules.length, "| not reassessed:", notRe.length, "| evaluations:", evaluations.length, "| cells:", totalCells, "diffAll:", diffAll.length, "| diffM1:", diffM1.length, "/", ncells, "| size:", fs.statSync("output/answer.json").size);
