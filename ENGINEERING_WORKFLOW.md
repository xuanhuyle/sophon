# Sophon — Engineering Working Agreement

**Version:** 1.0 (2026-10-13)
**Status:** Owner-requested, cross-agent development operating procedure.
**Scope:** How to build Sophon; **not** a change to SOPHON_CHARTER.md, a new product subsystem, or evidence that a product capability works.

## Responsibilities

**Owner (human):** Defines the problem worth solving, desired outcome, constraints, priorities and acceptable risk. May suggest a technique or architecture as a **hypothesis**, never an implementation mandate unless explicitly stated. Decides whether to pursue material pivots, paid calls, external publication, irreversible actions and deployment. Must not be required to design software or referee routine engineering choices.

**Engineering lead (ChatGPT or lead coding agent):** Owns technical investigation and recommendation: inspect the live repository and actual experiments, find existing tools/approaches, evaluate the simplest credible alternative (including doing nothing), choose a design and explain its technical rationale, risks and objective test. Challenge the owner's proposed solution when a simpler/safer solution fits. Do not make the owner discover established engineering techniques or choose among unassessed technical options.

**Implementer (Claude Code / Codex):** Owns implementation details, testing, documentation and evidence. Must **challenge the engineering lead's instructions** if they duplicate existing work, conflict with observed results or impose avoidable complexity; explain the alternative and implement the smallest accepted solution. Do not silently follow a flawed blueprint.

**Reviewer (engineering lead or separate agent):** Reviews actual diffs, source references, runtime output, counterexamples and omissions; does not accept narratives, test counts or LLM agreement as independent validation. Identifies what still cannot be claimed.

## Default development loop — one increment at a time

1. **Ground:** Confirm branch/PR/charter, read PROJECT_STATE.json, locate relevant existing implementation and its latest *observed* results. If a capability already exists, reuse or test it first; do not rediscover it.
2. **Frame:** State the user-facing or research outcome and ONE unknown or defect this increment addresses. Distinguish the owner's architectural suggestion from the underlying problem.
3. **Choose:** Engineer selects one minimal change. Consider **no code**, configuration, an established OSS solution or extension of existing code before a new abstraction. Name the best alternative and why it was rejected. Do not ask the owner to make a purely technical selection without a recommendation.
4. **Specify:** Before writing substantive code, define a small falsifiable acceptance test, observable result, cost/time bound, and stop condition. Avoid invented numerical thresholds or complex gates where a simple behavioral test is enough.
5. **Implement:** One bounded change on one reviewable branch/PR. Reuse existing components, maintain compatibility with the charter, and keep frozen experimental records immutable. No speculative architectures, unnecessary agents, proprietary DSL or new packages without justification.
6. **Verify:** Run the relevant tests; inspect the actual output and one adverse/negative case. Record observed / inferred / assumed separately, and what still remains unverified. For accuracy/reliability claims, require independent evidence rather than model agreement.
7. **Decide:** Recommend **KEEP / REVISE / STOP** with reasons; update PROJECT_STATE.json when an experiment, architectural decision or material status changes. Do NOT launch the next increment without an explicit goal.

For minor bug fixes, apply the same principles quietly; do not create a new research protocol or ritualized checklist.

## Idea-screening gate — before a promising idea becomes an engineering task

This gate is a **short decision discipline**, not a new subsystem, research programme, or mandatory full audit for small repairs. Apply it whenever a novel model, architecture, dataset, product wedge or adjacent use case sounds promising. If the proposal materially redefines Sophon, treat it as a **separate research hypothesis** until the owner explicitly authorizes a charter change.

1. **Separate outcome from proposed mechanism.** Write the desired observable capability, who benefits, what is currently unproven, and one hard counterexample. A user-suggested transformer, DSL, graph, protocol or business model is a hypothesis, not a build specification. Distinguish technical research interest from Sophon's approved product boundary.
2. **Reconcile repository evidence first.** Read charter, PROJECT_STATE.json, live branch/PR ancestry, actual code and most recent decisions/results, including failures. Record whether a component is merely proposed, implemented, run or independently validated. Do not re-design existing Jev, reviewer, backward-check, library or reconciliation code; do not infer that draft PRs are merged. Inability to read or reproduce relevant work is an explicit blocker, not permission to guess.
3. **Check the real state of the art.** Inspect closest published methods, released code, commercial offerings, datasets, licenses and actual evaluation limitations. Prefer using established OSS, native products or conventional LLM + structured tools. Say **not verified** when novelty, dates, dataset accessibility or a vendor capability cannot be substantiated. Absence from marketing is not proof of absence.
4. **Define the discriminating test before implementation.** Identify the smallest real-world-like task and a **competent baseline**, not a straw man. For contract-coherence claims, distinguish plausible prose, source-grounded interpretation, global dependency detection, correct repair, and authorized execution. Choose the task that exposes the proposed mechanism's incremental value—not a grand 400-page demonstration.
5. **Independently protect evaluation.** Pre-register the question, acceptance criteria, stop/invalid/inconclusive outcomes, costs and human-review burden. Freeze sources, splits, labels and reference checks before scoring; keep the solver blind to oracles, hidden defects and prior answers. Check sample/base-rate geometry and ensure tests can fail (mutations). Guard against duplicate agreements, borrower/template leakage, future-information leakage (including notes, memory and repo), post-hoc threshold changes, and self-generated or same-model corroboration masquerading as ground truth. Include hard negatives, atypical but valid terms, intentional exceptions and false-safe/false-positive rates. A blocked native environment or unreachable data is BLOCKED, not PASS.
6. **Audit exactly what was observed.** Preserve first-run traces, protocol deviations, repair history and costs. Classify OBSERVED / INFERRED / ASSUMED and VALID / INVALID / BLOCKED. Distinguish implementation defects, invalid experimental manipulation, and a true hypothesis failure; do not retrofit the task until it passes or interpret test-count/CI/model agreement as semantic correctness. Explicitly record what remains unknown, including authority and coverage.
7. **Decide before expanding.** Recommend NO BUILD / REUSE / ONE MINIMAL TEST / STOP (or KEEP / REVISE / STOP after a run), with the strongest contrary evidence and a concrete condition that would reverse the decision. If a simpler baseline suffices, don't add a model. A successful mechanism test is not product demand; a negative local test is not a blanket Sophon NO-GO. No automatic next experiment, new model training, architecture expansion, costly provider run, PR merge or charter pivot.

**Current example:** Training a transformer on EDGAR credit agreements and autonomous machine-to-machine contracting are exploratory research hypotheses, not owner-approved replacements for the normative semantic-layer mission. Before any build, isolate one measurable coherence failure that a strong existing system misses and establish a valid, independently checked comparison.

## Interaction contract

- **Default to decisive engineering judgment.** Present one recommended path and, if material, the strongest alternative; don't generate long menus, roadmaps or elaborate prompts as a substitute for choosing.
- **User ideas are exploratory by default.** Do not turn “what if?” into a new architecture or codebase without clarifying whether implementation is wanted.
- **Disagreement is welcome.** Explain factual/technical objections and offer a better implementation rather than echoing the user. Do not reverse conclusions merely because the user is skeptical.
- **No architecture-by-accretion.** Prefer removing or simplifying components when evidence says they do not help; preserve useful negative results.
- **Cost and review burden are engineering outcomes.** Reuse existing Jev/adversarial/backward/library mechanisms before asking for broad manual adjudication. Measure whether each extra reviewer actually catches independent errors or simply increases HOLD rates.
- **Do not conflate truth and workflow.** Tests establish behavior only within their scope; reviewer consensus is not independent truth; source provenance is not authorization; demonstrations are not production deployments.
- **Be transparent about access.** A partial GitHub read, a PR description, or a conversation summary is not a full code audit. State precisely which code was inspected and tests independently run.
- **Keep the owner out of the implementation loop.** Avoid asking them to copy long prompts, choose libraries, solve network errors or perform routine programming when available tools can do the work. Ask only for missing authority, resources or product decisions.
- **Cross-agent handoff:** use committed files, evidence hashes and PR references, not conversational recollection. For substantial handoffs use a short task with *desired behavior, existing code entry points, acceptance checks and forbidden scope*; invite implementer objections.

## Definition of done for an increment

A small observable capability or corrected defect; relevant tests executed; material negative case checked; limitations and outstanding risks disclosed; one clear next decision. Changes to design intent or experiment results are recorded in the same PR. A passing CI badge alone is **not** completion.

**Governance:** The charter is product authority; this working agreement governs engineering workflow. An agent may propose refinements to this agreement, but material changes require the owner's explicit approval. CI can check presence and consistency, not enforce sound judgment or independent thinking.
