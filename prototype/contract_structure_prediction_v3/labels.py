"""Frozen label vocabulary and deterministic labeling rules (V3 masked-structure pilot).

Rules were written while reading TRAINING documents only (4 credit agreements, 4 vendor SLAs) and are
frozen (hash in frozen/freeze_receipt.json) before any heldout document is parsed or labeled.
Labels are PROVISIONAL_AGENT_AUTHORED: an agent-written rule set, not independent human adjudication.
A heading or unit that matches no rule is OTHER; [Reserved] units are RESERVED and never targets.
"""
from __future__ import annotations

import re

VERSION = "labels-v1-2026-10-13"

# ---- Dimension 3a: section function (document-level presence) -------------------------------------
# Credit agreements: rules over the ARTICLE heading (first match wins).
CA_SECTION_RULES = [
    ("RESERVED", r"^\[?reserved\]?$"),
    ("DEFINITIONS", r"definition|interpretation"),
    ("AFFIRMATIVE_COVENANTS", r"affirmative covenant"),
    ("NEGATIVE_COVENANTS", r"negative covenant"),
    ("FINANCIAL_COVENANTS", r"financial covenant"),
    ("COVENANTS_COMBINED", r"covenant"),
    ("GUARANTY", r"guarant"),
    ("REPRESENTATIONS", r"representation"),
    ("CONDITIONS_PRECEDENT", r"condition"),
    ("EVENTS_OF_DEFAULT", r"default"),
    ("AGENCY", r"\bagen(t|cy)\b"),
    ("YIELD_PROTECTION_TAXES", r"change in circumstances|yield protection|increased cost|taxes"),
    ("CREDIT_FACILITIES", r"\bcredits?\b|loans?|commitments?|facilit|amount and terms"),
    ("MISCELLANEOUS", r"miscellaneous|general provisions"),
]

# Vendor SLAs: rules over unit heading + text (a unit may carry several functions).
SLA_SECTION_RULES = [
    ("DEFINITIONS", r"(^|\s)definitions?\b|\"[^\"]{2,60}\" (means|is|are|occurs)"),
    ("SCOPE_APPLICABILITY", r"^appendix[^\n]{0,20}eligible|policy governing the use|applies separately to|depend on the type of account|(this|the) (sla|service level agreement) (applies|governs)"),
    ("SERVICE_COMMITMENT", r"(will|must|shall) (use commercially reasonable efforts to )?(provide|make|maintain)[^.]{0,200}\d{2}(\.\d+)?%|(will|must|shall) provide an? (monthly )?(uptime|availability) percentage"),
    ("CREDIT_SCHEDULE", None),   # computed: >= 2 band boundaries such as "less than 99.9%", "below 99.0%", "< 95.0%"
    ("CREDIT_CALCULATION_APPLICATION", r"credits? (are|is|will be) (calculated|applied|issued|made)|percentage of (the )?monthly (bill|fees|usage)|credited to|apply (any )?service credits|applied (to|against|within)"),
    ("CLAIM_PROCEDURE", r"(submit|request|notify|open|file)[^.]{0,80}(claim|ticket|case|credit|support)[^.]{0,120}within \d+|must (submit|request|notify|open)|requests? for [^.]{0,40}credits?[^.]{0,40}must be made"),
    ("CREDIT_CAP", r"maximum (aggregate )?(amount|number)?[^.]{0,40}credits?|credits?[^.]{0,120}(will|shall) not exceed|in no event[^.]{0,80}exceed"),
    ("EXCLUSIONS", r"exclusions?\b|(does|do|will) not apply to|not entitled to (any )?service credits"),
    ("SOLE_REMEDY", r"(sole|exclusive) (and exclusive )?remed"),
    ("TERMINATION_RIGHT", r"(right|days) to terminate|may terminate"),
    ("MEASUREMENT_METHOD", r"(is|are) (determined|calculated) by subtracting|^calculation$|example calculation|sampled every"),
]

CA_SECTION_FUNCTIONS = [n for n, _ in CA_SECTION_RULES if n != "RESERVED"]
SLA_SECTION_FUNCTIONS = [n for n, _ in SLA_SECTION_RULES]
SECTION_VOCAB = sorted(set(CA_SECTION_FUNCTIONS) | set(SLA_SECTION_FUNCTIONS))   # shared candidate universe

# ---- Dimension 4 (restricted): provision type = credit-agreement subsection function ---------------
# Ordered; first match on the subsection heading wins. Only credit agreements have source-level
# subsections in this corpus; vendor SLAs are flat, so provision-level prediction is NOT_TESTED for SLAs.
CA_PROVISION_RULES = [
    ("RESERVED", r"^\[?reserved\]?$"),
    ("JURY_TRIAL_WAIVER", r"jury"),
    ("COUNTERPARTS_INTEGRATION", r"counterparts|integration|electronic (execution|records)"),
    ("GOVERNING_LAW_JURISDICTION", r"governing law|new york law|judicial proceedings|jurisdiction"),
    ("BAIL_IN_QFC", r"bail-in|affected financial|qfc|covered entit"),
    ("ERRONEOUS_PAYMENTS", r"erroneous"),
    ("SANCTIONS_AML", r"sanction|anti-terror|anti-corruption|patriot|beneficial ownership"),
    ("ERISA", r"erisa"),
    ("DEFINED_TERMS", r"defined terms|^definitions$"),
    ("ACCOUNTING_TERMS", r"accounting terms|gaap"),
    ("BENCHMARK_RATES", r"benchmark|alternate rate|inability to determine|substituted for|^interest rates$"),
    ("AMEND_RESTATE_EXISTING", r"amendment and restatement"),
    ("INTERPRETATION", r"terms generally|interpretive|classification of loans|types of borrowings|divisions|^headings$"),
    ("LETTERS_OF_CREDIT", r"letters? of credit|lc disbursement|issuance and administration"),
    ("COMMITMENT_CHANGES", r"termination, reduction|changes of commitments|expansion option|increase of|extension of"),
    ("COMMITMENTS_BORROWINGS", r"commitments|loans and borrowings|^loans$|requests? for|notice of borrowings|funding of (loans|borrowings)|interest elections|competitive bid|borrowings by"),
    ("REPAYMENT_PREPAYMENT", r"repayment|prepayment|evidence of|maturity"),
    ("FEES_INTEREST", r"^fees$|^interest$|interest rates of loans|computation of interest|agent'?s fee"),
    ("INCREASED_COSTS_ILLEGALITY", r"increased cost|illegality|break funding|funding losses"),
    ("TAXES", r"taxes"),
    ("PAYMENTS_SHARING", r"payments generally|sharing of payments|pro rata"),
    ("MITIGATION_REPLACEMENT", r"mitigation|replacement of"),
    ("DEFAULTING_LENDERS", r"defaulting"),
    ("INTEREST_RATE_LIMITATION", r"interest rate limitation|usury"),
    ("GUARANTEE_TERMS", r"guarant|subrogation|reinstatement|obligations unconditional|^remedies$|contribution|discharge only|waiver by the company|instrument for the payment"),
    ("CONDITIONS_EFFECTIVENESS", r"effective date|effectiveness|each credit|initial loan"),
    ("EXISTENCE_ORGANIZATION", r"existence|^organization|conduct of business"),
    ("AUTHORIZATION_ENFORCEABILITY", r"authorization|corporate action|binding effect|enforceab|approvals|no breach|no conflicts"),
    ("FINANCIAL_CONDITION_NO_MAC", r"financial condition|financial information|material adverse"),
    ("LITIGATION", r"litigation"),
    ("INVESTMENT_COMPANY", r"investment company"),
    ("ENVIRONMENTAL", r"environmental|hazardous"),
    ("FULL_DISCLOSURE", r"disclosure"),
    ("MARGIN_REGULATIONS", r"margin|federal reserve"),
    ("PARI_PASSU", r"pari passu"),
    ("NO_DEFAULT", r"^no default"),
    ("FINANCIAL_REPORTING", r"financial statements|^information$|reporting"),
    ("NOTICE_OF_EVENTS", r"notices? of (material )?events|notice of default"),
    ("PAYMENT_OF_OBLIGATIONS", r"payment of obligations"),
    ("MAINTENANCE_INSURANCE", r"insurance|maintenance of propert"),
    ("BOOKS_INSPECTION", r"inspection|books"),
    ("COMPLIANCE_WITH_LAWS", r"compliance with laws"),
    ("USE_OF_PROCEEDS", r"use of (proceeds|credit|loans)"),
    ("FINANCIAL_RATIO_COVENANT", r"ratio|net worth|financial covenants"),
    ("LIENS", r"liens|negative pledge"),
    ("FUNDAMENTAL_CHANGES", r"fundamental change|consolidation|merger|sales? of assets"),
    ("INDEBTEDNESS", r"indebtedness|certain debt"),
    ("AFFILIATE_TRANSACTIONS", r"transactions with affiliates"),
    ("SUBSIDIARIES", r"subsidiar"),
    ("EVENTS_OF_DEFAULT_LIST", r"events of default"),
    ("EXPENSES_INDEMNITY", r"expenses|indemn"),
    ("AGENT_PROVISIONS", r"agent|arrangers|credit decision|consultation with experts|acknowledgments of lenders|authorization and action|delegation"),
    ("NOTICES_COMMUNICATIONS", r"^notices$|posting of communications"),
    ("WAIVERS_AMENDMENTS", r"waiver|amendment"),
    ("SUCCESSORS_ASSIGNS", r"successors|assign"),
    ("SURVIVAL", r"survival"),
    ("SEVERABILITY", r"severab|unenforceab"),
    ("SETOFF", r"setoff|set-off"),
    ("CONFIDENTIALITY", r"confidential|non-public"),
    ("NO_FIDUCIARY_DUTY", r"fiduciary"),
    ("JUDGMENT_CURRENCY", r"judgment currency"),
]
PROVISION_VOCAB = sorted(n for n, _ in CA_PROVISION_RULES if n != "RESERVED") + ["OTHER"]


def _first(rules, text: str) -> str:
    t = text.lower().strip()
    for name, pat in rules:
        if re.search(pat, t):
            return name
    return "OTHER"


def ca_section_function(heading: str) -> str:
    return _first(CA_SECTION_RULES, heading)


def ca_provision_type(heading: str) -> str:
    return _first(CA_PROVISION_RULES, heading)


def sla_unit_functions(heading: str, text: str) -> list[str]:
    blob = f"{heading} {text}"
    hits = []
    for n, pat in SLA_SECTION_RULES:
        if n == "CREDIT_SCHEDULE":
            if len(re.findall(r"(?i)(less than|below|<|-)\s*\d{2}(\.\d+)?\s*%", blob)) >= 2:
                hits.append(n)
        elif re.search(pat, blob, flags=re.I | re.M):
            hits.append(n)
    return hits or ["OTHER"]


GOV_LAW = re.compile(r"(?i)(?:governed by,? and (?:shall be )?(?:construed|interpreted)|construed in accordance with,? and governed by)[^.]{0,60}?laws? of (?:the )?(State of [A-Z][a-z]+(?: [A-Z][a-z]+)?|England(?: and Wales)?|[A-Z][a-z]+)")


def evidenced_governing_law(text: str) -> dict:
    """Governing law only when an explicit choice-of-law sentence is present; otherwise UNKNOWN."""
    m = GOV_LAW.search(text)
    if not m:
        return {"law": "UNKNOWN", "evidence": None}
    return {"law": m.group(1).upper().replace(" ", "_"), "evidence": text[max(0, m.start() - 40): m.end() + 10]}
