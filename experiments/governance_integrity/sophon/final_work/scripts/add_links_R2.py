#!/usr/bin/env python3
"""R2 links: law S4 (legi-data 2.384.0); rules G1 (= BEFORE commit 1932d654cf7a) and G1post_R2 (= AFTER, G1 + forward patch).
usage: python3 -I work/scripts/add_links_R2.py   (from the staging dir). Appends results to work/sophon/link_results_R2.jsonl.
Quotes are extracted by regex from the real S4 text so they are exact substrings (apostrophes / NBSP tolerant)."""
import json, re, subprocess, sys
STORE = 'work/sophon/store'
raw = json.load(open('inputs/law/S4_legi-data-2.384.0/articles.json'))['articles']
arts = {k: v[0] for k, v in raw.items()}
def flex(s):  # literal sentence -> pattern tolerant to apostrophe variants and NBSP
    out = []
    for ch in s:
        if ch == ' ': out.append(r'\s')
        elif ch == "'": out.append(r"['’]")
        else: out.append(re.escape(ch))
    return ''.join(out)
def q(num, pattern):
    t = arts[num]['text']; m = re.search(pattern, t); assert m, (num, pattern); return m.group(0)
Q_L6137 = q('L613-7', flex("Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale"))
Q_12M = q('D131-6-1', flex("est de douze mois à compter soit de la date d'effet d'affiliation de l'assuré"))
Q_BNC = q('D613-4', r'10\s000 euros 34\s% 6\s600 euros 23,1\s%')
Q_CIPAV = q('D613-4', r'35\s076 euros 34\s% 23\s150 euros 23,2\s%')
Q_BIC = q('D613-4', r'46\s300 euros 50\s% 23\s150 euros 21,2\s%')
V = {k: arts[k]['id'] for k in ('L613-7', 'D131-6-1', 'D613-4')}
print('versions', V, file=sys.stderr)

AE = {"date": "01/09/2024", "salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui",
      "dirigeant . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois", "établissement . commune . département . outre-mer": "non"}
BNC = {"entreprise . activité . nature": "'libérale'"}
ACRE_180 = dict(AE, **BNC, **{"dirigeant . exonérations . ACRE": "oui", "entreprise . date de création": "01/03/2024", "entreprise . durée d'activité": "180 jour"})
ACRE_500 = dict(AE, **BNC, **{"dirigeant . exonérations . ACRE": "oui", "entreprise . date de création": "01/03/2023", "entreprise . durée d'activité": "500 jour"})
NOACRE_BNC = dict(AE, **BNC, **{"dirigeant . exonérations . ACRE": "non", "entreprise . date de création": "01/01/2021"})
NOACRE_CIPAV = dict(NOACRE_BNC, **{"entreprise . activité . nature . libérale . réglementée": "oui", "entreprise . date de création": "01/01/2019"})
NOACRE_BIC = dict(AE, **{"dirigeant . exonérations . ACRE": "non", "entreprise . date de création": "01/01/2021", "entreprise . activité . nature": "'artisanale'", "entreprise . activités . service ou vente": "'service'"})
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . "
TA = C + "taux ACRE"
specs = []
for snap in ("G1", "G1post_R2"):
    specs.append(dict(tag=f"R2-{snap}-L613-7-tauxACRE", art='L613-7', quote=Q_L6137, rule=TA, snap=snap, check=TA, sit=ACRE_180, expect="50",
        claim=(f"L613-7 v.{V['L613-7']} I delegates to a DECREE a different global rate for ACRE-eligible micro-entrepreneurs; that decree article is NOT in the bounded set. "
               f"The library rule 'taux ACRE' (50 % of the normal rate during the first year for AE created >= 01/04/2020; sources cited by the rule: URSSAF FAQ, service-public.fr, outside the set) "
               f"is checked here as the ENGINE value only (50 at 180 days, ACRE oui): the number 50 is not in the bounded text. On G1 the rule is 'privé: oui' and not evaluable (expected FAILED); commit 1932d654cf7a removes 'privé: oui' (G1post_R2: expected VERIFIED).")))
specs.append(dict(tag="R2-G1post_R2-D131-6-1-dans-les-12-mois", art='D131-6-1', quote=Q_12M, rule=TA, snap="G1post_R2", check=C + "taux service BNC", sit=ACRE_180, expect="10.6",
    claim=(f"D131-6-1 v.{V['D131-6-1']} I: exemption lasts twelve months. Library: within 12 months (180 days, AE created 01/03/2024, ACRE oui) the BNC rate is reduced: taux ACRE 50 % x 21.1 = 10.55 -> arrondi 1 décimale 10.6. "
           "Only the DURATION logic is supported by the bounded text; the 50 % factor rests outside the set and the 21.1 base is the pre-existing D613-4 gap (23,1 % in force).")))
specs.append(dict(tag="R2-G1post_R2-D131-6-1-apres-12-mois", art='D131-6-1', quote=Q_12M, rule=TA, snap="G1post_R2", check=C + "taux service BNC", sit=ACRE_500, expect="21.1",
    claim=(f"D131-6-1 v.{V['D131-6-1']} I: after twelve months no exemption. Library: at 500 days (AE created 01/03/2023, ACRE oui) taux ACRE is non applicable and the unreduced library rate applies (21.1). "
           "The check verifies only that the reduction STOPS after 12 months; the value 21.1 itself is the pre-existing misalignment with D613-4 v.LEGIARTI000049624068 (23,1 %).")))
specs.append(dict(tag="R2-G1post_R2-D613-4-BNC", art='D613-4', quote=Q_BNC, rule=C + "taux service BNC", snap="G1post_R2", check=C + "taux service BNC", sit=NOACRE_BNC, expect="23.1",
    claim=f"D613-4 v.{V['D613-4']} (in force 2024-07-01..2025-05-01) e) BNC: global rate 23,1 % -- library AFTER commit 1932d654cf7a still computes 21.1 at 01/09/2024 (PRE-EXISTING gap, identical before/after; expected FAILED)"))
specs.append(dict(tag="R2-G1post_R2-D613-4-CIPAV", art='D613-4', quote=Q_CIPAV, rule=C + "cotisations CIPAV . taux", snap="G1post_R2", check=C + "cotisations CIPAV . taux", sit=NOACRE_CIPAV, expect="23.2",
    claim=f"D613-4 v.{V['D613-4']} b) CIPAV: global rate 23,2 % -- library AFTER commit 1932d654cf7a still computes 21.2 at 01/09/2024 (PRE-EXISTING gap, identical before/after; expected FAILED)"))
specs.append(dict(tag="R2-G1post_R2-D613-4-BIC", art='D613-4', quote=Q_BIC, rule=C + "service BIC . taux", snap="G1post_R2", check=C + "service BIC . taux", sit=NOACRE_BIC, expect="21.2",
    claim=f"D613-4 v.{V['D613-4']} d) BIC services: global rate 21,2 % -- library AFTER commit 1932d654cf7a computes 21.2 at 01/09/2024 (aligned; identical before/after)"))
out = open('work/sophon/link_results_R2.jsonl', 'a')
for s in specs:
    cmd = ['python3', 'src/sophon.py', '--store', STORE, 'link', 'add', '--rule', s['rule'], '--rules-snapshot', s['snap'],
           '--article', s['art'], '--law-snapshot', 'S4', '--quote', s['quote'], '--claim', s['claim'],
           '--check-rule', s['check'], '--check-situation', json.dumps(s['sit'], ensure_ascii=False), '--expect', s['expect'], '--tolerance', '0.001']
    p = subprocess.run(cmd, capture_output=True, text=True)
    rec = {'tag': s['tag'], 'article': s['art'], 'article_id': V[s['art']], 'quote': s['quote'], 'rule': s['rule'], 'snap': s['snap'], 'check_rule': s['check'], 'situation': s['sit'], 'expect': s['expect'],
           'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()[-300:], 'rc': p.returncode}
    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
    try:
        j = json.loads(p.stdout.strip().splitlines()[-1]); cr = j.get('check_result') or {}
        print(s['tag'], '->', j.get('link_id'), j.get('status'), 'observed=', cr.get('observed'), 'expected=', cr.get('expected'), (cr.get('error') or '')[:120], j.get('problems'))
    except Exception:
        print(s['tag'], 'RAW:', p.stdout.strip()[:400], p.stderr.strip()[-300:])
