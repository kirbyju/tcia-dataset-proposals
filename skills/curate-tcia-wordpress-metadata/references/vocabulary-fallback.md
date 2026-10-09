# Vocabulary harmonization and fallback

Use this reference only after inspecting the content and comparing the candidate concept with current TCIA usage through `tcia-query-skill`.

## Start with current TCIA usage

Inventory exact values and frequencies for the relevant field across current, visible Collections and Analysis Results. Inspect several records using each plausible label; a string match alone does not establish semantic equivalence.

Use the query surface appropriate to the environment. With a validated local snapshot, follow the query skill's schema guidance and derive download-label frequencies from `wordpress_download_labels`; derive dataset-field values from current visible WordPress records rather than historical versions. With MCP or REST, use supported search filters and follow representative matches with dataset detail. Do not bypass the query skill to enumerate hidden, staged, or retired records.

Prefer an existing label when:

- it represents the same concept at the same level of specificity;
- its capitalization and spelling are stable in current records; and
- using it does not hide a material distinction in the new dataset.

Do not merge concepts merely because one contains the other's words. In particular, keep primary disease site separate from imaged anatomy, data category/download role separate from data type, and transfer container separate from payload format.

## When no TCIA label fits

Consult the public source models in this order, using their current default/development branches rather than copying a stale list into this skill:

1. [NCI Imaging Submission Model](https://github.com/CBIIT/nci-imaging-submission-model/tree/main)
   - Use `model-desc/nci_imaging_submission_model.yml` to identify the applicable node.
   - Use `model-desc/nci_imaging_submission_model_properties.yml` and `model-desc/nci_imaging_submission_model_terms.yml` for definitions and terminology.
   - Relevant concepts include NCIt-backed primary diagnosis, UBERON-backed primary site/body part, NCBI taxonomy identifier, DICOM modality, and caDSR-backed file type and file size.
2. [GDC Data Dictionary schemas](https://github.com/NCI-GDC/gdcdictionary/tree/develop/src/gdcdictionary/schemas)
   - Inspect the current schema that owns the concept, its referenced `_terms.yaml` definition, and any enum definitions.
   - Relevant fields commonly include `disease_type`, `primary_site`, `data_category`, `data_type`, and `data_format`, but use only a field whose definition matches the TCIA concept.

These models guide terminology; they do not automatically define valid WordPress labels. Record the source repository, branch, file, field, and stable code or ontology identifier when available.

## Recommendation shape for a new term

Provide:

- proposed TCIA display label;
- definition in the context of this dataset/download;
- closest existing TCIA labels and why they do not fit;
- external source term, code/identifier, repository path, and retrieval date;
- whether the proposal is a synonym normalization, a narrower/broader mapping, or a genuinely new concept;
- affected WordPress field and example download/content evidence; and
- `needs curator decision` status.

Do not claim that a new term has been accepted, added to WordPress, or standardized across TCIA until that change is independently confirmed.
