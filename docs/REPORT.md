# Sophon: independent architecture investigation

21 September 2026. Written by Claude Code from the packet in `evidence/` and `evidence_followup/`, working alone.
Everything labelled **ran** was executed in this repository and can be re-run (see `README.md`). Everything labelled
**reported** is a claim I could not check.

## 1. The answer

**Do not build the control plane the viability report proposes.** Its deterministic kernel is not where the
novelty or the risk is. In a runnable comparison, a competent policy-as-code setup gave the same decision as a
purpose-built authority ledger on every one of 138,240 case decisions, and matched it on all 20 adversarial
properties once five ordinary engineering conventions were added. Deterministic enforcement at an agent gateway is
also already a shipping commodity.

**What might be worth building is thin:** a ledger of typed, dated grants and the workflow that turns a person's
answer to an escalated case into either a single-use permit (the default) or, by a separate act of someone empowered
to do it, a reusable rule. That sits on top of an existing policy engine and gateway. It is the one part I could
not find in a shipping product.

**Whether even that is a product is genuinely open, and cannot be settled alone.** The real evidence in the packet
leans against the amortization thesis more than the prior reports admit, and nothing available here measures the
economics. Section 8 says what would settle it.

## 2. The problem, stated so it can fail

For one bounded family of agent actions that pass through a single mediated tool boundary, keep an explicit, dated
record of who has granted the agent what, so that:

1. the agent acts alone exactly when the action falls inside a grant made by someone empowered to make it, in force
   when the action happens, whose conditions are all met by facts of adequate provenance;
2. everything else goes to a person, whose answer by default authorizes only that exact action, and widens future
   autonomy only through a separate, explicitly scoped act by someone with the power to widen it;
3. any executed action can be traced to the grants, facts, fact sources and policy version it relied on.

| | Success criterion | Can this solo exercise test it? |
|---|---|---|
| S1 | Nothing executes outside a grant (no silent authority, no spreading, no replay, no retroactivity). | Yes, as a mechanism property. Done: section 6. |
| S2 | Who / when / what / which-version is reconstructable per action. | Yes. Done, as-of queries in probes p08, p10, p19. |
| S3 | Reusable settlements decide enough later actions, at few enough human minutes, to beat case-by-case review. | **No.** Needs a real recurring workflow and a real authority holder. |
| S4 | Fewer human minutes or fewer wrong actions than the best alternative at equal coverage. | **No.** The lab cannot separate the architectures on outcomes (section 6). |
| S5 | Wrong clearances caused by wrong *facts* stay below a stated rate. | **No.** Needs real case narratives; synthetic ones would be circular. |

## 3. Load-bearing assumptions and what the packet actually says about them

| | Assumption | Evidence that bears on it | Verdict |
|---|---|---|---|
| A1 | Consequential actions can all be forced through one boundary. | None. K6 is synthetic and its code is absent. | Untested. |
| A2 | The facts a grant needs are observable when the action is taken. | The replay's export lacks all three universal facts (by inspection; the script itself proves nothing, see 4.3). In the 46 reviews, 16–20 outcomes relied on facts gathered *after* the original decision. | Leans against, in this domain. |
| A3 | People resolve uncertainty in reusable ways. | Mixed, and the most important row. See section 5. | Weaker than the thesis assumes. |
| A4 | The written policy says when an action *is* allowed. | It does not. The draft lab policy and the 23 curated IPSA propositions are all conditions and prohibitions; neither states a sufficient condition. | **False as a rule.** Autonomy has to come from explicit grants, not from compiling the text. |
| A5 | Wrong actions are costly and common enough to justify checking before acting. | Bundled sample: 997 paid, 1 not paid, 2 repaid (**ran**). Full file: 18 not paid and 446 repaid of 82,787 (**reported**). Median amount in a published dispute: £584 (**ran**). | False for expenses. Spending limits plus after-the-fact audit is the rational control there. |
| A6 | A deterministic kernel is safer than an LLM judge when the facts it consumes are themselves extracted by an LLM. | None in the packet. One outside survey finds 74% of agent safety requirements symbolically enforceable (secondary source, not checked by me). | Open. It decides how much the kernel's guarantee is worth. |
| A7 | The kernel is correct. | Reported only; see 4.4. | Unverifiable, and it matters little (section 6). |
| A8 | Incumbents will not ship this first. | Section 7. | The enforcement half is already shipped. |

## 4. Audit of the packet

`python -B audit/audit_packet.py` reproduces 4.1–4.3 and writes `results/audit_packet.json`.

**4.1 Integrity (ran).** All six frozen hashes match. The bundled 1,000-row join recounts to 997 / 1 / 2. All 46
PDFs were fetched from the official URLs and **46 of 46 SHA-256 hashes match the inventory**. I read the Davies
review myself: the 17th edition applied, the 18th later lifted the newsletter ban, 50% was funded, and paragraph 48
says the decision is "not a precedent". The inventory's keyword counts (22 / 24 / 1, median 18,021 characters)
reproduce from its JSON. One correction to my own first guess: the documents titled "Statement of Findings" are not
misconduct investigations. Both coding passes found that all 45 Compliance Officer documents are reviews of a
refused or recovered claim; the 46th is the tribunal decision.

**4.2 The authority probe's guards (ran).** Three of the six tests detect no mutation of the code under test. One
mutant treats review outcomes and announced guidance as live grants, which is precisely what the case study says the
probe guards against; **the whole suite still passes**. The cause is that those tests query a beneficiary
(`OTHER_MP`) that matches nothing, so they cannot fail. The report's claims 4–6 (Aquarone, Kawczynski, Davies) are
correct statements about the documents but are not tested by the code.

**4.3 The 1,000-claim replay (ran).** `decide()` has a single `return` whose decision is the literal
`"REQUEST_FACT"`. 100,000 fuzzed inputs, including a "party political donation" and a parking fine, all return it.
It reads 2 of the 17 feature fields and produces 11 distinct outputs over the 1,000 rows. So "1,000 `REQUEST_FACT`,
0 `CLEAR`, 0 `BLOCK`" is true by construction. The label-blind freeze, the hash and the sample size add nothing to
it, and the guard test that flips `Status` cannot fail because `Status` is never read. The author's underlying
judgment, that the public export lacks the facts, is right by inspection of the columns. It should be presented as
that judgment, not as an observation from 1,000 transactions.

**4.4 K1–K6 (reported; no code supplied).** The report enumerates 31 defect classes across the six kernels and
credits none of them to its 50,000–100,000-case randomized runs. Where it names the method (K1, K3, both K6 rounds)
it is post-freeze audit. K1 and K6 had each just passed a randomized run cleanly when audit found five defects in each. The final "zero errors" results are the same kind of evidence as the
results that were later overturned, and an oracle written by the same author shares the same blind spots. The
report draws exactly that lesson about its semantic compiler ("a second coverage model does not solve the problem")
but not about its kernel. I use K1–K6 as a **requirements list**, which is what my probes are built from, and not
as results.

**4.5 The solo lab (ran; `lab/READING.md`, `results/lab_results.json`).**

- The draft never says what *is* reimbursable, so whether "meets every clause" is enough must itself be adopted.
- Two ambiguities are missing from its own list of open issues: whether meals and equipment need manager approval
  at all, and whether "applies from its effective time" means expenses incurred or decisions made after it.
- `cases.csv` carries `transport_alternative_available` and `after_2200_work`, but no clause uses them.
- All four celebration-meal cases include a tip or alcohol, so no case-specific approval can ever clear one as submitted.
- The hard judgment is pre-digested: "team celebration" versus "work planning meeting" arrives as a clean column,
  and that distinction is what the Aquarone review turned on.
- **16 of the 24 held-out cases never move under any of 1,440 possible settlements; the ceiling on cases a settlement
  can newly clear is 8** (3 hotel, 3 meal, 2 equipment). The protocol's "reuse" number is a function of where the
  owner puts a threshold relative to amounts the generator chose.

## 5. How real authority resolves real uncertainty (ran)

I had two instances of the model code all 46 documents independently against a codebook written before either saw a
document (`corpus_study/CODEBOOK.md`), neither having seen the follow-up packet. Agreement was high (Cohen's kappa 0.78–1.0 by field), which for
same-model coders shows low noise and says nothing about shared bias. The codings are consistent with the follow-up's 13
hand-checked cases (side by side in `results/corpus_study.json`). Counts are given as [both coders, either coder] of 46.

| Finding | Count |
|---|---|
| Original decision changed at least in part | 23–24 (12 overturned, 12 partial; one informal reversal coded differently by the two passes) |
| Primary issue was a request for **discretionary relief or an exception** | 18–20 |
| Primary issue was the **meaning of a rule** | 12–13 |
| Decision-maker stated a **general reading** that would decide future similar claims | 22–24 |
| …and the same document expressly **disclaimed precedent** | 2 (Snell, Frith); 5 disclaimers overall |
| Decision-maker **recommended** a change to rules or guidance | 17, of which IPSA **committed** to 4 |
| Outcome relied on **facts gathered after** the original decision | 16–20 |
| Claimant invoked **past payments or staff advice** | 24–26: rejected 15, accepted 5, partly 4 |
| Original decision was mechanically decidable from the submission | 16–21; 5 of those were changed anyway |

This corrected my own prior. From the packet's five cases I expected adjudicators almost never to generalize. In
fact about half of these decisions contain a reusable reading. What is scarce is **the power to make it binding**:
the Scheme says a determination binds no later claim, the reviewer can only recommend, and 4 of 46 disputes led to a
committed change. Two decisions from the same year treat past practice in opposite ways: in Pound the officer felt
constrained by 19 earlier payments, and in McDonagh 25 earlier payments had "no bearing".

Three consequences for the architecture:

1. **The case resolver and the rule maker are different people with different powers.** A case answer must default
   to that case. A general reading found in it is a *proposal* routed to whoever can ratify it. This is the one
   mechanism in the Sophon thesis the real evidence supports.
2. **The largest share of human work is discretion on unique facts, which does not amortize.**
3. **"It was paid before" is argued in over half of disputes and rejected about two times in three.** Any design that
   learns from past approvals (retrieval of precedents, an LLM judge with memory) has this as its standing failure mode.

**Recurrence in 1,000 real claims (ran, `analysis/recurrence.py`).** If one settlement covered every later claim
of the same class, coverage would be 93% with classes defined by category and cost type (67 classes), and 37% with
classes defined by what was actually bought (633 classes, 86% never seen twice). A 1.2% sample thins repeats, so the
fine-grained figure is pessimistic; the ordering is the result. Repetition is plentiful at exactly the level the
policy owner already governs with bright lines, and scarce at the level where disputes actually arise.

**Outside evidence (found by a research sub-agent; I re-read only the items marked ✔).** A 113-person study ✔ found
that people asked to pre-author permission policies for an agent chose "ask me" for 114 of 140 rules, and that the
policies blocked 20 points less overreach than per-action approval
([Yan 2026](https://arxiv.org/abs/2608.27443)). Ramp ships the nearest incumbent loop ✔: detected ambiguity becomes a
suggested edit to the natural-language policy, which a permitted admin publishes
([Ramp](https://support.ramp.com/hc/en-us/articles/49015569046547-Policy-Suggestions-the-Policy-Agent)).
A sub-agent claim about a second paper did not match its abstract when I checked, and I dropped it.

## 6. The validation exercise I ran, and what it could have shown

**Question.** Is a purpose-built authority kernel warranted over a competent existing approach? This is the one
architectural question that can be answered without another person, and the prior reports assume the answer.

**Design.** Two independently written arms over the same 48 cases and the same reading of the draft policy:
`lab/ledger_arm.py` (typed, dated acts; issuer power checked when recorded; exact-action permits) and
`lab/baseline_arm.py` (rules in code, settings and exceptions in data files, every change a commit approved by a
codeowner, a stateless decision function). The baseline can switch on five conventions one at a time. Twenty probes
come from the protocol's stop conditions, from K1–K6's audit findings, and from the boundary shapes in the IPSA
reviews. All authority in the lab is fixture authority in memory; the real ledger
(`lab/ledger/owner_acts.json`) is empty and returns `REQUEST_AUTHORITY` for all 48 cases. I wrote my forecasts
before writing the probes (`docs/FORECAST.md`).

| | Forecast | Actual |
|---|---|---|
| F1 | Arms agree on all 48 cases for every settlement. | **0 disagreements** in 1,440 settlements × 48 cases × 2 comparisons. |
| F2 | Ledger 20/20; disciplined baseline 20/20; first-pass baseline fails 8–10, and I named nine. | Ledger 20/20; disciplined baseline 20/20; first-pass baseline fails **10**. I was wrong about one: I expected as-of history (p10) to pass. |
| F3 | Each baseline failure is fixed by exactly one convention. | **Yes**, all ten. |
| F4 | At most 12 of 24 held-out cases can be newly cleared. | **8.** |
| F5 | My probe suite leaves at least one seeded fault undetected on first run. | **Worse than forecast**: one fault survived and five probes detected nothing (`results/mutation_first_run.json`). After adding four faults and tightening p18, every probe detects at least one of 21 faults and none survives. |

The five conventions, and what each one fixes:

| Convention | Fixes |
|---|---|
| **Effective dating**: settings carry an effective date separate from commit time, never backdated | backdating, future-dated rules, a later rule reaching an earlier expense |
| **Typed ownership**: who may change what is checked per kind of change, with bounded delegation | unbounded delegates, self-dealing, a "clarification" that moves a spending threshold |
| **Version pinning**: nothing is live before adoption; each setting is pinned to the policy version it was made for | pre-adoption decisions, stale settings surviving an amendment |
| **Exact one-shot execution**: the payment step remembers what it executed | replay, reuse of an exception for another amount |
| **Closed surface**: anything unrecognised goes to a person | unknown action types clearing by default |

**What this shows.** Inside this class of workflow the authority ledger *is* the disciplined baseline, with its
conventions enforced in code instead of by habit. The two are also the same size: 246 logical lines for the
ledger arm (fault hooks included) and 243 for the baseline with all five conventions. There is no property here that requires a novel kernel, a normative graph, or a precedence engine.

**What it does not show.** I wrote both arms and the probes, so they share my blind spots. That is the same weakness
I charge K1–K6 with, and mutation-testing my own probes reduces it without removing it. The baseline is Python, not
Cedar or Rego. The probes cover what I thought to ask. It says nothing about economics.

**A property of the real cases no kernel can pre-compute.** In Davies the reviewer let a *later* rule change weigh
on an *earlier* claim as a matter of proportionality. In Pound past payments constrained the outcome; in McDonagh
they did not. These are exercises of discretion. A system can route them to the right person and record the answer
with the right scope. It cannot derive them, and K3-style automatic precedence would have got at least one wrong.

## 7. Approaches compared

| Approach | Fails by | Ongoing human work | Must prove |
|---|---|---|---|
| **A. Full Sophon control plane** (report §17: source tree, semantic AST, governance IR, authority graph, binding registry, runtime, gateway) | Reported 71–77% recall when compiling real rulebooks; large surface; K-claims unverified | Highest: ratify a compiled rulebook, then maintain it | That compiling beats hand-writing grants. The report's own evidence says no. |
| **B. Policy-as-code + reviewed repo + gateway** (Cedar/OPA, pull requests, decision logs) | Without the five conventions: 10 of 20 probes. No escalation outcomes beyond allow/deny. | Engineers write rules; the owner approves pull requests | Nothing new. It is the floor. |
| **C. LLM judge over policy + retrieved precedents, with sampled audit** | Precedent spreading (section 5); non-deterministic; cannot say *who authorized* an action | Lowest up front; audit load forever | That its wrong-action rate is acceptable. Plausible for cheap, reversible actions. |
| **D. Limits and after-the-fact audit** (budget, reversible actions only, clawback) | Useless for irreversible or high-severity actions | Audit sampling | Nothing. It is how organizations already delegate to people, and how IPSA actually controls 99.9% of claims. |
| **E. Thin grant ledger + typed settlement loop on top of B** *(recommended if anything is built)* | Same fact-integrity limit as every deterministic option; adoption risk | The owner settles classes of escalation; engineers integrate once | S3 and S4 in a real workflow |

**Why E over B, the strongest alternative.** B plus the five conventions is technically equal to E, and that is the
point. What E adds is not a better engine. It makes the conventions impossible to skip, and it gives the person
resolving an escalation a first-class choice between "this case only" and "propose a rule to whoever may make one",
with a replay of past cases before anything is ratified. B has no place for that choice: a pull request is how an
engineer changes a rule, not how a finance lead answers a question at 4 pm. If that workflow turns out not to
matter, B is the right answer and Sophon is a set of conventions worth publishing, not a product.

**What is already shipped** (sub-agent research; vendor pages unless marked, ✔ where I re-read the source).
Amazon Bedrock AgentCore Policy ✔ converts single plain-English rules to Cedar, checks them with automated reasoning,
and enforces default-deny on every gateway tool call, with session-scoped temporal conditions. Microsoft's Agent
Governance Toolkit does allow / deny / require-approval with Rego or Cedar and hash-chained logs. Auth0 binds
asynchronous human approval to transaction details. Permit.io separates one-time operation approvals from standing
access grants. I found no product with typed, versioned interpretations and exceptions carrying who / when /
what-power, nor the `REQUEST_FACT` and `SEMANTIC_REVIEW` outcomes. A startup, PolicyLayer, is aiming at the same
"system of record for agent authority" position for coding agents; its maturity is unverified. The sub-agent put its
confidence that the niche is unoccupied at about 65%, and I would not go higher.

Prior art the report does not cite: XACML's PEP/PDP/PAP/PIP split and its administrative delegation profile are the
report's §17 runtime; KeyNote and SPKI are K1; macaroons and Biscuit are K6's attenuated one-shot permits; Catala and
the Rules-as-Code work are the closest thing to a working "law to code with exceptions" practice, and they pair a
lawyer with a programmer, clause by clause. (From memory; links not fetched.)

## 8. What is genuinely open, and the smallest things that would close it

1. **Is there a workflow where checking before acting pays?** It needs actions that are costly or irreversible, a
   refusal rate that is not near zero, and facts the system can observe itself. Expenses fail all three. Candidates:
   refunds and credits above a threshold, access grants, payment release, contract concessions, outbound data sharing.
2. **Do policy owners, in that workflow, settle classes of escalation prospectively?** Section 5 says expect this to
   be slower and rarer than hoped, and to run through a different person than the one who handles the case.
3. **Does fact extraction erase the kernel's guarantee?** Needs real case narratives with a human-made fact sheet.

Smallest next steps, in the order I would take them (`docs/OWNER_REQUEST.md`):

- **Run the recurrence study on a real agent workload you already have**: your own Claude Code history. It is a
  live instance of this exact loop, with a real authority holder, complete mediation and real standing grants. The
  script is ready and prints only counts; I ran it on this session alone as a smoke test (92 tool calls, not
  evidence). It needs your permission because it reads other projects' session logs.
- **Do not spend your time on the 48-case lab as designed.** Its outcome metrics cannot separate the architectures
  and its reuse ceiling is 8 cases by construction. If you want to exercise the mechanism end to end once, the six
  decisions in the owner request are enough.
- **Then one design partner**, instrumented for S3–S5 against approach B.

## 9. Limits of this investigation

- It cannot establish economic value. No part of it measures human minutes, willingness to pay, or adoption.
- K1–K6, the semantic-compiler recalls, and the full-file IPSA counts are reported, not reproduced. I did not
  download the 2023–24 claims CSV; `python evidence/sophon_ipsa/replay.py fetch` then `reveal` would check it.
- The corpus is 46 *appeals*: selected, contested, and coded by two instances of one model. It describes how hard
  cases are resolved, not how often hard cases occur. I am not a lawyer and the codings are not legal classifications.
- Both lab arms, the probes and the seeded faults are mine.
- Several 2026 product facts come from one sub-agent's web research and from vendor pages; general-availability
  dates in particular come from secondary sources.
- I read 46 public PDFs from the official IPSA Compliance site through the fetch tool. They are not stored in this
  repository; only paraphrased codings are.
