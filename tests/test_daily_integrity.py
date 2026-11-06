"""Offline checks that checkpoints cannot make old/mixed observations look fresh."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from collector.daily import collect_shard,collection_run_id,fingerprint,merge,shard_for


CLOCK='2026-11-06T12:00:00+00:00'


class DailyIntegrityTests(unittest.TestCase):
    def payloads(self,root):
        sources=[dict(id='example',enabled=True)]
        for shard in range(2):
            ids=[s['id'] for s in sources if shard_for(s['id'],2)==shard]
            value=dict(schema_version=1,run_id='run-1',shard=shard,shards=2,
                registry_fingerprint=fingerprint(sources),complete=True,
                started_at='2026-11-06T11:00:00+00:00',finished_at='2026-11-06T11:30:00+00:00',
                expected_source_ids=ids,parts=[dict(report=dict(id=sid,status='ok',checked_at='2026-11-06T11:00:00+00:00'),jobs=[],closure_eligible=[]) for sid in ids])
            (root/f'shard-{shard}.json').write_text(json.dumps(value))
        return sources

    def merge_case(self,change=None,rejected=None):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);sources=self.payloads(root)
            catalog=root/'catalog.json';original=json.dumps(dict(jobs=[],updated_at='2026-11-05T12:00:00+00:00'))
            catalog.write_text(original)
            if change:
                path=root/'shard-1.json';value=json.loads(path.read_text());change(value);path.write_text(json.dumps(value))
            with patch('collector.daily.provision_files',return_value=([],sources)),patch('collector.daily.now',return_value=CLOCK),patch('collector.daily.finalize',return_value=({'jobs':[]},{})) as finalized:
                if rejected:
                    with self.assertRaisesRegex(ValueError,rejected):merge(root,2,root,run_id='run-1')
                    finalized.assert_not_called();self.assertEqual(catalog.read_text(),original)
                else:
                    merge(root,2,root,run_id='run-1')
                    self.assertEqual(finalized.call_args.args[5],'2026-11-06T11:30:00+00:00')

    def test_same_run_recent_shards_merge(self):
        self.merge_case()

    def test_finish_times_are_compared_as_instants_across_offsets(self):
        def change(payload):
            payload.update(started_at='2026-11-06T13:00:00+02:00',finished_at='2026-11-06T13:30:00+02:00')
        self.merge_case(change)

    def test_different_run_and_missing_run_id_preserve_catalog(self):
        for run_id in ('another-run',None):
            with self.subTest(run_id=run_id):
                self.merge_case(lambda p:p.update(run_id=run_id),'another collection run')

    def test_future_expired_reversed_and_naive_times_preserve_catalog(self):
        for change in (
            dict(finished_at='2026-11-06T13:00:00+00:00'),
            dict(started_at='2026-11-05T10:00:00+00:00',finished_at='2026-11-05T11:00:00+00:00'),
            dict(started_at='2026-11-06T11:45:00+00:00'),
            dict(finished_at='2026-11-06T11:30:00'),
            dict(finished_at='not-a-time'),
        ):
            with self.subTest(change=change):
                self.merge_case(lambda p:p.update(change),'timestamp')

    def test_source_time_must_belong_to_its_shard(self):
        # Both shards carry a source only when assigned; inject an old report
        # into the otherwise empty shard so the temporal check runs first.
        def change(payload):
            payload['parts']=[dict(report=dict(id='example',checked_at='2026-10-01T12:00:00+00:00'))]
        self.merge_case(change,'outside shard collection interval')

    def test_multi_shard_requires_run_id_before_provisioning(self):
        with patch.dict(os.environ,{},clear=True),patch('collector.daily.provision_files') as provisioned:
            with self.assertRaisesRegex(ValueError,'requires --run-id'):collect_shard(shards=2)
            with self.assertRaisesRegex(ValueError,'requires --run-id'):merge('.',shards=2)
            provisioned.assert_not_called()

    def test_collect_stores_explicit_and_environment_run_ids(self):
        for explicit,environment,expected in [('manual-run',None,'manual-run'),(None,'123/2','123/2'),(None,None,None)]:
            with self.subTest(expected=expected),tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{},clear=True),patch('collector.daily.provision_files',return_value=([],[])),patch('collector.daily.read',side_effect=lambda path,default:default),patch('collector.daily.now',return_value=CLOCK):
                if environment:os.environ['COLLECTOR_RUN_ID']=environment
                output=Path(directory)/'shard-0.json'
                payload=collect_shard(shards=1,output=output,run_id=explicit)
                self.assertEqual(payload['run_id'],expected)
                self.assertEqual(json.loads(output.read_text())['run_id'],expected)

    def test_invalid_run_id_rejected(self):
        for value in ('','contains spaces','line\nbreak'):
            with self.subTest(value=value),self.assertRaises(ValueError):collection_run_id(2,value)


if __name__=='__main__':unittest.main()
