# Agent instructions — Sophon

Before taking action in this repository, read **[SOPHON_CHARTER.md](SOPHON_CHARTER.md)**. It is the owner-defined product direction for new work, not evidence of a proven market or implementation.

Core invariants:
- Sophon is **AI-native governance infrastructure**, not a more capable LLM.
- It operates **through an organization's existing semantic layer**, connected to the data systems; do not replace that layer.
- The four capabilities **TRANSPOSE / TRACE / VERIFY / AUDIT** must remain part of the product vision.
- Persistent evidence, human-authorized interpretations/approvals, two distinct times (known-at and effective-at), independent reproducible verification, and explicit UNKNOWN/coverage are essential.
- Distinguish infrastructure feasibility from reliability, operational usefulness and adoption. Never generalize a narrow `STOP_KERNEL` result beyond its actual tested mechanism.
- Read the actual prior experiment results, preserve their negative findings and their limitations.
- Do not quietly redefine product scope, invent authority or claim downstream agent behavior was proved by a passing semantic query.
- A material change to the charter requires an explicit owner decision and a versioned decision record.

For Claude Code-specific workflows, also read [CLAUDE.md](CLAUDE.md).
