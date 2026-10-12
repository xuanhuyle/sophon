"""Run the 54 frozen scenarios through the validator and check them against their frozen expectations.

    python3 src/run_scenarios.py --out evidence/validation_results.json     (any Python >= 3.10 with pydantic 2)

Reads only committed files: cases/, evidence/catalog.json and evidence/receipts/. record_patch and receipt_tamper
are test-harness edits applied to in-memory copies (PROTOCOL.md §5); they are not IR features.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E3 = HERE.parent
sys.path.insert(0, str(HERE))
import validator as val  # noqa: E402


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def load_dir(d: Path) -> dict:
    return {p.stem: load(p) for p in sorted(d.glob("*.json"))}


def context() -> val.Context:
    ev = E3 / "evidence"
    return val.Context(root=E3, roster=load(E3 / "cases" / "roster.json"), registry=load(E3 / "cases" / "fact_registry.json"),
                       catalog=load(ev / "catalog.json"), native=load_dir(ev / "receipts" / "native"),
                       guards=load_dir(ev / "receipts" / "guards"), oracle=load_dir(ev / "receipts" / "oracle"))


def apply_patch(doc: dict, ops: list[dict]) -> dict:
    doc = copy.deepcopy(doc)
    for op in ops:
        *parents, last = op["path"]
        node = doc
        for k in parents:
            node = node[k] if isinstance(node, list) else node[k] if k in node else node.setdefault(k, {})
            if isinstance(node, dict) and k in ("readings",):
                pass
        # list paths address reading/atom positions by index
        if op["op"] == "set":
            node[last] = copy.deepcopy(op["value"])
        elif op["op"] == "delete":
            del node[last]
        else:
            raise ValueError(op)
    return doc


def tamper(native: dict, spec: dict | None) -> dict:
    if not spec:
        return native
    native = copy.deepcopy(native)
    rc = native[spec["receipt_id"]]
    metric = rc["query"]["metric"]
    rc["rows"][0][metric] = str(Decimal(rc["rows"][0][metric]) + Decimal("0.01"))
    if spec["mode"] == "ADD_ONE_CENT_FIRST_ROW_REHASH":
        rc["rows_sha256"] = val.sha_text(val.canon(rc["rows"]))
    elif spec["mode"] != "ADD_ONE_CENT_FIRST_ROW":
        raise ValueError(spec)
    return native


def check(exp: dict, res: dict) -> list[str]:
    f = []
    if res["status"] != exp["status"]:
        f.append(f"status {res['status']} != {exp['status']}")
    miss = [r for r in exp.get("reasons_include", []) if r not in res["reasons"]]
    if miss:
        f.append(f"missing reasons {miss}")
    if "selected_reading" in exp and res["meaning"].get("selected_reading") != exp["selected_reading"]:
        f.append(f"selected {res['meaning'].get('selected_reading')} != {exp['selected_reading']}")
    for rid, disp in exp.get("alternatives", {}).items():
        if res["meaning"].get("alternatives", {}).get(rid) != disp:
            f.append(f"alternative {rid} != {disp}")
    if "uncovered" in exp and res["uncovered"] != exp["uncovered"]:
        f.append(f"uncovered {res['uncovered']} != {exp['uncovered']}")
    if "technically_executable" in exp and res["technically_executable"] != exp["technically_executable"]:
        f.append("technically_executable differs")
    for rid, v in exp.get("readings_native_equals_oracle", {}).items():
        if res.get("evidence", {}).get(rid, {}).get("native_equals_oracle") != v:
            f.append(f"native_equals_oracle[{rid}] != {v}")
    blob = json.dumps(res)
    for token in exp.get("must_not_mention", []):
        if token in blob:
            f.append(f"output mentions {token}")
    return f


def run(ctx: val.Context) -> list[dict]:
    sc = load(E3 / "cases" / "SCENARIOS.json")["scenarios"]
    approvals = load_dir(E3 / "cases" / "approvals")
    out = []
    for s in sc:
        rec = apply_patch(load(E3 / "cases" / "records" / f"{s['record']}.json"), s["record_patch"])
        c = val.Context(**{**ctx.__dict__, "native": tamper(ctx.native, s["receipt_tamper"])})
        res = val.validate(rec, [approvals[a] for a in s["approvals"]], [approvals[r] for r in s["revocations"]], c,
                           s["eval_known_at"], s["eval_effective_at"])
        fails = check(s["expected"], res)
        out.append({"scenario_id": s["scenario_id"], "test": s["test"], "expected_status": s["expected"]["status"],
                    "status": res["status"], "passed": not fails, "check_failures": fails, "result": res})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run(context())
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    bad = [r for r in res if not r["passed"]]
    print(f"{len(res) - len(bad)}/{len(res)} scenarios as frozen")
    for r in bad:
        print(" FAIL", r["scenario_id"], r["check_failures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
