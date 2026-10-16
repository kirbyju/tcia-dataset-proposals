import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dataset_labels", ROOT / "scripts/export_catalog_dataset_labels.py")
labels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(labels)


class DatasetLabelInventoryTests(unittest.TestCase):
    def test_registered_unused_and_exact_public_usage_without_inheritance(self):
        registries = {
            "species": [{"id": 1, "species": "Human"}, {"id": 2, "species": "Mouse"}],
            "program": [{"id": 3, "program_name": "Community"}, {"id": 4, "program_name": "Unused"}],
            "external_resource": [{"id": 5, "external_resources": "Clinical"},
                                  {"id": 6, "external_resources": "Genomics"}],
        }
        record = {"id": 10, "hide_from_browse_table": "No", "collection_short_title": "Example",
                  "url": "https://example.org/collection/", "species": ["Human", "Human"],
                  "program": {"program_name": "Community", "related_collections": ["Unrelated"]},
                  "external_resources": ["Clinical", "Clinical"]}
        hidden = {**record, "id": 11, "hide_from_browse_table": "Yes", "species": ["Mouse"],
                  "external_resources": ["Genomics"], "program": {"program_name": "Unused"}}
        result = labels.assemble(registries, {"collections": [record, hidden]}, [], "2026-10-16")
        self.assertEqual(result["visible_dataset_count"], 1)
        by_field = {f: {r["label"]: r for r in rows} for f, rows in result["fields"].items()}
        self.assertEqual(by_field["species"]["Human"]["usage_count"], 1)
        self.assertEqual(by_field["species"]["Mouse"]["usage_count"], 0)
        self.assertEqual(by_field["program"]["Unused"]["usage_count"], 0)
        self.assertEqual(by_field["external_resource"]["Clinical"]["usage_count"], 1)
        self.assertEqual(by_field["external_resource"]["Genomics"]["registry_membership"], "registered")
        self.assertEqual(by_field["external_resource"]["Genomics"]["examples"], [])

    def test_false_optional_values_are_absent_not_label_strings(self):
        for field in labels.FIELDS:
            self.assertEqual(labels.dataset_values({"program": False, "species": [False],
                                                    "external_resources": [False]}, field), [])


if __name__ == "__main__":
    unittest.main()
