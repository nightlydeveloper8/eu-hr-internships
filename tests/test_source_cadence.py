from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from collector import cadence, daily
from collector.pipeline import reconcile


START = datetime(2026, 9, 1, tzinfo=timezone.utc)
SOURCE = {'id': 'example', 'adapter': 'universal-employer', 'enabled': True}


def report(day, status='ok', **extra):
    return dict(id=SOURCE['id'], checked_at=(START + timedelta(days=day)).isoformat(),
                status=status, **extra)


class SourceCadenceTests(unittest.TestCase):
    def test_default_off(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(cadence.enabled())
        with patch.dict(os.environ, {'COLLECTOR_SOURCE_CADENCE': '1'}):
            self.assertTrue(cadence.enabled())

    def test_complete_empty_history_is_weekly_after_sixty_days(self):
        first = cadence.observe({}, report(0, explicit_empty=True), 0)
        state = cadence.observe(first, report(59, records_inspected=40), 0)
        self.assertEqual(cadence.interval(SOURCE, state, START + timedelta(days=59), set()), 1)
        self.assertFalse(cadence.due(SOURCE, state, START + timedelta(days=60), set()))
        self.assertTrue(cadence.due(SOURCE, state, START + timedelta(days=66), set()))
        for observed, count in ((report(60, 'partial'), 0), (report(60), None),
                                (report(60, inventory_complete=False), 0)):
            self.assertNotIn('empty_since', cadence.observe(state, observed, count))

    def test_monthly_after_fifteen_recorded_failures_with_daily_overrides(self):
        state = {}
        for day in range(14):
            state = cadence.observe(state, report(day, 'failed', error='DNS'), 0)
        at = START + timedelta(days=15)
        self.assertTrue(cadence.due(SOURCE, state, at, set()))
        state = cadence.observe(state, report(14, 'failed', error='robots.txt disallows URL'), 0)
        self.assertFalse(cadence.due(SOURCE, state, at, set()))
        self.assertTrue(cadence.due(SOURCE, state, START + timedelta(days=44), set()))
        self.assertTrue(cadence.due(SOURCE, state, at, {'example'}))
        for adapter in cadence.DAILY_ADAPTERS:
            self.assertTrue(cadence.due(dict(SOURCE, adapter=adapter), state, at, set()))
        self.assertTrue(cadence.due(SOURCE, dict(state, last_hr=START.isoformat()), at, set()))
        self.assertEqual(cadence.observe(state, report(14, 'failed', error='DNS'), 0), state)
        reset = cadence.observe(state, report(15, 'partial'), 0)
        self.assertEqual(reset['failure_streak'], 0)

    def test_skipped_cycles_preserve_id_and_do_not_increment_missing_count(self):
        jobs = [{'id': 'existing', 'source_id': 'example', 'status': 'open',
                 'url': 'https://example.org/job', 'title': 'HR stage'}]
        first = reconcile(jobs, [], {'example'}, START.isoformat())
        skipped = reconcile(first, [], set(), (START + timedelta(days=2)).isoformat())
        self.assertEqual(skipped, first)
        second = reconcile(skipped, [], {'example'}, (START + timedelta(days=3)).isoformat())
        self.assertEqual(second[0]['status'], 'unverified')
        self.assertEqual(second[0]['missing_count'], 2)
        third = reconcile(second, [], {'example'}, (START + timedelta(days=4)).isoformat())
        self.assertEqual((third[0]['id'], third[0]['status']), ('existing', 'closed'))

    def test_opt_in_shard_and_merge_validate_the_same_baseline(self):
        state = dict(last_attempt=START.isoformat(), failure_streak=15, failure_reason='DNS')
        coverage = {'sources': [dict(report(0, 'failed'), cadence=state)]}
        catalog = {'jobs': []}
        stamp = (START + timedelta(days=1)).isoformat()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'coverage.json').write_text(json.dumps(coverage))
            (root/'catalog.json').write_text(json.dumps(catalog))
            with (patch.object(daily, 'ROOT', root/'..'), patch.object(daily, 'provision_files',
                  return_value=([], [SOURCE])), patch.object(daily, 'now', return_value=stamp),
                  patch.dict(os.environ, {'COLLECTOR_SOURCE_CADENCE': '1'}),
                  patch.object(daily, 'finalize', return_value=(catalog, coverage)) as finalize,
                  patch.object(daily, 'read', side_effect=lambda path, default:
                      json.loads((root/path.name).read_text())
                      if (root/path.name).exists() else default),
                  patch.object(daily, 'process_source') as process):
                payload = daily.collect_shard(shards=1, output=root/'shard-0.json')
                self.assertEqual(payload['expected_source_ids'], [])
                process.assert_not_called()
                daily.merge(root, shards=1, output=root)
                self.assertEqual(finalize.call_args.args[1:5], ([], catalog, coverage, []))
                (root/'catalog.json').write_text(json.dumps(dict(catalog, last_attempt_at=stamp)))
                with self.assertRaisesRegex(ValueError, 'publication base changed'):
                    daily.merge(root, shards=1, output=root)
