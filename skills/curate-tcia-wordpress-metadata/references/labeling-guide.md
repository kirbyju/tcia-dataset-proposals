# TCIA labeling reference for curators

Prepared October 15, 2026. This documents the requested curation rules and prior usage. It does not certify every existing label or change WordPress.

## What was already built

| Component | Existing behavior | Remaining implementation boundary |
| --- | --- | --- |
| WordPress metadata curation skill | Added October 9 (`1dc6eaf`); routing and DataCite checks expanded October 10 (`4f77b7b`, `d6e1114`). Covers pre-release recommendations and post-release QC, dataset disease/site labels, independent download category/type/format review, existing-term preference, and curator review for new terms. | Agent instructions, not a WordPress form validator. Ontologies previously appeared mainly in fallback guidance. |
| Supporting-data remapper and skill | Bundled MDF model, property/term definitions, fallback `schema.json` and `permissible_values.json`; mapping of clinical/supporting tables to recommended submission entities. | `get_closest_match` uses Python `difflib` against bundled values. The inspected validation path has no live NCIt, UBERON, caDSR, or WordPress registry lookup. These model enums are not a WordPress allowlist. |
| TCIA query skill | Supplies public dataset identity, current-download metadata, and exact published labels with release provenance. | A usage snapshot omits unused registered terms. Publication usage is not proof of semantic correctness. |

The October 15 update makes NCIt/UBERON checks explicit even for reused labels, questions unconfirmed values in all five fields, and adds the policy, observed inventory, exporter, and curator graphic linked below. It does not add live validation to either Streamlit application.

## Five separate questions

| Field | Scope / WordPress key | Meaning and source |
| --- | --- | --- |
| Disease type | Dataset / `cancer_types` | Diagnosed disease or documented cohort context. Map disease concepts to **NCI Thesaurus (NCIt)**; reuse a suitable TCIA display label. Record the ontology's preferred label separately. |
| Disease location | Dataset / `cancer_locations` | Known primary disease site. Verify against **UBERON using its API**. Scanned anatomy, metastatic sites, and annotation targets are separate concepts. |
| Data category | Each download / `download_type` | Broad component role. Compare exact existing WordPress values first. |
| Data type | Each download / `data_type` | Specific information or object represented, established from content. DICOM object codes and semantic types can coexist when justified. |
| File type | Each download / `file_type` | Delivered payload format, established from content or authoritative inventory. Track archive/transfer container and manifest format separately. |

Apply multiple labels only when the content supports multiple concepts. Dataset disease/site labels describe the cohort and are not patient-level evidence.

## Choose, verify, reuse, or question

1. Read the dataset description and inspect each download or authoritative inventory. Identify the right field and scope.
2. Compare exact labels already used in that same WordPress field. Inspect representative uses and match meaning and specificity, not just strings.
3. For disease/site labels, retrieve the NCIt/UBERON concept and check its definition, synonyms, hierarchy and active/obsolete status. Store the stable ID, preferred label, version or retrieval date, mapping relation and evidence. An established display label may differ from the ontology's preferred label if the mapping is faithful and documented.
4. For category/type/format, consult the NCI Imaging Submission Model's applicable entity/property and the GDC schema that owns the concept. Follow referenced definitions and enums. **These are guides; their terms do not automatically become valid WordPress labels.**
5. Reuse a confirmed existing label if the evidence fits. If a candidate is unseen, ambiguous, broader/narrower than the evidence, or not confirmed in the field's term registry, set **needs curator decision**. Show the closest existing terms, why they do not fit, and the proposed term's definition and provenance.
6. When a service or source cannot be checked, record **unable to verify** for that check. Do not treat an outage or missing mapping as permission to invent a code or approve a label.

Healthy/non-cancer cohorts, unknown primary sites, systemic disease, mixed cohorts and contextual labels such as “Various” need explicit treatment when no faithful disease/site mapping exists. Do not force a disease code onto a study context or invent a primary organ from the scan coverage.

## Non-Cancer and specific companion labels

Confirmed by the user October 16, 2026: retain **Non-Cancer** as the broad TCIA discovery filter and also assign the supported specific disease or cohort-context labels. For example, pair it with the existing **Vestibular Schwannoma (non-cancer)**, **COVID-19 Infection (non-cancer)**, or **Healthy Subject** where supported. Mixed cancer/non-cancer datasets can retain both groups of labels. A parenthetical “non-cancer” in a specific label does not supply the standalone filter value.

Non-Cancer is a TCIA discovery grouping with no single disease-code equivalence confirmed. Keep it unlinked rather than forcing an NCIt mapping. Verify specific companion concepts against NCIt and prefer registered WordPress display labels. Nonmalignant disease, negative screening findings, and healthy subjects are different contexts: absence of cancer alone does not prove healthy status. Represent phantom identity in species and retain supported simulated disease/site context. For VICTRE, retain **Breast Cancer + Non-Cancer** with **Computational Phantom** species (user confirmed October 16). Use **Not Applicable** when disease/site context does not apply; do not label computational subjects Healthy Subject. Dataset labels describe represented groups, not each participant's diagnosis.

See [confirmed decisions](label-decisions.json) and the [dated consistency review](non-cancer-label-review-2026-10-16.md). These are recommendations; no WordPress edits have been applied by this agent.

## APIs and model guidance

- **NCIt:** [NCI EVS API specification](https://api-evsrest.nci.nih.gov/v3/api-docs). Search `GET https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/search?term={URL-encoded concept}&include=summary`; retrieve the selected code with `/api/v1/concept/ncit/{code}?include=summary`. Inspect definitions, synonyms and status; expand requested detail as needed. A ranked search hit is a candidate, not a verified mapping. API example verified October 15: `C4878`, preferred label `Lung Carcinoma`, NCIt `26.09d`. That does not automatically map all “Lung Cancer” cohorts to carcinoma.
- **caDSR:** [NCI API Portal](https://cadsrapi.cancer.gov/NCIAPIPortal/) supports data-element/model/value-domain investigation. The inspected imaging model cites CDE `14905532` version 1 for NCIt primary diagnosis, CDE `14883047` version 1 for UBERON primary site, and CDE `11416926` version 2 for file format. A **caDSR CDE number is not an NCIt concept code**. Use caDSR to clarify the field/value domain and EVS to verify the disease concept.
- **UBERON:** [EMBL-EBI OLS API documentation](https://www.ebi.ac.uk/ols4/ols3help). Search `/ols4/api/search?q={URL-encoded concept}&ontology=uberon&local=true&obsoletes=false`; retrieve `/ols4/api/ontologies/uberon/terms?obo_id={URL-encoded UBERON ID}`. Verified example: `UBERON:0002048`, preferred label `lung`, not obsolete. Confirm the selected term actually belongs to UBERON and inspect its definition. Do not send patient data or raw private values to public lookup services.
- **NCI Imaging Submission Model:** [property definitions](https://github.com/CBIIT/nci-imaging-submission-model/blob/607fcbc3cdab254c76ccf674ea1017669e94093b/model-desc/nci_imaging_submission_model_properties.yml), inspected at commit `607fcbc3cdab254c76ccf674ea1017669e94093b`. Use `primary_diagnosis`, `primary_site`, `file_type`, applicable nodes, and term definitions. Not every property is a closed enum.
- **GDC:** [schema directory](https://github.com/NCI-GDC/gdcdictionary/tree/88d66b0fe361aa638977850c180bd9130d705924/src/gdcdictionary/schemas), inspected at commit `88d66b0fe361aa638977850c180bd9130d705924`. As an example, `slide_image.yaml` distinguishes `data_category`, `data_type`, and `data_format`; its `Biospecimen` category is a GDC value, not an instruction to replace TCIA's `Pathology Images`. Record the owning schema/property for any mapping.

## What the observed vocabulary does and does not establish

[wordpress-label-inventory-2026-10-09.json](wordpress-label-inventory-2026-10-09.json) contains all distinct labels observed in the selected public snapshot: **103 disease types, 61 disease locations, 5 data categories, 52 data types, and 36 file types**, across 292 visible Collections and Analysis Results and their current downloads. It preserves spelling, counts, representative public records, provenance and unreviewed mapping status.

The bundle was generated **October 9, 2026, 03:08 UTC**. Its snapshot hash, SQLite integrity and foreign keys were checked locally. It is **not latest-verified**, and it is **not a complete WordPress term registry or an approved vocabulary**. The installed query skill (`2026.10.14.1`) reported upstream version `2026.10.15.1` during the live guidance check. Refresh guidance before a freshness-sensitive corpus review.

“Observed” means a public record used the label. “Registered” means WordPress has the term available in the corresponding field. “Semantically verified” means the label fits this content and, where applicable, an ontology concept. These are different checks. An unseen value triggers review; prove that it is genuinely new using a complete, dated term registry export or authorized registry query. If that source is unavailable, leave membership unverified.

No full registry export was available for this reference, so it cannot identify unused registered values or certify current registry absence. All imported historical labels remain semantically unreviewed. Existing ambiguous or legacy labels are candidates for QC, not automatically deleted or renamed.

## Exact download labels observed in the dated snapshot

These are prior-use labels to compare, not a certified allowlist. Case and spelling are preserved. Counts and public examples are in the JSON inventory.

**Data category:** `Clinical Data`, `Image Annotations`, `Other`, `Pathology Images`, `Radiology Images`.

**Data type:** `Acquisition Metadata`, `Capsule Endoscopy`, `Classification`, `CODEX images`, `CR`, `CT`, `Data Dictionary`, `Demographic`, `Diagnosis`, `DX`, `Exposure`, `Family History`, `Fiducial`, `Follow-Up`, `Histopathology`, `Hyperspectral`, `Immunofluorescence`, `Immunohistochemistry`, `KO`, `Measurement`, `MG`, `Molecular Test`, `MR`, `Multiphoton`, `Multispectral Imaging`, `NM`, `OT`, `Other`, `Pathology Detail`, `Photomicrograph`, `PR`, `Protocol`, `PT`, `Radiomic Feature`, `REG`, `RF`, `RTDOSE`, `RTIMAGE`, `RTPLAN`, `RTSTRUCT`, `RWV`, `SC`, `SEG`, `Segmentation`, `Single-cell Image`, `SR`, `Tissue Microarray`, `Treatment`, `US`, `Whole Mount Tissue`, `Whole Slide Image`, `XA`.

**File type:** `BMP`, `BVAL`, `BVEC`, `CSV`, `DAT`, `DICOM`, `DOC`, `DOCX`, `ENVI`, `GeoJSON`, `HDF5`, `JPG`, `JSON`, `MATLAB`, `MHA`, `MHD`, `MPG`, `MPS`, `MRXS`, `NDPI`, `NIfTI`, `NRRD`, `PDF`, `PNG`, `SAS`, `SQLITE`, `SVS`, `TFM`, `TIFF`, `TSV`, `TXT`, `XLS`, `XLSX`, `XML`, `XPT`, `ZIP`.

## Common decisions

| Evidence | Category / data type / file type guidance |
| --- | --- |
| CT DICOM images | `Radiology Images` / `CT` / `DICOM`, if supported by inspected objects. |
| DICOM segmentation object | `Image Annotations` / `SEG` / `DICOM`. `Segmentation` may also be appropriate when supported by established usage; do not automatically migrate away from `SEG`. |
| Segmentation labelmaps stored as NIfTI in a ZIP | `Image Annotations` / `Segmentation` / `NIfTI`; record ZIP packaging separately and assess any existing `ZIP` label in context. |
| Clinical table with diagnoses and follow-up | `Clinical Data` / `Diagnosis`, `Follow-Up` / actual format such as `CSV` or `XLSX`. Do not infer that every clinical subtype is present. |
| TCIA manifest pointing to DICOM objects | Classify the delivered content; record the manifest separately. Do not call the delivered images `TXT` simply because the manifest is text. |

These examples demonstrate the dimensions; they do not define a universal category/type/format combination allowlist. Labels such as `Other` require content review and a reason a more specific existing term does not fit.

## Files and refresh

### Mapping evidence and remaining review

The [historical picklist workbook](https://docs.google.com/spreadsheets/d/1KnbOO85nqbx8A3m1VLWOiUhBJY_KxkI29_JwAVgKxjs/edit) supplies NCIt codes/definitions, UBERON anatomy terms and a legacy-site crosswalk. [label-mappings.json](label-mappings.json) joins only case-normalized labels or explicit source crosswalks to the observed inventory, records source row numbers and the workbook hash, and retains code-lookup results separately from semantic review. The AI comparison sheet is advisory evidence, including conflicting IDs; its `accepted` values are not imported as curator approval.

To complete review: verify unresolved candidates against ontology definitions and synonyms, resolve conflicting or composite mappings, decide how study contexts such as healthy/non-cancer, phantom and “Various” should be represented, and record a curator's decision and supporting evidence. Then confirm label membership against the corresponding WordPress registry. Category/type/format review requires content examples and the applicable NCI/GDC definitions; the diagnosis/site workbook alone cannot approve those assignments.

The proposal form already offers **Other**, but its primary site/diagnosis menus currently draw from the bundled submission-model lists rather than observed TCIA labels. A suitable next change is a shared, dated curation vocabulary with **Choose an existing TCIA label** as the default, plus **Propose another term**. That path should support explicit NCIt/UBERON search and selection and use the chosen term as an ordinary proposal answer. The app does not need a separate suggestion registry, retained search history, or review tracking: curators handle discussion with the submitter manually. Term existence does not establish a new WordPress label. If curators later use a new term in WordPress, a refresh of the shared WordPress-derived picklist should bring it into the proposal app. Keep a documented free-text fallback for unavailable APIs and study contexts without faithful ontology matches, rather than forcing the submitter to choose an incorrect term. Only abstract concepts should be sent to public terminology services.

- [Machine-readable policy](labeling-policy.json): field rules, API routes, source commits, review states, new-term review template and verified API examples.
- [Observed vocabulary](wordpress-label-inventory-2026-10-09.json): exact labels with counts and examples; ontology mappings intentionally unreviewed.
- [Curator graphic, PNG](../assets/tcia-labeling-guide.png) and [editable SVG](../assets/tcia-labeling-guide.svg): shareable overview, with dated vocabulary caveat.
- [Exporter](../scripts/export_wordpress_label_inventory.py): regenerates the inventory without network calls or patient data. Use an already-installed validated bundle; no artifact download is needed merely to read this reference.

```bash
python3 scripts/export_wordpress_label_inventory.py \
  --bundle /path/to/validated/current-bundle \
  --output /path/to/wordpress-label-inventory-YYYY-MM-DD.json
```

Run from the skill directory. The exporter verifies the database hash against the bundle manifest, SQLite quick_check and foreign keys before writing. It does not authenticate the manifest independently or assert latest-release status. Preserve the dated inventory when creating a new one. Record current registry evidence separately, review ontology mappings, and reconcile curator decisions before describing a future catalog as approved.

The visual uses TCIA's official logo and published palette from the [branding page](https://www.cancerimagingarchive.net/branding/), verified October 15, 2026. Layout, typography and semantic color assignments are design choices for this reference.
