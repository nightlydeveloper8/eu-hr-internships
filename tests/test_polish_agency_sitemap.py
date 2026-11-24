"""Polish slug selection and guarded agency rollout."""
import unittest
from unittest.mock import Mock

from collector.adapters import collect
from collector.daily import provision
from collector.employer_pages import polish_agency_slug_candidate
from collector.pipeline import ROOT, read


class PolishAgencySitemapTests(unittest.TestCase):
    def test_polish_title_and_location_slug(self):
        self.assertTrue(polish_agency_slug_candidate(
            'https://www.randstad.pl/znajdz-prace/sta%C5%BCysta-ds-rekrutacji_poznan_105818/'))
        self.assertTrue(polish_agency_slug_candidate(
            'https://www.randstad.pl/znajdz-prace/praktyki-studenckie-dzial-kadr_warszawa_105819/'))
        self.assertFalse(polish_agency_slug_candidate(
            'https://www.randstad.pl/znajdz-prace/specjalista-kadr?search=stazysta'))

    def test_rollout_and_hold_guard_and_provisioning_is_idempotent(self):
        companies = read(ROOT / 'data/companies.json', [])
        sources = read(ROOT / 'data/sources.json', [])
        source = next(source for source in sources if source['id'] == 'held-randstad-pl-jobposting')
        self.assertTrue(source['enabled'])
        client = Mock()
        with self.assertRaisesRegex(ValueError, 'collection activation hold'):
            collect(dict(source, enabled=True, collection_activation_hold=True), client)
        self.assertEqual(client.mock_calls, [])
        self.assertEqual(provision(companies, sources), (companies, sources))
