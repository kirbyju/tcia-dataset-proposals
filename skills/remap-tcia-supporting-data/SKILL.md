---
name: remap-tcia-supporting-data
description: Review TCIA supporting clinical or tabular files and their data dictionaries, give submitter feedback, or map columns and values to the recommended NCI Imaging Submission Model in MDF format. Support review without conversion and optional proposal-package import; the model is not a hard TCIA submission requirement.
---

# Remap TCIA Supporting Data

Help submitters and curators document, review, and optionally remap supporting tabular data. Strongly recommend a data dictionary alongside every tabular submission so its meaning is preserved and mapping to other models can be done later. Documentation and review do not require immediate standardization.

## Choose the task

Use the user's stated request; clarify only when the intended output is unclear.

- **Review only:** Inspect supplied tables and dictionaries and provide feedback or submitter questions. Do not rewrite values or generate remapped files unless requested.
- **Remap supporting data:** Start directly with source tables and their dictionaries. No proposal import, Program/Dataset interview, investigator collection, or CICADAS completion is required first.
- **Generate curation outputs:** Use the separate `tcia-remapper.py` workflow to import a TCIA proposal TSV/ZIP or CRDC submission-request XLSX, review and confirm investigators, and generate curation outputs. Preserve the original CRDC workbook because conversion does not retain every field. Do not add downstream Imaging Model completeness checks to proposal curation.

When narrative or CICADAS assistance is requested, use `review-tcia-dataset-proposal` if available. Narrative completion is not a prerequisite for spreadsheet review or remapping. Reuse supplied metadata instead of repeating an interview.

## File preflight before loading tables

Inspect file sizes and formats before loading full tables or rendering workbooks. For XLSX, inventory ZIP member sizes, worksheet names, reported dimensions, and dictionary locations using a lightweight reader. Reported dimensions are provisional, not verified record counts. File size alone does not predict memory use or review effort.

Choose the reading strategy from the inventory, requested checks, and available runtime resources; do not use a fixed megabyte or cell-count cutoff. Use the [large-table review approach](references/large-table-review.md) when expanded workbook contents, worksheet breadth or depth, shared strings, formulas, or expected output make a full load expensive or uncertain, or when an initial read is slow, truncated, or fails. Start with bounded previews and prefer streaming when resource needs are unclear. Keep a straightforward path for small, simple inputs. Do not dump whole tables into chat or repeatedly retry a failed full load.

## Data dictionary first

Strongly recommend that submitters provide a data dictionary with their clinical and other tabular files, including files they do not plan to remap. A companion worksheet or separate file is suitable. For each table, document what one row represents, identifier scope, links to other tables/images, and repeated or longitudinal observations. For each column, recommend documenting:

- Exact source column name and plain-language definition.
- Data type, format, and units; for ages and time intervals, the reference event or time origin.
- Allowed values and the meaning of every code or abbreviation, including missing, unknown, not applicable, and not assessed values.
- Relevant measurement, assessment, or derivation method; existing terminology/CDE references and versions when known.

Do not require submitters to select CDEs or ontology codes before providing well-documented source tables. Do not guess code meanings, units, or a missing-value convention from the observed values alone. If the dictionary is missing or incomplete, continue the supported review, identify the gaps, and provide focused questions or a draft dictionary with unresolved meanings explicitly marked for submitter confirmation. Do not invent definitions or turn this recommendation into an approval gate.

## Review-only feedback

Inspect the supplied files, worksheets, headers, row counts, sample values, and dictionary before proposing changes. Establish row meaning and identifier scope before interpreting duplicate IDs as duplicate observations. Use source evidence to assess documentation, missingness, code consistency, units, and table/image linkage; identify checks that could not be completed.

Return a concise summary followed by a field-level feedback table, for example:

| Source table/field | Finding or uncertainty | Suggested action | Evidence/status |
| --- | --- | --- | --- |
| Clinical.Age | Units and reference event undocumented | Ask whether this is age at diagnosis, enrollment, or imaging, and request units | Needs submitter confirmation |
| Clinical.Response | Codes present without definitions | Request code meanings and assessment criteria | Dictionary gap |

Include proposed MDF targets only when useful to the requested review; mapping is optional. Distinguish source/dictionary findings, assistant-performed checks, and app-reported validation. State material limitations. Group related questions rather than asking about each value separately. Keep unsupported mappings unresolved and preserve source values.

## Remapping target and workflow

Use the [NCI Imaging Submission Model repository](https://github.com/CBIIT/nci-imaging-submission-model), expressed in MDF YAML, as the recommended target people can consider mapping to. Do not substitute the TCIA query skill's discovery/harmonization schema as the submission target. The model is guidance, not a hard TCIA submission requirement. Well-documented variables without a supported target can remain in source tables for curator discussion and later mapping.

1. **Identify the target resources.** For app-compatible exports, use the remapper's bundled MDF model and identify the version used. If the user selects a different upstream version, inspect its definitions and flag compatibility differences rather than silently mixing schemas. Discover entities, fields, definitions, and requirements from that model; use the JSON schema only as a fallback.
2. **Propose structure mapping.** Summarize source table/column, proposed target entity/property, units or other transformations, mapping evidence, and unresolved questions. Retain an account of unmapped columns. Obtain agreement on proposed mappings before applying them unless the user's existing instructions already authorize them.
3. **Review values.** Check confirmed columns against the applicable permissible lists and source dictionary. Separate exact matches, candidate replacements, and unresolved values. Present grouped suggestions for review; apply only supported, authorized transformations.
4. **Generate requested outputs.** Use the existing remapper/helpers to split and export entity TSVs. Preserve original files and explain applied transformations and omitted fields. Report unresolved values and linkage limitations rather than claiming complete clinical QC from a successful export.

Model-required fields describe the selected model's expectations, not TCIA acceptance criteria. Missing information should be reported in context without inventing values. If imported metadata conflict with source tables, explain the conflicting evidence and seek clarification before resolving it.

## CDEs, ontologies, and semantic review

- Distinguish a **caDSR CDE reference describing a field** from an **ontology concept describing a value**. Existing references can help interpret a mapping; they do not establish that a new source variable is equivalent.
- The app uses exact membership and `difflib` text similarity against bundled permissible values. It does not search caDSR, select new CDEs, or perform live ontology/synonym validation. A code or definition displayed with a text match does not verify equivalence.
- When semantic verification is needed, consult the source dictionary and relevant authoritative terminology, such as NCIt, UBERON, or SNOMED CT as appropriate. Record the source, identifier/version when available, and rationale for verified recommendations. If verification is unavailable, label the candidate unverified and retain the source term.
- Preserve uncertainty, time context, and diagnostic specificity. Do not infer a more specific diagnosis from `NOS`, or treat unknown, not assessed, not applicable, and negative as interchangeable.
- Recommend curator discussion for variables outside the chosen model rather than automatically selecting supplemental CDEs or forcing a close match. Group decisions for review; do not describe unaccepted suggestions as auto-corrections.

## Runtime implementation and boundaries

In `tcia-dataset-proposals`, `tcia-remapper.py` provides the separate curation-output and supporting-data workflows. Runtime resources are outside this skill folder:

- `tcia_proposals/resources/model/`: bundled MDF YAML model, properties, and terms.
- `tcia_proposals/resources/schema.json`: fallback property definitions.
- `tcia_proposals/resources/permissible_values.json`: additional/fallback values with terminology metadata; MDF enums take precedence where supplied.
- `tcia_proposals/mdf_parser.py`: MDF parser.
- `tcia_proposals/remap_helper.py`: matching, validation, splitting, linkage warnings, and TSV helpers.
- `tcia_proposals/orcid_helper.py`: optional investigator lookup/parsing support.

The app reads CSV, TSV, and Excel, processing a selected worksheet at a time. Its value validator checks mapped controlled-list values and skips blanks; it does not comprehensively check required values, types, ranges, units, clinical plausibility, or cross-table identifier integrity. Linkage warnings check for missing linkage columns, not whether every referenced identifier exists. The splitter drops duplicate projected rows; review repeated-observation grain before conversion. Do not equate the app's success messages with a complete review.

For dataset/download WordPress labeling, use `curate-tcia-wordpress-metadata` if available. Submission-model values do not establish WordPress registry membership or authorize new labels.

If installed without the repository, obtain the user's selected model resources or retrieve the public repository resources before model-specific mapping. Review and data-dictionary feedback can proceed without a model download.
