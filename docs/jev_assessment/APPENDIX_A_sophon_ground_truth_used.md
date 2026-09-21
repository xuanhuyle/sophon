# Sophon fact base — FROM THE REAL REPOSITORY (github.com/xuanhuyle/sophon, main @ c8359ea, read 2026-09-21)

All of this is first-hand from the repo. Labels used in the repo: **ran** = executed and reproducible; **reported** = a packet claim the investigation could not check.

## 0. What Sophon is
A control layer that lets AI agents act under written policy and widen their autonomy as people resolve uncertainty. The repo is an INDEPENDENT ARCHITECTURE INVESTIGATION (21 Sep 2026) of whether that has a viable architecture, done from a supplied "packet" (`evidence/`, `evidence_followup/`) containing the earlier Sophon work. Domain used for evidence: UK parliamentary expenses (IPSA) plus a 48-case fictional expense-policy lab.

## 1. The standing conclusion (docs/REPORT.md §1, docs/DECISION.md)
1. **Do not build** the proposed control plane: no semantic compiler, no normative graph, no precedence engine, no purpose-built authorization kernel. **Buy enforcement**: a standard policy engine (Cedar or OPA) behind a gateway mediating tool calls.
2. **If anything is built, build only the thin layer**: a ledger of typed, dated grants, plus the workflow that turns a person's answer to an escalation into either a single-use permit (the default) or a proposal routed to whoever is empowered to make a rule. This is the one part not found in a shipping product.
3. **Do not commit even to that** until one real workflow shows escalation classes recur and the policy owner will settle them prospectively.
4. Several packet headline results do not show what they appear to.

## 2. The evidence that produced it (all **ran**)
- **Lab equivalence.** Two independently written arms over the same 48 cases: `lab/ledger_arm.py` (typed dated acts, issuer power checked at record time, exact-action permits) vs `lab/baseline_arm.py` (rules in code, settings/exceptions in data, every change a codeowner-approved commit, stateless decision function). Result: **0 disagreements across 1,440 settlements x 48 cases x 2 comparisons = 138,240 compared case decisions**. Ledger 20/20 on adversarial probes; disciplined baseline 20/20; first-pass baseline fails **10**, and each of the 10 is fixed by **exactly one** of five ordinary conventions. Sizes: 246 logical lines (ledger, fault hooks included) vs 243 (baseline with all five conventions). "There is no property here that requires a novel kernel, a normative graph, or a precedence engine."
- **The five conventions**: effective dating; typed ownership (power checked per kind of act, bounded delegation, no self-grants); version pinning (nothing live before adoption; settlements pinned to a policy version; an amendment suspends settlements it does not list as surviving); exact one-shot execution (permits bind case, beneficiary, category, amount cap and are consumed on first execution); closed surface (unrecognised action kinds go to a person).
- **Two more the evidence demands, not yet exercised in the lab**: (6) **grants are sufficiency statements** — written policy lists conditions and prohibitions and almost never says when an action IS allowed, so autonomy is the union of explicit grants and silence is never permission; (7) **facts carry provenance, and grants say what provenance they need** — system-observed / attested by an accountable person / asserted by the agent, and *"a grant may let the agent act alone only on facts it cannot author."*
- **Forecasts (docs/FORECAST.md, written before the probes existed)**: F1 identical decisions — 0 disagreements. F2 first-pass baseline fails 8–10 — actual 10, one miss (p10 as-of history). F3 each failure fixed by one convention — yes, all ten. F4 at most 12 of 24 held-out cases movable — actual **8**. F5 at least one seeded fault survives the probe suite on first run — worse: one survived and five probes detected nothing; after adding four faults and tightening p18, none survives.
- **20 probes** (`lab/probes.py`) drawn from the protocol's stop conditions, K1–K6 audit findings, and IPSA review boundary shapes: pre-adoption root, unratified proposal, K1 legitimacy, non-inflation, evidence clause, case-remedy spreading, expired exception, revoked act, superseded act, retrospectivity, effective-time reach, missing fact silently true, NaN bypass, reuse for a different amount/beneficiary, version timing, closed surface, power type, line items, as-of history, practice-is-not-a-grant.

## 3. The IPSA corpus study (**ran**; 46 public PDFs, 46/46 SHA-256 match; two model instances coded independently against a codebook written first; Cohen's kappa 0.78–1.0 by field, which for same-model coders shows low noise and says nothing about shared bias). Counts as [both coders, either coder] of 46:
| Finding | Count |
|---|---|
| Original decision changed at least in part | 23–24 (12 overturned, 12 partial) |
| Primary issue was discretionary relief or an exception | 18–20 |
| Primary issue was the meaning of a rule | 12–13 |
| Decision-maker stated a general reading that would decide future similar claims | 22–24 |
| ...and the same document expressly disclaimed precedent | 2 (5 disclaimers overall) |
| Decision-maker recommended a rule/guidance change | 17, of which IPSA **committed to 4** |
| **Outcome relied on facts gathered AFTER the original decision** | **16–20** |
| Claimant invoked past payments or staff advice | 24–26: rejected 15, accepted 5, partly 4 |
| Original decision mechanically decidable from the submission | 16–21; 5 of those were changed anyway |

Three architectural consequences drawn: (1) **the case resolver and the rule maker are different people with different powers** — a case answer defaults to that case, and a general reading in it is a *proposal* routed to whoever can ratify; this is the one mechanism in the Sophon thesis the real evidence supports; (2) the largest share of human work is **discretion on unique facts, which does not amortize**; (3) "it was paid before" is argued in over half of disputes and rejected about two times in three, so any design that learns from past approvals (precedent retrieval, LLM judge with memory) has that as its standing failure mode. Two same-year decisions treat past practice oppositely (Pound: constrained by 19 earlier payments; McDonagh: 25 earlier payments had "no bearing").

## 4. Recurrence / amortization evidence (**ran**)
- **1,000 real claim rows** (`results/recurrence.json`): coverage if one settlement covered every later claim of the same class — G1 category (7 classes) 99.3%; G2 category+cost type (67 classes) **93.3%**, median 5 claims per settlement, 22.4% never reused; G3 +short description (90) 91.0%; G4 +amount magnitude (174) 82.6%; G5 +normalised details (633 classes) **36.7%**, 86% never seen twice. Repetition is plentiful exactly where policy owners already use bright lines and scarce where disputes arise.
- **The owner's real Claude Code history** (`results/permission_log_study_ALL.json`; ran with permission; counts only; 9,404 tool calls, 56 sessions, 12 projects): L1 tool (50 settlements) 99.5% covered, 28% never reused, median 5; L2 tool+program (106) 98.9%, 18.9%, median 6; L3 +subcommand/folder (906) **90.4%**, **47.5% never reused**, median 2; L4 exact action (8,694) 7.5%, 96.1% never reused, median 1. Coverage does not grow over time at L3 (88.3 / 92.8 / 91.8 / 88.6% by quarter): new kinds of action arrive as fast as old ones repeat. A grant like "any python" is not a settlement, it is not asking.
- Outside: a 113-person study (Yan 2026, arXiv 2608.27443) found people pre-authoring agent permission policies chose "ask me" for **114 of 140 rules**, and those policies blocked 20 points less overreach than per-action approval.

## 5. Load-bearing assumptions and their verdicts (REPORT §3)
| | Assumption | Verdict |
|---|---|---|
| A1 | All consequential actions can be forced through one boundary | Untested |
| A2 | The facts a grant needs are observable when the action is taken | **Leans against**: the replay export lacks all three universal facts; 16–20 of 46 outcomes relied on later-gathered facts |
| A3 | People resolve uncertainty in reusable ways | **Weaker than the thesis assumes** |
| A4 | The written policy says when an action IS allowed | **False as a rule.** Autonomy must come from explicit grants, not from compiling the text |
| A5 | Wrong actions are costly and common enough to justify checking before acting | **False for expenses**: 997 paid / 1 not paid / 2 repaid in the 1,000 sample (**ran**); 18 not paid and 446 repaid of 82,787 (**reported**); median published dispute £584 |
| A6 | A deterministic kernel is safer than an LLM judge **when the facts it consumes are themselves extracted by an LLM** | **Open. It decides how much the kernel's guarantee is worth.** |
| A7 | The kernel is correct | Unverifiable, and matters little |
| A8 | Incumbents will not ship this first | The enforcement half is already shipped |

## 6. The audit of the packet (REPORT §4, **ran**)
- All six frozen hashes match; 46/46 PDF hashes match; the 1,000-row join recounts to 997/1/2.
- **The authority probe's guards**: 3 of 6 tests detect no mutation. A mutant that treats review outcomes and announced guidance as live grants — precisely what the case study says the probe guards against — still passes the whole suite, because those tests query a beneficiary (`OTHER_MP`) matching nothing.
- **The 1,000-claim replay**: `decide()` has a single return whose decision is the literal `"REQUEST_FACT"`. 100,000 fuzzed inputs all return it. It reads 2 of 17 feature fields. So "1,000 REQUEST_FACT / 0 CLEAR / 0 BLOCK" is true by construction, not an observation. The underlying judgment (the public export lacks the facts) is right by inspection.
- **K1–K6**: reported only, no code. 31 defect classes enumerated, none credited to the 50,000–100,000-case randomized runs; where the method is named it is post-freeze audit. K1 and K6 each passed a randomized run cleanly immediately before audit found five defects in each. Used as a **requirements list**, not as results.
- **The solo lab's own flaws**: the draft never says what IS reimbursable; two ambiguities missing from its open-issues list; `transport_alternative_available` and `after_2200_work` are columns with **no clause** (R12); all four celebration-meal cases include a tip or alcohol so none can ever clear as submitted; **the hard judgment is pre-digested** — "team celebration" vs "work planning meeting" arrives as a clean column, and that distinction is exactly what the Aquarone review turned on; **16 of 24 held-out cases never move under any of 1,440 settlements, ceiling 8**.

## 7. The lab's outcome vocabulary (already five-valued, `results/lab_results.json`)
Real ledger, unadopted and empty: **REQUEST_AUTHORITY x 48**. Conditional preview if the draft were adopted with zero settlements: **SEMANTIC_REVIEW 22, CLEAR 10, BLOCK 5, REQUEST_FACT 8, REQUEST_AUTHORITY 3**. So Sophon already distinguishes: cleared; blocked; a missing *fact*; a missing *authority*; and an unsettled *open term* needing semantic review. `lab/READING.md` maps each clause to which outcome fires when unmet.

## 8. Trust and failure boundaries (DECISION.md) — what the system can and cannot promise
| Boundary | Can | Cannot |
|---|---|---|
| Identity of issuers | Record the identity given and check its power | Authenticate anyone; lab uses plain strings |
| **Facts** | Record who supplied each fact; refuse grants whose provenance requirement is unmet | **Know that a fact is true. With an LLM agent supplying facts, the judgment moves into fact extraction. "This is the weakest point of every deterministic design, including this one."** |
| Completeness of a grant | Replay a proposed rule over past cases and show what changes | Prove the ratifier thought of every defeating condition |
| Mediation | Block what passes through the gateway | Anything reaching the tool another way |
| Tool effects | Detect a receipt that does not match the permit | Undo it |
| Discretion | Route to the right person, record the answer at the right scope | **Derive the answer** |
| Corpus | Cover the policy it was given | Know about a side agreement it was not given |

## 9. Approaches compared (REPORT §7)
- **A. Full Sophon control plane** (source tree, semantic AST, governance IR, authority graph, binding registry, runtime, gateway): fails by reported **71–77% recall** when compiling real rulebooks; largest surface; K-claims unverified. Must prove compiling beats hand-writing grants; the report's own evidence says no.
- **B. Policy-as-code + reviewed repo + gateway** (Cedar/OPA, PRs, decision logs): the floor. Without the five conventions it fails 10 of 20 probes. No escalation outcomes beyond allow/deny.
- **C. LLM judge over policy + retrieved precedents with sampled audit**: fails by precedent spreading; non-deterministic; cannot say who authorized an action. Plausible for cheap reversible actions.
- **D. Limits and after-the-fact audit**: useless for irreversible actions; it is how IPSA actually controls 99.9% of claims.
- **E. Thin grant ledger + typed settlement loop on top of B** — **recommended if anything is built**. Chosen over B for one reason only: a pull request is how an engineer changes a rule, not how a finance lead answers an escalation, and B gives that person no first-class choice between "this case only" and "propose a rule to whoever may make one" with replay before ratification. **"If that workflow turns out not to matter, B is the right answer and Sophon is a set of conventions worth publishing, not a product."**

## 10. What is already shipped (REPORT §7; sub-agent research, ✔ = source re-read)
Amazon Bedrock AgentCore Policy ✔ converts single plain-English rules to Cedar, checks them with automated reasoning, enforces default-deny on every gateway tool call, session-scoped temporal conditions. Microsoft Agent Governance Toolkit: allow / deny / require-approval with Rego or Cedar, hash-chained logs. Auth0 binds asynchronous human approval to transaction details. Permit.io separates one-time operation approvals from standing access grants. Ramp ✔ ships the nearest incumbent loop: detected ambiguity becomes a suggested edit to the natural-language policy which a permitted admin publishes. **No product found with typed, versioned interpretations and exceptions carrying who / when / what-power, nor the REQUEST_FACT and SEMANTIC_REVIEW outcomes.** PolicyLayer aims at the same "system of record for agent authority" position for coding agents; maturity unverified. Confidence the niche is unoccupied: ~65%, "and I would not go higher".
Prior art the packet does not cite: XACML PEP/PDP/PAP/PIP and its administrative delegation profile; KeyNote and SPKI (=K1); macaroons and Biscuit (=K6 attenuated one-shot permits); Catala and Rules-as-Code (closest working "law to code with exceptions" practice — and they pair a lawyer with a programmer, clause by clause).

## 11. What would change the recommendation (DECISION.md; numbers proposed, to be fixed before measuring)
**Towards build nothing**: under 1 in 5 escalations leads to a reusable settlement within a quarter, or a settlement decides a median of fewer than ~10 later actions; the policy owner cannot or will not settle prospectively; wrong clearances traced to wrong facts are as common as an LLM judge's wrong clearances on the same cases; AWS, Microsoft, Ramp or PolicyLayer ships case-versus-rule settlement with issuer provenance.
**Towards build more**: a probe from a real workflow that the disciplined baseline cannot pass without re-implementing a graph of norms (none of the 20 is one; candidates are several independent rule-makers whose acts conflict often, or deep delegation chains); a domain where compiling the rulebook clearly beats hand-ratifying grants.
**Towards the framing is wrong**: the design partner's pain turns out to be audit reconstruction after the fact, not autonomy before it — then the product is a decision log with provenance and the settlement loop is secondary.

## 12. The three genuinely open questions (REPORT §8)
1. **Is there a workflow where checking before acting pays?** Needs costly or irreversible actions, a refusal rate not near zero, and facts the system can observe itself. **Expenses fail all three.** Candidates: refunds and credits above a threshold, access grants, payment release, contract concessions, outbound data sharing.
2. **Do policy owners settle classes of escalation prospectively?** Expect slower and rarer than hoped, through a different person than the one handling the case.
3. **Does fact extraction erase the kernel's guarantee?** Needs real case narratives with a human-made fact sheet.
Next steps in order: the recurrence study (done, leans against); do NOT spend time on the 48-case lab as designed (its outcome metrics cannot separate the architectures, reuse ceiling 8); **then one design partner instrumented for S3–S5 against approach B**.

## 13. The earlier packet's own conclusions (evidence/Sophon_Technical_Viability_Report_2026-09-21.md) — this is what the owner means by "Sophon components"
- The original strong thesis (automatically compile arbitrary natural-language rulebooks into correct executable controls) **failed repeated real-corpus tests**: material rules, branches, scopes and open standards were missed or falsely determinized. Internal recall ~77% (Yale) and ~71% (a forward-construction plus coverage-search architecture). FAR test post-freeze audit still found inherited agency scope lost, open standards falsely determinized, required record-field enumeration collapsed, hidden residual semantics.
- *"A second coverage model does not solve the problem if both models share the same semantic blind spots."*
- **"Runtime enforcement is comparatively easy. Reliable semantic compilation is the load-bearing problem."** (still valid after K1–K6)
- The resulting safe architecture: DOCUMENT → SOURCE TREE → PROPOSED SEMANTIC AST → coverage/adversarial verification → unresolved disagreement exposed → AUTHORIZED RATIFICATION → GOVERNANCE IR → DETERMINISTIC RUNTIME. An AI-generated interpretation is **PROPOSED, never AUTHORITATIVE**, unless established by direct source entailment, explicit authoritative binding, properly authorized human interpretation, properly authorized precedent, or a properly authorized amendment/exception/implementation rule.
- **"This separates model confidence from normative authority. They must never be collapsed."**
- Typed AST model: ACTOR/SCOPE → DEONTIC MODALITY → ACTION → AND/OR/IF/ONLY_IF/UNLESS/EXCEPT → MODIFIER/EVIDENCE/EFFECT → OPEN_STANDARD/BINDING.
- Product insight: organizational authority is a hierarchy of normative objects (foundational authority → policies/contracts → implementation rules → authorized interpretations → exceptions/waivers → individual decisions → review/appeal decisions → precedents/settled practices); a rule acquires operational meaning through later authoritative acts with different normative force.
- The packet's own closing: the unresolved existential question is **economic rather than purely technical** — can human interpretation be sufficiently amortized, and can enough real enterprise authority be made observable and executable to create material autonomous-agent coverage. Next step: one real bounded workflow, not more synthetic kernel tests.

## 14. Direct hooks for the owner's Jev questions
- **Problem A (authority → trusted executable semantics)** is the *semantic compiler*, already judged the load-bearing failure (71–77% recall) and already excluded from the recommendation (approach A rejected). The governing rule is "model confidence ≠ normative authority".
- **Problem B (fuzzy factual predicates)** is **A6 / S5 / open question 3** — fact extraction — named the weakest point of every deterministic design. The owner's example, "Was public transport reasonably unavailable?", is literally `transport_alternative_available` in `evidence/sophon_solo/cases.csv`: an orphan column with no clause (R12), one of the pre-digested facts the report criticises. Values in the 48 cases: 36 blank, 8 yes, 4 no.
- **Problem C (deterministic execution)** is settled by the 138,240-decision equivalence: buy Cedar/OPA + gateway, apply five conventions. The remaining question is what feeds it.
- **Problem D (missing evidence)** is the 16–20 of 46 outcomes that relied on facts gathered after the original decision, plus the existing five-outcome vocabulary (CLEAR / BLOCK / REQUEST_FACT / REQUEST_AUTHORITY / SEMANTIC_REVIEW) and convention 7 on fact provenance.
- **The moat question** is already answered negatively for everything except the grant ledger + settlement workflow (§9 E, §10), and that answer was reached *without reference to Jev*.
