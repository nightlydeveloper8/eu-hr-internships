import unittest,json,tempfile,os
from unittest.mock import patch
from urllib.error import URLError
from collector.reviewed_html import aware_record
from collector.friesland import coverage
from collector.classify import canonical_url
from collector.adapters import Client
from collector.employer_pages import PageParser
from collector.universal import Document,job_from_visible,Crawler,provider_host
from collector.pipeline import apply_listing_reviews


class FrieslandTests(unittest.TestCase):
    def test_custom_recruitee_feed_requires_same_site_postings(self):
        class PublicClient:
            def __init__(self,external=False):self.calls=[];self.external=external
            def remaining(self):return 60
            def check(self):pass
            def request(self,url):
                self.calls.append(url)
                if url.rstrip('/').endswith('/api/offers'):
                    return json.dumps({'offers':[dict(id=1,status='published',title='HR Intern',description='HR internship',careers_url='https://example.org/o/hr',country_code='NL',city='Sneek')]}).encode(),200,url
                href='https://other.recruitee.com/o/hr' if self.external else '/o/hr'
                return ('<a href="'+href+'">HR Intern</a><a href="https://recruitee.com">Platform credit</a>').encode(),200,url
        source=dict(id='custom',employer='Example',allowed_hosts=['example.org'],start_urls=['https://example.org/jobs'],no_browser=True)
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'COLLECTOR_CACHE_DIR':folder}):
            client=PublicClient();crawler=Crawler(source,client);crawler.visit('https://example.org/jobs')
            self.assertEqual(len(crawler.records),1)
            self.assertIn('https://example.org/api/offers',client.calls)
            external=PublicClient(external=True);Crawler(dict(source,id='external'),external).visit('https://example.org/jobs')
            self.assertNotIn('https://example.org/api/offers',external.calls)
        self.assertFalse(provider_host('recruitee.com'))
        self.assertTrue(provider_host('employer.recruitee.com'))
    def test_tls_fallback_preserves_robots_restrictions(self):
        client=Client(delay=0)
        with patch.object(client,'permitted',return_value=False),patch('collector.tls_transport.request') as transport:
            with self.assertRaises(ValueError):client.request('https://example.org/jobs')
            transport.assert_not_called()
        with patch.object(client,'permitted',return_value=True),patch('collector.adapters.urlopen',side_effect=URLError('TLSV1_ALERT_PROTOCOL_VERSION')),patch('collector.tls_transport.request',return_value=(b'ok',200,'https://example.org/jobs')) as transport:
            self.assertEqual(client.request('https://example.org/jobs')[1],200)
            transport.assert_called_once()

    def test_cdata_wrapper_is_json_only(self):
        parser=PageParser();parser.feed('<script type="application/ld+json">//<![CDATA[ {"@type":"JobPosting","title":"Meewerkstage HR"} //]]></script>')
        self.assertEqual(parser.scripts[0]['title'],'Meewerkstage HR')

    def test_company_locations_in_prose_are_not_a_labelled_job_city(self):
        doc=Document(b'<main><h1>Meewerkstage HR</h1><p>Wij werken vanuit Wolvega voor onze locaties in Wolvega, Leeuwarden, Buitenpost en Groningen.</p></main>','https://example.org/job/hr')
        self.assertIsNone(job_from_visible(doc,{'id':'example','employer':'Example'})['city'])

    def test_pending_application_review_overrides_a_successful_head_check(self):
        job=dict(url='https://example.org/job/hr',status='open',last_verified_at='2026-11-06T06:00:00+00:00')
        result=apply_listing_reviews([job],[dict(url=job['url'],decision='needs-verification',reason='Application channel needs confirmation')])
        self.assertEqual(result[0]['status'],'unverified')
        self.assertEqual(result[0]['review_note'],'Application channel needs confirmation')
    def test_unicode_job_paths_are_encoded_without_double_encoding(self):
        url=canonical_url('https://example.org/vacatures/coördinator?utm_source=x')
        self.assertEqual(url,'https://example.org/vacatures/co%C3%B6rdinator')
        self.assertEqual(canonical_url(url),url)
    def test_reviewed_template_uses_job_heading_not_application_heading(self):
        body=b'''<section class="vacancy-hero"><h5 class="heading-xxl">Stage HR Heerenveen</h5><span class="location"><svg><text>icon</text></svg>Heerenveen</span></section><section class="vacancy-content"><h2>Jouw stage</h2><p>Je volgt een HBO opleiding HRM.</p></section><h1>Solliciteer nu</h1><form id="formie-vacancyApply-123"></form><footer><h5 class="heading-xxl">Join us</h5></footer>'''
        result=aware_record(body,{},dict(reviewed_city_countries={'Heerenveen':'NL'}))
        self.assertEqual(result['title'],'Stage HR Heerenveen')
        self.assertEqual(result['city'],'Heerenveen')
        self.assertEqual(result['countries'],['NL'])
        self.assertNotIn('Join us',result['text'])

    def test_missing_form_or_unreviewed_country_fails(self):
        body=b'<section class="vacancy-hero"><h5 class="heading-xxl">Stage HR</h5><span class="location">Unreviewed city</span></section><section class="vacancy-content">HR stage</section>'
        for candidate in [body,body+b'<form id="formie-vacancyApply-x"></form>']:
            with self.assertRaises(ValueError):aware_record(candidate,{},dict(reviewed_city_countries={'Heerenveen':'NL'}))

    def test_municipal_totals_overlap_but_provincial_employers_do_not(self):
        company=dict(id='one',name='One',source_ids=['one'],friesland_research={'size':{'qualification':'verified_50_plus','scope':'group'}},workplaces=[dict(region_code='NL12',city='Sneek',municipality_code='A',location_confidence='confirmed'),dict(region_code='NL12',city='Heerenveen',municipality_code='B',location_confidence='confirmed')])
        geography=dict(municipalities=[dict(cbs_code=c,name=c,settlement_count=1) for c in ['A','B','C']])
        jobs=[dict(id='local',status='open',internship_type='internship',source_id='one',employer='One',region_codes=['NL12']),dict(id='nonlocal',status='open',internship_type='internship',source_id='one',employer='One',region_codes=[]),dict(id='working-student',status='open',internship_type='working-student',source_id='one',employer='One',region_codes=['NL12'])]
        for job in jobs:job.update(link_status='verified',last_verified_at='2026-11-06T05:00:00+00:00')
        r=coverage([company],[dict(id='one',enabled=True)],[dict(id='one',checked_at='2026-11-06T05:00:00+00:00',status='partial',records_inspected=2)],jobs,geography,'2026-11-06T06:00:00+00:00')
        self.assertEqual(r['summary']['employers'],1)
        self.assertEqual([m['qualified_employers'] for m in r['municipalities']],[1,1,0])
        self.assertEqual(r['verified_hr_internship_ids'],['local'])
        self.assertEqual(r['summary']['collection_states'],{'partial':1})
        self.assertFalse(r['exhaustive'])


if __name__=='__main__':unittest.main()
