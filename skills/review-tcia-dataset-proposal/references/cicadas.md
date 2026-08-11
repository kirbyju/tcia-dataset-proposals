# Proposal-stage CICADAS gap review

Use the current [Cancer Imaging Checklist for DAta Sharing (CICADAS)](https://www.cancerimagingarchive.net/cancer-imaging-checklist-for-data-sharing-cicadas/) to determine what users would need to understand and reuse the dataset.

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

## Proposal-stage interpretation

CICADAS is guidance for a comprehensive dataset description, not a demand that every detail be finalized before AG review.

- Accept evidence from the proposal, preprint, publication, protocol, dictionary, README, or linked repository.
- Do not require exact DICOM acquisition values to be repeated when they are encoded in the files.
- Request a summary of acquisition characteristics when heterogeneity, protocol design, or technical properties materially affect scientific value or reuse.
- Describe unavailable information as a limitation; do not convert it into an automatic rejection rule.
- Treat a CICADAS-aligned preprint as strongly encouraged but optional.
- Focus pre-AG clinical review on whether the planned variables make the dataset scientifically useful, not on fully curating the table.
- Ask whether year of diagnosis is available. It is requested but not mandatory.
