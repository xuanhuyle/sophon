# Sophon — Next task: Semantic-Layer Boundary & Baseline Failure Test

**Date:** 2026-10-11  
**Status:** Execution prompt — bounded technical spike, NOT a request for a platform.  
**Goal:** Find a reproducible technical limitation in a *competent* Claude Code + native semantic-layer workflow that could justify ONE specialized Sophon mechanism. If no such limitation can be demonstrated, say so and stop.

## 0. Why we are doing this

The owner's precise Sophon thesis is:

> An authoritative governing corpus (contracts, regulations, organizational policies and approved amendments) is transposed **through the enterprise's existing semantic layer**, which is connected to downstream data systems and serves BI/AI consumers. Sophon should maintain a correct, evidence-backed, bidirectional relationship between governing authority and that semantic layer, support proposed changes when requirements change, verify when semantic definitions change, and preserve independent audit evidence over time.

The semantic layer is the **actual integration boundary**, not a decorative YAML representation. We do NOT substitute an independent policy runtime or reconstruct the entire warehouse in Sophon. The semantic layer is not assumed to govern actions outside its coverage, and correct semantic responses do not prove downstream agent behavioral compliance.

On 2026-10-11 the previous **governance-integrity** experiment finished with **STOP_KERNEL**, narrowly for a persistent link store added to Claude Code in a Publicodes legal-to-rule environment. Both arms produced identical material changes (22/22) and an equal as-of audit (9/9). The specialist store preserved provenance and revalidated, but changed no scored answers and consumed more tokens/time. Publicodes is **not** a dbt MetricFlow / Snowflake / Databricks business semantic layer.

Moreover, the prior preregistration contained a **chronology leak**: 2026 reverse episodes were executed before 2025/early-2026 maintenance tasks, with future evidence carried in each arm's memory. Two scoring passes were needed to repair ambiguous reference labels and evaluator bugs. These defects cannot recur.

**Do not rescue the stopped mechanism by simply re-running the same comparison on another repository.** Do not build a new ledger, graph, legal DSL, orchestration framework, product/UI, agent runtime or generalized compliance engine.

The next decision is smaller and earlier in the causal chain:

> **Does a strong Claude Code workflow using an actual pre-existing enterprise-style semantic layer and conventional governance/testing tools exhibit a concrete, reproducible failure in transposition, bidirectional verification, scope/coverage or evidence-based audit that is worth solving with specialized machinery?**

We are looking for the *failure and its cause*, not proving Sophon succeeds.

## 1. Read repository evidence BEFORE selecting a test

Inspect all of:

- README.md
- docs/REPORT.md and docs/DECISION.md (2026-09-21 policy-as-code parity)
- docs/OWNER_REQUEST.md
- Claude_Code_Sophon_Amendment_Impact_Experiment_Prompt_2026-10-04.md (prompt only, never executed)
- Claude_Code_Sophon_Governance_Integrity_Experiment_Prompt_2026-10-11.md
- On branch origin/experiment/governance-integrity-2026-10-11:
  - experiments/governance_integrity/EVIDENCE_GATE.md
  - experiments/governance_integrity/PROTOCOL.md
  - experiments/governance_integrity/RESULTS.md
  - experiments/governance_integrity/DECISION.md
  - experiments/governance_integrity/AUDIT_REPORT.md
- On branch origin/codex/alignment-review-agent (PR #2):
  - viability/RESULTS.md
  - viability/public_nyc/README.md

Read those branches **without modifying them** (git show, or a read-only worktree). Summarize in <= 500 words what is already known vs the one new uncertainty. Preserve negative evidence; never retroactively change prior verdicts.

**Important existing observations:** a synthetic Jaffle dbt/DuckDB governance fixture already passed 9/9 scripted checks, but all reference tests were authored manually; a public NYC taxi/dbt review found real record-loss and monetary-precision problems in existing transformation SQL but had no blinded baseline, no genuine MetricFlow semantic interface, and no authoritative contract matched to the upstream project. Do not count either as a new proof.

## 2. Scope / time discipline

This is a **single, bounded technical spike**, not another 22-run research program.

- Evaluate no more than TWO public candidate environments; choose ONE.
- Make ONE attempt to reproduce a genuine semantic-layer runtime and query (version-pin dependencies and inputs).
- ONE baseline solver run (one independent fresh context) covering at most two small change episodes plus one no-op/uncertain control.
- ONE independent verification pass with an immutable reference.
- No more than one narrow fix for a setup/runtime bug; if environment fundamentally cannot execute, document the failure and stop.
- No sophisticated agent swarms, no 15–30-case benchmarks, no API spending loops, no lengthy competitive landscape sweep, and no repo-wide refactoring.
- If a genuine technical failure is absent, **do not manufacture one** just to justify Sophon.

Write and commit under experiments/semantic_boundary/ only; do not modify prior PR #2 or PR #3.

## 3. Find the right environment — GATE FIRST

Candidates worth verifying directly from source (not preapproved):

**Candidate 1, actual MetricFlow:**  
https://github.com/behramkorkut/Governed-Analytics-Agent  
README claims dbt + MetricFlow + DuckDB/Snowflake, 15 governed metrics and an LLM consumer. The inputs are synthetic; there is no established external authoritative governing corpus or authentic amendment history. Confirm actual source, runtime, tests and versions.

**Candidate 2, native alternative with governance checks:**  
https://github.com/flyersworder/agentic-data-contracts  
Claims dbt/Cube/other semantic-source integration, contract-based business policies, verified-example validation, drift checks and evaluated agent access. Inspect what is runnable. This is a **conventional/competitor baseline**, not automatically a metric-layer implementation or an external legal corpus.

Choose an existing project with real executable **dbt MetricFlow semantic models** (entities/dimensions/measures/metrics or equivalent verified native Snowflake/Databricks semantic objects), executable underlying data, and at least one real downstream query or consumer. We prefer a single organization that has its own genuine, dated policy/metric-governing requirements and changed both sides historically. But **do not invent authenticity**.

Hard classifications:

- REAL GOVERNANCE MATCH: a demonstrably pre-existing normative/approved business policy from the same entity, not generated after looking at the implementation, mapped to existing semantic objects with genuine change history and independent reference.
- SEMANTIC-BOUNDARY ENGINEERING PROXY: real pre-existing semantic interface and executable data, but policy is project README (descriptive, not approved), data are synthetic, history is insufficient, or changes must be controlled mutations. This can test integration and certain failure modes, **not the enterprise governance thesis**.
- NO EXECUTABLE MATCH: none runnable. Report exact obstacles; don't spend time building a new synthetic organization.

Write GATE.md with source URLs, immutable SHAs, versions, governing-authority classification, data provenance, downstream consumption, run evidence, and limits. The earlier Publicodes experiment must not be reused as the target; its negative evidence stands.

## 4. The smallest runnable challenge (if gate permits)

Focus on **an existing semantic layer and its consumers**, not transformation SQL alone.

A. BASELINE STATE:
- Run the native semantic query interface (e.g., \`mf query\`, or the exact native equivalent) against its actual configured data.
- Identify a bounded *business requirement* independent of the solver's own generated rationale. Label actual authority: approved public policy, existing documented metric contract, or controlled lab requirement.
- Capture actual semantic source files, manifest (if available), output query and result, underlying data fingerprint, Git SHA, versions, and downstream BI/AI consumption evidence if the project exposes it.

B. FORWARD CASE:
- Use ONE genuine later requirement change if there is an authentic dated source and historical pre-change snapshot.
- Otherwise, use ONE **explicitly labelled controlled policy amendment** prepared and frozen by a separate builder against the PRE-change semantic project, not leaked to the baseline solver and NOT scored as genuine historical governance.
- Let Claude Code + native tools analyze the governing delta, identify the *existing semantic definitions* requiring change, propose edits on a disposable branch, execute the real semantic runtime on data, and produce source-grounded audit evidence. It is acceptable to abstain where the source is insufficient.
- Test both affected and unaffected metrics. The intended result must not be embedded in object names or post-change descriptions.

C. REVERSE CASE + NEGATIVE CONTROL:
- A separate real historical semantic-model change is preferable. If unavailable, make ONE controlled semantic mutation, separately prepared and hidden: changed aggregation, filter, join path/entity grain, effective date or an expression with non-obvious business implications. Do not only change a string literal.
- Include a legitimate no-op/equivalent refactor OR out-of-scope requirement. The solver should not flag everything as a violation.
- Ask if the unchanged governing definition is still correctly implemented, verify against live semantic results, and specify what remains NOT OBSERVABLE.

D. AS-OF EVIDENCE CHECK (small, not the old trivial audit):
- From the baseline's own retained artifacts, attempt to reproduce the governing-source/version claim, the semantic definition/commit, the executable metric result and any genuinely recorded approval. Validate hashes and executable commands.
- Do NOT make hashes a proprietary Sophon advantage. The baseline may use Git, checksums, documentation, tests, native metadata/lineage and existing governance tooling.
- Distinguish what the semantic layer can verify from actual behavior of downstream agents; do not claim the latter.

Do not make the same model both inventor of the only reference assertions and evaluator of its own output. Seal the builder's deterministic reference scenarios and expected outputs before the solver runs; keep any injected cases segregated from real-world evidence. Label ambiguous/unprovable claims UNRESOLVED.

## 5. Chronology / information isolation (mechanically enforced)

This requirement fixes the mistake in the previous experiment.

Before any solver run, create a machine-readable timeline manifest: each input source with (publication/commit time, effective time, allowed decision time); all historical cases must be in ascending **decision time**. Publication, legal effective date and date of observation are NOT interchangeable.

- Programmatically assert: no staged file, historical note, tool transcript, stored context or prior scenario contains an artifact published after that task's decision-time cutoff. Fail closed on violations.
- Never let a future episode's notes flow backwards. Use separate clean worktrees if tasks are nonchronological, or don't retain memory in that case.
- If a timeline cannot be reconstructed, make the task a **contemporaneous controlled diagnostic**, never a blind historical replay. Say so.
- A shared model's pretraining might already contain public commits; note this limitation. Do not assert complete blinding merely because the hidden folder was inaccessible.
- Execute scorer smoke tests with known pass, known fail and an ambiguous case **before** scoring. Freeze scorer code and reference before seeing solver results. No post-result gold redefinition.
- If a scoring error is found later, retain the entire first pass and issue a separate marked methodological amendment; do not present repaired scores as if preregistered.

One solver and one scorer context is enough. Record costs, model, exact commits and task transcript. Only let scorer see the hidden reference after the baseline answer is frozen.

## 6. Baseline FIRST; no Sophon-specific mechanism yet

The baseline is Claude Code with **all competent ordinary options**:
- same source corpus and semantic artifacts;
- Git history up to the correct date;
- dbt/MetricFlow tooling, manifests, compiled queries, data tests and read-only database checks;
- ordinary scripts, documentation, JSON/markdown, provenance hashes and change-impact mapping;
- existing compatible governance/data-contract tooling, if installable without turning this into a dependency project.

It may maintain persistent notes. Do not artificially limit the baseline to one-shot prompting, prohibit Git, or withhold data to make it fail.

**Do NOT implement a new Sophon link store.** The previous test already stopped that differentiator. Only build minimum fixture/run/scorer plumbing needed to observe a potential failure at the real semantic boundary.

Collect concrete proof of how the strong baseline does, including semantic query outputs and independent reference checks.

A **qualifying failure** must be all of:
1. material and evidenced by actual semantic metric execution or objectively unambiguous independent governing evidence;
2. not merely a missing dependency, artificially withheld context, fabricated policy, trivial mutation, compiler misconfiguration, hindsight artefact or scorer mistake;
3. reproducible (same failure without per-case prompt tuning), with a plausible reason why conventional tests or tools didn't catch it;
4. attributable to the governing-document ↔ existing semantic-layer translation, bidirectional verification, coverage, or audit relationship, not an unrelated coding bug.

Record ordinary baseline successes with the same prominence as failures. An unsolved ambiguity or missing authorized interpretation is **not** automatically an AI failure; correct abstention counts as success.

## 7. Decision / follow-up: only if the evidence earns it

Pre-register the following decision outputs in PROTOCOL.md before seeing baseline results.

**NO_GAP_FOUND**:
The competent baseline handles the bounded cases (or its errors are minor and fixed with ordinary tools). Do not implement a specialized Sophon mechanism. Conclusion: no demonstrated differentiation; the larger enterprise thesis remains unproven.

**QUALIFYING_GAP_FOUND**:
A significant, independently verified and reproducible baseline failure survives normal available tools, within the semantic-layer boundary. Write a one-page follow-up hypothesis specifying ONE causal mechanism, what conventional baseline it must beat, a decisive independent oracle, and a kill condition. **Do not implement the mechanism in this task.** This is permission for a new experiment, not evidence that Sophon fixes it.

**INCONCLUSIVE_INPUTS**:
No runnable real semantic layer, no defensible governing source/reference, invalid chronology, or inadequate independent truth to claim a meaningful baseline result. Write the exact gap and stop. A successfully executed controlled fixture may be separately labelled ENGINEERING_SMOKE_PASS, but never silently upgraded into real-world validation.

No GO/CONTINUE_SOPHON or business verdict is available from this small task. The technical hypothesis is not established by a good demo.

## 8. Deliverables (ONLY under experiments/semantic_boundary/)

- PRIOR.md — <= 500 words on what the repo already established; link precise prior evidence.
- GATE.md — why selected candidate, exact authority level, model, runtime, version, data and source limitations.
- PROTOCOL.md and protocol SHA256 — frozen ahead of scored baseline; objective metrics and fail-closed timeline constraints.
- TIMELINE.json + validator script; case manifest containing input hashes and provenance.
- README.md — exact reproducible commands including **Windows PowerShell** and expected native MetricFlow output.
- inputs/ and scripts/ — smallest artifacts needed to run semantic query and independently verify outcome. Controlled mutations explicitly separated and labelled.
- BASELINE.md — actual solver behavior, original outputs, tool calls, failures, clean successes, uncertainty.
- RESULTS.md — mechanical/independent verification and case-level outcomes, observed/inferred/assumed.
- DECISION.md — exactly one decision above and specific next engineering action.

Do not commit third-party dependencies or large raw datasets without license assurance. Keep upstream inputs pinned/retrievable with hashes; never push changes to upstream projects. Do not touch the established PR #2 or PR #3 artifacts.

## 9. Execution instructions and final response

Before coding: check repository branch and uncommitted files. Start a new feature worktree/branch \`experiment/semantic-boundary-kill-test-2026-10-11\` from current \`origin/main\`; preserve all user work. Fetch the existing two experiment branches for read-only inspection. If git fetch/network is blocked, report that, use already available refs where possible, and don't rewrite prior artifacts.

Carry out the evidence gate and, if valid, the native semantic runtime reproduction and small baseline test. Commit reproducible outputs, push the new feature branch, and open a **draft PR** when possible.

Your final response must answer:
1. What precise existing semantic-layer runtime did you actually execute against what data?
2. What governing requirement was actually authoritative versus only synthetic/descriptive?
3. Did the baseline succeed or fail on the forward, reverse and no-op cases? Show executed outputs/counterexamples.
4. Which failure, **if any**, cannot already be handled by conventional Claude Code + native tools?
5. Was chronological isolation validated mechanically, or are results only a non-scored diagnostic?
6. What is the exact decision and the cheapest justified next action?
7. Which paths, commits and draft PR contain the work?

**Do the experiment, not another architecture essay. Be willing to report NO_GAP_FOUND or INCONCLUSIVE_INPUTS.**
