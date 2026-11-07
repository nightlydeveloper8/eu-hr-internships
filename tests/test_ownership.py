import copy,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
from collector.universal import Crawler,job_from_json,job_from_visible,Document,Inventory
from collector.ownership import apply_ownership_reviews
from collector.pipeline import ROOT,process_source,finalize,now,read
from collector.runtime import PageCache
from tests.test_all_employers import source,posting,FakeClient

class OwnershipTests(unittest.TestCase):
 def test_referral_to_external_ats_does_not_inherit_university_employer(self):
  s=source();s['employer']='University'
  pages={'https://example.org':'<a href="https://third.recruitee.com/o/hr-intern">HR internship vacancy</a>',
   'https://third.recruitee.com/o/hr-intern':'<main><h1>HR Intern</h1><p class="location">Eindhoven, NL</p></main>'}
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}),patch('collector.adapters.collect',side_effect=AssertionError('Must not read unowned tenant feed')):
   rows=Crawler(s,FakeClient(pages)).run()
  self.assertEqual(list(rows),[])
 def test_external_career_page_needs_explicit_hiring_organization(self):
  s=source();url='https://work.example.net/jobs/1'
  self.assertIsNone(job_from_json(posting(),url,s))
  self.assertIsNone(job_from_json(posting(hiringOrganization={'name':'Other Company'}),url,s))
  self.assertIsNotNone(job_from_json(posting(hiringOrganization={'name':'Example'}),url,s))
  self.assertIsNone(job_from_visible(Document(b'<h1>HR Intern</h1>',url),s))
 def test_third_party_structured_posting_on_own_portal_is_not_employer_inventory(self):
  self.assertIsNone(job_from_json(posting(hiringOrganization={'name':'Other'}),'https://example.org/jobs/1',source()))
 def test_legacy_frontier_cannot_restore_third_party_ownership(self):
  s=source();s['ownership_scope']='reviewed-hosts'
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   PageCache(s['id']).save_state({'allowed_hosts':['third.recruitee.com'],'preferred_career_url':'https://third.recruitee.com','pending':[{'url':'https://third.recruitee.com/o/hr','job':True}]})
   crawler=Crawler(s,FakeClient({'https://example.org':'<p>No career inventory</p>'}));rows=crawler.run()
   self.assertNotIn('third.recruitee.com',rows.stats['allowed_hosts'])
   self.assertFalse(crawler.allow('https://third.recruitee.com/o/hr',observed=True))
 def test_process_source_rejects_poisoned_cached_or_feed_row(self):
  s=source();r=dict(source_id=s['id'],employer='Example',url='https://third.recruitee.com/o/hr')
  with patch('collector.pipeline.collect',return_value=Inventory([r],{'allowed_hosts':['third.recruitee.com']})):
   part=process_source(s,FakeClient({}),now())
  self.assertEqual(part['jobs'],[])
 def test_review_survives_daily_merge_and_preserves_catalog_id_links_and_verification(self):
  catalog=read(ROOT/'data/catalog.json',{});target=next(j for j in catalog['jobs'] if j['id']=='70d297b765fc2696c836')
  reviews=read(ROOT/'data/ownership-reviews.json',[])
  wrong=dict(target,employer='Tilburg University',source_name='Tilburg University',source_id='auto-tilburg-university')
  fresh=dict(target,id='new-source-generated-id',first_discovered_at=now(),last_seen_at=now())
  parts=[{'report':{'id':'auto-ennatuurlijk','status':'ok','checked_at':now(),'records_inspected':1},'jobs':[fresh],'closure_eligible':[]}]
  with tempfile.TemporaryDirectory() as d:
   result,_=finalize(read(ROOT/'data/sources.json',[]),[],dict(catalog,jobs=[wrong]),{},parts,now(),Path(d))
  self.assertEqual(len(result['jobs']),1);job=result['jobs'][0]
  self.assertEqual(job['id'],target['id']);self.assertEqual(job['employer'],'Ennatuurlijk');self.assertEqual(job['source_id'],'auto-ennatuurlijk')
  self.assertEqual(job['url'],target['url']);self.assertEqual(job['apply_url'],target['apply_url'])
  self.assertEqual(job['application_verification'],target['application_verification'])
  self.assertEqual(apply_ownership_reviews([job],reviews),[job])
 def test_review_is_individual_not_bulk_transfer(self):
  reviews=read(ROOT/'data/ownership-reviews.json',[])
  other={'id':'other','source_id':'auto-tilburg-university','url':'https://other.recruitee.com/o/hr'}
  self.assertEqual(apply_ownership_reviews([other],reviews),[other])

 def test_referral_and_staffing_pages_require_individual_employer_evidence_even_on_own_host(self):
  s=dict(source(),require_employer_identity=True);url='https://example.org/jobs/1'
  self.assertIsNone(job_from_json(posting(),url,s))
  self.assertIsNone(job_from_visible(Document(b'<h1>HR Intern</h1>',url),s))
  self.assertIsNotNone(job_from_json(posting(hiringOrganization={'name':'Example'}),url,s))
 def test_reviewed_external_ats_tenant_still_collects_valid_postings(self):
  s=source();s['allowed_hosts'].append('third.recruitee.com');s['start_urls']=['https://third.recruitee.com']
  offer=dict(id=1,status='published',title='HR Intern',description='HR internship',
   careers_url='https://third.recruitee.com/o/hr-intern',country_code='NL',city='Eindhoven')
  with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'COLLECTOR_CACHE_DIR':d}):
   rows=Crawler(s,FakeClient({'https://third.recruitee.com/api/offers':json.dumps({'offers':[offer]})})).run()
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['employer'],'Example')
