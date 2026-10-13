# Task prompt: independent human-adjudication package for the 8 V3 secondary heldout cases

**Date:** 13 October 2026. **Branch / PR:** `experiment/jev-v3-context-funnel-2026-10-13`, draft PR #17 (base before this task: `26902c6`).
**Requested by:** the owner, in a Claude Code cloud session. **Executed by:** Claude Code (agent). **Status of the result:** package prepared, `AWAITING_HUMAN_ADJUDICATION`. Original passages are blocked in the build session (see `REVIEW_PACKAGE.md` §0).

## Owner's instructions (verbatim)

> We need to close the outstanding V3 evidence gap before executing V4.
>
> Read Sophon Charter v1.2 from PR #15, the V3 protocol, RESULTS.md, and the latest V3 audit findings.
>
> Your task is to prepare an independent human-adjudication package for the 8 V3 secondary heldout cases.
>
> 1. Retrieve the original contractual evidence using the existing source manifest and recorded hashes.
>
> 2. Prepare a compact review table showing:
>    - Contract, section and source reference
>    - Original contractual passage
>    - Proposed section/provision classification
>    - Relevant predicted provision structures
>    - Supporting evidence and disputed classifications
>    - What the human reviewer needs to validate
>
> 3. Prioritize the 18 positive labels and all negative labels affecting the top-3 predictions. Identify separately which additional labels are necessary to validate the Brier scores.
>
> 4. Explicitly flag the segmentation, sparse-support, and misclassification problems identified in V3.
>
> 5. Do not adjudicate your own labels and present them as independently validated.
>
> 6. Save the task prompt and review package in the repository under prototype/contract_structure_prediction_v3/.
>
> 7. Commit and push the deliverables to PR #17.
>
> Do not modify the original frozen results. Do not start V4. Do not make paid API calls. Do not modify the charter. Do not merge any PR.
>
> If original evidence is unavailable, identify the exact blocker rather than inventing source passages.
>
> At completion, give me a concise summary and the exact file I need to review.

## Entry gate (CLAUDE.md)

1. **Charter section and stage.** The anchor is Charter v1.2 (draft PR #15, read via `git show origin/docs/normative-semantic-layer-charter-v1-2-2026-10-13:SOPHON_CHARTER.md`, unmodified). It sits under §3 VERIFY ("use independent oracles and counterexamples where correctness is claimed") and §3 AUDIT (keep proposed, agent-authored and validated states distinct). This is **Stage 1 component feasibility** evidence hygiene for an upstream TRANSPOSE input (the structural prior). It is not a product, BI or adoption test.
   - *Discrepancy carried forward, unresolved:* this branch's `SOPHON_CHARTER.md` and `CLAUDE.md` are still v1.1. This task follows the owner's explicit instruction to read v1.2 and changes neither file.
2. **Smallest uncertainty.** Are the 18 hidden-positive labels, and the 275 absence labels behind V3's post-freeze secondary result (`PREDICTIVE_SIGNAL_PROVISIONAL`), correct? All of them are `PROVISIONAL_AGENT_AUTHORED`.
3. **Sources and semantic layer.** Four genuine public documents: CA-MARKEL and CA-OLDDOMINION (SEC EDGAR exhibits), and SLA-CLOUDFLARE and SLA-MONGODB (current vendor pages at retrieval). No semantic layer or BI system is involved. Not proved: label correctness (pending a human), interpretation accuracy, and anything about Jev or BI.
4. **Architecture fit.** The package separates agent proposal from human validation and keeps every artifact reproducible from committed hashes, which is the charter's AUDIT discipline. It changes no predictor, rule or frozen result.
5. **Prior results built on.** V3 `RESULTS.md`: primary `INCONCLUSIVE`, secondary `PREDICTIVE_SIGNAL_PROVISIONAL`, limited to provision-within-section ranking, with no human labels. The post-run audit found the split was not chronological, training support was effectively 3 drafting styles, and the signal is concentrated in two conventional cases. These contrary findings are carried into the package, not erased.

## What was done (and not done)

- **Done.** `build_review_package.py` generated `REVIEW_PACKAGE.md`, `review_units.csv` (78 units to label), `review_labels.csv` (derived tiers) and `package_manifest.json`, offline, from committed files and the frozen `labels.py` and `predict.py`.
- **Done.** `fetch_local_evidence.py` was written for operator-run retrieval with SHA-256 verification and a structure-identity check. It was tested on synthetic fixtures only.
- **Done.** Offline tests: `test_adjudication.py` (10) and the existing `test_v3.py` (14).
- **Not done: source retrieval.** It is blocked in this session: `CONNECT tunnel failed, response 403` for `www.sec.gov`, `www.cloudflare.com` and `www.mongodb.com` (environment network policy, last checked 2026-10-13T16:30:29Z). No passage was invented or paraphrased.
- **Not done, by instruction:**
  - adjudication by the agent;
  - edits to `../results`, `../data` or `../frozen`;
  - V4;
  - provider calls;
  - charter edits;
  - merges.
