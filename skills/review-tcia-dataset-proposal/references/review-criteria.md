# TCIA Advisory Group review criteria

Use the current public sources as authority:

- [TCIA Advisory Group Charter](https://www.cancerimagingarchive.net/tcia-advisory-group-charter/)
- [Primary Data submission process](https://www.cancerimagingarchive.net/primary-data/)
- [Analysis Results submission process](https://www.cancerimagingarchive.net/analysis-results/)

Check whether the supplied materials explain:

1. Reproducibility value: how publication enables verification, replication, comparison, or extension of research.
2. Research or clinical need: the important gap or current clinical/research problem addressed.
3. Novelty: what is distinct from data already available through TCIA or comparable repositories. Do not assess this from the proposal alone. Perform the current TCIA comparison in `novelty-comparison.md`, identify the closest Collections and Analysis Results, and separate demonstrated differences from claims that still require PI clarification.
4. Scale and demographic distribution: whether the cohort size, composition, and relevant subgroups can support the stated uses or hypothesis development.
5. Supporting data and documentation: whether demographics, clinical history, treatments, outcomes, labels, annotations, dictionaries, protocols, or other context make the images scientifically useful.
6. Analysis rationale: for Analysis Results, the biological hypothesis, pathophysiologic rationale, discovery objective, or other scientific purpose behind the derived data.
7. Resource and feasibility context: approximate size, formats, timelines, facial-imaging considerations, access restrictions, and other factors that affect TCIA's ability to handle the submission.

Do not turn these criteria into a numeric score or decision. Identify the evidence present and the specific uncertainties that should be clarified before review.

## Disease type and primary location consistency

This is a proposal metadata check supporting the review, not an additional AG approval criterion. Perform it for every substantive proposal review using dataset-level documentation; it does not require patient-level data or imaging payloads.

- Compare the proposal's disease and location answers with its abstract, subject inclusion/exclusion criteria, and supplied manuscripts or other supporting documentation. For Analysis Results, check the submitted subset rather than assuming every diagnosis or site in the source Collection applies.
- Check that the selected disease's specificity is supported, including histologic subtype. A broader narrative and a narrower form answer require reconciliation; neither silently overrides the other. Do not infer a subtype from a dataset abbreviation, imaging assay, or immune-cell annotation.
- Distinguish the primary disease site from metastatic sites, specimen collection sites, and imaged anatomy. Check whether a site answer covers the cohort or omits documented primary sites. Do not infer a primary site merely from “primary tumor resection.”
- Use the label guidance in `curate-tcia-wordpress-metadata` when available for targeted NCIt disease verification, UBERON primary-site verification, and current WordPress registry checks. This targeted check does not require a full download or DataCite audit. If the skill is unavailable, verify the concepts through the official NCIt and UBERON services and check the corresponding public WordPress registries. Record concept IDs, definitions/scope, active or obsolete status, and retrieval dates; ontology membership alone does not establish WordPress registry membership. Report unavailable checks as unverified.
- Prefer a faithful existing WordPress label. If none fits, recommend a clearly identified new term for curator confirmation rather than forcing an inaccurate near-match. Keep the original answer, proposed mapping, evidence, and unresolved questions distinct.
- Ask only for facts not established elsewhere in the supplied package. Explain where a mismatch affects cohort interpretation before AG review; routine spelling, ontology mapping, or registry additions can remain curation follow-up. Put requested narrative clarification in **Abstract** and/or **Methods → Subject Inclusion and Exclusion Criteria**, and identify the structured proposal fields that also need correction.
- Report a compact disease/site comparison with evidence and confirmation state so the final WordPress labels can be checked against it after curation. Later confirmed corrections may supersede proposal-stage recommendations; preserve their source rather than treating the initial proposal as immutable.
