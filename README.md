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
