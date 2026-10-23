"""Proposal import, investigator review, and draft curation exports."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import zipfile

import pandas as pd

from . import crdc_converter, orcid_helper, remap_helper

INVESTIGATOR_COLUMNS = ['author_order', 'first_name', 'last_name', 'person_orcid', 'email', 'organization_name']


def clean(value):
    if isinstance(value, (list, dict)):
        return value
    return '' if value is None or pd.isna(value) else str(value).strip()


def normalize_investigators(rows):
    """Preserve author order and supplied fields without guessing identities."""
    result = []
    def order(row):
        try:
            return float(row.get('author_order', 999))
        except (TypeError, ValueError):
            return 999
    for row in sorted(rows, key=order):
        normalized = {key: clean(value) for key, value in row.items()}
        if not any(normalized.get(key) for key in INVESTIGATOR_COLUMNS[1:]):
            continue
        normalized['person_orcid'] = re.sub(r'^https?://(?:www\.)?orcid.org/', '', normalized.get('person_orcid', ''), flags=re.I).strip().upper()
        normalized['author_order'] = len(result) + 1
        result.append(normalized)
    return result


def parse_authors(text, strategy='Auto-detect'):
    rows = []
    for line in re.split(r'[;\n]', text):
        if line.strip():
            parsed = orcid_helper.parse_author_input(line, strategy=strategy)
            rows.append(dict(author_order=len(rows) + 1, first_name=parsed['first_name'],
                             last_name=parsed['last_name'], person_orcid=parsed['orcid'] or '',
                             email='', organization_name=''))
    return normalize_investigators(rows)


def investigator_warnings(rows):
    warnings = []
    if not rows:
        return ['No investigators were supplied. The author list will need follow-up.']
    seen = set()
    for row in rows:
        number = row['author_order']
        if not row.get('first_name') or not row.get('last_name'):
            warnings.append(f'Investigator {number}: incomplete given/family name; check the original author list.')
        orcid = row.get('person_orcid', '')
        if orcid:
            if not orcid_helper.valid_orcid(orcid):
                warnings.append(f'Investigator {number}: ORCID has an invalid format or checksum.')
            if orcid in seen:
                warnings.append(f'Investigator {number}: repeated ORCID; confirm the author order and identity.')
            seen.add(orcid)
    return warnings


def import_proposal(payload, filename, default_program, proposal_type='New Collection Proposal'):
    """Import supported TCIA packages or a CRDC v3.5 workbook, retaining raw answers."""
    investigators = []
    imported = None
    lower = filename.lower()
    if lower.endswith('.xlsx'):
        if not crdc_converter.is_crdc_workbook(payload):
            raise ValueError('This XLSX file is not a supported CRDC submission-request workbook.')
        imported = crdc_converter.import_crdc_workbook(payload, proposal_type=proposal_type)
        proposal = imported['proposal_data']
        investigators = imported['investigators']
    else:
        if lower.endswith('.zip'):
            with zipfile.ZipFile(BytesIO(payload)) as package:
                summaries = [name for name in package.namelist() if 'proposal_summary' in name and name.endswith('.tsv')]
                if len(summaries) != 1:
                    raise ValueError('The ZIP must contain exactly one proposal_summary TSV.')
                frame = pd.read_csv(BytesIO(package.read(summaries[0])), sep='\t', keep_default_na=False)
                inv_file = next((n for n in package.namelist() if 'investigators' in n and n.endswith('.tsv')), None)
                if inv_file:
                    investigators = pd.read_csv(BytesIO(package.read(inv_file)), sep='\t', keep_default_na=False).to_dict('records')
        else:
            frame = pd.read_csv(BytesIO(payload), sep='\t', keep_default_na=False)
        if len(frame) != 1:
            raise ValueError('The proposal summary must contain exactly one dataset.')
        proposal = frame.iloc[0].to_dict()
    proposal = {key: clean(value) for key, value in proposal.items()}
    if not proposal.get('Title') and not proposal.get('Nickname'):
        raise ValueError('No proposal title or short title was found. Import the proposal summary TSV, ZIP, or CRDC workbook.')
    dataset = {target: proposal.get(source, '') for target, source in (
        ('dataset_long_name', 'Title'), ('dataset_short_name', 'Nickname'),
        ('dataset_abstract', 'Abstract'), ('adult_or_childhood_study', 'adult_or_childhood_study'),
        ('acknowledgements', 'acknowledgements'), ('funding_agency', 'funding_agency'),
        ('funding_source_program_name', 'funding_source_program_name'), ('grant_id', 'grant_id'))}
    dataset['dataset_description'] = ''
    dataset['acknowledgements'] = dataset['acknowledgements'] or proposal.get('acknowledgments', '')
    related = []
    for key in ('citation_primary', 'citations_content', 'additional_publications', 'descriptor_publication'):
        if proposal.get(key):
            related.append(dict(title=proposal[key], publication_type='Journal Article',
                                relationship_type='Describes' if key == 'descriptor_publication' else 'IsDerivedFrom',
                                authorship='', DOI=''))
    try:
        manuscripts = json.loads(proposal.get('Manuscripts') or '[]')
    except (ValueError, TypeError):
        manuscripts = []
    for manuscript in manuscripts:
        value = manuscript.get('value', '')
        doi = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', value, re.I) if 'doi.org/' in value else None
        related.append(dict(title=value, publication_type='Preprint',
                            relationship_type='Describes' if manuscript.get('category') == 'Dataset Descriptor' else 'IsDerivedFrom',
                            authorship='', DOI=doi.group() if doi else ''))
    metadata = {'Program': [deepcopy(imported['program'] if imported else default_program)],
                'Dataset': [dataset],
                'Investigator': normalize_investigators(investigators) if investigators else parse_authors(proposal.get('Authors', '')),
                'Related_Work': imported['related_works'] if imported else related}
    return proposal, metadata


def metadata_gaps(proposal, metadata, schema, source):
    warnings = []
    for entity, rows in metadata.items():
        missing = [prop['Property'] for prop in schema.get(entity, [])
                   if prop.get('Required/optional') == 'R'
                   and any(not clean(row.get(prop['Property'])) for row in rows)]
        if missing:
            warnings.append(f'Imaging model — {entity}: missing required model values: {", ".join(missing)}.')
    for key, label in [('Title', 'descriptive title'), ('Nickname', 'short title'), ('Abstract', 'abstract'),
                       ('diagnosis', 'disease type'), ('disease_site', 'disease site'), ('species', 'species')]:
        if not proposal.get(key) or proposal[key] == '[]':
            warnings.append(f'TCIA — missing {label}.')
    if proposal.get('Proposal Type') == 'Analysis Results Proposal' and not any(
        work.get('publication_type') == 'Dataset' and work.get('DOI') for work in metadata['Related_Work']
    ):
        warnings.append('TCIA — Analysis Result source dataset DOI(s) need confirmation; source names alone are not DOI records.')
    from .summary_document import exact_dataset_labels
    for key, field in [('diagnosis', 'disease_type'), ('disease_site', 'disease_location'), ('species', 'species')]:
        try:
            exact_dataset_labels(proposal.get(key), field)
        except ValueError as exc:
            warnings.append(f'TCIA label review — {exc} The tracking document leaves a review placeholder; consult the original proposal.')
    if source.lower().endswith('.xlsx'):
        warnings.append('CRDC import — TCIA-specific answers and CRDC-only fields do not all have equivalents. Keep the original workbook; unmapped answers are not carried into the generated workbook.')
    return warnings


def build_model_package(metadata, schema, relationships, prefix='dataset'):
    """Generate isolated TSVs using the existing model writer and relationship rules."""
    processed = deepcopy(metadata)
    for entity, rows in processed.items():
        if entity == 'Investigator':
            rows[:] = normalize_investigators(rows)
        for relationship in relationships.values():
            for end in relationship.get('Ends', []):
                if end['Src'] != entity or not processed.get(end['Dst']):
                    continue
                destination = end['Dst'].lower()
                target = processed[end['Dst']][0]
                for prop in schema.get(entity, []):
                    name = prop['Property']
                    if name.startswith(destination + '.'):
                        value = target.get(name.split('.', 1)[1])
                        if value:
                            for row in rows:
                                if not row.get(name):
                                    row[name] = value
    buffer = BytesIO()
    with TemporaryDirectory(prefix='tcia-metadata-') as folder, zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as package:
        for entity, rows in processed.items():
            if rows:
                path = remap_helper.write_metadata_tsv(entity, rows, schema, folder, filename_prefix=prefix)
                if path:
                    package.write(path, Path(path).name)
    return buffer.getvalue()
