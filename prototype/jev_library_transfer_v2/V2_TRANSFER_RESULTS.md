# JEV V2 library-transfer experiment — results (13 October 2026)

**Status: `READY_NOT_RUN`.** The offline implementation is complete and tested, the Google source and checklist are frozen, the A-derived library is induced from the owner's genuine GitHub recording, and the no-network preflight passes with the operator's local credentials. **No Google (Contract B) provider call has been made. No transfer result exists. This is not a PASS.**

Charter anchor: Sophon Charter v1.2 (PR #15) §5 **Stage 1 component feasibility** of an *upstream interpretation/learning subcomponent*. It is outside the BI-first compliance-checker wedge (§2, §4) and produces no TRANSPOSE/VERIFY evidence against any semantic layer. Task prompt: `Claude_Code_Sophon_JEV_V2_Provision_Library_Transfer_2026-10-13.md`.

## 1. OBSERVED / INFERRED / ASSUMED

**OBSERVED (this iteration, offline):**
- The owner's local V1 recording `prototype/jev_clause_router_v0/live_runs/live_EXT_20261013T094923Z.json` (sha256 `a562ccf87ba3…`, untracked, left untouched) contains **20 `ACTUAL_PROVIDER` responses** for G1–G5 (5 × Jev `jev-1.13.0`, 5 × adversarial, 5 × backward, 5 × blind, all `claude-opus-5-5`, effort medium, one HTTP attempt each). Its corpus hash equals the frozen GitHub corpus (`4023ee71…`). The LAB recording holds 20 more. The committed `V1_LIVE_RESULTS.md` (`BLOCKED_NO_LIVE_RUN`) is **stale**; the live run did happen.
- **V1 blind-baseline failure diagnosed** (`transfer.py --mode diagnose-v1`): G1, G2, G3 were rejected for one field-level cause — `evidence_quotes: expected list, got dict` (the model returned an object keyed by element, as the V1 prompt wording "supporting each element" invited). No quote was unanchored. G4 and G5 were valid. The LAB-corpus blind failures were not re-diagnosed here. V2 prompts state the array shape explicitly, validators report per-field errors, and an object-shaped `slots` field is normalized and **flagged** (`OBJECT_FORM_NORMALIZED`), never silently accepted; evidence anchors were not loosened.
- **Library induction ran on real A evidence** (`--mode induce`): 3 `DISCOVER`, 2 `ABSTAIN`, 0 `REFINE`. Templates: `TIERED_SERVICE_CREDIT_SCHEDULE` (G1), `AVAILABILITY_METRIC_DEFINITION` (G2), `CREDIT_CLAIM_AND_REMEDY_PROCEDURE` (G4). G3 abstained: the recorded reviewer quotes dropped the enumerators "(i)…(iv)", so the `SLA_EXCLUSION_LIST` signature was not met. G5 abstained by protocol. The recorded Jev order-sensitivity flag on G1 (`PERMISSION_RIGHT` vs reversed `DEFINITION`) was carried into the template as two acceptable category readings. `validate_library` accepted v1 (no vendor literals in general rules, no Contract B vocabulary, every learned template source-anchored and `PROVISIONAL`).
- **Contract B frozen**: `https://cloud.google.com/storage/sla-20210624`, HTTP 200, retrieved 2026-10-13T12:07:25Z, 711,725 bytes, page sha256 `e5b91991…0314`, page labelled "Last modified: June 24, 2021" and "not the current version". Three packets: B1 `c74f4c1f…` (metric definitions), B2 `72df1f0c…` (SLO tiers + three credit schedules), B3 `5fd249c7…` (claim, maximum, exclusions). Corpus digest `1c6795da…`. Checklist digest `7fa0bd30…` (36 material elements: 9 + 13 + 14), sealed from all prompts (tested).
- **Preflight** (`--mode preflight`, zero network): plan **30 logical calls** (9 Jev + 18 reviewer + 3 blind; 31 with `-LibrarySynthesis`), hard physical cap 93 HTTP attempts (≤3 per call), estimate ≈ **USD 0.82** for Claude at `claude-opus-5-5` list price using the recorded V1 mean of 1,246 output tokens per LLM call, plus ≈ USD 0.0008 for Jev. **The transport has no enforceable spend cap.** Inside this Claude Code session without keys in the process environment it reported only `NO_TYPESAFE_API_KEY` / `NO_ANTHROPIC_API_KEY`; the runbook's `-PreflightOnly` path, which loads the ignored repo-root `.env`, reported `ready: true` (no values printed, no calls).
- Tests: `test_v2.py` 29 passed; V1 suite 40 passed; V0 normative suite 6 passed. All transport is mocked; fixtures are `LAB_FIXTURE`.

**INFERRED:** nothing about transfer, accuracy or reviewer value. The pre-registered rule has not been applied to any observation.

**ASSUMED (to be checked by the live run):** that Jev accepts up to ten `choice` criteria of ≤400 characters each and a structured state with `prior_examples`; that `claude-opus-5-5` returns the typed `slots` array; that the mean output-token figure holds.

## 2. ACTUAL vs new provider calls

| Kind | Count |
|---|---:|
| Reused `ACTUAL_PROVIDER` GitHub responses verified (G1–G4 × jev/adversarial/backward/blind) | **16** (12 used for induction, 4 blind used only for diagnosis) |
| New Contract A calls | **0** |
| Contract B (Google) calls | **0** |
| Optional A-only synthesis call | **0** (not run; `-LibrarySynthesis` adds 1) |
| USD spent this iteration | **0** |

## 3. Frozen inputs and hashes

| Artifact | Digest (canonical JSON / file) |
|---|---|
| GitHub corpus `external_github_sla_2021.json` | `4023ee710fb3fc35…` |
| V1 recording `live_EXT_20261013T094923Z.json` | `a562ccf87ba3e7ac…` (local, ignored by V2 policy; V1 copy untracked and untouched) |
| Google corpus `google_storage_sla_20210624.json` | `1c6795da509be8ee…` |
| Checklist `reference_checklist_b.json` | `7fa0bd30310414ca…` |
| `library_v0.json` | `70f87607f44c388e…` |
| `library_v1.json` | `7501df1d2e041669…` |

Four-dimensional sidecars (`context_libraries/`): legal context for both documents is `REFERENCED_SOURCE_UNAVAILABLE` (both point to an unavailable master "Agreement"); forum and mandatory rules `UNKNOWN`; both documents `SERVICE_LEVEL_AGREEMENT` with anchored evidence; nine section records with verbatim headings, `UNNUMBERED` / `HEADING_ABSENT` where the source has none (Google's sub-headings are bold paragraphs, not HTML headings; its credit schedules sit inside the Definitions list, so that section carries two functions); seven provision records with inherited context, inherited definitions and cross-section references. `validate_context` passes; the negative tests reject invented headings, unsupported function labels, bad parents, wrong section-to-source links, lost inheritance, unanchored overrides, unsupported jurisdiction inference, law/forum conflation and domicile-as-law.

## 4. Per-slot B comparison

Not available: `COLD_B`, `WARM_LIBRARY_B`, `WARM_RAW_A_B` and `BLIND_LLM_B` are all **NOT_RUN** on B1–B3. `transfer.py --mode score` will produce the per-packet table (recovered/denominator, novel elements, wrong transfers with critical flag, unmatched reviewer challenges, unresolved references, holds, tokens, attempts, latency) and apply the pre-registered rule once a recording exists.

## 5. Library edit diff (v0 → v1)

- `+ TIERED_SERVICE_CREDIT_SCHEDULE` v1: required `calculation, condition, measurement_period, threshold`; optional `deadline, exception, source_reference`; readings `DEFINITION | PERMISSION_RIGHT`; positive example G1 (six anchored quotes); counterexamples G2, G3, G4.
- `+ AVAILABILITY_METRIC_DEFINITION` v1: required `exception, measurement_granularity, normative_action, required_fact, threshold, trigger`; positive example G2; counterexamples G1, G3, G4.
- `+ CREDIT_CLAIM_AND_REMEDY_PROCEDURE` v1: required `cap, claim_condition, deadline, measurement_period, remedy`; positive example G4; counterexamples G1, G2, G3.
- Six bootstrap templates unchanged. Every learned entry carries the recording sha256, packet hashes, model ids and reviewer-issue hashes as evidence; status `PROVISIONAL`.

Known inducer artefacts (disclosed, not fixed post hoc): lexical detectors over-fire (G2's "exceeds five percent (5%)" matched the band detector, adding a band rule to the metric template; "(b)" matched the enumerator detector); the "measurement period is required" rule appears in every learned template. The detector vocabulary and template signatures are **agent-authored code written after reading both documents**.

## 6. Known limitations and no-claims

- Not blind: one agent froze B, wrote the checklist and the inducer. The checklist author and the reviewers are Claude-family models.
- n = 3 packets; counts only. Both documents are vendor SLAs: no cross-family, section-taxonomy or jurisdiction transfer can be assessed.
- `HOLD_UNRESOLVED` and reviewer `SUPPORTED_WITH_GAPS` are not quality scores; validity, anchoring, recall, wrong transfer and holds are reported separately.
- No claim of legal correctness, applicability to any customer, BI integration, enforcement, or that any template is authoritative. Nothing is approved.
- `library_v1.json` records the absolute local path of the recording for traceability; it contains no secrets.

## 7. Next action (operator, new terminal outside Claude Code)

```powershell
cd C:\Claude\sophon\prototype\jev_library_transfer_v2
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic
```

The runbook validates offline, runs the preflight, prints the call plan and cost estimate, requires a typed `YES`, makes ≤30 logical calls (≤31 with `-LibrarySynthesis`), replays and scores offline, and writes `receipts_<stamp>.json`. Raw evidence stays in the ignored `live_runs/`. Then fill §4 with the scored table and the pre-registered verdict, and have a human adjudicate every recovered element before any accuracy claim.

**Biggest unresolved question:** whether Jev's `choice` over ten provisional template definitions produces a stable, non-order-sensitive selection on unseen text at all; if not, the comparison is about the reviewers' memory, not Jev's.

## Commands run in this iteration

| Command (in `prototype/jev_library_transfer_v2`) | Exit |
|---|---:|
| `python transfer.py --mode validate` | 0 |
| `python transfer.py --mode diagnose-v1` | 0 |
| `python transfer.py --mode induce` (first attempt rejected for B-vocabulary in two slot descriptions and one token shared with A; vocabulary corrected, re-run) | 2 → 0 |
| `python transfer.py --mode preflight` (no keys in session env) | 2 (credential blockers only) |
| `powershell -File .\RUNBOOK_V2_TRANSFER.ps1 -PreflightOnly` (loads ignored `.env`; zero network) | 0 (`ready: true`) |
| `python -m unittest test_v2` (29) / V1 suite (40) / V0 suite (6) | 0 |
