"""Meaningful execution-boundary checks, separate from semantic-model accuracy."""
import copy
from pathlib import Path
import tempfile
import unittest

import duckdb

from viability.warehouse import Warehouse, packet
from viability.checks import clauses, reference_plan, validate_plan
from viability.run import HERE


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.duckdb'
        with duckdb.connect(str(self.path)) as con:
            con.execute('create table items(id integer, amount integer)')
            con.execute('insert into items values (1, 100), (2, NULL)')
        self.warehouse = Warehouse(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_select_preserves_missing_value(self):
        result = self.warehouse.query('select id, amount from items where amount is null')
        self.assertEqual(result['rows'], [[2, None]])

    def test_write_rejected_and_data_unchanged(self):
        with self.assertRaises(ValueError):
            self.warehouse.query('delete from items')
        self.assertEqual(self.warehouse.query('select count(*) from items')['rows'], [[2]])

    def test_multiple_statements_rejected(self):
        with self.assertRaises(ValueError):
            self.warehouse.query('select 1; select 2')

    def test_external_file_read_rejected(self):
        source = Path(self.temp.name) / 'outside.csv'
        source.write_text('secret\nnot-for-query\n')
        with self.assertRaises(duckdb.Error):
            self.warehouse.query("select * from read_csv('" + str(source) + "')")

    def test_result_budget_has_truncation_marker(self):
        result = self.warehouse.query('select * from range(100)', limit=5)
        self.assertEqual(len(result['rows']), 5)
        self.assertTrue(result['truncated'])

    def test_snapshot_changes_when_records_change(self):
        before = self.warehouse.snapshot('items')
        with duckdb.connect(str(self.path)) as con:
            con.execute('update items set amount=101 where id=1')
        after = self.warehouse.snapshot('items')
        self.assertNotEqual(before['rows_sha256'], after['rows_sha256'])


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.packet = packet(HERE / 'runs/integration/case_01', clauses(1))
        self.plan = reference_plan(self.packet, 1)

    def test_actual_lineage_reaches_both_seed_tables(self):
        nodes = {n['id'] for n in self.packet['nodes']}
        self.assertEqual(nodes, {'model.jaffle_shop.orders', 'model.jaffle_shop.stg_orders',
                                 'model.jaffle_shop.stg_payments', 'seed.jaffle_shop.raw_orders',
                                 'seed.jaffle_shop.raw_payments'})
        validate_plan(self.packet, self.plan)

    def test_missing_requirement_account_rejected(self):
        self.plan['coverage'].pop()
        with self.assertRaises(ValueError):
            validate_plan(self.packet, self.plan)

    def test_fabricated_clause_quote_rejected(self):
        self.plan['checks'][0]['source_quote'] = 'Amounts are in euros.'
        with self.assertRaises(ValueError):
            validate_plan(self.packet, self.plan)

    def test_citing_unlisted_dependency_rejected(self):
        self.plan['checks'][0]['node_ids'] = ['model.other.table']
        with self.assertRaises(ValueError):
            validate_plan(self.packet, self.plan)

    def test_plan_for_another_snapshot_rejected(self):
        self.plan['snapshot_id'] = 'old'
        with self.assertRaises(ValueError):
            validate_plan(self.packet, self.plan)


if __name__ == '__main__':
    unittest.main()
