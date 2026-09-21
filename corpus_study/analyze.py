"""Merge the two independent coding passes, measure agreement, and tabulate the corpus.

  python -B corpus_study/analyze.py

Inputs:  corpus_study/coded/passA.json, passB.json (one object per document, per CODEBOOK.md)
         corpus_study/coded/adjudication.json (optional: my reasoned resolution of disagreements on the key fields)
Outputs: results/corpus_study.json and a printed summary.

Both passes were coded by instances of the same model. Agreement therefore measures noise, not bias.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODED = ROOT / "corpus_study" / "coded"
KEY_FIELDS = ["doc_type", "primary_issue", "outcome", "outcome_scope", "guidance_change", "express_non_precedent",
              "relied_on_later_facts", "past_practice_invoked", "past_practice_treatment", "bright_line_decidable"]


def kappa(a: list, b: list) -> float | None:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else round((po - pe) / (1 - pe), 2)


def main() -> None:
    A = {d["doc_index"]: d for d in json.loads((CODED / "passA.json").read_text(encoding="utf-8"))}
    B = {d["doc_index"]: d for d in json.loads((CODED / "passB.json").read_text(encoding="utf-8"))}
    ids = sorted(A)
    assert ids == sorted(B) == list(range(46)), "both passes must cover documents 0-45"
    adj_path = CODED / "adjudication.json"
    adj = {int(k): v for k, v in json.loads(adj_path.read_text(encoding="utf-8")).items()} if adj_path.exists() else {}

    agreement = {}
    for f in KEY_FIELDS:
        a, b = [str(A[i][f]) for i in ids], [str(B[i][f]) for i in ids]
        agreement[f] = {"raw_agreement": round(sum(x == y for x, y in zip(a, b)) / len(ids), 2), "cohen_kappa": kappa(a, b),
                        "disagreeing_docs": [i for i in ids if str(A[i][f]) != str(B[i][f])]}
    issue_jaccard = []
    for i in ids:
        sa, sb = set(A[i]["issues"]), set(B[i]["issues"])
        issue_jaccard.append(len(sa & sb) / len(sa | sb))

    def final(i: int, f: str):
        if str(A[i][f]) == str(B[i][f]):
            return A[i][f]
        return adj.get(i, {}).get(f, "DISPUTED")

    hashes_ok = sum(bool(A[i]["sha256_matches_inventory"]) for i in ids)
    tab = {f: dict(Counter(str(final(i, f)) for i in ids)) for f in KEY_FIELDS}
    any_issue = Counter()
    for i in ids:
        for t in set(A[i]["issues"]) & set(B[i]["issues"]):        # an issue counts only if both coders listed it
            any_issue[t] += 1

    def both(f, v):      # lower bound: both coders agree the field has value v
        return [i for i in ids if str(A[i][f]) == str(B[i][f]) == str(v)]

    def either(f, v):    # upper bound: at least one coder says v
        return [i for i in ids if str(v) in (str(A[i][f]), str(B[i][f]))]

    n = len(ids)
    bounds = {
        "general_reading_stated": [len(both("outcome_scope", "GENERAL_READING")), len(either("outcome_scope", "GENERAL_READING"))],
        "express_non_precedent": [len(both("express_non_precedent", True)), len(either("express_non_precedent", True))],
        "guidance_change_recommended_or_committed": [
            len([i for i in ids if A[i]["guidance_change"] != "NONE" and B[i]["guidance_change"] != "NONE"]),
            len([i for i in ids if A[i]["guidance_change"] != "NONE" or B[i]["guidance_change"] != "NONE"])],
        "guidance_change_committed": [len(both("guidance_change", "COMMITTED")), len(either("guidance_change", "COMMITTED"))],
        "outcome_relied_on_facts_gathered_later": [len(both("relied_on_later_facts", True)), len(either("relied_on_later_facts", True))],
        "past_practice_or_advice_invoked": [len(both("past_practice_invoked", True)), len(either("past_practice_invoked", True))],
        "original_decision_bright_line_decidable": [len(both("bright_line_decidable", "YES")), len(either("bright_line_decidable", "YES"))],
        "primary_issue_is_discretion_or_exception": [len(both("primary_issue", "DISCRETION_EXCEPTION")), len(either("primary_issue", "DISCRETION_EXCEPTION"))],
        "primary_issue_is_rule_meaning": [len(both("primary_issue", "RULE_MEANING")), len(either("primary_issue", "RULE_MEANING"))],
    }
    # Among documents where past practice or advice was invoked (both coders), how was it treated?
    pp = both("past_practice_invoked", True)
    pp_treat = Counter(str(final(i, "past_practice_treatment")) for i in pp)
    # General readings that both coders saw: did they favour the claimant (expand what is payable) or not?
    gr = both("outcome_scope", "GENERAL_READING")
    gr_outcomes = Counter(str(final(i, "outcome")) for i in gr)
    # A general reading stated AND a disclaimer of precedent in the same document
    gr_and_disclaimed = [i for i in ids if "GENERAL_READING" in (A[i]["outcome_scope"], B[i]["outcome_scope"])
                         and True in (A[i]["express_non_precedent"], B[i]["express_non_precedent"])]
    amounts = sorted(x for x in (A[i]["amount_in_dispute_gbp"] for i in ids) if isinstance(x, (int, float)))
    years = Counter(A[i]["decision_year"] for i in ids)

    # Side by side with the follow-up packet's 13 hand-checked boundary cases (its document numbers are 1-based).
    followup = ROOT / "evidence_followup" / "sophon_ipsa_followup" / "case_checks.json"
    side_by_side = []
    if followup.exists():
        for c in json.loads(followup.read_text(encoding="utf-8")):
            i = c["document"] - 1
            side_by_side.append({"doc_index": i, "followup_boundary": c["boundary"],
                                 **{f: [A[i][f], B[i][f]] for f in ("outcome_scope", "express_non_precedent", "guidance_change",
                                                                    "relied_on_later_facts", "past_practice_treatment", "primary_issue")}})

    out = {"documents": n, "side_by_side_with_followup_hand_checks_[passA,passB]": side_by_side, "pdf_hashes_matching_packet_inventory": hashes_ok, "decision_years": dict(sorted(years.items())),
           "amount_in_dispute_gbp": {"n": len(amounts), "median": amounts[len(amounts) // 2], "min": amounts[0], "max": amounts[-1],
                                     "under_1000": sum(a < 1000 for a in amounts)},
           "inter_coder_agreement": agreement, "mean_jaccard_of_issue_lists": round(sum(issue_jaccard) / n, 2),
           "counts_as_[both_coders, either_coder]_of_46": bounds,
           "issue_present_per_both_coders": dict(any_issue.most_common()),
           "past_practice_treatment_where_both_coders_saw_it_invoked": dict(pp_treat),
           "outcomes_of_documents_with_an_agreed_general_reading": dict(gr_outcomes),
           "documents_with_a_general_reading_and_a_precedent_disclaimer": gr_and_disclaimed,
           "final_tabulation_(agreed_or_adjudicated)": tab, "adjudicated_documents": sorted(adj)}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "corpus_study.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(f"{n} documents; hashes matching inventory: {hashes_ok}; median amount in dispute: {out['amount_in_dispute_gbp']['median']}")
    print("agreement (raw / kappa):")
    for f, v in agreement.items():
        print(f"  {f:28s} {v['raw_agreement']:.2f} / {v['cohen_kappa']}   disagree: {v['disagreeing_docs']}")
    print("counts [both coders, either coder] of 46:")
    for k, v in bounds.items():
        print(f"  {k:46s} {v}")
    print("issues (both coders):", dict(any_issue.most_common()))
    print("past practice treated as:", dict(pp_treat), "| outcomes where a general reading was agreed:", dict(gr_outcomes))
    print("general reading AND precedent disclaimer in same document:", gr_and_disclaimed)


if __name__ == "__main__":
    main()
