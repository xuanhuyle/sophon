"""M2 cases: indépendant ACRE (D131-6-1 v.LEGIARTI000053451315, S9: quarter exoneration for créations/reprises from 2026-01-01; v.LEGIARTI000036475110 before).
usage: python3 -I work/scripts/gen_cases_M2.py <list_names.txt> <out cases.json>
PSS 2026 in the library = 48 060 €/an -> 3/4 = 36 045 ; 87,5 % = 42 052,5."""
import json, sys
names = set(l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8'))
IND = "dirigeant . indépendant . cotisations et contributions"; EX = IND + " . exonérations . ACRE"
RULES = ["dirigeant . exonérations . ACRE", EX, EX + " . taux", EX + " . prorata sur l'année", EX + " . maladie", EX + " . retraite de base", EX + " . invalidité et décès",
         EX + " . allocations familiales", EX + " . indemnités journalières maladie", IND + " . maladie", IND + " . retraite de base", IND + " . invalidité et décès",
         IND + " . allocations familiales", IND + " . indemnités journalières maladie", IND + " . retraite complémentaire", IND + " . CSG-CRDS", IND + " . cotisations", IND,
         "dirigeant . indépendant . assiette des cotisations", "dirigeant . indépendant . PSS proratisé", "plafond sécurité sociale"]
BASE = {"salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "non", "entreprise . imposition": "'IR'",
        "établissement . commune . département . outre-mer": "non", "dirigeant . exonérations . ACRE": "oui"}
AC = {"entreprise . activité . nature": "'commerciale'"}
PLNR = {"entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "non"}
cases = []
def add(cid, cre, date, R, act=AC, acre="oui"):
    sit = dict(BASE, **act); sit.update({"entreprise . date de création": cre, "date": date, "dirigeant . indépendant . revenu professionnel": f"{R} €/an", "dirigeant . exonérations . ACRE": acre})
    cases.append({"id": cid, "situation": sit, "rules": RULES})
# créations 2026 (new text) at several income levels, date 01/07/2026
for R in (20000, 36045, 42052.5, 60000): add(f"AC_cre2026_R{R}@01/07/2026", "01/01/2026", "01/07/2026", R)
add("PLNR_cre2026_R20000@01/07/2026", "01/01/2026", "01/07/2026", 20000, PLNR)
# création 2025 still in its 12 months in 2026 (old text per nota: créations before 2026-01-01)
for R in (20000, 42052.5): add(f"AC_cre072025_R{R}@01/07/2026", "01/07/2025", "01/07/2026", R)
# 2025 control (old text, 2025 PSS)
add("AC_cre2025_R20000@01/07/2025", "01/01/2025", "01/07/2025", 20000)
add("AC_cre2025_R41212@01/07/2025", "01/01/2025", "01/07/2025", 41212.5)
# no-ACRE control 2026
add("AC_cre2026_R20000_noACRE@01/07/2026", "01/01/2026", "01/07/2026", 20000, acre="non")
bad = sorted({k for c in cases for k in c["situation"] if k != "date" and k not in names} | {r for c in cases for r in c["rules"] if r not in names})
print("UNKNOWN KEYS/RULES:", bad)
json.dump(cases, open(sys.argv[2], "w"), ensure_ascii=False, indent=1); print("cases", len(cases))
