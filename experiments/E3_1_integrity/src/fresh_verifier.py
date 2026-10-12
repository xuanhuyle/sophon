"""E3.1 fresh verifier (PROTOCOL.md §4). Everything it trusts comes from cases/TRUSTED_MANIFEST.json, the pinned
upstream it rebuilds, and code files whose sha256 it checks against that manifest. It never reads a value, query or
hash from a candidate receipt to decide what is true.

FreshVerifier(upstream, manifest, workdir) performs the fresh rebuild on construction (E0's run_e0.py --regen in a
child process, warehouse deleted first) and checks the build against the trusted anchors. Native queries, reference
calculations and guards are computed lazily and cached for the lifetime of this verifier process.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E31 = HERE.parent
EXP = E31.parent
REPO = EXP.parent


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def by_period(rows: list[dict], metric: str) -> dict[str, str]:
    return {r["metric_time__year"][:4]: str(Decimal(r[metric])) for r in rows}


def dec_equal(a: dict | None, b: dict | None) -> bool:
    return a is not None and b is not None and set(a) == set(b) and all(Decimal(a[k]) == Decimal(b[k]) for k in a)


class FreshVerifier:
    def __init__(self, upstream: Path, manifest: dict, workdir: Path):
        self.up = Path(upstream).resolve()
        self.m = manifest
        self.work = Path(workdir)
        self.work.mkdir(parents=True, exist_ok=True)
        self.run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        self._native, self._ref, self._guards = {}, {}, {}
        self.build = self._rebuild()
        self.estates = {}
        if self.build["ok"]:
            self._load_trusted_modules()
            self.estates["TRUSTED_REBUILD"] = self.up / "data" / "warehouse.duckdb"
            self.estates["CONTROL_NEGATIVE_QUANTITY"] = self._control_negative_quantity()

    # ------------------------------------------------------------------ V-a fresh rebuild and anchor check
    def _rebuild(self) -> dict:
        wh = self.up / "data" / "warehouse.duckdb"
        for p in (wh, wh.with_suffix(".duckdb.wal")):
            if p.exists():
                p.unlink()
        py = self.up / ".venv" / "bin" / "python"
        out = self.work / "e0_regen"
        proc = subprocess.run([str(py), str(EXP / "E0_native_adapter" / "src" / "run_e0.py"), "--regen", "--upstream", str(self.up),
                               "--out", str(out)], capture_output=True, text=True)
        b = {"regen_exit": proc.returncode, "regen_stderr_tail": proc.stderr[-1500:]}
        commit = subprocess.run(["git", "-C", str(self.up), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        clean = subprocess.run(["git", "-C", str(self.up), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip() == ""
        freeze = subprocess.run(["uv", "pip", "freeze", "--python", str(py)], capture_output=True, text=True).stdout
        raw = self.up / "data" / "raw"
        csv = {f.name: sha_file(f) for f in sorted(raw.glob("*.csv"))}
        sm = self.up / "dbt" / "retail_dwh" / "target" / "semantic_manifest.json"
        b.update(upstream_commit=commit, upstream_clean=clean, env_freeze_sha256=hashlib.sha256(freeze.encode()).hexdigest(),
                 semantic_manifest_sha256=sha_file(sm) if sm.exists() else None, raw_csv_sha256=csv,
                 warehouse_sha256=sha_file(wh) if wh.exists() else None)
        b["anchor_checks"] = {
            "upstream_commit": commit == self.m["upstream"]["commit"], "upstream_clean": clean,
            "env_freeze": b["env_freeze_sha256"] == self.m["env_freeze_sha256"],
            "semantic_manifest": b["semantic_manifest_sha256"] == self.m["semantic_manifest_sha256"],
            "raw_csv": csv == self.m["raw_csv_sha256"],
            "code": {p: sha_file(REPO / p) == h for p, h in self.m["code_sha256"].items()}}
        ac = b["anchor_checks"]
        b["ok"] = proc.returncode == 0 and all(v for k, v in ac.items() if k != "code") and all(ac["code"].values())
        return b

    def _load(self, name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _load_trusted_modules(self) -> None:
        sys.path.insert(0, str(EXP / "E1_expressibility_erratum" / "src"))  # run_erratum's own imports (E1 wrapper, E0 adapter)
        self.erratum = self._load("e31_trusted_run_erratum", REPO / self.m["guard_code"]["code"])
        self.mfa = self.erratum.mfa

    def _control_negative_quantity(self) -> Path:
        import duckdb
        d = self.work / "estates" / "CONTROL_NEGATIVE_QUANTITY"
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        wh = d / "warehouse.duckdb"  # same file name keeps the manifest's catalog name valid
        shutil.copy(self.estates["TRUSTED_REBUILD"], wh)
        con = duckdb.connect(str(wh))
        try:
            rows = con.execute("select sales_id, unit_price from gold.fact_sales where status = 'completed' order by sales_id").fetchall()
            hi = next(r for r in rows if r[1] > 100)
            lo = next(r for r in rows if r[1] < 100)
            for sid, _ in (hi, lo):
                con.execute("update gold.fact_sales set quantity = -1, revenue = cast(-1 * unit_price as decimal(12,2)) where sales_id = ?", [sid])
            con.execute("checkpoint")
        finally:
            con.close()
        self.control_mutation = {"set_quantity_minus_1": [int(hi[0]), int(lo[0])]}
        return wh

    # ------------------------------------------------------------------ V-c fresh native
    def native(self, query: dict, estate: str, runtime: str) -> dict:
        key = (json.dumps(query, sort_keys=True), estate, runtime)
        if key in self._native:
            return self._native[key]
        res = {"ok": False, "by_period": None, "error": None}
        try:
            if not self.build["ok"]:
                raise RuntimeError("fresh build failed or not anchored")
            mf = "/nonexistent/E3_1_runtime_unavailable/mf" if runtime == "UNAVAILABLE" else None
            p = self.mfa.open_project(self.up, warehouse=self.estates[estate], mf=mf)
            r = self.erratum.e1.native_query_with_where(p, query["metric"], query["group_by"], query["where"])
            res.update(ok=r["ok"], exit_code=r["receipt"]["exit_code"], argv=r["receipt"]["argv"],
                       mf_identity=r["receipt"].get("mf_identity"), rows=r["rows"],
                       by_period=by_period(r["rows"], query["metric"]) if r["ok"] else None,
                       semantic_manifest_sha256=self.mfa.sha256_file(p.semantic_manifest),
                       warehouse_sha256=self.mfa.sha256_file(p.warehouse))
            if r["ok"]:
                ex = self.erratum.explain_with_where(p, query["metric"], query["group_by"], " AND ".join(query["where"]))
                res["compiled_sql"] = ex["sql"]
        except Exception as e:  # noqa: BLE001  (unavailable runtime is a result, not a crash)
            res["error"] = f"{type(e).__name__}: {e}"[:600]
        self._native[key] = res
        return res

    # ------------------------------------------------------------------ V-d fresh independent reference
    def reference(self, reading_key: str, code_mode: str) -> dict:
        key = (reading_key, code_mode)
        if key in self._ref:
            return self._ref[key]
        res = {"ok": False, "by_period": None, "error": None}
        spec = self.m["reference_functions"].get(reading_key)
        try:
            if spec is None:
                raise LookupError(f"no trusted reference function for {reading_key}")
            path = REPO / spec["code"]
            if code_mode == "TAMPERED":  # disposable altered copy; its hash will not match the manifest
                t = self.work / "tampered" / Path(spec["code"]).name
                t.parent.mkdir(parents=True, exist_ok=True)
                t.write_text(path.read_text(encoding="utf-8") + "\n# E3.1 control: one appended line\n", encoding="utf-8")
                path = t
            got = sha_file(path)
            res["code_sha256"] = got
            if got != self.m["code_sha256"][spec["code"]]:
                raise PermissionError(f"reference code hash {got[:12]} != trusted {self.m['code_sha256'][spec['code']][:12]}; not executed")
            raw = self.up / "data" / "raw"
            if {f.name: sha_file(f) for f in sorted(raw.glob("*.csv"))} != self.m["raw_csv_sha256"]:
                raise PermissionError("raw CSVs differ from trusted anchors")
            mod = self._load(f"e31_ref_{Path(spec['code']).stem}_{code_mode}", path)
            call = spec["call"]
            if call.startswith("compute("):
                val = mod.compute(raw)["by_year"]
            elif call.startswith("DIAGNOSTICS["):
                val = mod.DIAGNOSTICS[call.split("'")[1]](raw)
            elif call.startswith("h6("):
                val = mod.h6(raw)
            else:
                raise LookupError(call)
            res.update(ok=True, by_period=val)
        except Exception as e:  # noqa: BLE001
            res["error"] = f"{type(e).__name__}: {e}"[:600]
        self._ref[key] = res
        return res

    # ------------------------------------------------------------------ V-e fresh guards
    def guards(self, query: dict, estate: str) -> dict:
        key = (json.dumps(query, sort_keys=True), estate)
        if key in self._guards:
            return self._guards[key]
        res = {"ok": False, "guards": None, "error": None}
        try:
            wh = self.estates[estate]
            p = self.mfa.open_project(self.up, warehouse=wh)
            ex = self.erratum.explain_with_where(p, query["metric"], query["group_by"], " AND ".join(query["where"]))
            raw = self.up / "data" / "raw"
            prices = self.erratum.csv_prices(raw)
            g = self.erratum.guards(self.erratum.warehouse_lines(wh), prices, len(prices), ex["sql"])
            names = ("quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison")
            res.update(ok=all(g[n]["ok"] for n in names), guards={n: g[n]["ok"] for n in names},
                       min_quantity=g["quantity_positive"]["min_quantity"])
        except Exception as e:  # noqa: BLE001
            res["error"] = f"{type(e).__name__}: {e}"[:600]
        self._guards[key] = res
        return res
