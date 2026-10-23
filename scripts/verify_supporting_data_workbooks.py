#!/usr/bin/env python3
"""Verify Excel download cells against the guide data without an Excel runtime."""
import argparse
import json
import posixpath
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read_sheets(path):
    with zipfile.ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(e.itertext()) for e in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        result = {}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
            target = rels[sheet.attrib[REL]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            rows = []
            for row in ET.fromstring(z.read(target)).findall(".//m:sheetData/m:row", NS):
                values = {}
                for cell in row:
                    if cell.find("m:f", NS) is not None:
                        raise AssertionError(f"Unexpected formula in teaching data: {sheet.attrib['name']}")
                    col = cell.attrib["r"].rstrip("0123456789")
                    index = 0
                    for c in col:
                        index = index * 26 + ord(c) - 64
                    text = cell.findtext("m:v", "", NS)
                    if cell.attrib.get("t") == "s":
                        text = strings[int(text)]
                    elif cell.attrib.get("t") == "inlineStr":
                        text = "".join(cell.find("m:is", NS).itertext())
                    if text != "":
                        values[index-1] = text
                if values:
                    rows.append((int(row.attrib["r"]), values))
            result[sheet.attrib["name"]] = rows
        return result


def verify(root):
    data = json.loads((root / "guide-data.json").read_text())
    for kind in ["templates", "examples"]:
        sheets = read_sheets(root / "downloads" / f"{kind}.xlsx")
        assert set(sheets) == {t["name"] for t in data["tables"]} | {"Instructions", "Dictionary"}
        for table in data["tables"]:
            actual = dict(sheets[table["name"]])
            expected = [table["columns"]] + (table["rows"] if kind == "examples" else [])
            assert len(actual) == len(expected), (kind, table["name"], "row count")
            for rownum, row in enumerate(expected, 1):
                assert actual[rownum] == {c: str(v) for c, v in enumerate(row) if v != ""}, (kind, table["name"], rownum)
        dictionary = dict(sheets["Dictionary"])
        assert len(dictionary) == len(data["fields"]) + 1
        for rownum, field in enumerate(data["fields"], 2):
            expected = [field["table"], field["name"], field["basis"], field["type"], field["required"], field["description"], field["example"], field["note"], field["source"], "; ".join(f"{t.get('Origin', '')}:{t.get('Code', '')} v{t.get('Version', '')}" for t in field["terms"])]
            assert dictionary[rownum] == {i: str(v) for i, v in enumerate(expected) if v != ""}, (kind, "Dictionary", rownum)
        instruction_rows = dict(sheets["Instructions"])
        paragraphs = (root / "downloads/README.txt").read_text().split("\n\n")
        assert len(instruction_rows) == len(paragraphs) + 1
        for rownum, paragraph in enumerate(paragraphs, 2):
            assert instruction_rows[rownum][1] == paragraph.replace("\n", " "), (kind, "Instructions", rownum)
        print(f"Verified {kind}.xlsx: headers, all example cells, dictionary identities, no formulas")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "docs/supporting-data")
    verify(p.parse_args().root)
