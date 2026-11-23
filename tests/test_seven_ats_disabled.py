import json
import unittest
from pathlib import Path

from collector.company_registry import validate_registry
from collector.daily import provision

ROOT = Path(__file__).resolve().parents[1]
ENABLED = {
    'recruitee-peripass-be': 'peripass-be',
    'greenhouse-fanatics-collectibles-gb': 'fanatics-collectibles-gb',
    'recruitee-aquablu-nl': 'aquablu-nl',
    'recruitee-zeromotorcycles-nl': 'zero-motorcycles-nl',
    'recruitee-werkenbijyouvia-nl': 'youvia-nl',
}
HELD = {'recruitee-climeworks-ch': 'climeworks-ch'}


class SevenATSHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.companies = json.loads((ROOT / 'data/companies.json').read_text())
        cls.sources = json.loads((ROOT / 'data/sources.json').read_text())
        cls.geography = json.loads((ROOT / 'data/geography.json').read_text())

    def test_provision_preserves_reviewed_source_activation(self):
        self.assertTrue(validate_registry(self.companies, self.geography, self.sources))
        companies, sources = provision(self.companies, self.sources)
        self.assertEqual((companies, sources), (self.companies, self.sources))
        self.assertEqual(provision(companies, sources), (companies, sources))
        by_company = {c['id']: c for c in companies}
        for sid, cid in {**ENABLED, **HELD}.items():
            with self.subTest(source=sid):
                company = by_company[cid]
                owned = [s for s in sources if s.get('company_id') == cid]
                source, = owned
                active = sid in ENABLED
                self.assertEqual(source['id'], sid)
                self.assertIs(source['enabled'], active)
                self.assertIs(bool(source.get('collection_activation_hold')), not active)
                self.assertIs(bool(company.get('collection_activation_hold')), not active)
                self.assertIn(sid, company['source_ids'])

    def test_other_held_employers_reject_accidental_enablement(self):
        held_companies = {c['id'] for c in self.companies if c.get('collection_activation_hold')}
        sources_on_hold = {s['id'] for s in self.sources if s.get('company_id') in held_companies}
        self.assertTrue(HELD.keys() <= sources_on_hold)
        for source_id in sources_on_hold:
            with self.subTest(source=source_id):
                sources = [dict(s, enabled=True) if s['id'] == source_id else s for s in self.sources]
                with self.assertRaisesRegex(ValueError, 'Held employer has an enabled source'):
                    provision(self.companies, sources)


if __name__ == '__main__':
    unittest.main()
