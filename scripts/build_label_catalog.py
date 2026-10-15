#!/usr/bin/env python3
"""Build the self-contained TCIA observed-label catalog.

The inventory JSON is the only catalog data source. The generated HTML embeds the
inventory, policy, styles, scripts, and the official TCIA logo so it works from
GitHub Pages or as a file opened directly from disk.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "skills/curate-tcia-wordpress-metadata/references/wordpress-label-inventory-2026-10-09.json"
DEFAULT_POLICY = ROOT / "skills/curate-tcia-wordpress-metadata/references/labeling-policy.json"
DEFAULT_TEMPLATE = ROOT / "scripts/label_catalog_template.html"
DEFAULT_LOGO_SVG = ROOT / "skills/curate-tcia-wordpress-metadata/assets/tcia-logo-light.svg"
DEFAULT_MAPPINGS = ROOT / "skills/curate-tcia-wordpress-metadata/references/label-mappings.json"
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


def build(args: argparse.Namespace) -> None:
    inventory = read_json(args.inventory)
    policy = read_json(args.policy)
    validate_inventory(inventory)
    apply_mappings(inventory, read_json(args.mappings))

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
    print(f"Wrote {args.output} ({sum(EXPECTED_FIELDS.values())} observed labels)")


if __name__ == "__main__":
    build(parse_args())
