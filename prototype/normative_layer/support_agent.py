"""Independent example support client: no contract rules in its source code."""
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
    print(json.dumps({"client": "SUPPORT", "status": outcome["status"],
                      "credit_to_propose_eur": outcome.get("credit_eur"),
                      "needs_approval": outcome.get("approval_route"),
                      "governing_contract_version": outcome["contract_version"],
                      "execution_authorized": outcome["execution_authorized"]}, sort_keys=True))


if __name__ == "__main__":
    main()
