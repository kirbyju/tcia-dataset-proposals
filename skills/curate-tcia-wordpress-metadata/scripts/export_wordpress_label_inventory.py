#!/usr/bin/env python3
"""Export observed public label usage from an already-installed TCIA V2 bundle.

This is an evidence inventory, not an approved vocabulary or a WordPress term
registry. No network calls, patient data, or WordPress changes are involved.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3


def export(bundle):
    bundle = bundle.resolve()
    manifest_path = bundle / "tcia_metadata_v2_bundle_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    database = bundle / "tcia_snapshot.sqlite"
    expected = manifest["components"]["snapshot"]["sqlite_sha256"]
    digest = hashlib.sha256()
    with database.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected:
        raise ValueError("Snapshot SHA-256 does not match bundle manifest")
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as conn:
        if conn.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("Snapshot SQLite quick_check failed")
        if conn.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Snapshot foreign_key_check failed")
        fields = {k: defaultdict(set) for k in (
            "disease_type", "disease_location", "data_category", "data_type", "file_type")}
        datasets = {}
        for source, ident, raw in conn.execute(
            "SELECT source,id,normalized_json FROM wordpress_records "
            "WHERE hidden=0 AND source IN ('collections','analysis-results')"
        ):
            row = json.loads(raw)
            key = (source, ident)
            datasets[key] = {"short_title": row["short_title"], "url": row["link"]}
            for field, wp_field in (("disease_type", "cancer_types"),
                                    ("disease_location", "cancer_locations")):
                # Normalized dataset fields use semicolons; retain commas in labels.
                for label in set(x.strip() for x in (row.get(wp_field) or "").split(";")) - {""}:
                    fields[field][label].add(key)
        downloads = {}
        kinds = {"download_type": "data_category", "data_type": "data_type", "file_type": "file_type"}
        for rid, source, ident, title, kind, label in conn.execute(
            "SELECT d.download_row_id,d.parent_source,d.parent_id,d.download_title,l.label_kind,l.label "
            "FROM wordpress_downloads d JOIN wordpress_download_labels l USING(download_row_id) "
            "WHERE d.parent_hidden=0 AND d.is_current_version=1"
        ):
            if kind not in kinds or (source, ident) not in datasets:
                continue
            downloads[rid] = {**datasets[(source, ident)], "download_title": title}
            fields[kinds[kind]][label].add(rid)
        result = {}
        for field, values in fields.items():
            lookup = datasets if field.startswith("disease_") else downloads
            result[field] = [
                {"label": label, "usage_count": len(ids),
                 "examples": [lookup[i] for i in sorted(ids)[:3]],
                 "semantic_review": "not reviewed", "ontology_mapping": None}
                for label, ids in sorted(values.items(), key=lambda x: x[0].casefold())
            ]
    return {
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalog_kind": "observed published usage",
        "approved_vocabulary": False,
        "wordpress_registered_terms_complete": False,
        "latest_release_verified": False,
        "scope": "Visible Collections and Analysis Results; current downloads only; unused registered terms absent",
        "counting_basis": {"disease_fields": "distinct datasets per label",
                           "download_fields": "distinct download rows per label; multi-label counts overlap"},
        "provenance": {
            "bundle_generated_at_utc": manifest["generated_at_utc"],
            "release_fingerprint": manifest["release_fingerprint"],
            "snapshot_sqlite_sha256": expected,
            "bundle_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "local_checks": ["SHA-256 matches manifest", "SQLite quick_check", "SQLite foreign_key_check"],
            "visible_dataset_count": len(datasets)},
        "fields": result,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = export(args.bundle)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "distinct_labels": {
        field: len(values) for field, values in result["fields"].items()}}))
