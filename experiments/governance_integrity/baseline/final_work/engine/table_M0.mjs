// Usage: node work/engine/table_M0.mjs <results.jsonl> — compact table of the M0 AE checks (non-null values only, short names)
import fs from "fs";
const CC = "dirigeant . auto-entrepreneur . cotisations et contributions";
const short = n => n.replace(CC + " . cotisations . ", "").replace(CC, "CC").replace("protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur", "RCI.revenuAE").replace("protection sociale . retraite . base . cotisée . revenu auto-entrepreneur", "base.revenuAE").replace("dirigeant . auto-entrepreneur . ", "").replace(" . répartition . ", ".rep.").replace(" . taux de répartition", "").replace(/vente restauration hébergement/g, "vente").replace(/service BNC Cipav/g, "CIPAV").replace(/service BNC/g, "BNC").replace(/service BIC/g, "SBIC");
for (const line of fs.readFileSync(process.argv[2], "utf8").trim().split("\n")) {
  const r = JSON.parse(line); const cells = [];
  for (const [k, v] of Object.entries(r.results)) { if (v.error) { cells.push(short(k) + "=ERR"); continue; } if (v.value === null || v.value === undefined) continue; cells.push(short(k) + "=" + (typeof v.value === "number" ? +v.value.toFixed(4) : v.value) + (v.unit ? v.unit.replace("€/", "€/") : "")); }
  console.log(r.id.padEnd(24), (r.situation_error || r.error) ? "ERR " + (r.situation_error || r.error) : "", cells.join(" | "));
}
