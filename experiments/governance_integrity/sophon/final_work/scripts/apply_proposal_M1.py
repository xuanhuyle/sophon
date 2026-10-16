"""M1 proposal: transpose D613-4 v.LEGIARTI000052218738 and D613-6 v.LEGIARTI000052218747 (Décret n°2025-943 du 8 septembre 2025,
in force 2026-01-01, S8 = legi-data 2.489.0) into the G3 auto-entrepreneur rules; fix DROM CIPAV fractions for date >= 01/2025.
usage: apply_proposal_M1.py <règles root> (a fresh copy of the G3 tree)"""
import sys, io
root = sys.argv[1].rstrip('/')
def edit(path, old, new):
    s = io.open(path, encoding='utf-8').read()
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding='utf-8').write(s.replace(old, new))
A = root + '/dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes'
B = root + '/dirigeant/auto-entrepreneur/exonérations.publicodes'
REF4 = ("          références:\n"
        "            Article D613-4 du Code de la sécurité sociale, version LEGIARTI000052218738 (en vigueur au 01-01-2026): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000052218738\n"
        "            Article D613-4 du Code de la sécurité sociale, version LEGIARTI000049624097 (2025): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049624097\n")
REF6 = ("          références:\n"
        "            Article D613-6 du Code de la sécurité sociale, version LEGIARTI000052218747 (en vigueur au 01-01-2026): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000052218747\n"
        "            Article D613-6 du Code de la sécurité sociale, version LEGIARTI000049625405 (2025): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049625405\n")
SRC = "décret n°2025-943 du 8 septembre 2025, art. 1 (JORF 2025-09-09), applicable aux périodes courant à compter du 1er janvier 2026"
# ---- D613-4 rates
edit(A, "        taux:\n          variations:\n            - si: date >= 01/2026\n              alors: 26.1%\n",
     "        taux:\n" + REF4 + "          note: |\n"
     f"            [M1 2026-01-01, legi-data 2.489.0] Taux 2026 = 25,6 % (catégorie e, version LEGIARTI000052218738, {SRC}).\n"
     "            Remplace la valeur 26,1 % qui provenait de la version MODIFIE_MORT_NE LEGIARTI000049624125 (décret n°2024-484).\n"
     "            Taux 2025 = 24,6 % (version LEGIARTI000049624097).\n"
     "          variations:\n            - si: date >= 01/2026\n              alors: 25.6%\n")
edit(A, "        taux:\n          variations:\n            - si: date >= 10/2022\n              alors: 21.2%\n",
     "        taux:\n" + REF4 + "          note: |\n"
     f"            [M1 2026-01-01] Taux inchangé en 2026 = 21,2 % (catégorie d, version LEGIARTI000052218738, {SRC}).\n"
     "          variations:\n            - si: date >= 10/2022\n              alors: 21.2%\n")
edit(A, "        taux:\n          variations:\n            - si: date >= 10/2022\n              alors: 12.3%\n",
     "        taux:\n" + REF4 + "          note: |\n"
     f"            [M1 2026-01-01] Taux inchangé en 2026 = 12,3 % (catégorie a, version LEGIARTI000052218738, {SRC}).\n"
     "          variations:\n            - si: date >= 10/2022\n              alors: 12.3%\n")
edit(A, "        taux:\n          variations:\n            - si: date >= 07/2024\n              alors: 23.2%\n",
     "        taux:\n" + REF4 + "          note: |\n"
     f"            [M1 2026-01-01] Taux inchangé en 2026 = 23,2 % (catégorie b, version LEGIARTI000052218738, {SRC}).\n"
     "          variations:\n            - si: date >= 07/2024\n              alors: 23.2%\n")
# ---- D613-6 shares: BNC (e)
edit(A, "        répartition:\n          avec:\n            maladie-maternité:\n              valeur: service BNC * taux de répartition\n",
     "        répartition:\n" + REF6 + "          note: |\n"
     f"            [M1 2026-01-01] Parts 2026 (catégorie e, version LEGIARTI000052218747, {SRC}) :\n"
     "            maladie-maternité 4,10 % = 2,60 % (L. 621-1) + 1,50 % (prestations en espèces L. 621-2) agrégés dans une seule règle ;\n"
     "            invalidité-décès 3,30 % ; vieillesse de base 46,40 % ; vieillesse complémentaire 21,00 % ; CSG-CRDS 25,20 %.\n"
     "            Remplacent les parts 3 / 3,25 / 44,85 / 17,7 / 31,20 % issues de la version MODIFIE_MORT_NE LEGIARTI000049625445.\n"
     "          avec:\n            maladie-maternité:\n              valeur: service BNC * taux de répartition\n")
for old, new in [("3%", "4.10%"), ("3.25%", "3.30%"), ("44.85%", "46.40%"), ("17.7%", "21.00%"), ("31.20%", "25.20%")]:
    edit(A, f"                    - si: date >= 01/2026\n                      alors: {old}\n", f"                    - si: date >= 01/2026\n                      alors: {new}\n")
# ---- D613-6 shares: BIC and vente (a and d): new 2026 branch
for cat in ["service BIC", "vente restauration hébergement"]:
    edit(A, f"        répartition:\n          avec:\n            maladie-maternité:\n              valeur: {cat} * taux de répartition\n",
         "        répartition:\n" + REF6 + "          note: |\n"
         f"            [M1 2026-01-01] Parts 2026 (catégories a et d, version LEGIARTI000052218747, {SRC}) :\n"
         "            maladie-maternité 10,05 % = 8,80 % (L. 621-1) + 1,25 % (prestations en espèces L. 621-2) agrégés ;\n"
         "            invalidité-décès 3,15 % ; vieillesse de base 43,45 % ; vieillesse complémentaire 19,75 % ; CSG-CRDS 23,60 %.\n"
         "            Parts antérieures (version LEGIARTI000049625405) : 8,90 / 3,10 / 41,80 / 16,50 / 29,70 %.\n"
         f"          avec:\n            maladie-maternité:\n              valeur: {cat} * taux de répartition\n")
    for old, new in [("8.90%", "10.05%"), ("3.10%", "3.15%"), ("41.80%", "43.45%"), ("16.50%", "19.75%"), ("29.70%", "23.60%")]:
        edit(A, f"              valeur: {cat} * taux de répartition\n              avec:\n                taux de répartition: {old}\n",
             f"              valeur: {cat} * taux de répartition\n              avec:\n                taux de répartition:\n                  variations:\n"
             f"                    - si: date >= 01/2026\n                      alors: {new}\n                    - sinon: {old}\n")
# ---- D613-6 shares: Cipav (b): new 2026 branch
edit(A, "        répartition:\n          références:\n            Article D613-6 du Code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000043656780\n",
     "        répartition:\n" + REF6 + "          note: |\n"
     f"            [M1 2026-01-01] Parts 2026 (catégorie b, version LEGIARTI000052218747, {SRC}) :\n"
     "            maladie-maternité 11,40 % = 10,60 % (L. 621-1) + 0,80 % (L. 621-2) ; invalidité-décès 1,40 % (inchangé) ;\n"
     "            vieillesse de base 29,50 % = 24,30 % (1° D. 642-3) + 5,20 % (2° D. 642-3) ; complémentaire 30,70 % ; CSG-CRDS 27,00 %.\n")
for old, new in [("10.20%", "11.40%"), ("28.8%", "29.50%"), ("25.60%", "30.70%"), ("34.00%", "27.00%")]:
    edit(A, f"                    - si: date >= 07/2024\n                      alors: {old}\n",
         f"                    - si: date >= 01/2026\n                      alors: {new}\n                    - si: date >= 07/2024\n                      alors: {old}\n")
# ---- DROM (D756-5 fractions of the D613-4 rates)
edit(B, "    taux service BNC:\n      remplace: cotisations et contributions . cotisations . service BNC . taux\n      variations:\n        - si: première période\n",
     "    taux service BNC:\n      remplace: cotisations et contributions . cotisations . service BNC . taux\n      note: |\n"
     "        [M1 2026-01-01] Fractions D756-5 (1/6, 1/2, 2/3, arrondi au dixième supérieur) du taux D613-4 catégorie e) :\n"
     "        2026 = 4,3 / 12,8 / 17,1 % (taux 25,6 %, version LEGIARTI000052218738) ; 2025 = 4,1 / 12,3 / 16,4 % (taux 24,6 %).\n"
     "        Remplace 4,4 / 13,1 / 17,4 % (fractions du 26,1 % de la version MODIFIE_MORT_NE LEGIARTI000049624125).\n"
     "      variations:\n        - si: première période\n")
for old, new in [("4.4%", "4.3%"), ("13.1%", "12.8%"), ("17.4%", "17.1%")]:
    edit(B, f"              - si: date >= 01/2026\n                alors: {old}\n", f"              - si: date >= 01/2026\n                alors: {new}\n")
edit(B, "    taux CIPAV:\n      remplace: cotisations et contributions . cotisations . service BNC Cipav . taux\n      variations:\n        - si: première période\n          alors: 7.10%\n        - si: seconde période\n          alors: 10.60%\n        - sinon: 14.20%\n",
     "    taux CIPAV:\n      remplace: cotisations et contributions . cotisations . service BNC Cipav . taux\n      note: |\n"
     "        [M1 2026-01-01] Fractions D756-5 (1/3, 1/2, 2/3, arrondi au dixième supérieur) du taux D613-4 catégorie b) = 23,2 %\n"
     "        (version LEGIARTI000049624097 pour 2025, LEGIARTI000052218738 pour 2026) : 7,8 / 11,6 / 15,5 %.\n"
     "        Les anciennes valeurs 7,1 / 10,6 / 14,2 % (fractions de 21,2 %) sont conservées avant 01/2025 : le texte de la version\n"
     "        2024-07-01 (LEGIARTI000049624068) n'est pas disponible dans les snapshots de cette tâche (abstention).\n"
     "      variations:\n"
     "        - si: première période\n          alors:\n            variations:\n              - si: date >= 01/2025\n                alors: 7.8%\n              - sinon: 7.10%\n"
     "        - si: seconde période\n          alors:\n            variations:\n              - si: date >= 01/2025\n                alors: 11.6%\n              - sinon: 10.60%\n"
     "        - sinon:\n            variations:\n              - si: date >= 01/2025\n                alors: 15.5%\n              - sinon: 14.20%\n")
edit(B, "      valeur: taux Acre * cotisations et contributions . cotisations . service BNC . taux\n      arrondi:\n        variations:\n",
     "      valeur: taux Acre * cotisations et contributions . cotisations . service BNC . taux\n      note: |\n"
     "        [M1 2026-01-01] L'arrondi à 2 décimales pour 'date >= 01/2026' avait été prévu pour 50 % x 26,1 % = 13,05 % (version\n"
     "        MODIFIE_MORT_NE) ; avec le taux 2026 en vigueur 25,6 % (LEGIARTI000052218738) il donne 12,80 % = 12,8 % : sans effet, conservé.\n"
     "      arrondi:\n        variations:\n")
print("M1 proposal edits applied")
