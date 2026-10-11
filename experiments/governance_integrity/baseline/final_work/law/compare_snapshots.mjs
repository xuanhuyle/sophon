// Usage: node work/law/compare_snapshots.mjs <new_articles.json> <old_index.json> <old_texts.md> <tag>
// v2 (R1): also stores/compares the `nota` field (application dates!). Writes work/law/<tag>_index.json and work/law/<tag>_texts.md (same format as S0), prints a diff report.
import fs from "fs";
const [newPath, oldIdxPath, oldTxtPath, tag] = process.argv.slice(2);
const d = x => x == null ? null : new Date(x).toISOString().slice(0, 10);
const raw = JSON.parse(fs.readFileSync(newPath, "utf8"));
const recs = [];
for (const [num, list] of Object.entries(raw.articles)) for (const r of (Array.isArray(list) ? list : [list])) recs.push(r);
const newIdx = recs.map(r => ({ num: r.num, id: r.id, cid: r.cid, etat: r.etat, dateDebut: d(r.dateDebut), dateFin: d(r.dateFin),
  versions: (r.articleVersions || []).map(v => ({ id: v.id, etat: v.etat, dateDebut: d(v.dateDebut), dateFin: d(v.dateFin) })),
  lienModifications: r.lienModifications }));
fs.writeFileSync(`work/law/${tag}_index.json`, JSON.stringify(newIdx, null, 1));
let md = `# CSS articles ${raw.snapshot} (legi-data ${raw.legi_data_version}, published ${raw.published})\n\nmissing: ${JSON.stringify(raw.articles_missing_in_snapshot)}\n\n`;
for (const r of recs) md += `## ${r.num} — ${r.id} — ${r.etat} — in force ${d(r.dateDebut)} → ${d(r.dateFin)}\n\n${(r.text || "").trim()}${r.nota ? "\n\nNOTA: " + String(r.nota).trim() : ""}\n\n`;
fs.writeFileSync(`work/law/${tag}_texts.md`, md);
// old
const oldIdx = JSON.parse(fs.readFileSync(oldIdxPath, "utf8"));
const oldTxt = fs.readFileSync(oldTxtPath, "utf8");
const oldTexts = {}; const oldNotas = {};
for (const m of oldTxt.split(/^## /m).slice(1)) { const nl = m.indexOf("\n"); const head = m.slice(0, nl); const num = head.split(" — ")[0].trim(); let body = m.slice(nl).trim(); const ni = body.indexOf("\nNOTA: "); if (ni >= 0) { oldNotas[num] = body.slice(ni + 7).trim(); body = body.slice(0, ni).trim(); } oldTexts[num] = body; }
console.log("snapshot", raw.snapshot, raw.legi_data_version, raw.published, "missing:", raw.articles_missing_in_snapshot);
console.log("records:", recs.length, "nums:", [...new Set(recs.map(r => r.num))].join(","));
const norm = s => (s || "").replace(/\s+/g, " ").trim();
for (const n of newIdx) {
  const o = oldIdx.find(x => x.num === n.num);
  const r = recs.find(x => x.num === n.num && x.id === n.id);
  const changes = [];
  if (!o) { changes.push("NEW ARTICLE (not in S0)"); }
  else {
    for (const k of ["id", "etat", "dateDebut", "dateFin"]) if (o[k] !== n[k]) changes.push(`${k}: ${o[k]} -> ${n[k]}`);
    const ov = new Set(o.versions.map(v => v.id)), nv = new Set(n.versions.map(v => v.id));
    for (const v of n.versions) if (!ov.has(v.id)) changes.push(`version ADDED: ${JSON.stringify(v)}`);
    for (const v of o.versions) if (!nv.has(v.id)) changes.push(`version REMOVED: ${JSON.stringify(v)}`);
    for (const v of n.versions) { const w = o.versions.find(x => x.id === v.id); if (w && (w.etat !== v.etat || w.dateDebut !== v.dateDebut || w.dateFin !== v.dateFin)) changes.push(`version CHANGED: ${JSON.stringify(w)} -> ${JSON.stringify(v)}`); }
    const key = l => `${l.textCid}|${l.textTitle}|${l.linkType}|${l.dateDebutCible}`;
    const ol = new Set((o.lienModifications || []).map(key)), nl = new Set((n.lienModifications || []).map(key));
    for (const l of n.lienModifications || []) if (!ol.has(key(l))) changes.push(`lien ADDED: ${JSON.stringify(l)}`);
    for (const l of o.lienModifications || []) if (!nl.has(key(l))) changes.push(`lien REMOVED: ${JSON.stringify(l)}`);
    if (norm(oldTexts[n.num]) !== norm(r.text)) changes.push(`TEXT CHANGED (old len ${norm(oldTexts[n.num]).length}, new len ${norm(r.text).length})`);
    if (norm(oldNotas[n.num]) !== norm(r.nota)) changes.push(`NOTA CHANGED: ${JSON.stringify(norm(r.nota)).slice(0, 400)}`);
  }
  console.log(`\n### ${n.num} ${n.id} ${n.etat} ${n.dateDebut}→${n.dateFin}: ${changes.length ? "CHANGED" : "same"}`);
  for (const c of changes) console.log("   - " + c);
  if (changes.length && r && r.nota) console.log("   nota: " + norm(r.nota).slice(0, 400));
}
for (const o of oldIdx) if (!newIdx.find(x => x.num === o.num)) console.log(`\n### ${o.num}: REMOVED from new snapshot`);
