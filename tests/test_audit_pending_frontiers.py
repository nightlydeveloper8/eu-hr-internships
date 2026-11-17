"""No-network safety and accounting checks for shadow frontier auditing."""
import json
from pathlib import Path
import tempfile
import unittest

from collector.daily import shard_for
from scripts.audit_pending_frontiers import analyze_pending, combine, scan, source_cache_path


class PendingFrontierTests(unittest.TestCase):
    def test_only_identical_url_resource_or_invalid_are_candidates(self):
        urls = [
            {'url': 'https://careers.example.org/jobs/hr-intern-42', 'job': True, 'depth': 2},
            {'url': 'https://careers.example.org/jobs/hr-intern-42', 'job': False, 'depth': 1},
            {'url': 'https://careers.example.org/jobs/people-operations-43', 'job': True, 'depth': 2},
            {'url': 'https://js-www.smartrecruiters.com/career-site-ui/static/js/libs.js',
             'job': False, 'depth': 2},
            {'url': 'https://careers.example.org/privacy', 'job': False, 'depth': 1},
            {'url': 'javascript:alert(1)', 'job': False, 'depth': 1},
        ]
        result = analyze_pending(urls)
        self.assertEqual(result['stored_entries'], 6)
        self.assertEqual(result['exact_duplicate_entries'], 1)
        self.assertEqual(result['vendor_resource_entries'], 1)
        self.assertEqual(result['invalid_url_entries'], 1)
        self.assertEqual(result['review_navigation_entries'], 1)
        self.assertEqual(result['certain_shadow_removals'], 3)
        self.assertEqual(result['preserved_job_flagged'], 2)
        self.assertEqual(result['preserved_distinct_urls'], 3)
        # "privacy" is review-only; never automatically excluded.
        self.assertEqual(result['stored_entries'] - result['certain_shadow_removals'], 3)

    def test_actual_cache_snapshot_is_required_for_counts(self):
        sid = 'auto-audit-example'
        shard = shard_for(sid, 16)
        coverage = {'sources': [
            {'id': sid, 'checked_at': '2026-11-17T10:00:00+00:00',
             'adapter': 'universal-employer', 'matching': 0,
             'pending_urls': 15, 'requests': 60, 'status': 'partial'},
            {'id': 'older', 'checked_at': '2026-11-16T10:00:00+00:00',
             'adapter': 'universal-employer', 'matching': 0, 'pending_urls': 15},
        ]}
        sources = [{'id': sid}]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing = scan(coverage, sources, root, shard=shard)
            self.assertEqual(missing['candidate_sources'], 1)
            self.assertIn('problem', missing['records'][0])
            path = source_cache_path(root, sid)
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'pending': [
                {'url': 'https://careers.example.org/jobs/hr-intern', 'job': True, 'depth': 1},
                {'url': 'https://careers.example.org/jobs/hr-intern', 'job': False, 'depth': 3},
            ]}))
            observed = scan(coverage, sources, root, shard=shard)
            self.assertEqual(observed['records'][0]['coverage_pending'], 15)
            self.assertEqual(observed['records'][0]['stored_entries'], 2)
            self.assertEqual(observed['records'][0]['certain_shadow_removals'], 1)

    def test_aggregate_rejects_missing_and_duplicate_shards(self):
        a = {'shard': 0, 'shards': 2, 'coverage_day': '2026-11-17',
             'records': [{'source_id': 'a', 'coverage_pending': 100,
                          'stored_entries': 2, 'exact_duplicate_entries': 1,
                          'invalid_url_entries': 0, 'vendor_resource_entries': 0,
                          'review_navigation_entries': 0, 'preserved_distinct_urls': 1,
                          'preserved_job_flagged': 1, 'certain_shadow_removals': 1}]}
        b = {'shard': 1, 'shards': 2, 'coverage_day': '2026-11-17', 'records': [
            {'source_id': 'b', 'coverage_pending': 50, 'problem': 'frontier-cache-not-restored'}]}
        result = combine([a, b])
        self.assertEqual(result['cache_matched_sources'], 1)
        self.assertEqual(result['total_coverage_pending_in_target_sources'], 150)
        self.assertEqual(result['matched_source_totals']['stored_entries'], 2)
        self.assertEqual(result['matched_source_totals']['certain_shadow_removals'], 1)
        with self.assertRaises(ValueError):
            combine([a])
        with self.assertRaises(ValueError):
            combine([a, a])
        with self.assertRaises(ValueError):
            combine([a, dict(b, records=a['records'])])


if __name__ == '__main__':
    unittest.main()
