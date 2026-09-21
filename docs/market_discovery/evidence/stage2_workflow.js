export const meta = {
  name: 'sophon-market-stage2',
  description: 'Deep research stage 2: rank verified domain evidence, deep-dive the top workflows, design wedge, discovery and base-rate study, synthesize the owner report',
  phases: [
    { title: 'Rank', detail: 'shortlist from all verified clusters; hypothesis verdicts' },
    { title: 'Deep-dive', detail: 'operational walkthroughs of the top three, each refuted' },
    { title: 'Design', detail: 'wedge, discovery sprint, base-rate experiment; methodology review' },
    { title: 'Synthesize', detail: 'report A to H, completeness critique, revision' },
  ],
}

const SP = '/tmp/claude-0/-home-user-sophon/03144a04-0e98-54e7-9d2c-78cb7b16e172/scratchpad/market'
const NET = `NETWORK, READ CAREFULLY: this session's WebSearch quota is EXHAUSTED (200 of 200 queries used), so WebSearch will fail. WebFetch is blocked by the egress proxy on nearly every regulator, government, court, academic, industry-association, press and commercial-vendor host; raw.githubusercontent.com, github.com, pypi.org and npmjs.com are reachable. Therefore: rely on the digest and the per-cluster JSON files (which record what each finder and verifier could and could not source), on GitHub-hosted primary artefacts you can fetch (regulator open-source systems, vendor SDKs and API specifications, open datasets and scrapes), and on your own recall ONLY when flagged as [RECALL, unverified]. Never invent a number. Every number carries a URL and a source type, or the label estimate, or the label recall. The final report must state this evidence limitation prominently and must not present recall as measurement.`
const GROUND = `MANDATORY FIRST STEP: Read ${SP}/brief.md (the owner's brief) and ${SP}/prior_evidence.md. Then read ${SP}/digest.md, the condensed, adversarially verified output of fifteen domain sweeps; the full per-cluster JSON files are listed in it and may be read for detail. Rules: evidence over intuition; separate sourced numbers (with URL and source type) from estimates; distinguish total manual review from repeatable ambiguity that can be settled prospectively (category H); do not extrapolate one company's workflow to an industry; vendor claims are weak evidence; absence of data is uncertainty; be willing to conclude the thesis fails. Write tight prose, no filler, no em-dashes. ${NET}`

const RANK_SCHEMA = { type: 'object', properties: {
  executive_call: { type: 'string', enum: ['strong evidence', 'promising but unproven', 'weak evidence', 'evidence against'] },
  rationale: { type: 'string' },
  shortlist: { type: 'array', items: { type: 'object', properties: {
    workflow: { type: 'string' }, domain: { type: 'string' }, geography: { type: 'string' },
    why_humans_review: { type: 'string' },
    repeatable_ambiguity: { type: 'string', description: 'assessment, estimated H share, basis and sources' },
    volume: { type: 'string' }, economic_pain: { type: 'string' }, existing_solution: { type: 'string' },
    evidence_quality: { type: 'string', enum: ['strong', 'moderate', 'weak', 'negative', 'unknown'] },
    dimensions: { type: 'array', items: { type: 'object', properties: { dimension: { type: 'string' }, classification: { type: 'string', enum: ['strong evidence', 'moderate evidence', 'weak evidence', 'negative evidence', 'unknown'] }, basis: { type: 'string' } }, required: ['dimension', 'classification', 'basis'] } },
    settlement_loop_status: { type: 'string', description: 'operational / ceremonial / absent, with the evidence' } },
    required: ['workflow', 'domain', 'geography', 'why_humans_review', 'repeatable_ambiguity', 'volume', 'economic_pain', 'existing_solution', 'evidence_quality', 'dimensions', 'settlement_loop_status'] } },
  top_three: { type: 'array', items: { type: 'string' }, minItems: 3, maxItems: 3 },
  wedge_candidates: { type: 'array', items: { type: 'object', properties: { workflow: { type: 'string' }, why_cheap_to_test: { type: 'string' }, access_to_cases: { type: 'string' }, access_to_owners: { type: 'string' } }, required: ['workflow', 'why_cheap_to_test'] } },
  hypotheses: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, verdict: { type: 'string', enum: ['supported', 'partially supported', 'not supported', 'unknown'] }, evidence_for: { type: 'string' }, evidence_against: { type: 'string' }, varies_by_domain: { type: 'string' } }, required: ['id', 'verdict', 'evidence_for', 'evidence_against'] }, minItems: 8, maxItems: 8 },
  domains_rejected_and_why: { type: 'array', items: { type: 'string' } } },
  required: ['executive_call', 'rationale', 'shortlist', 'top_three', 'wedge_candidates', 'hypotheses', 'domains_rejected_and_why'] }

const DIVE_SCHEMA = { type: 'object', properties: {
  workflow: { type: 'string' }, geography: { type: 'string' },
  triggering_event: { type: 'string' }, available_rules: { type: 'string' }, available_facts: { type: 'string' },
  why_it_escalates: { type: 'string' }, who_resolves: { type: 'string' }, what_gets_settled: { type: 'string' },
  prospective: { type: 'string', description: 'does the settlement apply to later cases; evidence' },
  recurrence: { type: 'string', description: 'how often the same class recurs; evidence' },
  current_systems: { type: 'string' }, minimal_product: { type: 'string', description: 'what a minimal Sophon would actually do, and what it would NOT do' },
  buyer: { type: 'string' }, roi_logic: { type: 'string', description: 'with the arithmetic and its sources or estimates labelled' },
  review_split_A_to_H: { type: 'string' },
  key_numbers: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, url: { type: 'string' }, source_type: { type: 'string' }, sourced_or_estimate: { type: 'string' } }, required: ['claim', 'url', 'source_type', 'sourced_or_estimate'] } },
  penalties_triggered: { type: 'array', items: { type: 'string' }, description: 'which of the brief section 2 penalties apply and how badly' },
  regulatory_constraints_US_EU_FR: { type: 'string' },
  verdict: { type: 'string' } },
  required: ['workflow', 'geography', 'triggering_event', 'available_rules', 'available_facts', 'why_it_escalates', 'who_resolves', 'what_gets_settled', 'prospective', 'recurrence', 'current_systems', 'minimal_product', 'buyer', 'roi_logic', 'review_split_A_to_H', 'key_numbers', 'penalties_triggered', 'regulatory_constraints_US_EU_FR', 'verdict'] }

const VERIFY_SCHEMA = { type: 'object', properties: {
  target: { type: 'string' },
  refuted: { type: 'array', items: { type: 'object', properties: { point: { type: 'string' }, why: { type: 'string' } }, required: ['point', 'why'] } },
  weakened: { type: 'array', items: { type: 'object', properties: { point: { type: 'string' }, why: { type: 'string' } }, required: ['point', 'why'] } },
  strengthened: { type: 'array', items: { type: 'object', properties: { point: { type: 'string' }, why: { type: 'string' } }, required: ['point', 'why'] } },
  missing: { type: 'array', items: { type: 'string' } },
  corrected_verdict: { type: 'string' },
  overall: { type: 'string' } },
  required: ['target', 'refuted', 'weakened', 'strengthened', 'missing', 'corrected_verdict', 'overall'] }

const DESIGN_SCHEMA = { type: 'object', properties: {
  best_wedge: { type: 'object', properties: { workflow: { type: 'string' }, why: { type: 'string' }, access_to_historical_cases: { type: 'string' }, access_to_decision_owners: { type: 'string' }, why_not_the_larger_markets: { type: 'string' } }, required: ['workflow', 'why', 'access_to_historical_cases', 'access_to_decision_owners', 'why_not_the_larger_markets'] },
  competitive_threat: { type: 'object', properties: { shape: { type: 'string', enum: ['standalone software company', 'feature inside an existing workflow product', 'internal capability enterprises build themselves', 'consulting or service layer', 'not built at all'] }, reasoning: { type: 'string' }, who_would_absorb_it: { type: 'string' } }, required: ['shape', 'reasoning', 'who_would_absorb_it'] },
  research_gaps: { type: 'array', items: { type: 'string' } },
  discovery_sprint: { type: 'object', properties: { target_job_titles: { type: 'array', items: { type: 'string' } }, organisations: { type: 'array', items: { type: 'string' } }, questions: { type: 'array', items: { type: 'string' } }, evidence_to_request: { type: 'array', items: { type: 'string' } }, supporting_answers: { type: 'array', items: { type: 'string' } }, killing_answers: { type: 'array', items: { type: 'string' } }, sequencing_and_recruiting: { type: 'string' } }, required: ['target_job_titles', 'organisations', 'questions', 'evidence_to_request', 'supporting_answers', 'killing_answers', 'sequencing_and_recruiting'] },
  base_rate_experiment: { type: 'object', properties: { sample: { type: 'string' }, source_of_cases: { type: 'string' }, coding_protocol: { type: 'string' }, category_definitions: { type: 'string' }, coders_and_agreement: { type: 'string' }, thresholds: { type: 'string', description: 'minimum frequency of categories 7 and 8, minimum recurrence, and the customer-economics basis for each number' }, decision_rule: { type: 'string' }, what_it_cannot_decide: { type: 'string' } }, required: ['sample', 'source_of_cases', 'coding_protocol', 'category_definitions', 'coders_and_agreement', 'thresholds', 'decision_rule', 'what_it_cannot_decide'] } },
  required: ['best_wedge', 'competitive_threat', 'research_gaps', 'discovery_sprint', 'base_rate_experiment'] }

const CRITIC_SCHEMA = { type: 'object', properties: {
  missing_required_content: { type: 'array', items: { type: 'string' } },
  violated_research_discipline: { type: 'array', items: { type: 'string' } },
  factual_errors_vs_evidence: { type: 'array', items: { type: 'string' } },
  manual_review_conflated_with_H: { type: 'array', items: { type: 'string' } },
  hedging_or_optimism: { type: 'array', items: { type: 'string' } },
  concrete_fixes: { type: 'array', items: { type: 'string' } },
  verdict: { type: 'string' } },
  required: ['missing_required_content', 'violated_research_discipline', 'factual_errors_vs_evidence', 'manual_review_conflated_with_H', 'hedging_or_optimism', 'concrete_fixes', 'verdict'] }

phase('Rank')
const rank = await agent(`${GROUND}
ROLE: RANKER. Using the verified evidence from all fifteen clusters, produce: the executive call (strong evidence / promising but unproven / weak evidence / evidence against) with its rationale; a shortlist of 5 to 10 workflows, each with the brief's section 8 dimensions classified as strong / moderate / weak / negative / unknown evidence with the basis, the estimated share of repeatable ambiguity (category H) and how it was estimated, and the settlement-loop status (operational, ceremonial, absent); the top three; wedge candidates chosen for cheap access to real historical cases and decision owners, not market size; verdicts on hypotheses H1 to H8 with the best evidence for and against each, noting where the verdict varies by domain; and the domains rejected with reasons. Penalise heavily per section 2 of the brief. Where verifiers corrected a finder, use the corrected verdict.`, { label: 'rank:shortlist', phase: 'Rank', schema: RANK_SCHEMA, effort: 'high' })

phase('Deep-dive')
const items = rank.top_three.map((w, i) => ({ workflow: w, i }))
const [dives, designPair] = await parallel([
  () => pipeline(
    items,
    it => agent(`${GROUND}
ROLE: DEEP-DIVE ANALYST for the workflow "${it.workflow}". Attempt targeted additional research only through fetchable GitHub-hosted primary artefacts (WebSearch is exhausted; say so if a fetch fails), then write the operational walkthrough the brief requires in section 10.C: triggering event; available rules; available facts; why the decision escalates; who resolves it; what exactly gets settled; whether that settlement applies prospectively; how often the same class recurs; current systems involved; what a minimal Sophon product would actually do and would not do; buyer; ROI logic with arithmetic. Give the A to H review split with basis. List every key number with URL, source type and sourced-or-estimate. State which section 2 penalties the workflow triggers. Cover US, EU and France where regulation differs. End with a verdict.

RANKER CONTEXT FOR THIS WORKFLOW:
${JSON.stringify(rank.shortlist.find(s => s.workflow === it.workflow) || {}, null, 1)}`, { label: `dive:${it.i + 1}`, phase: 'Deep-dive', schema: DIVE_SCHEMA, effort: 'high' }),
    (d, it) => d ? agent(`${GROUND}
ROLE: ADVERSARIAL REFUTER of the deep dive on "${it.workflow}". Try to show this workflow FAILS the brief: the bottleneck is missing data not interpretation; decisions are discretionary or negotiated; ambiguity rarely repeats; incumbents already capture settlements; law or regulation keeps a human in the loop after precedent; volume or value per decision is too small; the buyer is unclear; the ROI arithmetic is wrong or unsourced; the settlement loop is ceremonial. Check the key numbers against their sources. Give refuted, weakened, strengthened, missing, and a corrected verdict.

DEEP DIVE:
${JSON.stringify(d, null, 1)}`, { label: `refute:${it.i + 1}`, phase: 'Deep-dive', schema: VERIFY_SCHEMA, effort: 'high' }).then(r => ({ workflow: it.workflow, dive: d, refutation: r })) : null
  ),
  () => agent(`${GROUND}
ROLE: DESIGNER of sections D, E, F, G and H of the brief. Using the ranker's shortlist, wedge candidates and hypothesis verdicts below, choose the single best initial wedge (cheap access to real historical cases and to decision owners; NOT market size), decide the competitive-threat shape (standalone company / feature of an existing product / internal capability / consulting layer / not built), list the research gaps only interviews or proprietary data can close, design a 10-interview discovery sprint (exact job titles, organisations, questions, evidence to request, answers that support, answers that kill, recruiting and sequencing), and design the base-rate experiment on 100 to 500 historical decisions with the eight categories defined operationally, two coders and an agreement gate, and thresholds for categories 7 and 8 derived from plausible customer economics (cost per escalation, escalations per year, a price the buyer would plausibly pay, and the share that must be H for the product to pay back), not set to preserve the project. State what the experiment cannot decide.

RANKER OUTPUT:
${JSON.stringify({ executive_call: rank.executive_call, rationale: rank.rationale, shortlist: rank.shortlist, wedge_candidates: rank.wedge_candidates, hypotheses: rank.hypotheses }, null, 1)}`, { label: 'design:D-E-F-G-H', phase: 'Design', schema: DESIGN_SCHEMA, effort: 'high' })
    .then(d => d ? agent(`${GROUND}
ROLE: METHODOLOGY REVIEWER of a discovery sprint and base-rate experiment design. Attack it: are the eight categories operationally separable by two coders; is the sample obtainable and from whom; are the thresholds derived from real economics or chosen to preserve the project; does the coding protocol let 'manual review' be counted as category H; are the interview questions leading; would the killing answers actually kill; is the wedge chosen for access rather than size; is the competitive-threat call consistent with the incumbent evidence in the digest. Give refuted, weakened, strengthened, missing, and a corrected verdict.

DESIGN:
${JSON.stringify(d, null, 1)}`, { label: 'review:design', phase: 'Design', schema: VERIFY_SCHEMA, effort: 'high' }).then(r => ({ design: d, review: r })) : null),
])

phase('Synthesize')
const bundle = { rank, dives: (dives || []).filter(Boolean), design: designPair }
log(`rank ok; dives ${bundle.dives.length}/3; design ${designPair ? 'ok' : 'missing'}`)
const draft = await agent(`${GROUND}
ROLE: REPORT WRITER. Using ONLY the material below, write the owner's report in EXACTLY the structure of brief section 10: A executive answer (one of the four choices, with why); B candidate workflow table with the exact columns | Workflow | Why humans review | Repeatable ambiguity? | Volume | Economic pain | Existing solution | Evidence quality |; C top three workflows with every listed field; D best initial wedge; E competitive threat; F research gaps; G customer discovery design; H base-rate experiment with the eight categories and thresholds. Then the hypotheses H1 to H8 verdicts in a short table. Where a refuter or reviewer refuted a point, do not carry it; where weakened, qualify it. Every number carries its source URL or is labelled estimate. Distinguish US, EU and France where it matters. No em-dashes. Short sentences. At most 7,000 words. End with exactly one of the two closing sentences the brief specifies.

MATERIAL:
${JSON.stringify(bundle, null, 1)}`, { label: 'write:draft', phase: 'Synthesize', effort: 'high' })

const critique = await agent(`${GROUND}
ROLE: COMPLETENESS CRITIC. Check the draft against brief section 10 item by item (A through H, every sub-field of C, the eight categories of H and their thresholds, the closing sentence), against section 11's research discipline, and against the digest and cluster files for factual accuracy. Flag every place 'manual review' is counted as repeatable ambiguity, every unsourced number, every vendor claim treated as independent, every extrapolation from one company to an industry, and every hedge that the evidence does not require. Give concrete fixes.

DRAFT:
${draft}`, { label: 'critique:draft', phase: 'Synthesize', schema: CRITIC_SCHEMA, effort: 'high' })

const finalReport = await agent(`${GROUND}
ROLE: REVISER. Apply the critic's fixes. Keep the exact structure and the closing sentence form. At most 7,500 words. Return the full revised report in markdown only.

CRITIQUE:
${JSON.stringify(critique, null, 1)}

DRAFT:
${draft}`, { label: 'write:final', phase: 'Synthesize', effort: 'high' })

return { report: finalReport, critique, bundle }
