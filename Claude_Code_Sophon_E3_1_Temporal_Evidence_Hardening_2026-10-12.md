# Claude Code — Sophon E3.1: Temporal Applicability & Independent Evidence Re-execution

**Date:** 12 October 2026
**Authorization:** Execute **E3.1 ONLY**, then STOP. E4 must be separately authorized/executed after review of this result.
**Governing:** `SOPHON_CHARTER.md` v1.1, `CLAUDE.md`, `AGENTS.md`, `SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md`.
**Starting point:** E3 PR #8 (`experiment/e3-governance-ir-2026-10-12`, head initially `5130518f2fa86281a8cd615bf7135d1dce5058e1`, check live). E0 PR #4 / E1 #5 / E2 #6 / erratum #7 remain historical dependencies, not new work.
**Scope:** Correct two concrete post-scoring defects in E3, with original E3 evidence immutable. Do NOT build an event store, proprietary language, compiler, generalized security system, amended legal interpretation, or E4.

## 0. Why we are doing this and what we are NOT proving

E3's frozen score **PASS_IR_GUARD_VALUE** is valid for its preregistered 54 cases, but post-hoc diagnostics in `experiments/E3_formal_ir/evidence/diagnostics_nonscored.json` disclose two consequential gaps:

1. A governing requirement whose `effective_from` is in the future (relative to `eval_effective_at`) may still become `VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS`. E3 checks date-order consistency but not **actual applicability at the target effective date**.
2. E3's validator trusts stored native receipts and stored oracle receipts. If an adversary **rewrites both consistently**, the validator accepts their self-consistent fiction (the E3 diagnostic records a forged `VERIFIED`). Replaying stored bytes does NOT independently establish authenticity.

E3.1 must show **(a)** temporal applicability is enforced orthogonally to when the organization learned the governing source/approval, and **(b)** each promoted result is checked against **fresh native MetricFlow execution and an independent raw-data calculation**, anchored to trusted upstream and source revisions **outside the untrusted candidate receipts**.

This is **engineering integrity under an explicitly bounded trust model**, NOT tamper-proof evidence or a security proof. A compromised verifier, reference code, trusted raw source, source pin, or trusted policy registry can still defeat the system. Do not imply cryptographic signing, production identity verification, legal approval, complete payment provenance or enterprise correctness.

## 1. Read and preserve the historical record

Read in full `origin/main:SOPHON_CHARTER.md`, `CLAUDE.md`, `AGENTS.md`, engineering plan and this prompt using `git show` after `git fetch origin`. Read the original E3 `PRIOR.md`, `PROTOCOL.md`, `RESULTS.md`, `DECISION.md`, `README.md`, `src/{validator,models,run_scenarios,collect_evidence,replay}.py`, the four records, approval/roster and registry fixtures, `evidence/diagnostics_nonscored.json`, and evidence for the three positive scenarios. Review the E1 erratum's guards, and E0/E2 independent-oracle definitions as needed. Inspect PR status and local `git status` / worktrees; preserve user changes and never merge.

**Important:** The 54/54 score and post-hoc diagnostics remain intact. **Do not edit any file within E0, E1, E2, E1 erratum, or E3 directories.** E3.1 builds a versioned *new* validator/wrapper within `experiments/E3_1_integrity/` which imports or deliberately minimally forks E3 code, records exact reason and hashes, and compares old behavior with corrected behavior. Avoid a sweeping rewrite or silently presenting E3.1's results as the original E3 score.

Worktree/PR:
- Fetch current remote and verify PR #8. If it remains unmerged, create isolated worktree/branch `experiment/e3-1-integrity-2026-10-12` starting at `origin/experiment/e3-governance-ir-2026-10-12`, then open a **draft stacked PR** whose base is E3's branch.
- If PR #8 has merged, branch from the actual commit containing E3 and document the alternate topology. Never base an implementation branch directly on `main` when prerequisite experiment files are absent.
- Reuse upstream `behramkorkut/Governed-Analytics-Agent` pinned at `312e97ad192dcef02f688e31edc0a08c6cf4345f`, E0 locked Python/dbt/MetricFlow environment and build instructions; no modification to authoritative source code, previous results, or source data except disposable controls.

## 2. Freeze protocol and reproductions BEFORE implementing fixes

Within `experiments/E3_1_integrity/` commit and push `PRIOR.md`, `PROTOCOL.md`, small `CASES.json` or `EXPECTED.json`, trusted-source manifest, minimal reproduction scripts/test vectors, and scorer/acceptance criteria **before writing the corrected validator or scoring E3.1**.

Reproduce and **record the two old failures** with unmodified E3 validator:
- **F-TIME**: an approved S2 lab requirement with a requirement start date AFTER the effective evaluation date, but with source observed and approval known; the E3 old validator returns VERIFIED. Preserve the exact original configuration and old output, making clear this is retrospective verification of the reported flaw.
- **F-FORGE**: on approved S2 customer-country reading, replace both stored native rows and expected-oracle rows with a **matching but wrong plausible result** (e.g., store-country result), recompute their internal hashes, preserve the same claimed query/semantic/source identities, and show old E3 validation still VERIFIED. Ensure the forged pair actually differs from the correct trusted row oracle and that no successful native query for that selected reading produced the forged number. Run in memory/disposable files only, never corrupt E3 receipts.

If a reproduction cannot match the reported defect, STOP, record the contrary observation and apply no speculative fix. Protocol may be frozen after recording the preexisting failures but **before implementation of correction**. Preserve controls' actual outputs and exact versions.

## 3. Temporal applicability rules, not just well-formed dates

Retain separate axes:
- `eval_known_at`: what source versions and approvals were actually known by this time.
- `eval_effective_at`: what governing rule is applicable to the business data at this date.

For an otherwise well-formed, known and authorized requirement:
- **Before `effective_from`**, return distinct `REQUIREMENT_NOT_IN_FORCE` (or `NOT_APPLICABLE_AT_EFFECTIVE_DATE`) and NEVER VERIFIED, regardless of successful native calculation or in-window approval.
- **At `effective_from`**, applicability starts inclusively.
- **At `effective_to`**, applicability remains in force inclusively; **after it**, not applicable.
- **Null `effective_to`** means no declared end.
- Distinguish "source/approval not yet known at knowledge-time" from "requirement not in force at effective-time." No future-known approvals/source may be used for past-as-known queries.
- A retroactively effective governing rule, observed later, may be applicable at the older effective-time **as evaluated at a later knowledge-time**, if the legitimate source/version and approvals support it. At an earlier knowledge-time it cannot be claimed known. Use separate timelines rather than comparing observed date to effective date incorrectly.
- A missing approval must remain unapproved even when requirement is applicable. Conversely a perfectly approved requirement must not become verified when the requirement itself is out of force.
- Structural/source-hash corruption must not be disguised as harmless NOT_APPLICABLE. Document status precedence relative to INVALID/MEANING_UNRESOLVED/MISSING_FACT and test it.
- Do not invent automatic supersession or choose between conflicting governing documents; if outside scope, label it OUT_OF_SCOPE, not verified.

Prefer a thin adapter around E3's pure validator or a minimal versioned fork if there is no safe insertion point. Record exactly what was changed; no generic bitemporal database.

## 4. Evidence trust boundary: **fresh execution** versus self-consistent receipts

Original E3 `src/replay.py` is a **consistency replay**, not an independent verification. E3.1 must distinguish these and stop treating them as equivalent.

**Trusted inputs for THIS LAB experiment**, explicitly whitelisted/pinned before checking proposed receipts:
- the pinned upstream commit and expected source definitions;
- independently identified and hashed raw CSV data from the E0 reproducible generator; E0/E2 raw-data oracle code (or an independently written equivalent) under explicit verifier control;
- the canonical approved E3 IR record, clause/source hash, selected reading and lab approvals as simulated test fixtures;
- **freshly observed** native MetricFlow catalog/manifest and warehouse identity generated from those pinned sources.
Do not pull the trusted oracle value, trusted query, or trusted source hashes *from the candidate receipt whose truth is in dispute*. Freeze a manifest of independent trusted references in E3.1.

For each candidate **promoted** case:
1. Check source hash/version, selected approved reading, date applicability, full coverage and required derivation guards on the **same actual data snapshot**.
2. In a new verifier process, reconstruct/build a clean warehouse from the trusted pinned raw source **or otherwise demonstrably anchor it to the trusted source snapshot outside the candidate receipt**. Declare exactly where trust resides.
3. Derive the expected behavior from **the approved lab clause/reading**, independently from the candidate implementation and its recorded oracle. Execute the reference computation from original raw CSVs (standard library/Decimal as appropriate).
4. Execute the **actual native MetricFlow** query on the expected implementation/semantic revision and snapshot, record CLI identity/exit, compiled SQL or a query reference where available, actual rows, source fingerprints, semantic manifest fingerprint and run ID. Do not replace native execution with SQL-only code or replayed mf stdout.
5. Compare **fresh** native rows with **fresh** reference rows, validate version/binding/guard scope and explicitly refuse candidate receipts that differ from the independently computed actual outputs. A rehashed, self-consistent forged pair must fail.
6. Produce machine-readable separate states: technically executable / approved lab meaning / applicable at the effective date / independent re-execution succeeded / reference agreement / **bounded** verification, including what remains trusted or unresolved.
7. On unavailable runtime, absent independent source, mismatched revision, unknown source provenance or failed guard: **NOT_VERIFIED / INCONCLUSIVE with reasons**, never cached success.

**Critical distinction:** Independent recomputation on pinned raw data checks the **specific lab business formula**, not whether the underlying source itself is genuine, or whether hypothetical approvals really came from a person. An attacker able to replace *all* trusted inputs, code and manifests is outside this threat model. State this plainly.

## 5. Small frozen test matrix

Use **one pinned synthetic estate, E3 S1/S2/S3 plus negative S4**, and no new clauses. Freeze exact expected outcomes before corrected code.

**Temporal (minimum eight):**
T1 start in future vs evaluation-effective date → NOT_APPLICABLE; T2 effective start boundary → applicable; T3 effective end boundary → applicable; T4 after end → NOT_APPLICABLE; T5 source discovered after `eval_known_at` → not available/invalid, not verified; T6 approval known later than `eval_known_at` → unresolved; T7 retroactive rule observed later, as-known before/after separated; T8 approval in force but source not in force → NOT_APPLICABLE. Include a sourced-but-unauthorized record to ensure it stays MEANING_UNRESOLVED rather than being promoted. Use explicit UTC and inclusive-date semantics.

**Evidence (minimum eight):**
V1 clean approved S1 (derived) passes, fresh native = independent oracle + guards; V2 clean approved S2 customer reading passes; V3 clean S3 with simulated semantic-equivalence approval passes, still labelled LAB_SIMULATED; V4 S4 payment missing remains missing despite running status proxy; V5 forged matching native+oracle receipt pair **rejected**, although old E3 accepted; V6 single tampered native receipt rejected; V7 stale/wrong semantic version or source/raw data hash rejected; V8 missing/stale native runtime or independent oracle → no promotion; plus negative-quantity S1 controls so a guard failure still blocks even if recorded amounts match.

**Anti-vacuity:** For V5, include one case where forged pair is internally consistent and points to a **plausible wrong business reading**, not a malformed file. Verify fresh native query for approved customer reading gives customer result, not the forged store reading. Do not allow "check both receipt hashes" to count as passing this control.

**Security boundary:** A separately documented diagnostic showing that an adversary who controls *all* trusted anchors or verifier code can defeat the check is acceptable; no requirement to invent signing or attestation.

## 6. Decision gate — EXACTLY one

- **PASS_INTEGRITY_HARDENING:** F-TIME and F-FORGE reproduced on unmodified E3; all frozen temporal and evidence tests pass after corrected code; zero inapplicable, unknown-at-time, forged, wrong-version, missing-source or guard-failed cases promoted; clean positives still pass using fresh native and independent raw-data execution; independent fresh-process rerun reproduces results; original E3 unchanged.
- **PARTIAL_INTEGRITY_HARDENING:** some properties corrected but no false VERIFIED in scored new tests; name missing coverage and the smallest remaining gap. A failed clean-positive verification from broken tooling cannot be presented as a full PASS.
- **FAIL_UNSAFE_INTEGRITY:** any outside-effective-window, source-unknown, forged-candidate-receipt, failed guard, missing-source, unapproved interpretation or incorrect fresh result becomes VERIFIED.
- **BLOCKED:** pinned native runtime or independent raw-data oracle cannot be run under one bounded repair attempt; or pre-fix defects cannot be reproduced and the correction cannot be properly grounded.
- **INCONCLUSIVE:** source anchors, reference independence or preregistration integrity compromised.

**Make no general tamper-proof/security claim.** PASS means only that the frozen attacks, under the frozen trust boundary, are detected.

## 7. Deliverables, limits, PR

Create under `experiments/E3_1_integrity/`:
- `PRIOR.md`, `PROTOCOL.md`, `EXPECTED.json`, hashes/freeze commits.
- `src/`: minimal versioned applicability check and fresh verifier (reuse existing E3 parser/validator where possible), independently anchored oracle wrapper and small runner/replay.
- `tests/`: adversarial/positive boundary tests, including actual native execution and negative controls.
- `evidence/`: **original E3 failure reproductions**, executable commands/receipts, native fresh results, independent raw data results, candidate-forgery controls, scenario results, fresh-process replay and trust-boundary statement.
- `RESULTS.md`, `DECISION.md`, `README.md` (actual commands; PowerShell instructions labelled UNTESTED unless executed).

Protocol/expected files committed and pushed before new corrected logic is used; don't change frozen controls/gates after seeing results. Preserve first failures, corrections and reruns. Limit to a small versioned wrapper/fork; no broad architecture change, no paid AI API, no legal source interpretation, no simulated customer evidence. Avoid huge evidence blobs/duplicated upstream trees in Git.

Open **draft PR stacked on E3 branch** while PR #8 unmerged. Do not merge. Explicitly describe what E3 originally got wrong and how E3.1 addresses it without rewriting its PASS/diagnostics.

Final user report: branch/base/PR, protocol and final commits, T/V test outcomes, old false-positive reproduction, whether new checker blocks it, native/oracle independently reproduced values, exact verdict, trust boundaries, and single next experiment (**E4 only if E3.1 passes**).

**STOP AFTER E3.1. A trusted, repeatable check is the objective—not a proprietary programming language or a general security platform.**
