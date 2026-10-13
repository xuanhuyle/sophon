"""Build the human-adjudication package for the 8 V3 SECONDARY heldout cases (offline, deterministic).

Reads only committed files (records, frozen results, frozen label rules and scoring code). Writes only
inside this folder: REVIEW_PACKAGE.md, review_units.csv, review_labels.csv, package_manifest.json.
It never writes to ../results, ../data or ../frozen and makes no network or provider call.

Nothing here adjudicates a label. Every label shown is PROVISIONAL_AGENT_AUTHORED (frozen rules
labels-v1-2026-10-13). Flags are mechanical (rule matches, OTHER units, recorded V3 errors) and are
questions for the human reviewer, not corrections.

    python build_review_package.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path.insert(0, str(V3))

import labels   # noqa: E402  (frozen)
import predict  # noqa: E402  (frozen)

PACKAGE_VERSION = "v3-secondary-adjudication-package-1"
INPUTS = ["data/records_heldout_secondary.json", "results/secondary_repaired_run.json", "data/source_manifest.json",
          "labels.py", "predict.py", "secondary.py", "RESULTS.md", "PROTOCOL.md"]
ARMS3 = ["GLOBAL_FREQ", "FAMILY", "FAMILY_SECTION"]   # EVIDENCED_LAW_FAMILY_SECTION is identical to FS here (checked)
SHORT = {"GLOBAL_FREQ": "G", "FAMILY": "F", "FAMILY_SECTION": "FS"}
HIGH_MASS = 0.25

# Known problems recorded by the V3 agent itself (RESULTS.md / PROTOCOL.md). Quoted as flags, not as corrections.
RECORDED = {
    ("SLA-CLOUDFLARE", "Unit 2"): "RESULTS.md: '1. Business SLA' is a service commitment ('commits to provide') that the rule does not catch -> labelled OTHER. If true, SERVICE_COMMITMENT is VISIBLE in this document.",
    ("SLA-CLOUDFLARE", "Unit 7"): "RESULTS.md: '6. Service Credit Calculation' was missed by the credit-calculation rule -> labelled OTHER. If true, CREDIT_CALCULATION_APPLICATION is VISIBLE, so it cannot be a hidden positive of this case.",
}
DOC_FLAGS = {
    "SLA-CLOUDFLARE": "POST-FREEZE segmentation (numbered-paragraph fallback written after the frozen run returned SLA_TITLE_NOT_FOUND). Headings are truncated at the first word after the number (e.g. '3. Service' for '3. Service Credit Claims'); unit boundaries themselves are unvalidated.",
    "CA-OLDDOMINION": "POST-FREEZE replacement for CA-MOTOROLA (an amendment, screened out after the freeze). Title observed: 'SECOND AMENDED AND RESTATED CREDIT AGREEMENT'. The reviewer should confirm it is a complete restated agreement, not an amendment. TOC lists no sections under Article 7 (EVENTS OF DEFAULT).",
    "CA-MARKEL": "Frozen pipeline (pre-registered primary and secondary). Many subsections fell to OTHER (rules were written on 4 training documents).",
    "SLA-MONGODB": "Frozen pipeline (pre-registered primary and secondary). 5 units only.",
}
BACKOFF_NOTE = ("CONTEXT_CONFLICT backoff fired: fewer than 50% of the VISIBLE provision labels have support under "
                "this section function in training (only CA-BESTBUY splits affirmative/negative covenants). The predictor "
                "fell back to the family-wide distribution, producing a large alphabetical tie. RESULTS.md calls this "
                "'sparse support read as conflict'. Visible-label errors (see multi-match flags) also enter this "
                "consistency check, so human labels for the VISIBLE units matter here, not only for the targets.")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def matching_rules(rules, text: str) -> list[tuple[str, str]]:
    t = text.lower().strip()
    out = []
    for name, pat in rules:
        if pat is None:
            continue
        m = re.search(pat, t)
        if m:
            out.append((name, m.group(0)))
    return out


def codes(flags: str) -> str:
    """Short reason codes for the compact table (full text stays in the per-case tables and the CSV)."""
    out = []
    for f in [x for x in flags.split(" || ") if x]:
        if f.startswith("OTHER"):
            out.append("OTHER")
        elif f.startswith("multi-match"):
            out.append("MULTI-MATCH " + f.split(": ", 1)[1])
        elif f.startswith("RECORDED V3 ERROR"):
            out.append("V3-RECORDED LABEL ERROR")
        elif f.startswith("heading truncated"):
            out.append("TRUNCATED HEADING")
    return ", ".join(out) or "—"


def md(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def load():
    recs = {r["doc_id"]: r for r in json.loads((V3 / "data/records_heldout_secondary.json").read_text(encoding="utf-8"))["records"]}
    run = json.loads((V3 / "results/secondary_repaired_run.json").read_text(encoding="utf-8"))
    man = {d["doc_id"]: d for d in json.loads((V3 / "data/source_manifest.json").read_text(encoding="utf-8"))["documents"]}
    sec = (V3 / "secondary.py").read_text(encoding="utf-8")
    od = {k: re.search(rf'"{k}": "([^"]+)"', sec).group(1) for k in ("url", "sha256", "filing_date", "accession", "title_observed")}
    man["CA-OLDDOMINION"] = {"doc_id": "CA-OLDDOMINION", "issuer": "Old Dominion Electric Cooperative", "source": "SEC EDGAR",
                             "exhibit": "EX-10.1", **od, "selected": "POST_FREEZE replacement (secondary.py REPLACEMENT)"}
    return recs, run, man


def scope_units(rec: dict, case: dict) -> list[dict]:
    if case["task"] == "SECTION":
        return [{"path": s["path"], "heading": s["heading"], "labels": s["functions"], "kind": s.get("kind", "ARTICLE"),
                 "sha": s.get("unit_text_sha256"), "children": [p["heading"] for p in s.get("subunits", [])]}
                for s in rec["sections"]]
    art = next(s for s in rec["sections"] if s["path"] == case["section_path"])
    return [{"path": p["path"], "heading": p["heading"], "labels": [p["provision_type"]], "kind": "SECTION", "sha": None, "children": []}
            for p in art["subunits"]]


def unit_rules(rec: dict, case: dict, u: dict) -> tuple[str, list[str]]:
    """(assigned-by evidence, other matching rules) from the frozen rule tables."""
    if rec["family"] == "CREDIT_AGREEMENT":
        rules = labels.CA_SECTION_RULES if case["task"] == "SECTION" else labels.CA_PROVISION_RULES
        hits = matching_rules(rules, u["heading"])
        if not hits:
            return "no rule matched heading -> OTHER", []
        first = f"{hits[0][0]} <- heading keyword '{hits[0][1]}' (first match wins)"
        return first, [f"{n} ('{k}')" for n, k in hits[1:]]
    # SLA: multi-label over heading + unit text; text not available offline, so only heading matches can be shown
    hh = matching_rules(labels.SLA_SECTION_RULES, u["heading"])
    ev = "multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256)"
    return ev, [f"heading alone matches {n} ('{k}')" for n, k in hh if n not in u["labels"]]


def tie_info(pred: dict, k: int = 3) -> str:
    ranked, probs = pred["ranked"], pred["probs"]
    pk = probs[ranked[k - 1]]["p"]
    idx = [i for i, c in enumerate(ranked) if abs(probs[c]["p"] - pk) < 1e-12]
    crosses = len(idx) > 1 and min(idx) < k <= max(idx)   # 0-based: group starts inside top-k and extends past it
    return f"{len(idx)}-way tie at p={pk:.3f} crosses rank 3" if crosses else ""


def build():
    recs, run, man = load()
    units_rows, label_rows, case_blocks = [], [], []
    counts = {"positives": 0, "negatives": 0, "neg_top3": 0, "neg_top3_high": 0, "neg_brier_only": 0, "units": 0}
    for item in run["cases"]:
        c = item["case"]
        rec = recs[c["doc_id"]]
        src = man[c["doc_id"]]
        preds = {a: item["arms"][a]["prediction"] for a in ARMS3}
        fs, el = item["arms"]["FAMILY_SECTION"]["prediction"], item["arms"]["EVIDENCED_LAW_FAMILY_SECTION"]["prediction"]
        assert fs["ranked"] == el["ranked"] and fs["probs"] == el["probs"], "EL arm differs from FS; package assumes identity"
        pos, neg = c["positives"], c["negatives"]
        masked = set(c["masked_paths"])
        su = scope_units(rec, c)
        # ---- negatives: tie-aware top-3 mass per arm (frozen predict.p_in_top)
        top3 = {n: {a: round(predict.p_in_top(preds[a], n, 3), 3) for a in ARMS3} for n in neg}
        top3_any = sorted(n for n in neg if any(v > 0 for v in top3[n].values()))
        top3_high = sorted(n for n in top3_any if max(top3[n].values()) >= HIGH_MASS)
        counts["positives"] += len(pos); counts["negatives"] += len(neg)
        counts["neg_top3"] += len(top3_any); counts["neg_top3_high"] += len(top3_high)
        counts["neg_brier_only"] += len(neg) - len(top3_any)
        # ---- unit rows
        scope_label = "whole document (top-level units)" if c["task"] == "SECTION" else f"{c['section_path']} ({c['section_heading']})"
        for u in su:
            uid = f"{c['doc_id']}|{u['path']}"
            assigned, others = unit_rules(rec, c, u)
            role = "MASKED_TARGET" if u["path"] in masked else "VISIBLE_CONTEXT"
            flags = []
            if role == "MASKED_TARGET":
                flags.append("carries hidden positive(s): " + ", ".join(l for l in u["labels"] if l in pos))
            if "OTHER" in u["labels"]:
                flags.append("OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT)")
            if others:
                flags.append("multi-match: " + "; ".join(others))
            if (c["doc_id"], u["path"]) in RECORDED:
                flags.append("RECORDED V3 ERROR CANDIDATE: " + RECORDED[(c["doc_id"], u["path"])])
            if c["doc_id"] == "SLA-CLOUDFLARE":
                flags.append("heading truncated by post-freeze fallback")
            if u["labels"] == ["RESERVED"]:
                flags.append("RESERVED (never a target or candidate)")
            prio = "P1" if role == "MASKED_TARGET" else ("P2" if len(flags) > 0 else "P3")
            if rec["family"] == "CREDIT_AGREEMENT":
                locator = (f"EDGAR exhibit; table of contents and body heading '{u['path']}'" if c["task"] == "PROVISION"
                           else f"EDGAR exhibit; '{u['path'].upper()}' heading and its sections")
                evidence_now = ("VERBATIM_TOC_HEADING (extracted by frozen code from the hash-verified file at freeze time)"
                                + ("; article section list available" if c["task"] == "SECTION" else ""))
                body = "BODY_PASSAGE_PENDING_LOCAL_RETRIEVAL" if c["task"] == "PROVISION" else "NOT_REQUIRED_FOR_ARTICLE_FUNCTION (section list shown); body optional"
            else:
                locator = f"web page unit {u['path']} (unit_text_sha256 {u['sha']})"
                evidence_now = "HEADING_ONLY" + (" (TRUNCATED)" if c["doc_id"] == "SLA-CLOUDFLARE" else "")
                body = "UNIT_TEXT_PENDING_LOCAL_RETRIEVAL (labels were assigned from the text)"
            units_rows.append({
                "unit_id": uid, "priority": prio, "case_id": c["case_id"], "task": c["task"], "scope": scope_label,
                "doc_id": c["doc_id"], "path": u["path"], "verbatim_heading": u["heading"], "role": role,
                "agent_labels": "+".join(u["labels"]), "label_status": "PROVISIONAL_AGENT_AUTHORED", "assigned_by": assigned,
                "flags": " || ".join(flags), "source_url": src["url"], "source_sha256": src["sha256"], "locator": locator,
                "unit_text_sha256": u["sha"] or "", "evidence_in_repo": evidence_now, "body_passage": body,
                "reviewer_labels": "", "reviewer_verdict": "", "reviewer_evidence_quote": "", "reviewer_notes": ""})
            counts["units"] += 1
        # ---- label rows (derived view, not filled by the reviewer)
        scope_ids = f"all {len(su)} units of case {c['case_id']} in review_units.csv"
        for p in pos:
            carriers = [f"{c['doc_id']}|{u['path']}" for u in su if u["path"] in masked and p in u["labels"]]
            ranks = {a: (preds[a]["ranked"].index(p) + 1) for a in ARMS3}
            label_rows.append({"case_id": c["case_id"], "label": p, "polarity": "POSITIVE (hidden)", "tier": "1A",
                               "collateral": "yes" if p in c["collateral_positives"] else "no",
                               "top3_mass_G_F_FS": "/".join(str(round(predict.p_in_top(preds[a], p, 3), 3)) for a in ARMS3),
                               "p_G_F_FS": "/".join(f"{preds[a]['probs'][p]['p']:.3f}" for a in ARMS3),
                               "display_rank_G_F_FS": "/".join(str(ranks[a]) for a in ARMS3),
                               "validated_when": f"masked unit(s) {', '.join(carriers)} carry {p} AND no VISIBLE unit in scope carries {p}",
                               "resolving_units": scope_ids})
        for n in neg:
            tier = "1B" if n in top3_any else "2"
            label_rows.append({"case_id": c["case_id"], "label": n, "polarity": "NEGATIVE (absent)", "tier": tier,
                               "collateral": "",
                               "top3_mass_G_F_FS": "/".join(str(top3[n][a]) for a in ARMS3),
                               "p_G_F_FS": "/".join(f"{preds[a]['probs'][n]['p']:.3f}" for a in ARMS3),
                               "display_rank_G_F_FS": "/".join(str(preds[a]["ranked"].index(n) + 1) for a in ARMS3),
                               "validated_when": f"no unit in scope ({scope_label}) carries {n}",
                               "resolving_units": scope_ids})
        case_blocks.append({"case": c, "rec": rec, "src": src, "preds": preds, "scores": {a: item["arms"][a]["score"] for a in ARMS3},
                            "units": [r for r in units_rows if r["case_id"] == c["case_id"]], "top3_any": top3_any,
                            "top3_high": top3_high, "top3": top3, "brier_only": sorted(set(neg) - set(top3_any))})
    return recs, run, man, units_rows, label_rows, case_blocks, counts


# ----------------------------------------------------------------------------------------------------- markdown
def pred_line(preds, a):
    p = preds[a]
    top = ", ".join(f"{x} {p['probs'][x]['p']:.2f}" for x in p["top_k"])
    t = tie_info(p)
    return f"{a}: {top}" + (f" ({t})" if t else "")


def render(recs, run, man, units_rows, label_rows, blocks, counts, input_hashes) -> str:
    L = []
    w = L.append
    w("# V3 secondary heldout: independent human-adjudication package")
    w("")
    w(f"**Package:** `{PACKAGE_VERSION}`, generated offline by `build_review_package.py` from committed files only "
      "(input SHA-256 in `package_manifest.json`). **Status: `AWAITING_HUMAN_ADJUDICATION`.** "
      "**Every label below is `PROVISIONAL_AGENT_AUTHORED`** (frozen rules `labels-v1-2026-10-13`). "
      "Nothing in this package has been adjudicated, and no agent opinion here counts as validation.")
    w("")
    w("Task prompt: [`ADJUDICATION_TASK_PROMPT.md`](ADJUDICATION_TASK_PROMPT.md). Frozen results are untouched: "
      "`../results/heldout_run.json` (primary, `INCONCLUSIVE`) and `../results/secondary_repaired_run.json` "
      "(post-freeze secondary, `PREDICTIVE_SIGNAL_PROVISIONAL`).")
    w("")
    w("## 0. Evidence status: original passages are BLOCKED in the session that built this package")
    w("")
    w("- **Blocker (exact):** from the Claude Code cloud session on 2026-10-13 (last check 16:30:29Z), every request to "
      "`www.sec.gov`, `www.cloudflare.com` and `www.mongodb.com` failed with `CONNECT tunnel failed, response 403`. "
      "The environment's network policy does not allow these hosts. No raw document from the manifest exists in that container; "
      "the frozen run's raw copies were kept outside the repository, in the earlier session's local scratchpad on the owner's machine.")
    w("- **Consequence:** this package contains **no body passages**. It does not paraphrase or reconstruct any. "
      "The column `body_passage` reads `..._PENDING_LOCAL_RETRIEVAL` wherever the text is needed.")
    w("- **What IS genuine source evidence here:** the verbatim headings and (for credit agreements) the full article → section "
      "table of contents. The frozen extractor took them from files whose SHA-256 matched the manifest at freeze time, and they are "
      "committed in `../data/records_heldout_secondary.json`. SLA unit-text hashes are included so retrieved text can be checked "
      "against exactly what the predictor saw.")
    w("- **To unblock (either):**")
    w("  1. On a machine with internet access, run `python fetch_local_evidence.py --download --user-agent \"<Name> <email>\"` "
      "(SEC requires a declared contact), or `--raw-dir <old corpus_dl>` if the earlier raw copies still exist. It verifies every "
      "SHA-256, rebuilds the structure with the frozen code, checks it is identical to the committed records, and writes passages "
      "to `local_evidence/` (git-ignored; full text is never committed).")
    w("  2. Or allow the three hosts in the cloud environment's network settings and ask Claude Code to run the same script there.")
    w("- **SLA caveat:** both SLA URLs are *current* pages (not archives), retrieved 2026-10-13 ~13:33Z. If a page has changed, "
      "its hash will not match, and the script refuses to treat it as the frozen evidence (`HASH_MISMATCH`). Do not adjudicate "
      "SLA units from a changed page without recording that substitution.")
    w("")
    w("| Doc | Source | Recorded SHA-256 | Needed for |")
    w("|---|---|---|---|")
    for d in ("CA-MARKEL", "CA-OLDDOMINION", "SLA-CLOUDFLARE", "SLA-MONGODB"):
        s = man[d]
        need = ("PROVISION cases (section bodies); SECTION case reviewable from TOC" if d.startswith("CA")
                else "all units (labels were assigned from unit text)")
        extra = f" ({s.get('accession', '')}, filed {s.get('filing_date', '')})" if d.startswith("CA") else " (current page)"
        w(f"| {d} | {s['url']}{extra} | `{s['sha256']}` | {need} |")
    w("")
    w("## 1. What to review, in priority order")
    w("")
    w(f"- **Tier 1A, the {counts['positives']} hidden-positive labels.** Each is validated when the masked unit really carries the "
      "type **and** no visible unit in the same scope carries it. If a visible unit carries it, the target was never hidden, "
      "because the leak guard assumes the labels are right.")
    w(f"- **Tier 1B, the {counts['neg_top3']} negative labels with non-zero tie-aware top-3 mass in at least one arm** "
      f"(G = GLOBAL_FREQ, F = FAMILY, FS = FAMILY_SECTION; EVIDENCED_LAW is identical to FS in every case). "
      f"Of these, **{counts['neg_top3_high']} carry mass ≥ {HIGH_MASS}**. The rest sit in large alphabetical ties "
      "(Markel Art. 7 and Old Dominion Art. 6/5), where each member gets a small share of a top-3 slot. "
      "Each is validated when **no unit in its scope carries the type**.")
    w(f"- **Tier 2, the {counts['neg_brier_only']} further negative labels needed only for Brier and log loss.** Per-case Brier "
      "averages over **every** candidate, so every negative must be confirmed absent, not only those near the top.")
    w(f"- **One pass resolves all three tiers.** Every label in a case refers to the same scope (the article for PROVISION "
      f"cases, the whole document for SECTION cases). So the worksheet `review_units.csv` asks you to label each of the "
      f"**{counts['units']} units** once. The difference between tiers is how thorough that check has to be:")
    w("  - **For Tier 1 (hit@3 and false expectations@3):** confirm the masked units' types, and check every visible unit in "
      "scope for the case's Tier 1 types (listed per case in §4).")
    w("  - **For Tier 2 (Brier):** additionally give each unit its **complete** label set from the frozen vocabulary "
      "(`labels.SECTION_VOCAB` or `labels.PROVISION_VOCAB`; multiple labels allowed).")
    w(f"- **Unit priority in the worksheet:** **P1** is a masked target unit ({sum(r['priority'] == 'P1' for r in units_rows)}). "
      f"**P2** is a visible unit with a mechanical flag: OTHER, multi-match, recorded V3 error or truncated heading "
      f"({sum(r['priority'] == 'P2' for r in units_rows)}). **P3** is a visible unit matched by exactly one rule "
      f"({sum(r['priority'] == 'P3' for r in units_rows)}).")
    w("")
    ca_sec = sum(1 for r in units_rows if r["doc_id"].startswith("CA") and r["task"] == "SECTION")
    ca_prov = sum(1 for r in units_rows if r["doc_id"].startswith("CA") and r["task"] == "PROVISION")
    sla = sum(1 for r in units_rows if r["doc_id"].startswith("SLA"))
    w("**What can be reviewed before retrieval, and what cannot:**")
    w(f"- **Credit-agreement SECTION cases (2 cases, {ca_sec} article units):** reviewable now. The article function is judged "
      "from the verbatim article heading plus its full section list, both committed. Body text is optional.")
    w(f"- **Credit-agreement PROVISION cases (4 cases, {ca_prov} section units):** heading-level review is possible now. OTHER "
      "and multi-match units need the section body (retrieval).")
    w(f"- **SLA cases (2 cases, {sla} units):** **not reviewable until retrieval.** Their labels were assigned from unit text, "
      "and Cloudflare's headings are truncated. Mark them `NOT_REVIEWABLE` rather than guessing from headings.")
    w("")
    w("**Verdict codes (`reviewer_verdict`).**")
    w("- `AGREE`: your complete label set equals `agent_labels`.")
    w("- `DISAGREE`: write your labels in `reviewer_labels`.")
    w("- `UNSURE`: say why. Both bounds will be reported.")
    w("- `NOT_REVIEWABLE`: the evidence is unavailable or the hash does not match.")
    w("- Put a short verbatim quote of the decisive text in `reviewer_evidence_quote`.")
    w("")
    w("**Reviewer independence (record at the top of the filled sheet).**")
    w("- Name and role.")
    w("- That you did not write the label rules.")
    w("- Whether you read §3's predictions before labelling (ideally not: label first, using §2 and the worksheet).")
    w("- Time spent.")
    w("- Evidence source: hash-verified local copy, or live page (with the date).")
    w("")
    w("An agent re-reading these labels would **not** count as independent adjudication.")
    w("")
    w("## 2. Known problems the reviewer must keep in view (from V3 RESULTS.md, PROTOCOL.md and the post-run audit)")
    w("")
    w("**Segmentation**")
    w("- **CA-MOTOROLA:** the exhibit is a *First Amendment* with a redlined conformed copy. The pre-split amendment screen "
      "only read the first 400 characters. It failed segmentation in the frozen primary and is **excluded** from these 8 cases.")
    w("- **CA-OLDDOMINION:** " + DOC_FLAGS["CA-OLDDOMINION"])
    w("- **SLA-CLOUDFLARE:** " + DOC_FLAGS["SLA-CLOUDFLARE"] + " In the frozen primary it was unscorable (`SLA_TITLE_NOT_FOUND`).")
    w("- **Credit agreements are labelled from table-of-contents headings only.** A heading can understate a section's "
      "content, and body text was never read by the labeller.")
    w("")
    w("**Sparse support misread as conflict**")
    w("- **CA-MARKEL:Article 7** (consistency 0.38) and **CA-OLDDOMINION:Article 6** (consistency 0.33): " + BACKOFF_NOTE)
    w("- Post-hoc diagnostic only (`../results/posthoc_no_conflict_backoff.json`): with the backoff disabled, provision hit@3 "
      "would have been 5.0/8 instead of 3.09/8.")
    w("- **Adjudication validates labels; it cannot repair the predictor.** A prospective fix belongs in a new frozen protocol.")
    w("")
    w("**Misclassification risks (mechanical flags, not verdicts)**")
    w("- **First-match-wins on multi-topic headings.** For example, Markel 7.08 'Compliance with Laws and Approvals' becomes "
      "AUTHORIZATION_ENFORCEABILITY, not COMPLIANCE_WITH_LAWS. Markel 7.01 'GAAP Financial Statements' becomes ACCOUNTING_TERMS, not "
      "FINANCIAL_REPORTING. Old Dominion 6.09 'Sanctions; Anti-Corruption; Use of Proceeds' becomes SANCTIONS_AML, though "
      "USE_OF_PROCEEDS also matches. These are **visible** units, so they change the prediction context, not only the score.")
    w("- **Substring artifacts.** For example, Markel 12.06 'Stay of Acceleration' becomes FINANCIAL_RATIO_COVENANT via "
      "'accele**ratio**n', and 9.02 'Remedies' becomes GUARANTEE_TERMS. Both are outside the 8 scored scopes, but they show the "
      "rules cannot be trusted without review.")
    w("- **Thin keyword support for positives.** The Markel Art. 1 positive INTERPRETATION rests on '1.10 Divisions' (keyword "
      "'divisions'), while visible siblings '1.02 Other Definitions and Provisions' and '1.05 References to Agreement and Laws' "
      "are OTHER. Whether INTERPRETATION was really hidden depends on those OTHER units.")
    w("- **Recorded Cloudflare label errors.** These are V3's own audit, quoted in the unit flags: Unit 2 is a probable "
      "SERVICE_COMMITMENT and Unit 7 a probable CREDIT_CALCULATION_APPLICATION.")
    w("- **A plausible wrong section label goes undetected.** In the negative control (Affirmative Covenants relabelled as "
      "Representations), predictions silently shifted. Labels for section function are therefore inputs that matter.")
    w("- **Training labels (8 documents) are out of scope here** but also agent-authored. Example: the Best Buy rule-order "
      "artifact where 'Use of Proceeds; Federal Reserve Regulations' becomes MARGIN_REGULATIONS. This remains a limitation "
      "after this adjudication.")
    w("")
    w("**Post-run audit findings (agent-authored, not adjudication)**")
    w("- **The split was hash-based, not chronological.** CA-MARKEL (filed 2023-06-23) and CA-OLDDOMINION (2023-12-13) were "
      "scored using CA-LINCOLN (2023-12-21) as training.")
    w("- **Training support is thinner than it looks.** Equitable and Lincoln are near-identical templates, so the four "
      "training credit agreements amount to about 3 drafting styles.")
    w("- **The provisional signal comes from two conventional cases.** FAMILY_SECTION's provision hit@3 of 3.09/8 comes from "
      "Markel Art. 1 (2.0) and Old Dominion Art. 5 (1.0). Section-level adds nothing over FAMILY, and Brier is worse than "
      "GLOBAL (0.256 vs 0.183).")
    w("- **Reproducibility.** Both frozen result files re-score exactly from the committed records, and all 9 freeze-receipt "
      "files are unchanged.")
    w("")
    # ---------------- compact case table
    w("## 3. Compact review table (one row per case)")
    w("")
    w("Predicted structures show each arm's top-3 with smoothed frequency p. FS flags and fallback come from the frozen run. "
      "Agent labels and predictions are **not** validated.")
    w("")
    w("| Case | Contract, section and source reference | Original contractual passage (what exists now) | Proposed section/provision classification (hidden positives ← masked unit) | Relevant predicted provision structures (top-3 per arm) | Supporting evidence and disputed classifications | What the human reviewer needs to validate |")
    w("|---|---|---|---|---|---|---|")
    for b in blocks:
        c, rec, src, preds = b["case"], b["rec"], b["src"], b["preds"]
        masked_units = [r for r in b["units"] if r["role"] == "MASKED_TARGET"]
        if c["task"] == "PROVISION":
            where = f"{c['doc_id']} {c['section_path']} '{c['section_heading']}' ({c['section_function']}); {src['url']}"
        else:
            where = f"{c['doc_id']}, whole document; {src['url']}"
        avail = "; ".join(f"{u['path']} '{u['verbatim_heading']}'" for u in masked_units)
        avail += " — body: BLOCKED (see §0)" if not (c["task"] == "SECTION" and c["doc_id"].startswith("CA")) else " — TOC headings + section lists (body optional)"
        prop = "; ".join(f"{', '.join(l for l in u['agent_labels'].split('+') if l in c['positives'])} ← {u['path']}" for u in masked_units)
        if c["collateral_positives"]:
            prop += f" (collateral: {', '.join(c['collateral_positives'])})"
        predtxt = "<br>".join(md(pred_line(preds, a)) for a in ARMS3)
        sc = b["scores"]
        predtxt += "<br>hit@3 G/F/FS: " + "/".join(str(sc[a]["hit3"]) for a in ARMS3)
        if preds["FAMILY_SECTION"]["flags"]:
            predtxt += "<br>FS flags: " + ", ".join(preds["FAMILY_SECTION"]["flags"])
        ev = "; ".join(f"{u['path']}: {u['assigned_by']}" for u in masked_units)
        disputes = [f"{u['path']} '{u['verbatim_heading'][:45]}' [{u['agent_labels']}: {codes(u['flags'])}]" for u in b["units"]
                    if u["role"] == "VISIBLE_CONTEXT" and u["priority"] == "P2"]
        mflags = [codes(u["flags"]) for u in masked_units if codes(u["flags"]) != "—"]
        dtxt = (f"{len(disputes)} flagged visible unit(s): " + "; ".join(disputes) if disputes else "no flagged visible units")
        if mflags:
            dtxt += f". Masked-unit flags: {'; '.join(mflags)}"
        must = (f"(1) {len(masked_units)} masked unit(s) carry {', '.join(c['positives'])}; "
                f"(2) none of the {len(b['units']) - len(masked_units)} visible units carries them; "
                f"(3) no unit in scope carries the {len(b['top3_any'])} Tier-1B types ({len(b['top3_high'])} with mass ≥ {HIGH_MASS}: "
                f"{', '.join(b['top3_high']) or '—'}); (4) for Brier, full labels for all {len(b['units'])} units "
                f"({len(b['brier_only'])} Tier-2 types)")
        w(f"| **{c['case_id']}** | {md(where)} | {md(avail)} | {md(prop)} | {predtxt} | {md(ev)}<br>**Disputed:** {md(dtxt)} | {md(must)} |")
    w("")
    # ---------------- per case unit detail
    w("## 4. Per-case scope: every unit the reviewer labels")
    w("")
    w("Units are in source order. **Bold** marks masked target units. The unit labels below are exactly what the predictor "
      "used; fill your answers in `review_units.csv`, keyed by `unit_id`.")
    w("")
    for b in blocks:
        c = b["case"]
        w(f"### {c['case_id']} ({c['task']}; law given to the predictor: {c['law']})")
        w("")
        if c["task"] == "PROVISION":
            w(f"Scope: **{c['section_path']} '{c['section_heading']}'** → section function `{c['section_function']}` "
              f"(itself an agent label; validate it in the SECTION case of {c['doc_id']}).")
        else:
            w(f"Scope: **all top-level units of {c['doc_id']}**. {DOC_FLAGS.get(c['doc_id'], '')}")
        if c["case_id"] in ("CA-MARKEL:Article 7", "CA-OLDDOMINION:Article 6"):
            w("")
            w(f"> **Sparse-support backoff case.** {BACKOFF_NOTE}")
        w("")
        w("| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |")
        w("|---|---|---|---|---|---|")
        for u in b["units"]:
            nm = f"**{u['path']}**" if u["role"] == "MASKED_TARGET" else u["path"]
            head = md(u["verbatim_heading"])
            if c["task"] == "SECTION" and c["doc_id"].startswith("CA"):
                kids = next(s for s in b["rec"]["sections"] if s["path"] == u["path"])["subunits"]
                joined = " · ".join(f"{k['path'].split()[-1]} {k['heading']}" for k in kids)
                head += f" <br><sub>{len(kids)} sections: " + md(joined[:420]) + ("…" if len(joined) > 420 else "") + "</sub>"
            w(f"| {u['priority']} | {nm} | {head} | {u['agent_labels']} | {md(u['assigned_by'])} | {md(u['flags']) or '—'} |")
        w("")
        w(f"- **Tier 1A ({len(c['positives'])}):** {', '.join(c['positives'])}" + (f" (collateral: {', '.join(c['collateral_positives'])})" if c["collateral_positives"] else ""))
        hi = [f"{n} [{'/'.join(f'{SHORT[a]} {b['top3'][n][a]}' for a in ARMS3 if b['top3'][n][a] > 0)}]" for n in b["top3_high"]]
        lo = [n for n in b["top3_any"] if n not in b["top3_high"]]
        w(f"- **Tier 1B ({len(b['top3_any'])}):** mass ≥ {HIGH_MASS}: {', '.join(hi) or '—'}. Tie-share only (< {HIGH_MASS}): "
          f"{len(lo)} types — {', '.join(lo) or '—'}.")
        w(f"- **Tier 2, Brier only ({len(b['brier_only'])}):** {', '.join(b['brier_only']) or '—'}.")
        w("")
    # ---------------- application rule
    w("## 5. Pre-registered rule for applying the adjudication (fixed before any human verdict)")
    w("")
    w("1. **What the reviewer produces.** One complete label set per unit in `review_units.csv`, using the frozen vocabulary "
      "(plus OTHER and RESERVED). The frozen files under `../data`, `../results` and `../frozen` are never edited.")
    w("2. **Derived sets per case.**")
    w("   - **Positives:** types carried by a masked unit and by **no** visible unit in scope.")
    w("   - **Negatives:** vocabulary types carried by **no** unit in scope.")
    w("   - **Removed from candidates:** a type carried by a visible unit.")
    w("   - **No positives left:** the case is reported as `TARGET_LEAKED_OR_EMPTY` and dropped from the re-score. It is not repaired.")
    w("3. **Re-score A (labels only).** Keep the frozen predictions. Drop removed candidates from each ranked list without "
      "renormalising. Apply the frozen `predict.score_case`, `summarize` and `decide`. Output to "
      "`results/adjudicated_secondary_rescore_A.json`, labelled `POST_HOC_HUMAN_ADJUDICATED_SECONDARY`.")
    w("4. **Re-score B (context corrected).** Required only if any **visible** label changes. Rebuild the case context from the "
      "human labels and re-run the frozen `predict.predict` (training labels unchanged). Output to "
      "`results/adjudicated_secondary_rescore_B.json`. If a section function changes, the provision case is re-run under the "
      "human section function.")
    w("5. **`UNSURE` units.** Report lower and upper bounds (UNSURE resolved against and for each arm). Do not choose a single value.")
    w("6. **What stays fixed.**")
    w("   - The pre-registered primary stays `INCONCLUSIVE`.")
    w("   - The re-score is still a **post-freeze secondary on agent-chosen documents**.")
    w("   - It **cannot** satisfy the gate to a Jev test, which requires ≥ 6 fresh, human-adjudicated documents.")
    w("   - Training labels remain agent-authored.")
    w("   - No rule, vocabulary or predictor change is made on the basis of these verdicts within V3.")
    w("")
    w("## 6. Label glossary: the frozen operational definitions")
    w("")
    w("The vocabulary has **no prose definitions**; each label is defined only by the frozen rule below (`../labels.py`, "
      "first match wins for credit agreements, multi-label for SLAs). Judge each unit by **meaning**, using the rule as a "
      "pointer to the intended category. Where the intended category is unclear, use `UNSURE` and say so: an unclear "
      "category is itself a finding about the vocabulary.")
    w("")
    w("Structural notes:")
    w("- `COVENANTS_COMBINED` catches any 'covenant' heading not already caught by AFFIRMATIVE_/NEGATIVE_/FINANCIAL_COVENANTS. "
      "It is a top-3 false expectation for F and FS in both credit-agreement SECTION cases, so decide whether a "
      "combined-covenants article exists.")
    w("- `CREDIT_SCHEDULE` is computed: at least 2 band boundaries such as 'less than 99.9%'.")
    w("- `OTHER` and `RESERVED` are never targets or candidates.")
    w("")
    w("| Task | Label | Frozen rule pattern (lower-cased heading; SLA: heading + text) |")
    w("|---|---|---|")
    for name, pat in labels.CA_SECTION_RULES:
        if name != "RESERVED":
            w(f"| SECTION (credit agreement) | `{name}` | `{md(pat)}` |")
    for name, pat in labels.SLA_SECTION_RULES:
        w(f"| SECTION (SLA) | `{name}` | `{md(pat) if pat else 'computed: >= 2 band boundaries (less than / below / < / - NN.N%)'}` |")
    for name, pat in labels.CA_PROVISION_RULES:
        if name != "RESERVED":
            w(f"| PROVISION (credit agreement) | `{name}` | `{md(pat)}` |")
    w("")
    w("## 7. Files")
    w("")
    w("| File | Role |")
    w("|---|---|")
    w(f"| `review_units.csv` | **Worksheet to fill** ({counts['units']} units, P1→P3; reviewer columns empty) |")
    w(f"| `review_labels.csv` | Derived label view: {counts['positives']} positives + {counts['negatives']} negatives with tier, "
      "top-3 mass, p and the units that resolve each label (do not fill) |")
    w("| `fetch_local_evidence.py` | Operator-run retrieval: SHA-256 check, rebuild with frozen code, identity check against committed records, passages into git-ignored `local_evidence/` |")
    w("| `build_review_package.py` | Regenerates this package offline and deterministically |")
    w("| `package_manifest.json` | Input hashes and counts |")
    w("| `test_adjudication.py` | Offline tests: frozen files untouched, counts, determinism, retrieval plumbing (synthetic) |")
    w("| `ADJUDICATION_TASK_PROMPT.md` | The task as given, constraints, charter anchor |")
    w("")
    return "\n".join(L) + "\n"


def main() -> None:
    recs, run, man, units_rows, label_rows, blocks, counts = build()
    order = {"P1": 0, "P2": 1, "P3": 2}
    units_sorted = sorted(units_rows, key=lambda r: (order[r["priority"]], r["case_id"], r["unit_id"]))
    with (HERE / "review_units.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(units_sorted[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(units_sorted)
    with (HERE / "review_labels.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(label_rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(sorted(label_rows, key=lambda r: (r["tier"], r["case_id"], r["label"])))
    input_hashes = {p: sha256_file(V3 / p) for p in INPUTS}
    (HERE / "REVIEW_PACKAGE.md").write_text(render(recs, run, man, units_rows, label_rows, blocks, counts, input_hashes), encoding="utf-8")
    manifest = {"package_version": PACKAGE_VERSION, "status": "AWAITING_HUMAN_ADJUDICATION",
                "label_status": "PROVISIONAL_AGENT_AUTHORED", "frozen_results_modified": False,
                "source_retrieval": {"status": "BLOCKED_IN_BUILD_SESSION",
                                     "detail": "CONNECT tunnel failed, response 403 for www.sec.gov, www.cloudflare.com, www.mongodb.com (environment network policy), last checked 2026-10-13T16:30:29Z"},
                "counts": counts, "inputs_sha256": input_hashes,
                "outputs_sha256": {p: sha256_file(HERE / p) for p in ("REVIEW_PACKAGE.md", "review_units.csv", "review_labels.csv")}}
    (HERE / "package_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
