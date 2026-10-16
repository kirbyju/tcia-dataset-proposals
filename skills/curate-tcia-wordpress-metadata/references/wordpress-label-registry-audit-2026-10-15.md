# WordPress disease/site option usage audit

Checked October 15, 2026 (America/New_York), using all public option-list pages and current dataset responses. Scope: 237 visible Collections and 54 visible Analysis Results. Hidden, draft, and future publication use is not asserted. Exact labels are preserved; case-only variants are counted as the same option and recorded separately. No WordPress records were changed.

## Summary

| Field | Public registered options | Options used by visible datasets | Zero-use options |
| --- | ---: | ---: | ---: |
| disease_type | 124 | 103 | 21 |
| disease_location | 75 | 61 | 14 |

`Misc Cancer` is the option post title; its display label is `Misc. Cancer` (option ID 27823). It has zero current visible dataset references and no hidden references in the public API response. The release-backed service search independently returned zero for the exact label, using the October 13 bundle (`a74b80068740d823657379be97e704e6db5229424a731de47397aa534213ff29`).

The registry value `mesothelioma` has three case-only uses as `Mesothelioma`: EAY131, Mediastinal-Lymph-Node-SEG, and EAY131-Tumor-Annotations. It is not unused.

`Phantom` currently labels disease type on 11 visible datasets and disease location on seven. The user requested retirement from both fields, using the species field for phantoms. NCIt C48660 (Not Applicable) was verified active in version 26.09d as a proposed non-applicability marker. No WordPress changes were applied.

## Unused disease_type

- Adenocarcinoma Colon
- Adenocarcinoma Pancreas
- Bladder Endothelial Carcinoma
- Cervical Squamous Cell Carcinoma and Endocervical Adenocarcinoma
- Endocrine Miscellaneous
- Healthy Controls (non-cancer)
- Hematopoietic
- High Grade Glioma
- Kidney Clear Cell Renal Cell Carcinoma
- Kidney Other
- Lung Other
- Major Salivary Gland
- Misc. Cancer
- Miscellaneous
- Pathologically Benign
- Rectum Mucinous Adenocarcinoma
- Renal Clear Cell
- Soft Tissue
- Testicular Germ Cell Tumors
- Thyroid Carcinoma
- Uterine Sarcoma

## Unused disease_location

- Bile duct
- Brain Phantom
- CUP
- Ear
- Endocrine
- Gastrointestinal
- Head & Chest Phantom
- Hip
- Lip
- Liver Phantom
- Lung Phantom
- Mouth
- Soft Tissue
- Testis

## Sources

- [WordPress disease-type options](https://www.cancerimagingarchive.net/api/v2/cancer-types) (all three pages at 50/page).
- [WordPress location options](https://www.cancerimagingarchive.net/api/v2/cancer-locations) (both pages at 50/page).
- [WordPress Collections](https://www.cancerimagingarchive.net/api/v2/collections) (all three pages at 100/page).
- [WordPress Analysis Results](https://www.cancerimagingarchive.net/api/v2/analysis-results) (all 60 returned records; hidden rows excluded).
- [NCIt C48660](https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/C48660?include=summary).
- [Machine-readable audit with per-option counts, public dataset links, and response hashes](wordpress-label-registry-audit-2026-10-15.json).

Zero public use is a cleanup-review candidate, not proof that a label is incorrect or unused in private/draft work. Phantom retirement and Not Applicable addition are recommendations pending application in WordPress.
