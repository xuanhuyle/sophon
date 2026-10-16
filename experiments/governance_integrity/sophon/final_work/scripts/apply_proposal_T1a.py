"""T1a proposal: traceability-only edits (no numeric change). Pins the AE global-rate rules to D613-4 version
LEGIARTI000049623867 (Décret 2024-484, in force 2024-06-01) and the RCI AE rule to D613-6 version LEGIARTI000049623885;
documents the announced future versions whose text is NOT in snapshot S1 (values deliberately not transposed)."""
import sys, io
P = "work/proposals/T1a/modele-social/règles/"
def edit(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:60], s.count(old))
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8").write(s)
REF4 = "Article D613-4 du code de la sécurité sociale (version LEGIARTI000049623867, en vigueur du 01/06/2024 au 01/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049623867/2024-06-01/"
DEC = "Décret n°2024-484 du 30 mai 2024 (JORF du 31/05/2024): https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049620955"
PEND4 = "Versions ultérieures annoncées par le même décret (texte NON disponible dans le snapshot legi-data 2.361.0 du 01/06/2024, taux non transposés, à revoir dès que le texte sera disponible) - LEGIARTI000049624068 (01/07/2024), LEGIARTI000049624097 (01/01/2025), LEGIARTI000049624125 (01/01/2026)."
ae = P + "dirigeant/auto-entrepreneur/auto-entrepreneur.publicodes"
edit(ae, [
 ("""  références:
    Les cotisations et contributions sociales: https://www.autoentrepreneur.urssaf.fr/portail/accueil/sinformer-sur-le-statut/lessentiel-du-statut.html#cout-durant-vie-auto-entreprise
""",
  f"""  note: |
    Taux globaux fixés par l'article D613-4 CSS (tableau du I). Version LEGIARTI000049623867 (Décret n°2024-484 du 30 mai 2024,
    art. 1, en vigueur le 01/06/2024) : a) vente 12,3 % ; b) CIPAV 21,2 % ; c) meublés de tourisme 6 % (non implémenté) ;
    d) service BIC 21,2 % ; e) BNC (102 ter) 21,1 % — identiques à la version précédente LEGIARTI000046714712.
    {PEND4}
  références:
    Les cotisations et contributions sociales: https://www.autoentrepreneur.urssaf.fr/portail/accueil/sinformer-sur-le-statut/lessentiel-du-statut.html#cout-durant-vie-auto-entreprise
    {REF4}
    {DEC}
"""),
 ("""    cotisations CIPAV . taux:  21.2%
""",
  f"""    cotisations CIPAV . taux:
      note: |
        D613-4 I b) « 11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 21,2 % » (version en vigueur au 01/06/2024). {PEND4}
      références:
        {REF4}
      valeur: 21.2%
"""),
 ("""    taux service BIC:
      variations:
        - si: date >= 10/2022
          alors: 21.2%
""",
  f"""    taux service BIC:
      note: |
        D613-4 I d) « 46 300 euros 50 % 23 150 euros 21,2 % » (version en vigueur au 01/06/2024). {PEND4}
      références:
        {REF4}
      variations:
        - si: date >= 10/2022
          alors: 21.2%
"""),
 ("""    taux service BNC:
      variations:
        - si: date >= 10/2022
          alors: 21.1%
""",
  f"""    taux service BNC:
      note: |
        D613-4 I e) « 10 000 euros 34 % 6 600 euros 21,1 % » (version en vigueur au 01/06/2024). {PEND4}
      références:
        {REF4}
      variations:
        - si: date >= 10/2022
          alors: 21.1%
"""),
 ("""    taux vente restauration hébergement:
      variations:
        - si: date >= 10/2022
          alors: 12.3%
""",
  f"""    taux vente restauration hébergement:
      note: |
        D613-4 I a) « 79 828 euros 71 % 23 150 euros 12,3 % » (version en vigueur au 01/06/2024). {PEND4}
      références:
        {REF4}
      variations:
        - si: date >= 10/2022
          alors: 12.3%
"""),
])
ps = P + "protection-sociale.publicodes"
edit(ps, [
 ("""        Article D613-6 du code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046714699/2022-12-10/""",
  """        Article D613-6 du code de la sécurité sociale (version LEGIARTI000049623885, en vigueur du 01/06/2024 au 01/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049623885/2024-06-01/
        Décret n°2024-484 du 30 mai 2024 (JORF du 31/05/2024): https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049620955"""),
 ("""    revenu cotisé auto-entrepreneur:
      applicable si: dirigeant . auto-entrepreneur
""",
  """    revenu cotisé auto-entrepreneur:
      applicable si: dirigeant . auto-entrepreneur
      note: |
        Répartition D613-6 CSS, version LEGIARTI000049623885 (Décret n°2024-484 du 30 mai 2024, art. 2, en vigueur le 01/06/2024),
        texte identique à la version précédente LEGIARTI000046714699 : a) et d) « Cotisation d'assurance vieillesse complémentaire 16,50 % »
        (12,3 % × 16,5 % ≈ 2,03 % ; 21,2 % × 16,5 % ≈ 3,50 %) ; e) pas de part retraite complémentaire (0 %).
        Versions ultérieures annoncées (texte NON disponible dans le snapshot legi-data 2.361.0 du 01/06/2024, non transposées) :
        LEGIARTI000049625264 (01/07/2024), LEGIARTI000049625405 (01/01/2025), LEGIARTI000049625445 (01/01/2026).
"""),
])
print("edits applied")
