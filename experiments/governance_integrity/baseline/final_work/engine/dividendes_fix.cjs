const fs = require("fs");
const ans = JSON.parse(fs.readFileSync("output/answer.json", "utf8"));
const l = ans.links.find(x => x.rule.startsWith("bénéficiaire . dividendes"));
l.status = "INFERRED"; l.confidence = "low";
l.check.match = false; l.check.inconclusive = true;
l.check.note = "INCONCLUSIVE: in this EI-at-IS situation the rule, `assiette forfaitaire` and `assiette forfaitaire max indépendant` all evaluated to null (non applicable), so no executable check settles the 10 % threshold; the bénéficiaire tree apparently needs a company/associate context that was not reproduced within the T0 budget. From the YAML only: `assiette forfaitaire max indépendant` = (entreprise . capital social + compte courant d'associé) x 10 % and `assiette régime indépendant` = bruts - min(bruts, that) — primes d'émission are not included and the block is marked [TODO] [dividendes-indep]. `dirigeant . indépendant . assiette des cotisations` = 31 183,89 €/an with or without 5 000 € of dividends, i.e. nothing from the dividend rules reaches the contribution base here.";
ans.not_observable = ans.not_observable.map(s => s.startsWith("L136-3 II 2°") ? "L136-3 II 2°: a 10 % dividend threshold exists in the YAML (`bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant`, block marked [TODO] [dividendes-indep]) but it evaluated to null for an EI at IS and did not change `dirigeant . indépendant . assiette des cotisations`; primes d'émission, the family-member extension (conjoint, partenaire, enfants mineurs) and the EI-specific reference amount (II 2° last sentence) are not modelled. Treat the dividend provision as not observable at G0 until a company situation is found that activates the rule." : s);
ans.self_reported_tool_calls = 30;
fs.writeFileSync("output/answer.json", JSON.stringify(ans, null, 2) + "\n");
const para = "\n\n## Addendum — dividends (L136-3 II 2°)\n\nA late grep found a 10 % threshold in `bénéficiaire.publicodes`: `bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant` = (capital social + compte courant d'associé) x 10 % and `… assiette régime indépendant` = bruts - min(bruts, that), block marked [TODO] [dividendes-indep]. Engine run (EI at IS, rémunération nette 30 000, capital 10 000, dividendes bruts 5 000, 01/01/2024): all three dividend rules returned null (non applicable) and `dirigeant . indépendant . assiette des cotisations` = 31 183,89 with or without the dividends. So the check is inconclusive (status INFERRED, confidence low) and the provision stays in not_observable; primes d'émission and the family-member extension are not modelled anyway. Next time: find the company situation (catégorie juridique SARL/EURL, associés) that activates `bénéficiaire . dividendes`. Results in work/engine/results_T0_dividendes.json.\n";
for (const f of ["output/NOTES.md", "work/notes/T0_findings.md"]) {
  let s = fs.readFileSync(f, "utf8");
  const k = s.indexOf("\n\n## Addendum — dividends");
  if (k >= 0) s = s.slice(0, k);
  fs.writeFileSync(f, s + para);
}
JSON.parse(fs.readFileSync("output/answer.json", "utf8"));
console.log("fixed; links =", ans.links.length, "; statuses:", JSON.stringify(ans.links.reduce((a, x) => (a[x.status] = (a[x.status] || 0) + 1, a), {})), "; tool calls field =", ans.self_reported_tool_calls);
