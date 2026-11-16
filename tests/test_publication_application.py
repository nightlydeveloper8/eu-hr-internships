"""Reviewed multilingual portal: exact inventory scope and same-ID visible form."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from collector.pipeline import process_source,finalize
from collector.employer_pages import index_records
from collector.verification import verify_vacancy
from collector.classify import classify_role

FOLDER=Path(__file__).parent/'fixtures/bsh-publication'
ROOT=Path(__file__).resolve().parents[1]
STAMP='2026-11-16T12:10:00+00:00'

class Client:
    def __init__(self,bodies):self.bodies=bodies;self.calls=[];self.redirects={}
    def request(self,url,method='GET',**kwargs):
        assert method=='GET';self.calls.append(url)
        return self.bodies[url],200,self.redirects.get(url,url)

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.bundle=json.loads((ROOT/'docs/eu27-expansion/batch-02-integration-bundle.json').read_text())
        self.source=copy.deepcopy(self.bundle['sources'][0]);self.lead=self.bundle['reviewed_internships'][0]
        self.index=self.source['index_urls'][0];self.vacancy=self.lead['vacancy_url'];self.application=self.lead['application_url'].split('?')[0]
        self.listed='https://jobs.bsh-group.de/46112-practicas-recursos-humanos-formacion/de/job.html'
        self.page=(FOLDER/'vacancy.html').read_bytes();self.form=(FOLDER/'application.html').read_bytes()
        self.client=Client({self.index:(FOLDER/'index.html').read_bytes(),self.vacancy:self.page,self.listed:self.page,self.application:self.form})
        self.client.redirects={self.listed:self.vacancy,self.application:self.lead['application_url']}
        self.record=dict(external_id='46112',url=self.vacancy,title=self.lead['title'])
    def verify(self):return verify_vacancy(self.record,self.source,self.client,STAMP)

    def test_spanish_placement_prefix_without_promoting_good_practices(self):
        self.assertEqual(classify_role('Prácticas Recursos Humanos - Formación')['internship_type'],'internship')
        self.assertIsNotNone(classify_role('Human Resources',employment='Prácticas'))
        for title in ['Responsable de buenas prácticas de Recursos Humanos','HR Manager','Prácticas Marketing Digital']:
            self.assertIsNone(classify_role(title,'Buenas prácticas de RRHH y recursos humanos'))

    def test_real_reduced_fixture_hashes(self):
        meta=json.loads((FOLDER/'provenance.json').read_text())
        for name,digest in meta['fixture_sha256'].items():self.assertEqual(hashlib.sha256((FOLDER/name).read_bytes()).hexdigest(),digest)

    def test_full_regular_index_excludes_unsolicited_applications(self):
        records=index_records(self.source,self.client)
        self.assertEqual(len(records),15)
        self.assertNotIn('40211',{r['external_id'] for r in records});self.assertNotIn('34367',{r['external_id'] for r in records})
        self.assertFalse(any(r['needs_page'] for r in records));self.assertTrue(records.stats['complete'])
        self.assertFalse(records.stats['closure_complete'])
        self.assertEqual(records.stats['page_discovery_mode'],'reviewed-full-index-titles-then-matching-pages')

    def test_missing_duplicate_scope_or_different_count_fails_closed(self):
        original=self.client.bodies[self.index]
        for page in [original.replace(b'id="publicationsList"',b'id="renamed"'),original+original,
                     original.replace(b'15 offene Stellen',b'16 offene Stellen')]:
            with self.subTest(page=hashlib.sha256(page).hexdigest()):
                self.client.bodies[self.index]=page
                with self.assertRaises(ValueError):index_records(self.source,self.client)

    def test_full_titles_opt_in_requires_count_and_rejects_truncated_title(self):
        self.source.pop('index_job_count_pattern')
        with self.assertRaisesRegex(ValueError,'published inventory count'):index_records(self.source,self.client)
        self.setUp();self.client.bodies[self.index]=self.client.bodies[self.index].replace('Prácticas Recursos Humanos -  Formación'.encode(),b'HR...')
        with self.assertRaisesRegex(ValueError,'truncated'):index_records(self.source,self.client)

    def test_without_opt_in_index_keeps_legacy_page_enrichment(self):
        self.source.pop('index_titles_complete')
        self.assertTrue(all(r['needs_page'] for r in index_records(self.source,self.client)))

    def test_visible_same_posting_form_and_document_reuse(self):
        proof=self.verify();self.assertEqual(proof['method'],'official-publication-same-posting-visible-form')
        self.assertEqual(proof['url'],self.lead['application_url'])
        self.assertEqual(self.client.calls,[self.vacancy,self.application])

    def test_no_observed_entry_or_wrong_collected_id_never_invents_route(self):
        self.client.bodies[self.vacancy]=self.page.replace(b'/job_application/new',b'/other')
        with self.assertRaises(ValueError):self.verify()
        self.assertNotIn(self.application,self.client.calls)
        self.setUp();self.record['external_id']='46113'
        with self.assertRaises(ValueError):self.verify()
        self.assertNotIn(self.application,self.client.calls)

    def test_application_different_title_action_posting_or_redirect_rejected(self):
        for body in [self.form.replace('Prácticas Recursos Humanos -  Formación'.encode(),b'Finance Intern'),
                     self.form.replace(b'/46112-',b'/46113-')]:
            with self.subTest(body=hashlib.sha256(body).hexdigest()):
                self.client.bodies[self.application]=body
                with self.assertRaises(ValueError):self.verify()
        self.client.bodies[self.application]=self.form
        for url in [self.application.replace('bsh-group.de','other.example'),self.application.replace('46112','46113'),self.application+'?session=abc']:
            self.client.redirects[self.application]=url
            with self.assertRaises(ValueError):self.verify()

    def test_hidden_disabled_missing_fields_and_submit_rejected(self):
        for body in [self.form.replace(b'<form ',b'<form hidden '),self.form.replace(b'type="submit"',b'type="submit" disabled'),
                     self.form.replace(b'<input ',b'<input disabled '),self.form.replace(b'[account][email]',b'[account][other]'),
                     self.form.replace(b'file-upload-curriculum_vitae',b'other-file')]:
            with self.subTest(body=hashlib.sha256(body).hexdigest()):
                self.client.bodies[self.application]=body
                with self.assertRaises(ValueError):self.verify()

    def test_only_hr_page_is_read_and_two_cycles_preserve_old_ids(self):
        part=process_source(self.source,self.client,STAMP);first=part['jobs'];report=part['report']
        self.assertEqual(len(first),1);self.assertEqual(first[0]['status'],'open');self.assertEqual(first[0]['country'],'ES')
        self.assertEqual(report['collected'],15);self.assertEqual(len(self.client.calls),4)
        previous=json.loads((ROOT/'data/catalog.json').read_text());expected=first[0]['id']
        absent=copy.deepcopy(previous);absent['jobs']=[j for j in absent['jobs'] if j['id']!=expected]
        for baseline in [absent,previous]:
            old_ids={j['id'] for j in baseline['jobs']}
            with tempfile.TemporaryDirectory() as folder:
                merged,_=finalize([self.source],[self.source],copy.deepcopy(baseline),{},[part],STAMP,Path(folder)/'first')
                second,_=finalize([self.source],[self.source],copy.deepcopy(merged),{},[part],STAMP,Path(folder)/'second')
            self.assertEqual({j['id'] for j in merged['jobs']},old_ids|{expected})
            self.assertEqual(merged['jobs'],second['jobs'])
        self.client.bodies[self.listed]=self.page.replace(b'Zaragoza',b'UnknownTown')
        unresolved=process_source(self.source,self.client,STAMP)
        self.assertEqual(unresolved['jobs'],[])
        self.assertTrue(unresolved['report']['page_errors'])

if __name__=='__main__':unittest.main()
