# Sophon — IPSA public-data shadow replay

**21 September 2026 | Corrected after an additional source check: stop using the public IPSA export as a falsification benchmark for Sophon's core economics. Keep the replay instrument.**

> **Policy-version correction.** The replay applied the 15th Scheme across the whole 2023–24 dataset. An [official October 2023 review](https://assets.ctfassets.net/w59ykwiqehvh/18t8MeQrTBBsNGJQoqpVs9/9eccd2744f3ce9e835f042aad08f968a/20231020-IPSA-COM-1491-KAWCZYNSKI-Review-Final.pdf) states that the **16th edition, revised July 2023**, governed that claim. Therefore this frozen replay is **not a historically version-correct policy evaluation** for all sampled dates. The 1,000 `REQUEST_FACT` observations remain a valid audit of missing fields in the public export; the report should not be read as a scored test of the applicable Scheme across the whole year. The new [authority case-study report](Sophon_IPSA_Authority_Case_Study_2026-09-21.md) analyzes this failure mode.

## Executive finding

I ran a frozen, label-blind replay of **1,000 real published IPSA expense rows** using the [2023–24 individual-claims export](https://www.theipsa.org.uk/mp-staffing-business-costs/annual-publications) and the [15th edition of the Funding Scheme](https://assets.ctfassets.net/nc7h1cs4q6ic/1neQ7j3vniH5Zpt9XpJIOA/4978bbea5a5a1ab13ce9f05cca7e2b0b/Fifteenth_Edition_of_the_Scheme_2023-24.pdf) as an incomplete reference. The selection covered expense dates from 1 April 2023 through 31 March 2024. The runtime produced 1,000 `REQUEST_FACT`, zero `CLEAR` and zero `BLOCK` decisions, before any published payment outcomes were examined. **The source-version mismatch above limits the inference to field observability and conservative abstention.**

After freezing decisions, I revealed the statuses: **997 Paid, 1 Not Paid, 2 Repaid**. The whole publication contains 91,567 rows, of which 82,787 have an expense/processing date within the 2023–24 year. Across those 82,787, **82,323 Paid, 18 Not Paid, 446 Repaid**. This means the random 1,000-row sample contains almost no adverse examples; even the full in-period file has only 18 explicit `Not Paid` entries. `Repaid` is not a clean proxy for an initially unauthorized claim: IPSA describes several possible repayment causes. [IPSA's guide](https://www.theipsa.org.uk/a-guide-to-mps-business-costs).

**Interpretation:** 0% observed deterministic coverage is a finding about this *public export as an action-time fact source*. It is **not** evidence that Sophon would achieve 0% with access to the claim submission system, supporting documents and budget ledger. Likewise, zero false `CLEAR` decisions here is a vacuous safety result: the runtime cleared nothing.

## What was built and frozen

The attached replay bundle contains a standard-library Python CLI, a hand-curated inventory of 23 Scheme propositions, a feature-only 1,000-row sample, individual decisions with the missing predicates, a sample manifest and a frozen decision hash. It never treats past published payment as prospective authority. This implements the narrow data audit; it does **not** compile the Scheme automatically, ratify interpretations, benchmark human minutes or execute reimbursements.

Sequence actually executed:

1. Download the source CSV and contemporary Scheme PDF; record their SHA-256 hashes.
2. Filter rows whose published `Date` falls in the financial year; select 1,000 by fixed SHA-256 ranking independent of outcome, then order them by published date.
3. Write a feature-only sample excluding `Status`, amount paid/not paid/repaid and reason if not paid; manually enumerate governing predicates from the Scheme.
4. Score the feature-only sample and freeze the decision file (`SHA-256 fff7cb525839c8ffd7d0cba28ebe0ec25feab3716d98ab840801ed3f8b111801`).
5. Only then join the publication labels and tabulate them. Run two guard tests proving changing an injected `Paid`/`Not Paid` field cannot change the decision, and that a rail category alone does not justify clearance.

The source CSV checksum is `4f4f5f52f7850996b48d4e118af7660216eafaaa3b2d93b368a023ee244413e9`; the Scheme PDF checksum is `f4b9c10b09d5bbfe88d3773db039f130ae8c8b2e6fc78289eb92b3df8446e4dc`. The code and feature-only outputs are in the separate replay bundle. The bundle can re-download the public raw sources.

## Why the conservative result is justified

The Scheme requires parliamentary purpose, value for money and supporting evidence, and puts responsibility for certification on the MP. Its determination provisions say that a decision is made upon submission with supporting evidence; an earlier determination **does not bind future similar claims** (§2.3). Relevant rules include Part A, §§1.1, 2.3, 3.2, 3.8–3.13 and category-specific chapters. [15th Scheme](https://assets.ctfassets.net/nc7h1cs4q6ic/1neQ7j3vniH5Zpt9XpJIOA/4978bbea5a5a1ab13ce9f05cca7e2b0b/Fifteenth_Edition_of_the_Scheme_2023-24.pdf).

The published fields include category, type, some amounts and occasional route or mileage data, but omit the receipts, actual certification, submission timestamp, current budget balance, internal review, and often the fact needed to assess the parliamentary purpose. A source clause that allows a type of expense does not authorize the exact amount or prove the evidence was submitted. IPSA also warns that some information is withheld, that publication is updated every two months, and that the published date usually refers to expenditure, occasionally an internal processing date. It is **not a reliable decision-time order**. [Annual publication](https://www.theipsa.org.uk/mp-staffing-business-costs/annual-publications), [data guide](https://www.theipsa.org.uk/a-guide-to-mps-business-costs).

| What the frozen replay measures | Result | Valid conclusion |
|---|---:|---|
| Published cases sampled | 1,000 | Real transactions across the financial year |
| `CLEAR` / `BLOCK` | 0 / 0 | No exact claim can be decided safely from these public fields under the conservative gate |
| `REQUEST_FACT` | 1,000 | Supporting evidence, certified purpose and budget/other-funding state are unavailable in all sampled rows |
| Published `Not Paid` | 1 | Strong class imbalance in the sample |
| Authorized interpretations | 0 | No policy owner was available and none was simulated |
| Human-effort comparison | Unmeasured | No basis to claim an economic advantage over policy-as-code or AI review |

The separately recorded `semantic_residuals` capture narrow candidate classes, but they are not exhaustive. Only one sampled row was flagged for a *reasonable transport alternative*; this is an artefact of visible categories and the hand-built taxonomy. It **must not** be read as evidence that only one row requires semantic judgment. No counterfactual amortization metric is computed from this data.

## Amendment check: possible, not validated

The [17th Scheme for 2024–25](https://assets.ctfassets.net/nc7h1cs4q6ic/5j9dlpZsDtyFgqi43bBB91/7eaea5bcc329496878b420bf2e511586/Seventeenth_edition_of_the_Scheme_2024-25.pdf) changes annual budgets (for example London office costs £33,840 → £36,550; non-London office costs £30,570 → £33,020) while keeping the published London/Europe hotel nightly cap at £210. Those are real version changes. The current bundle does not contain compiled authorization decisions or budget balances to invalidate, so it cannot measure impacted-authority recall, maintenance minutes or stale clearance. Claiming a successful amendment replay from a text diff alone would overstate the result.

## Decision and next experiment

The initial claim that IPSA would provide a strong, self-sufficient shadow pilot was **too optimistic**. IPSA is a good *schema and abstention stress test*, but its public export cannot adjudicate Sophon's central thesis: the cost and reuse of authorized interpretations. It also falls far short of the predeclared target of 100 non-obvious historical decisions with usable rationale.

Keep the frozen bundle as a negative benchmark for fact observability. For an economic test, the minimum dataset must expose the **decision-time evidence and authority** for at least one recurring workflow: policy version, submitted facts/receipts, approval timestamps, rationale, actor's delegated power and an outcome. Without such data or a real policy owner, report only instrument behavior and candidate reuse classes; do not call the public replay a product pass or failure. A future 2024–25 Scheme replay would require its own fresh source freeze and separate decision-time fact assessment.
