// Record-level deep compare of two legi-data snapshots of the bounded article set (same format as M0_S6_S7_record_diff.json).
// Usage: node work/law/record_diff.mjs <old articles.json> <new articles.json> <OLDTAG> <NEWTAG> <out.json>
import fs from "fs"; import crypto from "crypto";
const [oldP, newP, OT, NT, out] = process.argv.slice(2);
const load = p => { const raw = JSON.parse(fs.readFileSync(p, "utf8")); const m = {}; for (const [n, l] of Object.entries(raw.articles)) for (const r of (Array.isArray(l) ? l : [l])) m[n] = r; return { raw, m }; };
const A = load(oldP), B = load(newP);
const d = x => x == null ? null : new Date(x).toISOString().slice(0, 10);
const sha = s => crypto.createHash("sha256").update(s || "").digest("hex");
const res = { [OT]: { legi_data_version: A.raw.legi_data_version, published: A.raw.published }, [NT]: { legi_data_version: B.raw.legi_data_version, published: B.raw.published }, articles: {} };
for (const n of Object.keys(B.m)) {
  const a = A.m[n], b = B.m[n];
  const changed = Object.keys({ ...a, ...b }).filter(k => JSON.stringify(a[k]) !== JSON.stringify(b[k]));
  res.articles[n] = { record_identical: changed.length === 0, [`id_${OT}`]: a.id, [`id_${NT}`]: b.id, [`etat_${OT}`]: a.etat, [`etat_${NT}`]: b.etat,
    [`inforce_${OT}`]: `${d(a.dateDebut)} → ${d(a.dateFin)}`, [`inforce_${NT}`]: `${d(b.dateDebut)} → ${d(b.dateFin)}`,
    [`text_sha256_${OT}`]: sha(a.text), [`text_sha256_${NT}`]: sha(b.text), changed_fields: changed,
    [`nota_${NT}`]: b.nota || null, [`liens_${NT}`]: (b.lienModifications || []).map(l => `${l.textTitle} (${l.linkType}, JORF ${l.datePubliTexte}, effet ${l.dateDebutCible})`),
    [`versions_${NT}`]: (b.articleVersions || []).map(v => `${v.id} ${v.etat} ${d(v.dateDebut)}→${d(v.dateFin)}`) };
}
fs.writeFileSync(out, JSON.stringify(res, null, 1));
for (const [n, r] of Object.entries(res.articles)) console.log(n.padEnd(9), r.record_identical ? "identical" : "CHANGED: " + r.changed_fields.join(","), "|", r[`id_${NT}`], r[`inforce_${NT}`]);
