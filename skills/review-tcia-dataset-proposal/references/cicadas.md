# CICADAS across the TCIA proposal lifecycle

Use the current [Cancer Imaging Checklist for DAta Sharing (CICADAS)](https://www.cancerimagingarchive.net/cancer-imaging-checklist-for-data-sharing-cicadas/) to determine what users would need to understand and reuse the dataset.

## Role in the lifecycle

CICADAS completion is progressive.

- **Before submission:** Help a submitter assess and improve an early description. A complete CICADAS description is not expected and incompleteness should not discourage submission.
- **Before AG review:** Use available CICADAS information to clarify scientific value, cohort design, supporting data, reproducibility, limitations, and reuse. Separate questions material to AG review from documentation improvements that can wait.
- **After acceptance:** Help TCIA staff and the submitter finish the dataset-level abstract and description needed for publication. Keep unresolved facts in a separate confirmation list.

A CICADAS description can provide source material for a dataset-descriptor manuscript, including a submission to a journal such as *Scientific Data*. It does not establish compliance with any journal's requirements. Verify the target journal's current author instructions before preparing a manuscript-specific structure.

## Formatting checks

Report hard constraints separately from recommendations.

- Full title: recommend 110 characters or fewer.
- Short title: require fewer than 30 characters; use only letters, numbers, and dashes; do not use spaces; recommend avoiding `data` or `dataset`.
- Abstract: require no more than 1,000 characters and summarize subjects, imaging, supporting data, and potential research uses.
- Description: organize confirmed content under Introduction, Methods, Usage Notes, and optional External Resources. Use the applicable Methods subsections rather than inserting empty sections.

## Review areas

- Title and short title
- Abstract: subjects, imaging, supporting data, and potential uses
- Purpose, background, and uniqueness
- Inclusion and exclusion criteria
- Acquisition period, demographics, clinical characteristics, treatments, representativeness, and possible bias
- Scientifically meaningful acquisition summary by modality
- Clinical-data capture and relevant data-dictionary standards
- Other supporting data and known missingness
- Format conversions and preprocessing
- Annotation or segmentation methods, software, guidelines, annotator expertise, and variability assessment when applicable
- Quality control and validation
- Automated analyses, thresholds, scripts, code, and software versions
- Organization, identifiers, timepoints, predefined subsets, unusual formats, recommended software, and known errors
- Related datasets, publications, code, and external tools

## Coverage statuses

Use only these labels when reporting CICADAS coverage:

- `Established`
- `Partial`
- `Documented elsewhere`
- `Not established`
- `Not applicable`
- `Needs submitter confirmation`

For each applicable area, identify the status, evidence source, recommended action, and whether it would help before AG review or may wait until post-acceptance documentation.

## Editorial rules

- Preserve the submitter's intended meaning and terminology unless clarification is necessary.
- Ground every material addition in supplied evidence and record its source.
- Do not invent cohort counts, acquisition details, clinical variables, processing steps, validation, or limitations.
- Put only confirmed information in the clean draft. Place unresolved questions and editorial notes in a separate completion list or annotated draft.
- Accept evidence from the proposal, preprint, publication, protocol, dictionary, README, or linked repository.
- Reorganize and clarify content rather than requiring the submitter to repeat facts already documented elsewhere.

## Stage interpretation

CICADAS is guidance for a comprehensive dataset description, not a demand that every detail be finalized before AG review.

- Do not require exact DICOM acquisition values to be repeated when they are encoded in the files.
- Request a summary of acquisition characteristics when heterogeneity, protocol design, or technical properties materially affect scientific value or reuse.
- Describe unavailable information as a limitation; do not convert it into an automatic rejection rule.
- Treat a CICADAS-aligned preprint as strongly encouraged but optional.
- Focus pre-AG clinical review on whether the planned variables make the dataset scientifically useful, not on fully curating the table.
- Ask whether year of diagnosis is available. It is requested but not mandatory.
