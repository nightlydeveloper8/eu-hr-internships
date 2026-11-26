from datetime import datetime
import unittest
from unittest.mock import patch

from collector import weekly_discovery as discovery


STAMP = '2026-11-26T09:00:00+00:00'
WEEK = '2026-W48'
OBSERVATION = {'robots': True, 'sitemap': 'https://example.com/sitemap.xml', 'candidates': 1}
REPLAY = {'lost': [], 'excluded': False, 'budget': True, 'current': True}
REVIEWED = {'id': 'reviewed', 'employer': 'Employer', 'adapter': 'sitemap-jobposting',
            'career_url': 'https://example.com/', 'allowed_hosts': ['example.com'],
            'collection_seconds': 30, 'collection_delay': 2, 'max_requests': 12}


class WeeklyDiscoveryTests(unittest.TestCase):
    def test_rule_and_independent_rejections(self):
        self.assertEqual(discovery.gate(OBSERVATION, True, True, 19, 2099, REPLAY), '')
        cases = [
            ({'robots': False}, True, True, 19, 2099, REPLAY),
            (OBSERVATION, False, True, 19, 2099, REPLAY),
            (OBSERVATION, True, False, 19, 2099, REPLAY),
            (OBSERVATION, True, True, 20, 2099, REPLAY),
            (OBSERVATION, True, True, 19, 2100, REPLAY),
        ]
        cases += [(OBSERVATION, True, True, 19, 2099, dict(REPLAY, **failure))
                  for failure in ({'lost': ['old']}, {'excluded': True}, {'budget': False}, {'current': False})]
        for args in cases:
            with self.subTest(args=args):
                self.assertTrue(discovery.gate(*args))

    def test_migration_keeps_id_and_weekly_rerun_is_idempotent(self):
        previous = {'id': 'auto-employer', 'company_id': 'employer', 'adapter': 'universal-employer',
                    'enabled': True, 'career_url': 'https://example.com/'}
        evidence = dict(REVIEWED, id='production', enabled=True, career_url='https://production.example/',
                        allowed_hosts=['production.example'])
        state = {}
        catalog = {'jobs': [{'id': 'live', 'source_id': 'production'}]}
        inventory = {'example.com': {'migration': {'auto-employer'}, 'templates': {'reviewed': REVIEWED}}}
        with (patch.object(discovery, 'inventory', return_value=(inventory, set())),
              patch.object(discovery, 'current', return_value=True),
              patch.object(discovery, 'probe', return_value=dict(OBSERVATION)),
              patch.object(discovery, 'simulate', return_value=({}, REPLAY)) as simulate):
            sources, _, changed = discovery.stage([previous, evidence], catalog, state, STAMP, 1200)
            self.assertTrue(changed)
            self.assertEqual(sources[0]['id'], 'auto-employer')
            self.assertEqual(sources[0]['adapter'], 'sitemap-jobposting')
            self.assertEqual(state[WEEK]['auto-employer']['before'], previous)
            rerun, _, changed = discovery.stage(sources, catalog, state, STAMP, 1200)
            self.assertFalse(changed)
            self.assertEqual(rerun, sources)
            simulate.assert_called_once()

    def test_weekly_cap_counts_rollbacks_and_reruns(self):
        entries = {str(i): {'after': dict(REVIEWED), 'rollback': True} for i in range(20)}
        source = dict(REVIEWED, id='production', enabled=True, career_url='https://production.example/',
                      allowed_hosts=['production.example'])
        inventory = {'example.com': {'migration': set(), 'templates': {'reviewed': REVIEWED}}}
        with (patch.object(discovery, 'inventory', return_value=(inventory, set())),
              patch.object(discovery, 'current', return_value=True),
              patch.object(discovery, 'probe', return_value=dict(OBSERVATION)),
              patch.object(discovery, 'simulate') as simulate):
            _, reports, changed = discovery.stage(
                [source], {'jobs': [{'source_id': 'production'}]}, {WEEK: entries}, STAMP, 1200)
            self.assertFalse(changed)
            self.assertIn('20', reports['example.com']['reason'])
            simulate.assert_not_called()

    def test_rollback_on_each_condition_and_retry_is_idempotent(self):
        source = dict(REVIEWED, enabled=True)
        generic = dict(source, id='migrated', adapter='universal-employer')
        migrated = dict(source, id='migrated')
        baseline = {'jobs': [{'id': 'retained'}]}
        cases = [(2701, False, baseline), (1200, True, None), (1200, False, {'jobs': []})]
        for duration, timeout, after in cases:
            with self.subTest(duration=duration, timeout=timeout, after=after):
                entries = {'reviewed': {'before': None, 'after': source},
                           'migrated': {'before': generic, 'after': migrated}}
                reason = discovery.collection_result(duration, timeout, baseline, after)
                self.assertTrue(reason)
                result, changed = discovery.rollback([source, migrated], entries, reason, 123)
                self.assertTrue(changed)
                self.assertFalse(result[0]['enabled'])
                self.assertTrue(result[0]['collection_activation_hold'])
                self.assertEqual(result[1], generic)
                self.assertEqual(discovery.rollback(result, entries, reason, 123), (result, False))
        self.assertEqual(discovery.collection_result(2700, False, baseline, baseline), '')

    def test_audit_only_rolls_back_sources_in_the_collection_snapshot(self):
        activated = dict(REVIEWED, enabled=True)
        state = {WEEK: {'reviewed': {'before': None, 'after': activated}}}
        catalog = {'jobs': [{'id': 'retained'}]}
        event = {'id': 123, 'run_started_at': STAMP, 'updated_at': '2026-11-26T09:20:00+00:00',
                 'conclusion': 'failure', 'jobs': [{'conclusion': 'timed_out'}]}
        result, _, changed = discovery.audit([activated], state, event, catalog, [], None, STAMP)
        self.assertFalse(changed)
        self.assertEqual(result, [activated])
        result, reports, changed = discovery.audit(
            result, state, event, catalog, [activated], None, STAMP)
        self.assertTrue(changed)
        self.assertFalse(result[0]['enabled'])
        self.assertTrue(reports[WEEK]['timeout'])
        self.assertFalse(discovery.audit(result, state, event, catalog, [activated], None, STAMP)[2])

    def test_probe_respects_two_gets_and_excludes_disallowed_details(self):
        maps = b'<urlset><url><loc>https://example.com/jobs/hr-internship</loc></url><url><loc>https://example.com/private/hr-internship</loc></url></urlset>'
        robots = b'User-agent: *\nDisallow: /private/\nSitemap: https://example.com/sitemap.xml'
        client = discovery.BudgetClient(seconds=10, max_requests=2)
        requests = []
        def get(url, **kwargs):
            requests.append(url)
            client.requests += 1
            return (robots if url.endswith('robots.txt') else maps), 200, url
        with (patch.object(discovery, 'BudgetClient', return_value=client),
              patch.object(client, 'request', side_effect=get)):
            result = discovery.probe('example.com', {'maps': set()}, set())
        self.assertEqual(requests, ['https://example.com/robots.txt', OBSERVATION['sitemap']])
        self.assertEqual(result['candidates'], 1)

    def test_inventory_has_curated_inputs(self):
        hosts, exclusions = discovery.inventory([])
        self.assertEqual(len({sid for hints in hosts.values() for sid in hints['migration']}), 203)
        self.assertIn('careers.girteka.eu', hosts)
        self.assertIn('praktika.ut.ee', hosts)
        self.assertIn('manpower.lu', hosts)
        self.assertIn('grafton.com', exclusions)
        self.assertEqual(discovery.week_for(datetime.fromisoformat(STAMP).isoformat()), WEEK)

    def test_slug_uses_linguistic_title_without_country_inference(self):
        self.assertTrue(discovery.slug_candidate('https://manpower.lu/jobs/15182-stagiaire-recrutement-h-f-x/'))
        self.assertFalse(discovery.slug_candidate('https://example.com/apply/hr-internship/'))
        self.assertFalse(discovery.slug_candidate('https://example.com/jobs/working-student-hr/'))
