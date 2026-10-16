"""Read-only local adapter; Snowflake/Databricks implementations are not supplied."""
import hashlib
import json
from pathlib import Path
from threading import Timer

import duckdb


def canonical(value):
    return json.dumps(value, sort_keys=True, default=str)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Warehouse:
    def __init__(self, path):
        self.path = Path(path)

    def query(self, sql, limit=20):
        if len(sql) > 12000:
            raise ValueError('SQL exceeds review budget')
        with duckdb.connect(str(self.path), read_only=True, config={
            'enable_external_access': False, 'threads': 1, 'memory_limit': '256MB'
        }) as connection:
            statements = connection.extract_statements(sql)
            if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
                raise ValueError('Exactly one SELECT statement is allowed')
            timer = Timer(5, connection.interrupt)
            timer.daemon = True
            timer.start()
            try:
                cursor = connection.execute('SELECT * FROM (' + sql.rstrip().rstrip(';') + ') AS review_query LIMIT ' + str(limit + 1))
                rows = cursor.fetchall()
                columns = [d[0] for d in cursor.description]
            finally:
                timer.cancel()
        return {'sql': sql, 'columns': columns, 'rows': json.loads(canonical(rows[:limit])),
                'has_counterexamples': bool(rows), 'truncated': len(rows) > limit,
                'result_sha256': fingerprint([columns, rows])}

    def snapshot(self, relation):
        # Relation name is a quoted dbt manifest identifier, never a model-proposed expression.
        with duckdb.connect(str(self.path), read_only=True, config={'enable_external_access': False}) as con:
            schema = con.execute('DESCRIBE SELECT * FROM ' + relation).fetchall()
            rows = con.execute('SELECT * FROM ' + relation + ' ORDER BY ALL').fetchall()
        return {'schema': json.loads(canonical(schema)), 'row_count': len(rows),
                'rows_sha256': fingerprint(rows), 'sample': json.loads(canonical(rows[:5]))}


def packet(project, clauses):
    project = Path(project)
    manifest = json.loads((project / 'target/manifest.json').read_text())
    target = 'model.jaffle_shop.orders'
    visited, pending, nodes = set(), [target], []
    warehouse = Warehouse(project / 'warehouse.duckdb')
    while pending:
        ident = pending.pop()
        if ident in visited:
            continue
        visited.add(ident)
        node = manifest['nodes'][ident]
        dependencies = node.get('depends_on', {}).get('nodes', [])
        pending.extend(dependencies)
        nodes.append({'id': ident, 'relation': node['relation_name'], 'dependencies': dependencies,
                      'description': node.get('description'), 'columns': node.get('columns'),
                      'raw_code': node.get('raw_code'), 'compiled_code': node.get('compiled_code'),
                      'physical': warehouse.snapshot(node['relation_name'])})
    nodes.sort(key=lambda n: n['id'])
    value = {'authority_status': 'FICTIONAL_TEST_AGREEMENT', 'governing_clauses': clauses,
             'source_completeness': 'Complete only for the five synthetic requirements in this test.',
             'metric': {'id': 'order_consideration_aud', 'model': target,
                        'definition': 'SUM(amount) over orders with order_date from 2018-01-01 through 2018-04-30 inclusive',
                        'grain': 'one row per order', 'currency': 'AUD'},
             'nodes': nodes}
    value['snapshot_id'] = fingerprint(value)
    return value
