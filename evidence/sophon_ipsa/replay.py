"""A conservative, label-blind public-data replay; standard library only."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CSV_URL = "https://www.theipsa.org.uk/api/download?type=individualBusinessCosts&year=23_24"
SCHEME_URL = "https://assets.ctfassets.net/nc7h1cs4q6ic/1neQ7j3vniH5Zpt9XpJIOA/4978bbea5a5a1ab13ce9f05cca7e2b0b/Fifteenth_Edition_of_the_Scheme_2023-24.pdf"
RAW = DATA / "individual_business_costs_2023_24.csv"
POLICY = ROOT / "policy_15th.json"
SAMPLE = RESULTS / "sample_features.json"
DECISIONS = RESULTS / "decisions.json"
FREEZE = RESULTS / "freeze.json"
FEATURES = ("Date", "Claim Number", "Parliamentary ID", "Constituency", "Category", "Cost Type", "Short Description", "Details", "Journey Type", "From", "To", "Travel", "Nights", "Mileage", "Amount Claimed", "Supply Month", "Supply Period")
LABELS = ("Amount Paid", "Amount Not Paid", "Amount Repaid", "Status", "Reason If Not Paid")
SALT = "sophon-ipsa-v1"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(p: Path, value: object) -> None:
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def fetch() -> None:
    DATA.mkdir(exist_ok=True)
    for url, dest in ((CSV_URL, RAW), (SCHEME_URL, DATA / "scheme_15th.pdf")):
        if not dest.exists():
            with urlopen(url, timeout=90) as src, dest.open("wb") as out:
                for block in iter(lambda: src.read(1024 * 1024), b""):
                    out.write(block)
        print(dest.name, dest.stat().st_size, sha_file(dest))


def prepare() -> None:
    if FREEZE.exists():
        raise SystemExit("Frozen replay exists; do not change sample. Use a new directory for a new experiment.")
    selected = []
    n_eligible = 0
    with RAW.open(encoding="utf-8-sig", newline="") as f:
        for idx, row in enumerate(csv.DictReader(f)):
            try:
                date = dt.datetime.strptime(row["Date"], "%d/%m/%Y").date()
            except ValueError:
                continue
            if not dt.date(2023, 4, 1) <= date <= dt.date(2024, 3, 31):
                continue
            n_eligible += 1
            rank = sha_bytes(f"{SALT}|{row['Claim Number']}|{idx}".encode())
            selected.append((rank, date.isoformat(), idx, {k: row[k] for k in FEATURES}))
    selected.sort(key=lambda x: x[0])
    sample = sorted(selected[:1000], key=lambda x: (x[1], x[2]))
    if len(sample) != 1000:
        raise ValueError("Fewer than 1,000 eligible publication rows")
    # Input index permits later joining but is never a feature. Remove names and constituency
    # from the artifact: they are unnecessary for this limited, safe public-data test.
    items = [{"row_index": idx, "claim_key": sha_bytes(f"{idx}|{row['Claim Number']}".encode())[:16],
              "date": date, "features": {k: v for k, v in row.items() if k not in ("Parliamentary ID", "Constituency", "Claim Number")}}
             for _, date, idx, row in sample]
    write_json(SAMPLE, items)
    write_json(RESULTS / "sample_manifest.json", {"selection": "SHA-256 rank of SALT|Claim Number|zero-based input row index, then expense-date order", "salt": SALT,
                "eligible_rows": n_eligible, "sample_size": len(items), "raw_sha256": sha_file(RAW), "policy_sha256": sha_file(POLICY),
                "sample_sha256": sha_file(SAMPLE), "first_expense_date": items[0]["date"], "last_expense_date": items[-1]["date"]})
    print("Prepared feature-only sample:", len(items), "of", n_eligible, "eligible rows")


def decide(f: dict) -> dict:
    category, kind = f["Category"], f["Cost Type"]
    facts = ["supporting_evidence_and_validation", "certified_parliamentary_purpose", "available_budget_and_other_funding"]
    semantic = []
    relevant = ["Part A.1–2", "1.1(d)", "3.2", "3.8–3.13"]
    if category == "Accommodation":
        facts += ["mp_accommodation_eligibility", "registered_property_or_accommodation_mode"]
        relevant += ["4.2–4.13"]
        if "Hotel" in kind:
            facts += ["nightly_rate_location_and_stay_group", "dependant_registration_if_applicable"]
    elif category in ("MP Travel", "Staff Travel", "Dependant Travel"):
        facts += ["journey_purpose_and_route", "actual_traveller_and_commuting_status"]
        relevant += ["9.1–9.31"]
        if category == "Dependant Travel":
            facts.append("dependant_registration")
        if "Taxi" in kind or "Vehicle hire" in kind:
            facts.append("available_transport_alternatives_and_necessity")
            semantic.append("reasonable_transport_alternative")
        if "Mileage" in kind:
            facts.append("year_to_date_mileage_and_applicable_rate")
        if "Rail" in kind or "Air" in kind:
            facts.append("comparable_permitted_fare_at_booking")
        if "Hotel" in kind or "Subsistence" in kind:
            facts.append("overnight_stay_and_location")
    elif category == "Office Costs":
        facts.append("office_cost_purpose_and_item_eligibility")
        relevant.append("Chapter 6")
    elif category == "Staffing":
        facts.append("contract_and_staffing_eligibility")
        relevant.append("Chapter 7")
    else:
        facts.append("category_specific_eligibility")
        relevant.append("Chapter 10")
    # These are fact-gated decisions. Positive published outcomes are never used as proof.
    # No BLOCK rule is asserted solely from free-form description or an ambiguous category.
    return {"decision": "REQUEST_FACT", "missing_facts": sorted(set(facts)),
            "semantic_residuals": semantic, "source_sections": relevant,
            "proof": "Public row does not include evidence, purpose certification or budget state; §2.3 prevents inference of reusable authority from historical outcomes."}


def score() -> None:
    if FREEZE.exists():
        raise SystemExit("Frozen replay exists; do not re-score the committed experiment.")
    manifest = read_json(RESULTS / "sample_manifest.json")
    if sha_file(SAMPLE) != manifest["sample_sha256"] or sha_file(POLICY) != manifest["policy_sha256"]:
        raise SystemExit("Sample or policy changed after preparation")
    items = read_json(SAMPLE)
    decisions = [{"claim_key": item["claim_key"], "row_index": item["row_index"], "date": item["date"],
                  "category": item["features"]["Category"], "cost_type": item["features"]["Cost Type"],
                  **decide(item["features"])} for item in items]
    write_json(DECISIONS, decisions)
    write_json(FREEZE, {**manifest, "decisions_sha256": sha_file(DECISIONS), "runtime_sha256": sha_file(Path(__file__)),
                        "outcomes_used_in_score": False, "sample_outcomes_inspected": False})
    print("Frozen:", sha_file(DECISIONS), Counter(d["decision"] for d in decisions))


def reveal() -> None:
    freeze = read_json(FREEZE)
    if sha_file(DECISIONS) != freeze["decisions_sha256"] or sha_file(SAMPLE) != freeze["sample_sha256"] or sha_file(RAW) != freeze["raw_sha256"]:
        raise SystemExit("Frozen source, sample or decisions changed")
    decisions = read_json(DECISIONS)
    chosen = {d["row_index"]: d for d in decisions}
    labels = {}
    with RAW.open(encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i in chosen:
                labels[i] = {k: row[k] for k in LABELS}
    if len(labels) != len(chosen):
        raise ValueError("Some publication rows were lost")
    outcomes = Counter()
    by_category = defaultdict(Counter)
    facts = Counter()
    semantic = Counter()
    comparisons = []
    for d in decisions:
        label = labels[d["row_index"]]
        status = label["Status"]
        outcomes[status] += 1
        by_category[d["category"]][status] += 1
        facts.update(d["missing_facts"])
        semantic.update(d["semantic_residuals"])
        comparisons.append({"claim_key": d["claim_key"], "date": d["date"], "category": d["category"],
                            "decision": d["decision"], "published_status": status,
                            "published_amount_paid": label["Amount Paid"], "published_amount_not_paid": label["Amount Not Paid"],
                            "published_amount_repaid": label["Amount Repaid"]})
    write_json(RESULTS / "aggregate.json", {"total": len(decisions), "decisions": dict(Counter(d["decision"] for d in decisions)),
               "published_status": dict(outcomes), "by_category": {k: dict(v) for k, v in by_category.items()},
               "missing_facts": dict(facts), "semantic_residual_classes": dict(semantic),
               "observed_deterministic_coverage": sum(d["decision"] in ("CLEAR", "BLOCK") for d in decisions) / len(decisions),
               "unauthorized_CLEAR_observed": 0, "authority_settlements": 0,
               "note": "Zero autonomous CLEARs is a vacuous safety result; statuses are not normative ground truth and expense dates are not decision dates."})
    write_json(RESULTS / "comparison.json", comparisons)
    print(json.dumps(read_json(RESULTS / "aggregate.json"), indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("fetch", "prepare", "score", "reveal"))
    command = p.parse_args().command
    {"fetch": fetch, "prepare": prepare, "score": score, "reveal": reveal}[command]()
