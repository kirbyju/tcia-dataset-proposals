# Field evidence and calculations

Use this reference when inspecting a supplied path or validating published download values. Record the tool, source, scope, and exclusions for every calculation so another curator can reproduce it.

## Inventory without changing the source

- Resolve the exact file or directory and note whether it is a file, directory, archive, manifest, symlink, or remote route.
- Recursively inventory regular files, symlinks, archive members, byte sizes, and detected formats. Do not follow a symlink outside the requested tree or count the same target twice.
- Inspect archive member tables before extraction. Reject or quarantine absolute paths, `..` traversal, device files, and other unsafe members. Extract only into a temporary directory when content inspection requires it.
- Ignore operating-system metadata such as `.DS_Store` when classifying scientific content, but mention unexpected files that may need removal before release.
- Do not execute binaries, macros, notebooks, or scripts found in the dataset.

Use content-aware readers where available. Examples include DICOM parsers for DICOM objects, archive readers for ZIP/TAR, and appropriate metadata readers for NIfTI, NRRD, MHA/MHD, TIFF/WSI, CSV/TSV, XLSX, JSON, XML, and common image/video formats. If a required reader is unavailable, report the limitation rather than guessing from an extension.

## Dataset-level evidence

Use the narrative and structured contents together:

- **Disease/cancer type:** confirmed cohort diagnosis, study eligibility, or explicit non-cancer/phantom context. Separate primary disease, metastasis, and incidental findings.
- **Disease/cancer location:** primary disease site when known. Keep it distinct from `BodyPartExamined`, field of view, biopsy site, or metastatic site.
- **Species:** explicit subject metadata or documentation. Record a stable taxonomy identifier when available, but recommend the established TCIA display label.
- **Modality/image type:** DICOM `Modality`, image metadata, or documented acquisition type. Report heterogeneous modalities separately.
- **Supporting data:** actual clinical, genomic, pathology, annotation, measurement, or other non-primary-imaging components, not merely a mention in prose.

When dataset-level values differ across downloads, recommend the supported union and identify which component supports each term.

## Download labels

Classify each downloadable component independently.

- Detect the transfer object: direct file, archive, TCIA manifest, URL list, DRS manifest, or external repository route.
- Detect the delivered payload formats. Do not label a manifest-routed DICOM download merely as text because the manifest itself is text.
- Derive data type from the semantic content. For DICOM, inspect SOP Class, Modality, and relevant coded content rather than assuming every object is a conventional image. For tables, inspect headers, dictionaries, and descriptions rather than reading participant rows into the report.
- A component may need more than one data-type or file-type label when it intentionally contains heterogeneous content. Recommend splitting the download only when that would materially improve accuracy or usability; do not require it by default.

## DICOM counting rules

For a local DICOM payload, parse headers without loading pixel data where possible. Calculate:

- **Subjects/patients:** distinct nonblank `PatientID` values within the download scope.
- **Studies:** distinct nonblank `StudyInstanceUID` values.
- **Series:** distinct nonblank `SeriesInstanceUID` values.
- **Images:** DICOM SOP instances/files under the WordPress counting convention, not frames. State whether non-image composite objects such as SEG, RTSTRUCT, SR, PR, or KO were included.

Also report malformed/unreadable files, blank identifiers, duplicate SOP Instance UIDs, and objects whose identifiers conflict. Never print the identifiers themselves. Do not infer missing identifiers from directory structure.

For manifest-routed public DICOM, use the official manifest/digest and the TCIA query skill's public DICOM metadata route. Confirm the record scope before comparing counts. If one source counts frames while WordPress counts instances, report both and do not call a mismatch until the basis is reconciled.

For derived DICOM annotations, a one-object-per-series pattern can make the series and image/instance counts equal; that is not inherently an error.

## Non-DICOM counting rules

Patient, study, series, and image fields may not all apply to non-DICOM downloads.

- Count subjects only from an explicit, documented subject identifier and state the column or mapping source without exposing values.
- Count studies or series only when the format or supplied data model defines those entities. Do not reinterpret rows, visits, time points, folders, or files as studies/series without evidence.
- For pathology, distinguish subjects, specimens, blocks, slides, image files, and pyramid levels.
- For NIfTI and similar volumes, distinguish subjects, sessions/time points, volumes, files, and image frames. Do not force these into DICOM study/series counts.
- For tables and documents, image/study/series counts are normally `not applicable`; blank WordPress fields may therefore be correct.

## Size calculations

Preserve each relevant size basis:

- exact bytes of a directly downloadable file;
- compressed archive or transfer size;
- expanded regular-file bytes;
- external package or manifest-resolved payload bytes, when available.

Convert bytes using both decimal units (`MB = 10^6`, `GB = 10^9`) and binary units (`MiB = 2^20`, `GiB = 2^30`) when this could explain an apparent discrepancy. Do not compare an expanded directory total with a compressed WordPress download size as if they were the same measure.

Treat small differences explainable by displayed precision as rounding. Flag `change recommended` only when the values refer to the same byte scope and unit basis and the difference is not explained by rounding, packaging, or a known update. Otherwise use `needs curator decision` or `unable to verify` and explain why.

## Evidence precedence

Prefer, in order:

1. identifiers and formats read from the actual scoped payload;
2. an official manifest or metadata digest generated for that exact payload;
3. release-matched TCIA/IDC/NBIA public metadata;
4. the download description and data dictionary;
5. filenames, directory names, or general dataset prose.

Conflicts are findings to report, not reasons to silently choose one source. Preserve each source's date, version, checksum, or release fingerprint when available.
