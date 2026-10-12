"""E5 lifecycle state of a proposed native change (PROTOCOL.md §5; written after the freeze).

The state is computed from evidence, never read from a claim. DEPLOYED/IMPLEMENTED would require a deployment
receipt from a deployment system AND an authorization by a role whose roster entry may approve DEPLOYMENT. The E3
roster has no such role and E5 performs no deployment, so those states are unreachable here by construction.
"""
from __future__ import annotations

STATES = ("CHANGE_REQUIRED_NOT_PROPOSED", "PROPOSED_NOT_DEPLOYED", "PROPOSED_VERIFIED_NOT_DEPLOYED", "PROPOSAL_REJECTED_BY_VERIFICATION")


def state(proposal: dict | None, roster: dict, verification: dict | None = None, forged_claimed_state: str | None = None,
          deployment_authorization: dict | None = None, deployment_receipt: dict | None = None, approvals: dict | None = None) -> dict:
    reasons = []
    if forged_claimed_state is not None:
        reasons.append("CLAIM_WITHOUT_EVIDENCE")  # a claimed state is ignored, never an input
    if proposal is None or proposal.get("status") != "PROPOSED_NOT_DEPLOYED" or not proposal.get("patch"):
        return {"state": "CHANGE_REQUIRED_NOT_PROPOSED", "reasons": reasons + ["NO_VALID_PROPOSAL"], "deployed": False}
    if verification is None:
        st = "PROPOSED_NOT_DEPLOYED"
    elif verification.get("status") == "VERIFIED_FOR_LAB_CHECKS":
        st = "PROPOSED_VERIFIED_NOT_DEPLOYED"
    elif verification.get("status") == "NONCONFORMING_IMPLEMENTATION":
        st = "PROPOSAL_REJECTED_BY_VERIFICATION"
    else:
        st = "PROPOSED_NOT_DEPLOYED"
        reasons.append("VERIFICATION_INCONCLUSIVE")
    if deployment_authorization is not None:
        ap = (approvals or {}).get(deployment_authorization.get("approval_id"), {})
        role = roster["roles"].get(ap.get("approver_role"), {})
        if "DEPLOYMENT" not in role.get("may_approve", []) or (ap.get("claim") or {}).get("kind") != "DEPLOYMENT":
            reasons.append("DEPLOYMENT_AUTHORITY_NOT_RECOGNIZED")
    if deployment_receipt is None:
        reasons.append("NO_DEPLOYMENT_RECEIPT")
    return {"state": st, "reasons": sorted(set(reasons)), "deployed": False}
