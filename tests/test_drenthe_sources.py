import unittest
from unittest.mock import patch
from collector.applications import verify_application, ApplicationClosed
from collector.verification import verify_vacancy
from collector.employer_pages import page_record,index_records
from collector.classify import extract_metadata

class Client:
    def __init__(self,pages):self.pages=pages;self.calls=[]
    def request(self,url,**kwargs):self.calls.append(url);return self.pages[url].encode(),200,url
    def check(self):pass
    def remaining(self):return 100

class DrentheSourceTests(unittest.TestCase):
    def test_email_requires_reviewed_address_and_current_application_instruction(self):
        url='https://example.org/jobs/hr';source=dict(application_check='official-email',application_email='hr@example.org',allowed_hosts=['example.org'])
        page='<main><h1>HR stage</h1><p>Stuur je motivatie en CV naar <a href="mailto:hr@example.org">hr@example.org</a></p></main>'
        record=dict(url=url,title='HR stage');c=Client({url:page})
        proof=verify_vacancy(record,source,c,'2026-11-06T12:00:00+00:00')
        self.assertEqual(proof['method'],'official-vacancy-email-instructions');self.assertFalse(proof['delivery_verified'])
        for invalid in [page.replace('Stuur je motivatie en CV naar','Contact:'),page.replace('mailto:hr@','mailto:service@'),page.replace('<h1>HR stage','<h1>Other stage')]:
            with self.assertRaises(ValueError):verify_vacancy(record,source,Client({url:invalid}),'2026-11-06T12:00:00+00:00')
        with self.assertRaises(ApplicationClosed):verify_vacancy(record,source,Client({url:page.replace('</main>','This job is closed</main>')}),'2026-11-06T12:00:00+00:00')

    def test_formie_requisition_title_fields_and_enabled_submit_must_agree(self):
        url='https://example.org/jobs/hr';app='https://example.org/solliciteren?vacature=4260'
        source=dict(application_check='formie-linked',allowed_hosts=['example.org'])
        record=dict(url=url,title='HR stage',posting_identifier='4260')
        page='<h1>HR stage</h1><a href="/solliciteren?vacature=4260">Solliciteren</a>'
        form='<main>Solliciteren voor: HR stage<form data-form-handle="applicationFormOne"><input name="fields[vacancyId]" value="4260"><input name="fields[firstName]"><input name="fields[email]"><button type="submit">Apply</button></form></main>'
        self.assertEqual(verify_application(record,source,Client({url:page,app:form}))['url'],app)
        for invalid in [form.replace('value="4260"','value="99"'),form.replace('voor: HR stage','voor: Other stage'),form.replace('type="submit"','type="submit" disabled')]:
            with self.assertRaises(ValueError):verify_application(record,source,Client({url:page,app:invalid}))

    def test_reviewed_visible_workplace_comes_from_current_text(self):
        url='https://example.org/jobs/hr';source=dict(allowed_hosts=['example.org'],page_format='reviewed-visible',reviewed_workplaces=[dict(pattern=r'Locatie: Assen\b',city='Assen',country='NL')])
        page='<main><h1>HR stage</h1>Locatie: Assen '+('Relevant HR internship text. '*15)+'</main>'
        result=page_record(dict(url=url),source,Client({url:page}));self.assertEqual(result['city'],'Assen')
        with self.assertRaises(ValueError):page_record(dict(url=url),source,Client({url:page.replace('Locatie: Assen','Locatie: Amsterdam')}))

    def test_rendered_inventory_requires_matching_live_count(self):
        url='https://example.org/jobs';source=dict(id='one',employer='One',allowed_hosts=['example.org'],index_urls=[url],index_rendered=True,job_url_pattern=r'/job/',index_job_count_pattern=r'(\d+) results')
        body=b'1 results <a href="/job/1">HR stage</a>'
        with patch('collector.rendering.render_pages',return_value=([(url,body)],True)):
            self.assertEqual(len(index_records(source,Client({}))),1)
        with patch('collector.rendering.render_pages',return_value=([(url,body.replace(b'1 results',b'2 results'))],True)):
            with self.assertRaisesRegex(ValueError,'inventory count'):index_records(source,Client({}))
        with patch('collector.rendering.render_pages',return_value=([(url,body)],False)):
            with self.assertRaisesRegex(ValueError,'incomplete'):index_records(source,Client({}))

    def test_dutch_education_requirement_is_preserved(self):
        self.assertEqual(extract_metadata('Je volgt een HBO-opleiding Human Resource Management en zit in het tweede jaar.')['enrollment'],'Je volgt een HBO-opleiding Human Resource Management en zit in het tweede jaar.')
        self.assertIsNone(extract_metadata('We offer training and workshops.')['enrollment'])

    def test_captcha_meta_refresh_is_blocked_before_browser_navigation(self):
        from collector.universal import Crawler
        url='https://example.org/jobs'
        source=dict(id='captcha-test',employer='Example',allowed_hosts=['example.org'])
        body='<html><head><meta http-equiv="refresh" content="0;/.well-known/sgcaptcha/?r=jobs"></head></html>'
        with patch('collector.rendering.render_pages') as render:
            with self.assertRaisesRegex(ValueError,'Access challenge'):
                Crawler(source,Client({url:body})).visit(url)
        render.assert_not_called()
