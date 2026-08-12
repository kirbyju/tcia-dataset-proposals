# TCIA novelty comparison

Perform this comparison for every substantive proposal review. Novelty is often central to an informed AG review and must be investigated before asking the PI to explain it.

## Search preparation

1. Extract comparison axes from the proposal:
   - disease, diagnosis, and scientific question;
   - anatomy and specimen type;
   - adult, pediatric, or mixed population;
   - modality, image type, staining, and format;
   - cohort size, site count, and acquisition period;
   - cross-sectional or longitudinal design;
   - clinical variables, treatments, outcomes, annotations, and labels;
   - linked genomic, proteomic, or other multi-omic data; and
   - intended analyses or reuse cases.
2. Use the `tcia-query-skill` when available. Use TCIA WordPress Collection and Analysis Result metadata as the authority for TCIA publication.
3. Run the TCIA query skill's freshness preflight before making current-state claims. Report the snapshot generation time and whether freshness was verified. If refresh cannot be verified, disclose that the comparison may be outdated.
4. Exclude hidden, staged, retired, and internal-review records unless an authorized TCIA staff user explicitly requests them.

## Search sequence

1. Search for exact disease and cohort matches, including full names, abbreviations, historical terminology, and close synonyms.
2. Search separately for each major comparison axis. This catches datasets that are technically or scientifically similar even when the disease differs.
3. Search both Collections and Analysis Results. An Analysis Result may contain the annotations, labels, or derived data that make a Collection more comparable than its primary page suggests.
4. Inspect the full metadata and current downloads for the strongest candidates. Do not rely on a hit caused only by a program-wide related-dataset list, citation, or incidental use of a keyword.
5. Select three to six comparators that best represent meaningful overlap. Include an exact disease match when present; otherwise explain that none was found and select the closest feature-level comparators.

## Comparison dimensions

For each selected comparator, record:

- TCIA short title, dataset type, and public page;
- disease, population, anatomy, image type, scale, and supporting data;
- features shared with the proposal;
- material differences from the proposal; and
- whether it strengthens, qualifies, or does not materially affect the proposal's novelty claim.

Distinguish novelty in the individual components from novelty in their combination. A proposal may use a familiar modality yet still add a new disease cohort, population, longitudinal design, outcome linkage, annotation type, or combination of supporting data.

## Interpretation

Use calibrated conclusions:

- `No exact match found in the searched visible TCIA metadata` when the search finds no same-disease or same-design dataset.
- `The proposal appears differentiated within TCIA by ...` when metadata supports a specific distinction.
- `This differentiator remains unverified` when the proposal does not provide enough detail to compare reliably.
- `Existing TCIA datasets overlap in ...` when a component is already represented and should not be presented as novel by itself.

Do not claim that the proposal is globally unique or that no comparable dataset exists outside TCIA unless a broader repository and literature search was explicitly performed. Do not equate a metadata search miss with proof of absence.

## PI follow-up

Ask the PI only about distinctions that remain unresolved after the search. Name the closest TCIA comparators in the question so the PI can explain the added value concretely rather than restating a generic novelty claim.
