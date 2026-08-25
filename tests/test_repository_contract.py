import ast
import io
import json
import unittest
from pathlib import Path

import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tcia_proposals.pdf_footer import draw_dsa_footer, replace_dsa_page_number


ROOT = Path(__file__).resolve().parents[1]
HELPER_ROOT = ROOT / "tcia_proposals"
RESOURCES = HELPER_ROOT / "resources"
REVIEW_SKILL = ROOT / "skills" / "review-tcia-dataset-proposal"


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

    def test_generated_dsa_footer_uses_final_page_count(self):
        page_buffer = io.BytesIO()
        page_canvas = canvas.Canvas(page_buffer, pagesize=letter)
        draw_dsa_footer(page_canvas, page_number=6, total_pages=8)
        page_canvas.showPage()
        page_canvas.save()
        page_buffer.seek(0)

        text = PyPDF2.PdfReader(page_buffer).pages[0].extract_text()
        self.assertIn("Page 6 of 8", text)

    def test_template_page_number_overlay_uses_final_page_count(self):
        template_page = PyPDF2.PdfReader(RESOURCES / "agreement_template.pdf").pages[0]
        updated_page = replace_dsa_page_number(
            template_page,
            page_number=1,
            total_pages=8,
        )
        self.assertIn("Page 1 of 8", updated_page.extract_text())

    def test_review_skill_routes_by_role_and_lifecycle(self):
        skill = (REVIEW_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for required_text in (
            "Determine the role and lifecycle stage",
            "submitter or collaborator",
            "TCIA staff or curation-team member",
            "after acceptance while completing publication documentation",
            "Treat a stated role as workflow context, not authentication",
        ):
            self.assertIn(required_text, skill)

    def test_cicadas_guidance_is_progressive_and_source_grounded(self):
        guidance = (REVIEW_SKILL / "references" / "cicadas.md").read_text(encoding="utf-8")
        for required_text in (
            "CICADAS completion is progressive",
            "A complete CICADAS description is not expected",
            "Needs submitter confirmation",
            "Ground every material addition in supplied evidence",
            "does not establish compliance with any journal's requirements",
        ):
            self.assertIn(required_text, guidance)


if __name__ == "__main__":
    unittest.main()
