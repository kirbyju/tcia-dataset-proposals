# TCIA Dataset Proposals

Public tools and Codex skills for preparing TCIA dataset proposals and organizing supporting tabular data.

## Components

### Dataset Proposal Form

`tcia-dataset-proposal.py` is a Streamlit form for proposing either a new primary-data Collection or an Analysis Result derived from existing TCIA data. It collects proposal and institutional-readiness information, generates a proposal package, includes the current Data Submission Agreement, and can optionally email the package to a configured TCIA help desk.

The legal point of contact and DSA are intentionally included early. They encourage submitters to determine whether their institution can authorize publication before the proposal reaches the TCIA Advisory Group.

### Supporting-data remapper

`tcia-remapper.py` opens with a choice of two independent tasks: generate internal curation outputs, or remap tabular supporting data. The NCI Imaging Submission Model is recommended guidance and is not currently a hard requirement for TCIA submission.

For curation outputs, import a TCIA proposal TSV/ZIP package or CRDC Data Hub submission-request XLSX workbook. The app parses the author list and provides an editable investigator table, parsing options, and optional ORCID profile lookup. Confirm the investigator list to download the **TCIA curation tracking document**, **TSV imaging model package**, and **CRDC proposal workbook** (v3.5 XLSX). Information gaps appear as follow-up warnings. Changing the proposal or investigator table requires confirmation again. The tracking document starts with the short title followed by `(private)` and retains placeholders for later curation.

For supporting data, go directly to column mapping, permissible-value review, and standardized TSV generation without importing a proposal. The former Summary Metadata wizard and CICADAS phase have been removed. If you previously imported a proposal in the same session, its metadata remain available for dataset linkages. Missing links are reported for follow-up. Keep original CRDC workbooks: fields without TCIA equivalents are not all preserved in generated exports.

### Submitter supporting-data guide

The [supporting-data preparation guide](https://kirbyju.github.io/tcia-dataset-proposals/supporting-data/) explains recommended clinical tables and non-DICOM imaging metadata. It provides a searchable field reference, linked fictional examples, blank Excel/TSV templates and matching example downloads. It complements the [Streamlit validator](https://tcia-streamlit.duckdns.org/validator/), which handles column remapping, supported values and standardized exports.

The reference separates the pinned NCI Imaging Submission Model from additional recommended CT, MR, PET, contrast, slide, annotation and processing metadata. Additional tables are preparation guidance, not an official MDF extension or a promise of validator support. Examples are partial teaching records; model requirements are not mandatory TCIA policy. Existing caDSR references are displayed as recorded in the source. Additional variables should be discussed with the submitter's curator.

Source snapshots and authored guidance live in `scripts/supporting_data/`. The model snapshot records upstream commit and source-file hashes; the IDC schema snapshot records package/data versions. No live schema fetch happens during a build. Keep the remapper's bundled schema separate and review compatibility when updating either source.

Rebuild the page, dictionary and deterministic ZIP downloads with:

```bash
python3 scripts/build_supporting_data_guide.py
```

When fields, examples or instructions change, regenerate the Excel workbooks from the same `guide-data.json` using `node scripts/build_supporting_data_workbooks.mjs` with `@oai/artifact-tool` available. In the Codex desktop bundled runtime, `ARTIFACT_TOOL_MODULE` can point to the absolute path of its `dist/artifact_tool.mjs` entry point. `GUIDE_PREVIEW_DIR` optionally saves workbook previews outside the site. The workbooks are checked in; GitHub Actions needs only Python's standard library to verify every data cell and dictionary entry against the generated guide:

```bash
python3 scripts/verify_supporting_data_workbooks.py
python3 -m unittest discover -s tests -p test_supporting_data_guide.py
```

The Pages workflow verifies both guides before publishing `/docs`. Existing root links still open the label catalog, which links to the submitter guide. Typography and layout are implementation choices; logos and palette follow the TCIA branding resources.

### Proposal review skill

`skills/review-tcia-dataset-proposal/` is a public-facing Codex skill for submitter self-review, TCIA staff review before the AG, and post-acceptance completion of dataset-level narrative documentation. It determines the user's role and lifecycle stage, extracts evidence from supplied materials, summarizes AG and CICADAS coverage when applicable, identifies gaps or ambiguities, and improves supported dataset descriptions without making an approval decision. CICADAS completion is helpful but is not expected before proposal review.

Install that subdirectory as a Codex skill, then upload a generated proposal ZIP or its component files and ask the skill to review the package.

`skills/remap-tcia-supporting-data/` contains the optional post-approval Codex skill. Runtime helpers, schemas, permissible values, and the DSA resource required by the Streamlit applications live separately in `tcia_proposals/`.

### WordPress metadata curation skill

`skills/curate-tcia-wordpress-metadata/` helps curators recommend labels before release from a supplied file or directory, or quality-check a published TCIA Collection or Analysis Result from its page or DOI. It compares dataset and download metadata with the inspected contents, calculates applicable counts and sizes, and harmonizes recommendations with current TCIA usage before consulting NCI Imaging Submission Model or GDC terminology for genuinely new concepts. The skill produces an evidence-backed report and does not edit WordPress.

Its [curator labeling reference](skills/curate-tcia-wordpress-metadata/references/labeling-guide.md) explains NCIt disease mappings, UBERON primary-site checks, and independent category/type/format assignments. It includes a [machine-readable policy](skills/curate-tcia-wordpress-metadata/references/labeling-policy.json), a dated observed vocabulary with counts and provenance, and a [shareable curator graphic](skills/curate-tcia-wordpress-metadata/assets/tcia-labeling-guide.png). Unconfirmed WordPress values require curator review; observed usage is not a complete registered or approved term list. These resources guide curation rather than implementing live validation in the Streamlit applications.

The [TCIA Data Models reference](https://kirbyju.github.io/tcia-dataset-proposals/labels/)
provides public documentation of eight fields: disease type, primary disease
site, data category, data type, file format, species, program, and external
resource category. Searchable terms include ontology links and published examples;
usage counts and registry membership remain distinct from semantic suitability.
The spreadsheet export and downloadable offline HTML preserve references and
source provenance.

The form and documentation use a shared captured vocabulary in
`tcia_proposals/resources/label_catalog.json`. It preserves the current public
registries, exact labels, reviewed links, decisions, counts, and source response
hashes. The form offers registered labels and an Other route. Human and Adult
are defaults, and age groups are collected only when Human is selected. Program
is documented but is not collected in the proposal form.

Category order, category/type selection rules, and DICOM display explanations
are authored in `tcia_proposals/resources/proposal_data_model.json`. Both the form
and the documentation use this source; the page also exports it as JSON. These
are proposal selection rules with an Other route, not an ontology hierarchy or
restrictions on historical public metadata. Display explanations do not change
the exported labels. ZIP remains in the public reference but is excluded from
proposal-format choices because packaging is handled later.

Data components contain one category, multiple data types, and one file format.
External resources contain one category, one URL, and optional resource context per entry. The tracking document pairs each URL with its context in a bulleted list and lists resource categories separately. Structured JSON
columns in the proposal TSV preserve these associations. Legacy summary columns
are no longer emitted; older packages remain importable. The remapper imports external
resources and includes components and species in its summary. Funding and
acknowledgements are collected later in curation. The proposal Word document
includes blank DataCite funding fields for two sources and an acknowledgements
placeholder.

Rebuild the documentation from the shared capture:

```bash
python3 scripts/build_label_catalog.py
```

The Pages workflow retains the daily 10:17 UTC public registry/usage refresh,
manual dispatch, and relevant push triggers. A refresh uses the existing reviewed
references, flags new/unmapped terms, and never infers ontology codes. Publication
uses the generated `/docs` artifact; no repository commit is made by the workflow.

To advance the form's bundled vocabulary and rebuild the page together:

```bash
python3 scripts/refresh_label_catalog.py --output /tmp/catalog-current.json
python3 scripts/build_label_catalog.py --live-inventory /tmp/catalog-current.json --write-shared-catalog
```

Alternatively, import the capture embedded in a saved public page or offline copy:

```bash
python3 scripts/import_public_label_catalog.py --html /path/to/captured-labels.html
python3 scripts/build_label_catalog.py
```

The importer requires all eight public registries and refuses older captures.
The Pages build publishes `labels/form-reference.json`, pairing the complete
catalog and proposal selection guidance in one response. The deployed proposal
form checks that feed hourly, retaining the last good in-process reference or its
bundled fallback during an outage. It rejects incomplete captures and older rules.
Once this form version and Pages workflow are deployed, registry updates flow
through the daily capture to the running form without application redeployment.
The proposal form uses Pathology Images, matching the current WordPress category.
SM (Slide Microscopy) is available under Pathology Images in the captured
WordPress data-type registry. The former Histopathology Images name is retained
only as a compatibility alias for proposals exported by earlier form versions.
Entirely new category/type relationships still require an explicit rule in the shared JSON; registry membership alone does
not establish those relationships. Other category offers only Other type.
Each proposal records the catalog capture timestamp and selection-guidance version,
with those troubleshooting fields shown in the Word footer. Historical inventories, mapping evidence, and
curation decisions remain in `skills/curate-tcia-wordpress-metadata/references/`
for audit. New confirmed reference mappings should be added there before refresh.

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

### Automatic label catalog refresh

GitHub Pages refreshes all eight label fields from the public WordPress API daily
at 10:17 UTC (GitHub may delay scheduled jobs), on relevant pushes to `main`, or
through **Actions → Publish TCIA reference guides → Run workflow**. Each deployment
captures the complete public registries, visible dataset assignments and each
record's own current downloads. Pagination, identities, required fields and
nonempty capture checks must pass before deployment. A failed build preserves the
last successful published site; the catalog displays its actual capture time.

The workflow builds fresh data directly into the Pages artifact; it does not make
bot commits or overwrite the dated source inventories. The checked-in HTML remains
an offline reference built from the dated inventories. The deployed offline copy
and spreadsheet export carry the current capture. Reviewed NCIt/UBERON references
are maintained separately and preserved. New labels, unmatched ontology references
and registry discrepancies are flagged in the Actions summary and spreadsheet;
refresh never guesses IDs or approves labels. Unused registered terms remain
visible with zero public uses (except explicitly retired Phantom disease/site
options). Hidden/private records are outside the usage counts.

To reproduce a current capture and build:

```sh
python3 scripts/refresh_label_catalog.py --output /tmp/catalog-current.json
python3 scripts/build_label_catalog.py --live-inventory /tmp/catalog-current.json
```

`supporting-data` is the WordPress registry behind `external_resources`. Historical
assignments can describe hosted supporting data, so this field alone must not be
used to infer hosting location. Dataset-specific curator audits are kept outside
this repository.
