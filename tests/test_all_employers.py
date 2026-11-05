import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from collector.daily import provision,shard_for,merge,employer_report
from collector.pipeline import read,ROOT,process_source,now
from collector.universal import Document,job_from_json,job_from_visible,Crawler,Inventory
from collector.runtime import PageCache,CollectionBudgetExceeded,BudgetClient

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

class BudgetDelayTests(unittest.TestCase):
 def test_long_host_delay_never_stalls_other_employers(self):
  c=BudgetClient(seconds=1)
  with patch('collector.runtime.time.sleep') as sleep:
   with self.assertRaises(CollectionBudgetExceeded):c.pause(300)
   sleep.assert_not_called()

class RenderingFallbackTests(unittest.TestCase):
 def test_complete_jsonld_is_read_without_unnecessary_browser(self):
  s=source();s['no_browser']=False
  body='<script type="application/ld+json">'+json.dumps(posting())+'</script>'
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}),patch('collector.rendering.render_pages',side_effect=RuntimeError('must not be called')) as browser:
   rows=Crawler(s,FakeClient({'https://example.org':body})).run()
  self.assertEqual(len(rows),1);browser.assert_not_called()

class QualityRegressionTests(unittest.TestCase):
 def test_praktijk_is_a_business_practice_and_praktijkstage_is_an_internship(self):
  from collector.classify import classify_role
  self.assertIsNone(classify_role('HR Adviseur | Internationale praktijk'))
  self.assertIsNotNone(classify_role('HR praktijkstage'))
 def test_dutch_internal_payroll_job_is_not_an_internship(self):
  from collector.classify import classify_role
  self.assertIsNone(classify_role('Payroll Specialist Intern','Jij coördineert salarisverwerking voor 1200 medewerkers. Vast contract.'))
  self.assertIsNotNone(classify_role('HR Intern','Jij bent student en zoekt een stage.'))
 def test_recruiter_advice_article_is_not_a_vacancy(self):
  d=Document(b'<main><h1>Recruiter Q&amp;A: Internships and Career Advice</h1><div class="location">Germany</div></main>','https://example.org/blogs/recruiter-interview')
  self.assertIsNone(job_from_visible(d,source()))
 def test_language_mirrors_merge_but_distinct_official_ids_remain(self):
  from collector.pipeline import deduplicate
  base=dict(id='a',source_id='loreal',employer='Loreal',first_discovered_at=now(),last_verified_at=now(),country='DE',countries=['DE'])
  a=dict(base,url='https://careers.loreal.com/en/job/hr-intern/3456/45385292416')
  b=dict(base,id='b',url='https://careers.loreal.com/fr/emploi/hr-intern/3456/45385292416')
  c=dict(base,id='c',url='https://careers.loreal.com/en/job/hr-intern/3456/45385292417')
  self.assertEqual(len(deduplicate([a,b,c])),2)
 def test_intervieweb_languages_and_published_tracking_links_merge(self):
  from collector.pipeline import deduplicate
  base=dict(id='a',source_id='despar',first_discovered_at=now(),last_verified_at=now(),country='IT',countries=['IT'])
  a=dict(base,url='https://despar.intervieweb.it/jobs/hr-stage-11939/it')
  b=dict(base,id='b',url='https://despar.intervieweb.it/jobs/hr-stage-11939/de?d=qrcode')
  self.assertEqual(len(deduplicate([a,b])),1)
 def test_reviewed_false_positive_cannot_reappear_from_previous_partial_catalog(self):
  from collector.pipeline import apply_listing_reviews
  jobs=[dict(url='https://example.org/jobs/1'),dict(url='https://example.org/jobs/2')]
  rows=apply_listing_reviews(jobs,[dict(url='https://example.org/jobs/1',decision='excluded')]);self.assertEqual(rows,[jobs[1]])
 def test_sitemap_discovers_opaque_postings_without_guessing_urls(self):
  from urllib.robotparser import RobotFileParser
  r=RobotFileParser();r.parse(['User-agent: *','Allow: /','Sitemap: https://example.org/jobs-map.xml'])
  pages={'https://example.org':'<h1>Example</h1>','https://example.org/jobs-map.xml':'<urlset><url><loc>https://example.org/jobs/9901</loc></url></urlset>','https://example.org/jobs/9901':'<script type="application/ld+json">'+json.dumps(posting())+'</script>'}
  client=FakeClient(pages);client.robots={'https://example.org':r}
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):rows=Crawler(source(),client).run()
  self.assertEqual(len(rows),1);self.assertIn('https://example.org/jobs/9901',client.calls)
 def test_known_hr_offers_are_revisited_before_discovery(self):
  s=source();s['known_job_urls']=['https://example.org/jobs/9901'];client=FakeClient({'https://example.org/jobs/9901':'<script type="application/ld+json">'+json.dumps(posting())+'</script>','https://example.org':'<h1>Example</h1>'})
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):rows=Crawler(s,client).run()
  self.assertEqual(client.calls[0],'https://example.org/jobs/9901');self.assertEqual(len(rows),1)

class CrawlFairnessTests(unittest.TestCase):
 def test_stale_cached_pages_rotate_instead_of_restarting_at_the_first_url(self):
  import os
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   c=Crawler(source(),FakeClient({}));old='https://example.org/jobs/2';new='https://example.org/jobs/1'
   c.cache.put(old,{});c.cache.put(new,{});os.utime(c.cache.path(old),(10,10));os.utime(c.cache.path(new),(20,20))
   self.assertEqual(sorted([(new,True,1),(old,True,1)],key=c.priority)[0][0],old)
 def test_job_details_precede_deep_company_navigation(self):
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   c=Crawler(source(),FakeClient({}));detail=('https://example.org/jobs/3',True,2);about=('https://example.org/careers/our-values',False,2)
   self.assertLess(c.priority(detail),c.priority(about))

class VisibleLocationTests(unittest.TestCase):
 def test_elementor_template_class_is_not_job_location(self):
  d=Document(b'<main class="elementor-location-single"><h1>HR Intern</h1><p>Work with our team in Amsterdam and other offices.</p></main>','https://example.org/jobs/1')
  self.assertEqual(job_from_visible(d,source())['location'],'')
 def test_published_map_marker_labels_only_its_compact_job_location(self):
  d=Document(b'<main><h1>HR Intern</h1><div class="elementor-icon-box-wrapper"><svg class="e-fas-map-marker-alt"></svg><div><span>Rotterdam</span></div></div><p>Other company text</p></main>','https://example.org/jobs/1')
  self.assertEqual(job_from_visible(d,source())['location'],'Rotterdam')

class ExtractionCacheVersionTests(unittest.TestCase):
 def test_extractor_change_does_not_reuse_old_normalized_content(self):
  with tempfile.TemporaryDirectory() as d:
   a=PageCache('example',d);a.put('https://example.org/jobs/1',{'location':'old template text'})
   b=PageCache('example',d,revision=2);self.assertIsNone(b.get('https://example.org/jobs/1'))
   b.put('https://example.org/jobs/1',{'location':'Rotterdam'});self.assertEqual(b.get('https://example.org/jobs/1')['location'],'Rotterdam')
