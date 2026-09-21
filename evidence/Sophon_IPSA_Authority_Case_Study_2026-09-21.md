# Sophon: how far the public IPSA evidence can take us

**21 September 2026 | Five published decisions, one scope probe, and a corrected reading of the earlier replay**

## What changed

The first 1,000-claim replay was an observability audit, not a valid full-year historical policy score. An [October 2023 Compliance Officer review](https://assets.ctfassets.net/w59ykwiqehvh/18t8MeQrTBBsNGJQoqpVs9/9eccd2744f3ce9e835f042aad08f968a/20231020-IPSA-COM-1491-KAWCZYNSKI-Review-Final.pdf) names the **16th Scheme, revised July 2023**, as governing its case. The replay had assigned the 15th Scheme to all claims dated in 2023–24. The 1,000 `REQUEST_FACT` outputs still show that essential fields were absent from the export, but they cannot be used to measure version-correct policy accuracy. The earlier report and bundle have been marked with this correction, without changing the frozen decisions.

I located a richer public corpus: [IPSA Compliance Officer's completed reviews](https://www.ipsacompliance.org.uk/investigations/completed-reviews). Each selected report identifies a reviewer with authority to decide an appeal, recounts evidence and a sequence of decisions, and often identifies the applicable Scheme. This allows a realistic **authority provenance and lifecycle test** without recruiting another person. It does not make the review decision a general, binding precedent: the [Scheme §2.3](https://assets.ctfassets.net/nc7h1cs4q6ic/5j9dlpZsDtyFgqi43bBB91/7eaea5bcc329496878b420bf2e511586/Seventeenth_edition_of_the_Scheme_2024-25.pdf) says an IPSA determination on one claim does not bind future similar claims. The Davies review expressly disclaims precedent for its own 50% remedy.

I also indexed and downloaded all **46 PDF links** on the official completed-reviews page and recorded source URL and SHA-256 per file. All downloads succeeded. Text extraction yielded a median of **18,021 characters**; one tribunal decision produced only 13 characters and needs OCR or separate manual review. Keyword screening found 22 documents containing “exceptional circumstances” and 24 referencing a Scheme edition. These are navigation counts, **not** counts of authoritative interpretations, unique cases or correct extractions. The inventory and re-download script are in the case-study bundle; the five cases below were checked against the original reports.

## Five case studies from original reports

| Case | Normative issue actually visible | Correct treatment in Sophon |
|---|---|---|
| [McMahon storage](https://assets.ctfassets.net/w59ykwiqehvh/1UXeAPGp5NulMX4jNZJkMI/c8405a00f24572716ab0170d5da81788/IPSA_Compliance_review_outcome_report__final__J_McMahon_COM-1613.pdf) | Panel granted storage for one MP, initially for eight weeks; extended it through March 2024; refused a retrospective request covering April–July 2024. | Case-specific authority has named beneficiary, purpose and end date. A later claim must request fresh authority, even if it appears cheaper than alternative accommodation. |
| [Kawczynski electricity](https://assets.ctfassets.net/w59ykwiqehvh/18t8MeQrTBBsNGJQoqpVs9/9eccd2744f3ce9e835f042aad08f968a/20231020-IPSA-COM-1491-KAWCZYNSKI-Review-Final.pdf) | Panel rejected a £935.07 contingency application; officer found no exceptional circumstances after examining bills and payment history, yet permitted limited case-specific relief tied to the prior year's budget after consulting IPSA's CEO. Report identifies the intervening 16th Scheme. | Separate factual finding, interpretation of an open standard, and the individual remedy. Do not compile this into a general right to carry budget underspends forward. |
| [Aquarone festive meal](https://assets.ctfassets.net/w59ykwiqehvh/3hxqCNweqk2KJYPceDx2ZS/c766330d6ae1c4e75bd0ef4a00eea0ee/Review_outcome_-_Steff_Aquarone.pdf) | IPSA accepted that festive hospitality guidance had caused confusion and said it would clarify it; the officer upheld refusal of a restaurant meal and service charge, distinguishing the parliamentary away day from the later meal. | A stated intention to update guidance is a **proposal**, not an effective amendment. The decision is case-specific; the activity timeline and receipt components matter. |
| [Davies newsletter](https://assets.ctfassets.net/w59ykwiqehvh/7boh1E125Hqmhohr12JTMs/c8ec7864b49280a6e6df60adff705715/Ann_Davies_review_of_IPSA_determination.pdf) | Officer says the newsletter rule changed in the 18th edition. The original refusal was correct on the facts then known; after new evidence the officer altered it to **50% funding**, expressly stating this was **not a precedent** for future joint funding. | Separate source amendment, original determination, newly established facts and non-precedential partial remedy. Never turn 50% into a general split-funding rule. |
| [Hussain monitors](https://assets.ctfassets.net/w59ykwiqehvh/6HFLYxtdTQ9Y2F5RTBhk3C/32837ad7125b9ea8ac91ce3cf0652004/IPSA_Compliance_statement_of_review_decision_Imran_Hussain_MP.pdf) | Office IT was supplied through Parliamentary Digital Services after the 2024 election. The officer upheld refusal of £840.97 as submitted, but said £44.97 of accessories might be funded if separately resubmitted. | Check the right funding authority and bind each line item. Neither the full approval nor a universal sub-£50 threshold follows from the partial resubmission route. |

These reports contain **later-gathered facts**, such as internal panel notes, invoices, correspondence and interviews. A retrospective engine must restrict itself to evidence actually available at each original decision point. Using the final review as if it were the initial dossier would leak the answer backward in time.

## What I implemented

The accompanying case-study bundle records each report with its source and paragraph references. A minimal `authority_probe.py` answers only whether a published, case-specific *grant window* is documented; it **never** emits payment clearance. Its six passing guards check that:

1. McMahon's documented storage extension does not authorize another MP.
2. The extension does not authorize costs after March 2024.
3. Even an in-period match returns `AUTHORITY_EVIDENCE_ONLY` because the exact invoice, grant instrument, effect and applicable policy are not public.
4. IPSA's intention to clarify festive guidance does not become a published rule.
5. Kawczynski's individual outcome does not grant another MP's electricity claim.
6. Davies's expressly non-precedential 50% remedy does not authorize a different newsletter.

This establishes that a small provenance ledger can preserve **who, what and until when** from real reported decisions. It does **not** establish that Sophon can independently extract every clause, validate the original grant, adjudicate the underlying claim or save human governance time. The code is a narrow guard built from hand-curated official reports, not a general semantic compiler.

## Highest-value next move without an outsider

There are two honest layers we can now build ourselves:

**1. Continue the public, authority-aware corpus.** The 46-document indexed corpus is ready for chronological curation: capture source version, initial facts, later facts, deciding actor, decision power, case-specific scope, amendment evidence and outcome. Score the extraction and scope guard against a *manually prepared case sheet*, keeping the eventual decision hidden during extraction. These are selected appeal cases; they cannot estimate ordinary expense automation rates.

**2. Create an explicitly separate sandbox policy owned by the experiment participant.** The owner writes or adopts its rules, ratifies prospective interpretations, and times the ratification work. We can replay real claim *shapes* with anonymized or constructed facts inside this sandbox. The owner's acts would be genuine authority **for the sandbox only**, never IPSA authority. Compare the same person's minutes and coverage against a conventional rule-writing baseline. This can test the interaction cost and mechanical compounding under controlled conditions, while disclosing self-review bias and lack of commercial generalizability.

We can proceed with both layers without anyone outside the project. We cannot honestly claim the original business hypothesis has passed until the ratification economics have been observed in an operational setting with decision-time evidence.
