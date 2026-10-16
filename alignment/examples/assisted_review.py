"""Serialize the first interactive assistant review, NOT a model accuracy benchmark.

Judgments below were authored after reading the real repository documents in the
conversation. This script just adds exact quotes and the snapshot ID. Running it
does not call a model or re-review changed text; frozen hashes enforce that limit.
"""
from pathlib import Path
from alignment.agent import read, write

HERE = Path(__file__).parent


def main():
    packet = read(HERE / 'packet.json')
    expected = {
        'policy': 'ebee78addf435659fb7e36afc1e9ea0a6a72d4b747dee599b142ddf10fd0a04b',
        'reading': 'dee53beee0bf891be9bd2e249f43e00868110f4ed403799cfd413b4f9dfe4900',
    }
    assert {d['id']: d['sha256'] for d in packet['documents']} == expected, 'Recorded judgments do not apply to changed documents'
    segments = {s['id']: s for s in packet['segments']}

    def cite(segment_id):
        return {'segment_id': segment_id, 'quote': segments[segment_id]['text']}

    cases = [
        ('F1', 'UNSUPPORTED_ASSUMPTION', 'Supporting evidence is narrowed to a receipt',
         'The policy requires supporting evidence; R2 selects receipt_present == yes as its operational proxy. The draft does not state that a receipt is the sole acceptable evidence. The table openly labels its readings as proposed choices, so this is a ratification question, not an adopted-policy breach.',
         'An expense supported by another acceptable document could be routed as missing evidence.',
         'Confirm the accepted evidence types and document the receipt-only choice or map the broader evidence predicate.',
         ['policy:L5'], ['reading:L11', 'reading:L4']),
        ('F2', 'MISSING_REQUIREMENT', 'Necessary business travel has no explicit disposition',
         'The hotel clause refers to necessary business travel. R1 tests whether purpose is non-empty; R4 checks manager approval; R8 preserves reasonable price. This supplied table does not explicitly evaluate necessity or establish that manager approval attests it. This is a gap in this table only; other operational evidence was not supplied.',
         'The listed checks may permit the necessity condition to disappear during implementation.',
         'Add a necessity disposition or reference the approved rule establishing how necessity is attested.',
         ['policy:L6'], ['reading:L10', 'reading:L13', 'reading:L18']),
        ('F3', 'UNSUPPORTED_ASSUMPTION', 'The alternative-supplier rule is partitioned by catalogue availability',
         'The source states documented unavailability or business necessity. R10 requires documented unavailability when an item is absent and considers business necessity when it is available. That partition is an additional interpretation of the source OR. The table acknowledges it is unadopted, but this branching choice still needs explicit disposition.',
         'The implementation may not consider business necessity as an alternative when an item is unavailable and documentary proof of unavailability is missing.',
         'Review whether either source alternative applies independently of catalogue availability; preserve the unresolved branch until settled.',
         ['policy:L8'], ['reading:L20', 'reading:L4']),
        ('F4', 'UNSUPPORTED_ASSUMPTION', 'Non-empty purpose does not establish company purpose',
         'R1 treats a non-empty purpose as the documented-purpose check. That can establish presence but does not itself establish a company purpose. The policy and the supplied table contain no approved equivalence between these predicates.',
         'A personal-purpose description could pass the documented-purpose check unless another assessment supplies the missing classification.',
         'Separate evidence presence from company-purpose classification and identify who or what attests the latter.',
         ['policy:L5'], ['reading:L10']),
    ]
    findings = []
    for ident, kind, title, explanation, consequence, action, gov, op in cases:
        findings.append({'id': ident, 'kind': kind, 'severity': 'medium', 'title': title,
                         'explanation': explanation, 'consequence': consequence, 'suggested_action': action,
                         'governing_evidence': [cite(x) for x in gov],
                         'operational_evidence': [cite(x) for x in op]})
    rationale = {
        'policy:L1': 'Draft label, not an operative rule.',
        'policy:L3': 'Authority boundary preserved by the target introduction; no adopted status inferred.',
        'policy:L5': 'Self-approval prohibition represented; evidence and purpose proxies require review (F1/F4).',
        'policy:L6': 'Manager approval and reasonable cost represented; necessity disposition not explicit (F2).',
        'policy:L7': 'Modesty, alcohol/tip exclusions and celebration approval represented; fact classification remains assumed.',
        'policy:L8': 'Source alternatives are narrowed into availability branches (F3); impracticability remains an open issue.',
        'policy:L9': 'Strict >1000 and >5000 thresholds preserved in R5; amount validity is an additional implementation constraint.',
        'policy:L10': 'R7/R11 reference matching case exceptions. Full exception payload validation lies outside this descriptive table; do not infer absence from this file.',
        'policy:L11': 'R5/R10 distinguish relaxation from interpretation; issuer-power validation is not demonstrated by this table.',
        'policy:L12': 'R13 exposes timing ambiguity; table alone does not verify amendment suspension or runtime implementation.',
        'policy:L14': 'Open-issue heading.',
        'policy:L16': 'R8 preserves the open hotel-price standard rather than inventing a threshold.',
        'policy:L17': 'R9 preserves modesty; restaurant eligibility remains a semantic issue.',
        'policy:L18': 'R10 does not settle catalogue impracticability; F3 addresses an extra branch interpretation.',
        'policy:L19': 'Delegation remains unsettled; no additional delegation is adopted by this table.',
        'policy:L21': 'R0/R8/R9/R10 and the introduction explicitly preserve owner judgment.',
        'reading:L1': 'Document title.',
        'reading:L3': 'Target clearly declares it is unadopted.',
        'reading:L4': 'Proposed-choice disclaimer limits every finding; it does not supply ratification.',
        'reading:L5': 'Confirms interpretive nature of operational choices; referenced adoption material is outside this input scope.',
        'reading:L7': 'Table headings.', 'reading:L8': 'Table separator.',
        'reading:L9': 'Explicitly preserves the unsettled sufficiency/closure choice; not an invented live grant.',
        'reading:L10': 'Purpose presence is represented but company-purpose semantics and necessity are not established (F2/F4).',
        'reading:L11': 'Receipt-only mapping is an additional choice (F1).',
        'reading:L12': 'Self-approval exclusion matches clause 1.',
        'reading:L13': 'Manager approval matches clause 2; no explicit attestation of necessity (F2).',
        'reading:L14': 'Explicitly identified approval-scope ambiguity; not a contradiction.',
        'reading:L15': 'Strict threshold operators preserved. Finite-positive check is an acknowledged proposed validation choice.',
        'reading:L16': 'Exclusion of alcohol/tips preserved; whole-submission blocking is an explicit operational treatment.',
        'reading:L17': 'Celebration owner approval preserved; semantic classification of purpose is assumed.',
        'reading:L18': 'Reasonable-price uncertainty correctly retained; travel necessity not addressed here (F2).',
        'reading:L19': 'Modesty retained as unresolved; this file does not establish the full behavior for celebration meals.',
        'reading:L20': 'Conditional decomposition of the source alternatives needs review (F3).',
        'reading:L21': 'Matching-exception requirement does not itself create a new permission.',
        'reading:L22': 'Accurately distinguishes case columns from source requirements; no missing-rule claim.',
        'reading:L23': 'Conservative dual-time reading is explicitly acknowledged, not presented as source wording.',
        'reading:L24': 'Unknown categories route to review, not silently to permission.',
        'reading:L26': 'Acknowledges extra ambiguities and preclassified facts.',
        'reading:L27': 'Continuation of the acknowledged fact-classification limitation.',
        'reading:L28': 'Continuation of the acknowledged fact-classification limitation.',
    }
    assert set(rationale) == set(segments)
    non_substantive = {'policy:L1', 'policy:L14', 'reading:L1', 'reading:L7', 'reading:L8'}
    coverage = [{'segment_id': sid, 'disposition': 'NON_SUBSTANTIVE' if sid in non_substantive else 'ASSESSED',
                 'rationale': rationale[sid],
                 'finding_ids': [f['id'] for f in findings if any(c['segment_id'] == sid for c in f['governing_evidence'] + f['operational_evidence'])]}
                for sid in segments]
    response = {'packet_id': packet['packet_id'], 'findings': findings, 'coverage': coverage,
                'limitations': ['Interactive assistant-authored draft observations, not an unattended API run or independent benchmark.',
                                'Both sources are draft lab materials; no contract breach or adopted authority is asserted.',
                                'Only supplied documentation was compared. Actual runtime behavior, omitted documents and company data were not verified.',
                                'Exact quotations and segment coverage do not establish semantic correctness or exhaustive obligation coverage.']}
    write(HERE / 'review.json', response)


if __name__ == '__main__':
    main()
