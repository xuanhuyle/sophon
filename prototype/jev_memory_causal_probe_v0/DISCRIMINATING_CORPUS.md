# Discriminating normative candidate set v0 — two new authentic SLAs

**Status:** `PREDECLARED_BEFORE_ANY_JEV_QUERY_NOT_INDEPENDENT_LEGAL_GOLD`
- 0 provider or model calls were made.
- **No cold Jev error has been observed on these documents**, because no Jev call has been made on them.
- Scope labels: `MANUALLY_CURATED_SOURCE_EXCERPTS` · `MULTI_LABEL_PER_EXCERPT` · `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`.

**Recommendation: `GO_TO_BOUNDED_COLD_SCREEN`, narrowed after the engineering-lead review of 2026-10-16 to the three definitive Microsoft update decisions only (at most 6 Jev calls).** This is a request for owner authorization only. It does not authorize any call, and it does not imply the library helps.

Data: `discriminating_candidates_v0.json`. Check: `test_discriminating_candidates.py`.

## Sources (both fetched and verified 2026-10-16)

| Source ID | Split | Publisher / document | Version | Retrieval | SHA-256 of fetched bytes |
|---|---|---|---|---|---|
| `MS-OSSLA-2021-07` | **LIBRARY_UPDATE** | Microsoft, *Service Level Agreement for Microsoft Online Services* (Volume Licensing, WW, English) | July 1, 2021 (cover date) | [microsoft.com versioned archive](https://www.microsoft.com/licensing/docs/documents/download/OnlineSvcsConsolidatedSLA(WW)(English)(July2021)(CR).docx), HTTP 200, 123,064 B docx | `f94b354a…b7ac4a1` |
| `ORCL-PILLAR-2026-09` | **HOLDOUT** | Oracle, *PaaS and IaaS Public Cloud Services Pillar Document*, §3 Service Level Agreement Policy | September 2026 (cover and footers; Last-Modified 17 Sep 2026) | [oracle.com/contracts](https://www.oracle.com/contracts/docs/paas_iaas_pub_cld_srvs_pillar_4021422.pdf?download=false), HTTP 200, 2,747,733 B PDF | `aa43a70b…b936af4b` |

**Independence from earlier work.** These are different publishers and templates from GitHub 2021 and Google Cloud Storage 2021, and neither document was used before in this repo.

**Version stability.** Microsoft's file is a dated archive copy, so it should stay stable. Oracle's URL serves the current Pillar document, so a later fetch may return a newer version; the recorded hash pins the September 2026 one.

**Rights.** Both documents are copyrighted. Only short excerpts (12 contexts, about 6.3k characters) are committed, and the full documents are not.

**Offsets.** Offsets index a whitespace-normalised extraction:
- Microsoft: docx `<w:t>` text.
- Oracle: `pdftotext` 24.02.0.

That extraction is hashed in the JSON. PDF extraction introduces small artefacts; for example, the de-hyphenated "thirdparty" appears in OR2's context.

**Reachability.** The environment's proxy blocked AWS, DigitalOcean, Cloudflare and web.archive.org (403 on CONNECT). The two sources above are simply the reachable primary publishers, not a selection made for difficulty.

## The 12 predeclared decisions

Function wording is copied verbatim from `probe.py`, so there is no new ontology. `NO` means *this clause* does not express the function. It does not assert that no such duty exists elsewhere in the agreement.

| ID | Split | Function | Label | Why this case can discriminate |
|---|---|---|---|---|
| MS1 | update | OBLIGATION | **YES** | Standalone provider duty: "We will provide at least 90 days’ notice for adverse material changes to this SLA." |
| MS2 | update | PROHIBITION | **YES** | "You may not unilaterally offset your Applicable Monthly Service Fees…". It forbids a self-help action, though it sits next to a sole-remedy sentence. |
| MS3 | update | PROHIBITION | **NO** | The Limitations list ("do not apply to any performance or availability issues:") excludes listed Customer conduct from coverage; it does not forbid it. Tests exclusion vs prohibition. |
| MS4 | update | OBLIGATION | UNRESOLVED | "We will publish notice…" sits *inside* the Scheduled Downtime definition. It may be a promise, or only a definitional condition. |
| MS5 | update | OBLIGATION | UNRESOLVED | "In order for Microsoft to consider a claim, you must submit the claim…". Same structure as the contested Google B3 notice. |
| OR1 | holdout | EXCLUSION | **YES** | Oracle's "Common Exclusions": "does not apply to … that results from the following". |
| OR2 | holdout | PROHIBITION | **NO** | "Any actions or inactions of You…" (e.g. "restarting, stopping, or patching a database") are excluded causes, not forbidden acts. Contrast with MS3. |
| OR3 | holdout | OBLIGATION | **NO** | "Oracle may issue Service Credits … at Oracle’s discretion" is a discretion, not a duty. |
| OR4 | holdout | OBLIGATION | **YES** | "Oracle will use commercially reasonable efforts to process a claim within sixty (60) days…" is an efforts duty. |
| OR5 | holdout | OBLIGATION | UNRESOLVED | "In order to be considered to receive Service Credits, You must file a claim…". Same structure as B3 and MS5. |
| OR6 | holdout | OBLIGATION | **NO** | "are contingent on Your adherence to Oracle's recommended … requirements" is a condition with no "must" addressed to the Customer. Tests turning a condition into a duty. |
| OR7 | holdout | PROHIBITION | UNRESOLVED | "You may not carry those Service Credits over to another month". The modal "may not" limits the Customer's own credits right after "will expire". Contrast with MS2. |

**Counts:** 4 YES, 4 NO, 4 UNRESOLVED.

| Split | Definitive decisions | UNRESOLVED |
|---|---|---|
| Library update (Microsoft) | 3: MS1 Y, MS2 Y, MS3 N | 2 |
| Holdout (Oracle) | 5: OR1 Y, OR2 N, OR3 N, OR4 Y, OR6 N | 2 |

Each JSON record holds the exact quote, an interpretive context excerpt, offsets, the context SHA-256, evidence for **both** readings, and a qualification.

**Why the four UNRESOLVED cases are kept.** Three repeat the unresolved B3 question (is a claim prerequisite with forfeiture an OBLIGATION?). OR7 adds the "may not" restriction-of-own-right variant. If the owner sets that taxonomy rule, these become definitive with no new sourcing. Until then they are excluded from error accounting.

## Verification (offline, deterministic)

`test_discriminating_candidates.py` runs in CI with the other probe tests.

| Check | Result |
|---|---|
| 8–12 decisions, ≥3 YES and ≥3 NO, wording identical to `probe.py`, evidence present for both readings | pass |
| Each quote sits at its recorded offsets inside its context; context hashes match | pass |
| Exactly one HOLDOUT document; no holdout quote appears in update contexts, in the PR #22 GitHub-derived library, or in the Google cases (and vice versa for update quotes in holdout contexts) | pass |
| Opt-in: `SOPHON_SLA_SOURCE_DIR=<dir with ms_sla_jul2021.docx, pillar.pdf>` re-verifies source SHA-256, the normalised-text hash, every context at its offsets, and quote uniqueness | **pass**, run on 2026-10-16 against the downloaded files |
| Adverse check: quote altered and split changed in a copy | the tests fail as expected |

## What is and is not demonstrated

**Demonstrated:**
- Two authentic, dated, publicly retrievable SLAs from new publishers.
- 12 source-verifiable decisions with balanced positives and negatives, covering four confusion types: exclusion vs prohibition, discretion vs duty, condition vs duty, and a definition with operative language.
- An explicit holdout with tested split separation.

**Not demonstrated:**
- That Jev errs on any of these decisions.
- That any label is legally correct. The labels are the implementing agent's engineering judgement, written before any query, with no independent legal review.
- Any library benefit.

**Limits on future error headroom, from existing recorded evidence.** In the completed PR #22 run, COLD Jev scored the Google exclusion excerpt B3c at PROHIBITION 0.07, so exclusion-vs-prohibition cases (MS3, OR2) may sit at ceiling. Clean "may not" and "will" cases are probably easy too. Of the 5 definitive holdout decisions, OR3 (discretion) and OR6 (condition) are the likeliest sources of genuine cold errors, and that is a hypothesis. The set is small: any later learning comparison on 5 holdout decisions can show only per-decision changes, never rates.

## Next step: requires new owner authorization (not started)

The original proposal was 24 calls (all 12 contexts twice). The engineering-lead review on PR #23 (2026-10-16) narrowed it, for two reasons. That proposal spent 10 calls on the Oracle holdout and 8 on unscored UNRESOLVED cases before anyone knew whether the update document has usable headroom. And holdout outcomes should not be seen before a library update exists.

**Narrowed screen.** MS1, MS2 and MS3 only, each sent twice, for **at most 6 Jev calls**.
- **Fixed inputs:** exact `jev-1.13.0`, failing closed rather than substituting another model; the identical `probe.py` question set; the recorded context; an empty library.
- **Recording:** labels frozen as committed; a new git-ignored recording path with request hashes; no retries.
- **Validate offline first.** No Oracle (holdout) and no UNRESOLVED context is sent.

**Pre-registered reading:**
- A definitive label contradicted in **both** repeats (YES with p < 0.5, or NO with p ≥ 0.5) is a **candidate classification disagreement**. It needs independent source-level adjudication and is not an established normative error. The labels are the implementer's unreviewed interpretation.
- A disagreement in only one of the two repeats is noise or instability, not a disagreement.
- **0 reproducible candidate disagreements → STOP** the learning experiment on this dataset. Do not query the Oracle holdout and do not add library templates.
- **≥1 → first decide whether its label is defensible.** Only then propose a separately approved, bounded library update with a sealed holdout design.

**Holdout discipline.** The Oracle texts and labels are already visible on this branch. Future library changes must never be tuned on Oracle outcomes, whether or not any exact quote overlaps.

The screen needs a small offline addition: a cold-only mode in `probe.py` limited to MS1–MS3. That code is not written here. PR #22's frozen evidence is not modified.
