#!/usr/bin/env python3
"""Fresh-process replay of recorded E1 evidence (PROTOCOL.md test 9). Runs no mf and opens no database.

    python src/replay.py --evidence evidence/run --out evidence/replay.json [--raw .upstream/data/raw]

For every recorded case and live-evaluated variant it rebuilds a SnapshotContext from the recorded transcript,
re-runs the frozen decision procedure (src/evaluator.py) and compares case status, verified flag and every
predicate status with what was recorded. Trust model: the recorded native responses, warehouse column list,
semantic manifest and oracle outputs are trusted as captured (their content is hashed in the output); the replay
checks that the statuses follow from that evidence by the frozen procedure, not that the evidence is true. With
--raw, the oracle responses are also recomputed from the raw CSVs and compared.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluator as ev  # noqa: E402
import oracle as oracle_mod  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw")
    a = ap.parse_args()
    ed = Path(a.evidence)
    frozen = json.loads((HERE.parent / "FROZEN_CASES.json").read_text(encoding="utf-8"))
    scored = json.loads((ed / "case_results.json").read_text(encoding="utf-8"))["scored"]
    adv = json.loads((ed / "adversarial_results.json").read_text(encoding="utf-8"))["adversarial"]
    items = [(f"scored:{k}", frozen["cases"][k], v, None) for k, v in scored.items()]
    items += [(f"adversarial:{k}", ev.apply_variant(frozen, frozen["adversarial"][k]), v,
               frozen["adversarial"][k].get("frozen_fingerprint_override")) for k, v in adv.items() if "transcript" in v]
    report = {"pid": os.getpid(), "items": {}, "oracle_recomputed": {}}
    ok = True
    for name, case, rec, fp in items:
        r = ev.evaluate_case(case, frozen, ev.SnapshotContext(rec["transcript"]), fp)
        same = (r["case_status"] == rec["result"]["case_status"]
                and r["verified_for_recorded_checks"] == rec["result"]["verified_for_recorded_checks"]
                and {k: v["status"] for k, v in r["predicates"].items()} == {k: v["status"] for k, v in rec["result"]["predicates"].items()})
        ok &= same
        report["items"][name] = {"replayed_case_status": r["case_status"], "recorded_case_status": rec["result"]["case_status"],
                                 "equal": same, "transcript_sha256": ev.sha(rec["transcript"])}
        if a.raw:
            for key, val in rec["transcript"].items():
                if key.startswith("oracle:"):
                    again = oracle_mod.expected(a.raw, json.loads(key[len("oracle:"):]))
                    eq = again == val
                    ok &= eq
                    report["oracle_recomputed"][f"{name}:{key}"] = eq
    report["all_equal"] = ok
    report["trust_limits"] = ("Recorded native receipts, warehouse columns, distinct values, semantic manifest and estate "
                              "fingerprint are trusted as captured; replay re-derives statuses from them with the frozen "
                              "procedure and does not re-execute MetricFlow. Oracle outputs are recomputed from raw CSVs "
                              "only when --raw is given.")
    Path(a.out).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"all_equal": ok, "items": {k: v["replayed_case_status"] for k, v in report["items"].items()},
                      "oracle_recomputed_all_equal": all(report["oracle_recomputed"].values()) if report["oracle_recomputed"] else None}, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
