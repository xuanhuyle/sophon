export const meta = {
  name: 'sophon-market-stage1',
  description: 'Deep research stage 1: domain sweeps for Sophon-shaped workflows, each adversarially verified',
  phases: [
    { title: 'Find', detail: 'one finder per domain cluster' },
    { title: 'Verify', detail: 'adversarial verification of each domain result' },
  ],
}

const SP = '/tmp/claude-0/-home-user-sophon/03144a04-0e98-54e7-9d2c-78cb7b16e172/scratchpad/market'
const NET = `NETWORK: WebSearch works and its result snippets are usable evidence (cite the URL). WebFetch is blocked on many domains by an egress proxy (known blocked: typesafe.ai, theregister.com, langchain.com, tomshardware.com, datacamp.com, dev.to, substack.com, news.ycombinator.com, x.com, reddit.com, medium.com, openrouter.ai, developers.cloudflare.com, pydantic.dev, arxiv.org may be blocked). Government, regulator, court, standards-body, industry-association and vendor documentation sites often work; GitHub works. Try a fetch once; if blocked, record the URL under blocked_urls and rely on search snippets or an alternative source. Never invent a number. Every number carries a URL and a type.`
const GROUND = `MANDATORY FIRST STEP: Read ${SP}/brief.md (the owner's brief; sections 1, 2, 5, 7 and 11 define what counts) and ${SP}/prior_evidence.md (prior findings to test, not anchors). You are one finder in a multi-domain adversarial market discovery. Your job is EVIDENCE, not opinion: for every workflow you examine, find operational numbers (decision volumes, review/exception/escalation/appeal/override rates, headcount, cost per review, error or leakage cost), find how organisations resolve ambiguity today (systems, committees, precedent databases, guidance updates), and hunt specifically for the SETTLEMENT LOOP: an ambiguous case escalated to an owner whose decision is then recorded and applied prospectively to later similar cases. Classify why humans review using the brief's A to H categories with rough shares and the basis for them. Distinguish sourced data (with URL and source type: regulator / government statistics / court or tribunal / academic / audit or inspector-general / industry association / vendor / press) from your own estimates. Prefer primary sources. Vendor marketing is weak evidence. Absence of data is uncertainty, not support. Be willing to say a domain is negative. Use at least 10 distinct WebSearch queries and fetch at least 5 sources. ${NET}`

const FIND_SCHEMA = { type: 'object', properties: {
  domain: { type: 'string' },
  workflows: { type: 'array', items: { type: 'object', properties: {
    name: { type: 'string' },
    geography: { type: 'string' },
    decision_volume: { type: 'string', description: 'number, unit, geography, URL, sourced-or-estimate' },
    human_review_rate: { type: 'string', description: 'share and basis, URL' },
    why_humans_review: { type: 'string', description: 'rough shares across A missing evidence, B factual classification, C rule interpretation, D conflict of authorities, E true discretion, F commercial negotiation, G one-off circumstances, H repeatable ambiguity settled prospectively, with the basis' },
    settlement_loop_evidence: { type: 'array', items: { type: 'object', properties: { description: { type: 'string' }, source_url: { type: 'string' }, source_type: { type: 'string' }, prospective: { type: 'string', enum: ['yes', 'no', 'unclear'] }, reusable_how: { type: 'string' } }, required: ['description', 'source_url', 'source_type', 'prospective'] } },
    economic_pain: { type: 'string', description: 'cost per review, error cost, headcount, delays, with URLs' },
    existing_solutions: { type: 'string', description: 'systems and vendors used today and whether they capture settlements as versioned executable precedents' },
    buyer_and_budget: { type: 'string' },
    regulatory_constraints: { type: 'string' },
    evidence_quality: { type: 'string', enum: ['strong', 'moderate', 'weak', 'negative', 'unknown'] },
    verdict: { type: 'string', enum: ['promising', 'uncertain', 'weak', 'negative'] },
    notes: { type: 'string' } },
    required: ['name', 'geography', 'decision_volume', 'human_review_rate', 'why_humans_review', 'settlement_loop_evidence', 'economic_pain', 'existing_solutions', 'buyer_and_budget', 'regulatory_constraints', 'evidence_quality', 'verdict'] } },
  evidence_against_thesis: { type: 'array', items: { type: 'string' } },
  not_found: { type: 'array', items: { type: 'string' } },
  blocked_urls: { type: 'array', items: { type: 'string' } },
  sources: { type: 'array', items: { type: 'object', properties: { url: { type: 'string' }, type: { type: 'string' }, used_for: { type: 'string' } }, required: ['url', 'type', 'used_for'] } },
  domain_assessment: { type: 'string' } },
  required: ['domain', 'workflows', 'evidence_against_thesis', 'not_found', 'sources', 'domain_assessment'] }

const VERIFY_SCHEMA = { type: 'object', properties: {
  domain: { type: 'string' },
  refuted: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, why: { type: 'string' } }, required: ['claim', 'why'] } },
  weakened: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, why: { type: 'string' } }, required: ['claim', 'why'] } },
  confirmed: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, evidence: { type: 'string' } }, required: ['claim', 'evidence'] } },
  manual_review_conflated_with_repeatable_ambiguity: { type: 'array', items: { type: 'string' } },
  corrected_workflow_verdicts: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, evidence_quality: { type: 'string', enum: ['strong', 'moderate', 'weak', 'negative', 'unknown'] }, verdict: { type: 'string', enum: ['promising', 'uncertain', 'weak', 'negative'] }, why: { type: 'string' } }, required: ['name', 'evidence_quality', 'verdict', 'why'] } },
  missing: { type: 'array', items: { type: 'string' } },
  overall: { type: 'string' } },
  required: ['domain', 'refuted', 'weakened', 'confirmed', 'manual_review_conflated_with_repeatable_ambiguity', 'corrected_workflow_verdicts', 'missing', 'overall'] }

const domains = args.domains
if (!Array.isArray(domains) || domains.length === 0) throw new Error('args.domains required')

phase('Find')
const results = await pipeline(
  domains,
  d => agent(`${GROUND}\n\nDOMAIN CLUSTER: ${d.key}\n${d.prompt}`, { label: `find:${d.key}`, phase: 'Find', schema: FIND_SCHEMA, effort: 'high' }),
  (found, d) => found ? agent(`${GROUND}\n\nYou are an ADVERSARIAL VERIFIER for the domain cluster "${d.key}". Below is a finder's result. Your job: (1) re-check the load-bearing numbers against their cited sources (fetch if possible, search snippets otherwise) and refute or downgrade anything misquoted, vendor-sourced but presented as independent, or unsupported; (2) find where the finder conflated "manual review" with "repeatable ambiguity that can be settled prospectively" (category H) and re-estimate the H share honestly; (3) check every settlement-loop item: is the settlement really prospective and reusable, or case-specific, or merely a published ruling that does not feed an operational system; (4) look for evidence the finder missed that cuts AGAINST the workflow (existing systems that already capture settlements, regulation that keeps humans in the loop, low volumes, missing-facts dominance); (5) issue corrected verdicts per workflow. Be specific, cite URLs.\n\nFINDER RESULT:\n${JSON.stringify(found, null, 1)}`, { label: `verify:${d.key}`, phase: 'Verify', schema: VERIFY_SCHEMA, effort: 'high' }).then(v => ({ key: d.key, found, verification: v })) : null
)

const done = results.filter(Boolean)
log(`${done.length}/${domains.length} domain clusters complete`)
return { clusters: done }
