import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("supporting_guide", ROOT / "scripts/build_supporting_data_guide.py")
guide = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guide)


class SupportingDataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = guide.build_data()
        cls.tables = {t["name"]: t for t in cls.data["tables"]}

    def test_additional_guidance_does_not_become_model_properties(self):
        model = guide.read("model_snapshot.json")["model"]
        for f in self.data["fields"]:
            if f["basis"] == "model":
                self.assertIn(f["name"], model["Nodes"][f["table"]]["Props"])
            elif f["basis"] == "additional":
                self.assertNotIn(f["table"], model["Nodes"])
        self.assertTrue(any(f["name"] == "EchoTime" and f["basis"] == "additional" for f in self.data["fields"]))

    def test_all_teaching_links_resolve_within_the_dataset(self):
        for table in self.data["tables"]:
            for row in table["rows"]:
                for column, value in zip(table["columns"], row):
                    if "." not in column or value == "":
                        continue
                    target, field = column.split(".", 1)
                    target_table = self.tables[target]
                    values = {r[target_table["columns"].index(field)] for r in target_table["rows"]}
                    self.assertIn(value, values, (table["name"], column, value))
        annotation = self.tables["annotation_details"]
        source = annotation["rows"][0][annotation["columns"].index("source_file_name")]
        files = self.tables["file"]
        self.assertIn(source, [r[files["columns"].index("file_name")] for r in files["rows"]])

    def test_source_and_processed_spacing_are_distinct(self):
        context, mr = self.tables["image_context"], self.tables["mr_acquisition"]
        submitted = json.loads(context["rows"][0][context["columns"].index("submitted_spacing_mm")])
        acquisition = mr["rows"][0][mr["columns"].index("PixelSpacing_row_mm")]
        self.assertNotEqual(submitted[0], acquisition)
        spacing = next(f for f in self.data["fields"] if f["table"] == "mr_acquisition" and f["name"] == "PixelSpacing_row_mm")
        self.assertIn("source acquisition", spacing["note"])

    def test_repeated_values_keep_their_array_representation(self):
        for f in self.data["fields"]:
            if f["type"].startswith("JSON array") and f["example"] != "":
                self.assertIsInstance(json.loads(f["example"]), list)

    def test_downloads_have_no_invented_portal_identifiers(self):
        files = self.tables["file"]
        self.assertTrue(all(row[files["columns"].index("file_id")] == "" for row in files["rows"]))
        self.assertIn("partial teaching records", guide.readme(self.data))


if __name__ == "__main__":
    unittest.main()
