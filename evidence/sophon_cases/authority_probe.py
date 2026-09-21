"""Conservative query of *evidence of case authority*, never expense clearance."""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def probe(beneficiary: str, cost_class: str, service_date: str):
    date = dt.date.fromisoformat(service_date)
    events = json.loads((ROOT / "authority_events.json").read_text())
    for act in events:
        if act["type"] != "CASE_SPECIFIC_EXCEPTION_EVIDENCE":
            continue
        if act["beneficiary"] == beneficiary and act["cost_class"] == cost_class:
            if dt.date.fromisoformat(act["valid_from"]) <= date <= dt.date.fromisoformat(act["valid_until"]):
                return {"status": "AUTHORITY_EVIDENCE_ONLY", "event": act["id"],
                        "needed_before_CLEAR": ["original authorization", "exact invoice and amount", "effect contract", "current applicable policy"]}
            return {"status": "REQUEST_AUTHORITY", "reason": "known case-specific grant outside its documented service period"}
    return {"status": "REQUEST_AUTHORITY", "reason": "no applicable documented case grant; review outcomes or guidance intentions cannot create general grants"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("beneficiary")
    parser.add_argument("cost_class")
    parser.add_argument("service_date")
    args = parser.parse_args()
    print(json.dumps(probe(args.beneficiary, args.cost_class, args.service_date), indent=2))
