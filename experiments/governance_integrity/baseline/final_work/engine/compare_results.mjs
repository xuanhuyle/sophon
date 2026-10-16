// Usage: node work/engine/compare_results.mjs <before.jsonl> <after.jsonl> [all]
// Prints, per check, every rule whose (value, unit, missing, error) differs between the two result files; with "all" prints everything.
import fs from 'fs';
const [bf, af, mode] = process.argv.slice(2);
const rd = f => fs.readFileSync(f, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
const B = rd(bf), A = rd(af);
const fmt = v => !v ? '-' : v.error ? 'ERR:' + v.error.slice(0, 60) : JSON.stringify(v.value) + (v.unit ? ' ' + v.unit : '') + (v.missing ? ' [miss ' + v.missing + ']' : '');
let ndiff = 0, ncells = 0;
for (let i = 0; i < Math.max(A.length, B.length); i++) {
  const b = B[i] || {}, a = A[i] || {}; const keys = new Set([...Object.keys(b.results || {}), ...Object.keys(a.results || {})]);
  const rows = [];
  for (const k of keys) { ncells++; const fb = fmt((b.results || {})[k]), fa = fmt((a.results || {})[k]); if (fb !== fa) { ndiff++; rows.push('   ' + k + ' : ' + fb + '  ->  ' + fa); } else if (mode === 'all') rows.push('   ' + k + ' = ' + fa); }
  if (rows.length || b.situation_error !== a.situation_error) { console.log('### ' + (b.id || a.id) + ' @ ' + (b.date || a.date) + (b.situation_error || a.situation_error ? '  SITERR ' + b.situation_error + ' -> ' + a.situation_error : '')); rows.forEach(r => console.log(r)); }
}
console.log(`cells compared: ${ncells}, differing: ${ndiff}`);
