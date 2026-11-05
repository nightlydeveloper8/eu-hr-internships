import json,unittest
from collector.public_feeds import personio_records,recruitee_records
from collector.employer_pages import index_records
from collector.pipeline import record_countries
from collector.classify import country_codes,classify_role

class Client:
 def __init__(self,body):self.body=body.encode();self.calls=[]
 def request(self,url):self.calls.append(url);return self.body,200,url

class PublicFeedTests(unittest.TestCase):
 def source(self):return dict(id='example',employer='Example',feed_url='https://example.jobs.personio.de/xml',allowed_hosts=['example.jobs.personio.de'])
 def test_personio_metadata_and_documented_public_job_url(self):
  body='<workzag-jobs><position><id>42</id><name>Praktikum HR</name><office>Berlin</office><employmentType>intern</employmentType><jobDescriptions><jobDescription><name>Requirements</name><value>Fluent in English</value></jobDescription></jobDescriptions></position></workzag-jobs>'
  r=personio_records(self.source(),Client(body))[0]
  self.assertEqual(r['url'],'https://example.jobs.personio.de/job/42');self.assertEqual(r['location'],'Berlin');self.assertIsNone(r['published_at']);self.assertIn('Fluent',r['text'])
 def test_wrong_xml_root_or_doctype_is_failure(self):
  for body in ['<html/>','<!DOCTYPE x><workzag-jobs/>']:
   with self.assertRaises(ValueError):personio_records(self.source(),Client(body))
 def test_recruitee_published_null_fields_and_multi_country(self):
  source=self.source();source['feed_url']='https://example.jobs.personio.de/api/offers/'
  job=dict(id=42,status='published',title='HR Intern',careers_url='https://example.jobs.personio.de/o/hr',description=None,requirements=None,locations=[dict(city='UnknownTown',country_code='DE'),dict(city='OtherTown',country_code='FR')])
  rows=recruitee_records(source,Client(json.dumps({'offers':[job,dict(job,id=43,status='draft')]})))
  self.assertEqual(len(rows),1);self.assertEqual(record_countries(rows[0]),['DE','FR'])
 def test_recruitee_unapproved_posting_host_fails(self):
  body={'offers':[dict(id=1,status='published',careers_url='https://unreviewed.example/job')]}
  with self.assertRaises(ValueError):recruitee_records(self.source(),Client(json.dumps(body)))
 def test_index_real_labels_deduplicate_numeric_ids(self):
  source=dict(id='example',employer='Example',allowed_hosts=['example.org'],index_urls=['https://example.org/jobs'],job_url_pattern=r'^https://example.org/job/\d+/',job_id_pattern=r'/job/(\d+)/')
  body='<a href="/job/42/hr"><h3>HR Internship</h3></a><a href="/job/42/hr">Apply</a><a href="https://other.org/job/42/hr">HR Intern</a>'
  rows=index_records(source,Client(body));self.assertEqual(len(rows),1);self.assertEqual(rows[0]['title'],'HR Internship')
 def test_local_country_metadata_and_working_student_kind(self):
  self.assertEqual(country_codes('', 'Nederland'),['NL']);self.assertEqual(country_codes('deutschlandweit remote'),['DE'])
  self.assertEqual(classify_role('Werkstudierende Recruiting',employment='intern')['internship_type'],'working-student')
 def test_curated_job_title_wins_over_long_apply_button_label(self):
  source=dict(id='example',employer='Example',allowed_hosts=['example.org'],index_urls=['https://example.org/job/42/hr'],job_url_pattern=r'^https://example.org/job/\d+/',include_index_jobposting=True)
  body='<a href="  /students  ">Very long student navigation label</a><a href="/job/42/hr">Apply apply for this vacancy today</a><script type="application/ld+json">{"@type":"JobPosting","title":"HR Intern"}</script>'
  self.assertEqual(index_records(source,Client(body))[0]['title'],'HR Intern')
 def test_dutch_compound_internship_title(self):
  self.assertIsNotNone(classify_role('Meewerkstage HR'))
  self.assertIsNotNone(classify_role('Afstudeerstage HR'))
 def test_people_events_requires_explicit_hr_tasks(self):
  self.assertIsNone(classify_role('Praktikum People & Events','Customer trade show planning'))
  self.assertIsNotNone(classify_role('Praktikum People & Events','Interne Personalbetreuung'))
if __name__=='__main__':unittest.main()
