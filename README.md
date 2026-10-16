# TCIA Dataset Proposals

Public tools and Codex skills for preparing TCIA dataset proposals and organizing supporting tabular data.

## Components

### Dataset Proposal Form

`tcia-dataset-proposal.py` is a Streamlit form for proposing either a new primary-data Collection or an Analysis Result derived from existing TCIA data. It collects proposal and institutional-readiness information, generates a proposal package, includes the current Data Submission Agreement, and can optionally email the package to a configured TCIA help desk.

The legal point of contact and DSA are intentionally included early. They encourage submitters to determine whether their institution can authorize publication before the proposal reaches the TCIA Advisory Group.

### Supporting-data remapper

`tcia-remapper.py` is a post-approval Streamlit workflow for collecting missing dataset-level information and mapping supporting clinical or tabular data to the NCI Imaging Submission Model. The model is recommended guidance and is not currently a hard requirement for TCIA submission.

The remapper can import TCIA proposal TSV/ZIP packages or CRDC Data Hub submission-request XLSX files, guide completion of a CICADAS-aligned description, map source columns to model entities, review permissible values, and generate standardized TSV files. Its final artifacts include a CRDC v3.5 workbook populated from the mapped TCIA proposal metadata.

### Proposal review skill

`skills/review-tcia-dataset-proposal/` is a public-facing Codex skill for submitter self-review, TCIA staff review before the AG, and post-acceptance completion of dataset-level narrative documentation. It determines the user's role and lifecycle stage, extracts evidence from supplied materials, summarizes AG and CICADAS coverage when applicable, identifies gaps or ambiguities, and improves supported dataset descriptions without making an approval decision. CICADAS completion is helpful but is not expected before proposal review.

Install that subdirectory as a Codex skill, then upload a generated proposal ZIP or its component files and ask the skill to review the package.

`skills/remap-tcia-supporting-data/` contains the optional post-approval Codex skill. Runtime helpers, schemas, permissible values, and the DSA resource required by the Streamlit applications live separately in `tcia_proposals/`.

### WordPress metadata curation skill

`skills/curate-tcia-wordpress-metadata/` helps curators recommend labels before release from a supplied file or directory, or quality-check a published TCIA Collection or Analysis Result from its page or DOI. It compares dataset and download metadata with the inspected contents, calculates applicable counts and sizes, and harmonizes recommendations with current TCIA usage before consulting NCI Imaging Submission Model or GDC terminology for genuinely new concepts. The skill produces an evidence-backed report and does not edit WordPress.

Its [curator labeling reference](skills/curate-tcia-wordpress-metadata/references/labeling-guide.md) explains NCIt disease mappings, UBERON primary-site checks, and independent category/type/format assignments. It includes a [machine-readable policy](skills/curate-tcia-wordpress-metadata/references/labeling-policy.json), a dated observed vocabulary with counts and provenance, and a [shareable curator graphic](skills/curate-tcia-wordpress-metadata/assets/tcia-labeling-guide.png). Unconfirmed WordPress values require curator review; observed usage is not a complete registered or approved term list. These resources guide curation rather than implementing live validation in the Streamlit applications.

The [interactive observed label catalog](https://kirbyju.github.io/tcia-dataset-proposals/labels/) provides searchable, curator-focused views of all five fields in that dated inventory. The [HTML file](docs/labels/index.html) is self-contained: download it and open it directly from disk for offline use. Rebuild it after updating the inventory or policy with:

```bash
python3 scripts/build_label_catalog.py
```

Confirmed terminology decisions are stored in [`label-decisions.json`](skills/curate-tcia-wordpress-metadata/references/label-decisions.json) and override historical candidates when the catalog is rebuilt. Disease/site labels link directly to human-readable NCIt or UBERON pages. Routine name, synonym, and definition checks are recorded in [`label-reference-links.json`](skills/curate-tcia-wordpress-metadata/references/label-reference-links.json), including API response hashes. TCIA labels display as plain text with only the concept identifiers hyperlinked. Broad or combined reference scope notes remain in the spreadsheet export. Only Non-Cancer and Various remain intentionally unlinked as TCIA context/grouping labels. Retired `Phantom` options are hidden; `Not Applicable` is included with zero observed uses in the October 9 snapshot. The combined Ewing/pPNET label retains its historical count and shows links to the two proposed replacement labels until WordPress is updated and usage is refreshed. Counts remain dated evidence, not a claim that pending curator updates were applied.

The catalog's **Export spreadsheet (.csv)** button downloads all five fields, including usage counts, displayed ontology URLs, confirmed decisions, and historical mapping evidence. CSV opens in Excel or other spreadsheet applications. The export always includes the complete catalog, regardless of the current search/filter.

Historical mapping evidence is stored separately in `skills/curate-tcia-wordpress-metadata/references/label-mappings.json`. To refresh it, download the referenced public Google Sheet as XLSX, then run `.venv/bin/python scripts/import_label_mappings.py --workbook /path/to/source.xlsx --verify` and rebuild the HTML. The importer uses direct source labels or explicit crosswalks; it does not infer fuzzy matches or treat the source's AI recommendations as curator approval. Ontology lookup failures remain visible as `unable to verify`.

GitHub Pages publishes the `/docs` folder on `main` through the [Publish curator label catalog](.github/workflows/pages.yml) Actions workflow. The Pages publishing source must be **GitHub Actions** in the repository settings. The workflow verifies that the generated HTML matches its source data before uploading and deploying it. Push the regenerated HTML with its source changes to `main`, or run the workflow manually to redeploy; stale generated HTML fails the build rather than silently publishing old labels.

## Run locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run tcia-dataset-proposal.py
```

Run the post-approval remapper with:

```bash
streamlit run tcia-remapper.py
```

## Optional email submission

Package generation works without SMTP configuration. To enable direct submission from a deployed proposal form, configure:

- `SMTP_SERVER`
- `SMTP_PORT` (defaults to `587`)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `TCIA_HELP_DESK_EMAIL` (defaults to `help@cancerimagingarchive.net`)

Keep credentials in the deployment environment or Streamlit secret-management layer. Never commit them to this repository.

## Proposal guidance

- [TCIA Advisory Group Charter](https://www.cancerimagingarchive.net/tcia-advisory-group-charter/)
- [CICADAS](https://www.cancerimagingarchive.net/cancer-imaging-checklist-for-data-sharing-cicadas/)
- [Primary Data submissions](https://www.cancerimagingarchive.net/primary-data/)
- [Analysis Results submissions](https://www.cancerimagingarchive.net/analysis-results/)
- [Submission and de-identification overview](https://www.cancerimagingarchive.net/submission-and-de-identification-overview/)

Do not upload patient-level data or protected health information when requesting a proposal review. Data curation and de-identification use separate approved workflows.

## License

Apache License 2.0. See `LICENSE`.
