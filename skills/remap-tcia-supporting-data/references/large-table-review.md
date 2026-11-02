# Large supporting-table review

Use this approach when the file preflight in `SKILL.md` indicates a large or difficult input. There is no fixed file-size cutoff in this workflow: choose the strategy from the work required and the resources available. Distinguish file-access or upload failures, parser/memory failures, and excessive tool output; each needs a different remedy. Preserve the original workbook; review does not require converting or editing it.

## Inventory and select a reading strategy

- Record the filename, on-disk bytes, format, and available runtime. For XLSX, inspect ZIP directory metadata for total uncompressed size and large worksheet/shared-string members before parsing cells; do not extract everything just to measure it. Compressed size is not a memory estimate.
- Inventory worksheets, including hidden sheets, and identify dictionaries, notes, headers, and data tables with bounded previews. Label stored worksheet dimensions as reported; formatting or incorrect metadata can inflate or understate them. Verify data-row counts during a completed scan, with an explicit header/blank-row rule.
- Prefer a programmatic reader for data profiling. For XLSX, use `openpyxl.load_workbook(..., read_only=True)` and sequential row iteration, one worksheet at a time, closing the workbook afterward. Read-only mode reduces cell materialization but does not eliminate every memory cost, including shared strings. If dimensions conflict with observed content, investigate and use `reset_dimensions()` where justified rather than trusting them. Use a format-appropriate reader for XLS/XLSB; openpyxl is for XLSX-family files.
- For CSV/TSV, use `pandas.read_csv(..., chunksize=...)` or a streaming CSV parser. Preserve identifiers and source tokens as text where needed; avoid default missing-value conversion silently collapsing codes such as `NA`. Inspect raw headers before a reader renames duplicates. Count parsed records, not physical lines, because quoted fields can contain newlines.
- Do not assume `pandas.read_excel` supports CSV-style chunking. Avoid loading every worksheet into a dictionary of DataFrames, constructing a list of all streamed rows, or importing the whole workbook into a rendering tool solely to inspect values. Use bounded visual inspection only when layout carries meaning.

## Review in passes

1. **Structure and documentation.** Read the dictionary and notes first. Identify row meaning, header locations, identifier scope, units, missing-value conventions, and proposed links. Inspect all relevant fields, grouping very wide tables into column blocks rather than silently dropping columns.
2. **Programmatic profile.** Stream relevant data to compute row/nonblank counts, missingness under documented conventions, type/format inconsistencies, numeric ranges where meaningful, and code frequencies. Keep raw blanks and distinct missing-value tokens separate until their meanings are confirmed. Bound examples and in-memory counters; high-cardinality fields and exact duplicate/linkage checks may require disk-backed SQL or external sorting. Do not build unlimited Python sets or concatenate chunks back into one large table.
3. **Focused evidence.** Retrieve a few source rows for each material issue with worksheet, original row number, and column/header. For exploratory sampling, document the selection method and seed where applicable; include coverage beyond the first rows, such as a reservoir sample during a sequential scan. A preview or sample cannot establish whole-file missingness, uniqueness, permissible-value coverage, or linkage integrity.

Inspect formula expressions when relevant. With `data_only=True`, openpyxl returns cached results rather than calculating formulas; absent or stale caches are an evaluation limitation, not proof that the source value is missing. CSV exports can lose formulas, formatting, notes, and Excel display formats such as leading zeros; record such losses and retain the original if an intermediate export is necessary.

## Keep execution and reporting bounded

Write detailed profiles or issue tables to local artifacts and bring only compact summaries and selected evidence into the conversation. Retain exact source coordinates, tokens, counts, and parser settings needed to reproduce findings. Avoid printing every row, every distinct identifier, or thousands of repeated warnings. Keep review artifacts containing source data outside public repositories.

Use bounded jobs and report progress between passes or worksheets. After a timeout or memory failure, change strategy by reducing the scope of each job, streaming, or using disk-backed processing; do not repeat the same full-load attempt. If the environment cannot access or process the file, state the limitation and continue any supported dictionary/structure review. Request a local execution route or targeted worksheet export only when necessary to finish the requested checks. Never silently replace a requested full review with sampling.

Include a compact coverage table in the result: file/worksheet, fields and rows examined, check performed, full scan versus sample (with selection method), and checks skipped or incomplete with reasons. Separate reported dimensions, verified counts, and estimates. Only describe a check as complete when its intended scope finished successfully; a completed read alone is not complete clinical QC.

## Reader references

- [openpyxl optimized modes](https://openpyxl.readthedocs.io/en/stable/optimized.html): read-only iteration, explicit closing, and incorrect worksheet dimensions.
- [pandas read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html): chunked iteration, data types, missing-value handling, and header behavior.
