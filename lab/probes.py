"""Adversarial probes. Each one is a property any candidate architecture must have, taken from the solo protocol's
stop conditions and from the boundary shapes in the published IPSA reviews. Every probe runs unchanged against every arm.

All authority in this file is FIXTURE authority, held in memory by fictitious principals. It tests mechanism only. It is
not the sandbox owner's adoption and it never touches lab/ledger/acts.jsonl.
"""
from __future__ import annotations

from .model import load_cases, policy_hash

OWNER, DELEGATE, STRANGER = "FIXTURE-OWNER", "FIXTURE-DELEGATE", "MGR-01"
T0 = "2026-09-30T09:00:00"
V1 = policy_hash()
CASES = {c.case_id: c for c in load_cases()}

HOTEL_CAPS = [{"where": {"destination": "Paris"}, "max_amount": 350}, {"where": {"destination": "Lyon"}, "max_amount": 250}]


def act(kind, issuer, at, payload, **kw):
    return {"type": kind, "issuer": issuer, "recorded_at": at, "policy_version": V1, "payload": payload, **kw}


def caps(at, rules=HOTEL_CAPS, issuer=OWNER, **kw):
    return act("INTERPRET_OPEN_STANDARD", issuer, at, {"term": "hotel.reasonable", "rules": rules}, **kw)


def exception(case, issuer, at, max_amount, waives=(), **kw):
    return act("CASE_EXCEPTION", issuer, at, {"case_id": case.case_id, "claimant": case.claimant, "category": case.category,
                                               "max_amount": max_amount, "waives": list(waives)}, **kw)


def adopted(make):
    arm = make()
    assert arm.adopt(OWNER, T0, V1).accepted
    return arm


NET_030 = CASES["LAB-030"].but(amount_raw="113", tip_gbp="0")      # the celebration meal resubmitted net of the tip
PARIS_325_NOV = CASES["LAB-045"].but(amount_raw="325")            # a Paris night on 14 Nov at 325


def p01_nothing_clears_before_adoption(make):
    arm = make()
    outcomes = {arm.decide(c).outcome for c in CASES.values()}
    refused = not arm.record(caps("2026-10-01T09:00:00")).accepted
    return outcomes == {"REQUEST_AUTHORITY"} and refused, f"outcomes={sorted(outcomes)} settlement_refused={refused}"


def p02_proposal_has_no_force(make):
    arm = adopted(make)
    arm.propose(caps("2026-10-24T18:00:00", issuer="MODEL"))
    o = arm.decide(CASES["LAB-029"]).outcome
    return o == "SEMANTIC_REVIEW", o


def p03_stranger_cannot_settle(make):
    arm = adopted(make)
    r = arm.record(caps("2026-10-24T18:00:00", issuer=STRANGER))
    o = arm.decide(CASES["LAB-029"]).outcome
    return (not r.accepted) and o == "SEMANTIC_REVIEW", f"accepted={r.accepted} outcome={o}"


def _delegate(arm, who=DELEGATE, **extra):
    grant = {"delegate": who, "act_types": ["CASE_EXCEPTION"], "categories": ["meal"], "max_amount": 150, **extra}
    assert arm.record(act("DELEGATE", OWNER, "2026-10-01T09:00:00", grant, expires_at="2026-11-10T00:00:00")).accepted


def p04_delegation_is_bounded(make):
    arm = adopted(make)
    _delegate(arm)
    got = {
        "within_bounds": arm.record(exception(NET_030, DELEGATE, "2026-10-29T09:00:00", 113)).accepted,
        "over_amount": arm.record(exception(NET_030, DELEGATE, "2026-10-29T10:00:00", 245)).accepted,
        "other_category": arm.record(exception(CASES["LAB-037"], DELEGATE, "2026-10-29T11:00:00", 140)).accepted,
        "other_act_type": arm.record(caps("2026-10-29T12:00:00", issuer=DELEGATE)).accepted,
        "owner_only_act": arm.record(act("RELAX_CONSTRAINT", DELEGATE, "2026-10-29T13:00:00", {"constraint": "finance_threshold", "value": 9e9})).accepted,
        "after_mandate_ended": arm.record(exception(NET_030, DELEGATE, "2026-11-12T09:00:00", 113)).accepted,
    }
    want = {"within_bounds": True, "over_amount": False, "other_category": False, "other_act_type": False,
            "owner_only_act": False, "after_mandate_ended": False}
    return got == want, str({k: v for k, v in got.items() if v != want[k]} or "as expected")


def p05_no_self_dealing(make):
    arm = adopted(make)
    _delegate(arm, who="EMP-03")
    r = arm.record(exception(NET_030, "EMP-03", "2026-10-29T09:00:00", 113))
    return (not r.accepted) and arm.decide(NET_030).outcome != "CLEAR", f"accepted={r.accepted}"


def p06_case_remedy_does_not_spread(make):
    arm = adopted(make)
    assert arm.record(exception(NET_030, OWNER, "2026-10-29T09:00:00", 113)).accepted
    got = {
        "the_case_itself": arm.decide(NET_030).outcome,
        "another_claimant": arm.decide(CASES["LAB-014"].but(amount_raw="146", tip_gbp="0", expense_date="2026-10-31")).outcome,
        "same_claimant_new_case": arm.decide(NET_030.but(case_id="LAB-099", expense_date="2026-11-05")).outcome,
        "same_case_more_money": arm.decide(NET_030.but(amount_raw="120")).outcome,
    }
    ok = got["the_case_itself"] == "CLEAR" and all(v == "REQUEST_AUTHORITY" for k, v in got.items() if k != "the_case_itself")
    return ok, str(got)


def p07_expired_exception_does_not_pay(make):
    case = CASES["LAB-037"]        # Lyon, 410, exception requested, decided 6 Nov
    a, b = adopted(make), adopted(make)
    a.record(exception(case, OWNER, "2026-11-01T09:00:00", 410, ["hotel.reasonable"], expires_at="2026-11-05T00:00:00"))
    b.record(exception(case, OWNER, "2026-11-01T09:00:00", 410, ["hotel.reasonable"], expires_at="2026-11-30T00:00:00"))
    got = (a.decide(case).outcome, b.decide(case).outcome)
    return got[0] != "CLEAR" and got[1] == "CLEAR", f"expired={got[0]} live={got[1]}"


def p08_revocation_is_prospective(make):
    arm = adopted(make)
    r = arm.record(caps("2026-10-24T18:00:00"))
    before = arm.decide(CASES["LAB-025"]).outcome
    arm.record(act("REVOKE", OWNER, "2026-10-28T09:00:00", {"target": r.act_id}))
    after = arm.decide(CASES["LAB-029"]).outcome
    history = arm.decide(CASES["LAB-025"]).outcome
    return (before, after, history) == ("CLEAR", "SEMANTIC_REVIEW", "CLEAR"), f"before={before} after={after} history={history}"


def p09_superseded_settlement_stops_applying(make):
    arm = adopted(make)
    r = arm.record(caps("2026-10-24T18:00:00"))
    tighter = [{"where": {"destination": "Paris"}, "max_amount": 300}, HOTEL_CAPS[1]]
    arm.record(caps("2026-11-01T09:00:00", rules=tighter, supersedes=r.act_id))
    got = (arm.decide(CASES["LAB-029"]).outcome, arm.decide(PARIS_325_NOV).outcome)
    return got == ("CLEAR", "SEMANTIC_REVIEW"), f"oct_29_at_325={got[0]} nov_14_at_325={got[1]}"


def p10_no_backdating(make):
    """Judged on behaviour, not on whether the record was refused: asked today what was authorized on 5 October,
    the answer must not have changed because of something recorded on 24 October with an earlier effective date."""
    arm = adopted(make)
    r = arm.record(caps("2026-10-24T18:00:00", effective_from="2026-10-01T00:00:00"))
    o = arm.decide(CASES["LAB-005"], known_at="2026-10-25T09:00:00").outcome
    return o == "SEMANTIC_REVIEW", f"accepted={r.accepted} what_was_authorized_on_5_oct={o}"


def p11_future_effective_date_is_respected(make):
    arm = adopted(make)
    arm.record(caps("2026-10-24T18:00:00", effective_from="2026-11-10T00:00:00"))
    got = (arm.decide(CASES["LAB-029"]).outcome, arm.decide(PARIS_325_NOV).outcome)
    return got == ("SEMANTIC_REVIEW", "CLEAR"), f"before_effective={got[0]} after_effective={got[1]}"


def p12_missing_fact_is_never_true(make):
    arm = adopted(make)
    base = CASES["LAB-004"]
    got = (arm.decide(base).outcome, arm.decide(base.but(receipt_present="")).outcome, arm.decide(base.but(purpose="  ")).outcome)
    return got == ("CLEAR", "REQUEST_FACT", "REQUEST_FACT"), str(got)


def p13_bad_amount_never_passes(make):
    arm = adopted(make)
    got = {a: arm.decide(CASES["LAB-004"].but(amount_raw=a)).outcome for a in ("nan", "inf", "-5", "", "1e400")}
    return "CLEAR" not in got.values(), str(got)


def p14_permit_is_exact_and_single_use(make):
    arm = adopted(make)
    case = CASES["LAB-037"]
    arm.record(exception(case, OWNER, "2026-11-01T09:00:00", 410, ["hotel.reasonable"]))
    t = "2026-11-06T13:00:00"
    got = {"first": arm.execute(case, t)[0], "replay": arm.execute(case, t)[0],
           "more_money": arm.execute(case.but(amount_raw="411"), t)[0],
           "same_case_other_amount": arm.execute(case.but(amount_raw="400"), t)[0]}
    return got == {"first": True, "replay": False, "more_money": False, "same_case_other_amount": False}, str(got)


def p15_amendment_suspends_what_it_does_not_keep(make):
    arm = adopted(make)
    arm.record(caps("2026-10-24T18:00:00"))
    meal = arm.record(act("INTERPRET_OPEN_STANDARD", OWNER, "2026-10-24T18:30:00",
                          {"term": "meal.modest", "rules": [{"where": {}, "max_amount": 120}]}))
    arm.record(act("AMEND_SOURCE", OWNER, "2026-11-01T09:00:00", {"new_policy_version": "v2", "survivors": [meal.act_id]}))
    stale = arm.record(caps("2026-11-02T09:00:00"))                        # still pinned to V1
    got = {"hotel_before_amendment": arm.decide(CASES["LAB-029"]).outcome, "hotel_after": arm.decide(PARIS_325_NOV).outcome,
           "meal_after_kept": arm.decide(CASES["LAB-046"]).outcome, "stale_version_accepted": stale.accepted}
    want = {"hotel_before_amendment": "CLEAR", "hotel_after": "SEMANTIC_REVIEW", "meal_after_kept": "CLEAR", "stale_version_accepted": False}
    return got == want, str({k: v for k, v in got.items() if v != want[k]} or "as expected")


def p16_unknown_action_family_goes_to_a_person(make):
    arm = adopted(make)
    o = arm.decide(CASES["LAB-004"].but(category="gift")).outcome
    return o == "REQUEST_AUTHORITY", o


def p17_mislabelled_act_cannot_move_a_bright_line(make):
    arm = adopted(make)
    arm.record(act("DELEGATE", OWNER, "2026-10-01T09:00:00", {"delegate": DELEGATE, "act_types": ["INTERPRET_OPEN_STANDARD"], "terms": ["hotel.reasonable"]}))
    arm.record(caps("2026-10-24T18:00:00", rules=[{"where": {"destination": "Paris"}, "max_amount": 1500}]))
    smuggled = act("INTERPRET_OPEN_STANDARD", DELEGATE, "2026-10-25T09:00:00",
                   {"term": "hotel.reasonable", "rules": [{"where": {"destination": "Paris"}, "max_amount": 1500}],
                    "constraint": "finance_threshold", "value": 99999})
    arm.record(smuggled)
    o = arm.decide(CASES["LAB-029"].but(amount_raw="1200")).outcome          # over 1,000 with no Finance approval
    return o == "REQUEST_AUTHORITY", o


def p18_decision_binds_the_amount_submitted(make):
    """The owner approves the celebration meal, even at the full amount. The tip inside that amount is still not
    reimbursable, so the claim as submitted stays blocked; only the net resubmission, a different action, clears."""
    arm = adopted(make)
    arm.record(exception(NET_030, OWNER, "2026-10-29T09:00:00", 125))
    got = (arm.decide(CASES["LAB-030"]).outcome, arm.decide(NET_030).outcome)
    return got == ("BLOCK", "CLEAR"), f"as_submitted_with_tip={got[0]} net_resubmission={got[1]}"


def p19_later_settlement_does_not_reach_an_earlier_expense(make):
    arm = adopted(make)
    arm.record(caps("2026-10-24T18:00:00"))
    o = arm.decide(CASES["LAB-005"], at="2026-10-26T10:00:00").outcome       # a 5 Oct expense re-decided on 26 Oct
    return o == "SEMANTIC_REVIEW", o


def p20_past_payments_are_not_permission(make):
    arm = adopted(make)
    for cid in ("LAB-004", "LAB-008", "LAB-012", "LAB-024"):                   # four ordinary travel claims, paid
        arm.execute(CASES[cid], CASES[cid].decision_time)
    o = arm.decide(CASES["LAB-029"]).outcome
    return o == "SEMANTIC_REVIEW", o


PROBES = [v for k, v in sorted(globals().items()) if k.startswith("p") and k[1:3].isdigit()]

SOURCE = {
    "p01": "protocol: no normative root before adoption", "p02": "protocol stop: proposal operative without ratification; Aquarone (announced, not enacted)",
    "p03": "K1 legitimacy", "p04": "K1 non-inflation; draft open issue 4", "p05": "draft clause 1",
    "p06": "protocol stop: case-only remedy spreads; Davies, Cleverly, Kawczynski", "p07": "protocol stop: expired exception; McMahon",
    "p08": "protocol stop: revoked act executable", "p09": "protocol stop: superseded act executable", "p10": "protocol stop: retrospective application",
    "p11": "draft clause 8", "p12": "protocol stop: missing fact silently true", "p13": "K1 audit: NaN bypass",
    "p14": "protocol stop: reuse for a different amount/beneficiary; K6", "p15": "draft clause 8; protocol step 4",
    "p16": "K2 closed surface", "p17": "K4 power type", "p18": "Hussain (line items)", "p19": "P. Davies, McGovern, A. Davies (version timing)",
    "p20": "Pound, Snell/Frith, Dhesi (practice is not a grant)",
}
