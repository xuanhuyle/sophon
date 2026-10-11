## Task T1b — forward transposition of the self-employed contribution-base reform (decision date {DECISION_DATE})

Law snapshot {LAW_SNAPS} is the first in which the implementing decree of the 2024 social-security
financing law's reform of the self-employed contribution base is consolidated. The rule library is at pin
{RULES_PIN}. Relevant articles in the bounded set: L131-6 and L136-3 (law, in force 2023-12-28),
D136-5, D621-2, D633-3 (decree, in force 2024-07-07). Read them; note what each says about the base of
the CSG-CRDS and of the contributions of `dirigeant . indépendant`, the flat abattement, its floor and
ceiling, the maladie reduced-rate formula and the retirement rates, and from when they apply.

1. Identify the changed articles (version ids, in-force dates, modifying text).
2. Classify every bounded `dirigeant . indépendant . cotisations et contributions . …` rule and the
   `assiette minimale` rules as `AFFECTED`, `UNAFFECTED` or `NEEDS_REVIEW`, with evidence.
3. Propose edits in `work/proposals/T1b/modele-social/règles` for what the text settles
   deterministically (percentages, floor and ceiling expressed as a share of the annual social
   security ceiling `plafond sécurité sociale`, dates), run `build`, and `evaluate` before/after for a
   self-employed trader (`dirigeant . régime social: "'indépendant'"`, `entreprise . catégorie juridique: "'EI'"`,
   `entreprise . imposition: "'IR'"`, `entreprise . activité . nature: "'commerciale'"`,
   `dirigeant . indépendant . revenu professionnel: 40000 €/an`) at 2024-12-01 and 2025-06-01.
   Where the text leaves the meaning open (for example which income lines enter the base), say so and
   abstain rather than guess.

### Deliverable `output/answer.json`

Same shape as T1a (`task: "T1b"`), with `evaluations` giving, for every number you transposed, the
quote and article version id that justify it, and `abstentions` for what you did not transpose and why.
Also write `output/NOTES.md`.
