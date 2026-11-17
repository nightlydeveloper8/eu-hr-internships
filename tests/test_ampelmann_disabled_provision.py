"""Disabled-source regression and daily auto-provisioning guard; no employer calls."""
import copy
import json
import unittest

from collector.company_registry import validate_registry
from collector.daily import provision
from collector.pipeline import ROOT
from scripts.prepare_ampelmann_disabled import prepare, COMPANY_ID, SOURCE_ID, EMPLOYER


class AmpelmannDisabledTests(unittest.TestCase):
    def test_new_company_and_reviewed_source_are_disabled(self):
        companies, sources, result = prepare([], [])
        self.assertEqual(result['active_sources'], 0)
        self.assertEqual(result['auto_provisioned'], 0)
        self.assertTrue(companies[0]['collection_activation_hold'])
        self.assertFalse(sources[0]['enabled'])
        self.assertEqual(sources[0]['adapter'], 'recruitee')
        self.assertEqual(sources[0]['feed_format'], 'recruitee-public-xml')
        self.assertEqual(sources[0]['allowed_hosts'], ['careers.ampelmann.nl'])
        self.assertEqual(companies[0]['source_ids'], [SOURCE_ID])
        geography=json.loads((ROOT/'data/geography.json').read_text())
        self.assertTrue(validate_registry(companies, geography, sources))

    def test_daily_provision_does_not_enable_universal_crawler(self):
        companies, sources, _ = prepare([], [])
        after_companies, after_sources = provision(companies, sources)
        self.assertEqual(after_companies, companies)
        self.assertEqual(after_sources, sources)
        self.assertNotIn('auto-' + COMPANY_ID, {s['id'] for s in after_sources})

    def test_idempotency_and_other_employers_preserved(self):
        other = dict(id='other-employer', name='Other Employer',
                     career_url='https://other.example.org/jobs',
                     evidence_url='https://other.example.org/jobs',
                     source_ids=['existing'], target_countries=['NL'], workplaces=[])
        existing_source = dict(id='existing', company_id='other-employer',
                               enabled=True, employer='Other Employer', adapter='recruitee',
                               allowed_hosts=['other.example.org'])
        once = prepare([other], [existing_source])
        again = prepare(once[0], once[1])
        self.assertEqual((once[0], once[1]), (again[0], again[1]))
        self.assertEqual(again[1][0], existing_source)
        self.assertFalse(again[1][-1]['enabled'])

    def test_review_hold_conflicting_active_sources_fail_closed(self):
        companies, sources, _ = prepare([], [])
        enabled = copy.deepcopy(sources)
        enabled[0]['enabled'] = True
        with self.assertRaisesRegex(ValueError, 'active|enabled'):
            prepare(companies, enabled)
        with self.assertRaisesRegex(ValueError, 'Held employer has an enabled source'):
            provision(companies, enabled)

    def test_company_collision_rejected(self):
        companies, sources, _ = prepare([], [])
        extra = dict(companies[0], id='ampelmann-duplicate')
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            prepare(companies + [extra], sources)


if __name__ == '__main__':
    unittest.main()
