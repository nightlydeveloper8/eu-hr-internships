"""Offline workflow boundaries: freshness, reproducibility, inert external claims."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from collector.provincial_factory import (
    checkpoint, compact, digest, encode, import_handoff, read, snapshot, source_state,
)

AT = '2026-11-07T15:00:00+00:00'


class FactoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        (self.root / 'collector').mkdir()
        (self.root / 'collector/version.py').write_text('VERSION = 1\n')
        self.save('p-geography', dict(province=dict(nuts2_code='NL13'), municipalities=[dict(name='Assen', cbs_code='GM1')]))
        states = [dict(status='ok', complete=True, inventory_complete=True),
                  dict(status='partial', complete=False, records_inspected=3),
                  dict(status='partial', complete=False, records_inspected=0),
                  dict(status='failed', error='robots.txt disallows URL'),
                  dict(status='failed', error='Connection reset'),
                  dict(status='ok', complete=True, checked_at='2026-11-01T15:00:00+00:00')]
        self.save('companies', [dict(id=f'c{i}', name=f'Employer {i}', source_ids=[f's{i}'], p_research=dict(size={}),
            workplaces=[dict(region_code='NL13', municipality_code='GM1', location_confidence='confirmed')]) for i in range(7)])
        self.save('sources', [dict(id=f's{i}', enabled=True) for i in range(7)])
        self.save('coverage', dict(sources=[dict(dict(id=f's{i}', checked_at=AT), **state) for i, state in enumerate(states)]))
        job = dict(id='j1', employer='Employer 0', source_id='s0', region_codes=['NL13'], internship_type='internship',
                   status='open', link_status='verified', last_verified_at='2026-11-05T16:00:00+00:00',
                   verification=dict(state='verified', policy_version=2))
        self.save('catalog', dict(jobs=[job, dict(job, id='student', internship_type='working-student'),
                                     dict(job, id='untrusted', link_status='unverified')]))
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        self.commit()
        self.baseline = self.data_hashes()

    def commit(self):
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.name=Factory Test', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'fixture'], cwd=self.root, check=True)

    def save(self, name, data):
        (self.root / f'data/{name}.json').write_bytes(encode(data))

    def data_hashes(self):
        return {p.name: digest(p.read_bytes()) for p in (self.root / 'data').glob('*.json')}

    def candidate_file(self, **updates):
        candidate = dict(employer='Untrusted $(touch /tmp/not-executed)', official_career_url='https://example.invalid/careers',
                         municipality='Assen', evidence_url='https://github.com/example/issues/1', observed_at=AT,
                         confidence=0.7, review_status='verified')
        candidate.update(updates)
        path = self.root / 'input.json'
        path.write_bytes(encode(dict(schema_version=1, candidates=[candidate])))
        return path

    def test_states_are_distinct_and_complete_requires_evidence(self):
        report = snapshot(self.root, 'p', AT)
        self.assertEqual(report['source_states'], dict(complete=2, partial=1, incomplete=1, blocked=1, failed=1, **{'not-attempted': 1}))
        self.assertEqual(report['complete_recent_sources'], 1)
        self.assertEqual(report['complete_recent_employers'], 1)
        self.assertEqual(report['stale_sources'], 2)
        self.assertEqual(report['verified_hr_internship_ids'], ['j1'])
        self.assertEqual(source_state(dict(status='ok')), 'incomplete')
        self.assertEqual(source_state(dict(status='ok', complete=True, inventory_complete=False)), 'incomplete')
        self.assertEqual(report['municipalities'][0]['identified'], 7)

    def test_identified_disabled_missing_and_unconfigured_are_separate(self):
        companies = read(self.root / 'data/companies.json')
        companies.append(dict(id='unconfigured', name='No source', p_research=True, source_ids=[]))
        self.save('companies', companies)
        sources = read(self.root / 'data/sources.json')
        sources[0]['enabled'] = False
        self.save('sources', sources[:-1])
        report = snapshot(self.root, 'p', AT)
        self.assertEqual(report['identified_employers'], 8)
        self.assertEqual(report['configured_employers'], 5)
        self.assertEqual(report['configured_sources'], 5)
        self.assertEqual(report['complete_recent_employers'], 0)
        self.assertEqual({r['reason'] for r in report['anomalies']} & {'disabled', 'missing-source-config'},
                         {'disabled', 'missing-source-config'})

    def test_summary_is_bounded_deterministic_and_read_only(self):
        report = snapshot(self.root, 'p', AT)
        text = compact(report, 's3')
        self.assertEqual(text, compact(snapshot(self.root, 'p', AT), 's3'))
        self.assertIn('blocked', text)
        report['municipalities'] *= 200
        self.assertLessEqual(len(compact(report).splitlines()), 100)
        self.assertEqual(self.data_hashes(), self.baseline)
        with self.assertRaises(ValueError):
            compact(report, 'unknown')

    def test_future_naive_invalid_and_stale_times_are_never_fresh(self):
        for value in ['2026-11-08T00:00:00Z', '2026-11-07T00:00:00', 'bad', None]:
            with self.subTest(value=value):
                self.save('coverage', dict(sources=[dict(id='s0', status='ok', complete=True, checked_at=value)]))
                report = snapshot(self.root, 'p', AT)
                self.assertEqual(report['complete_recent_sources'], 0)
        self.assertEqual(snapshot(self.root, 'p', '2026-11-10T15:00:00Z')['verified_hr_internship_ids'], [])

    def test_checkpoint_idempotent_validated_resume_and_immutable_history(self):
        first, action = checkpoint(self.root, 'p', AT)
        self.assertEqual(action, 'created')
        path = self.root / '.staging/factory/p/checkpoint.json'
        before = path.read_bytes()
        second, action = checkpoint(self.root, 'p', '2026-11-07T15:01:00Z', resume=True)
        self.assertEqual(action, 'reused')
        self.assertEqual(first, second)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(len(list(path.parent.glob('checkpoints/*.json'))), 1)
        self.assertFalse(first['capabilities']['mid_crawler_resume'])
        self.assertEqual(len(first['processed_sources']), 6)
        self.assertTrue(first['pending_tasks'])
        self.assertEqual(self.data_hashes(), self.baseline)

    def test_vacancy_expiry_invalidates_before_checkpoint_age_limit(self):
        checkpoint(self.root, 'p', AT)
        with self.assertRaises(ValueError):
            checkpoint(self.root, 'p', '2026-11-07T16:01:00Z', resume=True)
        result, action = checkpoint(self.root, 'p', '2026-11-07T16:01:00Z')
        self.assertEqual(action, 'created')
        self.assertEqual(result['verified_hr_internship_ids'], [])
        self.assertEqual(len(list((self.root / '.staging/factory/p/checkpoints').glob('*.json'))), 2)

    def test_missing_checkpoint_and_clock_rollback_rejected(self):
        with self.assertRaises(ValueError):
            checkpoint(self.root, 'p', AT, resume=True)
        checkpoint(self.root, 'p', AT)
        with self.assertRaises(ValueError):
            checkpoint(self.root, 'p', '2026-11-07T14:59:00Z', resume=True)

    def test_source_freshness_expiry_and_checkpoint_maximum_age(self):
        checkpoint(self.root, 'p', AT)
        with self.assertRaises(ValueError):
            checkpoint(self.root, 'p', '2026-11-09T15:00:01Z', resume=True)
        report = snapshot(self.root, 'p', '2026-11-09T15:00:01Z')
        self.assertEqual(report['complete_recent_sources'], 0)

    def test_code_data_commit_and_schema_invalidate(self):
        for change in ('code', 'data', 'commit', 'schema', 'content'):
            with self.subTest(change=change):
                checkpoint(self.root, 'p', AT)
                if change == 'code':
                    (self.root / 'collector/version.py').write_text('VERSION = 2\n')
                elif change == 'data':
                    self.save('catalog', dict(jobs=[]))
                elif change == 'commit':
                    (self.root / 'note.txt').write_text('new base')
                    self.commit()
                else:
                    path = self.root / '.staging/factory/p/checkpoint.json'
                    old = read(path)
                    if change == 'schema':
                        old['schema_version'] = 99
                    else:
                        old['next_command'] = 'echo corrupted'
                    path.write_bytes(encode(old))
                with self.assertRaises(ValueError):
                    checkpoint(self.root, 'p', AT, resume=True)
                checkpoint(self.root, 'p', AT)

    def test_handoff_untrusted_idempotent_and_invalidates_checkpoint(self):
        checkpoint(self.root, 'p', AT)
        path = self.candidate_file()
        with patch('subprocess.run', side_effect=AssertionError('must not execute input')):
            self.assertEqual(import_handoff(self.root, 'p', path, AT), 1)
            queue = self.root / '.staging/factory/p/handoff.json'
            before = queue.read_bytes()
            modified_at = queue.stat().st_mtime_ns
            self.assertEqual(import_handoff(self.root, 'p', path, '2026-11-07T15:01:00Z'), 1)
            self.assertEqual(queue.read_bytes(), before)
            self.assertEqual(queue.stat().st_mtime_ns, modified_at)
        row = read(queue)['candidates'][0]
        self.assertEqual(row['review_status'], 'pending')
        self.assertEqual(row['claimed_review_status'], 'verified')
        self.assertEqual(snapshot(self.root, 'p', AT)['review_candidates'], 1)
        self.assertNotIn('Untrusted', compact(snapshot(self.root, 'p', AT)))
        self.assertEqual(self.data_hashes(), self.baseline)
        with self.assertRaises(ValueError):
            checkpoint(self.root, 'p', AT, resume=True)

    def test_invalid_handoff_is_atomic_and_never_reaches_catalog(self):
        import_handoff(self.root, 'p', self.candidate_file(), AT)
        queue = self.root / '.staging/factory/p/handoff.json'
        before = queue.read_bytes()
        for updates in [dict(municipality='Elsewhere'), dict(official_career_url='file:///tmp/evil'),
                        dict(evidence_url='https://user:password@example.invalid'), dict(confidence=True),
                        dict(confidence=float('nan')), dict(confidence=1.1), dict(observed_at='bad'),
                        dict(observed_at='2026-12-01T00:00:00Z'), dict(employer='Injected\nline'), dict(command='sh evil')]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                import_handoff(self.root, 'p', self.candidate_file(**updates), AT)
            self.assertEqual(before, queue.read_bytes())
        payload = read(self.candidate_file(employer='New valid row'))
        payload['candidates'].append(dict(payload['candidates'][0], municipality='Elsewhere'))
        path = self.root / 'mixed.json'
        path.write_bytes(encode(payload))
        with self.assertRaises(ValueError):
            import_handoff(self.root, 'p', path, AT)
        self.assertEqual(before, queue.read_bytes())
        self.assertEqual(self.data_hashes(), self.baseline)

    def test_province_validation_and_no_cross_province_import(self):
        for slug in ['../data', 'unknown', 'P']:
            with self.assertRaises(ValueError):
                snapshot(self.root, slug, AT)
        with self.assertRaises(ValueError):
            snapshot(self.root, 'p', '2026-11-07')


if __name__ == '__main__':
    unittest.main()
