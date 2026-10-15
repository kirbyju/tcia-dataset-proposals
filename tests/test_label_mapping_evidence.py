import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("label_mapping_import", ROOT / "scripts/import_label_mappings.py")
mapping_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping_import)


class MappingEvidenceTests(unittest.TestCase):
    def test_historical_codes_and_ai_recommendations_do_not_become_approval(self):
        def sheet(rows):
            return SimpleNamespace(iter_rows=lambda **_: iter(rows))
        book = {
            "Primary Diagnosis": sheet([("C123", "Example Disease", "Source definition")]),
            "Anatomic Site": sheet([("thigh", "Source anatomy definition", "iri", "UBERON:0004463")]),
            "Primary Site Mappings for legac": sheet([("Various", None, None, "No Match Found (IRI API)")]),
            "Updated AI legacy comparison": sheet([("ID_DIFFERENT", "Thigh", 1, "accepted", "single",
                "UBERON:0000376", None, "hindlimb stylopod", None, None, None, None, "Different source IDs; review.")]),
        }
        inventory = {"fields": {
            "disease_type": [{"label": "EXAMPLE DISEASE"}, {"label": "Example Disease NOS"}],
            "disease_location": [{"label": "Thigh"}, {"label": "Various"}],
        }}
        result = mapping_import.read_candidates(book, inventory)
        disease = result["disease_type"]["EXAMPLE DISEASE"]
        self.assertEqual(disease["mapping_candidates"][0]["codes"], ["C123"])
        self.assertEqual(disease["semantic_review"], "needs curator decision")
        self.assertEqual(result["disease_type"]["Example Disease NOS"]["mapping_candidates"], [])
        thigh = result["disease_location"]["Thigh"]
        self.assertEqual(thigh["mapping_candidates"][0]["codes"], ["UBERON:0004463"])
        self.assertEqual(thigh["legacy_comparison"]["recommended_code"], "UBERON:0000376")
        self.assertEqual(thigh["semantic_review"], "needs curator decision")
        self.assertEqual(result["disease_location"]["Various"]["mapping_candidates"][0]["codes"], [])


if __name__ == "__main__":
    unittest.main()
