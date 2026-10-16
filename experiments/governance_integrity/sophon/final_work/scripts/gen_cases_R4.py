#!/usr/bin/env python3
"""R4 cases: indépendant retraite de base (D633-3) on the modele-ti/modele-commun trees.
usage: python3 -I work/scripts/gen_cases_R4.py > work/evals/cases_R4.json
The assiette is set directly (`indépendant . cotisations et contributions . assiette sociale`): going through
`indépendant . revenu professionnel` is circular in modele-ti (garbage 99 M values)."""
import json
BASE = {"entreprise . imposition": "'IR'", "entreprise . date de création": "01/01/2020",
        "établissement . commune . département . outre-mer": "non", "situation personnelle . RSA": "non",
        "situation personnelle . domiciliation fiscale à l'étranger": "non", "entreprise . activité . saisonnière": "non",
        "indépendant . conjoint collaborateur": "non",
        "indépendant . cotisations et contributions . cotisations . exonérations . pension invalidité": "non"}
ACT = {"AC": {"entreprise . activité": "'commerciale'", "entreprise . activité . commerciale . débit de tabac": "non"},
       "PLNR": {"entreprise . activité": "'libérale'", "entreprise . activité . libérale . réglementée": "non"},
       "CNAVPL": {"entreprise . activité": "'libérale'", "entreprise . activité . libérale . réglementée": "oui",
                  "indépendant . profession libérale . réglementée . métier": "'expert-comptable'",
                  "indépendant . profession libérale . CNAVPL . exonération incapacité": "non"}}
P = "indépendant . cotisations et contributions . cotisations . retraite de base"
COMMON = [P, "protection sociale . retraite . base . revenu cotisé", "protection sociale . retraite . base . trimestres",
          "indépendant . cotisations et contributions . cotisations", "protection sociale . retraite . base", "indépendant . PSS proratisé"]
BEFORE = [P + " . tranche 1", P + " . tranche 2", P + " . tranche 1 . taux", P + " . tranche 2 . taux"]
AFTER = [P + " . taux T1", P + " . taux T2", P + " . assiette", "protection sociale . retraite . base . revenu cotisé . taux de cotisation"]
CN_AFTER = ["indépendant . profession libérale . CNAVPL . retraite de base", "indépendant . profession libérale . CNAVPL . retraite de base . tranche 1",
            "indépendant . profession libérale . CNAVPL . retraite de base . tranche 2"]
cases = []
def add(cid, act, date, assiette, extra=None):
    sit = dict(BASE); sit.update(ACT[act]); sit["date"] = date
    sit["indépendant . cotisations et contributions . assiette sociale"] = f"{assiette} €/an"
    if extra: sit.update(extra)
    rules = list(COMMON) + (["protection sociale . retraite . base . CNAVPL . points acquis"] if act == "CNAVPL" else [])
    cases.append({"id": cid, "situation": sit, "rules": rules, "rules_before": BEFORE, "rules_after": AFTER + (CN_AFTER if act == "CNAVPL" else [])})
for act in ("AC", "PLNR", "CNAVPL"):
    for yr, date in (("2024", "01/07/2024"), ("2025", "01/07/2025")):
        for a in (4000, 6900, 20000, 23000, 47100, 60000, 120000, 250000):
            add(f"{act}_{a}_{yr}", act, date, a)
add("AC_60000_2026", "AC", "01/07/2026", 60000)
add("AC_tabac_60000_2025", "AC", "01/07/2025", 60000, {"entreprise . activité . commerciale . débit de tabac": "oui",
    "indépendant . cotisations et contributions . déduction tabac": "10000 €/an"})
print(json.dumps(cases, ensure_ascii=False, indent=0))
