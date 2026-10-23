TCIA supporting-data preparation materials

Use templates when practical. If you already have spreadsheets, the remapping tool
can help align them with the recommended model: https://tcia-streamlit.duckdns.org/validator/

These are recommended preparation materials, not a mandatory submission format.
Use only the tables relevant to your dataset. All example records are fictional.
Examples are partial teaching records, not a validated or complete submission.
No image files are included. Blank cells mean values were not supplied in the
example; they are not zero or a prescribed missing-value code. Discuss unknown,
not collected and not applicable values with your curator; preserve distinctions.

Model tables follow NCI Imaging Submission Model 0.0.4, commit
607fcbc3cdab254c76ccf674ea1017669e94093b. Dot-notation columns express model relationships.
They follow the existing remapper's template convention, not MDF property names.
The remapper's deployed schema may differ. These downloads are preparation
templates, not a guarantee of direct import into the deployed validator.
file_id is assigned by the CRDC Submission Portal per upstream documentation;
it is left blank here. Discuss identifier assignment with your curator.

Additional recommended imaging tables are outside the current MDF model and
are not automatically supported by the validator. They use file.file_name to
link to exact relative paths in file.tsv, scoped to the same dataset. Keep paths
unique within a dataset. annotation_details has one row per region/group;
other additional tables have one row per submitted file or image volume.
Report source acquisition metadata separately from submitted image properties.
Use JSON arrays for repeated fields, for example [2.5, 5.0]. Preserve pairing
and ordering in source records when needed; distinct-value lists are not a
per-frame or per-voxel mapping. Do not infer acquisition settings from appearance.
Pixel/voxel spacing and nominal slice thickness are different measurements.
Do not invent DICOM UIDs for non-DICOM files.

The Excel workbooks contain these same columns. Each data sheet has its header
in row 1. The Instructions and Dictionary sheets are reference material.
Blank templates contain no example data; copy only relevant sheets into your
working package. Keep one observation per row and one variable per column.

Consult your data curator about how to provide additional data points you have
collected. Supply patient-level information only through the curation workflow
agreed with TCIA, using permitted de-identified identifiers and dates.

Sources: https://github.com/CBIIT/nci-imaging-submission-model
https://idc-index.readthedocs.io/en/latest/indices_reference.html
IDC source snapshot: idc-index 0.12.3,
idc-index-data 24.2.0, v24.
Reviewed: 2026-10-18.
Model definitions are reproduced from the Apache-2.0 licensed upstream project.
