"""M0 proposal (documentation-only: no numeric change). usage: apply_proposal_M0.py <règles root>"""
import sys, io
root = sys.argv[1].rstrip('/')
def edit(path, old, new):
    s = io.open(path, encoding='utf-8').read()
    assert s.count(old) == 1, (path, old[:60], s.count(old))
    io.open(path, 'w', encoding='utf-8').write(s.replace(old, new))
A = root + '/dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes'
B = root + '/dirigeant/auto-entrepreneur/exonérations.publicodes'
edit(A, "        taux:\n          variations:\n            - si: date >= 01/2026\n              alors: 26.1%\n",
"""        taux:
          références:
            Article D613-4 du Code de la sécurité sociale, version LEGIARTI000049624097 (2025-01-01 au 2026-01-01): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049624097
          note: |
            [M0 2025-10-01, legi-data 2.469.0] La valeur 2025 (24,6 %) correspond au texte en vigueur (catégorie e).
            La branche 'date >= 01/2026' (26,1 %) provient de la version LEGIARTI000049624125 annoncée par le
            décret n°2024-484, désormais MODIFIE_MORT_NE (fin 2025-09-10). La version en vigueur au 01-01-2026 est
            LEGIARTI000052218738, dont le texte n'est pas disponible dans le snapshot : la valeur 26,1 % n'est
            appuyée par aucun texte disponible (abstention) et doit être revue dès publication du texte.
          variations:
            - si: date >= 01/2026
              alors: 26.1%
""")
edit(A, "        répartition:\n          avec:\n            maladie-maternité:\n              valeur: service BNC * taux de répartition\n",
"""        répartition:
          références:
            Article D613-6 du Code de la sécurité sociale, version LEGIARTI000049625405 (2025-01-01 au 2026-01-01): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049625405
          note: |
            [M0 2025-10-01] Parts 2025 (3,40 / 3,50 / 47,60 / 13,00 / 32,50 %) conformes au texte en vigueur (catégorie e).
            Les parts 'date >= 01/2026' proviennent de la version LEGIARTI000049625445, désormais MODIFIE_MORT_NE
            (fin 2025-09-10) ; la version en vigueur au 01-01-2026 est LEGIARTI000052218747, sans texte disponible :
            abstention, à revoir dès publication du texte.
          avec:
            maladie-maternité:
              valeur: service BNC * taux de répartition
""")
edit(A, "            Article D613-6 du Code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000043656780\n",
        "            Article D613-6 du Code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049625405\n")
edit(B, "    taux service BNC:\n      remplace: cotisations et contributions . cotisations . service BNC . taux\n      variations:\n        - si: première période\n",
"""    taux service BNC:
      remplace: cotisations et contributions . cotisations . service BNC . taux
      note: |
        [M0 2025-10-01] Fractions D756-5 (1/6, 1/2, 2/3, arrondi au dixième supérieur) du taux D613-4 catégorie e) :
        2025 = 4,1 / 12,3 / 16,4 % (taux 24,6 %, version LEGIARTI000049624097). Les valeurs 'date >= 01/2026'
        (4,4 / 13,1 / 17,4 %) dérivent du taux 26,1 % de la version MODIFIE_MORT_NE LEGIARTI000049624125 ; la version
        LEGIARTI000052218738 en vigueur au 01-01-2026 n'a pas de texte disponible : abstention, à revoir.
      variations:
        - si: première période
""")
edit(B, "      valeur: taux Acre * cotisations et contributions . cotisations . service BNC . taux\n      arrondi:\n        variations:\n",
"""      valeur: taux Acre * cotisations et contributions . cotisations . service BNC . taux
      note: |
        [M0 2025-10-01] L'arrondi à 2 décimales pour 'date >= 01/2026' suppose le taux 26,1 % (version MODIFIE_MORT_NE
        LEGIARTI000049624125) ; la version LEGIARTI000052218738 en vigueur au 01-01-2026 n'a pas de texte disponible : à revoir.
      arrondi:
        variations:
""")
print("proposal edits applied")
