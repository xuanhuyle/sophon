"""E1 known-binding and observability evaluator (decision procedure frozen in PROTOCOL.md section 3).

Plain Python over plain JSON. The evaluator receives a case (required predicate id -> binding or None) and a context.
It never reads EXPECTED.json, never branches on a case id, and returns FULLY_OBSERVABLE_FOR_THIS_CALCULATION only
when every required predicate is bound to an existing, designated, natively exposed object, the target metric's
own definition is consistent with those bindings, and the native MetricFlow result equals the independent oracle.

Contexts:
  LiveContext      native MetricFlow through the E0 adapter (imported unmodified), DuckDB read-only, oracle on raw CSVs.
                   Every response is recorded in a transcript.
  SnapshotContext  replays a recorded transcript (no mf, no DuckDB) for the fresh-process replay.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E0_SRC = HERE.parents[1] / "E0_native_adapter" / "src"
sys.path.insert(0, str(E0_SRC))
sys.path.insert(0, str(HERE))
import mf_adapter as mfa  # noqa: E402  (E0 adapter, unmodified)
import oracle as oracle_mod  # noqa: E402

CENT = Decimal("0.01")


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


# --------------------------------------------------------------------------------------------- native query with --where
def native_query_with_where(p: mfa.Project, metric: str, group_by: list[str], where: list[str]) -> dict:
    """The E0 adapter's query() has no --where option. This mirrors it with the adapter's own pieces (identity check
    before running, _run, fingerprints) and adds --where. No metric arithmetic; rows come from the CSV mf wrote."""
    identity = mfa.mf_identity(p)
    before = mfa.fingerprints(p)
    args = ["query", "--metrics", metric]
    if group_by:
        args += ["--group-by", ",".join(group_by)]
    if where:
        args += ["--where", " AND ".join(where)]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "result.csv"
        r = mfa._run(p, [*args, "--csv", str(out)])  # noqa: SLF001
        csv_text = out.read_text(encoding="utf-8") if out.exists() else None
    r["argv"] = [*r["argv"][: len(args) + 1], "--csv", "<csv>"]
    r["csv_written"] = csv_text is not None
    r["csv_sha256"] = mfa.sha256_text(csv_text) if csv_text is not None else None
    r["fingerprints_before"], r["fingerprints_after"], r["mf_identity"] = before, mfa.fingerprints(p), identity
    for k in ("stdout", "stderr"):
        if len(r.get(k) or "") > 3000:
            r[k] = r[k][:1500] + "\n...[truncated; sha256 recorded]...\n" + r[k][-1200:]
    ok = r["exit_code"] == 0 and csv_text is not None
    rows = list(csv.DictReader(csv_text.splitlines())) if ok else []
    return {"ok": ok, "rows": rows, "receipt": r}


# --------------------------------------------------------------------------------------------- contexts
class LiveContext:
    def __init__(self, project: mfa.Project, raw_dir: Path | None = None):
        self.p = project
        self.raw = raw_dir or project.upstream / "data" / "raw"
        self.transcript: dict[str, object] = {}
        self._cache: dict[str, object] = {}

    def _rec(self, key: str, fn):
        if key not in self._cache:
            self._cache[key] = fn()
            self.transcript[key] = self._cache[key]
        return self._cache[key]

    def warehouse_columns(self) -> list[str]:
        def f():
            import duckdb
            con = duckdb.connect(str(self.p.warehouse), read_only=True)
            try:
                return sorted(".".join(r) for r in con.execute(
                    "select table_schema, table_name, column_name from information_schema.columns").fetchall())
            finally:
                con.close()
        return self._rec("warehouse_columns", f)

    def distinct_values(self, field: str) -> list[str]:
        def f():
            import duckdb
            s, t, c = field.split(".")
            con = duckdb.connect(str(self.p.warehouse), read_only=True)
            try:
                return sorted(str(r[0]) for r in con.execute(f'select distinct "{c}" from "{s}"."{t}"').fetchall())
            finally:
                con.close()
        return self._rec(f"distinct_values:{field}", f)

    def semantic_manifest(self) -> dict:
        return self._rec("semantic_manifest", lambda: json.loads(self.p.semantic_manifest.read_text(encoding="utf-8")))

    def native_dimensions(self, metric: str) -> list[str]:
        def f():
            r = mfa.list_dimensions(self.p, metric)
            return {"dimensions": r["dimensions"], "exit_code": r["receipt"]["exit_code"], "stdout_sha256": r["receipt"]["stdout_sha256"]}
        return self._rec(f"native_dimensions:{metric}", f)["dimensions"]

    def native_query(self, metric: str, group_by: list[str], where: list[str]) -> dict:
        key = "native_query:" + json.dumps([metric, group_by, where], ensure_ascii=False)
        return self._rec(key, lambda: native_query_with_where(self.p, metric, group_by, where))

    def estate_fingerprint(self) -> str:
        def f():
            import inventory
            return inventory.canon_sha(inventory.estate(self.p))
        return self._rec("estate_fingerprint", f)

    def oracle(self, required: list[str]) -> dict:
        key = "oracle:" + json.dumps(sorted(required))
        return self._rec(key, lambda: oracle_mod.expected(self.raw, required))


class SnapshotContext:
    """Answers only from a recorded transcript; a missing response is an error, never a default."""

    def __init__(self, transcript: dict):
        self.t = transcript

    def _get(self, key: str):
        if key not in self.t:
            raise KeyError(f"replay: response not recorded: {key}")
        return self.t[key]

    def warehouse_columns(self):
        return self._get("warehouse_columns")

    def distinct_values(self, field):
        return self._get(f"distinct_values:{field}")

    def semantic_manifest(self):
        return self._get("semantic_manifest")

    def native_dimensions(self, metric):
        return self._get(f"native_dimensions:{metric}")["dimensions"]

    def native_query(self, metric, group_by, where):
        return self._get("native_query:" + json.dumps([metric, group_by, where], ensure_ascii=False))

    def estate_fingerprint(self):
        return self._get("estate_fingerprint")

    def oracle(self, required):
        return self._get("oracle:" + json.dumps(sorted(required)))


# --------------------------------------------------------------------------------------------- helpers
def _relation(model: dict) -> str:
    nr = model.get("node_relation") or {}
    return f"{nr.get('schema_name')}.{nr.get('alias')}"


def _col(obj: dict) -> str:
    return obj.get("expr") or obj["name"]


def _primary_entity(model: dict) -> str | None:
    return next((e["name"] for e in model.get("entities") or [] if e.get("type") == "primary"), None)


def _where_clause(binding_dim: str, pred: dict) -> str:
    if pred["kind"] == "categorical_equals":
        return "{{ Dimension('%s') }} = '%s'" % (binding_dim, pred["value"])
    if pred["kind"] == "numeric_threshold":
        return "{{ Dimension('%s') }} %s %s" % (binding_dim, pred["op"], pred["value"])
    raise ValueError(pred["kind"])


# --------------------------------------------------------------------------------------------- predicate status
def evaluate_predicate(pid: str, pred: dict, binding: dict | None, frozen: dict, ctx) -> dict:
    metric = frozen["target"]["metric"]
    designated = frozen["authority_registry"].get(pred["fact_kind"], [])
    cols = set(ctx.warehouse_columns())
    out = {"predicate": pid, "kind": pred["kind"], "fact_kind": pred["fact_kind"], "binding": binding,
           "designated_fields": designated, "designated_fields_present": [f for f in designated if f in cols]}

    if binding is None:  # 3.1.1
        out["status"] = "MISSING_BINDING" if out["designated_fields_present"] else "NOT_FOUND_IN_BOUNDED_ESTATE"
        out["reason"] = ("a designated field exists but no binding was supplied" if out["designated_fields_present"]
                         else f"no field designated for {pred['fact_kind']} exists in the bounded estate "
                              f"({len(cols)} warehouse columns inspected); not a claim of absence elsewhere")
        return out
    phys = binding["physical"]
    out["physical_present"] = phys in cols
    if not out["physical_present"]:  # 3.1.2
        out["status"], out["reason"] = "INVALID_BINDING", f"physical field {phys} does not exist"
        return out
    if phys not in designated:  # 3.1.3
        out["status"] = "NOT_AUTHORITATIVE_FOR_FACT"
        out["reason"] = f"{phys} exists but is not designated for {pred['fact_kind']} (untrusted proxy; no equivalence rule exists)"
        return out

    sm = ctx.semantic_manifest()
    sem = binding["semantic"]
    p_table, p_col = phys.rsplit(".", 1)
    if "measure" in sem:  # 3.1.4 measure
        model = next((m for m in sm["semantic_models"] if m["name"] == sem["semantic_model"]), None)
        meas = next((x for x in (model or {}).get("measures") or [] if x["name"] == sem["measure"]), None)
        out["semantic_resolution"] = {"model": (model or {}).get("name"), "relation": _relation(model) if model else None,
                                      "measure_expr": _col(meas) if meas else None, "agg": (meas or {}).get("agg")}
        if not meas or _relation(model) != p_table or _col(meas) != p_col:
            out["status"], out["reason"] = "INVALID_BINDING", "measure missing or not computed from the bound physical column"
            return out
    else:  # 3.1.4 dimension / time_dimension
        name = sem.get("dimension") or sem.get("time_dimension")
        native = ctx.native_dimensions(metric)
        out["in_native_dimension_list"] = name in native
        if name not in native:
            exposing = [[m["name"], kind, x["name"]] for m in sm["semantic_models"] if _relation(m) == p_table
                        for kind in ("dimensions", "measures") for x in m.get(kind) or [] if _col(x) == p_col]
            out["catalog_scan_exposing_physical_column"] = exposing
            if exposing:
                out["status"], out["reason"] = "MISSING_BINDING", "column is exposed under another semantic name"
                return out
            out["status"] = "PRESENT_IN_SOURCE_NOT_EXPOSED"
            out["reason"] = f"{phys} exists and is designated, but no semantic object exposes it for {metric}"
            if pred["kind"] in ("categorical_equals", "numeric_threshold"):
                q = ctx.native_query(metric, [], [_where_clause(name, pred)])
                out["native_exposure_probe"] = {"where": _where_clause(name, pred), "accepted": q["ok"],
                                                "exit_code": q["receipt"]["exit_code"], "argv": q["receipt"]["argv"]}
            return out
        ent, _, dim = name.partition("__")
        model = next((m for m in sm["semantic_models"] if _primary_entity(m) == ent
                      and any(d["name"] == dim for d in m.get("dimensions") or [])), None)
        d = next((d for d in (model or {}).get("dimensions") or [] if d["name"] == dim), None)
        out["semantic_resolution"] = {"model": (model or {}).get("name"), "relation": _relation(model) if model else None,
                                      "dimension_column": _col(d) if d else None, "type": (d or {}).get("type")}
        if not d or _relation(model) != p_table or _col(d) != p_col:
            out["status"], out["reason"] = "INVALID_BINDING", f"{name} does not resolve to {phys}"
            return out
        if "time_dimension" in sem and (d.get("type") != "time" or ((model.get("defaults") or {}).get("agg_time_dimension") != dim)):
            out["status"], out["reason"] = "INVALID_BINDING", f"{name} is not the time dimension that drives metric_time"
            return out
    if pred["kind"] == "categorical_equals":  # 3.1.5
        vals = ctx.distinct_values(phys)
        out["observed_values"] = vals
        if pred["value"] not in vals:
            out["status"], out["reason"] = "VALUE_NOT_OBSERVED", f"{pred['value']!r} not among observed values"
            return out
    out["status"] = "BOUND_AND_EXPOSED"
    return out


# --------------------------------------------------------------------------------------------- case status
def _metric_consistency(frozen: dict, required: dict, preds: dict, ctx) -> list[str]:
    metric = frozen["target"]["metric"]
    sm = ctx.semantic_manifest()
    m = next((x for x in sm["metrics"] if x["name"] == metric), None)
    if m is None:
        return [f"metric {metric} not in semantic manifest"]
    bound = {pid: r for pid, r in preds.items() if r["status"] == "BOUND_AND_EXPOSED"}
    problems = []
    measure = ((m.get("type_params") or {}).get("measure") or {}).get("name")
    measures = {r["binding"]["semantic"]["measure"] for r in bound.values() if r["kind"] == "measure_sum"}
    if measure not in measures:
        problems.append(f"metric input measure {measure!r} is not the measure of a bound line-amount predicate {sorted(measures)}")
    allowed = {"{{ Dimension('%s') }} = '%s'" % (r["binding"]["semantic"]["dimension"], frozen["predicates"][pid]["value"])
               for pid, r in bound.items() if r["kind"] == "categorical_equals"}
    for w in ((m.get("filter") or {}).get("where_filters") or []):
        if w.get("where_sql_template") not in allowed:
            problems.append(f"metric filter {w.get('where_sql_template')!r} is not implied by a bound required predicate")
    owner = next((s for s in sm["semantic_models"] for x in s.get("measures") or [] if x["name"] == measure), None)
    agg_t = ((owner or {}).get("defaults") or {}).get("agg_time_dimension")
    times = {r["binding"]["semantic"]["time_dimension"].partition("__")[2] for r in bound.values() if r["kind"] == "time_grain"}
    if agg_t not in times:
        problems.append(f"metric time dimension {agg_t!r} is not a bound time predicate {sorted(times)}")
    return problems


def _plan(frozen: dict, preds: dict, ctx) -> dict:
    metric = frozen["target"]["metric"]
    m = next(x for x in ctx.semantic_manifest()["metrics"] if x["name"] == metric)
    in_filter = {w.get("where_sql_template") for w in ((m.get("filter") or {}).get("where_filters") or [])}
    where = []
    for pid, r in preds.items():
        if r["status"] == "BOUND_AND_EXPOSED" and r["kind"] in ("categorical_equals", "numeric_threshold"):
            clause = _where_clause(r["binding"]["semantic"]["dimension"], frozen["predicates"][pid])
            if clause not in in_filter:
                where.append(clause)
    grain = next((frozen["predicates"][pid]["grain"] for pid, r in preds.items() if r["kind"] == "time_grain"), None)
    return {"metric": metric, "group_by": [f"metric_time__{grain}"] if grain else [], "where": where}


def native_by_year(rows: list[dict], metric: str) -> dict[str, str]:
    return {r["metric_time__year"][:4]: str(Decimal(r[metric]).quantize(CENT)) for r in rows}


def evaluate_case(case: dict, frozen: dict, ctx, frozen_fingerprint: str | None = None) -> dict:
    required = case["required"]
    preds = {pid: evaluate_predicate(pid, frozen["predicates"][pid],
                                     frozen["bindings"][bid] if bid else None, frozen, ctx)
             for pid, bid in required.items()}
    res = {"required": required, "predicates": preds,
           "uncovered": sorted(pid for pid, r in preds.items() if r["status"] != "BOUND_AND_EXPOSED")}
    problems = _metric_consistency(frozen, required, preds, ctx)
    res["metric_consistency_problems"] = problems
    statuses = [r["status"] for r in preds.values()]
    fp_live = ctx.estate_fingerprint()
    fp_frozen = frozen_fingerprint or frozen["bounded_estate"]["estate_fingerprint"]
    res["estate_fingerprint"] = {"live": fp_live, "frozen": fp_frozen, "equal": fp_live == fp_frozen}
    if problems:
        status = "INVALID_BINDING"
    elif "INVALID_BINDING" in statuses:
        status = "INVALID_BINDING"
    elif not res["estate_fingerprint"]["equal"]:
        status = "INCONCLUSIVE"
    elif "NOT_FOUND_IN_BOUNDED_ESTATE" in statuses:
        status = "NOT_FOUND_IN_BOUNDED_ESTATE"
    elif "PRESENT_IN_SOURCE_NOT_EXPOSED" in statuses:
        status = "PRESENT_IN_SOURCE_NOT_EXPOSED"
    elif any(s != "BOUND_AND_EXPOSED" for s in statuses):
        status = "UNVERIFIED"
    else:
        status = None  # all bound: decided by native execution vs oracle
    if not problems:
        plan = _plan(frozen, preds, ctx)
        q = ctx.native_query(plan["metric"], plan["group_by"], plan["where"])
        native = {"plan": plan, "ok": q["ok"], "receipt_argv": q["receipt"]["argv"], "exit_code": q["receipt"]["exit_code"],
                  "csv_sha256": q["receipt"].get("csv_sha256"),
                  "by_year": native_by_year(q["rows"], plan["metric"]) if q["ok"] else None}
        if status is None:
            orc = ctx.oracle(list(required))
            res["oracle"] = orc
            res["native"] = native
            if not q["ok"]:
                status, res["reason"] = "UNVERIFIED", "native query failed"
            elif not orc.get("computable"):
                status, res["reason"] = "UNVERIFIED", "oracle not computable: " + orc.get("reason", "")
            else:
                res["comparison"] = oracle_mod.compare(native["by_year"], orc["by_year"])
                status = "FULLY_OBSERVABLE_FOR_THIS_CALCULATION" if res["comparison"]["equal"] else "UNVERIFIED"
        else:
            native["label"] = "COVERED SUBSET ONLY: does not cover " + ", ".join(res["uncovered"])
            res["covered_subset_native"] = native
    res["case_status"] = status
    res["verified_for_recorded_checks"] = status == "FULLY_OBSERVABLE_FOR_THIS_CALCULATION"
    return res


def apply_variant(frozen: dict, variant: dict) -> dict:
    """Build a case from a frozen adversarial variant (binding or required-set edits only)."""
    base = frozen["cases"][variant["base"]]
    req = dict(base["required"])
    req.update(variant.get("set_binding", {}))
    req.update(variant.get("add_required", {}))
    return {"clause": base["clause"], "required": req}
