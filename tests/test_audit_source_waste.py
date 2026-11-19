"""Offline, no-network regressions for source-cost triage."""
import unittest

from scripts.audit_source_waste import audit, pattern


def report(source_id, *, requests=10, matching=0, status='partial',
           adapter='universal-employer', checked='2026-11-17',
           pending=0, renders=0, error=None):
    return dict(id=source_id, checked_at=checked + 'T08:00:00+00:00',
                requests=requests, bytes_read=requests * 100,
                duration_seconds=requests / 10, rendered_pages=renders,
                matching=matching, status=status, complete=status == 'ok',
                adapter=adapter, pending_urls=pending,
                error=error)


class SourceWasteAuditTests(unittest.TestCase):
    def test_five_distinct_diagnostic_buckets_and_control(self):
        rows = [
            report('pending', requests=80, pending=50, renders=2),
            report('render', requests=45, renders=4),
            report('universal', requests=5),
            report('adapter', requests=20, adapter='lever'),
            report('access', requests=30, error='robots.txt disallows'),
            report('complete', requests=2, status='ok'),
            report('with-hr', requests=6, matching=1),
            dict(report('unknown', requests=4), matching=None),
            report('yesterday', requests=500, checked='2026-11-16'),
        ]
        result = audit({'sources': rows})
        self.assertEqual(result['observation_date_utc'], '2026-11-17')
        self.assertEqual(result['fresh_source_reports'], 8)
        self.assertEqual(result['all_fresh_cost']['requests'], 192)
        self.assertEqual(result['no_hr_cost']['requests'], 182)
        self.assertEqual(result['known_zero_hr_source_days'], 6)
        self.assertEqual(result['positive_hr_source_days'], 1)
        self.assertEqual(result['matching_unknown_source_days'], 1)
        self.assertEqual(result['no_hr_cost']['renderings'], 6)
        rank = {r['pattern']: r['requests'] for r in result['technical_pattern_rank_by_requests']}
        self.assertEqual(rank, {
            'access_or_collection_error': 30,
            'universal_frontier_backlog': 80,
            'browser_render_without_hr': 45,
            'universal_incomplete_other': 5,
            'nonuniversal_incomplete': 20,
        })
        self.assertEqual(result['nontechnical_complete_no_hr']['requests'], 2)
        self.assertEqual(result['technical_pattern_rank_by_requests'][0]['pattern'],
                         'universal_frontier_backlog')
        self.assertEqual({r['source_id'] for r in result['top_costly_zero_hr_sources']},
                         {'pending', 'render', 'universal', 'adapter', 'access', 'complete'})

    def test_conservative_unknown_and_blocked_never_become_empty(self):
        self.assertEqual(pattern(report('blocked', status='failed', pending=18)),
                         'access_or_collection_error')
        self.assertEqual(pattern(report('partial', pending=18)),
                         'universal_frontier_backlog')
        r = audit({'sources': [dict(report('unscored'), matching=None),
                               report('HR', matching=2)]}, '2026-11-17')
        self.assertEqual(r['no_hr_cost']['requests'], 0)
        self.assertEqual(r['matching_unknown_source_days'], 1)

    def test_stale_report_not_charged_and_missing_date_rejected(self):
        r = audit({'sources': [report('old', checked='2026-11-16'),
                               report('new', checked='2026-11-17')]}, '2026-11-17')
        self.assertEqual(r['all_fresh_cost']['requests'], 10)
        with self.assertRaises(ValueError):
            audit({'sources': []})
        with self.assertRaises(ValueError):
            audit({'sources': []}, 'bad-date')


if __name__ == '__main__':
    unittest.main()
