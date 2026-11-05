import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from collector.daily import provision,shard_for,merge,employer_report
from collector.pipeline import read,ROOT,process_source,now
from collector.universal import Document,job_from_json,job_from_visible,Crawler,Inventory
from collector.runtime import PageCache,CollectionBudgetExceeded

class FakeClient:
 def __init__(self,pages):self.pages=pages;self.calls=[]
 def check(self):pass
 def request(self,url,**kw):
  self.calls.append(url)
  if kw.get('method')=='HEAD':return b'',200,url
  return self.pages[url].encode(),200,url

def source():return dict(id='auto-example',company_id='example',employer='Example',adapter='universal-employer',allowed_hosts=['example.org'],start_urls=['https://example.org'],no_browser=True,max_pages=10)
def posting(**extra):
 return dict({'@type':'JobPosting','title':'HR Intern','description':'Six month HR internship. Fluent in English.','jobLocation':{'address':{'addressLocality':'UnknownCity','addressCountry':'NL'}}},**extra)

class AllEmployerTests(unittest.TestCase):
 def test_all_real_employers_have_exactly_one_active_collector_and_assignment_is_idempotent(self):
  c,s=provision(read(ROOT/'data/companies.json',[]),read(ROOT/'data/sources.json',[]));self.assertGreaterEqual(len(c),842)
  enabled={x['id'] for x in s if x.get('enabled')}
  self.assertTrue(all(len(enabled.intersection(x['source_ids']))==1 for x in c))
  self.assertEqual(provision(c,s),(c,s))
  assigned=[sid for i in range(8) for sid in enabled if shard_for(sid,8)==i]
  self.assertEqual(len(assigned),len(enabled));self.assertEqual(set(assigned),enabled)
 def test_missing_shard_cannot_overwrite_catalog(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);(out/'catalog.json').write_text('prior catalog')
   with patch('collector.daily.provision_files',return_value=([],[])):
    with self.assertRaises(ValueError):merge(out,8,out)
   self.assertEqual((out/'catalog.json').read_text(),'prior catalog')
 def test_homepage_200_is_not_successful_empty_inventory(self):
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   rows=Crawler(source(),FakeClient({'https://example.org':'<main><h1>Example</h1><p>Our company</p></main>'})).run()
  self.assertFalse(rows.stats['complete']);self.assertNotEqual(rows.stats['status'],'ok');self.assertFalse(rows.stats['explicit_empty'])
 def test_follows_observed_external_career_link_and_reads_opaque_job_id(self):
  pages={'https://example.org':'<a href="https://work.example.net/careers">Careers</a>','https://work.example.net/careers':'<a href="/jobs/12345">Read more</a>','https://work.example.net/jobs/12345':'<script type="application/ld+json">'+json.dumps(posting())+'</script>'}
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   rows=Crawler(source(),FakeClient(pages)).run()
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['countries'],['NL']);self.assertIn('work.example.net',rows.stats['allowed_hosts'])
  self.assertFalse(rows.stats['complete'])
 def test_partial_extraction_publishes_matches_but_never_closes_absent_jobs(self):
  s=source();r=job_from_json(posting(),'https://example.org/jobs/1',s)
  rows=Inventory([r],dict(status='partial',complete=False,allowed_hosts=['example.org']))
  with patch('collector.pipeline.collect',return_value=rows):part=process_source(s,FakeClient({}),now())
  self.assertEqual(len(part['jobs']),1);self.assertEqual(part['closure_eligible'],[]);self.assertEqual(part['report']['status'],'partial')
 def test_expired_posting_and_permanent_role_not_promoted(self):
  self.assertIsNone(job_from_json(posting(validThrough='2020-01-01'),'https://example.org/jobs/1',source()))
  d=Document(b'<main><h1>HR Manager</h1><p>Manage our internship programme.</p></main>','https://example.org/jobs/1')
  self.assertIsNone(job_from_visible(d,source()))
 def test_visible_geography_never_uses_headquarters_footer(self):
  d=Document(b'<main><h1>HR Intern</h1><p>HR internship supporting recruitment.</p></main><footer><div class="location">Paris, France</div></footer>','https://example.org/jobs/1')
  r=job_from_visible(d,source());self.assertEqual(r['location'],'');self.assertTrue(r['geography_unresolved'])
 def test_labelled_location_and_multilingual_content(self):
  d=Document(b'<main><h1>HR Intern</h1><p class="job-location">Amsterdam, Netherlands</p><p>Fluent in English.</p></main>','https://example.org/jobs/1')
  r=job_from_visible(d,source());self.assertIn('Amsterdam',r['location']);self.assertFalse(r['geography_unresolved'])
 def test_budget_interrupt_preserves_current_url_for_next_run(self):
  class C(FakeClient):
   def request(self,url,**kw):raise CollectionBudgetExceeded('time limit')
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   rows=Crawler(source(),C({})).run();state=PageCache(source()['id']).state()
  self.assertEqual(state['pending'][0]['url'],'https://example.org');self.assertEqual(rows.stats['pending_urls'],1)
 def test_cache_expires_and_rejects_changed_lastmod(self):
  with tempfile.TemporaryDirectory() as d:
   c=PageCache('example',d);c.put('https://example.org/jobs/1',{'title':'HR Intern'},lastmod='a')
   self.assertEqual(c.get('https://example.org/jobs/1',lastmod='a')['title'],'HR Intern');self.assertIsNone(c.get('https://example.org/jobs/1',lastmod='b'));self.assertIsNone(c.get('https://example.org/jobs/1',max_age_hours=-1))
 def test_report_distinguishes_configured_attempted_and_actual_extraction(self):
  companies=[dict(id='a',name='A',source_ids=['a'],target_countries=['IT']),dict(id='b',name='B',source_ids=['b'],target_countries=['IT'])];sources=[dict(id='a',enabled=True),dict(id='b',enabled=True)]
  parts=[dict(report=dict(id='a',status='partial',records_inspected=3,checked_at=now(),matching=1))]
  r=employer_report(companies,sources,parts,now());self.assertEqual(r['summary']['configured'],2);self.assertEqual(r['summary']['attempted'],1);self.assertEqual(r['summary']['not-attempted'],1);self.assertEqual(r['summary']['partial'],1)
