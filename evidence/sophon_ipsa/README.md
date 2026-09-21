# Sophon / IPSA public shadow replay

**Correction:** the frozen v1 applies the 15th Scheme to a whole-year 2023–24 sample. An official October 2023 Compliance Officer review identifies the 16th edition (revised July 2023) as the applicable source at that time. Accordingly, treat the frozen run only as a *public-field observability and abstention audit*, not as historically version-correct policy scoring. Do not extend the run into a 2023–24 policy accuracy benchmark without first obtaining and time-binding the 16th Scheme and verifying other changes. The decision file is deliberately preserved rather than silently regenerated.

Reproducible, conservative test of the IPSA 2023–24 claims publication against the 15th edition of the Funding Scheme. This is a **public-data observability test**, not a live deployment or a test of authorized human ratification.

Run with Python 3.10+ and no third-party dependencies. The archive already contains a frozen run. To inspect its aggregates, open `results/aggregate.json`; to rejoin labels after downloading the original sources, run `fetch` and `reveal`.

To make a **new** replay, copy only `replay.py`, `policy_15th.json`, and `test_guards.py` into a new empty directory, then run:

```bash
python replay.py fetch
python replay.py prepare
python replay.py score
python replay.py reveal
```

`prepare` selects 1,000 2023–24 rows by a predeclared SHA-256 rank over the claim number and input row index, then sorts those rows by **expense date**. It writes a feature-only sample and its hash. `score` reads only the feature-only file, never the historical label fields. `reveal` verifies the frozen decision hash and joins published outcomes by the input row index. Run commands in order for a new replay. `fetch` downloads the authoritative IPSA CSV and the contemporary 15th Scheme and records SHA-256 hashes. There is no model call, hidden training or inferred authority.

The exact question scored is whether the **full amount claimed** can be cleared from the public fields under the Scheme. A category, amount or prior paid status alone cannot prove the claim was within scope, evidenced and validly submitted. The runtime therefore cannot issue `CLEAR` based only on the publication. It records missing facts and unresolved semantic classes separately, and can issue `BLOCK` only for an unambiguous prohibition with enough visible facts. Some claims are direct supplier payments rather than reimbursements, so submission deadlines are listed as potentially needed, rather than asserted for every row.

Published date is generally expenditure date, occasionally internal processing date, and is **not a decision timestamp**. Published `paid`, `not paid` and `repaid` are useful diagnostic outcomes, but a `paid` row does not establish that its supporting facts were publicly observable before decision. The 15th Scheme §2.3 expressly states that an IPSA decision does not bind future similar claims. The replay does not turn historical decisions into precedents.

Sources:

- [IPSA 2023–24 individual business costs CSV](https://www.theipsa.org.uk/api/download?type=individualBusinessCosts&year=23_24)
- [IPSA 15th edition Funding Scheme PDF](https://assets.ctfassets.net/nc7h1cs4q6ic/1neQ7j3vniH5Zpt9XpJIOA/4978bbea5a5a1ab13ce9f05cca7e2b0b/Fifteenth_Edition_of_the_Scheme_2023-24.pdf)
- [IPSA guide to published statuses and dates](https://www.theipsa.org.uk/a-guide-to-mps-business-costs)

The outputs in `results/` contain no MP names. Raw IPSA data is downloaded to `data/` when the user runs `fetch`.
