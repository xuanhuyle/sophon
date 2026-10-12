"""Independent example billing client: same API; no contract rules in its source code."""
import argparse
import json
from urllib.request import Request, urlopen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--contract-key", required=True)
    p.add_argument("--policy-key", required=True)
    p.add_argument("--facts", required=True, help="JSON facts from operational system; NOT verified by V0")
    a = p.parse_args()
    request = {"contract_key": a.contract_key, "policy_key": a.policy_key, "facts": json.loads(a.facts),
               "on_date": "2026-10-12"}
    call = Request(a.base + "/assess", json.dumps(request).encode(), {"Content-Type": "application/json"})
    with urlopen(call, timeout=5) as rsp:
        outcome = json.load(rsp)
    print(json.dumps({"client": "BILLING", "status": outcome["status"],
                      "draft_credit_note_eur": outcome.get("credit_eur"),
                      "approval_route": outcome.get("approval_route"),
                      "contract_version_used": outcome["contract_version"],
                      "payment_or_credit_issued": False}, sort_keys=True))


if __name__ == "__main__":
    main()
