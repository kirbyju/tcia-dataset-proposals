#!/usr/bin/env python3
"""Capture complete public WordPress label registries and current dataset/download usage.

No ontology assignment, WordPress writes, payload transfers, or repository commits.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from export_catalog_dataset_labels import fetch_pages, dataset_values

FIELDS = {
    "disease_type": ("cancer-types", "cancer_type"),
    "disease_location": ("cancer-locations", "cancer_location_label"),
    "data_category": ("download-types", "download_type"),
    "data_type": ("data-types", "data_type"),
    "file_type": ("file-types", "file_type"),
    "species": ("species", "species"),
    "program": ("programs", "program_name"),
    "external_resource": ("supporting-data", "external_resources"),
}
DOWNLOAD_FIELDS = {"data_category": "download type", "data_type": "data type", "file_type": "file type"}


def values(value):
    if value is None or value is False:
        return []
    if not isinstance(value, list):
        raise ValueError("Expected a label array")
    if any(x is not None and x is not False and (not isinstance(x, str) or not x.strip()) for x in value):
        raise ValueError("Invalid value in label array")
    return [x for x in value if isinstance(x, str)]


def assemble(registries, datasets, sources, captured_at):
    usage = {f: defaultdict(dict) for f in FIELDS}
    visible = set()
    downloads_seen = set()
    for endpoint, records in datasets.items():
        for r in records:
            if r.get("hide_from_browse_table") not in ("Yes", "No"):
                raise ValueError("Missing or unknown dataset visibility")
            if r["hide_from_browse_table"] != "No":
                continue
            identity = (endpoint, r["id"])
            visible.add(identity)
            name = r.get("collection_short_title") or r.get("result_short_title")
            if not name or not r.get("url"):
                raise ValueError("Missing public dataset identity")
            example = {"short_title": name, "url": r["url"]}
            for field in FIELDS:
                if field in DOWNLOAD_FIELDS:
                    continue
                if field in ("disease_type", "disease_location"):
                    key = "cancer_types" if field == "disease_type" else "cancer_locations"
                    if key not in r:
                        raise ValueError("Missing disease field")
                    labels = values(r[key])
                else:
                    key = {"species": "species", "program": "program", "external_resource": "external_resources"}[field]
                    if key not in r:
                        raise ValueError("Missing dataset label field")
                    labels = dataset_values(r, field) if field == "program" else values(r[key])
                for label in set(labels):
                    usage[field][label][identity] = example
            # These are the downloads attached to this record's current version.
            # Never use Analysis Result collection_downloads (related source data).
            key = "collection_downloads" if endpoint == "collections" else "result_downloads"
            if key not in r or not isinstance(r[key], list):
                raise ValueError("Missing current download array")
            local_ids = set()
            for download in r[key]:
                if not isinstance(download, dict) or "id" not in download or download["id"] in local_ids:
                    raise ValueError("Malformed or duplicate current download")
                local_ids.add(download["id"])
                did = (endpoint, r["id"], download["id"])
                downloads_seen.add(did)
                for field, source_key in DOWNLOAD_FIELDS.items():
                    if source_key not in download:
                        raise ValueError("Missing download label field")
                    for label in set(values(download[source_key])):
                        usage[field][label][did] = example
    if not visible or not downloads_seen:
        raise ValueError("Empty public dataset/download capture")
    fields = {}
    for field, (_, key) in FIELDS.items():
        registered = {}
        if not registries[field]:
            raise ValueError("Empty registry: " + field)
        for r in registries[field]:
            label = r.get(key)
            if not isinstance(label, str) or not label.strip() or label in registered:
                raise ValueError("Invalid/duplicate registry label: " + field)
            registered[label] = r["id"]
        fields[field] = []
        for label in sorted(set(registered) | set(usage[field]), key=str.casefold):
            examples = sorted(usage[field][label].values(), key=lambda x: x["short_title"].casefold())
            unique = {x["url"]: x for x in examples}
            fields[field].append({"label": label, "usage_count": len(examples),
                "examples": list(unique.values())[:3], "registry_id": registered.get(label),
                "registry_membership": "registered" if label in registered else "absent from complete registry",
                "usage_snapshot_date": captured_at, "semantic_review": "not reviewed"})
    return {"schema_version": "2.0.0", "generated_at_utc": captured_at,
        "wordpress_registered_terms_complete": True, "approved_vocabulary": False,
        "visible_dataset_count": len(visible), "current_download_count": len(downloads_seen),
        "counting_basis": {"disease_fields": "distinct visible datasets per exact label",
            "download_fields": "current download records per exact label, scoped to their dataset"},
        "sources": sources, "fields": fields}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    endpoints = [ep for ep, _ in FIELDS.values()] + ["collections", "analysis-results"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        fetched = dict(zip(endpoints, pool.map(fetch_pages, endpoints)))
    result = assemble({f: fetched[ep][0] for f, (ep, _) in FIELDS.items()},
        {ep: fetched[ep][0] for ep in ("collections", "analysis-results")},
        [s for ep in endpoints for s in fetched[ep][1]], datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, args.output)
    print(json.dumps({"captured_at_utc": result["generated_at_utc"], "visible_datasets": result["visible_dataset_count"],
                      "current_downloads": result["current_download_count"],
                      "registry_sizes": {f: len(rows) for f, rows in result["fields"].items()}}))


if __name__ == "__main__":
    main()
