"""M2 proposal: transposes D131-6-1 v.LEGIARTI000053451315 (S9; Décret n°2026-69 du 6 février 2026 art. 1; nota: créations et reprises à compter du 01/01/2026)
into the indépendant ACRE rate, documents the 60-day request deadline / L. 131-6-5 reservation, and carries over the DROM BNC 2026 fix (D613-4 v.LEGIARTI000052218738 x D756-5).
usage: python3 -I work/scripts/apply_proposal_M2.py <root of the copied règles dir>"""
import sys, os
root = sys.argv[1]
def edit(rel, repls):
    p = os.path.join(root, rel); s = open(p, encoding="utf-8").read()
    for old, new in repls:
        assert s.count(old) == 1, (rel, old[:60], s.count(old)); s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s); print("edited", rel, len(repls), "replacements")
NEW_V = "LEGIARTI000053451315"; OLD_V = "LEGIARTI000036475110"
# 1. indépendant ACRE rate: quarter of the contributions for créations/reprises from 2026-01-01 (D131-6-1 II, v8.0), unchanged before
edit("dirigeant/exonérations.publicodes", [(
"""dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux:
  taux progressif:
    assiette: assiette des cotisations
    multiplicateur: PSS proratisé
    tranches:
      - taux: 100%
        plafond: 75%
      - taux: 0%
        plafond: 100%
""",
"""dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux:
  variations:
    - si: entreprise . date de création >= 01/01/2026
      alors:
        taux progressif:
          assiette: assiette des cotisations
          multiplicateur: PSS proratisé
          tranches:
            - taux: 25%
              plafond: 75%
            - taux: 0%
              plafond: 100%
    - sinon:
        taux progressif:
          assiette: assiette des cotisations
          multiplicateur: PSS proratisé
          tranches:
            - taux: 100%
              plafond: 75%
            - taux: 0%
              plafond: 100%
  note: |
    D131-6-1 II (version LEGIARTI000053451315, en vigueur au 1er janvier 2026, décret n° 2026-69 du 6 février 2026,
    art. 1 ; nota : s'applique aux créations et reprises d'entreprise intervenant à compter du 1er janvier 2026) :
    « l'exonération [...] correspond au quart du montant total des cotisations » jusqu'à 3/4 du PSS, puis
    « Montant de l'exonération = 0,25 E/0,25 PSS×(PSS−R) » (soit 25 % décroissant linéairement jusqu'à 0 au PSS).
    Pour les créations antérieures au 1er janvier 2026 l'ancienne rédaction (LEGIARTI000036475110 : exonération
    totale jusqu'à 3/4 du PSS, puis E/0,25 PSS × (PSS-R)) reste appliquée.
    Limite connue (préexistante) : le taux est appliqué aux cotisations dues au revenu R alors que le texte
    l'applique à E, cotisations dues pour un revenu égal à 3/4 du PSS.
  références:
    Article D131-6-1 du code de la sécurité sociale (créations à compter du 01/01/2026): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053451315
    Article D131-6-1 du code de la sécurité sociale (créations avant le 01/01/2026): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000036475110/2018-01-01
"""),
("""    'L’Acre pour les indépendants: quel avantages ?': https://www.urssaf.fr/portail/home/independant/je-beneficie-dexonerations/accre/quels-avantages/travailleurs-independants-ne-rel.html
""",
"""    'L’Acre pour les indépendants: quel avantages ?': https://www.urssaf.fr/portail/home/independant/je-beneficie-dexonerations/accre/quels-avantages/travailleurs-independants-ne-rel.html
    Article D131-6-1 du code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053451315
""")])
# 2. ACRE applicability rule: documentation only (12 months unchanged; new 60-day request deadline and L. 131-6-5 reservation not modelled)
edit("dirigeant/exonérations/ACRE.publicodes", [("\n  références:\n",
"""
    - Décret n° 2026-69 du 6 février 2026 (D131-6-1 version LEGIARTI000053451315, créations et reprises à
    compter du 1er janvier 2026) : la durée reste de douze mois (I) ; l'exonération des indépendants hors
    micro-social est ramenée au quart des cotisations (II, voir la règle
    `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux`), « sans préjudice des
    dispositions de l'article L. 131-6-5 » (texte non disponible ici) ; la demande mentionnée au II de
    l'article L. 131-6-4 « est introduite au plus tard le soixantième jour qui suit la date d'ouverture de
    l'activité » (IV) — ce délai n'est pas modélisé. Le taux micro-social de l'Acre relève d'un autre article.

  références:
"""), ("exoneration-acre-createur.html\n", "exoneration-acre-createur.html\n    Article D131-6-1 du code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053451315\n")])
# 3. DROM BNC 2026 fractions (pre-existing misalignment, D613-4 v.LEGIARTI000052218738 e) 25,6 % x D756-5 1/6, 1/2, 2/3 rounded up to 0,1)
edit("dirigeant/auto-entrepreneur/exonérations.publicodes", [
("""              - si: date >= 01/2026
                alors: 4.4%
""", """              - si: date >= 01/2026
                alors: 4.3%
"""),
("""              - si: date >= 01/2026
                alors: 13.1%
""", """              - si: date >= 01/2026
                alors: 12.8%
"""),
("""              - si: date >= 01/2026
                alors: 17.4%
""", """              - si: date >= 01/2026
                alors: 17.1%
""")])
print("done")
