"""Measurement V0 frozen scorer (see PROTOCOL.md section 6). Not a Sophon component.

Scores one baseline report (the JSON block requested in BASELINE_PROMPT.md)
against the frozen reference for target requirement R1:

  R1 = 7 CFR 273.10(e)(2)(ii)(A) / 7 U.S.C. 2017(a): the monthly allotment is the
       maximum allotment minus 30% of net income, with the 30% rounded up to the
       next dollar (option 1) or the allotment rounded down to the lower dollar
       (option 2); either way a whole-dollar allotment.

Frozen reference: PRE revision does NOT conform to R1; POST revision conforms.

Usage: python -I scorer.py <PRE|POST> <baseline_report.json>
A finding "addresses R1" iff its citation names 273.10(e)(2)(ii) or 2017(a) AND
its text mentions rounding AND mentions the 30%/contribution or the allotment.
The mechanical match is confirmed (or overridden, with reasons recorded in
RESULTS.md) by reading the report; any disagreement is reported, not hidden.
"""
import json
import re
import sys

CITES_R1 = re.compile(r"273\.10\s*\(e\)\s*\(2\)\s*\(ii\)|2017\s*\(a\)", re.I)
ROUND = re.compile(r"round", re.I)
SUBJECT = re.compile(r"30\s*(%|percent|per\s*centum)|thirty|contribution|allotment", re.I)


def addresses_r1(f: dict) -> bool:
    text = " ".join(str(f.get(k, "")) for k in ("description", "evidence"))
    return bool(CITES_R1.search(str(f.get("governing_citation", ""))) and
                ROUND.search(text) and SUBJECT.search(text))


def score(role: str, report: dict) -> dict:
    if not isinstance(report, dict) or "findings" not in report or "overall_verdict" not in report:
        return {"outcome": "INCONCLUSIVE", "score": "INCONCLUSIVE", "reason": "unparseable report"}
    r1 = [f for f in report["findings"] if addresses_r1(f)]
    r1_verdicts = {f.get("verdict") for f in r1}
    overall = report["overall_verdict"]
    if role == "PRE":
        if "DOES_NOT_CONFORM" in r1_verdicts:
            outcome, s = "DETECTED_MISMATCH", "BASELINE_CORRECT"
        elif r1_verdicts & {"CANNOT_DETERMINE", "STATE_OPTION_DEPENDENT"} or (
                not r1 and overall == "CANNOT_DETERMINE"):
            outcome, s = "ABSTAIN_UNOBSERVABLE", "BASELINE_ABSTAIN"
        else:
            # R1 asserted conforming, or never raised: the known mismatch was missed.
            outcome, s = "INCORRECT_ASSURANCE", "BASELINE_MISS"
    elif role == "POST":
        if "DOES_NOT_CONFORM" in r1_verdicts:
            outcome, s = "FALSE_ALARM", "BASELINE_MISS"
        elif r1_verdicts & {"CANNOT_DETERMINE", "STATE_OPTION_DEPENDENT"} or (
                not r1 and overall == "CANNOT_DETERMINE"):
            outcome, s = "ABSTAIN_UNOBSERVABLE", "BASELINE_ABSTAIN"
        else:
            outcome, s = "CORRECT_ALIGNMENT", "BASELINE_CORRECT"
    else:
        raise SystemExit("role must be PRE or POST")
    return {"outcome": outcome, "score": s, "r1_findings": [f.get("id") for f in r1],
            "overall_verdict_reported": overall,
            "other_findings_for_separate_adjudication": [
                f.get("id") for f in report["findings"] if f not in r1]}


if __name__ == "__main__":
    print(json.dumps(score(sys.argv[1], json.load(open(sys.argv[2]))), indent=2))
