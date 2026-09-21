# Prompt for Claude Code: independent Sophon architecture investigation

Act as an independent product and systems architect. Your goal is to decide what architectural approach, if any, would make **Sophon** viable, and establish the foundations needed to test that decision. You have discretion over the problem framing, architecture, tools, technology, prototype, evaluation method, and order of work. Challenge the materials in this packet, including the Sophon thesis itself. Do not treat earlier proposed implementations or experiments as requirements.

## The problem to investigate

Organizations want AI agents to take useful actions under changing written policies, delegated permissions, ambiguous language, exceptions, and case-specific decisions. A mistaken action can have real consequences; repeatedly sending every decision to a human defeats the point of autonomy. Can a system expand justified autonomy as people resolve uncertainty, while preserving enough control and evidence to know what was authorized, when, by whom, and for which action? Is this a valuable, tractable product problem, and what is the simplest credible way to address it?

You may conclude that Sophon's current framing is wrong, that an existing approach suffices, that a narrower problem should come first, or that a different architecture is warranted. Find the strongest alternative explanations and competing solutions yourself. Do not favor a novel control plane simply because prior reports propose one.

## Materials available

Read the packet as fallible research input, not as a specification:

- `evidence/Sophon_Technical_Viability_Report_2026-09-21.md` gives the current thesis, claimed K1–K6 results, and known failure history. The underlying code for all those reported results is not supplied here; distinguish reported results from independently reproduced ones.
- `evidence/Sophon_IPSA_Shadow_Replay_2026-09-21.md` and `evidence/sophon_ipsa/` document a frozen 1,000-claim public-data exercise. Its policy-version correction matters: a 15th Scheme rule set was applied across a period in which a revised 16th edition became applicable. It is an observability exercise, not a historically valid full-year policy accuracy benchmark. Audit or reject its implications as you see fit.
- `evidence/Sophon_IPSA_Authority_Case_Study_2026-09-21.md` and `evidence/sophon_cases/` contain five manually examined public review cases, a 46-PDF index, and a hand-built authority probe. The original reports are linked in the data. In particular, one review expressly says its partial remedy is not precedent. The probe's classifications are proposals for scrutiny, not ground truth for a general engine.
- `evidence/sophon_solo/` contains an optional fictional policy, protocol, adoption form, and 48 synthetic cases intended to permit a solo experiment. The policy is **unadopted**; nobody has supplied an owner decision or settlement. You are free to use, revise, replace, or discard this lab design. Its repeated case mix is synthetic and cannot establish real-world frequency or economics.

Check source claims and provenance where useful. If something is absent or access is unavailable, proceed with the work that can be done, label the limitation, and identify the smallest way to resolve it. Do not invent policy authority, owner ratification, historical applicability, or facts available only after a decision. Do not convert a case-specific remedy into a general permission without evidence of that effect. Any executable experiment must remain isolated from real claims, payments, and people.

## Your assignment

1. Form your own precise problem statement and success criteria. Identify which assumptions are load-bearing, which evidence in the packet actually bears on them, and which claimed successes are weak, confounded, or unverified.
2. Explore the most credible approaches *you* find, including the option of a simpler existing system or a change in product scope. Compare their failure modes, ongoing maintenance, human work, and what each would have to prove. Choose an architecture only if the evidence supports choosing one now; otherwise articulate the decision that is genuinely open.
3. Design a discriminating validation exercise that could change your conclusion. Decide whether to use the supplied IPSA material, the fictional lab, another local corpus, a new counterexample, a prototype, or some combination. Establish a fair comparison with the best practical alternative, and say what can be established without involving an outside person. Choose the implementation language and amount of code, if any, based on the question being tested.
4. Carry the investigation as far as you can independently. Inspect the supplied artifacts, reproduce or audit claims when valuable, and build or run focused experiments if that is the fastest way to reduce uncertainty. Record actual results separately from forecasts. If a decision genuinely requires the user's adoption of a fictional policy or another human act, prepare a concrete, reviewable request only after completing independent work. Do not simulate their approval.
5. Leave a clear, usable foundation for the next stage: your recommended architecture or decision framework, its trust and failure boundaries, the minimal evidence or implementation supporting it, what would falsify it, and the next action. You choose the form of the artifacts. Explain why your solution is preferable to the strongest alternative and what would cause you to change your mind.

Make your reasoning and any runnable work reproducible. Report genuine limitations, including if this solo exercise cannot establish the product's economic value. Do not force a favorable conclusion or build a system merely to match the prior reports.
