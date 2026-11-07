import unittest
from collector.applications import checked_document, ApplicationClosed, verify_application
from unittest.mock import patch
from collector.verification import verify_vacancy

class PageClient:
    def __init__(self, body): self.body=body
    def request(self,url): return self.body.encode(),200,url

class UtrechtVacancyTests(unittest.TestCase):
    def test_expired_attrax_vacancy_is_not_verified(self):
        # Real Sopra Steria expiry marker, despite a retained full description.
        url='https://example.org/job/stage-hr-jid-9153'
        body='<h1>Stage HR</h1><div class="attrax-expired-vacancy-message"><h2>This vacancy has now expired. <a href="/jobs">See all jobs</a></h2></div><p>HR internship in Nieuwegein</p>'
        with self.assertRaises(ApplicationClosed):checked_document(url,{'allowed_hosts':['example.org']},PageClient(body))
        with self.assertRaises(ApplicationClosed):checked_document(url,{'allowed_hosts':['example.org']},PageClient('<h1>Vacature niet beschikbaar</h1>'))

    def test_same_vacancy_recruitee_form_needs_live_applicant_fields(self):
        url='https://example.org/o/hr-stagiaire'
        body='<h1>HR Stagiair(e)</h1><form id="offer-application-form"><input name="candidate.name"><input name="candidate.email" type="email"><input name="candidate.cv" type="file"><button type="submit">Versturen</button></form>'
        record={'url':url,'title':'HR Stagiair(e)','external_id':'2068985','inventory_evidence':'current-employer-feed'}
        source={'allowed_hosts':['example.org']}
        proof=verify_vacancy(record,source,PageClient(body),'2026-11-07T12:00:00+00:00')
        self.assertEqual(proof['method'],'same-vacancy-applicant-form')
        with self.assertRaises(ValueError):verify_vacancy(record,source,PageClient(body.replace('<button type="submit">','<button type="button">')),'2026-11-07T12:00:00+00:00')

    def test_watson_rendered_form_requires_title_and_requisition(self):
        url='https://example.org/banen/stage/46386869952'
        target='https://example.org/vacatures-solliciteer?title=Stage%20HR&req=281438'
        vacancy='<h1>Stage HR</h1><a href="'+target+'">Solliciteer direct</a>'
        application='<h1>Sollicitatie vacature</h1><p>Je solliciteert op de functie Stage HR</p><form id="watson-apply-form"><input name="ReqId" value="req281438"><input name="FirstName"><input name="LastName"><input name="Email"><input name="Resume"><button type="submit">Verstuur sollicitatie</button></form>'
        record={'url':url,'title':'Stage HR','posting_identifier':'req281438'}
        source={'allowed_hosts':['example.org'],'application_check':'watson-rendered'}
        with patch('collector.rendering.render_pages',return_value=([(target,application.encode())],True)):
            self.assertEqual(verify_application(record,source,PageClient(vacancy))['method'],'rendered-watson-same-requisition-form')
        for invalid in [application.replace('req281438','req999'),application.replace('functie Stage HR','functie Other role'),application.replace('name="Email"','name="Other"'),application.replace('type="submit"','type="button"'),application+'<p>This vacancy has now expired.</p>']:
            with patch('collector.rendering.render_pages',return_value=([(target,invalid.encode())],True)):
                with self.assertRaises(ValueError):verify_application(record,source,PageClient(vacancy))

    def test_reviewed_non_h1_heading_requires_source_opt_in_and_live_title(self):
        from collector.employer_pages import page_record
        body='<article><h2 class="vacancy-title"><span>Meewerkstage HR</span></h2><div>Nieuwegein / Netherlands</div><p>'+('HR stage descriptions. '*12)+'</p><p>Reageer dan snel en stuur je motivatie en CV naar <a href="mailto:lea.ruijsdam@dominos.nl">lea.ruijsdam@dominos.nl</a>.</p></article>'
        source={'allowed_hosts':['example.org'],'page_format':'reviewed-visible','reviewed_title':{'tag':'h2','class':'vacancy-title'},'reviewed_workplaces':[{'pattern':r'Nieuwegein / Netherlands','city':'Nieuwegein','country':'NL'}],'application_check':'official-email','application_email':'lea.ruijsdam@dominos.nl'}
        raw={'url':'https://example.org/hoofdkantoor/meewerkstage-hr'}
        record=page_record(raw,source,PageClient(body))
        self.assertEqual(record['title'],'Meewerkstage HR')
        self.assertEqual(verify_vacancy(record,source,PageClient(body),'2026-11-07T12:00:00+00:00')['method'],'official-vacancy-email-instructions')
        for invalid in [body.replace('vacancy-title','another-title'),body.replace('Meewerkstage HR','Other vacancy'),body.replace('</article>','<h2 class="vacancy-title">Meewerkstage HR</h2></article>'),body.replace('Nieuwegein','Rotterdam')]:
            with self.assertRaises(ValueError):
                changed=page_record(raw,source,PageClient(invalid))
                verify_vacancy(dict(changed,title='Meewerkstage HR'),source,PageClient(invalid),'2026-11-07T12:00:00+00:00')
        with self.assertRaises(ValueError):page_record(raw,dict(source,reviewed_title=None),PageClient(body))

if __name__=='__main__':unittest.main()
