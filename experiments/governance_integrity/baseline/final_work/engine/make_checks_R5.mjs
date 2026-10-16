// Generates work/engine/checks_R5_mayotte.json : D136-5 floor/cap at Mayotte (commit c14ee26d0c67), modele-ti + modele-commun trees.
import fs from 'fs';
let names = [];
try { const raw = fs.readFileSync('work/engine/list_R5_context_tree_after.json', 'utf8'); const j = JSON.parse(raw); names = Array.isArray(j) ? j : (j.rules || j.names || Object.keys(j.rules || {})); } catch (e) { names = []; }
if (!names.length) names = fs.readFileSync('work/engine/list_R5_context_tree_after.json', 'utf8').split('\n').map(s => s.replace(/^\s*"|",?\s*$/g, '')).filter(s => s.includes(' . '));
const children = names.filter(n => /^indépendant \. cotisations et contributions \. cotisations \. [^.]+$/.test(n) && !/exonérations|conjoint/.test(n));
const base = (date, activité, revenu, extra = {}) => ({
  date, 'entreprise . catégorie juridique': "'EI'", 'entreprise . imposition': "'IR'", 'entreprise . date de création': '01/01/2015',
  'entreprise . activité': `'${activité}'`, 'indépendant . revenu professionnel': `${revenu} €/an`, 'indépendant . revenu brut': `${revenu} €/an`,
  'entreprise . imposition . IR . régime micro-fiscal': 'non', ...extra });
const MAY = { 'établissement . commune . département': "'Mayotte'" };
const PARIS = { 'établissement . commune . département': "'Paris'" };
const PLNR = { 'entreprise . activité . libérale . réglementée': 'non' };
const rules = [
  'établissement . commune . département . outre-mer . Mayotte', 'plafond sécurité sociale', 'plafond sécurité sociale . annuel',
  'indépendant . cotisations et contributions . après réforme',
  'indépendant . cotisations et contributions . assiette CSG-CRDS . abattement . plancher',
  'indépendant . cotisations et contributions . assiette CSG-CRDS . abattement . plafond',
  'indépendant . cotisations et contributions . assiette CSG-CRDS . abattement',
  'indépendant . cotisations et contributions . assiette CSG-CRDS',
  'indépendant . cotisations et contributions . assiette sociale',
  'indépendant . cotisations et contributions . CSG-CRDS',
  'indépendant . cotisations et contributions . cotisations',
  ...children,
  'indépendant . cotisations et contributions', 'indépendant . rémunération . nette'];
const checks = []; const add = (id, situation) => checks.push({ id, situation, rules });
for (const [tag, date] of [['25', '01/06/2025'], ['26', '01/03/2026']]) {
  for (const rev of [0, 1000, 2000, 2290, 2300, 20000, 100000, 169000, 170000, 300000]) add(`MAY_AC_${rev}@${tag}`, base(date, 'artisanale', rev, MAY));
  for (const rev of [2000, 20000, 300000]) add(`METRO_unset_AC_${rev}@${tag}`, base(date, 'artisanale', rev));
  for (const rev of [2000, 300000]) add(`PARIS_AC_${rev}@${tag}`, base(date, 'artisanale', rev, PARIS));
}
for (const rev of [2000, 300000]) add(`MAY_AC_${rev}@24`, base('01/12/2024', 'artisanale', rev, MAY));
for (const rev of [2000, 300000]) add(`MAY_PLNR_${rev}@25`, base('01/06/2025', 'libérale', rev, { ...MAY, ...PLNR }));
fs.writeFileSync('work/engine/checks_R5_mayotte.json', JSON.stringify(checks, null, 1));
console.log(checks.length + ' checks; rules (' + rules.length + '):'); console.log(rules.join('\n'));
