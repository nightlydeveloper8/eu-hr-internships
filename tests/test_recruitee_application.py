"""Opt-in Recruitee verification: current feed, employer, ID and visible form."""
import copy,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from collector.public_feeds import recruitee_records
from collector.verification import verify_vacancy,applicant_form
from collector.pipeline import process_source,finalize
from collector.applications import ApplicationClosed

FOLDER=Path(__file__).parent/'fixtures/eu27-recruitee'
STAMP='2026-11-16T12:00:00+00:00'


class Client:
    def __init__(self,bodies):self.bodies=bodies;self.calls=[];self.redirects={}
    def request(self,url,method='GET',**kwargs):
        assert method=='GET';self.calls.append(url)
        return self.bodies[url],200,self.redirects.get(url,url)


class RecruiteeApplicationTests(unittest.TestCase):
    def setUp(self):
        self.source=dict(id='recruitee-monsterscore',employer='Monsterscore',adapter='recruitee',
            enabled=False,application_check='recruitee-linked',
            feed_url='https://monsterscore.recruitee.com/api/offers',allowed_hosts=['monsterscore.recruitee.com'])
        self.feed=(FOLDER/'feed.json').read_bytes();self.job=json.loads(self.feed)['offers'][0]
        self.vacancy=self.job['careers_url'];self.application=self.job['careers_apply_url']
        self.page=gzip.decompress((FOLDER/'vacancy.html.gz').read_bytes())
        self.form=gzip.decompress((FOLDER/'application.html.gz').read_bytes())
        self.client=Client({self.source['feed_url']:self.feed,self.vacancy:self.page,self.application:self.form})
        self.record=recruitee_records(self.source,self.client)[0]

    def verify(self):return verify_vacancy(self.record,self.source,self.client,STAMP)

    def test_reduced_real_fixture_hashes_and_visible_application(self):
        meta=json.loads((FOLDER/'provenance.json').read_text())
        self.assertEqual(hashlib.sha256(self.page).hexdigest(),meta['fixture_body_sha256']['vacancy'])
        self.assertEqual(hashlib.sha256(self.form).hexdigest(),meta['fixture_body_sha256']['application'])
        self.assertTrue(applicant_form(self.page))
        self.assertFalse(applicant_form(self.page,strict=True))
        self.assertTrue(applicant_form(self.form,strict=True))
        self.assertEqual(self.verify()['method'],'official-recruitee-same-posting-visible-form')
        self.assertEqual(self.verify()['url'],self.application)

    def test_legacy_sources_keep_their_existing_record_shape(self):
        source=dict(self.source);source.pop('application_check')
        record=recruitee_records(source,self.client)[0]
        self.assertEqual(record['apply_url'],self.vacancy)
        self.assertNotIn('observed_application_url',record)
        self.assertNotIn('posting_identifier',record)

    def test_missing_observed_entry_never_invents_c_new_or_uses_hidden_tab(self):
        self.record.pop('observed_application_url')
        with self.assertRaisesRegex(ValueError,'feed and vacancy identity'):self.verify()
        self.assertNotIn(self.application,self.client.calls)

    def test_static_cache_label_or_wrong_collected_id_fails_before_application(self):
        for change in [dict(inventory_evidence='cache'),dict(posting_identifier='570049')]:
            with self.subTest(change=change):
                previous=copy.deepcopy(self.record);self.record.update(change)
                with self.assertRaises(ValueError):self.verify()
                self.record=previous
        self.assertNotIn(self.application,self.client.calls)

    def test_cross_host_other_slug_query_and_fragment_are_rejected(self):
        for url in [self.application.replace('monsterscore.recruitee.com','evil.example'),
                    self.application.replace('/stageplek-human-resources-management','/other'),
                    self.application+'?id=570048',self.application+'#apply']:
            with self.subTest(url=url):
                self.record['observed_application_url']=url
                with self.assertRaises(ValueError):self.verify()
                self.assertNotIn(url,self.client.calls)

    def test_wrong_application_title_identifier_employer_or_redirect_fails(self):
        mutations=[self.form.replace(b'Stageplek Human Resources Management',b'Stage Finance'),
                   self.form.replace(b'570048',b'570049'),self.form.replace(b'Monsterscore',b'Other Employer')]
        for body in mutations:
            with self.subTest(body_hash=hashlib.sha256(body).hexdigest()):
                self.client.bodies[self.application]=body
                with self.assertRaises(ValueError):self.verify()
        self.client.bodies[self.application]=self.form
        self.client.redirects[self.application]=self.vacancy
        with self.assertRaises(ValueError):self.verify()

    def test_disabled_or_hidden_form_cannot_establish_application(self):
        for body in [self.page,self.form.replace(b'<form ',b'<form hidden '),
                     self.form.replace(b'<button ',b'<button disabled ')]:
            with self.subTest(body_hash=hashlib.sha256(body).hexdigest()):
                self.client.bodies[self.application]=body
                with self.assertRaises(ValueError):self.verify()

    def test_closed_challenged_and_expired_application_fail(self):
        for suffix in [b'This vacancy is closed',b'Verify you are human']:
            self.client.bodies[self.application]=self.form.replace(b'<main>',b'<main>'+suffix)
            with self.assertRaises(ValueError):self.verify()
        text=self.form.decode().replace('"@type": "JobPosting"','"@type": "JobPosting", "validThrough":"2020-01-01"')
        self.client.bodies[self.application]=text.encode()
        with self.assertRaises(ApplicationClosed):self.verify()

    def test_feed_rejects_unapproved_observed_application_host(self):
        data=json.loads(self.feed);data['offers'][0]['careers_apply_url']='https://evil.example/apply'
        client=Client({self.source['feed_url']:json.dumps(data).encode()})
        with self.assertRaises(ValueError):recruitee_records(self.source,client)
        self.assertEqual(client.calls,[self.source['feed_url']])

    def test_two_pipeline_cycles_preserve_existing_ids_without_production_writes(self):
        root=FOLDER.parents[2];prior=json.loads((root/'data/catalog.json').read_text());old={j['id'] for j in prior['jobs']}
        part=process_source(self.source,self.client,STAMP)
        self.assertEqual(len(part['jobs']),1)
        self.assertEqual(part['jobs'][0]['status'],'open')
        self.assertEqual(part['jobs'][0]['verification']['policy_version'],2)
        with tempfile.TemporaryDirectory() as folder:
            first,_=finalize([self.source],[self.source],copy.deepcopy(prior),{},[part],STAMP,Path(folder)/'first')
            second,_=finalize([self.source],[self.source],copy.deepcopy(first),{},[part],STAMP,Path(folder)/'second')
        self.assertEqual(first['jobs'],second['jobs'])
        ids={j['id'] for j in first['jobs']}
        self.assertEqual(len(ids-old),1)
        self.assertTrue(old.issubset(ids))
        self.assertFalse(self.source['enabled'])


if __name__=='__main__':unittest.main()
