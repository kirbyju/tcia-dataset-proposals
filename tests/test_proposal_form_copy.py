import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_FORM = ROOT / "tcia-dataset-proposal.py"


class ProposalFormCopyTests(unittest.TestCase):
    def test_poc_fields_request_institutional_email_addresses(self):
        source = PROPOSAL_FORM.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=PROPOSAL_FORM.name)

        labels = None
        institutional_email_help = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "LABELS":
                        labels = ast.literal_eval(node.value)
                    elif isinstance(target, ast.Name) and target.id == "INSTITUTIONAL_EMAIL_HELP":
                        institutional_email_help = ast.literal_eval(node.value)

        self.assertIsNotNone(labels)
        self.assertEqual(
            labels["Scientific POC Email"],
            "Scientific POC Institutional Email*",
        )
        self.assertEqual(
            labels["Technical POC Email"],
            "Technical POC Institutional Email*",
        )
        self.assertEqual(
            labels["Legal POC Email"],
            "Legal POC Institutional Email*",
        )
        self.assertIn("provided by your institution", institutional_email_help)
        self.assertIn("Gmail", institutional_email_help)


if __name__ == "__main__":
    unittest.main()
