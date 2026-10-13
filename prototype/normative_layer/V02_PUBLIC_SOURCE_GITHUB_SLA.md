# V0.2 public governing sources — GitHub Online Services SLA (13 Oct 2026)

**Status:** RECOMMENDED EXTERNAL CORPUS / NOT A VALIDATION RESULT. This note selects independently authored public terms for the next outside-in test. Neither this note nor an LLM prediction is an authoritative legal interpretation. No live contract or specific customer's acceptance has been verified. **Do not embed full copyrighted documents in the repository**; retain official URLs, retrieval timestamp, locally recorded content hashes and a short set of clause citations/excerpts as permitted.

## Primary sources — read in this order

1. **GitHub Online Services SLA, June 2026 (current published terms):** https://github.com/customer-terms/github-online-services-sla
2. **GitHub Online Services SLA, June 2021, archived vendor-hosted PDF (2 pages):** https://assets.ctfassets.net/8aevphvgewt8/7rEf04yu01oTt1cGyeXz03/f58072058dfb2f1fb25cb80b0b285890/GitHub.Online.Services.SLA_20210630_locked
3. **GitHub's June 2026 change notice:** https://github.com/customer-terms/updates
4. **GitHub Customer Agreement general terms:** https://github.com/customer-terms/general-terms

GitHub's official update notice says that the substantially rewritten **June 2026 SLA applies to new customers and renewals beginning 1 June 2026**. It does **not** state that all existing 2021 customers automatically switched on that date. Model applicability as a contract/renewal fact, not by global date alone.

These are genuine supplier-published standardized contractual terms; they do **not** establish that a particular company has signed/accepted an order. The founder case is a *company as buyer of GitHub services*: support and finance/billing agents retrieve the same supplier obligations and claims conditions.

## Why this corpus, not a lab-authored threshold

There are **two real published versions**, rather than a synthetic amendment. It exercises document applicability by customer cohort and renewal status, cross-document definitions, multi-tier credits, service-specific uptime methods, exclusions, claim procedure and date, and historical meaning. Multiple operational facts are missing from the contract and must come from a system of record.

June 2021 SLA, GHEC uptime tier: **10%** of eligible service-feature fees for uptake **>99.0% and <=99.9%**, and **25%** for uptime **<99.0%**. Literal wording at exactly 99.9% sits uneasily with the 'at least 99.9%' service-level objective; record it as an interpretation concern, not a license to confidently award a credit.

June 2026 SLA, Section 3: **5%** for uptime **>=99.5% and <99.9%**, **10%** for **>=99.0% and <99.5%**, **25%** for **<99.0%**. Claims must be requested in writing within 30 days of the end of the applicable quarter, with applicable purchase channel and outstanding invoices affecting actual redemption. Section 4 lists exclusions. Section 5 defines service-specific uptime calculations.

**Never assume 2021 and 2026 terms govern the same customer simultaneously.** The actual executed subscription/order and renewal history are missing. Use explicit labeled *simulated customer contract metadata* to decide applicable version; default to UNKNOWN where absent.

## Frozen working expectations to review *before* implementation

These are arithmetic examples under stated, simulated conditions (GitHub Enterprise Cloud, qualifying quarter, valid claim, all invoices paid, no excluded downtime, verified uptime and fees). Not legal conclusions.

| Case | Assumed published SLA version and renewal status | Uptime | Eligible fees | Conditional credit | Important caveat |
|---|---|---:|---:|---:|---|
| A | 2021 still governs, no renewal | 99.7% | EUR 1,000 | EUR 100 | Estimate only; service-feature fee base must be checked |
| B | New/renewed customer governed by June 2026 | 99.7% | EUR 1,000 | EUR 50 | Same facts; different governing version |
| C | 2026 governs | 99.2% | EUR 1,000 | EUR 100 | 2026 second band |
| D | 2026 governs | 98.9% | EUR 1,000 | EUR 250 | 2026 third band |
| E | 2026 governs | 99.9% | EUR 1,000 | EUR 0 | SLA not breached at threshold |
| F | 2021, exactly 99.9% | 99.9% | EUR 1,000 | UNRESOLVED | Potential textual tension with 'at least' 99.9% |
| G | Version/renewal unknown | 99.7% | EUR 1,000 | UNRESOLVED | Do not guess applicable authority |
| H | 2026, claim out of window or invoice unpaid | 99.7% | EUR 1,000 | NOT CLAIM-READY | Distinguish prospective arithmetic from remedy entitlement |
| I | 2026, downtime excluded/unverified | 99.7% | EUR 1,000 | NEEDS_EVIDENCE/UNRESOLVED | Do not accept caller's unsupported metric as verified |

Use the original official documents to adjudicate each before scoring. If a number, interpretation, fee base or quoted rule above is mistaken, amend this *working reference with a recorded reason before implementation*; do not let production code be the oracle.

## Single integrated demonstration; avoid the infinite testing loop

1. Prove V0 **actually fails/abstains** on the independently authored wording; preserve the failure.
2. Implement just enough **source-anchored candidate extraction + reviewed normative version routing** to answer the GHEC conditional credit and claim-readiness questions. It is acceptable to return UNKNOWN for unsupported conditions, but not to silently drop a relevant one.
3. Demonstrate *two distinct clients* (support and finance) using the same normative API, without contract-specific client code.
4. Demonstrate an actual published contractual **version change upon simulated renewal** (not a fabricated threshold amendment), correctly scoped to one customer while an unrenewed customer remains on 2021. Retain both versions.
5. Include one **implementation-originated drift** and one harmless no-op check if feasible; otherwise report the precise missing reverse capability without claiming success.
6. Default offline CI: source snapshots/hashes captured separately (subject to rights), mocked candidate proposals; no paid external model calls required. Never treat simulated operational data or fabricated order history as genuine customer evidence.

**Bound the effort:** aim for a single focused V0.2 implementation iteration, then decide **CONTINUE / NARROW / STOP** for the *normative representation kernel*, based on the following capabilities: true cross-agent portability, correct version selection, no silent confident misinterpretation of the included conditions, and less contract-specific wiring than two independent hardcoded clients. Do **not** add another 5-10 rounds of micro-tests merely to turn a FAIL into a PASS. Record an architectural obstacle as an actual outcome.

## Relation to the task prompt

See `Claude_Code_Sophon_V02_Outside_In_Walking_Skeleton_2026-10-13.md` at the branch root. This note selects a specific more discriminating real public corpus, which can replace the prompt's initial Cloudflare R2 candidate; do not silently narrow the experiment to fit the old two regexes. Read all four official documents above before implementation.
