"""T1b proposal (law S3 legi-data 2.381.0 x rules G1 2a0e452617fc). Transposes ONLY what the S3 texts settle
deterministically: unified base with 26 % flat abattement (L131-6 I / L136-3 III, LEGIARTI000048683707 / LEGIARTI000048683641),
floor 1,76 % and ceiling 130 % of the annual PSS (D136-5 LEGIARTI000049899286, in force 2024-07-07), maladie reduced-rate
formula T1..T5 (D621-2 LEGIARTI000049904592, 2024-07-07), retraite de base 17,15 % within PSS + 0,72 % on the total
(D633-3 LEGIARTI000049904636, 2024-07-07). Everything left open by the texts is a flagged PLACEHOLDER (see notes in the YAML).
usage: python3 work/scripts/apply_proposal_T1b.py   (after copying the G1 tree to work/proposals/T1b/modele-social/règles)"""
import io
P = "work/proposals/T1b/modele-social/règles/"
def edit(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(path, "w", encoding="utf-8").write(s)
f = P + "dirigeant/indépendant.publicodes"
DATE = "date >= 07/07/2024"
edit(f, [
# ---- E1: unified base with flat abattement (L131-6 I, L136-3 III, D136-5) ----
("""dirigeant . indépendant . assiette des cotisations:
  unité: €/an
  description: Il s'agit de l'assiette des cotisations sociales, nombre forcément positif
  valeur: sans plancher
  plancher: 0

  avec:
    sans plancher:
      somme:
        - revenu professionnel
        - cotisations facultatives . déductibles
""",
"""dirigeant . indépendant . assiette des cotisations:
  unité: €/an
  description: Il s'agit de l'assiette des cotisations sociales, nombre forcément positif
  valeur:
    variations:
      - si: réforme assiette 2024
        alors: réforme assiette 2024 . assiette unifiée
      - sinon: sans plancher
  plancher: 0
  note: |
    PROPOSITION T1b (2024-07-17). Depuis la version LEGIARTI000048683707 de l'article L131-6 (en vigueur le 28/12/2023),
    les cotisations des travailleurs indépendants « sont assises sur l'assiette définie à l'article L. 136-3 » ; cette
    assiette (L136-3 III, LEGIARTI000048683641) « fait l'objet d'un abattement de 26 % » encadré par un plancher et un
    plafond fixés par décret. Le décret n°2024-688 du 5 juillet 2024 (D136-5, LEGIARTI000049899286, en vigueur le
    07/07/2024) fixe le plancher à 1,76 % et le plafond à 130 % du plafond annuel de la sécurité sociale. La date
    d'application retenue ici est la date d'entrée en vigueur du décret telle qu'elle figure dans les données consolidées
    (07/07/2024) ; la date d'application aux cotisations d'une année donnée n'est pas énoncée dans les textes disponibles.
  références:
    Article L131-6 du code de la sécurité sociale (version LEGIARTI000048683707): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048683707/
    Article L136-3 du code de la sécurité sociale (version LEGIARTI000048683641): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000048683641/
    Article D136-5 du code de la sécurité sociale (version LEGIARTI000049899286): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049899286/

  avec:
    sans plancher:
      somme:
        - revenu professionnel
        - cotisations facultatives . déductibles

    réforme assiette 2024:
      titre: réforme de l'assiette sociale des indépendants (LFSS 2024, décret 2024-688)
      valeur: """ + DATE + """
      description: |
        Vrai lorsque l'assiette unifiée (L131-6 I / L136-3 III) et son abattement forfaitaire (D136-5) s'appliquent.

    réforme assiette 2024 . plafond annuel:
      titre: plafond annuel de la sécurité sociale
      valeur: plafond sécurité sociale
      unité: €/an

    réforme assiette 2024 . assiette avant abattement:
      titre: assiette avant abattement forfaitaire (lignes de revenu NON tranchées)
      unité: €/an
      valeur: sans plancher
      note: |
        PLACEHOLDER (abstention). Les textes disponibles (L136-3 I 1° et 2°, L131-6 I) ne permettent pas de trancher quelles
        lignes de revenu entrent dans cette assiette (notamment le sort des cotisations sociales obligatoires, des cotisations
        facultatives et des cotisations du conjoint collaborateur, qui étaient réintégrées dans l'ancienne assiette de la
        CSG). Faute de texte, la règle reprend la ligne déjà utilisée par la bibliothèque (revenu professionnel + cotisations
        facultatives déductibles). À revoir dès qu'un texte le précise.

    réforme assiette 2024 . abattement forfaitaire:
      titre: abattement forfaitaire de 26 % (L136-3 III, D136-5)
      unité: €/an
      valeur: 26% * assiette avant abattement
      plancher: 1.76% * plafond annuel
      plafond: 130% * plafond annuel
      note: |
        L136-3 III : « fait l'objet d'un abattement de 26 % » ; D136-5 I : plancher « fixé à 1,76 % de la valeur annuelle du
        plafond de la sécurité sociale » ; D136-5 II : plafond « fixé à 130 % de la valeur annuelle du plafond de la sécurité
        sociale ».

    réforme assiette 2024 . assiette unifiée:
      titre: assiette unifiée des cotisations et de la CSG-CRDS
      unité: €/an
      valeur: assiette avant abattement
      abattement: abattement forfaitaire
"""),
# ---- E2: maladie reduced-rate formula (D621-2 LEGIARTI000049904592) ----
("""    taux progressif:
      arrondi: 2 décimales
      taux progressif:
        assiette: assiette
        multiplicateur: plafond sécurité sociale
        tranches:
          - taux: 0.5%
            plafond: 40%
          - taux: 4.5%
            plafond: 60%
          - taux: 7.20%
            plafond: 110%
      références:
        Article D621-2 du Code de la sécurité sociale: https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046714747/
""",
"""    taux progressif:
      arrondi: 2 décimales
      variations:
        - si: """ + DATE + """
          alors:
            taux progressif:
              assiette: assiette
              multiplicateur: plafond sécurité sociale
              tranches:
                - taux: 0%
                  plafond: 20%
                - taux: 1.5%
                  plafond: 40%
                - taux: 4%
                  plafond: 60%
                - taux: 6.5%
                  plafond: 110%
                - taux: 7.7%
                  plafond: 200%
                - taux: 8.5%
                  plafond: 300%
        - sinon:
            taux progressif:
              assiette: assiette
              multiplicateur: plafond sécurité sociale
              tranches:
                - taux: 0.5%
                  plafond: 40%
                - taux: 4.5%
                  plafond: 60%
                - taux: 7.20%
                  plafond: 110%
      note: |
        PROPOSITION T1b. Version LEGIARTI000049904592 de D621-2 (décret n°2024-688 du 5 juillet 2024 art. 2, en vigueur le
        07/07/2024) : taux nul sous 20 % du PASS ; T1 = 1,5 % à 40 % ; T2 = 4 % à 60 % ; T3 = 6,5 % à 110 % ; T4 = 7,7 % à
        200 % ; T5 = 8,5 % à 300 % ; interpolation linéaire entre ces points, « a » étant l'assiette définie à L131-6.
        Au-delà de 300 % du PASS le texte renvoie au taux de base (L621-3 I / D621-1), qui n'est pas dans le corpus : la valeur
        8,5 % retenue au-delà de 300 % est le prolongement mécanique de la dernière tranche, PAS une valeur transposée
        (abstention). Avant le 07/07/2024 : version LEGIARTI000046714747 (inchangée).
      références:
        Article D621-2 du Code de la sécurité sociale (version LEGIARTI000046714747, jusqu'au 07/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000046714747/
        Article D621-2 du Code de la sécurité sociale (version LEGIARTI000049904592, en vigueur le 07/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049904592/
"""),
# ---- E3: retraite de base rates (D633-3 LEGIARTI000049904636) ----
("""    tranches:
      - taux: taux
        plafond: plafond sécurité sociale
      - taux: 0.6%
  arrondi: oui
""",
"""    tranches:
      - taux: taux
        plafond: plafond sécurité sociale
      - taux: taux déplafonné
  arrondi: oui
"""),
("""  avec:
    taux: 17.75%
""",
"""  avec:
    taux:
      titre: taux dans la limite du plafond (D633-3 I) + taux sur la totalité (D633-3 II)
      variations:
        - si: """ + DATE + """
          alors: 17.87%
        - sinon: 17.75%
      note: |
        PROPOSITION T1b. D633-3 version LEGIARTI000049904636 (décret n°2024-688 art. 3, en vigueur le 07/07/2024) : « dans la
        limite du plafond est fixé à 17,15 % » et « sur la totalité de l'assiette de cotisations est fixé à 0,72 % » ; la
        première tranche cumule les deux : 17,15 + 0,72 = 17,87 % (avant : 17,15 + 0,60 = 17,75 %, LEGIARTI000041967101).
      références:
        Article D633-3 du Code de la sécurité sociale (version LEGIARTI000041967101, jusqu'au 07/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000041967101/
        Article D633-3 du Code de la sécurité sociale (version LEGIARTI000049904636, en vigueur le 07/07/2024): https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049904636/

    taux déplafonné:
      titre: taux sur la totalité de l'assiette (D633-3 II)
      variations:
        - si: """ + DATE + """
          alors: 0.72%
        - sinon: 0.6%
"""),
# ---- E4: CSG-CRDS base unified with the contributions base (L136-3 I/III) ----
("""  valeur:
    somme:
      - assiette des cotisations . sans plancher
      - cotisations
      - conjoint collaborateur . cotisations
""",
"""  valeur:
    variations:
      - si: assiette des cotisations . réforme assiette 2024
        alors: assiette des cotisations . réforme assiette 2024 . assiette unifiée
      - sinon:
          somme:
            - assiette des cotisations . sans plancher
            - cotisations
            - conjoint collaborateur . cotisations
"""),
])
print("applied 5 edits to", f)
