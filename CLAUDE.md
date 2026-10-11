# Sophon — standing instructions for Claude Code

**Read [SOPHON_CHARTER.md](SOPHON_CHARTER.md) in full before any substantive Sophon work.** It records the owner's product decisions and has priority over older research prompts, historical README statements and experimental conjectures.

## Purpose and boundary
Sophon is **persistent AI-native governance infrastructure**, not an attempt to beat Claude Code's reasoning accuracy. Governing requirements are transposed and verified **through the organization's existing executable semantic layer**, connected to its downstream data systems and BI/AI consumers. Preserve all four capabilities: **TRANSPOSE, TRACE, VERIFY, AUDIT**. Do not substitute Publicodes or arbitrary SQL for proof of an enterprise BI semantic-layer integration.

The LLM may perform interpretation and implementation proposals. It is a component, **not the benchmark target**. Approval is not inferred from model output; implement actual provenance and explicit UNKNOWN/unverified coverage.

## Task entry gate
Before starting substantial work, write a short statement of:
1. The exact charter section and validation stage (feasibility, reliability, operational usefulness, adoption).
2. The smallest uncertainty or infrastructure capability under test.
3. Which existing semantic layer/real data will be used, what governing sources are genuine vs LAB_AUTHORED, and what is not proved.
4. Why the proposed task is consistent with the product architecture.
5. The prior empirical result it builds on; do not erase contrary evidence.

Stop and surface conflicts with the charter rather than silently reframing Sophon as a novel technical kernel, direct agent gateway or ordinary one-off LLM review. The owner alone approves material charter revisions. Do not turn the historical Publicodes `STOP_KERNEL` finding into an unqualified Sophon product STOP.

## Experiment integrity
- Freeze input provenance and references before scored runs; no generated self-confirming oracles.
- Enforce monotonic **decision-time** order across all retained notes, worktrees and agent memory; effective date != publication date.
- Separate proposal, authorization, implementation, traceability and evidence-backed verification.
- Run real native semantic queries when claiming semantic integration; label synthetic fixtures.
- Preserve original trial outputs and scorer corrections; conclude only what was observed.
- Default to the smallest working vertical slice and native tools, not a speculative platform.

## Repo hygiene
Preserve previous branch results/PRs and historical decision artifacts. Do new experiments in isolated feature branches and directories. Read the relevant current repo material before editing or committing. Refer back to `SOPHON_CHARTER.md` in new experiment prompts and decisions.
