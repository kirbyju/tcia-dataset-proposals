#!/usr/bin/env python3
"""Build the self-contained TCIA observed-label catalog.

Dated inventory, historical mappings, and confirmed decisions supply the catalog.
The generated HTML embeds data, policy, styles, scripts, and the official TCIA logo so it works from
GitHub Pages or as a file opened directly from disk.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "skills/curate-tcia-wordpress-metadata/references/wordpress-label-inventory-2026-10-09.json"
DEFAULT_POLICY = ROOT / "skills/curate-tcia-wordpress-metadata/references/labeling-policy.json"
DEFAULT_TEMPLATE = ROOT / "scripts/label_catalog_template.html"
DEFAULT_LOGO_SVG = ROOT / "skills/curate-tcia-wordpress-metadata/assets/tcia-logo-light.svg"
DEFAULT_MAPPINGS = ROOT / "skills/curate-tcia-wordpress-metadata/references/label-mappings.json"
DEFAULT_DECISIONS = ROOT / "skills/curate-tcia-wordpress-metadata/references/label-decisions.json"
DEFAULT_REFERENCES = ROOT / "skills/curate-tcia-wordpress-metadata/references/label-reference-links.json"
DEFAULT_OUTPUT = ROOT / "docs/labels/index.html"

EXPECTED_FIELDS = {
    "disease_type": 103,
    "disease_location": 61,
    "data_category": 5,
    "data_type": 52,
    "file_type": 36,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--logo-svg", type=Path, default=DEFAULT_LOGO_SVG)
    parser.add_argument("--mappings", type=Path, default=DEFAULT_MAPPINGS)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--references", type=Path, default=DEFAULT_REFERENCES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def validate_inventory(inventory: dict) -> None:
    fields = inventory.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("Inventory has no fields object")

    if set(fields) != set(EXPECTED_FIELDS):
        raise ValueError(f"Unexpected fields: {sorted(fields)}")

    for field, expected_count in EXPECTED_FIELDS.items():
        rows = fields[field]
        if len(rows) != expected_count:
            raise ValueError(
                f"{field} has {len(rows)} labels; expected {expected_count} for this dated snapshot"
            )
        labels = [row.get("label") for row in rows]
        if len(labels) != len(set(labels)):
            raise ValueError(f"{field} contains duplicate labels")
        for row in rows:
            if not isinstance(row.get("label"), str) or not row["label"].strip():
                raise ValueError(f"{field} contains a blank or invalid label")
            if not isinstance(row.get("usage_count"), int) or row["usage_count"] < 1:
                raise ValueError(f"{field}/{row['label']} has an invalid usage count")
            if not isinstance(row.get("examples"), list):
                raise ValueError(f"{field}/{row['label']} has invalid examples")

    if inventory.get("wordpress_registered_terms_complete") is not False:
        raise ValueError("Catalog must retain the incomplete-registry warning")
    if inventory.get("approved_vocabulary") is not False:
        raise ValueError("Catalog must not claim to be an approved vocabulary")


def official_logo(logo_svg: Path) -> str:
    source = logo_svg.read_bytes()
    if b"<svg" not in source or b"TCIA Logo" not in source:
        raise ValueError("Logo is not the expected official TCIA SVG")
    return "data:image/svg+xml;base64," + base64.b64encode(source).decode("ascii")


def apply_mappings(inventory: dict, mappings: dict) -> None:
    """Join source candidates without turning historical mappings into approval."""
    inventory["mapping_provenance"] = mappings["provenance"]
    for field, rows in inventory["fields"].items():
        for row in rows:
            evidence = mappings.get("fields", {}).get(field, {}).get(row["label"])
            if evidence:
                row.update(evidence)


def safe_script_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def concept_link(ontology: str, code: str, name: str) -> dict:
    if ontology == "UBERON":
        iri = "http://purl.obolibrary.org/obo/" + code.replace(":", "_")
        url = "https://www.ebi.ac.uk/ols4/ontologies/uberon/classes?iri=" + quote(iri, safe="")
    elif ontology == "NCIt":
        url = "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/" + code
    else:
        raise ValueError(f"Unsupported ontology: {ontology}")
    return {"ontology": ontology, "code": code, "preferred_label": name, "url": url}


def apply_decisions(inventory: dict, decisions: dict, references: dict | None = None) -> None:
    """Confirmed decisions override historical candidates, including explicit no-link choices."""
    inventory["label_decisions"] = decisions
    inventory["reference_provenance"] = (references or {}).get("provenance", {})
    for field, rows in inventory["fields"].items():
        field_decisions = decisions.get("fields", {}).get(field, {})
        for label, decision in field_decisions.items():
            if decision.get("decision") == "confirmed" and not any(r["label"] == label for r in rows):
                rows.append({"label": label, "usage_count": 0, "examples": [],
                             "semantic_review": "confirmed concept; usage not observed in dated snapshot"})
        retained = []
        for row in rows:
            decision = field_decisions.get(row["label"])
            reference = (references or {}).get("fields", {}).get(field, {}).get(row["label"])
            row["reference_links"] = []
            row["display_note"] = ""
            if decision:
                if decision["decision"] == "remove from field":
                    continue
                row["confirmed_decision"] = decision
                row["semantic_review"] = decision["decision"]
                row["review_note"] = decision.get("meaning", decision.get("application_rule", ""))
                row["display_note"] = row["review_note"]
                if decision.get("code") and decision.get("url"):
                    row["reference_links"] = [concept_link(decision["ontology"], decision["code"], decision["preferred_label"])]
                elif decision.get("replacements"):
                    row["replacement_links"] = [concept_link(c["ontology"], c["code"], c["display_label"])
                                                for c in decision["replacements"]]
                    row["display_note"] = "Legacy combined label: replace with the supported separate diagnosis label(s)."
            else:
                # A reference link is not dataset-level semantic approval. Only expose
                # active exact-name concepts; aliases/conflicts remain unlinked.
                links = {}
                for candidate in row.get("mapping_candidates", []):
                    for check in candidate.get("ontology_checks", []):
                        if (check.get("active") is True and
                                check.get("preferred_label", "").casefold() == row["label"].casefold()):
                            link = concept_link(candidate["ontology"], check["code"], check["preferred_label"])
                            links[(link["ontology"], link["code"])] = link
                if len(links) == 1:
                    row["reference_links"] = list(links.values())
            # Explicit no-ontology context decisions remain unlinked. Technical
            # verification may complete a user-confirmed meaning without asking
            # the curator to approve routine ID lookups again.
            if reference and not (decision and decision.get("ontology") is None):
                row["reference_links"] = reference["concepts"]
                row["reference_scope"] = reference["scope_note"]
                row["reference_relation"] = reference["mapping_relation"]
                if reference["scope_note"]:
                    row["display_note"] = reference["scope_note"]
            if field.startswith("disease_") and row["label"] == "Various" and not decision:
                row["display_note"] = "Legacy grouping for multiple diseases; no single disease concept. Replace with specific supported labels during curation."
            if field.startswith("disease_") and not row["reference_links"] and not row.get("replacement_links") and not decision:
                if row["label"] != "Various":
                    raise ValueError(f"Missing terminology reference for {field}/{row['label']}")
            if row["usage_count"] == 0:
                row["display_note"] += " No published use in the October 9 snapshot."
            retained.append(row)
        inventory["fields"][field] = sorted(retained, key=lambda r: r["label"].casefold())


def build(args: argparse.Namespace) -> None:
    inventory = read_json(args.inventory)
    policy = read_json(args.policy)
    validate_inventory(inventory)
    apply_mappings(inventory, read_json(args.mappings))
    apply_decisions(inventory, read_json(args.decisions), read_json(args.references))

    template = args.template.read_text(encoding="utf-8")
    replacements = {
        "__CATALOG_JSON__": safe_script_json(inventory),
        "__POLICY_JSON__": safe_script_json(policy),
        "__TCIA_LOGO_DATA_URI__": official_logo(args.logo_svg),
    }
    for token, replacement in replacements.items():
        if template.count(token) != 1:
            raise ValueError(f"Template must contain exactly one {token} token")
        template = template.replace(token, replacement)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(template, encoding="utf-8")
    print(f"Wrote {args.output} ({sum(len(rows) for rows in inventory['fields'].values())} catalog labels)")


if __name__ == "__main__":
    build(parse_args())
