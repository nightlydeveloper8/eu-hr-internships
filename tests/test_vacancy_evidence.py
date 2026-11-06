"""Offline acceptance cases; no applications are submitted."""
import unittest
from unittest.mock import patch
from urllib.request import Request
from collector.verification import verify_vacancy, applicant_form
from collector.applications import ApplicationClosed
from collector.adapters import CheckedRedirect, Client
from collector.pipeline import process_source
from collector.classify import classify_role, workplace_languages, language_summary

STAMP='2026-11-06T12:00:00+00:00'
SOURCE=dict(id='test',employer='Example',adapter='lever',allowed_hosts=['example.org'])
URL='https://example.org/jobs/123'
FORM='<form id="application"><input name="name"><input type="email" name="email"><button type="submit">Apply</button></form>'
class Pages:
    def __init__(self,pages):self.pages=pages;self.calls=[]
    def request(self,url,**kwargs):
        self.calls.append((url,kwargs));value=self.pages[url]
        if isinstance(value,Exception):raise value
        if isinstance(value,tuple):return value
        return value.encode(),200,url

def record(**kwargs):
    return dict(dict(external_id='123',employer='Example',title='HR Intern',text='Fluent in English.',location='Berlin',url=URL,apply_url=URL,inventory_evidence='current-employer-feed'),**kwargs)

class VacancyEvidenceTests(unittest.TestCase):
    def test_http_200_and_title_alone_are_incomplete(self):
        client=Pages({URL:'<h1>HR Intern</h1>'})
        with self.assertRaisesRegex(ValueError,'application entry'):verify_vacancy(record(),SOURCE,client,STAMP)
        self.assertNotIn('HEAD',str(client.calls))
    def test_current_inventory_title_and_form_are_verified(self):
        result=verify_vacancy(record(),SOURCE,Pages({URL:'<h1>HR Intern</h1>'+FORM}),STAMP)
        self.assertEqual(result['inventory'],'current-employer-feed')
        self.assertEqual(result['method'],'same-vacancy-applicant-form')
    def test_matching_linked_application_and_wrong_requisition(self):
        apply='https://example.org/apply/123'
        pages={URL:'<h1>HR Intern</h1><a href="/apply/123">Apply</a>',apply:'<h1>HR Intern</h1>'+FORM}
        self.assertEqual(verify_vacancy(record(),SOURCE,Pages(pages),STAMP)['url'],apply)
        pages[apply]='<h1>Software Intern</h1>'+FORM
        with self.assertRaisesRegex(ValueError,'same vacancy'):verify_vacancy(record(),SOURCE,Pages(pages),STAMP)
    def test_soft_closed_and_expired(self):
        with self.assertRaises(ApplicationClosed):verify_vacancy(record(),SOURCE,Pages({URL:'<h1>HR Intern</h1>This job is no longer available'}),STAMP)
        with self.assertRaises(ApplicationClosed):verify_vacancy(record(),SOURCE,Pages({URL:'<h1>HR Intern</h1><script type="application/ld+json">{"@type":"JobPosting","title":"HR Intern","validThrough":"2026-11-05"}</script>'+FORM}),STAMP)
        self.assertTrue(verify_vacancy(record(valid_through='2026-11-05'),SOURCE,Pages({URL:'<h1>HR Intern</h1>'+FORM}),STAMP))
    def test_wrong_redirect_even_with_same_title(self):
        with self.assertRaisesRegex(ValueError,'redirected'):
            verify_vacancy(record(),SOURCE,Pages({URL:(('<h1>HR Intern</h1>'+FORM).encode(),200,'https://example.org/jobs/456')}),STAMP)
    def test_newsletter_and_disabled_application_do_not_verify(self):
        self.assertFalse(applicant_form(FORM.replace('id="application"','id="newsletter"').encode()))
        self.assertFalse(applicant_form(FORM.replace('type="submit"','type="submit" disabled').encode()))
    def test_blocked_is_distinct_from_incomplete_and_closed(self):
        for body,state,status in [(ValueError('robots.txt disallows job'),'blocked','unverified'),('<h1>HR Intern</h1>','incomplete','unverified'),('<h1>HR Intern</h1>This job is closed','closed','closed')]:
            with self.subTest(state=state),patch('collector.pipeline.collect',return_value=[record()]):
                result=process_source(SOURCE,Pages({URL:body}),STAMP)
                self.assertEqual(result['jobs'][0]['verification']['state'],state)
                self.assertEqual(result['jobs'][0]['status'],status)
    def test_later_enrichment_failure_keeps_earlier_valid_match(self):
        records=[record(),record(external_id='2',url='https://example.org/jobs/2')]
        with patch('collector.pipeline.collect',return_value=records),patch('collector.pipeline.enrich',side_effect=[records[0],ValueError('Detail unavailable')]):
            result=process_source(SOURCE,Pages({URL:'<h1>HR Intern</h1>'+FORM}),STAMP)
        self.assertEqual(len(result['jobs']),1);self.assertEqual(result['report']['status'],'partial')
    def test_redirect_destination_robots_checked_before_following(self):
        client=Client(0)
        with patch.object(client,'permitted',return_value=False) as permitted:
            with self.assertRaisesRegex(ValueError,'robots'):
                CheckedRedirect(client).redirect_request(Request(URL),None,302,'Found',{},'https://example.org/blocked')
        permitted.assert_called_once_with('https://example.org/blocked')

class HRAndLanguageEdges(unittest.TestCase):
    def test_specialisations_and_student_types(self):
        for title in ['Recruitment Intern','Talent Acquisition Intern','Learning & Development Intern','People Operations Intern','HR Analytics Intern','Compensation & Benefits Intern','Employee Relations Intern','Organizational Development Intern','Employer Branding Intern']:
            with self.subTest(title=title):self.assertIsNotNone(classify_role(title))
        self.assertEqual(classify_role('Working Student Talent Acquisition')['internship_type'],'working-student')
        for title in ['HR Manager','Graduate Programme HR','Management Trainee HR','HR internship opportunities','HR Talent Community','Benefits Marketing Intern']:
            with self.subTest(title=title):self.assertIsNone(classify_role(title))
    def test_explicit_english_is_not_english_alone(self):
        text='Fluent in English and Dutch.'
        summary=language_summary(text)
        self.assertEqual(summary['required_languages'],['en','nl'])
        self.assertEqual(summary['english_support'],'documented');self.assertEqual(summary['english_sufficiency'],'unknown')
        self.assertEqual(language_summary('English is the only required language. We work in English.')['english_sufficiency'],'documented')
    def test_scoped_negation_and_preferences(self):
        langs=workplace_languages('Fluent in English, Dutch is not required.')
        self.assertEqual([l['code'] for l in langs],['en'])
        langs=workplace_languages('Fluent in English and preferably Dutch.')
        self.assertEqual({l['code']:l['requirement'] for l in langs},{'en':'required-or-working','nl':'preferred'})
    def test_multilingual_ads_are_not_filtered_by_language(self):
        for title,text in [('Stage ressources humaines','Vous parlez couramment français et anglais.'),('Praktikum Personalentwicklung','Sehr gute Deutschkenntnisse und fließend Englisch.'),('Stage personeelsadministratie','Je spreekt vloeiend Nederlands.')]:
            with self.subTest(title=title):self.assertIsNotNone(classify_role(title,text))
        self.assertEqual(language_summary('The intern will join our team and learn with us.')['requirements_status'],'unknown')

class ReviewRegressions(unittest.TestCase):
    def test_accented_french_closure(self):
        with self.assertRaises(ApplicationClosed):
            verify_vacancy(record(),SOURCE,Pages({URL:'<h1>HR Intern</h1><p>Cette offre est expirée.</p>'+FORM}),STAMP)
    def test_conflicting_structured_application_id(self):
        import json
        def page(identifier):return '<h1>HR Intern</h1><script type="application/ld+json">'+json.dumps({'@type':'JobPosting','title':'HR Intern','identifier':{'value':identifier}})+'</script>'
        apply=URL+'/apply'
        pages={URL:page('123')+'<a href="'+apply+'">Apply</a>',apply:page('456')+FORM}
        with self.assertRaisesRegex(ValueError,'requisition differs'):
            verify_vacancy(record(),SOURCE,Pages(pages),STAMP)
    def test_preferred_list_is_not_mandatory(self):
        for statement in ['Preferred languages: English and Dutch.','Preferred languages are English and Dutch.']:
            summary=language_summary(statement)
            self.assertEqual(summary['required_languages'],[]);self.assertEqual(summary['english_support'],'unknown')
    def test_vacancy_path_application_child_without_form_title(self):
        apply=URL+'/apply'
        result=verify_vacancy(record(),SOURCE,Pages({URL:'<h1>HR Intern</h1><a href="'+apply+'">Apply</a>',apply:'<h1>Application</h1>'+FORM}),STAMP)
        self.assertEqual(result['vacancy_match'],'vacancy-path-application-child')
