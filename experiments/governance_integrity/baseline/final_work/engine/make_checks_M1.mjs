// Builds the M1 check specs from the M0 ones: same situations and rules, dates 01/12/2025 (last month of the 2025 versions)
// and 01/01/2026 (décret 2025-943 versions in force), plus the five aggregate `cotisations . répartition . *` amounts.
// Usage: node work/engine/make_checks_M1.mjs   -> work/engine/checks_M1_{ae,acre,drom}.json
import fs from "fs";
const DATES = ["01/12/2025", "01/01/2026"];
const COT = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations";
const AGG = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"].map(b => `${COT} . répartition . ${b}`);
for (const f of ["ae", "acre", "drom"]) {
  const src = JSON.parse(fs.readFileSync(`work/engine/checks_M0_${f}.json`, "utf8"));
  const seen = new Set(); const out = [];
  for (const c of src) {
    const base = c.id.replace(/@.*$/, ""); if (seen.has(base)) continue; seen.add(base);
    for (const date of DATES) {
      const situation = { ...c.situation, date };
      const rules = f === "ae" && !base.startsWith("DROM") ? [...c.rules, ...AGG.filter(r => !c.rules.includes(r))] : c.rules;
      out.push({ id: `${base}@${date.replace(/\//g, "-")}`, situation, rules });
    }
  }
  fs.writeFileSync(`work/engine/checks_M1_${f}.json`, JSON.stringify(out, null, 1));
  console.log(`checks_M1_${f}.json: ${out.length} checks, ${out.reduce((n, c) => n + c.rules.length, 0)} cells`);
}
