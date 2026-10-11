# Sophon — Experiment G1: A complete governed transition through an existing semantic layer

**Created:** 12 October 2026
**Owner intent:** Implement and falsify the smallest end-to-end instance of Sophon's infrastructure *and its core customer outcome*, without pretending that a lab workflow demonstrates market demand.
**Charter:** SOPHON_CHARTER.md v1.1, especially §§2–5A.
**Supersedes for the next task:** the earlier draft at Claude_Code_Sophon_Semantic_Layer_Boundary_Test_2026-10-11.md. Keep that historical prompt intact.
**Experiment type:** Engineering feasibility / end-to-end workflow, NOT a smarter-LLM benchmark, commercial pilot, or novel-kernel hunt.

## 0. The question, success definition, and guardrails

Can a minimal Sophon service take **one governed change** from an independently maintained governing requirement, through a customer's **actual existing executable semantic layer**, to a controlled, data-backed and persistent outcome that an auditor can reconstruct without the originating LLM session?

The resulting demonstration must show these four distinct capabilities, as ONE workflow:

1. **TRANSPOSE** a governing amendment to a proposed edit to an existing semantic definition. Do not replace the existing semantic stack.
2. **TRACE** source, interpretation, revision, owner decision, implementation and verification across change episodes and fresh processes.
3. **VERIFY** data-backed semantics when governance changes AND when semantic code changes independently. Detect harmless changes and honest unknowns.
4. **AUDIT** the state **as known at** a specified time AND **effective at** a specified date, with independent replay and evidence available even after the original model/session disappears.

**The objective is a governed transition, not a feature checklist**: a complete record must result in one of "sandbox implementation verified for specified checks", "correctly unchanged", "unresolved/rejected" or "blocked". Do not claim production deployment or legal compliance.

Sophon may use ordinary Git, SQLite, hashes, native dbt/MetricFlow tooling, a code-writing LLM and existing CI. Those are proper building blocks. **No Claude-vs-Sophon A/B test.** No claim that a capability unavailable to Databricks, Snowflake, dbt or a competent internal developer has been invented.

The **business outcome gap** (would customers prefer to buy this instead of implement with existing tools?) is NOT testable in this lab. Capture operational instrumentation to inform that later question, but do not report fictional customer ROI.

## 1. Mandatory reading and actual state of the repository

Before touching implementation, inspect and reference in a short PRIOR.md:

- SOPHON_CHARTER.md **v1.1**, CLAUDE.md, AGENTS.md, main README.md.
- Main branch: docs/REPORT.md, docs/DECISION.md, docs/OWNER_REQUEST.md. These describe the older agent authorization thesis and do not supersede the charter.
- PR #3 on origin/experiment/governance-integrity-2026-10-11: experiments/governance_integrity/{EVIDENCE_GATE.md,PROTOCOL.md,RESULTS.md,AUDIT_REPORT.md,DECISION.md}.
- PR #2 on origin/codex/alignment-review-agent: viability/RESULTS.md and viability/public_nyc/README.md.
- The October 11 execution prompt on main, **for historical context only**.

Record at least these facts accurately:
- PR #3 tested legal text → Publicodes executable rules, **not an analytics semantic layer**. Its store achieved 356/356 hash-linked entries and all 224 existing VERIFIED checks held on replay, but substantive M1/M2 outcomes and the audit were tied with Claude Code + normal notes/tools; B consumed more tokens. Its STOP_KERNEL verdict is about **incremental algorithm/tool performance in that bounded test**, not proof that persistent governance infrastructure is worthless.
- PR #3's preregistered sequence leaked 2026 texts into earlier 2025/2026 tasks through persistent workspaces. Symmetric exposure does not remove causal uncertainty. Its reference/scorer needed corrections and its as-of auditor retained all sealed original sources.
- PR #2 executed dbt/DuckDB with useful semantic findings and deterministic context invalidation, but did not use a real native MetricFlow lifecycle with an approved independent contract, a blinded reliability score or live vendor deployment.
- Neither PR established the end-to-end, governed transition through an existing executable BI semantic layer; neither established customer willingness to pay. Do **not** rewrite or rerun these studies.

No product-wide GO/NO-GO may be inferred from the prior STOP_KERNEL or from this experiment alone.

## 2. First gate: execute a genuine existing semantic layer

**One preferred upstream candidate (already source-inspected):**
https://github.com/behramkorkut/Governed-Analytics-Agent
Previously pinned by Sophon PR #3 at commit 312e97ad192dcef02f688e31edc0a08c6cf4345f. Its repository has:
- Native dbt/MetricFlow models and metrics: dbt/retail_dwh/models/marts/semantic/_semantic_models.yml and _metrics.yml.
- Sales metrics including completed_revenue, average_order_value, return_rate and gross_margin_rate.
- DuckDB warehouse, synthetic source-data generator, CI, and a dashboard/agent consumer.
- MIT license noted in upstream README (verify LICENSE in the pinned source).

Use **that exact commit** unless you document why it cannot be used and pin another audited commit. Verify actual definitions, origin, hash, dependency lock, CLI commands, native query behavior and MIT LICENSE; descriptions are not substitutes for execution.

Spend at most one controlled environment repair on setup. Follow upstream setup (prefer uv/Python 3.11, pinned lock, dbt build, parse). **Actually run a native MetricFlow query against underlying rows**, capturing dbt invocation, MetricFlow invocation, compiled SQL if available, output, manifests, environment and data fingerprints. Repeat a selected query to establish deterministic behavior. If the upstream "native" client resolves via its own wrapper, check it genuinely invokes MetricFlow rather than returning a precomputed fixture.

Check whether one *existing* downstream dashboard/agent consumes those catalog definitions; record what is actually evidenced. Do not build a new dashboard to simulate integration. Snowflake/Databricks live execution is **not** established by DuckDB.

**Gate status:**
- NATIVE_RUNTIME_PASS: real native semantic metrics query correctly executed on warehouse data; proceed.
- NATIVE_RUNTIME_BLOCKED: cannot execute after one focused repair; stop with exact log and avoid a substitute Publicodes or fabricated YAML/SQL "semantic" demo.

If the preferred upstream fails, one credible alternative with real native dbt MetricFlow (or a proven native semantic API) is allowed, subject to the same evidence gate; otherwise stop. Do NOT reselect Publicodes just because it has authentic legislation.

### Governing authority: deliberately honest

This upstream is a **retail portfolio dataset with synthetic data**, not an authentic enterprise and not known to have approved contracts or policy amendments.

For this experiment use ONE compact **LAB_AUTHORED business agreement/metric-definition policy**, with V1 and a later amendment V2. This is engineering evidence only. Do not manufacture signed agreements, claim real legal compliance, or confuse fictitious sign-off with an actual customer approval.

Choose a consequential but simple distinction on an existing metric (for example eligibility for completed_revenue by status/effective date, or a return-rate definition) that can be verified with the actual data and native MetricFlow query. Pick it based on observed source rows and semantic capabilities, not on a known expected score. Make it possible to leave at least one existing unrelated metric unchanged.

The lab policy must be a **separate document**, not a definition copied from semantic YAML and presented as independent business authority. Its original content, V2 delta, provenance and "LAB_AUTHORED" classification must be inspectable. Include at least one ambiguous or outside-semantic-scope clause to show a truthful limit.

## 3. Pre-register the complete workflow BEFORE coding Sophon

Save in experiments/governed_transition_g1/:
- PRIOR.md and SOURCE_GATE.md (actual native runtime and authority classification).
- PROTOCOL.md, FROZEN_CASES.json, TIMELINE.json and SHA256 manifest.
- A small seeded oracle and the commands/tests that prove its **pass**, **fail** and **not-enough-information** paths work.
- Dates as distinct publication/observed, effective and simulated approval times.

**Freeze protocol, test criteria, policy V1/V2, expected semantic behavior, data sample/fingerprints, and the oracle in a Git commit before implementing the governance service or viewing its outcomes.** Record that protocol commit. Preserve any later correction as a labelled amendment with the original scores/logs intact.

For the LAB timeline: strictly advance simulated observation time from V1 to V2 to independent code change. V2 may have a retroactive *effective* date: a bitemporal query before its observed time must never see it as known. Use deterministic checks over all persisted states and stage inputs. **Do not claim a blind historical test:** the designer knows its synthetic future scenarios. If using separate model contexts, prevent future files/notes from entering an earlier staged context; a mechanical staged-file allowlist must reject them. Future knowledge inside the orchestrator is disclosed, not described as absent.

Use independently executable SQL/row-level arithmetic as a cross-check for the reference expected metric result, not merely the LLM-generated metric query. The same overall research process may author both lab policy and oracle; label this limitation. Keep the recorded verification scripts separate from the Sophon implementation and test that they reject a deliberately wrong metric.

The experiment may test *mechanical correctness of governance plumbing*. It cannot estimate real-world interpretation accuracy from a case whose policy and expected results were created by the same lab.

## 4. Minimum working infrastructure and event sequence

Implement the smallest durable component (Python standard library/SQLite or equivalent; conventional Git/versioned documents; no DSL, graph database, giant agent framework, web UI, orchestrator or fake microservices).

The service should connect **actual existing semantic identities** (not just filename strings) to precise authority clauses and versions. Use source hashes, code revision, native query and result receipts, meaningful disposition/owner fields, and an explicit trust boundary for integrity anchors. A hash proves identity, not correctness or approval. Snapshot original evidence or retain genuinely immutable retrievable versions; a list of hashes with missing source text is insufficient.

**Stage A — Initial baseline and authorization boundaries**
- Ingest V1 LAB policy. Its status is PROPOSED until a **simulated** policy-owner approval event is recorded by the lab harness. Preserve the difference between authorship, interpretation, authority and approval.
- Map its requirement to one or two actual native semantic objects and provide an explicit list of related objects whose impact remains UNKNOWN.
- Execute V1 native MetricFlow query on real generated warehouse data, preserve semantic file revision, test output, warehouse fingerprint and bitemporal state.
- Record one expected OUT_OF_SCOPE clause as not verified, even when other calculations pass.

**Stage B — Forward amendment and controlled transposition**
- Introduce V2 at a later observation time; perhaps retroactively effective.
- Automatically mark only genuinely dependent verifications STALE/REVIEW_REQUIRED; unaffected ones must not be falsely considered violations.
- Before policy-owner approval, only propose a semantic code/configuration patch on a disposable branch. An LLM may propose it, but it may not self-authorize.
- Record a simulated policy-owner review and simulated data-owner review as two **separate, explicitly simulated** approval events with principal, role, provenance and time. Reject an unauthorized or missing approval in an adversarial test.
- Apply the patch only in a disposable copy, use native dbt/MetricFlow validation and re-query actual rows. Differentiate "sandbox implemented and checked" from "approved/verified in production".
- Show a coherent, auditable transition from old requirement and metric value to new, with any unresolved policy ambiguity remaining unresolved.

**Stage C — Reverse-change monitoring**
- Independently modify the **actual semantic definition** in the disposable upstream copy in a way that violates V2 meaning but still parses and returns a plausible metric. The underlying data stay fingerprinted. Sophon must detect the relevant changed object and produce an evidence-backed review/failure, not just report a changed hash.
- Also perform one harmless/equivalent description/refactor change or one unaffected metric modification. No fabricated compliance violation and no blanket "everything changed".
- Distinguish implementation discrepancy from data quality, missing rule evidence and out-of-scope action.

**Stage D — Context loss and audit**
- Terminate the initial execution/session. Start a **separate clean process**, and preferably a fresh model context with *only committed/snapshotted evidence, not the initial chat/agent notes*.
- The auditor must reconstruct exact authority V1/V2, simulated approvals/absence, source/observed/effective times, semantic file revisions, linked metric, recorded native query, before/after result, drift status and unresolved coverage.
- Independently re-run a native semantic query from the recorded version on preserved/retrievable data and verify the evidence. The auditor must not be handed a ready-made report as an unexamined answer.
- Remove an archived original, alter a numeric verification receipt, edit an approval, alter an observed time, and tamper with semantic code. These are separate negative controls; tampering must fail closed where a trusted root actually exists. Clearly state any unanchored-storage trust limitations.

The mechanism must persist meaningful state across all stages **without resetting mappings manually**. A Claude-generated Markdown summary alone is NOT a working system of record.

## 5. Operational outcome instrumentation: do not fake a customer pilot

For each stage record a concise event ledger:

- start/end clock timestamps and process/tool calls (if measurable);
- owner roles whose decisions were required and which were simulated;
- # affected/unaffected/unknown semantic objects; # review items and false alerts;
- semantic query outputs, data fingerprints, exact replay commands and native exceptions;
- human review time: **NOT MEASURED** unless an actual human participated;
- terminal disposition (sandbox verified / unchanged / blocked / out-of-scope), with remaining work and accountable owner;
- cost of running this slice when knowable; no invented efficiency percentages.

Compare **what the native platform/Git/tests provide alone** with the connective workflow state Sophon actually maintains, using explicit interface/evidence inventories, not an intentionally crippled Claude baseline or another costly two-arm statistical benchmark.

Don't claim a paid customer wants this until actual usage and buying behavior exist. What matters now is whether a controlled transition can be **completed and audited**, not the performance of a particular LLM.

## 6. Precommitted acceptance checks and stop conditions

The frozen oracle must score **each** check PASS / FAIL / INCONCLUSIVE with original evidence, not just model assertions.

Minimum required checks:

1. Native, actual MetricFlow execution with data-backed queries (otherwise BLOCKED).
2. V1 recorded with independently retrievable original evidence, links and distinct timestamps.
3. V1 proposal cannot be mistaken for an approved interpretation; role/approval status is faithfully recorded.
4. V2 receipt automatically invalidates materially dependent verification, leaves unaffected object valid, and surfaces unknown coverage.
5. V2 produces an actual semantic-layer patch whose native execution matches independently computed rows/expected business values.
6. Change cannot be designated approved/production-verified based on an LLM assertion or a simulated review alone; missing/unauthorized approvals remain observable.
7. Semantic-originated substantive drift produces a documented discrepancy with counterexample; harmless/no-op produces no false violation.
8. A fresh process/auditor can recover V1 and V2 (known-at versus effective-at), code, recorded metric values, evidence, negative controls and missing approvals, without prior LLM chat.
9. Tamper tests reveal material corruption or loss under the recorded trust model; explain what cannot be detected without an external root.
10. Out-of-scope and insufficiently observable governing clauses remain UNKNOWN/PARTIAL/OUT_OF_SCOPE; no invented full enterprise compliance.
11. A substantive integration path to an existing AI/BI consumer is verified from real source code/manifest when the upstream provides it; if absent, explicitly not observed.
12. Outputs are reproducible from a clean worktree on Windows PowerShell or Linux, with immutable upstream version and dependencies pinned (document platform exceptions rather than claiming unrun portability).

A scorer must check actual artifacts, return receipts, dataset identities and lineage—not just whether files contain expected keywords. Include pass/fail mutation sanity tests; if disabling the registry, omitting a governing source, or swapping the metric doesn't change the result, the scorer is vacuous and must be considered failed.

**Decision (choose one, no spin):**
- INFRASTRUCTURE_SLICE_WORKS — checks 1–10 pass with executable native evidence; checks 11–12 are accurately disclosed, any remaining limitations named. This proves bounded *technical integration and persistence*, not market value, real legal reliability, ROI or a proprietary moat.
- SLICE_FAILS — native semantic execution works but one or more mandatory core transition, authorization, reverse-check, persistence or audit properties fail; explain why and the cheapest correction.
- BLOCKED_NATIVE_RUNTIME — no genuine native semantic execution after the bounded setup attempt(s); stop rather than substituting a different kind of rule engine.
- INCONCLUSIVE — independent reference or evidence irreparably invalid even though native execution may work; describe what is missing.

Never call a successful lab scenario "validated customer outcome" or a "GO for company". Likewise, a working horizontal incumbent feature doesn't make a useful assembled workflow automatically nonviable.

## 7. Resource budget, repository hygiene, deliverables

**Bounded disposable spike:**
- Exactly ONE external semantic project (one fallback allowed only if blocked), ONE lab-authored V1→V2 amendment, ONE real semantic drift mutation, ONE harmless control, ONE out-of-scope provision, ONE independent audit session.
- Small state store and CLI, no UI/SaaS/cloud provisioning, no new generalized contract parser, no data-warehouse rewrite, no distributed agents or huge research sweep.
- No speculative elaborate provenance graph. If you cannot keep the implementation small and complete, report the limitation and narrow execution transparently rather than shipping architecture theatre.
- LLM may be used to generate candidate interpretations and code; no large repeated paid-API call loop and do not expose secrets.
- Do not spend effort reproducing PR #3's 22-run A/B benchmark or adding another "novel kernel" competition.

**Git:**
- Inspect git status and protect all local modifications first.
- Read origin/main for charter v1.1 and this prompt, then create feature branch from origin/main in an **isolated worktree** named experiment/governed-transition-g1-2026-10-12; preserve PR #2 and PR #3 branches and artifacts.
- Put **all new executable experiment material** under experiments/governed_transition_g1/. Do not alter legacy experiments or source projects. Third-party code is retrieved at a pinned SHA rather than copy/pasted without provenance/license.
- Commit protocol/gate BEFORE implementation, then implementation and result. Preserve first-run failures and diagnostics. Push branch and open a **draft PR** if available; do not merge it.
- Keep local raw/generated synthetic databases out of Git unless tiny, licensable fixtures are genuinely necessary. Make clean reproduction deterministic and document power/CPU/network requirements when relevant.

**Final files:**
- PRIOR.md, SOURCE_GATE.md and PROTOCOL.md with pre-code commit+hash.
- TIMELINE.json, FROZEN_CASES.json and oracle/verification scripts and hashes.
- README.md with **exact executable PowerShell commands** and a Linux equivalent, including fresh-auditor reproduction.
- src/, tests/, small fixtures/event schemas, persistent state example/rehydration and native MetricFlow query receipts.
- TRANSITION_REPORT.md (V1→V2, reverse drift, no-op, out-of-scope, event history, actual before/after queries).
- AUDIT.md (independent reconstruction, tamper/replay results, limits).
- OPERATIONAL_METRICS.md (measured proxies only, clear "no customer usage" label).
- DECISION.md (one of the exact statuses and the cheapest justified next experiment, WITHOUT a generic new-platform roadmap).

**Your final answer must provide:**
1. Pinned native semantic platform + actual metric, warehouse and execution output.
2. One table of the five governing-transition stages and corresponding observed outcomes.
3. How source authority, simulated approval, data-owner change and semantic state remain separate.
4. What survives Claude Code session loss, what the fresh auditor proved, and what would fail if evidence were tampered with.
5. Explicit limitations: **LAB_AUTHORED policy + synthetic data**, no live Snowflake/Databricks, no real customer approvals, no commercial outcome.
6. Machine-checked acceptance score, actual deviations, exact decision.
7. Branch, commits, draft PR link and precise PowerShell commands to replay.

**Conclude with a functional, independently checkable governed transition or a clear bounded failure. No redefinition of Sophon and no product story substituted for evidence.**
