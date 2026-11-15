"""Explicit direct email applications remain distinct from contact details."""
import unittest
import copy
import tempfile
from pathlib import Path
from collector.verification import verify_vacancy
from collector.pipeline import ROOT,read,process_source,finalize
from collector.classify import canonical_url
from tests.test_drenthe_sources import Client

URL = 'https://example.org/jobs/hr-intern'
SOURCE = dict(application_check='official-email',application_email='jobs@example.org',allowed_hosts=['example.org'])
RECORD = dict(url=URL,title='HR stage')
STAMP = '2026-11-15T18:20:00+00:00'


class DirectEmailApplicationTests(unittest.TestCase):
    def page(self, instruction, address='jobs@example.org'):
        return '<main><h1>HR stage</h1><p>'+instruction+' <a href="mailto:'+address+'">'+address+'</a></p></main>'

    def verify(self,page):
        return verify_vacancy(RECORD,SOURCE,Client({URL:page}),STAMP)

    def test_explicit_direct_application_without_mandatory_cv(self):
        page=self.page('Wil je direct reageren? Neem contact op met Recruitment via')
        proof=self.verify(page)
        self.assertEqual(proof['method'],'official-vacancy-email-instructions')
        self.assertEqual(proof['application_email'],'jobs@example.org')
        self.assertFalse(proof['delivery_verified'])

    def test_contact_negation_and_distant_address_are_not_instructions(self):
        for instruction in ['Heb je vragen? Neem contact op via',
                            'Wil je niet direct reageren? Neem contact op via',
                            'Wil je direct reageren? Lees de FAQ. Contact via',
                            'Wil je direct reageren? Neem contact op voor vragen via',
                            'Wil je direct reageren? Mail niet naar',
                            'Wil je direct reageren? Neem contact op '+('x '*100)+'via']:
            with self.subTest(instruction=instruction),self.assertRaises(ValueError):
                self.verify(self.page(instruction))

    def test_same_vacancy_and_reviewed_mailto_still_required(self):
        page=self.page('Wil je direct reageren? Neem contact op via')
        for changed in [page.replace('<h1>HR stage','<h1>Another vacancy'),
                        page.replace('mailto:jobs@','mailto:info@'),
                        page.replace('</main>','This job is closed</main>')]:
            with self.subTest(page=changed),self.assertRaises(ValueError):self.verify(changed)

    def test_registered_source_two_cycles_preserve_ids_and_region_without_network(self):
        registry=read(ROOT/'data/sources.json',[])
        source=next(s for s in registry if s['id']=='auto-webo')
        url=canonical_url('https://www.webo.nl/vacatures/stage-hrm/')
        page='<main>Terug <h1>Stage HRM</h1> Rijssen | HBO | Meewerkstage '+('Synthetic internship duties. '*15)
        page+='Wil je direct reageren? Neem contact op met Recruitment via <a href="mailto:werken@webo.nl">werken@webo.nl</a></main>'
        # The observed careers page may omit this stage from its featured list.
        # The reviewed visible seed must still be collected without inventing URLs.
        client=Client({canonical_url(source['index_urls'][0]):'<a href="/about">About</a>',url:page})
        part=process_source(source,client,STAMP)
        self.assertEqual(len(part['jobs']),1)
        self.assertEqual(part['jobs'][0]['status'],'open')
        self.assertFalse(part['report']['closure_complete'])
        prior=read(ROOT/'data/catalog.json',{})
        with tempfile.TemporaryDirectory() as folder:
            a,_=finalize(registry,[source],copy.deepcopy(prior),{},[part],STAMP,Path(folder)/'a')
            b,_=finalize(registry,[source],copy.deepcopy(a),{},[part],STAMP,Path(folder)/'b')
        self.assertEqual(a['jobs'],b['jobs'])
        previous={j['id'] for j in prior['jobs']}
        current={j['id'] for j in b['jobs']}
        self.assertTrue(previous.issubset(current))
        self.assertEqual(len(current-previous),1)
        job=next(j for j in b['jobs'] if j['id'] not in previous)
        self.assertEqual(job['region_codes'],['NL21'])
        self.assertEqual(job['countries'],['NL'])


if __name__=='__main__':unittest.main()
