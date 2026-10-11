#!/usr/bin/env python3
"""R3 links: law S5 (legi-data 2.385.0, == S4 == S3 texts) + S0 (for the D613-4 version in force before 2024-06-01);
rules G2 (= BEFORE commit 9bb43d710094) and G2post_R3 (= AFTER, G2 + forward patch).
usage: python3 -I work/scripts/add_links_R3.py   (from the staging dir). Appends to work/sophon/link_results_R3.jsonl.
Situations are taken by id from work/evals/cases_R3_drom.json (same ones as the before/after evals)."""
import json, re, subprocess, sys
STORE = 'work/sophon/store'
raw = json.load(open('inputs/law/S5_legi-data-2.385.0/articles.json'))['articles']
arts = {k: v[0] for k, v in raw.items()}
S0 = json.load(open('work/sophon/store/law/S0.json'))['articles']
def flex(s):
    out = []
    for ch in s:
        if ch == ' ': out.append(r'\s')
        elif ch == "'": out.append(r"['’]")
        else: out.append(re.escape(ch))
    return ''.join(out)
def q(num, pattern, text=None):
    t = text if text is not None else arts[num]['text']; m = re.search(pattern, t); assert m, (num, pattern); return m.group(0)
Q_FRAC1 = q('D756-5', flex("1/6 pour les travailleurs indépendants mentionnés au 2° de l'article L. 611-1 et 1/3 dans les autres cas, jusqu'à la fin du septième trimestre civil qui suit celui au cours duquel intervient la date d'effet de l'affiliation"))
Q_FRAC2 = q('D756-5', flex("1/2 pour la période qui court entre la fin de la période mentionnée au a et la fin de la troisième année civile d'activité"))
Q_FRAC3 = q('D756-5', flex("2/3 à compter de la quatrième année civile d'activité"))
Q_ROUND = q('D756-5', flex("après arrondi au dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1"))
Q_CAP = q('D756-5', flex("L'exonération prévue au I est calculée sur le chiffre d'affaires ou les recettes dans la limite du seuil fixé par les articles 50-0 et 102 ter du code général des impôts"))
Q_BNC23 = q('D613-4', r'10\s000 euros 34\s% 6\s600 euros 23,1\s%')
Q_CIPAV23 = q('D613-4', r'35\s076 euros 34\s% 23\s150 euros 23,2\s%')
Q_BIC = q('D613-4', r'46\s300 euros 50\s% 23\s150 euros 21,2\s%')
Q_VENTE = q('D613-4', r'79\s828 euros 71\s% 23\s150 euros 12,3\s%')
Q_BNC21 = q('D613-4', r'10\s000 euros 34\s% 6\s600 euros 21,1\s%', S0['D613-4']['text'])
Q_CIPAV21 = q('D613-4', r'35\s076 euros 34\s% 23\s150 euros 21,2\s%', S0['D613-4']['text'])
Q_L6137 = q('L613-7', flex("Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale"))
V = {k: arts[k]['id'] for k in ('L613-7', 'D756-5', 'D613-4')}; V0 = S0['D613-4']['id']
print('versions', V, 'S0 D613-4', V0, file=sys.stderr)
CASES = {c['id']: c['situation'] for c in json.load(open('work/evals/cases_R3_drom.json'))}
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . "
D = "dirigeant . auto-entrepreneur . DROM"
D4 = f"D613-4 v.{V['D613-4']} (in force 2024-07-01..2025-05-01)"; D4o = f"D613-4 v.{V0} (in force 2022-12-10..2024-06-01, text in store snapshot S0)"
P = f"D756-5 v.{V['D756-5']} (in force since 2017-05-12)"
BASE_NOTE = " The base rates are read in D613-4 because D756-5 still cites the pre-2020 numbering 'D. 131-6-1' (renumbering decree outside the bounded set); the 1/6-vs-1/3 split rests on L. 611-1 (outside the set) and follows the library's own reading (1/3 = CIPAV)."
specs = []
def add(tag, art, law, quote, rule, snap, check, case, expect, claim, status=None):
    specs.append(dict(tag=tag, art=art, law=law, quote=quote, rule=rule, snap=snap, check=check, case=case, expect=expect, claim=claim, status=status))
# ---- BEFORE (G2): DROM fractions not applied at all
add("R3-G2-D756-5-1/6-BNC-05/2024", 'D756-5', 'S5', Q_FRAC1, D, 'G2', C + "service BNC", "DROM_BNC_P1_05-2024", "36",
    f"{P} a): 1/6 of the base rate during the first 7 quarters. At 01/05/2024 the base is BNC 21,1 % ({D4o}): 21,1/6 = 3,517 -> rounded up 3,6 % -> 36 €/mois on 1 000 €/mois. BEFORE commit 9bb43d710094 (G2) the DROM rate rules are nested inside 'seconde période' and not parsed (1258 rules): the engine charges the full 21,1 % = 211 €/mois (expected FAILED)." + BASE_NOTE)
add("R3-G2-D756-5-1/6-BNC-10/2024", 'D756-5', 'S5', Q_FRAC1, D, 'G2', C + "service BNC", "DROM_BNC_P1_10-2024", "39",
    f"{P} a) x {D4} e) BNC 23,1 %: 23,1/6 = 3,85 -> rounded up 3,9 % -> 39 €/mois. BEFORE (G2): full 23,1 % = 231 €/mois (expected FAILED).")
add("R3-G2-D756-5-1/6-BIC-10/2024", 'D756-5', 'S5', Q_FRAC1, D, 'G2', C + "service BIC", "DROM_BIC_P1_10-2024", "36",
    f"{P} a) x {D4} d) BIC 21,2 %: 21,2/6 = 3,533 -> 3,6 % -> 36 €/mois. BEFORE (G2): full 21,2 % = 212 €/mois (expected FAILED).")
add("R3-G2-D756-5-1/6-VENTE-10/2024", 'D756-5', 'S5', Q_FRAC1, D, 'G2', C + "vente restauration hébergement", "DROM_VENTE_P1_10-2024", "21",
    f"{P} a) x {D4} a) vente 12,3 %: 12,3/6 = 2,05 -> 2,1 % -> 21 €/mois. BEFORE (G2): full 12,3 % = 123 €/mois (expected FAILED).")
# ---- AFTER (G2post_R3): BIC and vente aligned
A = 'G2post_R3'
add("R3-after-D756-5-1/6-BIC-10/2024", 'D756-5', 'S5', Q_FRAC1, D + " . taux service BIC", A, C + "service BIC", "DROM_BIC_P1_10-2024", "36", f"{P} a) x {D4} d) 21,2 %: 21,2/6 = 3,533 -> 3,6 % = 36 €/mois. AFTER the commit the DROM rule replaces the BIC rate: engine 36 (aligned)." + BASE_NOTE)
add("R3-after-D613-4-BIC-base", 'D613-4', 'S5', Q_BIC, D + " . taux service BIC", A, C + "service BIC", "DROM_BIC_P1_10-2024", "36", f"{D4} d) BIC services 21,2 % is the base of the DROM fraction (1/6 -> 3,6 %); engine 36 €/mois at 01/10/2024 (aligned).")
add("R3-after-D756-5-1/2-BIC-10/2024", 'D756-5', 'S5', Q_FRAC2, D + " . taux service BIC", A, C + "service BIC", "DROM_BIC_P2_10-2024", "106", f"{P} b): 1/2 x 21,2 = 10,6 % -> 106 €/mois (aligned).")
add("R3-after-D756-5-2/3-BIC-10/2024", 'D756-5', 'S5', Q_FRAC3, D + " . taux service BIC", A, C + "service BIC", "DROM_BIC_P3_10-2024", "142", f"{P} c): 2/3 x 21,2 = 14,133 -> rounded up 14,2 % -> 142 €/mois (aligned).")
add("R3-after-D756-5-arrondi-BIC", 'D756-5', 'S5', Q_ROUND, D + " . taux service BIC", A, C + "service BIC", "DROM_BIC_P3_10-2024", "142", f"{P}: rounding UP to the tenth of a percent: 14,133 -> 14,2 (engine 142 €/mois on 1 000 €/mois; aligned for BIC).")
add("R3-after-D756-5-1/6-VENTE-10/2024", 'D756-5', 'S5', Q_FRAC1, D + " . taux vente restauration hébergement", A, C + "vente restauration hébergement", "DROM_VENTE_P1_10-2024", "21", f"{P} a) x {D4} a) 12,3 %: 2,05 -> 2,1 % = 21 €/mois (aligned).")
add("R3-after-D613-4-VENTE-base", 'D613-4', 'S5', Q_VENTE, D + " . taux vente restauration hébergement", A, C + "vente restauration hébergement", "DROM_VENTE_P1_10-2024", "21", f"{D4} a) vente 12,3 % is the base of the DROM fraction (1/6 -> 2,1 %); engine 21 €/mois (aligned).")
add("R3-after-D756-5-1/2-VENTE-10/2024", 'D756-5', 'S5', Q_FRAC2, D + " . taux vente restauration hébergement", A, C + "vente restauration hébergement", "DROM_VENTE_P2_10-2024", "62", f"{P} b): 1/2 x 12,3 = 6,15 -> 6,2 % = 62 €/mois (aligned).")
add("R3-after-D756-5-2/3-VENTE-10/2024", 'D756-5', 'S5', Q_FRAC3, D + " . taux vente restauration hébergement", A, C + "vente restauration hébergement", "DROM_VENTE_P3_10-2024", "82", f"{P} c): 2/3 x 12,3 = 8,2 % = 82 €/mois (aligned).")
# ---- AFTER: BNC and CIPAV built on the superseded 21,1 / 21,2 bases -> MISMATCH for dates >= 2024-07-01
add("R3-after-D756-5-1/6-BNC-10/2024", 'D756-5', 'S5', Q_FRAC1, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P1_10-2024", "39", f"{P} a) x {D4} e) BNC 23,1 %: 23,1/6 = 3,85 -> rounded up 3,9 % -> 39 €/mois. AFTER the commit the engine computes 3,6 % = 36 €/mois (1/6 of the superseded 21,1 %) -> MISMATCH (expected FAILED)." + BASE_NOTE)
add("R3-after-D613-4-BNC-base-23,1", 'D613-4', 'S5', Q_BNC23, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P1_10-2024", "39", f"{D4} e) BNC 23,1 % in force at 01/10/2024; DROM 1/6 -> 3,9 % = 39 €/mois; engine 36 (MISMATCH, expected FAILED).")
add("R3-after-D756-5-1/2-BNC-10/2024", 'D756-5', 'S5', Q_FRAC2, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P2_10-2024", "116", f"{P} b): 1/2 x 23,1 = 11,55 -> 11,6 % -> 116 €/mois; engine 10,6 % = 106 (MISMATCH, expected FAILED).")
add("R3-after-D756-5-2/3-BNC-10/2024", 'D756-5', 'S5', Q_FRAC3, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P3_10-2024", "154", f"{P} c): 2/3 x 23,1 = 15,4 % -> 154 €/mois; engine 14,1 % = 141 (MISMATCH, expected FAILED).")
add("R3-after-S0-D613-4-BNC-21,1-05/2024", 'D613-4', 'S0', Q_BNC21, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P1_05-2024", "36", f"{D4o} e) BNC 21,1 %: 1/6 -> 3,517 -> 3,6 % = 36 €/mois at 01/05/2024; engine 36. The commit's BNC values are correct ONLY for dates before 2024-07-01 (that version was superseded by v.{V['D613-4']}).")
add("R3-after-S0-D613-4-BNC-2/3-05/2024", 'D756-5', 'S5', Q_FRAC3, D + " . taux service BNC", A, C + "service BNC", "DROM_BNC_P3_05-2024", "141", f"{P} c) x BNC 21,1 % ({D4o}): 14,067 -> 14,1 % = 141 €/mois at 01/05/2024; engine 141 (aligned for the pre-07/2024 base only).")
add("R3-after-D756-5-1/3-CIPAV-10/2024", 'D756-5', 'S5', Q_FRAC1, D + " . taux CIPAV", A, C + "cotisations CIPAV", "DROM_CIPAV_P1_10-2024", "936", f"{P} a) '1/3 dans les autres cas' x {D4} b) CIPAV 23,2 %: 23,2/3 = 7,733 -> rounded up 7,8 % -> 936 €/an on 12 000 €/an. AFTER the commit the engine computes 7,1 % = 852 €/an (1/3 of the superseded 21,2 %) -> MISMATCH (expected FAILED)." + BASE_NOTE)
add("R3-after-D613-4-CIPAV-base-23,2", 'D613-4', 'S5', Q_CIPAV23, D + " . taux CIPAV", A, C + "cotisations CIPAV", "DROM_CIPAV_P1_10-2024", "936", f"{D4} b) CIPAV 23,2 % in force at 01/10/2024; DROM 1/3 -> 7,8 % = 936 €/an; engine 852 (MISMATCH, expected FAILED).")
add("R3-after-D756-5-1/2-CIPAV-10/2024", 'D756-5', 'S5', Q_FRAC2, D + " . taux CIPAV", A, C + "cotisations CIPAV", "DROM_CIPAV_P2_10-2024", "1392", f"{P} b): 1/2 x 23,2 = 11,6 % -> 1 392 €/an; engine 10,6 % = 1 272 (MISMATCH, expected FAILED).")
add("R3-after-D756-5-2/3-CIPAV-10/2024", 'D756-5', 'S5', Q_FRAC3, D + " . taux CIPAV", A, C + "cotisations CIPAV", "DROM_CIPAV_P3_10-2024", "1860", f"{P} c): 2/3 x 23,2 = 15,467 -> 15,5 % -> 1 860 €/an; engine 14,2 % = 1 704 (MISMATCH, expected FAILED).")
add("R3-after-S0-D613-4-CIPAV-21,2-05/2024", 'D613-4', 'S0', Q_CIPAV21, D + " . taux CIPAV", A, C + "cotisations CIPAV", "DROM_CIPAV_P1_05-2024", "852", f"{D4o} b) CIPAV 21,2 %: 1/3 -> 7,067 -> 7,1 % = 852 €/an at 01/05/2024; engine 852 (aligned for the pre-07/2024 base only).")
# ---- textual links without executable check
add("R3-after-D756-5-II-plafond-CA", 'D756-5', 'S5', Q_CAP, D, A, None, None, None, f"{P} II: the DROM reduction applies only up to the micro-fiscal CA threshold (CGI 50-0 / 102 ter, outside the set). Not implemented before or after the commit (no CA cap in the DROM rules): pre-existing gap, textual link only.", status='INFERRED')
add("R3-after-L613-7-taux-different-exoneration", 'L613-7', 'S5', Q_L6137, D, A, None, None, None, f"L613-7 v.{V['L613-7']} I: a different global rate may be set by decree for exemption periods; D756-5 is such a decree provision for the DROM. Textual link only.", status='INFERRED')
out = open('work/sophon/link_results_R3.jsonl', 'a')
for s in specs:
    cmd = ['python3', 'src/sophon.py', '--store', STORE, 'link', 'add', '--rule', s['rule'], '--rules-snapshot', s['snap'], '--article', s['art'], '--law-snapshot', s['law'], '--quote', s['quote'], '--claim', s['claim']]
    sit = CASES[s['case']] if s['case'] else None
    if s['check']:
        cmd += ['--check-rule', s['check'], '--check-situation', json.dumps(sit, ensure_ascii=False), '--expect', s['expect'], '--tolerance', '0.001']
    else:
        cmd += ['--status', s['status']]
    p = subprocess.run(cmd, capture_output=True, text=True)
    aid = V[s['art']] if s['law'] == 'S5' else V0
    rec = {'tag': s['tag'], 'article': s['art'], 'law_snapshot': s['law'], 'article_id': aid, 'quote': s['quote'], 'rule': s['rule'], 'snap': s['snap'], 'check_rule': s['check'], 'case': s['case'], 'situation': sit, 'expect': s['expect'], 'rc': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()[-400:]}
    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
    try: j = json.loads(p.stdout.strip().splitlines()[-1]); cr = j.get('check_result') or {}
    except Exception: j = {}; cr = {}
    print(f"{s['tag']:48s} {j.get('link_id')} {j.get('status')} exp={s['expect']} obs={cr.get('observed')} {('ERR:' + str(cr.get('error')))[:80] if cr.get('error') else ''} {('REJ:' + p.stdout[:120]) if not j.get('link_id') else ''}")
