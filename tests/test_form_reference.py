import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tcia_proposals.proposal_metadata import (
    data_type_display, data_type_options, load_catalog, load_form_reference,
    load_proposal_model, species_options, validate_components,
)

ROOT = Path(__file__).resolve().parents[1]


class FormReferenceTests(unittest.TestCase):
    def setUp(self):
        previous = patch('tcia_proposals.proposal_metadata._last_good_reference', None)
        previous.start()
        self.addCleanup(previous.stop)
        self.local = {'catalog': load_catalog(), 'proposal_model': load_proposal_model()}

    def test_published_atomic_pair_matches_both_documentation_inputs(self):
        published = json.loads((ROOT / 'docs/labels/form-reference.json').read_text())
        self.assertEqual(published, self.local)
        newer = copy.deepcopy(self.local)
        newer['catalog']['generated_at_utc'] = '2099-01-01T00:00:00+00:00'
        with patch('tcia_proposals.proposal_metadata.urlopen', return_value=io.BytesIO(json.dumps(newer).encode())):
            self.assertEqual(load_form_reference(), newer)
        with patch('tcia_proposals.proposal_metadata.urlopen', side_effect=OSError('offline')):
            self.assertEqual(load_form_reference(), newer)

    def test_network_error_and_incomplete_or_old_pair_keep_bundled_reference(self):
        with patch('tcia_proposals.proposal_metadata.urlopen', side_effect=OSError('offline')):
            self.assertEqual(load_form_reference(), self.local)
        bad = copy.deepcopy(self.local)
        bad['proposal_model']['version'] = '2020.1.1.1'
        malformed = copy.deepcopy(self.local)
        malformed['proposal_model']['category_data_types'] = []
        for value in (bad, malformed, {}, {'catalog': {'fields': {}}}):
            with patch('tcia_proposals.proposal_metadata.urlopen', return_value=io.BytesIO(json.dumps(value).encode())):
                self.assertEqual(load_form_reference(), self.local)

    def test_sm_appears_after_registration_and_other_is_restricted(self):
        catalog = self.local['catalog']
        before = {r['label'] for r in catalog['fields']['data_type']}
        if 'SM' not in before:
            self.assertNotIn('SM', data_type_options(catalog, 'Histopathology Images'))
            catalog['fields']['data_type'].append({'label': 'SM', 'registry_membership': 'registered'})
        self.assertIn('SM', data_type_options(catalog, 'Histopathology Images'))
        self.assertEqual(data_type_display('SM'), 'SM (Slide Microscopy)')
        self.assertEqual(data_type_options(catalog, 'Other'), ['Other'])
        self.assertTrue(validate_components([{'category':'Other', 'data_types':['CT'], 'file_format':'DICOM', 'other_category':'Custom'}]))
        options = species_options(catalog)
        self.assertEqual(options[options.index('Physical Phantom') + 1], 'Computational Phantom')
