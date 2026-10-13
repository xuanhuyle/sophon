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
