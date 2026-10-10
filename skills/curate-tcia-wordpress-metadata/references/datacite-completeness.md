# DataCite completeness and consistency

Use this reference for a supplied DOI registration draft, a post-release DOI review, or a corpus-wide TCIA DOI audit. Read the current DataCite Metadata Schema documentation rather than freezing its controlled lists in this skill. Record the schema version, DataCite retrieval time, TCIA query provenance, and WordPress snapshot/fingerprint.

## Establish the audit cohort

- For one dataset, resolve the canonical current WordPress Collection or Analysis Result, normalize its DOI, and retrieve that exact live DataCite record.
- For a corpus audit, enumerate records owned by the current TCIA DataCite client/repository and join them to current visible WordPress DOI values. Include every DOI prefix represented in WordPress; do not assume the historical `10.7937` prefix is exhaustive.
- Report DataCite records without a current WordPress match and WordPress DOI values without a DataCite match separately. Neither condition alone proves an error; retired, staged, migrated, or externally registered records may require curator interpretation.
- Compare current records with current records. Do not mix a historical WordPress version with live DataCite metadata without stating the version boundary.

## Classify completeness correctly

Use the obligation level from the current DataCite schema:

- **Schema-mandatory:** Identifier/DOI, Creator, Title, Publisher, PublicationYear, and ResourceType including its required general type. A missing, empty, placeholder, or structurally invalid value is `change recommended`.
- **Schema-recommended:** Subject, Contributor, Date, RelatedIdentifier, Description, and GeoLocation. Absence is not automatically an error. Description with `descriptionType=Abstract` is the highest-priority recommended element for a TCIA dataset.
- **Schema-optional:** fields such as Language, AlternateIdentifier, Size, Format, Version, Rights, FundingReference, and RelatedItem. Optional status does not prevent TCIA from adopting a stronger local baseline.

Do not equate an empty JSON array with a populated property. Validate nonblank values, required sub-properties, cardinality, identifier syntax, controlled values, and internally consistent schemes/URIs.

## TCIA baseline and parity checks

For current TCIA dataset DOIs, check these fields even when DataCite marks them optional:

- DOI state is findable unless the review explicitly concerns a draft or registered record.
- Publisher uses the current canonical TCIA publisher name.
- `resourceTypeGeneral` accurately represents the release; normally this is `Dataset` for a TCIA Collection or Analysis Result. Treat legacy alternatives as review findings, not automatic replacements.
- Title is materially consistent with the current WordPress title and does not omit a meaning-changing qualifier. Cosmetic punctuation or an appended short name is not a failure.
- URL is the public canonical landing page, not a preview, staging, query-string, or obsolete route.
- AlternateIdentifier includes the exact TCIA Short Name with the correct identifier type.
- Version is present and agrees with the current WordPress dataset version when both systems describe the same version scope. If the two systems use different version semantics, use `needs curator decision` and explain the distinction.
- Rights describe every current access/license regime that should appear in the DOI record and use consistent rights identifiers and URIs where available. Compare against WordPress, but account for downloads with different licenses before recommending a change.
- Descriptions include a nonblank Abstract that remains materially consistent with the current dataset description.
- Personal creator/contributor names use structured given/family names when known. ORCID-shaped identifiers must use the ORCID scheme and URI rather than a generic scheme.

Apply conditional checks only when supported:

- An Analysis Result derived from identifiable source datasets should encode the appropriate DOI relationships, normally `IsDerivedFrom`, for each supported source DOI.
- Use version relationships when separate DOI records represent versions and the relationship is verified.
- Populate Contributor, Date, Subject, FundingReference, GeoLocation, Size, Format, Language, or RelatedItem only when the release metadata supplies a defensible value. Do not manufacture values to increase field coverage.

## Detect corpus outliers

For a corpus-wide review, calculate nonblank coverage for each property over current WordPress-linked DOI records. Report:

1. all schema-mandatory failures;
2. all TCIA baseline failures and WordPress/DataCite parity conflicts;
3. fields populated in at least 90% of the cohort with every missing instance; and
4. recommended or conditional fields below that threshold as coverage observations, not blanket remediation items.

The 90% threshold identifies local-practice outliers; it does not change DataCite's obligation levels. Show the numerator, denominator, percentage, cohort definition, and retrieval date so curators can reproduce the result.

## Status and remediation rules

- Use `change recommended` for a confirmed mandatory omission, invalid controlled value, nonpublic landing URL, missing TCIA baseline field, or clear current-record conflict.
- Use `needs curator decision` for legacy values, ambiguous version semantics, multiple download licenses, material title differences, or a relationship whose direction/scope needs domain review.
- Use `pass` only after checking both presence and value.
- Use `not applicable` only when the concept does not apply.
- Use `unable to verify` when the relevant DataCite/WordPress record or comparison evidence is unavailable.

Keep DataCite event metrics separate from TCIA download totals. DataCite views/downloads/citations describe DataCite-tracked events and are not a substitute for WordPress or storage-derived download counts and sizes.
