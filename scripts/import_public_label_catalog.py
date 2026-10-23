#!/usr/bin/env python3
"""Import a captured public catalog without discarding its provenance or reviewed links."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def import_catalog(html_path, output):
    html = Path(html_path).read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>', html, re.S)
    if not match:
        raise ValueError("No embedded catalog found")
    catalog = json.loads(match.group(1))
    required = {"disease_type", "disease_location", "species", "data_category", "data_type", "file_type", "program", "external_resource"}
    if catalog.get("wordpress_registered_terms_complete") is not True or set(catalog.get("fields", {})) != required:
        raise ValueError("A complete eight-field public registry capture is required")
    if catalog.get("approved_vocabulary") is not False or not catalog.get("sources") or not catalog.get("generated_at_utc"):
        raise ValueError("Catalog must retain provenance and distinguish registry membership from approval")
    for field, rows in catalog["fields"].items():
        labels = [row["label"] for row in rows]
        if not labels or len(labels) != len(set(labels)):
            raise ValueError(f"Empty or duplicate labels in {field}")
    output = Path(output)
    if output.exists():
        previous = json.loads(output.read_text(encoding="utf-8"))
        if catalog["generated_at_utc"] < previous["generated_at_utc"]:
            raise ValueError("Refusing to replace the catalog with an older capture")
    output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "tcia_proposals/resources/label_catalog.json")
    args = parser.parse_args()
    import_catalog(args.html, args.output)
