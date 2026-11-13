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
- Publisher uses the current canonical TCIA publisher name and its ROR identifier. Check structured publisher metadata as described below; the name alone does not establish an organization connection in Commons.
- `resourceTypeGeneral` accurately represents the release; normally this is `Dataset` for a TCIA Collection or Analysis Result. Treat legacy alternatives as review findings, not automatic replacements.
- Title is materially consistent with the current WordPress title and does not omit a meaning-changing qualifier. Cosmetic punctuation or an appended short name is not a failure.
- URL is the public canonical landing page, not a preview, staging, query-string, or obsolete route.
- AlternateIdentifier includes the exact TCIA Short Name with the correct identifier type.
- Version is present and agrees with the current WordPress dataset version when both systems describe the same version scope. If the two systems use different version semantics, use `needs curator decision` and explain the distinction.
- Rights describe every current access/license regime that should appear in the DOI record and use consistent rights identifiers and URIs where available. Compare against WordPress, but account for downloads with different licenses before recommending a change.
- Descriptions include a nonblank Abstract that remains materially consistent with the current dataset description.
- Apply the Subjects, Formats, Dates, and source-relationship checks below to each new release and each changed release, not only to legacy corpus backfills.
- Personal creator/contributor names use structured given/family names when known. ORCID-shaped identifiers must use the ORCID scheme and URI rather than a generic scheme.

Apply conditional checks only when supported:

- An Analysis Result derived from identifiable source datasets should encode the appropriate DOI relationships, normally `IsDerivedFrom`, for each supported source DOI.
- Use version relationships when separate DOI records represent versions and the relationship is verified.
- Populate Contributor, FundingReference, GeoLocation, Language, or RelatedItem only when the release metadata supplies a defensible value. Apply the explicit TCIA Subjects, Formats, and Dates baselines below. Size is not a routine TCIA backfill requirement; do not manufacture any value to increase coverage.

## Release enrichment checks

These are TCIA QC expectations for new dataset releases and release updates,
including Analysis Results. Distinguish local expectations from DataCite schema
obligations: Subjects and Dates are schema-recommended, Formats is optional,
and the publisher identifier is an optional sub-property. A missing supported
local-baseline value can merit `change recommended` without being a mandatory
schema error. Do not claim these additions guarantee a F-UJI score increase.

### Subjects: disease, location, species, and Data Category

Check `subjects` against the release's existing WordPress disease type, disease
location, species, and current primary-download **Data Category** labels.
The public API represents these as `cancer_types`, `cancer_locations`, `species`,
and standalone download `download_type` (or embedded `download type`). Examples
of exact category labels include `Radiology Images`, `Pathology Images`,
`Image Annotations`, and `Clinical Data`; use the actual source labels rather
than inventing alternative spellings.

Do not generate new subject keywords from dataset `data_types`, download
`data_type`, or embedded `data type` values such as `MR`, `CT`, `SEG`, or
`RTSTRUCT`. They remain technical data types rather than the chosen generalized
TCIA subject categories. Preserve existing DataCite subjects, including legacy
technical terms and verified controlled-vocabulary metadata; this policy does
not authorize deleting them. Add missing supported terms without duplicating
case/whitespace variants. Plain labels are valid subjects: add `subjectScheme`,
`schemeUri`, or `valueUri` only when the mapping is verified and supported.

### Formats: existing primary-download file types

Check the optional `formats` array against current primary-download WordPress
`file_type` / embedded `file type` values. Retain the existing declared labels,
including archive/container labels when WordPress supplies them; do not block
straightforward parity enrichment on MIME conversion or container-versus-payload
normalization. Preserve existing formats and identify unsupported conflicting
labels rather than silently replacing them. Do not use file-format strings as
subject Data Categories. An Analysis Result's linked source-image downloads do
not automatically become components of its own release; distinguish its primary
result downloads from reused source links before collecting formats.

### Dates: dataset release events, with history retained

For a supported published dataset-update date, check for an entry in `dates`
with `dateType=Updated` and the appropriate WordPress date/version scope.
A missing matching entry is a local enrichment finding; a documented scope
conflict or uncertain date meaning is `needs curator decision`. First-release
`Issued` dates can be recommended when an explicit release date is available;
do not invent one from an unrelated timestamp. Prefer the specific documented
date over duplicating only the already-recorded publication year.

Keep `publicationYear`, the version string, dataset lifecycle dates, WordPress
page-edit timestamps, and DataCite's automatic `created`, `registered`, and
`updated` record timestamps distinct. In particular, a DOI metadata edit does
not itself establish a new dataset release date. Preserve every earlier valid
date event and its `dateInformation`, including multiple `Updated` entries;
propose an additional missing event rather than replacing the history. Report
blank/invalid legacy entries separately. Compare semantic values rather than
treating absent optional keys and explicit JSON nulls as different dates.

### Qualified relationships: actual source data, not contextual citations

For `relatedIdentifiers`, verify the relation, target DOI, direction, and release
scope using the dataset's acquisition/analysis narrative and explicit source
provenance. Propose `IsDerivedFrom` for an Analysis Result only when the target
dataset actually supplied source data for that result. Preserve existing
relationships and do not infer reciprocal or version links without evidence.

A WordPress `Publication Citation` entry can be a merely related/background paper
that was intentionally not registered as a DataCite relationship. Its presence
and absence from DataCite alone are not a gap and do not justify `References`,
`IsCitedBy`, `IsDescribedBy`, or `IsDerivedFrom`. Recommend a publication relation
only when independent evidence establishes the specific connection. Distinguish
these contextual citations from TCIA's verified analytical-use bibliography.

Likewise, a generic related-Collection link or reuse of another dataset's
annotation protocol does not establish source-data derivation. Read the source
methods; do not promote every related Collection to `IsDerivedFrom`. If API bulk
relationship arrays are suspect, verify isolated records and their identity
before using them. Keep methodology/background links separate from source-image
or source-annotation provenance.

### Size, funding, and license boundaries

Do not recommend routine duplication of WordPress download sizes into DataCite
`sizes`; this field is outside the agreed TCIA backfill baseline. Its absence
alone is not a QC failure. Existing sizes can be checked for a demonstrated
scope/value conflict without summing overlapping components or inferring bytes.

Funding enrichment awaits the planned structured WordPress funding fields.
Do not turn blank `fundingReferences` into a release-blocking or mandatory-schema
failure, scrape acknowledgements into unverified funder/award assignments, or
assume those planned fields are already available. When structured funding
metadata is supplied, compare explicit funders, identifiers, and awards and
report supported discrepancies or gaps. Do not imply a historic corpus backfill
has been approved merely because a new release contains funding information.

For rights parity, retain download/component and version scope. A license
conflict requires a curator/rights decision; do not resolve it by dropping NC,
ND, SA, controlled-access restrictions, or by appending apparently conflicting
licenses indiscriminately. A source/derived DOI relationship or protocol reuse
alone does not establish inherited restrictions. No general publication or
reuse approval follows from a successful metadata comparison.

## Detect corpus outliers

For a corpus-wide review, calculate nonblank coverage for each property over current WordPress-linked DOI records. Report:

1. all schema-mandatory failures;
2. all TCIA baseline failures and WordPress/DataCite parity conflicts;
3. fields populated in at least 90% of the cohort with every missing instance, separating coverage observations from actionable policy findings; and
4. recommended or conditional fields below that threshold as coverage observations, not blanket remediation items.

The 90% threshold identifies local-practice outliers; it does not change DataCite's obligation levels or override the exclusions for sizes, contextual citations, and deferred funding enrichment. Show the numerator, denominator, percentage, cohort definition, and retrieval date so curators can reproduce the result.

## Status and remediation rules

- Use `change recommended` for a confirmed mandatory omission, invalid controlled value, nonpublic landing URL, missing TCIA baseline field, or clear current-record conflict.
- Use `needs curator decision` for legacy values, ambiguous version semantics, multiple download licenses, material title differences, or a relationship whose direction/scope needs domain review.
- Use `pass` only after checking both presence and value.
- Use `not applicable` only when the concept does not apply.
- Use `unable to verify` when the relevant DataCite/WordPress record or comparison evidence is unavailable.

Keep DataCite event metrics separate from TCIA download totals. DataCite views/downloads/citations describe DataCite-tracked events and are not a substitute for WordPress or storage-derived download counts and sizes.

## Publisher identity and DataCite Commons discovery

For TCIA-published records with publisher `The Cancer Imaging Archive`, recommend
`publisherIdentifier=https://ror.org/02qyzaf42`,
`publisherIdentifierScheme=ROR`, and `schemeUri=https://ror.org` in the publisher
object. The publisher name is schema-mandatory; the identifier is optional in
DataCite's schema but is a TCIA discovery baseline. Missing linkage is
`change recommended`, not a missing mandatory-property error. A conflicting
organization identifier or publisher name requires curator review rather than
automatic replacement. Do not add TCIA as an author or creator affiliation just
to make a publisher connection.

Retrieve live DOI metadata with `publisher=true&affiliation=true`; without these
parameters the API can omit identifier details. Do not diagnose a missing ROR
from a name-only default response. Check creator/contributor and publisher
identifiers separately, preserving the organizations' actual roles.

Commons organization pages show identifier-linked works, not a name search or a
complete repository inventory. Compare their results with the public DOI records
owned by the current TCIA repository account (`nihnci.tcia` as verified in November
2026), then join to current WordPress records for publication scope. Known TCIA
prefixes include `10.7937` and `10.25737`; re-enumerate the account rather than
freezing these as an exhaustive list. Counts may differ because of identifier
coverage, DOI state, organization relation filters, or indexing lag; do not
interpret a low Commons count as missing publications without checking these.

DataCite also connects works through the Member/Consortium Organization's ROR
setting in Fabrica. Check that account hierarchy separately; a repository under
NIH/NCI does not authorize replacing the parent organization's identifier with
TCIA's. Account settings are not a substitute for correct DOI publisher metadata.

The skill remains recommendation-only. A QC report does not authorize DOI
updates or account-profile changes. Any separately authorized repair must
preserve unrelated metadata and date/relationship history, distinguish approval
from verified application, and keep credentials, backups, and curator worklists
outside version control. New DOI creation should include publisher identifiers
so that a corpus backfill is not repeatedly needed.

Sources:

- [Connecting organizations in DOI metadata](https://support.datacite.org/docs/connecting-to-organizations)
- [Organization connection criteria in Commons](https://support.datacite.org/docs/organizations-in-datacite-commons)
- [API publisher/affiliation identifier representation](https://support.datacite.org/docs/datacite-rest-api-affiliation-and-publisher-default-change)
- [DataCite Subject property](https://datacite-metadata-schema.readthedocs.io/en/4.7/properties/subject/)
- [DataCite Format property](https://datacite-metadata-schema.readthedocs.io/en/4.7/properties/format/)
- [DataCite Date property](https://datacite-metadata-schema.readthedocs.io/en/4.7/properties/date/)
- [DataCite RelatedIdentifier property](https://datacite-metadata-schema.readthedocs.io/en/4.7/properties/relatedidentifier/)
