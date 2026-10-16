"""Boundary tests. These do not measure model alignment-detection accuracy."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from alignment.agent import ROOT, prepare, validate, report, freshness, live_review, read, write


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.packet = prepare(ROOT, ROOT / 'alignment/examples/lab_manifest.json')
        self.response = read(ROOT / 'alignment/examples/review.json')

    def test_real_assisted_review_has_valid_evidence(self):
        self.assertTrue(validate(self.packet, self.response))
        result = report(self.packet, self.response, {'mode': 'test'})
        self.assertEqual(result['authority'], 'DRAFT_OR_UNVERIFIED_REFERENCE')
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')

    def test_fabricated_quotation_rejected(self):
        self.response['findings'][0]['governing_evidence'][0]['quote'] = 'All receipts are optional.'
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_operational_text_cannot_be_its_own_authority(self):
        self.response['findings'][0]['governing_evidence'] = self.response['findings'][0]['operational_evidence']
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_missing_segment_disposition_rejected(self):
        self.response['coverage'].pop()
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_duplicate_disposition_rejected(self):
        self.response['coverage'].append(self.response['coverage'][0])
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_different_snapshot_rejected(self):
        self.response['packet_id'] = 'wrong'
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_tampered_packet_rejected(self):
        self.packet['segments'][0]['text'] += 'Changed'
        with self.assertRaises(ValueError):
            validate(self.packet, self.response)

    def test_unverifiable_is_incomplete_even_without_findings(self):
        self.response['findings'] = []
        for entry in self.response['coverage']:
            entry['finding_ids'] = []
        self.response['coverage'][0]['disposition'] = 'UNVERIFIABLE'
        self.assertEqual(report(self.packet, self.response, {})['status'], 'REVIEW_INCOMPLETE')

    def test_no_findings_does_not_certify_alignment(self):
        self.response['findings'] = []
        for entry in self.response['coverage']:
            entry['finding_ids'] = []
        result = report(self.packet, self.response, {})
        self.assertEqual(result['status'], 'NO_ISSUES_DETECTED_IN_SUPPLIED_SCOPE')
        self.assertIn('not certified', result['validation'])

    def test_live_api_requires_credential(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'no live model call'):
                live_review(self.packet, 'test-model')

    def test_model_refusal_cannot_be_published(self):
        from io import BytesIO
        payload = json.dumps({'status': 'completed', 'output': [
            {'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'Unable to review'}]}]}).encode()
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-only-not-a-real-key'}), \
             patch('urllib.request.urlopen', return_value=BytesIO(payload)):
            with self.assertRaisesRegex(ValueError, 'refused'):
                live_review(self.packet, 'test-model')

    def test_document_change_invalidates_review(self):
        manifest = read(ROOT / 'alignment/examples/lab_manifest.json')
        previous = report(self.packet, self.response, {})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for doc in manifest['documents']:
                dest = root / doc['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / doc['path']).read_bytes())
            path = root / 'manifest.json'
            write(path, manifest)
            self.assertEqual(freshness(root, path, previous)['status'], 'CURRENT')
            source = root / manifest['documents'][0]['path']
            source.write_text(source.read_text().replace('£1,000', '£2,000'))
            result = freshness(root, path, previous)
            self.assertEqual(result['status'], 'STALE_REVIEW')
            self.assertEqual(result['changed_documents'], ['policy'])

    def test_dbt_adapter_includes_code_and_dependency_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'policy.md').write_text('Royalty applies to paid invoices.')
            node = {'unique_id': 'model.demo.revenue', 'resource_type': 'model',
                    'description': 'Paid revenue', 'raw_code': 'select * from invoices',
                    'compiled_code': 'select * from warehouse.invoices',
                    'depends_on': {'nodes': ['source.demo.invoices']}}
            write(root / 'dbt.json', {'nodes': {node['unique_id']: node}})
            manifest = {'scope': 'Inspect stated definition and SQL; no database execution.', 'documents': [
                {'id': 'p', 'role': 'governing', 'authority_status': 'draft', 'path': 'policy.md'},
                {'id': 'd', 'role': 'operational', 'path': 'dbt.json', 'format': 'dbt_manifest',
                 'node_ids': [node['unique_id']]}]}
            write(root / 'manifest.json', manifest)
            packet = prepare(root, root / 'manifest.json')
            representation = packet['segments'][1]['text']
            self.assertIn('Paid revenue', representation)
            self.assertIn('warehouse.invoices', representation)
            self.assertIn('source.demo.invoices', representation)


if __name__ == '__main__':
    unittest.main()
