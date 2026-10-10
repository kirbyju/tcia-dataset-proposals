---
name: curate-tcia-wordpress-metadata
description: Audit or recommend TCIA WordPress and DataCite DOI metadata. Use for pre-release curation from supplied files or directories and for post-release review of a TCIA Collection, Analysis Result, or DOI, including requests to review, audit, sanity-check, or look for issues in a newly or recently published dataset even when the user does not mention WordPress, DataCite, DOI metadata, or labels. Verify dataset descriptions and labels, download category/data/file types, counts, sizes, accessible contents, and DOI completeness and consistency; do not edit WordPress or DataCite.
---

# Curate TCIA WordPress Metadata

## Objective

Help TCIA curators populate or review dataset-level and download-level WordPress fields and the corresponding DataCite DOI metadata. Prefer terms already used consistently in current TCIA records. Independently inspect the supplied or published contents before recommending labels, counts, sizes, or DOI metadata, and preserve uncertainty when the evidence does not support an exact value.

This is a metadata recommendation and QC workflow. It does not authorize a WordPress or DataCite edit, DOI registration/update, publication, payload transfer, access-control change, or release decision.

## Use the TCIA query skill first

Load and follow `tcia-query-skill` for every substantive task. Run its freshness check when its scripts are available, record the selected snapshot or service fingerprint, and use its normal query workflow rather than scraping WordPress as the primary discovery method.

- Use current TCIA Collections and Analysis Results to inventory existing dataset and download labels, spelling, capitalization, and usage context.
- For a URL, retrieve the matching current TCIA record and all current downloads.
- For a DOI, use TCIA/DataCite DOI lookup to identify the related TCIA record; a DOI alone does not prove that a page or file is TCIA-published.
- Treat DataCite as the authority for registered DOI metadata and WordPress as the authority for current TCIA publication identity, landing-page fields, downloads, access, and licenses. Compare them rather than substituting one for the other.
- When auditing the corpus, enumerate the current TCIA DataCite client/repository records and join them to current WordPress DOI values. Do not assume all TCIA DOIs use one prefix.
- Check related Analysis Results when annotations or derived data may be published separately.
- For public DICOM evidence, follow the query skill's IDC-first route and its NBIA fallback rules.
- Report the query-skill version and data fingerprint/date used for the comparison. If freshness is unverified, label the corpus comparison unverified instead of claiming that the recommendations reflect the current vocabulary.

Treat prior TCIA usage as harmonization evidence, not proof that an existing label is correct. A widely reused label can still be ambiguous or wrong for the supplied content.

## Select the workflow

### Pre-release recommendation

Use when the curator supplies a local file, archive, manifest, or directory.

1. Resolve the exact target and inventory it recursively without modifying the source.
2. Inspect archive members safely; do not execute contents. Use a temporary directory only when extraction is necessary.
3. Detect formats from content and metadata, not filename extensions alone.
4. Read the dataset description, proposal, README, data dictionary, manifest, or other supplied documentation before assigning semantic labels.
5. Calculate applicable counts and sizes using [field-evidence.md](references/field-evidence.md).
6. Compare candidate terms with current TCIA usage, then recommend the smallest set of labels that accurately describes the dataset and each separately downloadable component.
7. If a DOI registration draft or DataCite export is supplied, assess its completeness and consistency using [datacite-completeness.md](references/datacite-completeness.md). Do not invent conditional values merely to fill a field.

Do not print or return subject identifiers, filenames containing identifiers, DICOM headers, contact details, credentials, or other sensitive values. Keep local contents local; when consulting public vocabularies, send only the abstract concept that needs mapping.

### Post-release QC

Use when the curator supplies a TCIA Collection or Analysis Result URL, short title, or related DOI.

1. Resolve the canonical TCIA record and capture every current download's displayed/raw fields: title, URL/route, description, download type/category, data type, file type, subject/patient count, study count, series count, image count, size and unit, access, and license.
2. Retrieve the live DataCite record for the WordPress DOI and audit it using [datacite-completeness.md](references/datacite-completeness.md). Include mandatory-property completeness, TCIA baseline fields, controlled-value consistency, and parity with the current WordPress record.
3. Read the full dataset description and the description of each download. Do not infer a label from the page title alone.
4. Prefer already-published manifests, metadata digests, inventories, and public metadata services for remote validation. Cross-check them against the actual accessible payload when practical.
5. Before transferring a payload, follow the TCIA query skill's download rules. Ask whether the user wants a local download and where it should be stored; never transfer controlled data without the required authorization and user-provided credential path.
6. Recalculate applicable values using [field-evidence.md](references/field-evidence.md), recording the evidence source and counting basis for each value.
7. Compare the entered value with the observed value. Explain rounding, archive/container, multi-frame, duplicate, applicability, or version-scope differences before calling a mismatch.

If the payload is inaccessible, too large to transfer, controlled, or lacks enough metadata, mark the affected checks `unable to verify`. Do not convert absence of evidence into a pass or failure.

## Recommend labels

Evaluate all dataset fields present in the current WordPress record, including at minimum disease/cancer type, disease/cancer location, species, imaging modality or image type, and supporting-data labels when applicable.

- Disease type describes the cohort's diagnosed condition or study context, not every incidental finding or annotation class.
- Disease location describes the disease's primary site when known. Do not substitute every body part scanned or annotated.
- Species must be supported by the description or subject metadata. Do not infer it from names or institutional context.
- Use multiple labels only when the dataset genuinely contains multiple concepts; do not add broad umbrella labels merely to improve discoverability.

Evaluate every current or proposed download independently. Keep these concepts separate even when the WordPress presentation uses similar wording:

- **Download type or data category:** the component's functional role, such as images, annotations, clinical/supporting data, metadata, or derived results, using the exact current TCIA vocabulary.
- **Data type:** the specific information represented, such as an imaging object class, measurement, classification, segmentation, or clinical table, based on content and established TCIA usage.
- **File type:** the payload format. Record the transfer container separately from the contained formats; a ZIP or TCIA manifest is not automatically the format of the files it delivers.

Prefer an exact existing TCIA label when it represents the same concept. Do not force a near-match that changes meaning. When no established TCIA term fits, follow [vocabulary-fallback.md](references/vocabulary-fallback.md) and label the result as a proposed new or mapped term requiring curator confirmation.

## Produce the report

Start with the target, workflow, TCIA query provenance, inspected evidence, and important limitations. Then provide:

1. **Dataset fields** — one row per field with `field`, `entered value` (post-release only), `observed evidence`, `recommended value`, `status`, `confidence`, and `source`.
2. **Download fields** — group by download and use the same columns for category/download type, data type, file type, counts, and size.
3. **Counting and size basis** — state how subjects, studies, series, images/instances, files, compressed bytes, and expanded bytes were calculated and which concepts were not applicable.
4. **DataCite DOI metadata** — one row per checked property or parity rule with `property`, `DataCite value`, `comparison evidence`, `status`, `confidence`, and `recommended action`. Distinguish schema-mandatory, schema-recommended, TCIA baseline, and conditional properties.
5. **Curator remediation queue** — group copy-ready changes by system (`WordPress`, `DataCite`, or `both`) and priority. For a corpus audit, summarize coverage and list every affected DOI/short title for fields that are normally populated but missing or inconsistent.
6. **Recommended WordPress changes** — a concise, copy-ready list of changes, additions, removals, and values needing curator confirmation. In pre-release work, present this as proposed field values.
7. **Unverified items** — identify the missing evidence or access needed to complete each check.

Use only these statuses: `pass`, `change recommended`, `needs curator decision`, `not applicable`, and `unable to verify`. Never silently replace a value or present a recommendation as an applied WordPress change.

## Guardrails

- Do not edit WordPress or DataCite, publish or retire a dataset, register or alter a DOI, or change a downloadable object unless the user separately requests and authorizes that action.
- Do not expose PHI or participant identifiers. Return aggregate counts and bounded examples only when examples are necessary and non-sensitive.
- Do not treat a directory name, filename, archive name, or prose claim as sufficient evidence for patient/study/series/image counts.
- Do not treat blanks as zero. Use `not applicable` only when the field's concept does not apply, and `unable to verify` when it applies but evidence is insufficient.
- Do not sum download-level subject counts to obtain a dataset total unless the subject sets are proven disjoint. Report union counts only from stable identifiers, without exposing those identifiers.
- Do not equate DICOM instances with frames, studies with time points, series with files, or pathology slides with radiology series.
- Keep Collection and Analysis Result evidence separate unless the requested QC explicitly covers both.
- Do not call every blank recommended or optional DataCite property an error. Apply the obligation, empirical-baseline, and applicability rules in [datacite-completeness.md](references/datacite-completeness.md), and never infer funding, relationships, geography, identifiers, or contributor roles without evidence.
- Preserve access and license boundaries. Public metadata does not authorize controlled-data retrieval.
