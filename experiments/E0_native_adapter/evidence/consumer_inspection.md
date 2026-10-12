# S13 consumer inspection (source code read at 312e97ad; nothing executed)

## governed_analytics_agent/reporting.py (sha256 8fb3c84955d6e4ff…)
```
14:def fetch(
27:    rows = sl.run_query(q)
35:def kpis() -> dict[str, float]:
37:    df = fetch(["completed_revenue", "gross_margin_rate", "orders", "active_customers"])
42:        "completed_revenue": float(row.get("completed_revenue", 0) or 0),
```

## streamlit_app.py (sha256 4167f8632f0605f0…)
```
17:from governed_analytics_agent.catalog import load_catalog
43:    if settings.semantic_manifest_path.exists() and settings.warehouse_db_abs.exists():
66:        proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env, capture_output=True, text=True)
80:    return load_catalog()
84:def fetch(metrics, group_by=None, order_by=None, limit=None) -> pd.DataFrame:
89:def get_kpis() -> dict:
90:    return reporting.kpis()
207:    k = get_kpis()
209:    c1.metric("Completed revenue", eur(k.get("completed_revenue", 0)))
```

## governed_analytics_agent/semantic_layer.py (sha256 e95cda4a84c1fa6e…)
```
19:from .catalog import load_catalog
59:def _base_cmd() -> list[str]:
67:    local_mf = Path(sys.executable).parent / "mf"
70:    found = shutil.which("mf")
73:    return ["uv", "run", "mf"]
76:def _run_mf(
79:    env = {**os.environ, **settings.metricflow_env(), **(extra_env or {})}
81:        _base_cmd() + args,
82:        cwd=str(settings.dbt_project_dir),
92:    return frozenset(load_catalog().time_dimensions)
109:def run_query(q: MetricQuery) -> list[dict]:
113:        proc = _run_mf([*_query_args(q), "--csv", str(out)])
120:def explain_sql(q: MetricQuery) -> str:
122:    proc = _run_mf([*_query_args(q), "--explain"])
```

## governed_analytics_agent/catalog.py (sha256 1f827a69ee391689…)
```
4:read from target/semantic_manifest.json (produced by `dbt parse`), so the
60:def load_catalog(manifest_path: Path | None = None) -> Catalog:
61:    path = Path(manifest_path or settings.semantic_manifest_path)
```

## governed_analytics_agent/config.py (sha256 e2073cc5a0c65209…)
```
53:    def semantic_manifest_path(self) -> Path:
54:        return self.dbt_project_dir / "target" / "semantic_manifest.json"
56:    def metricflow_env(self) -> dict[str, str]:
```

