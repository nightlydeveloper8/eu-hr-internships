import unittest
from unittest.mock import patch
from collector.rendering import unigarant_inventory_search
from collector.unigarant import inventory_records,index_records
from collector.employer_pages import index_records as html_index

class UnigarantTests(unittest.TestCase):
    def test_application_read_cannot_inherit_inventory_post_exceptions(self):
        from unittest.mock import Mock
        from collector.rendering import render_pages
        for option in ('cegid_search','unigarant_search'):
            client=Mock()
            with self.assertRaisesRegex(ValueError,'cannot enable inventory POSTs'):
                render_pages('https://werkenbijunigarant.nl/vacatures/',client,lambda url:True,
                             application_read=True,**{option:True})
            client.permitted.assert_not_called()

    def setUp(self):
        self.url='https://werkenbijunigarant.nl/vacatures/'
        self.source=dict(id='unigarant',employer='Unigarant',allowed_hosts=['werkenbijunigarant.nl'],index_urls=[self.url],index_error_pattern='Er ging iets mis',discovery_scope='Official public inventory')
        self.item=dict(id=1,title='Stage',shortDescription='HR recruitment meewerkstage.',type='student',url='https://werkenbijunigarant.nl/vacature/stage/')
        self.payload='--Boundary\r\nContent-Disposition: form-data; name="page"\r\n\r\n1\r\n--Boundary--\r\n'

    def test_public_pagination_has_exact_host_path_and_single_page_field(self):
        endpoint='https://werkenbijunigarant.nl/vacatures-ajax'
        self.assertTrue(unigarant_inventory_search(endpoint,self.payload,self.url))
        for target in [endpoint+'/apply',endpoint+'?page=1',endpoint+'#x',endpoint.replace('https:','http:'),endpoint.replace('unigarant.nl','unigarant.nl.evil.example')]:
            self.assertFalse(unigarant_inventory_search(target,self.payload,self.url))
        for value in [None,self.payload.replace('name="page"','name="email"'),self.payload.replace('\r\n1\r\n','\r\n0\r\n'),self.payload.replace('\r\n1\r\n','\r\n1000\r\n'),self.payload+'extra',self.payload.replace('--Boundary--','--Different--'),'{"page":1}']:
            self.assertFalse(unigarant_inventory_search(endpoint,value,self.url))
        self.assertFalse(unigarant_inventory_search(endpoint,self.payload,self.url+'?types=student'))

    def test_short_description_and_unknown_workplace_remain_separate(self):
        rows,scope=inventory_records(dict(success=True,total=1,vacancies=[self.item]),self.source)
        self.assertTrue(scope['complete']);self.assertEqual(rows[0]['text'],'HR recruitment meewerkstage.')
        self.assertIsNone(rows[0]['city']);self.assertIsNone(rows[0]['country']);self.assertEqual(rows[0]['countries'],[])
        self.assertFalse(inventory_records(dict(success=True,total=2,vacancies=[self.item]),self.source)[1]['complete'])
        def render(*args,**kwargs):kwargs['unigarant_responses'].append(dict(success=True,total=1,vacancies=[self.item]));return [],True
        with patch('collector.rendering.render_pages',side_effect=render):result=index_records(self.source,None)
        self.assertTrue(result.stats['observed_scopes'][0]['complete'])
        self.assertFalse(result.stats['complete']);self.assertFalse(result.stats['closure_complete']);self.assertEqual(result.stats['status'],'partial')

    def test_errors_duplicates_external_urls_and_contradictory_counts_fail(self):
        for data in [dict(success=False,total=0,vacancies=[]),dict(success=True,total='0',vacancies=[]),dict(success=True,total=0,vacancies=[self.item]),dict(success=True,total=2,vacancies=[self.item,self.item]),dict(success=True,total=1,vacancies=[dict(self.item,url='https://evil.example/vacature/stage/')]),dict(success=True,total=1,vacancies=[dict(self.item,id=0)])]:
            with self.assertRaises(ValueError):inventory_records(data,self.source)

    def test_loading_failure_cannot_become_a_reviewed_empty_inventory(self):
        source=dict(self.source,job_url_pattern=r'/vacature/[^/]+',reviewed_empty_index=dict(heading='Vacatures',pattern='Geen vacatures'))
        class Client:
            def request(self,url):return b'<h1>Vacatures</h1>Geen vacatures. Er ging iets mis.',200,url
        with self.assertRaisesRegex(ValueError,'loading error'):html_index(source,Client())
