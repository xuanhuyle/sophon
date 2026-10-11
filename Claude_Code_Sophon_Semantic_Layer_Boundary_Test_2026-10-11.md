# Sophon — Build the minimal persistent AI-governance infrastructure

Date: 2026-10-11
Status: **REVISED execution prompt**, superseding the earlier "Semantic Layer Boundary & Baseline Failure Test" at this path.

## 0. Essential correction: product thesis and evaluation objective

The owner has explicitly rejected the idea that Sophon's reason to exist is to outperform the best LLM at comparing a governing policy with business code.

**Sophon is proposed as AI-native governance INFRASTRUCTURE.** A capable LLM may perform the interpretation and coding extremely well, but a chat or an ephemeral coding session is not itself an organization's durable system of record, change-control mechanism or audit interface. Conversely, competent engineers *can* construct such infrastructure with Git, databases and existing governance products. Sophon does not claim an intrinsically novel algorithm merely because it persists information.

The architecture is SPECIFIC:

    AUTHORITY: contracts / regulations / approved organizational policies / amendments
                                 |
                                 v
                              SOPHON
       translate proposals / maintain evidence & authority / verify / audit
                                 |
                                 v
               EXISTING ENTERPRISE SEMANTIC LAYER
             (dbt MetricFlow or verified native equivalent)
                                 |
                                 v
                     EXISTING DATA SYSTEMS
                                 |
                                 v
                   BI and AI metric consumers

**Transposition occurs THROUGH the existing semantic layer**, which already represents business meaning and connects to the data systems. Do NOT separately rebuild the warehouse, directly patch every downstream consumer, or invent a parallel semantics engine. A correct semantic metric does not prove all downstream agent actions comply with policy; state this boundary.

The real next question is:

> Can we build the smallest working infrastructure that keeps authoritative policy versions, approved interpretations, semantic definitions, applicable dates, validation runs, changes and their evidence persistently linked, and that remains queryable and independently auditable after the LLM session ends and either side changes?

The experiment is a **functional vertical-slice validation** of infrastructure, not another A-versus-B LLM accuracy benchmark, sales exercise, or claim of novelty.

**Do the build-and-test, not just write a proposal.** If the actual semantic runtime cannot be made to work in the bounded effort, report BLOCKED with reproducible diagnostics; do not substitute Publicodes or pretend static YAML is a functioning BI semantic layer.

## 1. Read and preserve previous evidence

Read:
- README.md, docs/REPORT.md, docs/DECISION.md, docs/OWNER_REQUEST.md.
- The completed experiment on branch \`origin/experiment/governance-integrity-2026-10-11\`: \`experiments/governance_integrity/EVIDENCE_GATE.md\`, \`PROTOCOL.md\`, \`RESULTS.md\`, \`DECISION.md\`, \`AUDIT_REPORT.md\`.
- On \`origin/codex/alignment-review-agent\` (PR #2): \`viability/RESULTS.md\` and \`viability/public_nyc/README.md\`.
- The historical prompt at this file's parent Git commit if needed to understand why the task changed.

Record a short \`experiments/governance_infrastructure/PRIOR.md\` explicitly affirming:

(a) Publicodes experiment: **STOP_KERNEL** for the extra hash-linked store as a performance differentiator on that bounded law-to-rule task, not a verdict that governance infrastructure is unnecessary;  
(b) previous dbt/DuckDB viability: technically interesting but synthetic/manual reference and NOT a live MetricFlow test;  
(c) the previous experiment was chronologically contaminated (2026 texts before 2025 tasks);  
(d) persistent governance / provenance / independent audit **must actually work**, irrespective of LLM comparative accuracy.

Do not overwrite, selectively reinterpret or quietly erase the negative findings. Do not rerun the previous 22-agent experiment.

## 2. Choose ONE existing real semantic-layer execution environment

Preferred starting candidate:
https://github.com/behramkorkut/Governed-Analytics-Agent

It claims a working dbt + MetricFlow + DuckDB retail analytics stack, native \`mf\` queries, downstream AI/BI consumers and 15 metrics. Inspect actual source, versions, SQL, executable metrics, licenses and tests; do not trust the README alone. Its data are **synthetic** and no authentic external policy corpus is established. That is fine for a labelled **ENGINEERING** proof of infrastructure, but not for claiming real enterprise compliance.

If blocked, inspect at most ONE credible alternative with a real, executable native semantic interface. Do not spend days building a new data estate. If neither works, stop with BLOCKED / exact execution evidence; no fake semantic substitute.

Reuse the existing published semantic definitions and their underlying data as-is initially. Choose a metric whose meaning is governed by an intelligible, independently checkable business policy. Run a real native semantic query before proceeding. Preserve upstream commit, manifest, relevant semantic files, compiled query and query output/data fingerprint. Check at least one downstream BI/AI consumer is actually wired to the same semantic catalog if the project provides one. Do not claim live external platform compatibility when running DuckDB locally.

## 3. Freeze a tiny, transparently labelled policy-and-change scenario BEFORE coding

If no **authentic matched governing policy** exists (likely), use a small explicitly **LAB-AUTHORED** governing document. This is permitted to validate infrastructure mechanics but *never* used as evidence that Sophon can interpret real legal complexity or that a company's policy was approved.

Have an independent harness prepare and freeze BEFORE the implementation:
- V1 of a *bounded* business policy with an explicit effective date, 1–2 requirements and an example expected semantic outcome;
- a plausible policy amendment V2 with publication/observed time and effective date;
- one changed semantic definition that should be identified as drift (separate reverse direction);
- one equivalent refactor or untouched metric as a negative control;
- an ambiguity/out-of-scope example that cannot honestly be verified through the semantic layer;
- deterministic expected behavior on selected underlying records / metric queries, prepared separately from the code generator. The oracle must not simply replay the generated implementation.

Keep exact test inputs and oracle out of the LLM proposing the implementation when feasible. Include publication, observed and effective dates as distinct concepts. Validate that a historical "known as of" query cannot know later-published amendments, even if an amendment is backdated. **Mechanically enforce chronology**; no future memory leaks.

A small controlled scenario is not cheating if it is candidly an engineering test. It is cheating to claim it is a real historical enterprise governance benchmark.

## 4. Build the MINIMUM reusable infrastructure (one narrow vertical slice)

Implement under \`experiments/governance_infrastructure/\` with one native semantic adapter and a minimal durable state store, using conventional standards/libraries whenever possible (Git, SQLite, content hashes, JSON; no proprietary DSL, graph database, orchestration platform, new legal ontology, production service or web UI).

Six functional properties must exist:

**I. INGEST & VERSION authority.**
Register original governing text, amendments, observed-at time, effective period, source provenance, interpretation state (proposed / approved / rejected / unresolved), and the real approver event *if any*. It must never infer an approval merely from LLM output or a Git merge. Synthetic acceptance events must be labelled simulation.

**II. MAP THROUGH THE EXISTING SEMANTIC LAYER.**
Propose requirement <-> existing metric / semantic model / dimension / dependency links, referencing actual source file, semantic identity and git revision; show provenance, confidence and unresolved coverage. The LLM can propose links. The infrastructure must persist both proposal and disposition, not magically treat a proposal as verified.

**III. TRANSPOSE WITH CONTROL.**
Given amendment V2, propose a change to the *existing semantic-layer code/configuration* in a disposable copy/branch, not directly to raw production tables. Gate the change on the actual applicable authority/approval status. Execute its native syntax/compile, metric query and relevant data-backed assertions against the independently frozen expected results. Preserve the proposed patch, rule/metric version, input fingerprint, test output and who/what authorized promotion. If no real person has approved it, the result remains explicitly UNAPPROVED / SANDBOX_ONLY.

**IV. BIDIRECTIONAL VERIFY / INVALIDATE.**
After a governing change, automatically mark dependent verification stale and produce an actionable impact set, including no-op links. After an independent semantic change, re-evaluate relevant governing claims and distinguish material discrepancy / harmless refactor / unknown. No manual reset of links between changes. Show both "correct for recorded test cases" and "not fully verified" rather than claiming universal legal compliance.

**V. PERSIST WITHOUT LLM CONTEXT.**
Terminate the initial execution/context, start a clean process/worktree (and ideally a separate fresh Claude context for the independent auditor). Without original chat or transient agent memory, query durable state and reconstruct the relevant source versions, interpretation/approval status, semantic versions, events and execution receipts. Exact immutable source material or retrievable content-addressed records must be preserved: a hash alone is not the evidence.

**VI. INDEPENDENT AUDIT.**
Provide \`as-of\` queries for (a) effective policy at date X *as known at date Y*, (b) semantic definition in force, (c) last verification and what data it tested, (d) missing or superseded authority, (e) amendments and recorded approvals, and (f) **coverage/unknowns**. An independent audit script must recompute the hashes, inspect the actual source snippets/semantic files and re-execute at least one recorded metric check. An LLM-written PDF/report without verifiable receipts FAILS.

Only use an LLM where it adds interpretation/proposal convenience. The audit, source integrity, as-of ordering, stale-state transitions and compiled semantic query must be demonstrably operational without believing the LLM's narrative.

## 5. Acceptance / adversarial checks

Pre-register an independent machine-checkable \`PROTOCOL.md\` and immutable reference BEFORE writing solution code. Focus on functionality, not benchmark superiority.

Required pass/fail tests:
1. V1 policy is stored with a stable original artifact, correct source identity, observed/effective dates and semantic binding.
2. Native semantic query actually runs on underlying data, and V1 result matches a *separately specified* expectation.
3. V2 policy arrival invalidates only relevant links, can be transposed into a proposed semantic change, and native result matches the separate V2 expectation (no false claim of deployment/approval).
4. Independently editing the existing semantic definition creates an appropriate review/failed-verification status; an equivalent refactor/no-op does not produce a fabricated compliance violation.
5. After a fresh process/session starts, an auditor **without the first agent's chat/session** can reconstruct both V1 and V2, binding versions, recorded tests, approvals or their absence, and unknown coverage.
6. Tampering with stored source or semantic code, deleting evidence, modifying effective dates or modifying a result receipt causes independent integrity/audit checks to fail closed. If hashes/archives are themselves editable without an anchored trusted root, state the integrity trust assumption.
7. An unpublished future amendment is never treated as already known for an earlier knowledge-time query even if its effective date is retroactive.
8. A policy item not represented by the semantic layer is classified OUT_OF_SCOPE or UNKNOWN, not VERIFIED.
9. Outputs remain **accurately labelled**: LAB_AUTHORED policy, simulated approval vs real, native runtime vs emulation, verified test-case behavior vs general compliance, semantics vs downstream agent behavior.

Include tests that fail if the core implementation is disabled (mutation/sabotage sanity). Treat generic successful scripts, a hash match or 100% test pass with a vacuous oracle as no evidence.

What we seek is a *real running infrastructure capability*, not higher recall than Claude on a constrained dataset. Correctness, persistence, traceability, auditability and as-of reconstruction are **necessary acceptance criteria** even if an LLM can perform all interpretive work.

## 6. Failure interpretation: do not confuse product thesis and engineering feasibility

**INFRASTRUCTURE_SLICE_WORKS**: Native semantic layer executed; the end-to-end sequence passes independently replayed tests, survives context loss and preserves audit/authority boundaries. Conclude only that the minimal infrastructure is feasible in a small controlled workflow; not that we have legal accuracy, a commercially differentiated kernel, adoption or production reliability.

**SLICE_FAILS**: An actual required property cannot be made to work in the bounded implementation, with reproducible evidence. Describe the cause and whether architectural assumptions are at fault.

**BLOCKED / INCONCLUSIVE**: Unable to execute native semantic runtime or establish independent expected outcomes under the resource bound. Do not fabricate them.

No A/B performance comparison to a stronger LLM is required. Use conventional technologies and existing tools as building blocks, not enemies to defeat. A useful governance infrastructure can be entirely composed of existing primitives. No novelty claim is necessary.

Separately disclose remaining product/platform engineering obligations (integrations, authentication, authorized workflows, source-of-truth management, nonrepudiation, throughput, permissions, deployment, long-running maintenance and real-policy coverage). Do not expand this spike to implement them.

## 7. Execution limits and outputs

Limit: ONE environment, ONE bounded policy with one amendment, ONE reverse semantic drift and one harmless control, ONE independent audit replay. Small scripts and a CLI, not a platform. Do not create a large synthetic organization, dozens of subagents, or run another long literature/market sweep.

Repository hygiene:
- Check status; do not overwrite uncommitted work.
- Start feature branch \`experiment/governance-infrastructure-slice-2026-10-11\` based on \`origin/main\`. Read PR #2 and #3 as references only, not as active work branches.
- Put all new work under \`experiments/governance_infrastructure/\`.
- Commit reproducible code and small evidence; license/pin upstream; keep heavy dependencies and datasets out of Git.
- Push branch and open a **draft PR** if tooling permits. No changes to upstream third-party repositories.

Deliver:
- PRIOR.md (what the prior STOP_KERNEL did and did not mean)
- SOURCE_GATE.md (authentic vs LAB_AUTHORED source truth; actual semantic interface)
- PROTOCOL.md, TIMELINE.json + chronology validation, SHA256 and frozen independent reference
- README.md with exact PowerShell reproduction commands
- \`src/\`, \`tests/\`, minimal fixtures, state, real native-semantic output receipts
- SCENARIO_RESULTS.md (each pass/fail, original outputs and reproducible checks)
- AUDIT.md (fresh-context as-of audit and tamper result)
- DECISION.md (one of the three statuses, exact limitations, next smallest usable increment)

In the final answer tell the owner:
1. Which existing semantic runtime, metrics and underlying data actually executed.
2. Exactly how the policies enter, get versioned, link to semantics and trigger reassessment.
3. The specific forward transposition and reverse-check outputs.
4. What survives the initial LLM process and what an independent auditor can reproduce.
5. How missing authority, retroactive dates, source tampering and out-of-scope requirements behave.
6. What remains unproven about real contracts and agent compliance.
7. Branch/PR/commit, commands and honest PASS/FAIL decision.

**Build a working, persistent, independently auditable governance infrastructure slice. Do not ask the LLM to defeat itself.**
