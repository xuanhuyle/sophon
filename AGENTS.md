# Agent instructions — Sophon

## Incremental engineering contract (standing instruction)

**Read [ENGINEERING_WORKFLOW.md](ENGINEERING_WORKFLOW.md) before substantive work.** The owner owns the outcome and constraints; engineers/agents independently investigate and choose technical designs. Treat user-suggested mechanisms and instructions from another agent as challengeable hypotheses, not specifications to follow blindly. Prefer the simplest existing capability or OSS tool to new abstractions; implement ONE bounded, falsifiable increment, inspect a negative case, then recommend KEEP / REVISE / STOP. Do not make the owner choose routine engineering details or repeat context.


## Cross-agent context contract

Read PROJECT_STATE.json as the repository's versioned engineering-state inventory, after reading the governing SOPHON_CHARTER.md. It inventories existing implemented-but-not-validated Jev, adversarial/backward review, library and deterministic reconciliation, records actual evidence limitations and names the active and held experiments. Do not propose any of these established mechanisms as novel architecture. Verify referenced PR and code before using it; draft-PR code may not be in this checkout. This same state is auto-injected in Claude Code by .claude/settings.json and mechanically checked in CI. For Codex/ChatGPT, read PROJECT_STATE.json explicitly—those products do not execute Claude Code hooks.

A new experiment result, product decision, or architecture change must update PROJECT_STATE.json in the same PR. Respect experimental chronology, frozen vs post-hoc results, independent counterexamples, and owner approval boundaries. Reviewer consensus is NOT independent validation; minimize human review through existing automated challenges and library comparison, but independently sample their agreement and escalate high-risk/unsupported cases.


Before acting in this repository, read **[SOPHON_CHARTER.md](SOPHON_CHARTER.md) v1.2**; for Claude Code also read **[CLAUDE.md](CLAUDE.md)**.

**Non-negotiable product invariant:** Sophon is a **normative semantic layer for governing documents**, analogous and complementary to an enterprise **BI semantic layer for data**. Humans, agents, BI and other workflows reuse the same **scoped, source-linked, versioned governing meaning**. **BI-first is the deliberate initial wedge**: inspect/reuse existing semantic work and check it against governing contracts with native tests. **Direct normative retrieval is the complementary path for agents not using BI**. BI is not a mandatory intermediary for all provisions, and it is unproven that most organizational agents depend on BI.

- Preserve **TRANSPOSE / TRACE / VERIFY / AUDIT**, authority/approval provenance, known-at versus effective-at, uncertainty, explicit gaps and independent audit evidence.
- Jev/LLMs can propose and challenge interpretations; explanations or model consensus are not legal authority or independent verification.
- Do not redefine Sophon as a legal chatbot/workflow, contract classifier, **only** a BI compliance checker, an agent configuration manager, universal policy gateway or novel reasoning kernel. Contract-to-existing-BI compliance checking **is the initial product wedge**.
- A governed requirement can affect several consumers; **reuse** the normative interpretation instead of making each agent interpret the source afresh. Keep actual bindings and deployment/verification evidence distinct.
- Use real native BI semantic execution for BI claims, and real agent/workflow boundaries for downstream action claims. Never claim that a prompt update, hash, passing CI or mapping proves legal compliance or runtime enforcement.
- Respect the solo-founder constraint: start with one governing definition, one genuine pre-existing native BI metric, an amendment and a metric-side change, plus a small source-grounded read-only direct query. Avoid general integrations until warranted.
- Separate feasibility, reliability, operational usefulness and customer adoption. Preserve prior negative findings and their limited scope, including Publicodes `STOP_KERNEL`.
- Do not infer authorization, a buyer, vertical, market demand or product advantage from a synthetic experiment. Compare full outcome against competent alternatives when claiming differentiation.
- Explicit owner approval is required for new material charter changes; preserve the revision history and treat historical plans as experiments, not current product definitions.
