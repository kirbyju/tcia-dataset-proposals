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
        catalog.apply_decisions(inventory, catalog.read_json(catalog.DEFAULT_DECISIONS))
        sites = {row["label"]: row for row in inventory["fields"]["disease_location"]}
        diseases = {row["label"]: row for row in inventory["fields"]["disease_type"]}
        self.assertEqual(sites["Thigh"]["reference_links"][0]["code"], "UBERON:0000376")
        self.assertNotIn("Phantom", sites)
        self.assertNotIn("Phantom", diseases)
        self.assertEqual(sites["Not Applicable"]["usage_count"], 0)
        self.assertEqual(sites["Various"]["reference_links"], [])
        self.assertEqual(diseases["Non-Cancer"]["reference_links"], [])
        self.assertEqual(diseases["Gastroesophageal Cancer"]["reference_links"], [])
        combined = diseases["Ewing Sarcoma/Peripheral Primitive Neuroectodermal Tumor"]
        self.assertEqual({link["code"] for link in combined["replacement_links"]}, {"C4817", "C9341"})
        self.assertGreater(combined["usage_count"], 0)  # Preserve actual historical use.
        self.assertTrue(all("api-evsrest" not in link["url"]
                            for field in inventory["fields"].values()
                            for row in field for link in row["reference_links"]))


if __name__ == "__main__":
    unittest.main()
