import unittest,json
from collector.amazon import search_records
from collector.adapters import Client
from unittest.mock import patch

def source():return dict(id='amazon',employer='Amazon',allowed_hosts=['www.amazon.jobs','amazon.jobs'],search_urls=['https://www.amazon.jobs/de/search?base_query=human+resources+intern'])
def job(i,locations=None):return dict(id_icims=str(i),title='HR Intern',description='Internship. Fluent in English.',basic_qualifications='Learning agreement with university.',job_path='/en/jobs/'+str(i)+'/hr-intern',locations=locations or [json.dumps(dict(countryIso2a='CZ',city='Kojetin'))],company_name='Amazon Europe',posted_date='September 28, 2026')
def page(rows,total,start=0):return dict(jobs=rows,hits=total,job_posting_search_request=json.dumps(dict(jobPostingSearchRequest=dict(start=start))))
class FakeClient:
 def __init__(self,pages):self.pages=iter(pages);self.calls=[]
 def json(self,u):self.calls.append(u);return next(self.pages)
class AmazonTests(unittest.TestCase):
 def test_all_pages_and_official_countries(self):
  c=FakeClient([page([job(1)],2),page([job(2)],2,1)]);rows=search_records(source(),c)
  self.assertEqual(len(rows),2);self.assertEqual(rows[0]['countries'],['CZ']);self.assertIn('offset=1',c.calls[1]);self.assertIn('Learning agreement',rows[0]['text'])
 def test_multi_country_location_evidence_is_preserved(self):
  c=FakeClient([page([job(1,[dict(countryIso2a='DE',city='Berlin'),dict(countryIso2a='FR',city='Paris')])],1)])
  self.assertEqual(search_records(source(),c)[0]['countries'],['DE','FR'])
 def test_ignored_offset_never_claims_complete(self):
  with self.assertRaises(ValueError):search_records(source(),FakeClient([page([job(1)],2),page([job(2)],2,0)]))
 def test_repeated_or_changed_inventory_is_quarantined(self):
  for pages in [[page([job(1)],2),page([job(1)],2,1)],[page([job(1)],2),page([job(2)],3,1)]]:
   with self.assertRaises(ValueError):search_records(source(),FakeClient(pages))
 def test_parseable_robots_denials_still_apply_amid_invalid_lines(self):
  c=Client(delay=0);body=b'<!doctype html>\nUser-agent: *\nDisallow: /jobs\n<html>Invalid extra text</html>'
  with patch.object(c,'request',return_value=(body,200,'https://x/robots.txt')):self.assertFalse(c.permitted('https://x/jobs'))
 def test_robots_access_challenges_still_stop_collection(self):
  c=Client(delay=0)
  with patch.object(c,'request',return_value=(b'<html><title>Just a moment</title>Verify you are human</html>',200,'https://x/robots.txt')):
   with self.assertRaises(ValueError):c.permitted('https://x/jobs')

class PublicPageJSONTests(unittest.TestCase):
 def test_public_smartrecruiters_job_is_extracted_and_closed_applications_are_rejected(self):
  from collector.public_json import smartrecruiters_job
  data=dict(jobTitle='HR Internship',isApplyAvailable=True,jobAdLocation='Milan, Italy',employmentType='Intern',uuid='published-id',applyUrl='https://jobs.smartrecruiters.com/Example/123-hr-internship',content={'sections':{'jobDescription':{'text':'Six-month HR internship.'},'companyDescription':{'text':'Generic company boilerplate'}}})
  s=dict(id='example',employer='Example');url='https://jobs.smartrecruiters.com/Example/123'
  result=smartrecruiters_job(data,url,s);self.assertEqual(result['records'][0]['countries'],['IT']);self.assertNotIn('boilerplate',result['records'][0]['text'])
  result=smartrecruiters_job(dict(data,isApplyAvailable=False),url,s);self.assertEqual(result['records'],[]);self.assertEqual(result['closed_urls'],[url])
 def test_unrelated_json_is_not_a_job_posting(self):
  from collector.public_json import smartrecruiters_job
  self.assertIsNone(smartrecruiters_job({'title':'HR Intern'},'https://example.org/api',{}))
 def test_amazon_accepts_numeric_string_offset_published_by_the_website(self):
  p=page([job(1)],1);p['job_posting_search_request']=json.dumps({'jobPostingSearchRequest':{'start':'0'}})
  self.assertEqual(len(search_records(source(),FakeClient([p]))),1)

class ApplicationRequirementsTests(unittest.TestCase):
 def test_university_learning_agreement_is_visible_to_applicants(self):
  from collector.classify import extract_metadata
  evidence='Mandatory to be able to sign a learning agreement with the university.'
  self.assertEqual(extract_metadata(evidence)['enrollment'],evidence)
 def test_published_onsite_location_type_is_preserved(self):
  p=page([job(1,[dict(countryIso2a='DE',city='Berlin',type='ONSITE')])],1)
  self.assertEqual(search_records(source(),FakeClient([p]))[0]['work_mode'],'on-site')
