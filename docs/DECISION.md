# Decision record: what to build, if anything

Status: **recommendation, 21 September 2026.** Evidence is in `docs/REPORT.md`. This file is the part to argue with.

## Decision

1. **Do not build** a semantic compiler, a normative graph, a precedence engine, or a purpose-built authorization
   kernel. Buy or reuse enforcement: a standard policy engine (Cedar or OPA) behind a gateway that mediates the tool calls.
2. **If anything is built, build only the thin layer** that existing products lack: a ledger of typed, dated grants,
   and the workflow by which a person's answer to an escalation becomes either a single-use permit or a proposal to
   whoever is empowered to make a rule.
3. **Do not commit to building even that** until one real workflow shows that classes of escalation recur and that
   the policy owner will settle them prospectively (section "What would change my mind").

## The architecture, in one picture

```text
   agent ──proposes action──▶ GATEWAY (bought: mediates every tool call, default-deny,
                                │        one effect per exact action, fresh check at execution)
                                ▼
                          POLICY ENGINE (bought: Cedar / OPA) ◀── compiled from ──┐
                                │                                                  │
             inside a grant ────┤                                          GRANT LEDGER (built)
                 CLEAR          │ outside every grant                      append-only typed acts:
                                ▼                                          adopt · interpret · relax/add constraint ·
                       ESCALATION to a person                              case exception · delegate · amend · revoke
                       "missing fact / missing approval /                  each with issuer, power relied on, policy
                        unsettled term / conflict"                         version, recorded-at, effective-from, expiry
                                │                                                  ▲
                                ▼                                                  │
                       SETTLEMENT (built)                                          │
                       default: permit for THIS exact action, single use ──────────┤
                       optional: "this should be a rule" ─▶ PROPOSAL ─▶ replay over past cases
                                                            ─▶ ratified by someone whose power covers it ─┘
```

Built code is the ledger, the settlement workflow, and a compiler from grants to the bought engine's language. In
lab form the ledger is about 250 lines (`lab/ledger_arm.py`). Five rules make it safe, and each is there because removing
it breaks a specific probe (`results/lab_results.json`):

1. **Effective dating.** Every act has a recorded time and an effective time; effective is never earlier than
   recorded; a settlement must be in force when the action happened *and* when it is decided.
2. **Typed ownership.** Power is checked per kind of act, when the act is recorded, against bounded delegations.
   Nobody grants to themselves. An interpretation can only fill a declared open term; it cannot move a threshold.
3. **Version pinning.** Nothing is live before an adoption. Every settlement names the policy version it was made
   for. An amendment suspends every settlement it does not list as surviving.
4. **Exact, single-use permits.** A case answer binds case, beneficiary, category and amount cap, and is consumed by
   the first execution.
5. **Closed surface.** An unrecognised kind of action goes to a person.

Two more that the evidence demands and the lab does not yet exercise:

6. **Grants are sufficiency statements.** Written policies list conditions and prohibitions; they almost never say
   when an action *is* allowed. Autonomy is the union of explicit grants, and whether "meets every clause" is enough
   is itself something the owner must adopt. Never compile a rulebook and treat silence as permission.
7. **Facts carry provenance, and grants say what provenance they need.** System-observed (amount, payee, approver
   identity, time, running totals), attested by an accountable person, or asserted by the agent. A grant may let the
   agent act alone only on facts it cannot author.

## Trust and failure boundaries

| Boundary | What the system can promise | What it cannot |
|---|---|---|
| Identity of issuers | Records the identity it was given and checks that identity's power | Authenticate anyone. The lab uses plain strings. Production needs signed acts or SSO. |
| Facts | Records who supplied each fact and refuses grants whose provenance requirement is unmet | Know that a fact is true. With an LLM agent supplying facts, the judgment moves into fact extraction. **This is the weakest point of every deterministic design, including this one.** |
| Completeness of a grant | Replays a proposed rule over past cases and shows what changes | Prove the ratifier thought of every defeating condition. The ratifier owns that. |
| Mediation | Blocks what passes through the gateway | Anything that reaches the tool another way |
| Tool effects | Detect a receipt that does not match the permit | Undo it |
| Discretion | Route to the right person and record the answer at the right scope | Derive the answer. In the IPSA reviews the same year produced opposite treatments of past practice. |
| Corpus | Cover the policy it was given | Know about a side agreement it was not given |

## Why this and not the strongest alternative

The strongest alternative is **policy-as-code in a reviewed repository behind a gateway**. It is technically equal:
with the five conventions it passes all 20 probes and agrees with the ledger on all 138,240 compared decisions. I
recommend the thin layer over it for one reason only. A pull request is how an engineer changes a rule. It is not
how a finance lead answers an escalated case, and it gives that person no way to say "this case only" as the safe
default, or "this should be a rule, send it to whoever can decide". The IPSA reviews show that this split is how real
authority works: about half of the case decisions contain a reusable reading, the person deciding the case cannot
make it binding, and 4 of 46 became a committed rule change. If that workflow proves not to matter, the alternative
wins outright and Sophon reduces to five conventions worth publishing.

I prefer it to an **LLM judge with remembered precedents** wherever actions are costly, because claimants argued
"it was paid before" in over half of the reviewed disputes and were refused about two times in three. A design that
learns from past approvals inherits that error. For cheap, reversible actions the LLM judge, or plain spending limits
with after-the-fact audit, is the better choice, and no control plane is needed.

## What would change my mind

**Towards "build nothing"** (the numbers are my proposal; fix them before measuring, not after):
- In a real workflow, under 1 in 5 escalations leads to a reusable settlement within a quarter, or a settlement
  decides a median of fewer than about 10 later actions.
- The policy owner cannot or will not settle prospectively (the Yan study's participants chose "ask me" for 81% of rules).
- Wrong clearances traced to wrong facts are as common as an LLM judge's wrong clearances on the same cases.
- AWS, Microsoft, Ramp or PolicyLayer ships case-versus-rule settlement with issuer provenance.

**Towards "build more than the thin layer":**
- A probe, drawn from a real workflow, that the disciplined baseline cannot pass without re-implementing a graph of
  norms. None of my 20 is one. The candidates would be several independent rule-makers whose acts conflict often, or
  deep delegation chains.
- A domain where compiling the rulebook clearly beats hand-ratifying grants. The report's own recall figures
  (71–77%, reported) say this is not it.

**Towards "the framing is wrong":**
- The design partner's pain turns out to be audit reconstruction after the fact, not autonomy before it. Then the
  product is a decision log with provenance, and the settlement loop is secondary.

## Next action

`docs/OWNER_REQUEST.md`: one permission (run the recurrence study on your own agent history), and, only if you want
to exercise the mechanism end to end, six decisions on the draft lab policy.
