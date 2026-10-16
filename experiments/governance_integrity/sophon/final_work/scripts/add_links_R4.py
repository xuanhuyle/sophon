#!/usr/bin/env python3
"""R4 links: law S9 (legi-data 2.514.0), article D633-3 v.LEGIARTI000049904636 (in force 2024-07-07, applicable to
periods from 2025-01-01 per the decree's nota) <-> indépendant retraite de base rules, on the two trees of commit
d3e0cfe0f12d: G4pre_R4 (parent, "tranche 1 + tranche 2" = the CSS formula) and G4post_R4 (after, Urssaf barème).
usage: python3 -I work/scripts/add_links_R4.py   (from the staging dir). Appends to work/sophon/link_results_R4.jsonl.
Situations are taken by id from work/evals/cases_R4.json (the same ones as the before/after evals)."""
import json, re, subprocess, sys
STORE = 'work/sophon/store'
raw = json.load(open('inputs/law/S9_legi-data-2.514.0/articles.json'))['articles']
arts = {k: v[0] for k, v in raw.items()}
def flex(s):
    out = []
    for ch in s:
        if ch == ' ': out.append(r'\s')
        elif ch == "'": out.append(r"['’]")
        else: out.append(re.escape(ch))
    return ''.join(out)
def q(num, pattern):
    t = arts[num]['text']; m = re.search(pattern, t); assert m, (num, pattern); return m.group(0)
QI = q('D633-3', flex("Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %."))
QII = q('D633-3', flex("Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %."))
V = arts['D633-3']['id']
D = f"D633-3 v.{V} (in force 2024-07-07; nota: applies to periods from 2025-01-01)"
print('version', V, file=sys.stderr)
CASES = {c['id']: c['situation'] for c in json.load(open('work/evals/cases_R4.json'))}
RB = "indépendant . cotisations et contributions . cotisations . retraite de base"
PRE, POST = 'G4pre_R4', 'G4post_R4'
URSSAF = (" The commit replaces the CSS decomposition (T1 on the capped base + T2 on the WHOLE base) by the Urssaf"
          " presentation (T1' = 17,15 + 0,72 = 17,87 % on the part <= PSS, T2 = 0,72 % on the part above PSS only);"
          " the two are algebraically identical for every assiette: 17,15 x min(A,P) + 0,72 x A = 17,87 x min(A,P) + 0,72 x max(A-P,0).")
specs = []
def add(tag, quote, rule, snap, check, case, expect, claim, status=None, tol=1.0):
    specs.append(dict(tag=tag, quote=quote, rule=rule, snap=snap, check=check, case=case, expect=expect, claim=claim, status=status, tol=tol))
# ---- BEFORE (G4pre_R4): the library literally transcribes D633-3 I and II
add("R4-pre-D633-3-I-taux-17.15", QI, RB + " . tranche 1 . taux", PRE, RB + " . tranche 1 . taux", "AC_60000_2025", "17.15",
    f"{D} I: 17,15 % on the assiette within the plafond. BEFORE the commit `tranche 1 . taux` = 17,15 % for artisans/commerçants/PLNR at 01/07/2025 (textual rate).", tol=1e-6)
add("R4-pre-D633-3-II-taux-0.72", QII, RB + " . tranche 2 . taux", PRE, RB + " . tranche 2 . taux", "AC_60000_2025", "0.72",
    f"{D} II: 0,72 % on the totality of the assiette. BEFORE the commit `tranche 2 . taux` = 0,72 % (après réforme = date >= 01/2025) (textual rate).", tol=1e-6)
add("R4-pre-D633-3-I-amount-60000", QI, RB, PRE, RB, "AC_60000_2025", "8510",
    f"{D} I+II on assiette 60 000 (> PSS 2025 = 47 100): 17,15 % x 47 100 = 8 077,65 + 0,72 % x 60 000 = 432 -> 8 509,65 -> 8 510 €/an. BEFORE: tranche 1 (8 078) + tranche 2 (432) = 8 510 (aligned).")
add("R4-pre-D633-3-II-amount-20000", QII, RB, PRE, RB, "AC_20000_2025", "3574",
    f"{D} on assiette 20 000 (<= PSS): (17,15 + 0,72) % x 20 000 = 3 574 €/an. BEFORE: 3 430 + 144 = 3 574 (aligned).")
add("R4-pre-D633-3-I-amount-250000", QI, RB, PRE, RB, "AC_250000_2025", "9878",
    f"{D} on assiette 250 000: 8 077,65 + 0,72 % x 250 000 (1 800, uncapped per II 'totalité de l'assiette') = 9 877,65 -> 9 878 €/an. BEFORE: 8 078 + 1 800 = 9 878 (aligned).")
# ---- AFTER (G4post_R4): Urssaf barème, same amounts
add("R4-post-D633-3-I+II-tauxT1-17.87", QI, RB + " . taux T1", POST, RB + " . taux T1", "AC_60000_2025", "17.87",
    f"{D}: the text states 17,15 % (I) within the plafond and 0,72 % (II) on the whole assiette; AFTER the commit `taux T1` = 17,87 % = 17,15 + 0,72 applied to the part <= PSS, i.e. the two textual rates folded together (Urssaf presentation, not a rate written in the text)." + URSSAF, tol=1e-6)
add("R4-post-D633-3-II-tauxT2-0.72", QII, RB + " . taux T2", POST, RB + " . taux T2", "AC_60000_2025", "0.72",
    f"{D} II: 0,72 %. AFTER the commit `taux T2` = 0,72 % but applied by the barème to the part of the assiette ABOVE the PSS only (the 0,72 % on the part <= PSS is carried by taux T1).", tol=1e-6)
add("R4-post-D633-3-I-amount-60000", QI, RB, POST, RB, "AC_60000_2025", "8510",
    f"{D} I+II on assiette 60 000: expected 8 510 €/an (see pre link). AFTER: barème 17,87 % x 47 100 (8 416,77) + 0,72 % x 12 900 (92,88) = 8 509,65 -> 8 510 (aligned, identical to BEFORE).")
add("R4-post-D633-3-II-amount-20000", QII, RB, POST, RB, "AC_20000_2025", "3574",
    f"{D} on assiette 20 000: 3 574 €/an expected; AFTER 17,87 % x 20 000 = 3 574 (aligned, identical to BEFORE).")
add("R4-post-D633-3-I-amount-250000", QI, RB, POST, RB, "AC_250000_2025", "9878",
    f"{D} on assiette 250 000: 9 878 €/an expected; AFTER 8 416,77 + 0,72 % x 202 900 (1 460,88) = 9 877,65 -> 9 878 (aligned, identical to BEFORE).")
add("R4-post-D633-3-I-amount-PSS", QI, RB, POST, RB, "PLNR_47100_2025", "8417",
    f"{D} on assiette exactly = PSS 2025 (47 100, PLNR): 17,15 % + 0,72 % = 17,87 % x 47 100 = 8 416,77 -> 8 417 €/an; AFTER 8 417 (aligned, identical to BEFORE).")
add("R4-post-D633-3-I-amount-tabac", QI, RB, POST, RB, "AC_tabac_60000_2025", "8438",
    f"{D} with the débit de tabac deduction (10 000) on 60 000: assiette 50 000 -> 8 077,65 + 0,72 % x 50 000 (360) = 8 437,65 -> 8 438 €/an; AFTER 8 438 (aligned, identical to BEFORE).")
add("R4-post-D633-3-floor-4000", QII, RB, POST, RB, "AC_4000_2025", "955",
    f"{D} on assiette 4 000 raised to the library's assiette minimale (450 h x SMIC 11,88 = 5 346; floor itself from D633-2, outside the bounded set): 17,87 % x 5 346 = 955,33 -> 955 €/an; AFTER 955 = BEFORE 955 (aligned). NOTE: the derived `revenu cotisé` (R351-9/R634-1, outside the set) drops from 5 569 to 5 344 and `trimestres` from 3 to 2.")
# ---- 2024 (before the reform): governing version not in the snapshot -> no expected value
add("R4-2024-abstain-23000", QI, RB, POST, None, "AC_23000_2024", None,
    f"At 01/07/2024 the library applies 17,75 %/0,60 % (après réforme = non). The D633-3 version in force then (LEGIARTI000041967101, 2020-05-25..2024-07-07) has no text in snapshot S9 (only the current version's text is included), so no expected value can be derived: ABSTAIN. Engine: BEFORE 4 082 (3 944 + 138, two roundings) vs AFTER 4 083 (one rounding of 17,75 % x 23 000 = 4 082,5): a 1 € rounding-path difference; same at 4 000 (930 -> 931) and 6 900 (1 224 -> 1 225). Not assessable against the bounded text.", status='UNKNOWN')
results = []
for s in specs:
    cmd = ['python3', 'src/sophon.py', '--store', STORE, 'link', 'add', '--rule', s['rule'], '--rules-snapshot', s['snap'],
           '--article', 'D633-3', '--law-snapshot', 'S9', '--quote', s['quote'], '--claim', s['claim']]
    if s['check']:
        cmd += ['--check-rule', s['check'], '--check-situation', json.dumps(CASES[s['case']], ensure_ascii=False), '--expect', s['expect'], '--tolerance', str(s['tol'])]
    if s['status']: cmd += ['--status', s['status']]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try: out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception: out = {'raw': p.stdout[-500:], 'err': p.stderr[-500:]}
    rec = {'tag': s['tag'], 'rule': s['rule'], 'snap': s['snap'], 'case': s['case'], 'expect': s['expect'], 'result': out}
    results.append(rec)
    print(s['tag'], '->', out.get('link_id') or out.get('id'), out.get('status'), (out.get('check') or {}).get('value') if isinstance(out.get('check'), dict) else out.get('check'), out.get('error') or out.get('reason') or '')
with open('work/sophon/link_results_R4.jsonl', 'a') as fo:
    for r in results: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
