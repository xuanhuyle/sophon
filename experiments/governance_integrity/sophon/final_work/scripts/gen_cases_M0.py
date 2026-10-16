"""M0 cases: AE rules at G3 for 01/12/2024 (v5, text not in S7), 01/07/2025 (v6 = S7 current text), 01/01/2026 (v8, text not in S7).
usage: python3 -I work/scripts/gen_cases_M0.py <list_names.txt> <out cases.json>"""
import json, sys
names = set(l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8'))
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
P = {"salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui",
     "dirigeant . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois",
     "entreprise . date de création": "01/01/2021", "dirigeant . exonérations . ACRE": "non", "établissement . commune . département . outre-mer": "non"}
ACT = {"BNC": {"entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "non"},
       "CIPAV": {"entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "oui", "entreprise . date de création": "01/01/2019"},
       "BIC": {"entreprise . activité . nature": "'artisanale'", "entreprise . activités . service ou vente": "'service'"},
       "VENTE": {"entreprise . activité . nature": "'commerciale'", "entreprise . activités . service ou vente": "'vente'"}}
X = {"BNC": "service BNC", "CIPAV": "service BNC Cipav", "BIC": "service BIC", "VENTE": "vente restauration hébergement"}
SPLIT = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"]
PER = {"P1": {"entreprise . durée d'activité": "300 jour", "entreprise . durée d'activité . trimestres civils": "4 trimestre civil", "entreprise . durée d'activité . années civiles": "1 année civile"},
       "P2": {"entreprise . durée d'activité": "900 jour", "entreprise . durée d'activité . trimestres civils": "10 trimestre civil", "entreprise . durée d'activité . années civiles": "3 année civile"},
       "P3": {"entreprise . durée d'activité": "1500 jour", "entreprise . durée d'activité . trimestres civils": "20 trimestre civil", "entreprise . durée d'activité . années civiles": "5 année civile"}}
DROMTAUX = {"BNC": "taux service BNC", "CIPAV": "taux CIPAV", "BIC": "taux service BIC", "VENTE": "taux vente restauration hébergement"}
cases = []
for a in ["BNC", "BIC", "VENTE", "CIPAV"]:
    for d in ["01/12/2024", "01/07/2025", "01/01/2026"]:
        sit = dict(P, **ACT[a]); sit["date"] = d
        rules = [f"{C} . {X[a]} . taux", f"{C} . {X[a]}", C, "dirigeant . auto-entrepreneur . cotisations et contributions"] + [f"{C} . {X[a]} . répartition . {s} . taux de répartition" for s in SPLIT]
        cases.append({"id": f"{a}@{d}", "situation": sit, "rules": rules})
for a, per, d in [("BNC", "P1", "01/07/2025"), ("BNC", "P2", "01/07/2025"), ("BNC", "P3", "01/07/2025"), ("BNC", "P1", "01/01/2026"), ("BNC", "P2", "01/01/2026"), ("BNC", "P3", "01/01/2026"),
                  ("CIPAV", "P1", "01/07/2025"), ("CIPAV", "P2", "01/07/2025"), ("CIPAV", "P3", "01/07/2025"), ("BIC", "P1", "01/07/2025"), ("VENTE", "P1", "01/07/2025")]:
    sit = dict(P, **ACT[a]); sit.update(PER[per]); sit["établissement . commune . département . outre-mer"] = "oui"; sit["date"] = d
    cases.append({"id": f"DROM_{a}_{per}@{d}", "situation": sit, "rules": [f"dirigeant . auto-entrepreneur . DROM . {DROMTAUX[a]}", f"{C} . {X[a]}", C]})
for d, cre in [("01/07/2025", "01/03/2025"), ("01/01/2026", "01/09/2025")]:
    sit = dict(P, **ACT["BNC"]); sit.update({"date": d, "dirigeant . exonérations . ACRE": "oui", "entreprise . date de création": cre, "entreprise . durée d'activité": "180 jour"})
    cases.append({"id": f"ACRE_BNC@{d}", "situation": sit, "rules": ["dirigeant . auto-entrepreneur . Acre . taux Acre", "dirigeant . auto-entrepreneur . Acre . taux service BNC", f"{C} . service BNC . taux", f"{C} . service BNC"]})
bad = sorted({k for c in cases for k in c["situation"] if k != "date" and k not in names} | {r for c in cases for r in c["rules"] if r not in names})
print("UNKNOWN KEYS/RULES:", bad)
json.dump(cases, open(sys.argv[2], "w"), ensure_ascii=False, indent=1); print("cases", len(cases))
