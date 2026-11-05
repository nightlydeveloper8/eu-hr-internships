import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from collector.pipeline import run,read

class DeepCollectionTests(unittest.TestCase):
 def source(self):return dict(id='opaque',employer='Example',adapter='employer-sitemap',enabled=True,allowed_hosts=['example.org'])
 def raw(self,path):return dict(url='https://example.org/'+path,title=path,text='',employment='',needs_page=True)
 def detail(self,raw,title):
  return dict(raw,source_id='opaque',external_id=raw['url'],employer='Example',title=title,text='Fluent in English.',location='Amsterdam, Netherlands',country='NL',city='Amsterdam',apply_url=raw['url'],language=None,published_at=None,work_mode=None,needs_page=False)
 def reader(self,path,default):
  if path.name=='sources.json':return [self.source()]
  if path.name=='companies.json':return []
  return read(path,default)
 def run_with(self,output,records,enrichment):
  with patch('collector.pipeline.read',side_effect=self.reader),patch('collector.pipeline.collect',return_value=records),patch('collector.pipeline.enrich',side_effect=enrichment),patch('collector.pipeline.Client') as client:
   client.return_value.request.side_effect=lambda u,**kw:(b'',200,u)
   return run(output=output)
 def test_opaque_page_is_read_and_misleading_hr_slug_is_rejected(self):
  opaque=self.raw('jobs/12345');misleading=self.raw('jobs/hr-intern')
  def enrich(r,s,c):return self.detail(r,'HR Intern' if r is opaque else 'Software Engineer')
  with tempfile.TemporaryDirectory() as d:
   result,report=self.run_with(Path(d),[opaque,misleading],enrich)
  self.assertEqual(len(result['jobs']),1);self.assertTrue(result['jobs'][0]['url'].endswith('12345'))
  self.assertEqual(report['sources'][0]['records_inspected'],2)
 def test_partial_page_failure_keeps_previous_jobs_and_new_matches(self):
  old=self.raw('jobs/1');new=self.raw('jobs/2');broken=self.raw('jobs/3')
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)
   self.run_with(output,[old],lambda r,s,c:self.detail(r,'HR Intern'))
   def enrich(r,s,c):
    if r is broken:raise ValueError('Unsupported page layout')
    return self.detail(r,'HR Intern')
   result,report=self.run_with(output,[new,broken],enrich)
  self.assertEqual(len(result['jobs']),2);self.assertEqual(result['update_status'],'partial')
  self.assertEqual(report['sources'][0]['status'],'partial');self.assertEqual(report['sources'][0]['page_failures'],1)
if __name__=='__main__':unittest.main()

class StructuredCountryTests(unittest.TestCase):
 def test_explicit_countries_survive_unrecognised_city_names(self):
  from collector.employer_pages import page_record
  from collector.pipeline import record_countries
  data={'@type':'JobPosting','title':'HR Intern','description':'HR internship','jobLocation':[{'address':{'addressLocality':'UnknownTown1','addressCountry':'DE'}},{'address':{'addressLocality':'UnknownTown2','addressCountry':'FR'}}]}
  class C:
   def request(self,u):return ('<script type="application/ld+json">'+json.dumps(data)+'</script>').encode(),200,u
  r=page_record({'url':'https://example.org/job/1'},dict(employer='Example',allowed_hosts=['example.org']),C())
  self.assertEqual(record_countries(r),['DE','FR'])
