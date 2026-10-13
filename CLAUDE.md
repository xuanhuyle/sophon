# Sophon — standing instructions for Claude Code

**Read [SOPHON_CHARTER.md](SOPHON_CHARTER.md) in full before substantial work.** Charter **v1.2 (13 October 2026)** records the owner's current product decisions and supersedes narrower assertions in old prompts, reports and experiments.

## Product invariant — repeat before choosing an architecture

**Sophon is a shared normative semantic layer for governing documents.** It makes authoritative contractual, regulatory and policy meaning **source-grounded, versioned, applicable, reusable and inspectable** for humans and AI agents, including consumers of existing BI semantic layers. **The BI semantic layer disambiguates data; Sophon disambiguates governing requirements.** Sophon's **first practical wedge is a contract-to-existing-BI-semantic-layer compliance checker**, reusing definitions data teams have already built and verifying their meaning and native execution. BI is not a universal bottleneck: agents doing non-data work must be able to retrieve the same governing context **directly**.

Preserve **TRANSPOSE / TRACE / VERIFY / AUDIT**, authority and approval provenance, effective-time vs known-at chronology, explicit uncertainty and independent auditability. Sophon is **not** defined by any one consumer: it is not a contract classifier, legal workflow tool, agent configuration manager, **only** a BI compliance checker, or a new authorization gateway.

Jev, LLMs and reviewers are **replaceable proposers/challengers**, not authorities or proof of correctness. A model explanation is not an audit trail. A clause classification is not a successful transposition. Repeatedly reinterpreting a contract in each agent is not a shared normative layer.

## Task entry gate

Before implementing or recommending substantial work, write briefly:
1. **Which charter capability and §5 validation stage** the task addresses.
2. The exact authoritative or LAB_AUTHORED **source and version**, and the **shared normative artifact** being created, linked or checked.
3. The real **consumer and interface**: native BI semantic runtime, agent/workflow configuration boundary, or human-facing view. If a subcomponent is isolated, say so.
4. What can actually be verified, the independent oracle/baseline if correctness is claimed, and what remains unresolved.
5. Which prior result this builds on and why it does **not** change the product thesis.

**Implementation priority for a solo founder:** one real existing BI semantic metric checked against one external contractual definition, a real amendment and a reverse metric change, source-linked evidence and reproducible checks. Add a minimal read-only direct governing-context query for non-BI consumers; do **not** build a generalized agent control plane or multi-agent integration first. **Do not assume that most enterprise agents consume data through BI**: verify which actual agents do. Do not replace genuine native BI semantics with synthetic YAML or SQL-only fixtures.

## Experiment and implementation integrity

- Distinguish **proposed interpretation, genuinely authorized interpretation, mapped binding, approved change, deployed change, verified checks, and unverified behavior**.
- Preserve source hashes, exact citations, model/prompt/version and raw outcome where relevant, known-at and effective-at times, approvals, immutable/independently retrievable evidence and replayable reconciliation.
- Prevent future-information leakage across logs, agents, notes, worktrees and scored tasks. Freeze test corpora and independently authored oracles before scored runs.
- When testing BI, run **real native semantic executions** with actual data; SQL-only or fabricated YAML demos cannot support a claim of native integration.
- When testing agents, identify actual capabilities, deployment/configuration interfaces and observed controls; **prompt changes alone do not prove action enforcement**.
- Report formatting failures, semantic errors, reviewer objections, abstention, deployment status and compliance evidence **as separate quantities**.
- Preserve historical PRs/branches and negative findings (including the scoped Publicodes `STOP_KERNEL`). Do not infer product-wide GO/NO-GO from a component test.
- No automatic authorization from LLM agreement; no proprietary DSL, universal policy engine or multi-agent architecture without demonstrated need.

## Repo hygiene

Work on isolated branches; preserve historical documents and reports. New tasks and PRs reference the latest charter; old engineering plans remain scoped historical plans unless the owner explicitly renews them. Surface any conflict with these invariants for owner decision rather than silently drifting.
