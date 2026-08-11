import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER_ROOT = ROOT / "tcia-remapping-skill"
RESOURCES = HELPER_ROOT / "resources"


class RepositoryContractTests(unittest.TestCase):
    def test_entrypoints_parse(self):
        for name in ("tcia-dataset-proposal.py", "tcia-remapper.py"):
            source = (ROOT / name).read_text(encoding="utf-8")
            ast.parse(source, filename=name)

    def test_required_helpers_exist(self):
        for name in ("mdf_parser.py", "orcid_helper.py", "remap_helper.py"):
            self.assertTrue((HELPER_ROOT / name).is_file(), name)

    def test_required_resources_exist(self):
        expected = (
            "schema.json",
            "permissible_values.json",
            "agreement_template.pdf",
            "model/nci_imaging_submission_model.yml",
            "model/nci_imaging_submission_model_properties.yml",
            "model/nci_imaging_submission_model_terms.yml",
        )
        for name in expected:
            self.assertTrue((RESOURCES / name).is_file(), name)

    def test_json_resources_are_valid(self):
        for name in ("schema.json", "permissible_values.json"):
            with (RESOURCES / name).open(encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)

    def test_dsa_resource_is_pdf(self):
        self.assertTrue((RESOURCES / "agreement_template.pdf").read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
