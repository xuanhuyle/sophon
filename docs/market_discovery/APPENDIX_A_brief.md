# Market discovery brief (verbatim from the owner, 21 September 2026)

I want you to identify the most promising real-world use cases for a product with the following capability:

A system captures how an organisation resolves ambiguous or under-specified operational decisions, records the authoritative interpretation with provenance and versioning, and turns repeated future cases into deterministic decisions when the relevant facts are available.

Do not assume that such a product is valuable. Your task is to determine whether there are workflows where this mechanism solves a sufficiently large and recurring economic problem to justify an independent software product.

This is an adversarial market discovery exercise, not a brainstorming exercise.

## 1. The mechanism being tested

The candidate product does NOT primarily: generate policy text; answer questions conversationally; classify documents; replace a rules engine; make discretionary decisions autonomously; infer authoritative meaning from policy documents without human ratification.

Instead, it addresses this pattern:
1. An operational decision must be made.
2. Existing rules, contracts, policies, regulations, precedents, or procedures do not fully determine the answer.
3. A qualified person settles the ambiguity.
4. That settlement is authoritative for at least some future cases.
5. The same or materially similar ambiguity recurs.
6. Future cases can then be resolved faster because the prior settlement has been captured, versioned, and made executable.

The core economic hypothesis is: Organisations repeatedly pay humans to settle the same classes of ambiguity because institutional interpretations are not captured in a sufficiently structured, governed, reusable form. Your job is to test whether this hypothesis is true in any meaningful market.

## 2. What constitutes a good use case

Search for workflows where most of the following are true: high decision volume; meaningful cost per decision; rules or policies constrain decisions but do not fully determine them; human interpretation is routinely required; interpretations recur across similar cases; decisions can later become rules once an authorised settlement exists; the cost of a wrong decision is significant; auditability matters; decision provenance matters; multiple documents or authorities may apply; rules change over time; there is a clear institutional owner who can approve interpretations; outcomes can be represented in structured form; relevant factual evidence can usually be obtained; automation would save real labour or reduce operational risk; customers have budget and a clear software buyer.

Penalise heavily use cases where: decisions are mostly one-off judgment calls; ambiguity rarely repeats; decisions are fundamentally discretionary; existing BPM/rules engines already solve the problem adequately; the main bottleneck is missing data rather than interpretation; humans must remain involved for legal or commercial reasons even after precedent exists; the value per decision is too small; decision volume is too low; regulations prohibit or severely constrain automation; the buyer is unclear; implementation requires replacing a core system of record.

## 3. Search domains broadly

Do not anchor prematurely on compliance or legal workflows. Investigate at least: insurance claims; insurance underwriting; banking operations; lending and credit exceptions; payments and fraud operations; KYC / AML; tax operations; procurement; employee expenses; HR policy administration; payroll; benefits administration; healthcare administration; prior authorisation; government benefits; public-sector casework; customs and trade compliance; export controls; logistics; aviation operations; telecom operations; utility operations; construction; property management; warranty claims; returns and refunds; marketplace trust and safety; content moderation; cybersecurity operations; enterprise access control; contract operations; legal operations; regulated professional services. Add others if evidence points elsewhere. Do not limit the search geographically unless regulation materially affects the use case. Where relevant, distinguish US, EU and French market conditions.

## 4. Look for empirical evidence

Do not rely primarily on hypothetical reasoning. Search for evidence of: manual review rates; exception rates; escalation rates; appeal rates; override rates; rework; policy interpretation disputes; claims leakage; compliance operating cost; headcount involved in decision review; SLA delays caused by review; repeated support tickets involving policy interpretation; internal policy exception committees; case management systems; "tribal knowledge" or undocumented precedent; spreadsheet/email/manual workflow dependence; audit findings caused by inconsistent interpretation; existing software categories attempting to solve similar problems.

Whenever possible quantify: annual decision volume; percentage requiring human review; percentage involving rule ambiguity versus missing facts; labour cost; downstream loss/error cost; recurrence of similar cases; addressable user count; software spend; likely ROI from automation. Clearly separate sourced data from estimates.

## 5. Distinguish the types of human review (critical)

For each use case, estimate how much human intervention belongs to:
A. missing evidence; B. factual classification; C. interpretation of an existing rule; D. conflict between authorities/rules; E. true discretion; F. commercial negotiation; G. one-off exceptional circumstances; H. repeatable ambiguity that can be settled prospectively.
Only category H strongly supports the product hypothesis. Do not treat all "manual review" as addressable.

## 6. Study existing alternatives

For each promising use case, identify how organisations solve the problem today: rules engines; BPM/workflow tools; case management systems; policy management tools; GRC software; knowledge bases; expert systems; decision management systems; low-code platforms; LLM/agent products; vertical SaaS; in-house tooling. Vendors may include Pega, Appian, ServiceNow, Camunda, Drools, OPA, Cedar, FICO, Guidewire, Duck Creek, Workday, SAP, Salesforce, Palantir, GRC platforms, emerging AI decision/agent products. Do not assume Sophon has a moat where incumbent functionality is already adequate.

## 7. Search specifically for the "settlement loop" (most important)

Find evidence that organisations already perform: ambiguous case → escalation → expert or policy owner decision → precedent/convention created → later similar cases resolved consistently. Examples: coverage interpretations; underwriting exceptions; compliance interpretations; policy exceptions; accounting interpretations; tax rulings; HR precedents; entitlement decisions; access-policy exceptions; procurement exceptions; operational waivers. For each candidate, determine whether the settlement is actually reusable and prospective, rather than merely case-specific.

## 8. Rank candidates using evidence, not intuition

Shortlist 5 to 10 workflows. For each assess: annual decision volume; current human review rate; estimated share of repeatable ambiguity; cost per review; cost/risk of wrong decision; recurrence of settlements; ability to codify settlements; existence of an authoritative decision owner; availability of structured evidence; integration complexity; regulatory constraints; incumbent software strength; buyer; willingness to pay; sales cycle; potential initial ACV; expansion potential. Classify each dimension as strong evidence / moderate evidence / weak evidence / negative evidence / unknown. No pseudo-precise scores.

## 9. Falsification criteria

Actively test: H1 Most manual reviews are caused by missing facts, not recurring interpretive ambiguity. H2 Interpretive ambiguity exists but repeats too rarely to compound. H3 Once ambiguity is settled, organisations already encode it adequately in existing systems. H4 Interpretation remains legally or organisationally discretionary even after precedent exists. H5 The relevant institutional knowledge is too local or contextual to generalise. H6 The product becomes merely a feature of BPM, GRC, vertical SaaS, or agent platforms. H7 The settlement corpus does not create meaningful switching costs or defensibility. H8 The economics cannot support standalone software because the addressable labour pool is too small. If the evidence supports these hypotheses, say so clearly.

## 10. Required output

A. Executive answer: strong evidence / promising but unproven / weak evidence / evidence against, with why.
B. Candidate workflow table: | Workflow | Why humans review | Repeatable ambiguity? | Volume | Economic pain | Existing solution | Evidence quality |
C. Top three workflows, operational walkthrough each: triggering event; available rules; available facts; why the decision escalates; who resolves it; what exactly gets settled; whether that settlement applies prospectively; how often the same class recurs; current systems involved; what a minimal Sophon product would actually do; buyer; ROI logic.
D. Best initial wedge: the single workflow to test empirically; prefer cheap access to real historical cases and actual decision owners, not market size.
E. Competitive threat: standalone software company / feature inside an existing workflow product / internal capability / consulting-service layer / not built at all.
F. Research gaps: facts public research cannot establish.
G. Customer discovery design for the best workflow: 10-interview sprint; exact target job titles; organisations; questions; evidence to request; answers that support; answers that kill.
H. Base-rate experiment: ~100 to 500 historical decisions classified as (1) fully deterministic from existing rules and facts; (2) missing evidence; (3) factual classification; (4) one-off discretion; (5) ambiguity of rule meaning; (6) conflict between rules/authorities; (7) recurring previously-settled ambiguity; (8) new ambiguity that could be settled prospectively. Define the minimum frequency and recurrence of 7 and 8 that would justify continuing, set by plausible customer economics, not to preserve the project.

## 11. Research discipline

Cite primary sources wherever possible. Prefer operational evidence over marketing. Distinguish vendor claims from independent evidence. Distinguish total manual review from addressable repeatable ambiguity. Do not extrapolate one company's workflow to an industry without evidence. Do not recommend a use case because AI adoption is high there. Do not assume a large regulated industry is attractive. Treat absence of data as uncertainty, not positive evidence. Be willing to conclude that no attractive standalone use case exists.

The key question is not "Where could Sophon be used?" It is: "Where are organisations repeatedly paying humans to resolve ambiguities that become reusable institutional decisions, at enough volume and cost that capturing those settlements creates compounding economic value?"

End with: "The strongest evidence for a Sophon-shaped market is ________, because ________." or, if negative, "I would stop searching for a standalone Sophon product because ________."
