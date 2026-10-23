#!/usr/bin/env python3
"""Build the submitter guide, field dictionary and teaching TSVs from pinned sources.

No network or Streamlit dependencies. Excel files are authored separately with
build_supporting_data_workbooks.mjs using the same generated guide-data.json.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/supporting_data"
OUTPUT = ROOT / "docs/supporting-data"
KEYS = {
    "program": "program_id", "dataset": "dataset_id", "subject": "subject_id",
    "procedure": "procedure_id", "diagnosis": "diagnosis_id", "file": "file_id",
    "radiology": "radiology_id", "histopathology": "histopathology_id",
    "multiplex_imaging": "multiplex_image_id", "multiplex_channels": "channel_id",
    "investigator": "investigator_id", "related_work": "related_work_id",
}
PURPOSES = {
    "program": "The program or initiative associated with the dataset.",
    "dataset": "One row describing the dataset.",
    "subject": "One row per de-identified subject within this dataset.",
    "procedure": "One row per examination, procedure or laboratory observation. A subject can have multiple procedures.",
    "diagnosis": "One row per diagnosis record linked to the relevant procedure.",
    "file": "One row per submitted file, linked to its procedure and applicable imaging metadata. Populate only the imaging links that apply.",
    "radiology": "One row per radiology acquisition or image grouping. Multiple files can share acquisition metadata.",
    "histopathology": "One row per applicable histopathology metadata record.",
    "multiplex_imaging": "One row per multiplex imaging metadata record.",
    "multiplex_channels": "One row per channel. The pinned model links multiplex imaging to channels; discuss multi-channel packaging with your curator.",
    "investigator": "One row per contributing investigator.",
    "related_work": "One row per related publication or resource.",
}


def read(name):
    return json.loads((SOURCE / name).read_text())


def tsv(headers, rows):
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, delimiter="\t", lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue()


def sample_records():
    """Intentionally partial fictional teaching records, never a submission assertion."""
    return {
        "program": [{"program_id": "PROG-DEMO", "program_name": "Community", "program_short_name": "Community"}],
        "dataset": [{"dataset_id": "DATA-DEMO", "dataset_short_name": "Fictional-example", "dataset_long_name": "Fictional supporting-data preparation example", "dataset_abstract": "Fictional teaching records showing subject, procedure and file relationships.", "dataset_description": "All records and acquisition settings in this example are invented for instruction.", "program.program_id": "PROG-DEMO"}],
        "subject": [{"subject_id": "SUBJ-001", "sex_at_birth": "Female", "dataset.dataset_id": "DATA-DEMO"}],
        "procedure": [{"procedure_id": name, "image_modality": modality, "subject.subject_id": "SUBJ-001"} for name, modality in [("PROC-MR", "MR"), ("PROC-CT", "CT"), ("PROC-PET", "PT"), ("PROC-SLIDE", "SM")]],
        "diagnosis": [{"diagnosis_id": "DX-001", "primary_diagnosis": "Lung Adenocarcinoma", "primary_site": "Lung", "procedure.procedure_id": "PROC-CT"}],
        "radiology": [{"radiology_id": f"RAD-{mod}", "modality": code, "body_part_examined": body, "series_description": desc, "pixel_spacing_row": spacing, "slice_thickness": thickness} for mod, code, body, desc, spacing, thickness in [("MR", "MR", "BRAIN", "Fictional baseline T1 acquisition", "0.8\\0.8", "1"), ("CT", "CT", "CHEST", "Fictional chest CT", "0.8\\0.8", "1"), ("PET", "PT", "CHEST", "Fictional PET acquisition", "4\\4", "4")]],
        "histopathology": [{"histopathology_id": "HIST-001", "nominal_magnification": "40"}],
        "file": [
            {"file_name": "images/SUBJ-001_baseline_T1.nii.gz", "file_type": "NIfTI", "file_description": "Fictional MR volume; source acquisition resampled for submission", "procedure.procedure_id": "PROC-MR", "radiology.radiology_id": "RAD-MR"},
            {"file_name": "images/SUBJ-001_chest_CT.nii.gz", "file_type": "NIfTI", "file_description": "Fictional CT volume", "procedure.procedure_id": "PROC-CT", "radiology.radiology_id": "RAD-CT"},
            {"file_name": "images/SUBJ-001_PET.nii.gz", "file_type": "NIfTI", "file_description": "Fictional PET volume", "procedure.procedure_id": "PROC-PET", "radiology.radiology_id": "RAD-PET"},
            {"file_name": "slides/SUBJ-001_slide.tiff", "file_type": "TIFF", "file_description": "Fictional slide image", "procedure.procedure_id": "PROC-SLIDE", "histopathology.histopathology_id": "HIST-001"},
            {"file_name": "annotations/SUBJ-001_target.nii.gz", "file_type": "NIfTI", "file_description": "Fictional label map in the submitted MR grid", "procedure.procedure_id": "PROC-MR", "radiology.radiology_id": "RAD-MR"},
        ],
    }


def build_data():
    snapshot, idc, guidance = (read(n) for n in ["model_snapshot.json", "idc_snapshot.json", "guidance.json"])
    model, definitions = snapshot["model"], snapshot["properties"]
    fields, tables = [], []
    examples = sample_records()
    for node, info in model["Nodes"].items():
        columns = []
        for name in info["Props"]:
            prop = definitions[name]
            terms = prop.get("Term", [])
            key = f"{node}.{name}"
            item = dict(table=node, name=name, basis="model", type=prop.get("Type", "text"),
                        description=prop.get("Desc") or next((t.get("Definition") for t in terms if t.get("Definition")), "Identifier within this dataset; coordinate assignment with your curator."),
                        required="Required by model" if prop.get("Req") in ("Yes", True) else "Optional in model",
                        values=prop.get("Enum", []), terms=terms,
                        note=guidance["field_notes"].get(key, ""),
                        source=f'{snapshot["repository"]}/blob/{snapshot["commit"]}/model-desc/nci_imaging_submission_model_properties.yml',
                        example=next((r[name] for r in examples.get(node, []) if r.get(name) is not None), ""))
            fields.append(item); columns.append(name)
        for rel in model["Relationships"].values():
            for end in rel["Ends"]:
                if end["Src"] == node:
                    dst = end["Dst"]
                    name = f"{dst}.{KEYS[dst]}"
                    columns.append(name)
                    fields.append(dict(table=node, name=name, basis="relationship", type="text", required="Link when applicable", values=[], terms=[],
                        description=f"Link to {KEYS[dst]} in {dst}.tsv. Use the exact same identifier.",
                        note="Relationship-derived template column, following the remapper's dot-notation convention. It is not a standalone MDF property.",
                        source=f'{snapshot["repository"]}/blob/{snapshot["commit"]}/model-desc/nci_imaging_submission_model.yml',
                        example=next((r[name] for r in examples.get(node, []) if name in r), "")))
        tables.append(dict(name=node, title=node.replace("_", " ").capitalize(), basis="model", description=PURPOSES[node], columns=columns,
                           rows=[[r.get(c, "") for c in columns] for r in examples.get(node, [])]))
    files = {"ct_acquisition": "images/SUBJ-001_chest_CT.nii.gz", "pet_acquisition": "images/SUBJ-001_PET.nii.gz", "slide_details": "slides/SUBJ-001_slide.tiff", "annotation_details": "annotations/SUBJ-001_target.nii.gz"}
    for name, table in guidance["additional_tables"].items():
        columns, row = ["file.file_name"], [files.get(name, "images/SUBJ-001_baseline_T1.nii.gz")]
        fields.append(dict(table=name, name="file.file_name", basis="additional", type="text", required="Recommended linkage", values=[], terms=[],
            description="Exact relative path from file.tsv. Scope the filename to this dataset and keep spelling and case consistent.", note="Recommended table linkage; not an MDF model field.", source="", example=row[0]))
        for spec in table["fields"]:
            if isinstance(spec, str):
                original = next(c for c in idc["tables"][table["idc_table"]] if c["name"] == spec)
                description = original.get("description") or spec.replace("_", " ")
                # Index aggregation is a provenance fact, not an instruction to submitters.
                desc = description.split("; aggregated")[0].split("; constant across")[0]
                dtype = original["type"].lower()
                if original["mode"] == "REPEATED":
                    dtype = f"JSON array of {dtype}"
                example = guidance["idc_examples"].get(spec, "")
                source = idc["reference"] + "#" + table["idc_table"].replace("_", "-")
                note = f'Concept aligned with {table["idc_table"]}.{spec}. IDC schemas describe DICOM series/instances; these preparation tables link to submitted files. Preserve units and per-file meaning. This is not a model extension accepted automatically by the validator.'
                if spec in ["PixelSpacing_row_mm", "PixelSpacing_col_mm"]:
                    note += " Report source acquisition spacing; submitted-file spacing belongs in image_context."
                if spec == "PixelSpacing_0":
                    note += " In mm: 0.00025 mm equals 0.25 micrometres."
            else:
                spec, dtype, desc, example = spec
                source = idc["reference"] + "#seg-index" if name == "annotation_details" else ""
                note = "Recommended preparation field outside the current MDF model."
            columns.append(spec); row.append(example)
            fields.append(dict(table=name, name=spec, basis="additional", type=dtype, required="Recommended when applicable", values=[], terms=[], description=desc, note=note, source=source, example=example))
        tables.append(dict(name=name, title=table["title"], basis="additional", description=table["description"], columns=columns, rows=[row]))
    for f in fields:
        if len(f["values"]) == 0:
            f["values_note"] = "No permissible-value list is enumerated in this pinned source. Ask your curator or use the validator's supported value guidance."
    return dict(model={k: snapshot[k] for k in ["repository", "commit", "retrieved_on", "sha256"]}, version=model["Version"],
                idc={k: v for k, v in idc.items() if k != "tables"}, reviewed_on=guidance["reviewed_on"],
                validator_url=guidance["validator_url"], fields=fields, tables=tables)


def readme(data):
    return f"""TCIA supporting-data preparation materials

Use templates when practical. If you already have spreadsheets, the remapping tool
can help align them with the recommended model: {data['validator_url']}

These are recommended preparation materials, not a mandatory submission format.
Use only the tables relevant to your dataset. All example records are fictional.
Examples are partial teaching records, not a validated or complete submission.
No image files are included. Blank cells mean values were not supplied in the
example; they are not zero or a prescribed missing-value code. Discuss unknown,
not collected and not applicable values with your curator; preserve distinctions.

Model tables follow NCI Imaging Submission Model {data['version']}, commit
{data['model']['commit']}. Dot-notation columns express model relationships.
They follow the existing remapper's template convention, not MDF property names.
The remapper's deployed schema may differ. These downloads are preparation
templates, not a guarantee of direct import into the deployed validator.
file_id is assigned by the CRDC Submission Portal per upstream documentation;
it is left blank here. Discuss identifier assignment with your curator.

Additional recommended imaging tables are outside the current MDF model and
are not automatically supported by the validator. They use file.file_name to
link to exact relative paths in file.tsv, scoped to the same dataset. Keep paths
unique within a dataset. annotation_details has one row per region/group;
other additional tables have one row per submitted file or image volume.
Report source acquisition metadata separately from submitted image properties.
Use JSON arrays for repeated fields, for example [2.5, 5.0]. Preserve pairing
and ordering in source records when needed; distinct-value lists are not a
per-frame or per-voxel mapping. Do not infer acquisition settings from appearance.
Pixel/voxel spacing and nominal slice thickness are different measurements.
Do not invent DICOM UIDs for non-DICOM files.

The Excel workbooks contain these same columns. Each data sheet has its header
in row 1. The Instructions and Dictionary sheets are reference material.
Blank templates contain no example data; copy only relevant sheets into your
working package. Keep one observation per row and one variable per column.

Consult your data curator about how to provide additional data points you have
collected. Supply patient-level information only through the curation workflow
agreed with TCIA, using permitted de-identified identifiers and dates.

Sources: {data['model']['repository']}
{data['idc']['reference']}
IDC source snapshot: idc-index {data['idc']['idc_index_version']},
idc-index-data {data['idc']['idc_index_data_version']}, {data['idc']['idc_data_version']}.
Reviewed: {data['reviewed_on']}.
Model definitions are reproduced from the Apache-2.0 licensed upstream project.
"""


def build(output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    downloads = output / "downloads"
    downloads.mkdir(exist_ok=True)
    data = build_data()
    (output / "guide-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    instructions = readme(data)
    (downloads / "README.txt").write_text(instructions)
    dictionary_headers = ["table", "field", "basis", "type", "expectation", "description", "example", "notes", "source", "caDSR_references"]
    dictionary_rows = [[f["table"], f["name"], f["basis"], f["type"], f["required"], f["description"], f["example"], f["note"], f["source"], "; ".join(f"{t.get('Origin', '')}:{t.get('Code', '')} v{t.get('Version', '')}" for t in f["terms"])] for f in data["fields"]]
    dictionary = tsv(dictionary_headers, dictionary_rows)
    (downloads / "field-dictionary.tsv").write_text(dictionary)
    for kind in ["templates", "examples"]:
        # Fixed ZIP timestamps make builds reproducible.
        with zipfile.ZipFile(downloads / f"{kind}.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
            def add(name, content):
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 18, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, content.encode())
            add("README.txt", instructions)
            add("field-dictionary.tsv", dictionary)
            for table in data["tables"]:
                group = "model" if table["basis"] == "model" else "additional-recommended"
                add(f"{group}/{table['name']}.tsv", tsv(table["columns"], table["rows"] if kind == "examples" else []))
    logo = (ROOT / "skills/curate-tcia-wordpress-metadata/assets/tcia-logo-light.svg").read_bytes()
    html = (SOURCE / "template.html").read_text()
    html = html.replace("__LOGO__", "data:image/svg+xml;base64," + base64.b64encode(logo).decode())
    html = html.replace("__GUIDE_DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c"))
    (output / "index.html").write_text(html)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.glob("*.json"))}
    (output / "source-manifest.json").write_text(json.dumps(hashes, indent=2) + "\n")
    print(f"Built {len(data['fields'])} fields and {len(data['tables'])} tables in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    build(parser.parse_args().output)
