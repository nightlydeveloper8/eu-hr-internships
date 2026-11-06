from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from collector.pipeline import reconcile,deduplicate,run,allowed_url
from collector.adapters import collect,enrich,Client

def job(**kwargs):
    value=dict(id='abc',source_id='a',url='https://jobs.lever.co/a/1',first_discovered_at='2026-01-01T00:00:00+00:00',status='open')
    value.update(kwargs);return value

class PipelineTests(unittest.TestCase):
    def test_failed_source_preserves_record(self):
        old=job();self.assertEqual(reconcile([old],[],set(),'2026-01-02T00:00:00+00:00'),[old])

    def test_conservative_closure_and_daily_idempotency(self):
        rows=[job()]
        rows=reconcile(rows,[],{'a'},'2026-01-02T00:00:00+00:00');self.assertEqual(rows[0]['status'],'unverified')
        again=reconcile(rows,[],{'a'},'2026-01-02T12:00:00+00:00');self.assertEqual(again[0]['missing_count'],1)
        rows=reconcile(rows,[],{'a'},'2026-01-03T00:00:00+00:00');self.assertNotEqual(rows[0]['status'],'closed')
        rows=reconcile(rows,[],{'a'},'2026-01-04T00:00:00+00:00');self.assertEqual(rows[0]['status'],'closed')

    def test_reappearance_keeps_first_discovery(self):
        merged=reconcile([job(status='closed')],[job(first_discovered_at='2026-02-01T00:00:00+00:00')],{'a'},'2026-02-01T00:00:00+00:00')
        self.assertEqual(merged[0]['first_discovered_at'],'2026-01-01T00:00:00+00:00');self.assertEqual(merged[0]['status'],'open')

    def test_explicitly_closed_posting_stays_closed_when_absent(self):
        closed=job(status='closed',closure_reason='Official application unavailable')
        self.assertEqual(reconcile([closed],[],{'a'},'2026-01-02T00:00:00+00:00'),[closed])

    def test_tracking_duplicates_merge_but_distinct_postings_stay(self):
        self.assertEqual(len(deduplicate([job(),job(id='def',url='https://jobs.lever.co/a/1?utm_source=x')])),1)
        self.assertEqual(len(deduplicate([job(),job(id='def',url='https://jobs.lever.co/a/2')])),2)

    def test_shared_application_urls_merge_mirrors(self):
        rows=[job(apply_url='https://jobs.lever.co/a/1/apply'),job(id='def',url='https://careers.example.com/job',apply_url='https://jobs.lever.co/a/1/apply')]
        self.assertEqual(len(deduplicate(rows)),1)

    def test_shared_generic_apply_url_cannot_merge_distinct_official_ids(self):
        rows=[job(source_posting_id='1',apply_url='https://careers.example.com/apply'),
              job(id='def',source_posting_id='2',url='https://jobs.lever.co/a/2',apply_url='https://careers.example.com/apply')]
        self.assertEqual({j['source_posting_id'] for j in deduplicate(rows)},{'1','2'})

    def test_same_posting_id_still_merges_language_mirrors(self):
        rows=[job(source_posting_id='1'),
              job(id='def',source_posting_id='1',url='https://careers.example.com/fr/job/1')]
        self.assertEqual(len(deduplicate(rows)),1)

    def test_unapproved_url_rejected(self):
        with self.assertRaises(ValueError):allowed_url('https://evil.example/a',{'allowed_hosts':['jobs.lever.co']})

    def test_all_fail_does_not_advance_success_time(self):
        stamp='2026-01-01T00:00:00+00:00'
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'catalog.json').write_text(json.dumps({'jobs':[],'updated_at':stamp}))
            with patch('collector.pipeline.collect',side_effect=RuntimeError('network unavailable')):
                result,_=run(['greenhouse-adyen'],output=root)
            self.assertEqual(result['updated_at'],stamp);self.assertEqual(result['update_status'],'failed')

class FakeClient:
    def __init__(self,pages):self.pages=list(pages);self.calls=[]
    def json(self,url):self.calls.append(url);return self.pages.pop(0)

class AdapterTests(unittest.TestCase):
    def source(self,kind):return {'id':'test','adapter':kind,'board':'example','employer':'Example'}
    def test_greenhouse_complete_board(self):
        c=FakeClient([{'jobs':[{'id':1,'title':'HR Intern','location':{'name':'Amsterdam'},'content':'Fluent in English','absolute_url':'https://job-boards.greenhouse.io/example/jobs/1'}],'meta':{'total':1}}])
        result=collect(self.source('greenhouse'),c);self.assertEqual(result[0]['external_id'],'1');self.assertIn('content=true',c.calls[0])

    def test_incomplete_greenhouse_is_failure(self):
        with self.assertRaises(ValueError):collect(self.source('greenhouse'),FakeClient([{'jobs':[],'meta':{'total':5}}]))

    def test_lever_pagination_and_full_text(self):
        page=[{'id':str(i),'text':'Software Engineer','hostedUrl':f'https://jobs.lever.co/example/{i}','categories':{},'lists':[{'text':'Requirements','content':'English'}]} for i in range(100)]
        c=FakeClient([page,[]]);result=collect(self.source('lever'),c)
        self.assertEqual(len(result),100);self.assertIn('skip=100',c.calls[1]);self.assertIn('English',result[0]['text'])

    def test_lever_eu_region(self):
        c=FakeClient([[]]);source=self.source('lever');source['region']='eu';collect(source,c);self.assertIn('api.eu.lever.co',c.calls[0])

    def test_ashby_excludes_unlisted(self):
        c=FakeClient([{'jobs':[{'isListed':False},{'title':'HR Intern','jobUrl':'https://jobs.ashbyhq.com/example/uuid','isListed':True,'location':'Paris','descriptionPlain':'Fluent in French.','employmentType':'Intern'}]}])
        result=collect(self.source('ashby'),c);self.assertEqual(len(result),1);self.assertEqual(result[0]['external_id'],'uuid')

    def test_smartrecruiters_pagination(self):
        row={'id':'1','name':'HR Intern','location':{'city':'Amsterdam','country':'nl'}}
        c=FakeClient([{'content':[row],'totalFound':2},{'content':[dict(row,id='2')],'totalFound':2}])
        result=collect(self.source('smartrecruiters'),c);self.assertEqual(len(result),2);self.assertIn('offset=1',c.calls[1])

    def test_smartrecruiters_empty_incomplete_fails(self):
        with self.assertRaises(ValueError):collect(self.source('smartrecruiters'),FakeClient([{'content':[],'totalFound':1}]))

    def test_smartrecruiters_enrichment(self):
        c=FakeClient([{'active':True,'postingUrl':'https://jobs.smartrecruiters.com/Example/1','jobAd':{'sections':{'companyDescription':{'text':'Ignore company boilerplate'},'qualifications':{'text':'Fluent in English'}}}}])
        result=enrich({'external_id':'1','url':'https://jobs.smartrecruiters.com/Example/1'},self.source('smartrecruiters'),c)
        self.assertEqual(result['text'],'Fluent in English')

    def test_duplicate_ids_fail_snapshot(self):
        c=FakeClient([{'jobs':[{'id':1,'title':'HR Intern','absolute_url':'https://job-boards.greenhouse.io/e/1'}]*2,'meta':{'total':2}}])
        with self.assertRaises(ValueError):collect(self.source('greenhouse'),c)

    def test_robots_denial_stops_requests(self):
        client=Client(delay=0)
        with patch.object(client,'permitted',return_value=False),patch('collector.adapters.build_opener') as opened:
            with self.assertRaises(ValueError):client.json('https://api.example.com/jobs')
            opened.assert_not_called()

if __name__=='__main__':unittest.main()


class HostRateLimitTests(unittest.TestCase):
    def test_crawl_delay_does_not_leak_between_employers(self):
        c=Client(delay=.35)
        def robots(url,**kwargs):
            text='User-agent: *\nCrawl-delay: 2\n' if 'slow.example' in url else 'User-agent: *\nAllow: /\n'
            return text.encode(),200,url
        with patch.object(c,'request',side_effect=robots):
            self.assertTrue(c.permitted('https://slow.example/jobs'))
            self.assertTrue(c.permitted('https://fast.example/jobs'))
        self.assertEqual(c.host_delays['slow.example'],2)
        self.assertEqual(c.delay,.35)
        self.assertEqual(c.host_delays.get('fast.example',c.delay),.35)

class UnverifiedDuplicateTests(unittest.TestCase):
 def test_unverified_language_mirrors_do_not_block_the_entire_catalog(self):
  rows=[job(last_verified_at=None),job(id='def',last_verified_at=None,url='https://jobs.lever.co/a/1?utm_source=x')]
  self.assertEqual(len(deduplicate(rows)),1)
 def test_verified_copy_supersedes_unverified_without_losing_identity(self):
  a=job(last_verified_at=None);b=job(id='def',last_verified_at='2026-11-05T12:00:00+00:00')
  result=deduplicate([a,b]);self.assertEqual(result[0]['id'],'abc');self.assertEqual(result[0]['last_verified_at'],b['last_verified_at'])

class PublishedATSAliasTests(unittest.TestCase):
 def test_intervieweb_query_alias_and_language_routes_share_posting_id(self):
  a=job(source_id='despar',url='https://despar.intervieweb.it/jobs/hr-stage-11939/it',last_verified_at=None)
  b=job(id='def',source_id='despar',url='https://despar.intervieweb.it/app.php?module=annunci&l=hr-stage-11939&lang=de',last_verified_at=None)
  self.assertEqual(len(deduplicate([a,b])),1)

class EvidenceDedupTests(unittest.TestCase):
 def test_general_portal_without_posting_ids_does_not_merge(self):
  for sid in ['a','b']:
   rows=[job(url='https://example.org/jobs/1',apply_url='https://example.org/apply'),job(id='other',source_id=sid,url='https://example.org/jobs/2',apply_url='https://example.org/apply')]
   self.assertEqual(len(deduplicate(rows)),2)
 def test_recent_failed_or_closed_observation_supersedes_old_verification(self):
  for state,status in [('incomplete','unverified'),('closed','closed')]:
   old=job(last_seen_at='2026-11-05T12:00:00Z',last_verified_at='2026-11-05T12:00:00Z',verification={'state':'verified','checked_at':'2026-11-05T12:00:00Z'})
   new=job(id='new',last_seen_at='2026-11-06T12:00:00Z',last_verified_at=None,status=status,verification={'state':state,'checked_at':'2026-11-06T12:00:00Z'})
   merged=deduplicate([old,new])[0]
   self.assertEqual(merged['status'],status);self.assertEqual(merged['id'],old['id']);self.assertEqual(merged['last_verified_at'],old['last_verified_at'])
