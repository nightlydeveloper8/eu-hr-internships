from datetime import datetime
from urllib.error import HTTPError
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

    def test_unchanged_sitemap_revalidates_robots_and_skips_parsing(self):
        robots = b'User-agent: *\nSitemap: https://example.com/sitemap.xml'
        mime = b'<urlset><url><loc>https://example.com/jobs/hr-internship</loc></url></urlset>'
        calls = []
        client = discovery.BudgetClient(seconds=10, max_requests=2)
        def get(url, **kwargs):
            calls.append(url)
            client.requests += 1
            if url.endswith('robots.txt'):
                return robots, 200, url
            if getattr(client, 'conditional_get_headers', {}).get('If-None-Match'):
                raise HTTPError(url, 304, 'Not modified', None, None)
            client.response_validators = {'ETag': '"original"'}
            return mime, 200, url
        with (patch.object(discovery, 'BudgetClient', return_value=client),
              patch.object(client, 'request', side_effect=get)):
            hints = {'maps': set()}
            first = discovery.probe('example.com', hints, set())
            client.requests = 0
            with patch.object(discovery, 'parse_sitemap', side_effect=AssertionError('cached')):
                cached = discovery.probe('example.com', hints, set(), first)
        self.assertEqual(calls, ['https://example.com/robots.txt', OBSERVATION['sitemap']] * 2)
        self.assertTrue(cached['cache_hit'])
        self.assertEqual(cached['signature'], first['signature'])
        self.assertEqual(cached['candidates'], 1)

    def test_funnel_preserves_partial_indexes_and_lists_failed_conditions(self):
        indexed = dict(OBSERVATION, candidates=0, children=8, urls=0, reason='Termini da rivedere')
        self.assertEqual(discovery.funnel_bucket(indexed), 'Termini da rivedere')
        failed = dict(OBSERVATION, replay=dict(REPLAY, budget=False, current=False), reason='Replay fallito')
        self.assertIn('budget o lettura incompleta, livello di prova', discovery.funnel_bucket(failed))

    def test_migration_gate_needs_no_slug_or_listing_but_checks_replay(self):
        empty_site = {'robots': True, 'candidates': 0}
        no_listing = dict(REPLAY, current=False)
        self.assertEqual(discovery.gate(empty_site, True, False, 0, 1200, no_listing, migration=True), '')
        self.assertTrue(discovery.gate(empty_site, True, True, 0, 1200, no_listing))
        for update in ({'lost': ['old']}, {'excluded': True}, {'budget': False}):
            self.assertTrue(discovery.gate(empty_site, True, True, 0, 1200,
                                           dict(no_listing, **update), migration=True))
        for update in ({'robots_denied': True}, {'access_stop': 403}):
            self.assertTrue(discovery.gate(dict(empty_site, **update), True, True, 0, 1200,
                                           no_listing, migration=True))
        self.assertTrue(discovery.gate(empty_site, False, True, 0, 1200, no_listing, migration=True))

    def test_migration_is_applied_without_slug_or_current_listing(self):
        previous = dict(REVIEWED, id='auto-employer', adapter='universal-employer', enabled=True)
        production = dict(REVIEWED, id='production', enabled=True, career_url='https://another.example/',
                          allowed_hosts=['another.example'])
        hosts = {'example.com': {'migration': {previous['id']}, 'templates': {REVIEWED['id']: REVIEWED}}}
        no_listing = dict(REPLAY, current=False)
        with (patch.object(discovery, 'inventory', return_value=(hosts, set())),
              patch.object(discovery, 'probe', return_value=dict(OBSERVATION, candidates=0)),
              patch.object(discovery, 'simulate', return_value=({}, no_listing))):
            sources, reports, changed = discovery.stage([previous, production], {'jobs': []}, {}, STAMP, 1200)
        self.assertTrue(changed)
        self.assertEqual(reports['example.com']['reason'], 'Migrata')
        self.assertEqual(sources[0]['source_id_aliases'], ['auto-employer', 'reviewed'])

    def test_platform_route_is_prepared_for_an_existing_official_host(self):
        previous = dict(REVIEWED, id='generic', adapter='universal-employer')
        robots = [('disallow', '/applybutton/'), ('disallow', '/talentcommunity/')]
        name, confirmed = discovery.platform_signal('example.com', robots, [], None)
        self.assertEqual((name, confirmed), ('sf-rmk', True))
        source = discovery.migration_adapter(previous, dict(
            OBSERVATION, platform=name, platform_confirmed=confirmed))
        self.assertEqual(source['adapter'], 'sf-rmk')
        self.assertEqual(source['id'], 'generic')
        self.assertEqual(source['allowed_hosts'], ['example.com'])
        self.assertIsNone(discovery.migration_adapter(dict(previous, allowed_hosts=[]), dict(
            OBSERVATION, platform=name, platform_confirmed=confirmed)))

    def test_first_probe_falls_back_and_prioritizes_job_leaves_within_twelve_gets(self):
        base = 'https://example.com'
        known = base + '/absent.xml'
        preferred = base + '/sitemap-jobs.xml'
        other = [base + f'/sitemap-general-{i}.xml' for i in range(14)]
        children = ''.join(f'<sitemap><loc>{url}</loc></sitemap>' for url in [*other, preferred])
        documents = {
            base + '/robots.txt': b'User-agent: *\nSitemap: https://example.com/absent.xml',
            base + '/sitemap_index.xml': f'<sitemapindex>{children}</sitemapindex>'.encode(),
            preferred: b'<urlset><url><loc>https://example.com/jobs/hr-internship</loc></url></urlset>',
        }
        calls = []
        client = discovery.BudgetClient(seconds=60, max_requests=12)
        def get(url, **kwargs):
            calls.append(url)
            client.requests += 1
            if url in (known, base + '/sitemap.xml'):
                raise HTTPError(url, 404, 'missing', None, None)
            return documents.get(url, b'<urlset/>'), 200, url
        with (patch.object(discovery, 'BudgetClient', return_value=client),
              patch.object(client, 'request', side_effect=get)):
            result = discovery.probe('example.com', {'maps': set()}, set())
        self.assertEqual(calls[:5], [base + '/robots.txt', known, base + '/sitemap.xml',
                                     base + '/sitemap_index.xml', preferred])
        self.assertEqual(len(calls), 12)
        self.assertEqual(result['candidates'], 1)
        self.assertGreater(result['children'], 0)

    def test_robots_failure_counts_weeks_and_denial_is_cached_separately(self):
        hints = {'maps': set()}
        with patch.object(discovery.Scan, 'preflight', side_effect=OSError('network')) as fetch:
            result = {}
            for week in ('2026-11-12T09:00:00+00:00', '2026-11-19T09:00:00+00:00', STAMP):
                with patch.object(discovery, 'now', return_value=week):
                    result = discovery.probe('example.com', hints, set(), result)
                    cached = discovery.probe('example.com', hints, set(), result)
                    self.assertTrue(cached['cache_hit'])
            self.assertEqual(result['robots_attempts'], 3)
            self.assertEqual(fetch.call_count, 3)
        with patch.object(discovery.Scan, 'preflight', return_value=['https://example.com/sitemap.xml']):
            with patch.object(discovery.Scan, 'permitted', return_value=False):
                denied = discovery.probe('example.com', hints, set())
        self.assertTrue(denied['robots_denied'])
        self.assertNotIn('robots_attempts', denied)
        self.assertTrue(discovery.probe('example.com', hints, set(), denied)['cache_hit'])

    def test_replay_transport_uses_twelve_gets_even_if_source_budget_is_higher(self):
        self.assertEqual(discovery.ReplayClient(dict(REVIEWED, max_requests=100)).max_requests, 12)

    def test_replay_reports_missing_date_title_and_live_read_as_distinct_gaps(self):
        catalog = {'jobs': []}
        part = {'jobs': [{'id': 'candidate', 'url': 'https://example.com/jobs/hr-internship',
                          'title': 'HR internship', 'countries': ['NL']}],
                'report': {'status': 'partial', 'candidate_filter_reasons': {'not-hr-student-role': 1},
                           'page_errors': [{'error': 'request timeout'}]}}
        with patch.object(discovery, 'finalize', return_value=(catalog, {})):
            _, report = discovery.simulate(REVIEWED, [REVIEWED], catalog, STAMP, [],
                                           (part, 30, 4, 100, 0.1))
        self.assertFalse(report['current'])
        self.assertFalse(report['budget'])
        self.assertEqual(report['gaps'], {
            'Titolo non HR o stage non ammissibile': 1,
            'Annuncio o inventario non leggibile nella verifica live': 1,
            'Data di pubblicazione o scadenza assente': 1,
        })

    def test_funnel_counts_platforms_with_candidates_and_explains_evidence(self):
        hosts = {'example.com': {'migration': {'old'}}, 'unknown.example': {'migration': set()}}
        rows = {
            'example.com': dict(OBSERVATION, reason='Replay fallito',
                                replay=dict(REPLAY, current=False, gaps={'Data assente': 2})),
            'unknown.example': dict(OBSERVATION, reason='Piattaforma non in produzione · unknown',
                                    unsupported_platform='unknown'),
        }
        with patch.object(discovery, 'inventory', return_value=(hosts, set())):
            funnel = discovery.funnel([], rows)
        self.assertIn('Replay fallito · livello di prova | 1 | 1', funnel)
        self.assertIn('unknown · 1 host', funnel)
        self.assertIn('example.com · Data assente (2)', funnel)

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
