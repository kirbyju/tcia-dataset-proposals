---
name: review-tcia-dataset-proposal
description: Review a TCIA new-collection or analysis-results proposal package, including its TSV or DOCX summary, preprints, publications, and supporting documents. Compare the proposal with current visible TCIA Collections and Analysis Results to assess overlap and evidence of novelty. Use when a submitter or TCIA reviewer wants a source-grounded summary, TCIA comparator analysis, gaps or ambiguities to clarify before Advisory Group review, CICADAS alignment suggestions, AG-criteria coverage, or PI-ready follow-up questions. Proposal packages may include an early Data Submission Agreement for the site's legal review; exclude that PDF from proposal feedback. Do not make an approval decision or perform post-approval data curation.
---

# Review a TCIA Dataset Proposal

## Objective

Help a submitter or reviewer assemble enough evidence for an informed TCIA Advisory Group (AG) review. Extract information already present across the package before asking for it again. Summarize gaps and draft constructive clarification questions. Do not predict, assign, or recommend a proposal status.

Ignore the Data Submission Agreement (DSA) PDF when reviewing the proposal or providing feedback. TCIA sends it early so the site's legal team can begin review; it is expected to remain incomplete and unsigned until after AG approval.

## Load the references

- Read [proposal-package.md](references/proposal-package.md) when inventorying an uploaded proposal package or determining the proposal type.
- Read [review-criteria.md](references/review-criteria.md) for every substantive review.
- Read [novelty-comparison.md](references/novelty-comparison.md) and perform its TCIA comparator search for every substantive review.
- Read [cicadas.md](references/cicadas.md) when evaluating description completeness or drafting improvement suggestions.
- Read [nctn.md](references/nctn.md) when the proposal mentions an NCTN or NCORP trial, a cooperative group, CTEP, IROC, or CIP-directed publication.

## Workflow

1. Inventory the package.
   - List the ZIP members or uploaded files without exposing contact details in the response.
   - Locate the proposal TSV or DOCX, preprints or manuscripts, data dictionaries, and other supporting documentation.
   - Acknowledge a DSA only as an expected package artifact when needed for inventory; do not inspect, summarize, cite, or evaluate it.
   - State which expected proposal materials were not supplied. Treat a preprint as recommended, not mandatory, and never treat an incomplete or unsigned DSA as a missing proposal item.

2. Extract evidence before identifying gaps.
   - Read the complete proposal summary and relevant supporting documents.
   - Follow supplied publication, preprint, DOI, repository, and dataset links when accessible.
   - Record the source and location for each material claim.
   - Reuse evidence found in a preprint or publication instead of asking the submitter to repeat it.

3. Determine the review path.
   - Classify the proposal as a new primary-data Collection or an Analysis Result derived from existing image data.
   - Detect possible NCTN/NCORP provenance and apply the NCTN authorization check.
   - Note a CIP-directed NCTN route separately because it does not require an AG vote.

4. Compare with existing TCIA datasets.
   - Search current visible TCIA Collections and Analysis Results using the procedure in `novelty-comparison.md`.
   - Search first for the same disease or scientific cohort, then for overlap along individual axes such as anatomy, population, imaging type, longitudinal design, supporting data, annotations, and multi-omic linkage.
   - Inspect the closest candidates rather than relying on keyword-result counts.
   - State what each comparator shares with the proposal and what appears different.
   - Treat an absent exact match as evidence from the documented search, not proof that no comparable dataset exists anywhere.

5. Assess information coverage.
   - Compare the evidence with the AG criteria in `review-criteria.md`.
   - Compare the description with the proposal-stage interpretation of CICADAS in `cicadas.md`.
   - Distinguish information that is absent from information that is merely located in another supplied source.
   - Do not require exhaustive acquisition parameters when exact details are carried in DICOM or other data. Ask for a concise acquisition summary only when it helps explain scientific value, heterogeneity, limitations, or reuse.

6. Draft clarification questions.
   - Ask only questions whose answers would materially improve the AG's understanding.
   - Explain briefly why each question matters.
   - Separate questions that should be answered before AG review from optional description improvements.
   - Phrase questions for the scientific point of contact or PI in neutral, collaborative language.

7. Produce the review.
   - Use the output structure below.
   - Cite the proposal or supporting source for statements of fact.
   - Keep personal contact details out of the review unless the user explicitly requests them.

## Output structure

### Proposal snapshot

Summarize the proposal type, dataset purpose, approximate scale, imaging and supporting-data types, related TCIA Collections, and supplied supporting materials.

### TCIA novelty comparison

Report the TCIA search scope and metadata freshness, then compare the proposal with three to six closest visible Collections or Analysis Results. For each comparator, give the overlapping features, material differences, and relevance to the novelty assessment. Conclude with:

- novelty supported by the current TCIA comparison;
- overlap that reduces or qualifies the novelty claim; and
- differentiators that remain unverified and should be clarified with the PI.

### Evidence relevant to AG review

Organize evidence under the applicable AG criteria. Say `not established in the supplied materials` when evidence is missing; do not infer an answer.

### Clarifications to request before AG review

For each material gap, provide:

- the unclear or missing point;
- why it matters to the AG review;
- the source materials already checked; and
- one concise PI-ready question.

### Optional improvements

Suggest non-mandatory CICADAS-aligned improvements that would make the dataset easier to understand or reuse. Do not present these as submission requirements.

### Routing note

Include only when NCTN/NCORP authorization, CIP-directed handling, facial-imaging risk, controlled access, or another special path is relevant.

## Guardrails

- Do not vote, decide, score, rank, or assign `Approve`, `Decline`, `Approve with conditions`, or `Defer`.
- Do not call a proposal unique, unprecedented, or first-of-kind without a documented current TCIA search. Prefer `no exact match found in the searched TCIA metadata` and state the search limitations.
- Do not treat superficial keyword matches as comparators. Verify disease context, imaging type, population, supporting data, and dataset purpose from current TCIA metadata.
- Do not perform full clinical-data curation before AG review.
- Do not request patient-level data, imaging payloads, or protected health information for this review.
- Always ask whether year of diagnosis is available when clinical data are expected, but treat its absence as a limitation to document rather than an automatic rejection.
- Do not provide feedback on the DSA's organization fields, notice information, signatures, dates, legal terms, completeness, or execution status. The DSA is supplied early for legal review and is expected to be signed only after AG approval.
- Do not infer proposal readiness from the identity of the legal point of contact or from the DSA's completion status.
- Treat the NCI Imaging Submission Model used by the remapper as recommended guidance, not a current hard requirement.
- Do not claim that TCIA certifies the scientific accuracy of submitted annotations or analyses.
