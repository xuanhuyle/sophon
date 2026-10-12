"""Write REFERENCE.json and fixtures/reference_lines/ from the independent oracle (run once before the freeze).

    python3 src/build_reference.py --snapshots runs/snapshots
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
sys.path.insert(0, str(HERE))
import oracle  # noqa: E402
import snapshots  # noqa: E402

AMD = "2025-01-01"
KEYS = {  # key -> (policy, date_from, date_to)
    "P1v1|ALL": ("P1v1", None, None), "P1v2|ALL": ("P1v2", None, None),
    "P1v1|<2025-01-01": ("P1v1", None, AMD), "P1v2|>=2025-01-01": ("P1v2", AMD, None),
    "P1v1|>=2025-01-01": ("P1v1", AMD, None), "P2|ALL": ("P2", None, None)}
ROUTES = {"ROUTED@K_POST": [("P1v1", None, AMD), ("P1v2", AMD, None)], "ROUTED@K_PRE": [("P1v1", None, None)]}


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def sha(o) -> str:
    return hashlib.sha256(canon(o).encode()).hexdigest()


def discriminators(lines: dict) -> dict:
    amd = {k: f for k, f in lines.items() if f["order_date"] >= AMD}
    def ids(pred):
        return sorted((k for k, f in amd.items() if pred(f)), key=int)
    p = lambda f: Decimal(f["unit_price"])  # noqa: E731
    return {"v1_vs_v2_completed_100_to_lt120_from_2025": ids(lambda f: f["status"] == "completed" and 100 <= p(f) < 120),
            "ge119_vs_ge120_completed_119_to_lt120_from_2025": ids(lambda f: f["status"] == "completed" and 119 <= p(f) < 120),
            "gt120_vs_ge120_completed_exactly_120_from_2025": ids(lambda f: f["status"] == "completed" and p(f) == 120),
            "noncancelled_vs_completed_returned_ge120_from_2025": ids(lambda f: f["status"] == "returned" and p(f) >= 120),
            "history_2024_completed_100_to_lt120": sorted((k for k, f in lines.items() if f["order_date"] < AMD and f["status"] == "completed"
                                                           and 100 <= p(f) < 120), key=int)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshots", required=True)
    snaps = Path(ap.parse_args().snapshots)
    reg = snapshots.build(E5 / ".upstream" / "data" / "raw", snaps)
    out_dir = E5 / "fixtures" / "reference_lines"
    out_dir.mkdir(parents=True, exist_ok=True)
    results, disc = {}, {}
    for snap in ("PINNED", "BOUNDARY120"):
        lines = oracle.order_lines(snaps / snap)
        for key, (pol, a, b) in KEYS.items():
            r = oracle.evaluate(snaps / snap, pol, a, b, lines)
            results[f"{key}@{snap}"] = {"policy": pol, "window": [a, b], "by_year": r["by_year"], "line_count": r["line_count"], "lines_sha256": sha(r["lines"])}
            (out_dir / f"{key.replace('|', '_').replace('<', 'lt').replace('>=', 'ge')}@{snap}.json").write_text(canon(r["lines"]) + "\n")
        for key, segs in ROUTES.items():
            r = oracle.routed(snaps / snap, segs)
            results[f"{key}@{snap}"] = {"segments": [list(s) for s in segs], "by_year": r["by_year"], "line_count": r["line_count"], "lines_sha256": sha(r["lines"])}
        d = discriminators(lines)
        disc[snap] = {k: {"count": len(v), "first_ids": v[:12],
                          "facts": [{x: lines[i][x] for x in ("order_item_id", "order_date", "status", "quantity", "unit_price")} for i in v[:3]]}
                      for k, v in d.items()}
    e4 = json.loads((EXP / "E4_independent_verification" / "REFERENCE.json").read_text())["reference_results"]
    cross = {"P1v1|ALL@PINNED == E4 P1@PINNED": results["P1v1|ALL@PINNED"]["by_year"] == e4["P1@PINNED"]["by_year"]
             and results["P1v1|ALL@PINNED"]["lines_sha256"] == e4["P1@PINNED"]["lines_sha256"],
             "P2|ALL@PINNED == E4 P2@PINNED": results["P2|ALL@PINNED"]["by_year"] == e4["P2@PINNED"]["by_year"]
             and results["P2|ALL@PINNED"]["lines_sha256"] == e4["P2@PINNED"]["lines_sha256"]}
    packet = json.loads((E5 / "TRANSPOSE_PACKET.json").read_text())
    ref = {"label": "E5 frozen reference (LAB). Oracle = src/oracle.py over raw CSVs. Hidden from the transposer.",
           "registered_snapshots": {k: {"csv_sha256": v["csv_sha256"], "edits": v["edits"]} for k, v in reg.items()},
           "versions": {"P1v1": {"version_id": "P1_v1", "threshold": "100", "effective_from": "2024-01-01"},
                        "P1v2": {"version_id": "P1_v2", "threshold": "120", "effective_from": AMD, "supersedes_P1v1_from": AMD},
                        "P2": {"record": "E3 S2", "reading": "R_CUSTOMER_COUNTRY"}},
           "reference_results": results, "discriminating_rows": disc, "cross_check_with_e4_frozen_reference": cross,
           "pristine_semantic_manifest_sha256": "e8e9bfc7e1188bc3eb3f5ac551e8ed5350817af14a5471bdbcdfdca2bc01bd48",
           "baseline_semantic_manifest_sha256": packet["native_baseline"]["semantic_manifest_sha256"],
           "transpose_packet_sha256": hashlib.sha256((E5 / "TRANSPOSE_PACKET.json").read_bytes()).hexdigest(),
           "oracle_code_sha256": hashlib.sha256((HERE / "oracle.py").read_bytes()).hexdigest()}
    (E5 / "REFERENCE.json").write_text(json.dumps(ref, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"cross": cross, "disc": {s: {k: v["count"] for k, v in d.items()} for s, d in disc.items()},
                      "b120": disc["BOUNDARY120"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
