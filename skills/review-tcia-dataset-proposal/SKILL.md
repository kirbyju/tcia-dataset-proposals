---
name: review-tcia-dataset-proposal
description: Review a TCIA new-collection or analysis-results proposal package, including its TSV or DOCX summary, Data Submission Agreement, preprints, publications, and supporting documents. Use when a submitter or TCIA reviewer wants a source-grounded summary of the proposed dataset, gaps or ambiguities to clarify before TCIA Advisory Group review, CICADAS alignment suggestions, AG-criteria coverage, or PI-ready follow-up questions. Do not make an approval decision or perform post-approval data curation.
---

# Review a TCIA Dataset Proposal

## Objective

Help a submitter or reviewer assemble enough evidence for an informed TCIA Advisory Group (AG) review. Extract information already present across the package before asking for it again. Summarize gaps and draft constructive clarification questions. Do not predict, assign, or recommend a proposal status.

## Load the references

- Read [proposal-package.md](references/proposal-package.md) when inventorying an uploaded proposal package or determining the proposal type.
- Read [review-criteria.md](references/review-criteria.md) for every substantive review.
- Read [cicadas.md](references/cicadas.md) when evaluating description completeness or drafting improvement suggestions.
- Read [nctn.md](references/nctn.md) when the proposal mentions an NCTN or NCORP trial, a cooperative group, CTEP, IROC, or CIP-directed publication.

## Workflow

1. Inventory the package.
   - List the ZIP members or uploaded files without exposing contact details in the response.
   - Locate the proposal TSV or DOCX, DSA PDF, preprints or manuscripts, data dictionaries, and other supporting documentation.
   - State which expected materials were not supplied. Treat a preprint as recommended, not mandatory.

2. Extract evidence before identifying gaps.
   - Read the complete proposal summary and relevant supporting documents.
   - Follow supplied publication, preprint, DOI, repository, and dataset links when accessible.
   - Record the source and location for each material claim.
   - Reuse evidence found in a preprint or publication instead of asking the submitter to repeat it.

3. Determine the review path.
   - Classify the proposal as a new primary-data Collection or an Analysis Result derived from existing image data.
   - Detect possible NCTN/NCORP provenance and apply the NCTN authorization check.
   - Note a CIP-directed NCTN route separately because it does not require an AG vote.

4. Assess information coverage.
   - Compare the evidence with the AG criteria in `review-criteria.md`.
   - Compare the description with the proposal-stage interpretation of CICADAS in `cicadas.md`.
   - Distinguish information that is absent from information that is merely located in another supplied source.
   - Do not require exhaustive acquisition parameters when exact details are carried in DICOM or other data. Ask for a concise acquisition summary only when it helps explain scientific value, heterogeneity, limitations, or reuse.

5. Draft clarification questions.
   - Ask only questions whose answers would materially improve the AG's understanding.
   - Explain briefly why each question matters.
   - Separate questions that should be answered before AG review from optional description improvements.
   - Phrase questions for the scientific point of contact or PI in neutral, collaborative language.

6. Produce the review.
   - Use the output structure below.
   - Cite the proposal or supporting source for statements of fact.
   - Keep personal contact details out of the review unless the user explicitly requests them.

## Output structure

### Proposal snapshot

Summarize the proposal type, dataset purpose, approximate scale, imaging and supporting-data types, related TCIA Collections, and supplied supporting materials.

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
- Do not perform full clinical-data curation before AG review.
- Do not request patient-level data, imaging payloads, or protected health information for this review.
- Always ask whether year of diagnosis is available when clinical data are expected, but treat its absence as a limitation to document rather than an automatic rejection.
- Treat the legal point of contact and generated DSA as intentional early institutional-readiness checks.
- Treat the NCI Imaging Submission Model used by the remapper as recommended guidance, not a current hard requirement.
- Do not claim that TCIA certifies the scientific accuracy of submitted annotations or analyses.
