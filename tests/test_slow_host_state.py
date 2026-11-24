from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from collector.classify import stable_id
from collector.daily import fingerprint, merge, provision, split_collection_sources
from collector.pipeline import ROOT, read, write


class SlowHostStateTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.stamp = '2026-11-25T06:30:00+00:00'
        self.snapshot_time = '2026-11-25T03:17:00+00:00'
        sources = read(ROOT/'data/sources.json', [])
        self.slow = next(s for s in sources if s.get('slow_collection_lane'))
        self.regular = next(s for s in sources if s['id'] == 'public-eu-eures')
        self.sources = [self.slow, self.regular]
        url = 'https://www.gigroup.it/offerte-lavoro-dettaglio/milano-stage-risorse-umane/123'
        self.prior = dict(id=stable_id(self.slow['id'],url),external_id=url,
                          source_id=self.slow['id'],employer='Gi Group',title='Stage Risorse Umane',
                          country='IT',countries=['IT'],url=url,apply_url=url,
                          category='hr-generalist',categories=['hr-generalist'],
                          internship_type='internship',internship_confidence='confirmed',
                          workplace_languages=[],status='open',missing_count=2,
                          last_seen_at=self.stamp,last_verified_at=self.stamp,
                          verification=dict(state='verified',policy_version=2))
        write(self.root/'catalog.json', {'jobs': [self.prior]})
        self.inputs = self.root/'results'
        write(self.inputs/'shard-0.json', self.payload(self.regular, self.stamp))
        self.state = self.root/'slow.json'

    def payload(self, source, stamp, jobs=()):
        source_id = source['id']
        report = dict(id=source_id, status='ok', checked_at=stamp, records_inspected=len(jobs))
        return dict(schema_version=1, shard=0, shards=1, run_id='test',
                    registry_fingerprint=fingerprint([source]), started_at=stamp,
                    finished_at=stamp, complete=True,
                    parts=[dict(report=report,jobs=list(jobs),closure_eligible=[source_id])])

    def merge_state(self):
        with patch('collector.daily.now', return_value=self.stamp), patch(
                'collector.daily.provision_files', return_value=([],self.sources)):
            result,coverage,_ = merge(self.inputs,1,self.root,'test',slow_state=self.state)
        return result['jobs'],coverage

    def test_missing_snapshot_preserves_id_and_does_not_count_as_absence(self):
        jobs,_ = self.merge_state()
        self.assertEqual([(j['id'],j['status'],j['missing_count']) for j in jobs],
                         [(self.prior['id'],'open',2)])

    def test_old_snapshot_does_not_count_as_absence(self):
        write(self.state, self.payload(self.slow, '2026-11-23T03:17:00+00:00'))
        jobs,coverage = self.merge_state()
        self.assertEqual([(j['id'],j['status'],j['missing_count']) for j in jobs],
                         [(self.prior['id'],'open',2)])
        self.assertNotIn(self.slow['id'], {r['id'] for r in coverage['sources']})

    def test_fresh_snapshot_refreshes_same_id_once(self):
        sighting = dict(self.prior,last_seen_at=self.snapshot_time,last_verified_at=self.snapshot_time)
        write(self.state, self.payload(self.slow,self.snapshot_time,[sighting]))
        jobs,coverage = self.merge_state()
        self.assertEqual([(j['id'],j['status'],j['missing_count']) for j in jobs],
                         [(self.prior['id'],'open',0)])
        self.assertEqual(next(r for r in coverage['sources'] if r['id']==self.slow['id'])['checked_at'],
                         self.snapshot_time)
        write(self.root/'catalog.json', {'jobs': [dict(jobs[0],missing_count=1)]})
        jobs,_ = self.merge_state()
        self.assertEqual(jobs[0]['missing_count'],1)

    def test_provisioning_does_not_create_a_duplicate_slow_host_crawler(self):
        companies = read(ROOT/'data/companies.json', [])
        sources = read(ROOT/'data/sources.json', [])
        self.assertEqual(provision(companies,sources), (companies,sources))
        regular,slow = split_collection_sources(sources)
        self.assertIn(self.slow, slow)
        self.assertFalse(any(set(s['allowed_hosts']) & set(self.slow['allowed_hosts']) for s in regular))
        peer = dict(self.slow,id='same-host',slow_collection_lane=False)
        self.assertIn(peer,split_collection_sources(sources+[peer])[1])
