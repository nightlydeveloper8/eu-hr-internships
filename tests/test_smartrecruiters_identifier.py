"""Observed employer query IDs bridge ATS slugs without proving availability."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import unittest
from collector.verification import shares_identifier, verify_vacancy


class SmartRecruitersIdentifierTests(unittest.TestCase):
    vacancy='https://careers-nl.jdepeets.com/job-posting-detail?id=744000158015131&return_url=%2Fjob-search%2F'
    target='https://jobs.smartrecruiters.com/JACOBSDOUWEEGBERTS/744000158015131-internship-talent-acquisition?oga=true'

    def test_observed_query_id_matches_exact_slug_prefix_without_mutation(self):
        for url in (self.vacancy,self.vacancy.replace('/job-posting-detail','/nl-NL/job-posting-detail')):
            record=dict(url=url,external_id=url)
            before=copy.deepcopy(record)
            self.assertTrue(shares_identifier(record,self.target))
            self.assertEqual(record,before)

    def test_wrong_missing_ambiguous_or_conflicting_vacancy_id_fails(self):
        for url in (self.vacancy.replace('744000158015131','744000158015132'),
                    self.vacancy.replace('id=744000158015131','tracking=744000158015131'),
                    self.vacancy+'&id=744000158015131',self.vacancy+'&id=',
                    self.vacancy.replace('/job-posting-detail','/search')):
            with self.subTest(url=url):self.assertFalse(shares_identifier(dict(url=url),self.target))
        for key in ('posting_identifier','external_id'):
            self.assertFalse(shares_identifier(dict(url=self.vacancy,**{key:'744000158015132'}),self.target))

    def test_target_host_path_and_id_are_not_inferred_from_tracking(self):
        for target in (self.target.replace('744000158015131','744000158015132'),
                       self.target.replace('744000158015131-','7440001580151310-'),
                       self.target.replace('jobs.smartrecruiters.com','jobs.smartrecruiters.com.evil.org'),
                       'https://jobs.smartrecruiters.com/search?id=744000158015131',
                       self.target.replace('744000158015131-','744000158015132-')+'&id=744000158015131'):
            with self.subTest(target=target):self.assertFalse(shares_identifier(dict(url=self.vacancy),target))

    def test_explicit_posting_identifier_also_matches(self):
        self.assertTrue(shares_identifier(dict(url='https://example.org/jobs/hr',posting_identifier='744000158015131'),self.target))

    def verify(self,body,final=None,allowed=True):
        page=('<h1>Internship Talent Acquisition</h1><a href="'+self.target+'">APPLY</a>').encode()
        parent=self
        class Client:
            def request(self,url):
                return (page,200,url) if url==parent.vacancy else (body,200,final or url)
        return verify_vacancy(dict(url=self.vacancy,title='Internship Talent Acquisition'),
                              dict(id='not-a-pilot',allowed_hosts=['careers-nl.jdepeets.com']+(['jobs.smartrecruiters.com'] if allowed else [])),Client(),'2026-11-15T20:00:00+00:00')

    def test_identity_does_not_replace_form_title_host_redirect_or_closure_gates(self):
        form=b'<h1>Internship Talent Acquisition</h1><form id="application"><input name="name"><input type="email"><button>Apply</button></form>'
        self.assertEqual(self.verify(form)['method'],'linked-same-vacancy-applicant-form')
        for body in (b'{"jobTitle":"Internship Talent Acquisition"}',form.replace(b'Talent Acquisition',b'Finance'),form.replace(b'<button>',b'<button disabled>'),b'Verify you are human'+form):
            with self.subTest(body=body),self.assertRaises(ValueError):self.verify(body)
        with self.assertRaises(ValueError):self.verify(form,allowed=False)
        with self.assertRaisesRegex(ValueError,'redirected'):self.verify(form,final=self.target.replace('744000158015131','744000158015132'))
        with self.assertRaises(ValueError):self.verify(form+b' This vacancy is closed')

    def test_real_response_replay_still_cannot_verify_a_json_posting(self):
        root=Path(__file__).resolve().parents[1]
        report=json.loads((root/'docs/jde-application-identity-2026-11-15.json').read_text())
        folder=root/'tests/fixtures/smartrecruiters-identity'
        bodies={name:gzip.decompress((folder/name).read_bytes()) for name in report['fixture_sha256']}
        for name,body in bodies.items():
            self.assertEqual(hashlib.sha256(body).hexdigest(),report['fixture_sha256'][name])
        parent=self
        class Client:
            calls=[]
            def request(self,url):
                self.calls.append(url)
                if url==parent.vacancy:return bodies['vacancy.html.gz'],200,url
                return bodies['application.html.gz'],200,parent.target.split('?')[0]
        record=dict(url=self.vacancy,title='Internship Talent Acquisition',external_id=self.vacancy)
        original=copy.deepcopy(record)
        for _ in range(2):
            client=Client();client.calls=[]
            with self.assertRaisesRegex(ValueError,'Application page does not identify the same vacancy'):
                verify_vacancy(record,dict(id='not-a-pilot',allowed_hosts=['careers-nl.jdepeets.com','jobs.smartrecruiters.com']),client,'2026-11-15T20:00:00+00:00')
            self.assertEqual(len(client.calls),2)
            self.assertEqual(record,original)


if __name__=='__main__':unittest.main()
