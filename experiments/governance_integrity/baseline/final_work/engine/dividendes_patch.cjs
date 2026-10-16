// T0 addendum: evaluate the dividend 10 % rule and patch output/answer.json + notes.
const fs = require("fs"), { execFileSync } = require("child_process");
const R = "inputs/rules/G0_d9242882f96b/modele-social/règles";
const base = {"date":"01/01/2024","salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"non","entreprise . imposition":"'IS'","entreprise . activité . nature":"'commerciale'","entreprise . date de création":"01/01/2010","dirigeant . exonérations . ACRE":"non","dirigeant . rémunération . net":"30000 €/an","entreprise . capital social":"10000 €","bénéficiaire . dividendes . bruts":"5000 €/an"};
const rules = ["dirigeant . indépendant","bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant","bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire","bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant","dirigeant . indépendant . revenu professionnel","dirigeant . indépendant . assiette des cotisations","dirigeant . indépendant . cotisations et contributions . CSG-CRDS . assiette"];
function run(sit) { const a = ["src/publicodes_eval.mjs","evaluate","--rules",R,"--situation",JSON.stringify(sit)]; for (const r of rules) a.push("--rule", r); return JSON.parse(execFileSync("node", a, {encoding:"utf8", maxBuffer:1e8})); }
const withDiv = run(base), noDiv = run({...base, "bénéficiaire . dividendes . bruts": "0 €/an"});
const v = (res, r) => res.evaluations[r] && res.evaluations[r].nodeValue;
fs.writeFileSync("work/engine/results_T0_dividendes.json", JSON.stringify({id:"TI_IS_dividendes", situation:base, with_dividends:withDiv.evaluations, without_dividends:noDiv.evaluations, situation_error:withDiv.situation_error||null}, null, 1));
for (const r of rules) console.log(r, " = ", JSON.stringify(v(withDiv, r)), "| without dividends:", JSON.stringify(v(noDiv, r)));
if (withDiv.situation_error) console.log("SITUATION_ERROR", withDiv.situation_error);
const ari = v(withDiv, "bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant");
const maxf = v(withDiv, "bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant");
const baseWith = v(withDiv, "dirigeant . indépendant . assiette des cotisations"), baseNo = v(noDiv, "dirigeant . indépendant . assiette des cotisations");
const flows = typeof baseWith === "number" && typeof baseNo === "number" && Math.abs(baseWith - baseNo) > 1;
const ok = ari === 4000 && maxf === 1000;
const ans = JSON.parse(fs.readFileSync("output/answer.json", "utf8"));
ans.links.push({
  rule: "bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant", rules_pin: "G0", article: "L136-3", article_version_id: "LEGIARTI000048683641", in_force_from: "2023-12-28",
  quote: "qui est supérieure à 10 % d'un montant de référence constitué du capital social, primes d'émission incluses, détenu en toute propriété ou en usufruit par ces mêmes personnes et des sommes inscrites dans leurs comptes courants d'associés",
  claim: "For IS companies, the part of dividends above 10 % of (capital social + primes d'émission + comptes courants d'associés) belongs to the indépendant contribution base.",
  status: ok ? "VERIFIED" : "INFERRED",
  check: { rule: "bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant", situation: base, date: "01/01/2024", observed: ari, observed_unit: "€/an", expected: 4000,
    note: "5 000 dividends - 10 % x (10 000 capital + 0 compte courant) = 4 000. The 10 % threshold is reproduced; primes d'émission are not part of the rule's reference amount. `dirigeant . indépendant . assiette des cotisations` with dividends = " + JSON.stringify(baseWith) + " vs without = " + JSON.stringify(baseNo) + " (" + (flows ? "the excess dividends DO flow into the contribution base" : "the excess dividends do NOT reach `assiette des cotisations` in this situation; the rule is only exposed through the bénéficiaire tree, which carries a [TODO] [dividendes-indep] marker in the source") + ")." },
  approval: "none recorded", confidence: ok ? (flows ? "medium" : "low") : "low" });
ans.not_observable = ans.not_observable.map(s => s.startsWith("L136-3 II 2°") ? "L136-3 II 2°: the 10 % dividend threshold exists in `bénéficiaire . dividendes . cotisations et contributions . assiette régime indépendant` (see links), but primes d'émission are not counted in the reference amount, the family-member extension (conjoint, partenaire, enfants mineurs) and the EI-specific reference amount (II 2° last sentence) are not modelled" + (flows ? "." : ", and in the tested situation the excess did not change `dirigeant . indépendant . assiette des cotisations` (source marked [TODO] [dividendes-indep]).") : s);
ans.self_reported_tool_calls = 28;
fs.writeFileSync("output/answer.json", JSON.stringify(ans, null, 2) + "\n");
const para = "\n\n## Addendum — dividends (L136-3 II 2°)\n\nA late grep found the 10 % threshold in `bénéficiaire.publicodes`: `bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant` = (capital social + compte courant d'associé) x 10 % and `… assiette régime indépendant` = bruts - min(bruts, that). Engine (EI at IS, rémunération nette 30 000, capital 10 000, dividendes bruts 5 000, 01/01/2024): assiette régime indépendant = " + JSON.stringify(ari) + " €/an (expected 4 000), max forfaitaire = " + JSON.stringify(maxf) + ". `dirigeant . indépendant . assiette des cotisations` = " + JSON.stringify(baseWith) + " with dividends vs " + JSON.stringify(baseNo) + " without — " + (flows ? "the excess flows into the contribution base." : "the excess does not reach the contribution base in this situation (source marked [TODO] [dividendes-indep]).") + " Primes d'émission and the family-member extension are not modelled. Results in work/engine/results_T0_dividendes.json.\n";
fs.appendFileSync("output/NOTES.md", para);
fs.appendFileSync("work/notes/T0_findings.md", para);
console.log("patched answer.json: links =", ans.links.length, "status", ok ? "VERIFIED" : "INFERRED", "flows =", flows);
JSON.parse(fs.readFileSync("output/answer.json", "utf8")); console.log("answer.json parses OK");
