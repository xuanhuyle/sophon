#!/usr/bin/env python3
"""R1 links: same D613-4 checks on the BEFORE (G1pre_R1) and AFTER (G1) rule snapshots, law S3.
usage: python3 -I work/scripts/add_links_R1.py   (from the staging dir). Appends results to work/sophon/link_results_R1.jsonl.
Quotes are extracted by regex from the real S3 text so they are exact substrings."""
import json, re, subprocess, sys
STORE = 'work/sophon/store'
raw = json.load(open('inputs/law/S3_legi-data-2.381.0/articles.json'))
A = raw.get('articles', raw) if isinstance(raw, dict) else raw
def recs(A):   # staging format: {"articles": {"D613-4": [ {record}, ... ], ...}} (or dict / list variants)
    if isinstance(A, list):
        for r in A: yield r
        return
    for k, v in A.items():
        for r in (v if isinstance(v, list) else [v]):
            if isinstance(r, dict): yield dict(r, num=r.get('num', k))
arts = {}
for a in recs(A):
    if a.get('text'): arts.setdefault(a['num'], a)   # first record carrying text
print('loaded articles with text:', sorted(arts), file=sys.stderr)
t = arts['D613-4']['text']
def q(pattern):
    m = re.search(pattern, t); assert m, pattern; return m.group(0)
Q_BIC = q(r'46\s300 euros 50\s% 23\s150 euros 21,2\s%')
Q_BNC = q(r'10\s000 euros 34\s% 6\s600 euros 23,1\s%')
AE = {"date":"01/07/2024","salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur . chiffre d'affaires":"1000 €/mois","entreprise . date de création":"01/01/2021","dirigeant . exonérations . ACRE":"non","établissement . commune . département . outre-mer":"non"}
BNC = dict(AE, **{"entreprise . activité . nature":"'libérale'"})
BIC = dict(AE, **{"entreprise . activité . nature":"'artisanale'","entreprise . activités . service ou vente":"'service'"})
R = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux "
specs = []
for snap in ("G1pre_R1", "G1"):
    specs.append(dict(tag=f"R1-{snap}-BIC", rule=R+"service BIC", snap=snap, quote=Q_BIC, expect="21.2", sit=BIC,
        claim=f"D613-4 v.LEGIARTI000049624068 (in force 2024-07-01) d) BIC services: global rate 21,2 % -- library {snap} computes 21.2 at 01/07/2024 (aligned; identical before/after commit 2a0e452617fc)"))
    specs.append(dict(tag=f"R1-{snap}-BNC", rule=R+"service BNC", snap=snap, quote=Q_BNC, expect="23.1", sit=BNC,
        claim=f"D613-4 v.LEGIARTI000049624068 (in force 2024-07-01) e) BNC: global rate 23,1 % -- library {snap} still computes 21.1 at 01/07/2024 (PRE-EXISTING gap, not touched by commit 2a0e452617fc; expected FAILED)"))
out = open('work/sophon/link_results_R1.jsonl', 'a')
for s in specs:
    cmd = ['python3', 'src/sophon.py', '--store', STORE, 'link', 'add', '--rule', s['rule'], '--rules-snapshot', s['snap'],
           '--article', 'D613-4', '--law-snapshot', 'S3', '--quote', s['quote'], '--claim', s['claim'],
           '--check-rule', s['rule'], '--check-situation', json.dumps(s['sit'], ensure_ascii=False), '--expect', s['expect'], '--tolerance', '0.001']
    p = subprocess.run(cmd, capture_output=True, text=True)
    rec = {'tag': s['tag'], 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()[-300:], 'rc': p.returncode}
    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
    try:
        j = json.loads(p.stdout.strip().splitlines()[-1]); print(s['tag'], '->', {k: j.get(k) for k in ('ok','id','status','observed','expected','error') if k in j})
    except Exception:
        print(s['tag'], 'RAW:', p.stdout.strip()[:400], p.stderr.strip()[-300:])
