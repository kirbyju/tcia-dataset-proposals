---
name: review-tcia-dataset-proposal
description: Guide TCIA dataset proposals and narrative documentation across the submission lifecycle. Use when a submitter or collaborator wants pre-submission self-review or CICADAS coaching; when TCIA staff, curators, or another reviewer needs a source-grounded Advisory Group review, current TCIA comparator analysis, CICADAS coverage, or PI-ready questions; or when staff and an accepted submitter need to finish a TCIA dataset abstract, description, or dataset-descriptor manuscript scaffold. Review new Collections and Analysis Results without making an approval decision. Exclude an early Data Submission Agreement PDF from proposal feedback and do not perform patient-level or full clinical-data curation.
---

# Review a TCIA Dataset Proposal

## Freshness gate — run first

Before reading the proposal package, loading references, or beginning any substantive review, run:

```bash
python3 "<this-skill-directory>/scripts/check_freshness.py" check --max-age-hours 24
```

Resolve `<this-skill-directory>` to the directory containing this `SKILL.md`. The script always verifies the installed files against the bundled checksum manifest. It contacts the public GitHub repository only when there is no cached result for this installed version or the cached check is at least 24 hours old.

- On `current` or `current_cached`, continue with the review.
- On `update_required` or `local_modified`, stop before reviewing the package. Tell the user that the installed skill is not current, include the reported local and remote versions or changed files, and direct them to the reported `update_url` to reinstall or update the skill.
- On `unverified`, do not imply that the installed guidance is current. Report the network or verification error and retry when GitHub access is available. Proceed only if the user explicitly accepts using unverified guidance.

Do not replace this gate with a per-question GitHub request, and do not silently use remote `SKILL.md` content with older installed references or scripts.

## Objective

Help submitters, collaborators, TCIA staff, curators, and other reviewers prepare or evaluate a proposal and progressively complete its dataset-level narrative documentation. Extract information already present across the package before asking for it again. Summarize gaps, improve supported text, and draft constructive clarification questions. Do not predict, assign, or recommend a proposal status.

Treat CICADAS completion as progressive. A finished CICADAS description is not expected before proposal or AG review. Early CICADAS information can improve the review and reduce later documentation work, but incompleteness is not by itself a reason to delay submission or an adverse review finding. After acceptance, help staff and the submitter complete the narrative documentation needed for TCIA publication.

Ignore the Data Submission Agreement (DSA) PDF when reviewing the proposal or providing feedback. TCIA sends it early so the site's legal team can begin review; it is expected to remain incomplete and unsigned until after AG approval.

## Load the references

- Read [proposal-package.md](references/proposal-package.md) when inventorying an uploaded proposal package or determining the proposal type.
- Read [review-criteria.md](references/review-criteria.md) for every substantive review.
- Read [novelty-comparison.md](references/novelty-comparison.md) and perform its TCIA comparator search for every substantive review.
- Read [cicadas.md](references/cicadas.md) when evaluating description completeness or drafting improvement suggestions.
- Read [nctn.md](references/nctn.md) when the proposal mentions an NCTN or NCORP trial, a cooperative group, CTEP, IROC, or CIP-directed publication.

## Workflow

1. Determine the role and lifecycle stage.
   - Infer both from an explicit request. Otherwise ask two brief questions before substantive work:
     1. Are you a submitter or collaborator, a TCIA staff or curation-team member, or another reviewer?
     2. Is this before proposal submission, in preparation for AG review, or after acceptance while completing publication documentation?
   - Do not request names, contact details, credentials, or proof of role.
   - Treat a stated role as workflow context, not authentication or authorization to access nonpublic information.
   - Use submitter-facing coaching before submission, staff-facing evidence and PI-ready language before AG review, and collaborative documentation completion after acceptance.
   - For another reviewer, ask what outcome they need and do not assume TCIA staff access or internal context.

2. Inventory the supplied materials.
   - List the ZIP members or uploaded files without exposing contact details in the response.
   - Locate the proposal TSV or DOCX, preprints or manuscripts, data dictionaries, and other supporting documentation.
   - Acknowledge a DSA only as an expected package artifact when needed for inventory; do not inspect, summarize, cite, or evaluate it.
   - State which expected proposal materials were not supplied. Treat a preprint as recommended, not mandatory, and never treat an incomplete or unsigned DSA as a missing proposal item.

3. Extract evidence before identifying gaps.
   - Read the complete proposal summary and relevant supporting documents.
   - Follow supplied publication, preprint, DOI, repository, and dataset links when accessible.
   - Record the source and location for each material claim.
   - Reuse evidence found in a preprint or publication instead of asking the submitter to repeat it.

4. Determine the review path.
   - Classify the proposal as a new primary-data Collection or an Analysis Result derived from existing image data.
   - Detect possible NCTN/NCORP provenance and apply the NCTN authorization check.
   - Note a CIP-directed NCTN route separately because it does not require an AG vote.
   - For description-only coaching or post-acceptance documentation, do not force a full AG review or novelty comparison unless requested.

5. Compare with existing TCIA datasets for a substantive proposal review.
   - Search current visible TCIA Collections and Analysis Results using the procedure in `novelty-comparison.md`.
   - Search first for the same disease or scientific cohort, then for overlap along individual axes such as anatomy, population, imaging type, longitudinal design, supporting data, annotations, and multi-omic linkage.
   - Inspect the closest candidates rather than relying on keyword-result counts.
   - State what each comparator shares with the proposal and what appears different.
   - Treat an absent exact match as evidence from the documented search, not proof that no comparable dataset exists anywhere.

6. Assess information coverage.
   - For a substantive proposal review, compare the evidence with the AG criteria in `review-criteria.md`.
   - For description review or drafting at any stage, compare the supplied information with `cicadas.md`.
   - Distinguish information that is absent from information that is merely located in another supplied source.
   - Do not require exhaustive acquisition parameters when exact details are carried in DICOM or other data. Ask for a concise acquisition summary only when it helps explain scientific value, heterogeneity, limitations, or reuse.

7. Improve CICADAS documentation when requested.
   - Use the coverage statuses and editorial rules in `cicadas.md`.
   - Preserve submitter meaning and include only confirmed facts in a clean draft. Keep unresolved questions or placeholders in a separate completion list or annotated draft.
   - Before submission, provide an improved draft and optional suggestions without implying that every CICADAS item must be complete.
   - Before AG review, separate material scientific clarifications from documentation improvements that can wait until after acceptance.
   - After acceptance, produce a clean TCIA-ready abstract and description plus a list of remaining submitter confirmations. When the repository workflow is available, route tabular-data mapping and persisted dataset metadata to `remap-tcia-supporting-data`.
   - If asked for a dataset-descriptor manuscript, use confirmed CICADAS content as source material and verify the target journal's current author instructions. Do not equate CICADAS alignment with journal compliance or acceptance.

8. Draft stage-appropriate clarification questions.
   - Ask only questions whose answers would materially improve the proposal review or final documentation.
   - Explain briefly why each question matters and when it needs to be resolved.
   - Before AG review, separate material questions from optional description improvements.
   - After acceptance, separate publication-documentation confirmations from optional manuscript enhancements.
   - Phrase questions for the submitter, scientific point of contact, or PI in neutral, collaborative language.

9. Produce the stage-appropriate result.
   - Use the output structure below.
   - Cite the proposal or supporting source for statements of fact.
   - Keep personal contact details out of the review unless the user explicitly requests them.

## Output structure

Use only the sections applicable to the selected workflow. Do not force AG-review sections into description-only coaching or post-acceptance documentation work.

### Role and workflow

State the inferred or confirmed role, lifecycle stage, and selected workflow. Omit personal details.

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

### CICADAS coverage and draft

Include when the user requests description review or drafting. Use the columns `CICADAS area`, `Status`, `Evidence location`, `Recommended action`, and `Timing`. Then provide the stage-appropriate deliverable:

- before submission: an improved draft and optional completion questions;
- before AG review: material clarifications separated from later documentation improvements; or
- after acceptance: a clean TCIA-ready abstract and description, followed by unresolved confirmations and, when requested, a dataset-descriptor manuscript scaffold.

### Routing note

Include only when NCTN/NCORP authorization, CIP-directed handling, facial-imaging risk, controlled access, or another special path is relevant.

## Guardrails

- Do not vote, decide, score, rank, or assign `Approve`, `Decline`, `Approve with conditions`, or `Defer`.
- Do not call a proposal unique, unprecedented, or first-of-kind without a documented current TCIA search. Prefer `no exact match found in the searched TCIA metadata` and state the search limitations.
- Do not treat superficial keyword matches as comparators. Verify disease context, imaging type, population, supporting data, and dataset purpose from current TCIA metadata.
- Do not perform full clinical-data curation before AG review.
- After acceptance, limit work to dataset-level narrative documentation unless the user invokes the separate remapping workflow for structured supporting data. Do not perform patient-level curation in this skill.
- Do not request patient-level data, imaging payloads, or protected health information for this review.
- Always ask whether year of diagnosis is available when clinical data are expected, but treat its absence as a limitation to document rather than an automatic rejection.
- Do not provide feedback on the DSA's organization fields, notice information, signatures, dates, legal terms, completeness, or execution status. The DSA is supplied early for legal review and is expected to be signed only after AG approval.
- Do not infer proposal readiness from the identity of the legal point of contact or from the DSA's completion status.
- Treat the NCI Imaging Submission Model used by the remapper as recommended guidance, not a current hard requirement.
- Do not claim that TCIA certifies the scientific accuracy of submitted annotations or analyses.
- Do not treat CICADAS incompleteness as a reason to reject, defer, or discourage a proposal.
- Do not treat a self-declared TCIA role as permission to inspect hidden, staged, retired, internal-review, controlled-access, or other nonpublic records.
- Do not claim that a CICADAS-aligned description satisfies a journal's author requirements without checking the current instructions for that journal.
