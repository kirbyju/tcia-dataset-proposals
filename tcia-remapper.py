import streamlit as st
import pandas as pd
import json
import re
import os
import hashlib

from tcia_proposals import crdc_converter, orcid_helper, remap_helper
from tcia_proposals.mdf_parser import get_mdf_resources
from tcia_proposals.summary_document import generate_summary_docx

# Import functions
load_json = remap_helper.load_json
validate_dataframe = remap_helper.validate_dataframe
split_data_by_schema = remap_helper.split_data_by_schema
check_metadata_conflict = remap_helper.check_metadata_conflict
check_missing_links = remap_helper.check_missing_links

st.set_page_config(page_title="NCI Imaging Submission Validator", layout="wide")

# Load resources
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'tcia_proposals', 'resources')
SCHEMA_FILE = os.path.join(RESOURCES_DIR, 'schema.json')
PERMISSIBLE_VALUES_FILE = os.path.join(RESOURCES_DIR, 'permissible_values.json')

# Default programs with complete metadata
DEFAULT_PROGRAMS = {
    "Community": {
        "program_name": "Community",
        "program_short_name": "Community",
        "institution_name": "",
        "program_short_description": "Community-contributed imaging collections",
        "program_full_description": "The Community program encompasses imaging collections contributed by individual researchers and institutions that are not part of larger organized programs.",
        "program_external_url": "https://www.cancerimagingarchive.net/"
    },
    "TCGA": {
        "program_name": "The Cancer Genome Atlas",
        "program_short_name": "TCGA",
        "institution_name": "National Cancer Institute",
        "program_short_description": "A landmark cancer genomics program",
        "program_full_description": "The Cancer Genome Atlas (TCGA) is a landmark cancer genomics program that molecularly characterized over 20,000 primary cancer and matched normal samples spanning 33 cancer types.",
        "program_external_url": "https://www.cancer.gov/tcga"
    },
    "CPTAC": {
        "program_name": "Clinical Proteomic Tumor Analysis Consortium",
        "program_short_name": "CPTAC",
        "institution_name": "National Cancer Institute",
        "program_short_description": "A comprehensive and coordinated effort to accelerate proteogenomic cancer research",
        "program_full_description": "The Clinical Proteomic Tumor Analysis Consortium (CPTAC) is a comprehensive and coordinated effort to accelerate the understanding of the molecular basis of cancer through the application of large-scale proteome and genome analysis (proteogenomics).",
        "program_external_url": "https://proteomics.cancer.gov/programs/cptac"
    },
    "APOLLO": {
        "program_name": "Applied Proteogenomics OrganizationaL Learning and Outcomes",
        "program_short_name": "APOLLO",
        "institution_name": "National Cancer Institute",
        "program_short_description": "Network for proteogenomic characterization of cancer",
        "program_full_description": "The Applied Proteogenomics OrganizationaL Learning and Outcomes (APOLLO) Network aims to generate proteogenomic data and develop analytical tools to advance precision oncology.",
        "program_external_url": "https://proteomics.cancer.gov/programs/apollo-network"
    },
    "Biobank": {
        "program_name": "Cancer Imaging Biobank",
        "program_short_name": "Biobank",
        "institution_name": "",
        "program_short_description": "Organized collections of cancer imaging data",
        "program_full_description": "The Cancer Imaging Biobank program organizes and maintains curated collections of cancer imaging data for research purposes.",
        "program_external_url": "https://www.cancerimagingarchive.net/"
    }
}

def lookup_orcid(orcid_id):
    """Fetch metadata from ORCID API using orcid_helper"""
    profile = orcid_helper.get_orcid_profile(orcid_id)
    if profile:
        return {
            'first_name': profile.get('given_names', ''),
            'last_name': profile.get('family_name', ''),
            'organization': profile.get('organization', '')
        }
    return None

@st.cache_data
def load_resources():
    # Try loading from MDF first
    schema, mdf_pv, relationships = get_mdf_resources(RESOURCES_DIR)

    # Load legacy permissible values
    legacy_pv = load_json(PERMISSIBLE_VALUES_FILE)

    if schema:
        # Merge permissible values: MDF Enums take precedence, but legacy covers missing ones
        final_pv = legacy_pv.copy()
        if mdf_pv:
            for k, v in mdf_pv.items():
                final_pv[k] = v
        return schema, final_pv, relationships

    # Fallback to legacy JSON files
    st.warning("⚠️ Using legacy schema files. MDF model files not found or invalid.")
    schema = load_json(SCHEMA_FILE)
    return schema, legacy_pv, {}

def reset_app():
    """Reset all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Each visit starts with a choice of task. Neither workflow requires the other.
if 'workflow' not in st.session_state:
    st.session_state.workflow = None
    st.session_state.metadata = {entity: [] for entity in ('Program', 'Dataset', 'Investigator', 'Related_Work')}
    st.session_state.proposal_raw_data = {}
    st.session_state.uploaded_data = None
    st.session_state.column_mapping = {}
    st.session_state.structure_approved = False
    st.session_state.output_dir = 'output'

st.title("NCI Imaging Submission Validator")

if st.session_state.workflow is None:
    st.header("What would you like to do?")
    with st.container(border=True):
        st.subheader("Generate curation documents and summary metadata")
        st.write("Import a TCIA proposal package or CRDC workbook, review the investigators, "
                 "and download the internal tracking document, imaging model TSV package, and CRDC Excel workbook.")
        if st.button("Generate curation outputs", type="primary", width="stretch"):
            st.session_state.workflow = 'curation'
            st.rerun()
    with st.container(border=True):
        st.subheader("Generate or standardize tabular supporting data")
        st.write("Map source columns to the NCI Imaging Submission Model, review supported values, "
                 "and generate standardized TSV files.")
        if st.button("Remap supporting data", width="stretch"):
            st.session_state.workflow = 'remap'
            st.rerun()
    st.stop()

st.sidebar.title("Your task")
st.sidebar.write("Curation outputs" if st.session_state.workflow == 'curation' else "Supporting data remapper")
if st.sidebar.button("Change task"):
    st.session_state.workflow = None
    st.rerun()
if st.sidebar.button("Reset app"):
    reset_app()
    st.rerun()

schema, permissible_values, relationships = load_resources()

if st.session_state.workflow == 'curation':
    from tcia_proposals.curation_workflow import (
        INVESTIGATOR_COLUMNS, build_model_package, import_proposal, investigator_warnings,
        metadata_gaps, normalize_investigators, parse_authors,
    )
    st.header("Curation documents and summary metadata")
    st.caption("Import proposal → Review investigators → Download outputs")
    st.subheader("1. Import proposal")
    upload = st.file_uploader("Import proposal package (TCIA TSV/ZIP or CRDC XLSX)", type=['tsv', 'zip', 'xlsx'])
    if upload is None:
        st.info("Import a proposal to begin.")
        st.stop()
    proposal_type = 'New Collection Proposal'
    if upload.name.lower().endswith('.xlsx'):
        proposal_type = st.selectbox("TCIA proposal type", ['New Collection Proposal', 'Analysis Results Proposal'],
                                    help="The CRDC workbook does not identify the TCIA proposal type.")
    payload = upload.getvalue()
    fingerprint = hashlib.sha256(payload).hexdigest() + ':' + proposal_type
    try:
        if st.session_state.get('imported_proposal_fingerprint') != fingerprint:
            proposal, metadata = import_proposal(payload, upload.name, DEFAULT_PROGRAMS['Community'], proposal_type)
            st.session_state.proposal_raw_data = proposal
            st.session_state.metadata = metadata
            st.session_state.investigator_draft = metadata['Investigator']
            st.session_state.investigator_revision = 0
            st.session_state.confirmed_investigators = None
            st.session_state.imported_proposal_fingerprint = fingerprint
            st.session_state.pop('orcid_preview', None)
    except Exception as exc:
        st.error(f"Import failed: {exc}")
        st.stop()

    proposal = st.session_state.proposal_raw_data
    st.success(f"Imported: {proposal.get('Title') or proposal.get('Nickname')}")
    st.subheader("2. Review investigators")
    st.write("Names and ORCID identifiers have been separated into structured fields. "
             "Check the given and family names, affiliations, and author order before confirming.")
    with st.expander("Original author list and parsing options"):
        raw_authors = st.text_area("Raw author list", value=proposal.get('Authors', ''), key=f'raw_authors_{fingerprint}',
                                  help="Separate authors with semicolons or new lines. Parsing replaces the review table.")
        strategy = st.selectbox("Parsing strategy", ['Auto-detect', 'Family, Given', 'Given Family'])
        if st.button("Parse author list"):
            st.session_state.investigator_draft = parse_authors(raw_authors, strategy)
            st.session_state.investigator_revision += 1
            st.session_state.confirmed_investigators = None
            st.rerun()
    draft = pd.DataFrame(st.session_state.investigator_draft)
    for column in INVESTIGATOR_COLUMNS:
        if column not in draft:
            draft[column] = pd.Series(dtype='int64' if column == 'author_order' else 'str')
    edited = st.data_editor(draft, num_rows='dynamic', width="stretch",
                            key=f'investigators_{fingerprint}_{st.session_state.investigator_revision}',
                            column_order=INVESTIGATOR_COLUMNS,
                            column_config={'author_order': st.column_config.NumberColumn('Author order', min_value=1, step=1),
                                           'first_name': 'Given name(s)', 'last_name': 'Family name',
                                           'person_orcid': 'ORCID', 'organization_name': 'Organization', 'email': 'Email'})
    reviewed = normalize_investigators(edited.to_dict('records'))
    for warning in investigator_warnings(reviewed):
        st.warning(warning)
    st.caption("For names with multiple words or group authors, check the split against the original list. "
               "Blank or uncertain fields can remain for later follow-up.")

    with st.expander("Look up an investigator by ORCID"):
        orcid_value = st.text_input("ORCID identifier", key=f'orcid_lookup_{fingerprint}')
        if st.button("Look up ORCID"):
            identifier = orcid_value.strip().removeprefix('https://orcid.org/').removeprefix('http://orcid.org/')
            if not orcid_helper.valid_orcid(identifier):
                st.error("Enter an ORCID with a valid format and checksum.")
            else:
                with st.spinner("Looking up the public ORCID profile…"):
                    profile = lookup_orcid(identifier)
                st.session_state.orcid_preview = (identifier, profile) if profile else None
                if not profile:
                    st.warning("No public profile was found. You can keep the supplied names in the review table.")
        preview = st.session_state.get('orcid_preview')
        if preview:
            identifier, profile = preview
            st.write(profile)
            if reviewed:
                row_number = st.selectbox("Apply to investigator", range(len(reviewed)),
                                          format_func=lambda i: f"{i + 1}. {reviewed[i].get('first_name', '')} {reviewed[i].get('last_name', '')}")
                if st.button("Use profile for selected investigator"):
                    updated = reviewed[row_number].copy()
                    updated['person_orcid'] = identifier
                    for target, source in [('first_name', 'first_name'), ('last_name', 'last_name'), ('organization_name', 'organization')]:
                        if profile.get(source):
                            updated[target] = profile[source]
                    reviewed[row_number] = updated
                    st.session_state.investigator_draft = reviewed
                    st.session_state.investigator_revision += 1
                    st.session_state.confirmed_investigators = None
                    st.rerun()

    signature = json.dumps(reviewed, sort_keys=True)
    if st.button("Confirm investigators and generate outputs", type="primary"):
        st.session_state.metadata['Investigator'] = reviewed
        st.session_state.confirmed_investigators = signature
    if st.session_state.get('confirmed_investigators') != signature:
        st.info("Confirm the investigator list to generate the curation outputs.")
        st.stop()

    st.subheader("3. Download outputs")
    st.caption("These drafts use the imported answers and confirmed investigators. "
               "Missing information is reported here for later follow-up; it does not need to be completed in this app.")
    metadata = st.session_state.metadata
    workbook, crdc_warnings = crdc_converter.build_crdc_workbook(proposal, metadata)
    import_gaps = metadata_gaps(proposal, metadata, upload.name)
    crdc_warnings = [note for note in import_gaps if note.startswith('CRDC import —')] + crdc_warnings
    gaps = [note for note in import_gaps if not note.startswith('CRDC import —')]
    if gaps:
        with st.container(border=True):
            st.write("**Information gaps and export notes**")
            for warning in gaps:
                st.warning(warning)
    nickname = metadata['Dataset'][0].get('dataset_short_name') or 'dataset'
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '-', nickname)
    try:
        summary = generate_summary_docx(metadata, proposal, {}, allow_label_placeholders=True)
        st.download_button("Download TCIA curation tracking document", data=summary.getvalue(),
                           file_name=f'{safe_name}_curation_tracking.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    except ValueError as exc:
        st.error(f"Tracking document label review required: {exc}")
        st.caption("Unrecognized labels are not silently replaced. The TSV package and CRDC workbook remain available.")
    st.download_button("Download TSV imaging model package", data=build_model_package(metadata, schema, relationships, safe_name),
                       file_name=f'{safe_name}_imaging_model.zip', mime='application/zip')
    crdc_downloaded = st.download_button("Download CRDC proposal workbook", data=workbook,
                       file_name=f'{safe_name}_CRDC_Submission_Request_v3.5.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if crdc_downloaded:
        with st.container(border=True):
            st.write('**CRDC workbook export notes**')
            for warning in crdc_warnings:
                st.warning(warning)

elif st.session_state.workflow == 'remap':
    st.header("Supporting data remapper")
    st.caption("The NCI Imaging Submission Model is recommended guidance for TCIA supporting data.")
    os.makedirs(st.session_state.output_dir, exist_ok=True)
    st.markdown("""
    Upload your source data files, map your columns, and standardize your values.
    """)

    # File upload
    uploaded_file = st.file_uploader(
        "Upload your source data file (CSV, TSV, or Excel)",
        type=['csv', 'tsv', 'xlsx', 'xls']
    )

    if uploaded_file is not None:
        # Streamlit reruns reuse uploads; rewind and reset mappings for a new file.
        try:
            file_fingerprint = hashlib.sha256(uploaded_file.getvalue()).hexdigest() + ':' + uploaded_file.name
            if st.session_state.get('remap_fingerprint') != file_fingerprint:
                st.session_state.remap_fingerprint = file_fingerprint
                st.session_state.column_mapping = {}
                st.session_state.structure_approved = False
                st.session_state.uploaded_data = None
                for key in list(st.session_state):
                    if key.startswith('map_'):
                        del st.session_state[key]
            uploaded_file.seek(0)
            df = None
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.tsv'):
                df = pd.read_csv(uploaded_file, sep='\t')
            else:
                # Excel file
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                if len(sheet_names) > 1:
                    selected_sheet = st.selectbox("Select which sheet to process:", sheet_names)
                    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                else:
                    df = pd.read_excel(uploaded_file)

            if df is not None:
                # --- Basic Data Cleaning ---
                # 1. Drop completely empty rows and columns
                df = df.dropna(how='all').dropna(axis=1, how='all')

                # 2. Check for potential title rows (heuristic: first row has mostly NaNs)
                # If the first non-empty row has fewer non-NaN values than the next row,
                # it might be a title row.
                if len(df) > 1:
                    first_row_non_nans = df.iloc[0].count()
                    second_row_non_nans = df.iloc[1].count()
                    if first_row_non_nans == 1 and second_row_non_nans > 1:
                        st.info("💡 Detected a potential title row. Using the next row as header.")
                        new_header = df.iloc[1]
                        df = df[2:]
                        df.columns = new_header

                # 3. Strip whitespace from headers and string values
                df.columns = [str(c).strip() for c in df.columns]
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

                st.session_state.uploaded_data = df
                st.success(f"✅ Loaded data with {len(df)} rows and {len(df.columns)} columns")

                # Show preview
                with st.expander("Preview Data", expanded=True):
                    st.dataframe(df.head(10))

            st.markdown("---")
            st.subheader("Column Mapping")
            st.markdown("Map your source columns to the target properties.")

            # Get all target properties from schema
            all_properties = {}
            excluded_entities = list(st.session_state.metadata.keys())

            for entity_name, properties in schema.items():
                if entity_name in excluded_entities:
                    continue
                for prop in properties:
                    prop_name = prop['Property']
                    # Hide linkage properties (containing a dot) from the mapping UI
                    # These are automatically handled based on primary ID mappings
                    if "." in prop_name:
                        continue
                    # print(f"DEBUG: prop_name={prop_name}")
                    all_properties[f"{entity_name}.{prop_name}"] = prop

            # Create mapping interface
            st.write("**Map Source Columns to Target Properties:**")

            mapping_data = []
            for col in df.columns:
                cols = st.columns([3, 4, 2])
                with cols[0]:
                    st.write(f"**{col}**")
                    # Show sample values
                    sample_vals = df[col].dropna().unique()[:3]
                    st.caption(f"Sample: {', '.join(map(str, sample_vals))}")

                with cols[1]:
                    # Get current mapping if exists
                    current_mapping = None
                    for target, source in st.session_state.column_mapping.items():
                        if source == col:
                            current_mapping = target
                            break

                    # Property selector
                    property_options = ["(Skip this column)"] + list(all_properties.keys())
                    default_index = 0
                    if current_mapping and current_mapping in property_options:
                        default_index = property_options.index(current_mapping)

                    selected = st.selectbox(
                        "Target Property",
                        options=property_options,
                        index=default_index,
                        key=f"map_{col}",
                        label_visibility="collapsed"
                    )

                    if selected != "(Skip this column)":
                        mapping_data.append((selected, col))

                with cols[2]:
                    if selected != "(Skip this column)" and selected in all_properties:
                        prop_info = all_properties[selected]
                        if prop_info.get('Required/optional') == 'R':
                            st.write("✅ Required")
                        else:
                            st.write("⚪ Optional")

            st.markdown("---")

            if st.button("✅ Confirm Mapping", type="primary"):
                # Save mapping
                st.session_state.column_mapping = {target: source for target, source in mapping_data}
                st.session_state.structure_approved = True
                st.success("✅ Column mapping confirmed!")
                st.info("Scroll down to standardize values.")

                # Check for conflicts with imported proposal metadata
                conflicts = check_metadata_conflict(st.session_state.metadata, df, st.session_state.column_mapping)
                if conflicts:
                    st.warning("⚠️ Detected conflicts between uploaded data and imported proposal metadata:")
                    for conflict in conflicts:
                        st.write(f"- {conflict['entity']}.{conflict['property']}: Initial='{conflict['initial_value']}' vs New='{conflict['new_value']}'")
                    st.write("Please review and update either your imported proposal metadata or your uploaded data.")

            # Show proceed button if mapping is approved
            if st.session_state.structure_approved:
                st.info("✅ Column mapping confirmed! Scroll down to standardize values.")

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.info("👆 Please upload a file to begin structure mapping.")

    # --- Permissible Values (Standardization) ---
    if st.session_state.uploaded_data is not None and st.session_state.structure_approved:
        st.markdown("---")
        st.subheader("Value Standardization")
        st.markdown("""
        Standardize your data values to match permissible values using ontology-enhanced matching.
        """)

        df = st.session_state.uploaded_data

        # --- Automatic Linkage Handling ---
        # 1. Identify primary ID mappings from the current column mapping
        primary_id_mappings = {}
        for target, source in st.session_state.column_mapping.items():
            if "." in target:
                entity, prop = target.split(".", 1)
                # Identify if this is the primary ID for the entity (e.g., Subject.subject_id)
                if prop.lower() == f"{entity.lower()}_id" or prop.lower() == "id":
                    primary_id_mappings[entity.lower()] = source

        # 2. Automatically map any linkage properties that point to these identified entities
        for entity_name, properties in schema.items():
            for prop in properties:
                prop_name = prop['Property']
                if "." in prop_name:
                    # Linkage properties are in format 'target_entity.property'
                    target_entity_name = prop_name.split(".")[0].lower()
                    if target_entity_name in primary_id_mappings:
                        full_target_prop = f"{entity_name}.{prop_name}"
                        # Only auto-fill if not already manually mapped
                        if full_target_prop not in st.session_state.column_mapping:
                            st.session_state.column_mapping[full_target_prop] = primary_id_mappings[target_entity_name]

        # Split data by schema
        split_data = split_data_by_schema(df, st.session_state.column_mapping, schema)

        # Auto-populate linkages to imported metadata entities based on relationships
        for entity_name, entity_df in split_data.items():
            for rel_name, rel_info in relationships.items():
                for end in rel_info.get('Ends', []):
                    if end['Src'] == entity_name and end['Dst'] in st.session_state.metadata:
                        dst_meta = st.session_state.metadata[end['Dst']]
                        if dst_meta:
                            dst_lower = end['Dst'].lower()
                            for prop in schema.get(entity_name, []):
                                linkage_prop = prop['Property']
                                if linkage_prop.startswith(f"{dst_lower}."):
                                    link_val = dst_meta[0].get(linkage_prop.split('.', 1)[1])
                                    if link_val and linkage_prop not in entity_df.columns:
                                        entity_df[linkage_prop] = link_val

        st.write(f"**Identified {len(split_data)} target entities from your data.**")

        missing_links = check_missing_links(split_data, schema, relationships)
        if missing_links:
            st.warning("Some model relationships are missing linkages:")
            for link in missing_links:
                st.write(f"- **{link['entity']}** → **{link['target_entity']}**: `{link['property']}`")
            st.info("Review these linkages in the generated TSVs. Imported metadata can supply a linkage only when the corresponding model identifier is available.")

        for entity_name, entity_df in split_data.items():
            with st.expander(f"📊 {entity_name} ({len(entity_df)} rows)", expanded=True):
                st.dataframe(entity_df.head(10))

                # Validate values
                report, corrections = validate_dataframe(entity_df, entity_name, schema, permissible_values)

                if report:
                    st.write("**Validation Issues Found:**")
                    for item in report[:10]:  # Show first 10
                        st.write(f"- {item}")

                    if len(report) > 10:
                        st.info(f"... and {len(report) - 10} more issues")

                    if corrections:
                        st.write("**Suggested Corrections:**")
                        for col, col_corrections in corrections.items():
                            st.write(f"Column: **{col}**")
                            for old_val, new_val in list(col_corrections.items())[:5]:
                                extra_info = ""
                                if col in permissible_values:
                                    matches = permissible_values[col]
                                    if matches and isinstance(matches[0], dict):
                                        match = next((m for m in matches if m['value'] == new_val), None)
                                        if match:
                                            parts = []
                                            if 'code' in match and match['code']:
                                                parts.append(f"Code: {match['code']}")
                                            if 'definition' in match and match['definition']:
                                                # Truncate definition if too long
                                                defn = match['definition']
                                                if len(defn) > 100:
                                                    defn = defn[:97] + "..."
                                                parts.append(f"Def: {defn}")
                                            if parts:
                                                extra_info = " (" + " | ".join(parts) + ")"

                                st.write(f"  - '{old_val}' → **{new_val}**{extra_info}")

                        if st.button(f"Apply Corrections to {entity_name}", key=f"apply_{entity_name}"):
                            # Apply corrections
                            for col, col_corrections in corrections.items():
                                entity_df[col] = entity_df[col].replace(col_corrections)
                            st.success(f"✅ Applied corrections to {entity_name}")

                            # Save the corrected dataframe
                            output_file = os.path.join(st.session_state.output_dir, f"{entity_name.lower()}.tsv")
                            entity_df.to_csv(output_file, sep='\t', index=False)
                            st.success(f"✅ Saved to {output_file}")

                            # Offer download
                            with open(output_file, 'r') as f:
                                st.download_button(
                                    label=f"Download {entity_name}.tsv",
                                    data=f.read(),
                                    file_name=f"{entity_name.lower()}.tsv",
                                    mime="text/tab-separated-values",
                                    key=f"download_{entity_name}"
                                )
                else:
                    st.success("✅ All values are valid!")

                    # Save the dataframe
                    output_file = os.path.join(st.session_state.output_dir, f"{entity_name.lower()}.tsv")
                    entity_df.to_csv(output_file, sep='\t', index=False)
                    st.success(f"✅ Saved to {output_file}")

                    # Offer download
                    with open(output_file, 'r') as f:
                        st.download_button(
                            label=f"Download {entity_name}.tsv",
                            data=f.read(),
                            file_name=f"{entity_name.lower()}.tsv",
                            mime="text/tab-separated-values",
                            key=f"download_{entity_name}"
                        )

        st.markdown("---")
        st.success("🎉 Validation and transformation complete! All TSV files have been generated.")

        if st.button("🔄 Start New Validation"):
            reset_app()
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
NCI Imaging Submission Validator | Following <a href="https://github.com/CBIIT/nci-imaging-submission-model" style="color: gray;">NCI's Imaging Submission Model</a><br>
Leveraging NCIt, UBERON, and SNOMED ontologies for standardization
</div>
""", unsafe_allow_html=True)
