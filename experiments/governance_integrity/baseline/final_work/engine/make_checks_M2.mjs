// M2 check specs. (a) checks_M2_ti.json: travailleur indépendant (hors micro-social) with/without Acre, créations 2025 vs 2026, revenue levels
// around 3/4 PSS and PSS (PSS 2026 = 4 005 €/mois = 48 060 €/an in base.publicodes). (b) checks_M2_acre26.json: the four AE Acre categories
// for an entreprise créée le 01/01/2026 (notification + rates), derived from checks_M1_acre.json. The M1 specs (ae/acre/drom) are reused as-is.
// Usage: node work/engine/make_checks_M2.mjs
import fs from "fs";
const EX = "dirigeant . indépendant . cotisations et contributions . exonérations . ACRE";
const CC = "dirigeant . indépendant . cotisations et contributions";
const TI_RULES = ["plafond sécurité sociale", "dirigeant . indépendant . PSS proratisé", "dirigeant . indépendant . revenu professionnel", "dirigeant . indépendant . assiette des cotisations",
  "entreprise . durée d'activité . en début d'année", "dirigeant . exonérations . ACRE", EX, `${EX} . taux`, `${EX} . prorata sur l'année`,
  ...["maladie", "indemnités journalières maladie", "invalidité et décès", "retraite de base", "allocations familiales"].map(c => `${EX} . ${c}`),
  ...["maladie", "indemnités journalières maladie", "invalidité et décès", "retraite de base", "allocations familiales", "retraite complémentaire", "CSG-CRDS", "cotisations"].map(c => `${CC} . ${c}`), CC];
const base = (date, creation, debutAnnee, revenu, acre) => ({
  date, "salarié": "non", "dirigeant . régime social": "'indépendant'", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "non",
  "entreprise . imposition": "'IR'", "entreprise . activité . nature": "'commerciale'", "établissement . commune . département . outre-mer": "non",
  "entreprise . date de création": creation, "entreprise . durée d'activité . en début d'année": debutAnnee, "dirigeant . exonérations . ACRE": acre,
  "dirigeant . indépendant . revenu professionnel": `${revenu} €/an` });
const ti = [];
for (const rev of [20000, 42000, 55000, 80000]) ti.push({ id: `TI_ACRE_crea2026_rev${rev}@01-06-2026`, situation: base("01/06/2026", "01/01/2026", "0 an", rev, "oui"), rules: TI_RULES });
ti.push({ id: "TI_ACRE_crea2025-07_rev20000@01-06-2026", situation: base("01/06/2026", "01/07/2025", "6 mois", 20000, "oui"), rules: TI_RULES });
ti.push({ id: "TI_ACRE_crea2025-01_rev20000@01-06-2025", situation: base("01/06/2025", "01/01/2025", "0 an", 20000, "oui"), rules: TI_RULES });
ti.push({ id: "TI_noACRE_crea2026_rev20000@01-06-2026", situation: base("01/06/2026", "01/01/2026", "0 an", 20000, "non"), rules: TI_RULES });
ti.push({ id: "TI_noACRE_crea2026_rev42000@01-06-2026", situation: base("01/06/2026", "01/01/2026", "0 an", 42000, "non"), rules: TI_RULES });
fs.writeFileSync("work/engine/checks_M2_ti.json", JSON.stringify(ti, null, 1));
console.log(`checks_M2_ti.json: ${ti.length} checks, ${ti.reduce((n, c) => n + c.rules.length, 0)} cells`);

const acre = JSON.parse(fs.readFileSync("work/engine/checks_M1_acre.json", "utf8")).filter(c => c.id.endsWith("@01-01-2026"));
const out = acre.map(c => ({ id: c.id.replace(/@.*$/, "_crea2026@01-06-2026"),
  situation: { ...c.situation, date: "01/06/2026", "entreprise . date de création": "01/01/2026", "entreprise . durée d'activité": "5 mois" },
  rules: ["dirigeant . auto-entrepreneur . Acre . taux Acre 2026 à confirmer", ...c.rules] }));
fs.writeFileSync("work/engine/checks_M2_acre26.json", JSON.stringify(out, null, 1));
console.log(`checks_M2_acre26.json: ${out.length} checks, ${out.reduce((n, c) => n + c.rules.length, 0)} cells`);
