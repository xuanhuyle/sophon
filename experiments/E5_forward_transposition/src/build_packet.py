"""Build TRANSPOSE_PACKET.json (run once before the freeze). It is the ONLY input the transposer receives.

It contains: the two approved requirement versions (IR), the governing source texts, the approvals, the authorized
role, the fixed native binding, the native baseline (_metrics.yml text of the combined E4 M6B + M2 stack, its
semantic-manifest sha256 and catalog) and the patch constraints. It contains no oracle result, reference value,
expected outcome or scoring data. The baseline is rebuilt here with E4's unmodified candidate_stack.

    .upstream/.venv/bin/python src/build_packet.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
REPO = EXP.parent
E4 = EXP / "E4_independent_verification"
sys.path.insert(0, str(E4 / "src"))
import candidate_stack as cs  # noqa: E402  (E4, unmodified)

MET = "dbt/retail_dwh/models/marts/semantic/_metrics.yml"
FORBIDDEN_KEYS = ("reference_results", "expected", "by_year", "lines_sha256", "oracle")


def j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def catalog(manifest: dict) -> dict:
    dims = []
    for sm in manifest["semantic_models"]:
        prim = next((e["name"] for e in sm.get("entities", []) if e.get("type") == "primary"), None)
        for d in sm.get("dimensions", []):
            if prim:
                dims.append(f"{prim}__{d['name']}")
    return {"metrics": sorted(m["name"] for m in manifest["metrics"]), "dimensions": sorted(dims)}


def main() -> int:
    up = (E5 / ".upstream").resolve()
    base = j(E5 / "candidates" / "BASELINE.json")
    st = cs.build("BASELINE__PACKET", base["patch"], up / "data" / "raw", up, E5 / "runs" / "packet_build")
    if not st["ok"]:
        raise SystemExit(f"baseline build failed: {st.get('error')}")
    root = Path(st["upstream"])
    met_text = (root / MET).read_text(encoding="utf-8")
    manifest = j(root / "dbt" / "retail_dwh" / "target" / "semantic_manifest.json")
    v1, v2 = j(E5 / "ir" / "P1_v1.json"), j(E5 / "ir" / "P1_v2.json")
    docs = {}
    for v in (v1, v2):
        t = (REPO / v["governing_source"]["path"]).read_text(encoding="utf-8")
        docs[v["governing_source"]["document_id"]] = {"path": v["governing_source"]["path"], "text": t,
                                                      "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()}
    roster = j(EXP / "E3_formal_ir" / "cases" / "roster.json")
    packet = {
        "packet_id": "E5_TRANSPOSE_PACKET_1",
        "label": "ENGINEERED HOLD-OUT PACKET. Authored by the researcher who also set the E5 reference; it is not an "
                 "independently authored unseen contract. It contains no oracle result, reference value, expected outcome or scoring data.",
        "task": {"policy": "P1", "series": "LAB-REV-POLICY/S1", "from_version": "P1_v1", "to_version": "P1_v2"},
        "requirement_versions": {"P1_v1": v1, "P1_v2": v2},
        "source_documents": docs,
        "approvals": {"AP_S1_READ": j(EXP / "E3_formal_ir" / "cases" / "approvals" / "AP_S1_READ.json"),
                      "AP_S1_V2": j(E5 / "approvals" / "AP_S1_V2.json")},
        "authorized_roles": {"LAB_REVENUE_POLICY_OWNER": roster["roles"]["LAB_REVENUE_POLICY_OWNER"], "never_approvers": roster["never_approvers"]},
        "binding": j(E5 / "ir" / "NATIVE_BINDING.json"),
        "native_baseline": {"revision_id": base["revision_id"], "provenance": base["provenance"],
                            "upstream_commit": "312e97ad192dcef02f688e31edc0a08c6cf4345f",
                            "files": {MET: met_text}, "file_sha256": {MET: cs.sha_text(met_text)},
                            "semantic_manifest_sha256": st["semantic_manifest_sha256"], "catalog": catalog(manifest)},
        "patch_constraints": {"editable_files": [MET], "edit_mode": "IN_PLACE_EXISTING_METRIC", "anchor_must_be_unique": True,
                              "no_new_metrics": True, "no_removed_metrics": True,
                              "forbidden": ["dbt models (SQL)", "semantic models", "raw data", "metrics other than the impacted one"]},
    }
    txt = json.dumps(packet, indent=1, ensure_ascii=False)
    for k in FORBIDDEN_KEYS:
        if f'"{k}"' in txt:
            raise SystemExit(f"forbidden key {k} in packet")
    (E5 / "TRANSPOSE_PACKET.json").write_text(txt + "\n", encoding="utf-8")
    print(json.dumps({"baseline_semantic_manifest_sha256": st["semantic_manifest_sha256"], "catalog": catalog(manifest)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
