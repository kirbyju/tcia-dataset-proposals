"""Behavioral checks for fail-closed current catalog captures."""
import copy
import importlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
refresh = importlib.import_module('refresh_label_catalog')
exporter = importlib.import_module('export_catalog_dataset_labels')
builder = importlib.import_module('build_label_catalog')


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.registries = {f: [{'id': i + 1, key: f}] for i, (f, (_, key)) in enumerate(refresh.FIELDS.items())}
        self.record = {'id': 1, 'result_short_title': 'Example', 'url': 'https://example.org/',
            'hide_from_browse_table': 'No', 'cancer_types': ['disease_type', 'disease_type'],
            'cancer_locations': ['disease_location'], 'species': ['species'],
            'program': {'program_name': 'program'}, 'external_resources': ['external_resource'],
            'result_downloads': [{'id': 10, 'download type': ['data_category'],
                'data type': ['data_type', 'data_type'], 'file type': ['file_type']}],
            'collection_downloads': [{'id': 99, 'download type': ['WRONG RELATED SOURCE'],
                'data type': ['WRONG'], 'file type': ['WRONG']}]}

    def capture(self, record=None):
        return refresh.assemble(self.registries, {'analysis-results': [record or self.record]}, [], '2026-10-19')

    def test_download_counts_and_no_related_source_inheritance(self):
        self.record['result_downloads'].append({**self.record['result_downloads'][0], 'id': 11})
        result = self.capture()
        self.assertEqual(result['fields']['data_type'][0]['usage_count'], 2)
        self.assertEqual(result['fields']['disease_type'][0]['usage_count'], 1)
        self.assertEqual(len(result['fields']['data_category']), 1)
        self.assertEqual(result['current_download_count'], 2)

    def test_registered_unused_and_unregistered_observed_values(self):
        self.record['species'] = ['New species']
        rows = {r['label']: r for r in self.capture()['fields']['species']}
        self.assertEqual(rows['species']['usage_count'], 0)
        self.assertEqual(rows['New species']['registry_membership'], 'absent from complete registry')

    def test_missing_fields_and_empty_capture_fail(self):
        for key in ['result_downloads', 'hide_from_browse_table', 'species', 'external_resources']:
            record = copy.deepcopy(self.record)
            del record[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.capture(record)
        self.record['hide_from_browse_table'] = 'Yes'
        with self.assertRaises(ValueError):
            self.capture()

    def test_malformed_labels_and_duplicate_downloads_fail(self):
        self.record['species'] = ['species', {'bad': True}]
        with self.assertRaises(ValueError):
            self.capture()
        self.record['species'] = ['species']
        self.record['result_downloads'] *= 2
        with self.assertRaises(ValueError):
            self.capture()

    def test_new_term_is_flagged_without_guessing_or_resurrecting_removed_term(self):
        inventory = {'wordpress_registered_terms_complete': True, 'fields': {
            'disease_type': [{'label': 'New diagnosis', 'usage_count': 1, 'examples': []}]}}
        decisions = {'fields': {'disease_type': {'Retired term': {'decision': 'confirmed'}}}}
        builder.apply_decisions(inventory, decisions, {})
        rows = inventory['fields']['disease_type']
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['reference_review_required'])
        self.assertEqual(rows[0]['reference_links'], [])

    def test_current_renames_retain_reviewed_identifiers(self):
        refs = builder.load_references()
        inventory = {'wordpress_registered_terms_complete': True, 'fields': {'disease_type': [
            {'label': label, 'usage_count': 1, 'examples': []} for label in
            ['COVID-19 Infection', 'Vestibular Schwannoma', 'Lymphadenopathy', 'Ewing Sarcoma',
             'Peripheral Primitive Neuroectodermal Tumor', 'Desmoid-Type Fibromatosis']]}}
        builder.apply_decisions(inventory, {}, refs)
        for row in inventory['fields']['disease_type']:
            self.assertTrue(row['reference_links'], row['label'])
            self.assertFalse(row.get('reference_review_required'))

    def test_pagination_detects_truncation_duplicates_and_drift(self):
        class Response:
            def __init__(self, data): self.data = data
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return json.dumps(self.data).encode()
        for second in [
            {'page': 2, 'total': 101, 'total_pages': 2, 'results': []},
            {'page': 2, 'total': 101, 'total_pages': 2, 'results': [{'id': 0}]},
            {'page': 2, 'total': 102, 'total_pages': 2, 'results': [{'id': 100}, {'id': 101}]},
        ]:
            first = {'page': 1, 'total': 101, 'total_pages': 2, 'results': [{'id': i} for i in range(100)]}
            with patch.object(exporter, 'urlopen', side_effect=[Response(first), Response(second)]):
                with self.assertRaises(ValueError):
                    exporter.fetch_pages('example')


if __name__ == '__main__':
    unittest.main()
