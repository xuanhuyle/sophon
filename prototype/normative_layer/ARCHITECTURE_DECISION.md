# ADR-P0 — Exploratory normative semantic layer walking skeleton

**12 October 2026 · PROPOSED, NOT A CHARTER REVISION**

### Context

The product concept has expanded from verifying BI semantic metrics against governing clauses to offering an **agent-consumable normative semantic layer**. Source documents remain the externally owned governing texts. The layer records proposed and lab-authorized interpretations, applicable versions, unknowns and operating facts. This is an architectural exploration, not an assertion that formalized rules supersede governing documents or acquire legal authority.

### Experimental architectural choice

Build the smallest complete path: `contract/policy text → automated limited extraction → proposed clauses → simulated approval → SQLite versioned normative model → loopback JSON API → two different clients → amendment ingestion/approval → changed agent results + audit`. Use stdlib only. No compiler, custom language, graph database, general autonomous legal reasoner, payment tool, or network-facing enforcement.

### Key distinctions

- Document known/effective/approved dates are different. An amendment **ingested** is never automatically **approved**.
- A contractually established right is not a delegation of payment authority. `execution_authorized=false` is unconditional in V0; any actual execution requires a separate trusted guard and authenticated authorization.
- Unrecognized language is `UNRESOLVED`, not silently dropped. The narrow grammar gives no assurance of contract completeness.
- Extracting candidate meaning is not proving legal validity. Approvals are self-asserted labels for a lab exercise, not real authentication or signature verification.
- Numeric operational facts are caller-supplied proxies, not independently observed; this is not proof of downtime or credit entitlement.
- Source excerpts and hashes show provenance within an ordinary mutable SQLite file, not independent audit integrity.

### Relation to previous experiments and Rulebook

E0–E5 concern native BI semantic transposition and verification; this branch does not rewrite their findings and is **not** stacked on them. Rulebook Parts I–IV warn that linguistic ambiguity survives formalization and that encoding is only one activity among interpretation, binding, validation, ownership and maintenance. V0 intentionally prioritizes **end-to-end interoperability and version propagation**, while providing no broader semantic fidelity claim.

### What to learn next

Does the same interface remain useful when confronted with a *second independently authored text*, an ambiguous exception and a genuine operational data binding? This is not yet demonstrated. Capture failures first, then iterate. Explicit owner ratification required before broadening the binding Sophon Charter.
