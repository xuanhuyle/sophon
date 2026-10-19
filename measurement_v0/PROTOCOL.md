# Measurement V0 — frozen protocol (Task 010)

**Frozen:** 2026-10-19, committed **before** any scored baseline run. Changes after this commit are protocol deviations and must be listed in RESULTS.md.
**Charter scope:** v1.2 VERIFY/TRACE, §5 Stage 2 *measurement-method setup* only. Not a reliability result, not a Sophon-vs-baseline comparison, no Sophon arm.
**Surface label:** **NON-BI EXPLORATORY EVIDENCE.** The implementation is an independently authored open-source rules-as-code policy engine, not a BI semantic layer. This corresponds to the charter's direct non-BI path, not the BI wedge.
**E0–E5:** not used as dataset, oracle, baseline or reference code. Nothing in this directory derives from Sophon code or LAB_AUTHORED sources.

## 1. Candidate search (bounded, ~60 min of the 90-min budget)

| # | Candidate | Governing source | Implementation | Disposition |
|---|---|---|---|---|
| C1 | PolicyEngine-US SNAP allotment rounding | 7 CFR 273.10(e) (CFR 2025 ed., public domain) + 7 U.S.C. 2017(a) (USC 2024 ed.) — the statute is the implementation's own cited `reference` | `policyengine_us/variables/gov/usda/snap/snap_expected_contribution.py` → `snap_normal_allotment.py` → `snap`; AGPL-3.0 OSS | **SELECTED** (gate below) |
| C2 | GitLab public analytics dbt project vs public GitLab Handbook metric definitions (genuine BI semantic case) | GitLab Handbook | `gitlab-data/analytics` dbt models | **REJECTED — BLOCKED_RUNTIME/ACCESS:** no warehouse data to run native semantics; `git ls-remote https://gitlab.com/gitlab-data/analytics.git` from this environment fails (credential prompt); handbook version ↔ model binding not pinnable in the timebox |
| C3 | PolicyEngine-US NY child tax credit surviving-spouse phase-out threshold (fix `d8f06f394c`, 2026-09-10) | NY Tax Law §606(c-1)(1-a)(C) as enacted in S.3009-C | NY CTC parameter YAML | **REJECTED — oracle needs legislative-history fact** (which bill print was enacted) that we can only corroborate via secondary form instructions; also parameter-lookup only, weak as a governance-meaning test |

No BI candidate passed; we did not fabricate one.

## 2. Eligibility gate for C1 — evidence

- **Independent authorship / predates task:** regulation (federal); implementation formula `np.floor(snap_net_income) * 0.3` present since at least 2022-10-13 (`6b3ce4bc91`, rename commit) and unchanged until 2026-08-19; PolicyEngine maintainers fixed it in PR #9318 (merge `5d88007d90`, 2026-08-25, "Fixes #9312"). All authored outside Sophon and before this task (2026-10-19).
- **Pinned sources** (copied in `evidence/sources/`, public-domain U.S. government works):
  - `CFR-2025-title7-vol4-sec273-10.xml` sha256 `614a2334b335d953df58323e2728c61eb328fc811ba8d887494f798072659b76` — https://www.govinfo.gov/content/pkg/CFR-2025-title7-vol4/xml/CFR-2025-title7-vol4-sec273-10.xml
  - `CFR-2024-title7-vol4-sec273-10.xml` sha256 `a6f5916cc00d079ee9b7d9627c27128e5d716b7faace3be78e1e479967c92c75` (text of (e)(1)(ii) and (e)(2)(ii)(A) verified identical to 2025 ed.)
  - `USCODE-2024-title7-chap51-sec2017.htm` sha256 `6e06aad1a1c3d64df1f01bb90b1a71416ca8ac774dec86c80447879ed396467b`
  - The CFR 2026 edition was not available on govinfo; eCFR returned HTTP 403. **Amendment of the paragraph between 2025-01-01 and 2026-01 is UNVERIFIED** (residual risk; no known amendment).
- **Implementation revisions:** PRE = `5152b5f7c325717d84a0b67955594a4b12752dde` (main immediately before merging #9318; 2026-08-25 18:45 UTC; version 1.821.0). POST = `5d88007d90b8a8b77987e319875a43bfd6c8d17f` (merge of #9318). Repo https://github.com/PolicyEngine/policyengine-us.
- **Traceable binding (documented, not name-based):** `snap_expected_contribution.reference` and `snap.reference` = 7 U.S.C. 2017(a); `snap_normal_allotment = max(min_allotment, snap_max_allotment − snap_expected_contribution)`; `snap` adds `snap_if_takes_up`.
- **Governing requirement R1** (7 CFR 273.10(e)(2)(ii)(A)): allotment = maximum allotment − 30% of net income; if 30% of net income ends in cents the State shall either (1) round the 30% **up** to the next dollar, or (2) not round it and round the **allotment down** to the lower dollar. 7 U.S.C. 2017(a): "…reduced by an amount equal to 30 per centum of the household's income … rounded to the nearest lower whole dollar". For a whole-dollar maximum allotment M the two State options are arithmetically identical: `floor(M − 0.3N) = M − ceil(0.3N)`. **R1 therefore needs no State-option knowledge.**
- **Explicitly UNKNOWN / out of scope:** net-income rounding (273.10(e)(1)(ii): State chooses half-up rounding or its TANF procedure — Texas's choice is not established here); M's dollar value (taken from the model; FNS FY2026 table page was not machine-retrievable); initial-month proration and the <$10 rule; minimum benefit (applies to 1–2 person households only).
- **Legal conclusion needed?** No: R1 is arithmetic stated directly in the regulation and statute; no Texas-specific or adjudicative fact is required.

## 3. Frozen reference (oracle) — derived from the source + reproducible native behaviour

Instrument: `reference_check.py` (runs the native PolicyEngine model; compares `snap` with `M − ceil(3N/10)`). Inputs frozen: Texas, household of 3 (adult 35, two children 10), period `2026-01`, `snap_net_income` set directly to whole-dollar N ∈ {501, 1000, 1234, 1391, 1999} (1000 is a zero-cents control). Runtime: Python 3.13.16, lockfile versions (`evidence/runtime_pip_freeze.txt`).

Observed before freezing (`evidence/reference_pre.json`, `evidence/reference_post.json`, each exit 0, ~34 s):

| N | reference (M=785) | PRE `snap` | POST `snap` |
|---|---|---|---|
| 501 | 634 | 634.70 ✗ | 634 ✓ |
| 1000 | 485 | 485.00 ✓ | 485 ✓ |
| 1234 | 414 | 414.80 ✗ | 414 ✓ |
| 1391 | 367 | 367.70 ✗ | 367 ✓ |
| 1999 | 185 | 185.30 ✗ | 185 ✓ |

**Frozen expected outcome:** PRE does **not** conform to R1 (target answer: `DETECTED_MISMATCH`). POST conforms to R1 (target answer: `CORRECT_ALIGNMENT`). The instrument both rejects (PRE) and accepts (POST) — an instrument sensitivity check using two naturally occurring revisions, not an artificial fixture.

The oracle is the regulation/statute arithmetic plus native execution. The upstream fix is corroborating chronology only; it was AI co-authored, so it is **not** treated as independent ground truth.

## 4. Baseline arm (conventional, no Sophon)

- Two **fresh Claude Code cloud sessions**, created with **no repository attached** (no Sophon code, notes, PROJECT_STATE, oracle or this protocol on their filesystem), model inherited from the orchestrating session (recorded in RESULTS). Full transcripts retrievable via the session event log — the audit trail.
- `baseline-A` reviews PRE (**primary scored observation**, a naturally occurring historical defect). `baseline-B` reviews POST (**paired natural hard-negative observation**, guards against an always-flag-a-mismatch strategy). Opaque labels; each run sees one revision only.
- Prompt: `BASELINE_PROMPT.md`, verbatim. The baseline receives the same source, system and scope a future Sophon arm would receive: pinned regulation + statute, full checkout with git history up to the pinned commit (depth 500), native runtime, tests, and its own knowledge. No hint of rounding, no oracle, no hidden defect description. Not handicapped to a single command.
- Leakage controls: the fix (Aug 2026) post-dates the model's training cutoff (June 2026); post-commit PolicyEngine history and web search are forbidden by instruction (not technically enforced) and **audited in the transcript**.

## 5. Recorded per run

Session id, model, start/end wall time, all commands with exit codes and outputs (from the transcript), the final JSON report verbatim, protocol violations.

## 6. Scorer (frozen: `scorer.py`; controls in `evidence/scorer_controls/`)

A finding addresses R1 iff it cites 273.10(e)(2)(ii) or 2017(a) and describes rounding of the 30%/contribution/allotment. The mechanical match is confirmed by reading; disagreement is reported.

| Run | R1 finding verdict | Outcome | Score |
|---|---|---|---|
| A (PRE) | DOES_NOT_CONFORM | DETECTED_MISMATCH | BASELINE_CORRECT |
| A (PRE) | CONFORMS, or R1 never raised | INCORRECT_ASSURANCE (by assertion or omission) | BASELINE_MISS |
| A/B | CANNOT_DETERMINE / STATE_OPTION_DEPENDENT, or no R1 and overall CANNOT_DETERMINE | ABSTAIN_UNOBSERVABLE | BASELINE_ABSTAIN |
| B (POST) | DOES_NOT_CONFORM | FALSE_ALARM | BASELINE_MISS |
| B (POST) | CONFORMS or not raised (with no R1 mismatch) | CORRECT_ALIGNMENT | BASELINE_CORRECT |
| any | no parseable JSON, run failure, or audited protocol violation (post-commit PolicyEngine history / web search) | INCONCLUSIVE | INCONCLUSIVE |

Non-R1 findings are adjudicated **separately** against the pinned text as VALID / STATE_OPTION_UNKNOWN / FALSE_ALARM / OUT_OF_SCOPE and reported apart from the R1 score (formatting failures, semantic errors, abstentions reported as separate quantities).

**Scorer negative/positive controls** (synthetic reports, run before scoring, clearly *not* observations): `evidence/scorer_controls/controls_result.txt` — 6/6 pass, including rejection of a wrong assurance on PRE, of a false alarm on POST, and refusal to credit a net-income-only finding as R1.

## 7. Stop rules

- If a baseline session cannot run (environment/network), record `BLOCKED_RUNTIME` for that run; do not invent output. No retries with an altered prompt; at most one re-launch with the identical prompt for an infrastructure failure, disclosed.
- No change to R1, the oracle, inputs or scorer after the baseline runs start. No post-hoc oracle repair.
- After scoring: write SCORECARD/RESULTS/DECISION, open one draft PR, STOP. No Sophon arm, no E6, no second case.

## 8. Known selection bias

The case was found by searching PolicyEngine history for fix commits citing regulations, i.e., it is a defect that the maintainers' own conventional workflow (issue → AI-assisted fix → review) eventually caught. It is a single, arithmetic, single-paragraph requirement — easier than typical contractual meaning — and the regulation is well known to LLMs. A single observation is not a rate.
