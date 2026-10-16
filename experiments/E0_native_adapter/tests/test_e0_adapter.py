"""E0 adapter tests (PROTOCOL.md section 6, diagnostic D2). Run after src/run_e0.py has built the warehouse:

    .upstream/.venv/bin/python -m pytest -q tests/test_e0_adapter.py

They need the real native runtime and the built warehouse; they skip only if the semantic manifest is absent.
"""
from __future__ import annotations

import json
import shutil
import stat
import sys
from decimal import Decimal
from pathlib import Path

import pytest

E0 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E0 / "src"))
import crosscheck  # noqa: E402
import mf_adapter as mfa  # noqa: E402
from run_e0 import EXPECTED_IDENTITY, GROUP_BY, METRIC, ORDER  # noqa: E402

UPSTREAM = E0 / ".upstream"
P = mfa.open_project(UPSTREAM)
pytestmark = pytest.mark.skipif(not P.semantic_manifest.exists(), reason="run src/run_e0.py first (no semantic manifest)")


def by_year(rows: list[dict]) -> dict[str, Decimal]:
    return {r["metric_time__year"][:4]: Decimal(r[METRIC]).quantize(Decimal("0.01")) for r in rows}


def test_t1_live_query_is_native_and_repeatable():
    a = mfa.query(P, [METRIC], GROUP_BY, ORDER)
    b = mfa.query(P, [METRIC], GROUP_BY, ORDER)
    assert a["receipt"]["exit_code"] == 0 and a["receipt"]["csv_written"]
    assert a["csv"] == b["csv"] and len(a["rows"]) >= 1
    assert a["receipt"]["fingerprints_before"] == b["receipt"]["fingerprints_after"]
    assert a["receipt"]["mf_identity"]["distribution"].startswith("dbt_metricflow-")


@pytest.mark.parametrize("metrics,group_by", [(["completed_revenue_e0_nonexistent"], None),
                                              ([METRIC], ["sales__e0_nonexistent_dimension"])])
def test_t2_invalid_input_is_rejected_without_rows(metrics, group_by):
    with pytest.raises(mfa.NativeQueryError) as e:
        mfa.query(P, metrics, group_by, None)
    assert e.value.receipt["exit_code"] != 0 or not e.value.receipt["csv_written"]


def test_t3_stub_executable_is_rejected(tmp_path):
    stub = tmp_path / "mf"
    stub.write_text("#!/bin/sh\n# canned fixture pretending to be MetricFlow\nfor a in \"$@\"; do last=$a; done\n"
                    "printf 'metric_time__year,completed_revenue\\n2024-01-01 00:00:00,1\\n' > \"$last\"\nexit 0\n")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    fake = mfa.open_project(UPSTREAM, mf=stub)
    with pytest.raises(mfa.IdentityError):
        mfa.query(fake, [METRIC], GROUP_BY, ORDER)


def test_t4_metric_identity_drift_is_detected(tmp_path):
    target = tmp_path / "dbt" / "retail_dwh" / "target"
    target.mkdir(parents=True)
    sm = json.loads(P.semantic_manifest.read_text(encoding="utf-8"))
    for m in sm["metrics"]:
        if m["name"] == METRIC:
            m["filter"]["where_filters"][0]["where_sql_template"] = "{{ Dimension('sales__status') }} = 'returned'"
    (target / "semantic_manifest.json").write_text(json.dumps(sm), encoding="utf-8")
    shutil.copy(P.dbt_manifest, target / "manifest.json")
    drifted = mfa.Project(upstream=tmp_path, dbt_dir=tmp_path / "dbt" / "retail_dwh", warehouse=P.warehouse, mf=P.mf, python=P.python)
    assert mfa.identity_mismatches(mfa.inspect_metric(P, METRIC), EXPECTED_IDENTITY) == []
    assert mfa.identity_mismatches(mfa.inspect_metric(drifted, METRIC), EXPECTED_IDENTITY) != []


def test_t5_native_result_follows_the_rows(tmp_path):
    import duckdb
    copy_dir = tmp_path / "wh"
    copy_dir.mkdir()
    copy = copy_dir / "warehouse.duckdb"  # same file name: the manifest's catalog name is derived from it
    shutil.copy(P.warehouse, copy)
    con = duckdb.connect(str(copy))
    sid, year, price = con.execute("select sales_id, year(order_date), unit_price from gold.fact_sales "
                                   "where status = 'completed' order by sales_id limit 1").fetchone()
    con.execute("update gold.fact_sales set quantity = quantity + 1, revenue = revenue + unit_price where sales_id = ?", [sid])
    con.close()
    before = by_year(mfa.query(P, [METRIC], GROUP_BY, ORDER)["rows"])
    after = by_year(mfa.query(mfa.open_project(UPSTREAM, warehouse=copy), [METRIC], GROUP_BY, ORDER)["rows"])
    y = str(year)
    assert after[y] - before[y] == Decimal(str(price)).quantize(Decimal("0.01"))
    assert {k: v for k, v in after.items() if k != y} == {k: v for k, v in before.items() if k != y}


def test_t6_crosscheck_matches_native():
    native = {k: str(v) for k, v in by_year(mfa.query(P, [METRIC], GROUP_BY, ORDER)["rows"]).items()}
    assert native == crosscheck.compute(UPSTREAM / "data" / "raw")["by_year"]
