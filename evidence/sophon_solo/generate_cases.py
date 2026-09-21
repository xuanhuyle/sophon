"""Deterministically generate label-free controlled cases. Run once before adoption."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ["case_id", "sequence", "expense_date", "category", "amount_gbp", "claimant", "approver", "purpose", "destination", "venue", "receipt_present", "manager_approved", "finance_approved", "cfo_approved", "catalog_available", "catalog_unavailability_documented", "travel_mode", "transport_alternative_available", "after_2200_work", "alcohol_gbp", "tip_gbp", "requested_exception", "notes"]

HOTELS = [185, 255, 318, 345, 395, 275, 220, 325, 375, 410, 265, 355]
MEALS = [24, 44, 98, 158, 218, 80, 36, 125, 175, 245, 58, 110]
EQUIPMENT = [35, 115, 280, 520, 850, 1200, 45, 330, 675, 1060, 250, 95]
TRAVEL = [22, 38, 75, 105, 145, 60, 28, 92, 120, 180, 56, 98]


def make(family: str, idx: int, seq: int) -> dict:
    row = dict.fromkeys(FIELDS, "")
    row.update(case_id=f"LAB-{seq:03d}", sequence=seq,
               expense_date=(date(2026, 10, 1) + timedelta(days=seq - 1)).isoformat(),
               category=family, claimant=f"EMP-{(idx % 5) + 1:02d}", approver="MGR-01",
               receipt_present="yes" if idx not in (4, 10) else "no",
               manager_approved="yes" if idx not in (8,) else "no",
               finance_approved="yes" if idx in (5, 9) else "no", cfo_approved="no",
               requested_exception="no")
    if family == "hotel":
        row.update(amount_gbp=HOTELS[idx], purpose="Client workshop; overnight travel required",
                   destination="Paris" if idx % 3 else "Lyon", venue="Hotel",
                   notes="Large event week" if idx in (4, 9) else "Standard business trip")
        if idx == 9:row["requested_exception"] = "yes"
    elif family == "meal":
        row.update(amount_gbp=MEALS[idx], purpose="Team celebration" if idx in (3, 4, 7, 9) else "Work planning meeting",
                   venue="Restaurant" if idx in (3, 4, 7, 9) else "Office",
                   alcohol_gbp="20" if idx in (4, 9) else "0", tip_gbp="12" if idx in (3, 7) else "0",
                   notes="Meal followed a separate meeting" if idx in (3, 7) else "Refreshments during meeting")
        if idx == 7:row["requested_exception"] = "yes"
    elif family == "equipment":
        row.update(amount_gbp=EQUIPMENT[idx], purpose="Workstation equipment",
                   venue="External retailer", catalog_available="yes" if idx not in (2, 6, 10) else "no",
                   catalog_unavailability_documented="yes" if idx in (2, 10) else "no",
                   notes="Urgent replacement" if idx in (2, 6, 10) else "Routine purchase")
    else:
        row.update(amount_gbp=TRAVEL[idx], purpose="Client travel", travel_mode="Taxi" if idx % 2 else "Rail",
                   transport_alternative_available="no" if idx in (1, 5, 7, 11) else "yes",
                   after_2200_work="yes" if idx in (3, 7, 9) else "no",
                   notes="Alternative transport status is a recorded fact, not an interpretation")
    if idx == 11 and family == "equipment":
        row["approver"] = row["claimant"]
    return row


def main() -> None:
    target = ROOT / "cases.csv"
    manifest = ROOT / "manifest.json"
    if target.exists() or manifest.exists():
        raise SystemExit("The case corpus is frozen. Generate in a new directory to start a new experiment.")
    rows = [make(family, i, 4 * i + j + 1) for i in range(12) for j, family in enumerate(("hotel", "meal", "equipment", "travel"))]
    with target.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader();writer.writerows(rows)
    policy = ROOT / "draft_policy.md"
    manifest.write_text(json.dumps({"status": "DRAFT_UNADOPTED", "case_count": 48, "chronology": "2026-10-01 through 2026-11-17, simulated dates",
        "generation": "deterministic 4-family interleaving, 12 variations each, no outcomes",
        "cases_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "draft_policy_sha256": hashlib.sha256(policy.read_bytes()).hexdigest(),
        "initial_settlement_cases": [1, 24], "frozen_holdout_cases": [25, 48],
        "warning": "Synthetic repetition is designed into the test; not evidence of natural interpretation frequency."}, indent=2) + "\n")
    print(manifest.read_text())


if __name__ == "__main__":
    main()
