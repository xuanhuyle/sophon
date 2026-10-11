// Generates work/engine/checks_R4_rb.json : retraite de base checks for the R4 review (modele-ti + modele-commun trees).
import fs from 'fs';
const base = (date, activité, revenu, extra = {}) => ({
  date, 'entreprise . catégorie juridique': "'EI'", 'entreprise . imposition': "'IR'", 'entreprise . date de création': '01/01/2015',
  'entreprise . activité': `'${activité}'`, 'indépendant . revenu professionnel': `${revenu} €/an`, 'indépendant . revenu brut': `${revenu} €/an`, 'entreprise . imposition . IR . régime micro-fiscal': 'non', ...extra });
const PLR = { 'entreprise . activité . libérale . réglementée': 'oui', 'indépendant . profession libérale . réglementée . métier': "'rattaché Cipav'" };
const MED = { 'entreprise . activité . libérale . réglementée': 'oui', 'indépendant . profession libérale . réglementée . métier': "'santé'",
  'indépendant . profession libérale . réglementée . métier . santé': "'médecin'", 'indépendant . profession libérale . réglementée . métier . santé . médecin . secteur': "'S1'" };
const PLNR = { 'entreprise . activité . libérale . réglementée': 'non' };
const TABAC = { 'entreprise . activité . commerciale . débit de tabac': 'oui', 'indépendant . cotisations et contributions . déduction tabac': '5000 €/an' };
const rules = [
  'plafond sécurité sociale', 'indépendant . cotisations et contributions . PSS proratisé', 'indépendant . cotisations et contributions . après réforme',
  'indépendant . profession libérale . CNAVPL', 'indépendant . cotisations et contributions . assiette sociale',
  'indépendant . cotisations et contributions . cotisations . retraite de base',
  'indépendant . cotisations et contributions . cotisations . retraite de base . tranche 1',
  'indépendant . cotisations et contributions . cotisations . retraite de base . tranche 2',
  'indépendant . cotisations et contributions . cotisations . retraite de base . tranche 1 . taux',
  'indépendant . cotisations et contributions . cotisations . retraite de base . tranche 2 . taux',
  'indépendant . cotisations et contributions . cotisations . retraite de base . tranche 1 . assiette',
  'indépendant . cotisations et contributions . cotisations . retraite de base . assiette',
  'indépendant . cotisations et contributions . cotisations . retraite de base . taux T1',
  'indépendant . cotisations et contributions . cotisations . retraite de base . taux T2',
  'indépendant . profession libérale . CNAVPL . retraite de base', 'indépendant . profession libérale . CNAVPL . retraite de base . tranche 1',
  'indépendant . profession libérale . CNAVPL . retraite de base . tranche 2',
  'indépendant . cotisations et contributions . cotisations', 'indépendant . cotisations et contributions', 'indépendant . rémunération . nette',
  'protection sociale . retraite . base', 'protection sociale . retraite . base . revenu cotisé', 'protection sociale . retraite . base . trimestres',
  'protection sociale . retraite . base . CNAVPL', 'protection sociale . retraite . base . CNAVPL . points acquis'];
const checks = [];
const add = (id, situation) => checks.push({ id, situation, rules });
for (const [tag, date] of [['24', '01/12/2024'], ['25', '01/06/2025'], ['26', '01/03/2026']]) {
  for (const rev of [0, 6800, 7000, 20000, 46368, 47100, 50000, 60001, 63650, 75555, 100000, 123456, 300000]) add(`AC_${rev}@${tag}`, base(date, 'artisanale', rev));
  for (const rev of [20000, 100000]) add(`PLNR20_${rev}@${tag}`, base(date, 'libérale', rev, { ...PLNR, 'entreprise . date de création': '01/01/2020' }));
  for (const rev of [20000, 60001, 100000, 300000]) add(`PLNR_${rev}@${tag}`, base(date, 'libérale', rev, PLNR));
  for (const rev of [20000, 60001, 100000, 300000]) add(`CIPAV_${rev}@${tag}`, base(date, 'libérale', rev, PLR));
  for (const rev of [60001, 300000]) add(`MED_${rev}@${tag}`, base(date, 'libérale', rev, MED));
  for (const rev of [40000, 60001]) add(`TABAC_${rev}@${tag}`, base(date, 'commerciale', rev, TABAC));
}
fs.writeFileSync('work/engine/checks_R4_rb.json', JSON.stringify(checks, null, 1));
console.log(checks.length + ' checks');
