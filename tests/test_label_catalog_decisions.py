import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("label_catalog", ROOT / "scripts/build_label_catalog.py")
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogDecisionTests(unittest.TestCase):
    def test_confirmed_override_and_no_link_decisions_precede_historical_candidates(self):
        inventory = catalog.read_json(catalog.DEFAULT_INVENTORY)
        catalog.apply_mappings(inventory, catalog.read_json(catalog.DEFAULT_MAPPINGS))
        catalog.apply_decisions(inventory, catalog.read_json(catalog.DEFAULT_DECISIONS),
                                catalog.read_json(catalog.DEFAULT_REFERENCES))
        sites = {row["label"]: row for row in inventory["fields"]["disease_location"]}
        diseases = {row["label"]: row for row in inventory["fields"]["disease_type"]}
        self.assertEqual(sites["Thigh"]["reference_links"][0]["code"], "UBERON:0000376")
        self.assertNotIn("Phantom", sites)
        self.assertNotIn("Phantom", diseases)
        self.assertEqual(sites["Not Applicable"]["usage_count"], 0)
        self.assertEqual(sites["Various"]["reference_links"], [])
        self.assertEqual(diseases["Non-Cancer"]["reference_links"], [])
        self.assertEqual({link["code"] for link in diseases["Gastroesophageal Cancer"]["reference_links"]},
                         {"C9331", "C7478"})
        self.assertEqual(diseases["Neuroendocrine Tumors (all sites)"]["reference_links"][0]["code"], "C3809")
        self.assertEqual({link["code"] for link in diseases["HER2+ Breast Cancer"]["reference_links"]},
                         {"C9335", "C68748"})  # Do not impose the ER-negative subtype definition.
        combined = diseases["Ewing Sarcoma/Peripheral Primitive Neuroectodermal Tumor"]
        self.assertEqual({link["code"] for link in combined["replacement_links"]}, {"C4817", "C9341"})
        self.assertGreater(combined["usage_count"], 0)  # Preserve actual historical use.
        self.assertTrue(all("api-evsrest" not in link["url"]
                            for field in inventory["fields"].values()
                            for row in field for link in row["reference_links"]))
        for field in ("disease_type", "disease_location"):
            unlinked = {row["label"] for row in inventory["fields"][field]
                        if not row["reference_links"] and not row.get("replacement_links")}
            expected = {"Various", "Non-Cancer"} if field == "disease_type" else {"Various"}
            self.assertEqual(unlinked, expected)

    def test_missing_routine_reference_fails_build_instead_of_publishing_placeholders(self):
        inventory = {"fields": {"disease_type": [{"label": "Unmapped condition", "usage_count": 1,
                                                 "examples": []}]}}
        with self.assertRaisesRegex(ValueError, "Missing terminology reference"):
            catalog.apply_decisions(inventory, {"fields": {}})


if __name__ == "__main__":
    unittest.main()
