#!/usr/bin/env python3
"""Read public WordPress registries and dataset usage for the extra catalog fields."""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

API = "https://www.cancerimagingarchive.net/api/v2"
FIELDS = {"species": ("species", "species"), "program": ("programs", "program_name"),
          "external_resource": ("supporting-data", "external_resources")}


def fetch_pages(endpoint):
    evidence = []
    def fetch(page):
        url = f"{API}/{endpoint}?per_page=100&page={page}"
        with urlopen(url, timeout=45) as response:
            payload = response.read()
        data = json.loads(payload)
        assert data["page"] == page and isinstance(data["results"], list)
        return data, {"url": url, "sha256": hashlib.sha256(payload).hexdigest(),
                      "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                      "row_count": len(data["results"])}
    first, source = fetch(1)
    evidence.append(source)
    rows = list(first["results"])
    if first["total_pages"] > 1:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for data, source in pool.map(fetch, range(2, first["total_pages"] + 1)):
                assert data["total"] == first["total"], "Pagination changed during capture"
                rows.extend(data["results"])
                evidence.append(source)
    assert len(rows) == first["total"]
    assert len({r["id"] for r in rows}) == len(rows), "Duplicate records across pages"
    return rows, evidence


def dataset_values(row, field):
    if field == "program":
        program = row.get("program")
        value = program.get("program_name") if isinstance(program, dict) else program
        return [value] if isinstance(value, str) and value.strip() else []
    value = row.get("species" if field == "species" else "external_resources")
    if value in (None, False):
        return []
    if not isinstance(value, list):
        raise ValueError(f"Unexpected {field} shape")
    return [v for v in value if isinstance(v, str) and v.strip()]


def assemble(registries, datasets, sources, captured_at):
    usage = {field: defaultdict(dict) for field in FIELDS}
    visible = set()
    for endpoint, rows in datasets.items():
        for row in rows:
            if row.get("hide_from_browse_table") != "No":
                continue
            identity = (endpoint, row["id"])
            visible.add(identity)
            name = row.get("collection_short_title") or row.get("result_short_title")
            assert name and row.get("url")
            for field in FIELDS:
                for label in set(dataset_values(row, field)):
                    usage[field][label][identity] = {"short_title": name, "url": row["url"]}
    fields = {}
    for field, (_, registry_key) in FIELDS.items():
        registered = {}
        for row in registries[field]:
            label = row.get(registry_key)
            if not isinstance(label, str) or not label.strip():
                raise ValueError(f"Registry row lacks {registry_key}: {row['id']}")
            if label in registered:
                raise ValueError(f"Duplicate registry label: {label}")
            registered[label] = row["id"]
        fields[field] = []
        for label in sorted(set(registered) | set(usage[field]), key=str.casefold):
            examples = sorted(usage[field].get(label, {}).values(), key=lambda x: x["short_title"].casefold())
            fields[field].append({"label": label, "usage_count": len(examples), "examples": examples[:3],
                "semantic_review": "not reviewed", "registry_id": registered.get(label),
                "registry_membership": "registered" if label in registered else "absent from complete registry",
                "usage_snapshot_date": captured_at, "registry_checked_at_utc": captured_at})
    return {"schema_version": "1.0.0", "generated_at_utc": captured_at,
        "scope": "Complete public species/program/supporting-data registries plus exact-label usage in visible public Collections and Analysis Results. Zero means no visible public use, not absence from private records.",
        "counting_basis": "distinct visible datasets per exact label; repeated values count once per dataset; no inherited program membership or inferred external resources",
        "api_field_names": {"species": "species", "program": "program.program_name", "external_resource": "external_resources"},
        "normalized_query_api_alias": {"external_resource": "external_resource_labels"},
        "visible_dataset_count": len(visible), "sources": sources, "fields": fields}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    jobs = [ep for ep, _ in FIELDS.values()] + ["collections", "analysis-results"]
    with ThreadPoolExecutor(max_workers=5) as pool:
        fetched = dict(zip(jobs, pool.map(fetch_pages, jobs)))
    result = assemble({f: fetched[ep][0] for f, (ep, _) in FIELDS.items()},
                      {ep: fetched[ep][0] for ep in ["collections", "analysis-results"]},
                      [e for ep in jobs for e in fetched[ep][1]], datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"fields": {f: len(rows) for f, rows in result["fields"].items()},
                      "visible_dataset_count": result["visible_dataset_count"]}))


if __name__ == "__main__":
    main()
