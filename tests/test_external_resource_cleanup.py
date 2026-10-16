import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / 'skills/curate-tcia-wordpress-metadata/references'
spec = importlib.util.spec_from_file_location('catalog_for_cleanup', ROOT / 'scripts/build_label_catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CleanupHandoffTests(unittest.TestCase):
    def test_complete_crosswalk_uses_existing_targets_and_holds_content_dependent_choices(self):
        plan = json.loads((REFS/'external-resource-cleanup-plan-2026-10-16.json').read_text())
        inventory = json.loads(catalog.DEFAULT_DATASET_LABELS.read_text())
        registered = {r['label'] for r in inventory['fields']['external_resource'] if r['registry_membership']=='registered'}
        crosswalk = {r['old_label']: r for r in plan['crosswalk']}
        self.assertEqual(set(crosswalk), registered)
        canonical = {r['label'] for r in plan['canonical_categories']}
        self.assertTrue(canonical <= registered)
        self.assertTrue(all(set(r['proposed_labels']) <= canonical for r in plan['crosswalk']))
        self.assertEqual(crosswalk['NA']['proposed_labels'], [])
        self.assertEqual(crosswalk['Microarray']['status'], 'needs curator decision')
        self.assertEqual(crosswalk['proteogenomic features']['status'], 'needs curator decision')
        for label, row in crosswalk.items():
            if label not in canonical:
                self.assertEqual(sum(a['old_label']==label for a in plan['assignments']),row['public_dataset_count'])
        self.assertEqual(len({(a['dataset_type'],a['dataset']) for a in plan['assignments']}),plan['summary']['affected_datasets'])

    def test_species_references_do_not_turn_phantoms_into_biological_taxa(self):
        inventory = {'fields': json.loads(catalog.DEFAULT_DATASET_LABELS.read_text())['fields']}
        catalog.apply_decisions(inventory, catalog.read_json(catalog.DEFAULT_DECISIONS),
                                catalog.read_json(catalog.DEFAULT_REFERENCES))
        species = {r['label']: r for r in inventory['fields']['species']}
        self.assertEqual(species['Human']['reference_links'][0]['code'], 'C14225')
        self.assertEqual(species['Mouse']['reference_links'][0]['code'], 'C14238')
        self.assertEqual(species['Canine']['reference_links'][0]['code'], 'C14201')
        self.assertEqual(species['Physical Phantom']['reference_relation'], 'broader')
        self.assertEqual(species['Computational Phantom']['reference_links'], [])


if __name__ == '__main__':
    unittest.main()
