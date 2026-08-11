---
name: tcia-remapping-skill
description: Guide users after TCIA proposal approval through completing dataset-level metadata and mapping supporting clinical or tabular data to the recommended NCI Imaging Submission Model. Use when importing a TCIA proposal package, drafting a CICADAS-aligned description, mapping source columns, reviewing permissible values, or generating standardized TSVs. Treat the model as recommended guidance rather than a hard submission requirement.
---

# Remap TCIA Supporting Data

## Overview
Assist users after proposal approval in organizing supporting clinical or tabular data according to the recommended NCI Imaging Submission Model. Use medical ontologies and a structured conversational flow to improve mapping consistency without presenting the model as a hard TCIA submission requirement.

## Target Data Model
The skill target consists of 12 potential TSV files defined in the `resources/schema.json` file:
- Program, Dataset, Subject, Procedure, File, Diagnosis, Investigator, Related_Work, Radiology, Histopathology, Multiplex_Imaging, Multiplex_Channels.

## Conversational Workflow
To minimize user effort, the skill follows a tiered approach:

### Phase 0: Dataset-Level Metadata Collection
Before remapping any source files, collect high-level metadata for the submission.

1. **Sequential Interview**: Collect information in the following order:
   - **Start (Import)**: Offer the user the option to import an existing TCIA Proposal package (ZIP or TSV). If provided, use the `import_proposal` logic to pre-populate all subsequent fields.
   - **Program**: Focus on `program_name` and `program_short_name` (Required). **Steering**: Most users should be directed to use "Community" as their program unless they are part of a major NCI/NIH program (e.g., TCGA, CPTAC, APOLLO, Biobank).
   - **Dataset**: Focus on `dataset_long_name` and `dataset_short_name` (Required).
   - **CICADAS**: Guide the user through the [CICADAS checklist](https://cancerimagingarchive.net/cicadas) to generate a high-quality `dataset_abstract` and `dataset_description`. Use the current public checklist rather than requiring a separate bundled skill.
   - **Investigator**: Collect details for one or more investigators. Ask for `first_name`, `last_name`, `email`, and `organization_name` (Required). Support multiple entries and ORCID lookups.
   - **Related_Work**: Collect `DOI`, `title`, `publication_type`, and `relationship_type` (Required). Support multiple entries and DOI lookups.

2. **Handling Missing Info**: If a required field is missing, prompt the user. If they don't have the information, acknowledge it and proceed to the next step.

3. **Recap & Generation**:
   - Provide a recap of all collected metadata for user review.
   - After approval, generate the corresponding TSV files (`program.tsv`, `dataset.tsv`, `investigator.tsv`, `related_work.tsv`) using the `write_metadata_tsv` function.

### Phase 1: Structure Mapping & Organization
1. **Initiation**: Ask the user to upload their source data files.
2. **Analysis**: Identify existing columns and how they relate to the target entities.
3. **Summary Recommendation**: Provide a concise summary of the proposed mapping (e.g., "Source 'PtID' -> Target 'subject_id'").
4. **Quick Approval**: Allow the user to approve the entire structure mapping at once (e.g., "Everything looks good!") or flag specific items for discussion (e.g., "Discuss items 2 and 5").

### Phase 2: Value Standardization (Permissible Values)
Once the structure is confirmed, address data content one TSV/column at a time:
1. **Batch Validation**: For each confirmed column, identify values that do not match the permissible lists in `resources/permissible_values.json`.
2. **Ontology-Enhanced Matching**: Use both fuzzy matching and knowledge of medical ontologies (NCIt, SNOMED, UBERON) to suggest corrections.
3. **Focussed Discussion**: Present a summary of auto-corrected values for quick approval, and list only the "hard" cases that need manual user intervention.
4. **Handling "NOS"**: If a value is "NOS" (Not Otherwise Specified), suggest the most appropriate standard term from the ontology.

## Key Rules
- **Ontology Integration**: When a direct match is missing, use NCIt or UBERON codes (found in `permissible_values.json`) to verify if a user's term is a synonym of a standard term.
- **Tiered Interaction**: Always provide a summary first. Don't ask about 100 values one by one; group them.
- **Required Fields**: Prioritize fields marked "R" in `schema.json`.
- **Conflict Resolution**: If an uploaded file contains data that contradicts previously provided metadata (e.g., a different Program Name), use `check_metadata_conflict` to alert the user. Ask them to confirm which value is correct.

## Examples
### Example: Tiered Approval
Assistant: "I've mapped your 15 columns to the Subject and Diagnosis TSVs. Here is the summary: [Table]. Does this look good, or should we adjust specific mappings?"
User: "Looks good, proceed to values."
Assistant: "Great. In 'primary_site', I've auto-matched 90% of your values. I have 3 values that need your attention: 'Lung, NOS', 'Chest wall', and 'Unknown'. Recommendations: [List]. How should we handle these?"

## Resources
- `resources/model/`: NCI Imaging Submission Model files (MDF YAML format).
- `resources/schema.json`: Legacy property definitions (fallback).
- `resources/permissible_values.json`: Legacy valid values with ontology metadata (fallback).
- `mdf_parser.py`: Parser for the MDF model files.
- `remap_helper.py`: Utility script for fuzzy matching, data splitting, and conflict checking.
- `orcid_helper.py`: Utility for ORCID profile lookups and author parsing.
