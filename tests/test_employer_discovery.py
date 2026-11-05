import csv,io,json
from datetime import datetime,timezone
from pathlib import Path
import unittest
from unittest.mock import patch
from collector.employer_pages import sitemap_records,page_record,PageParser
from collector.company_registry import validate_registry,discover_channels,coverage_report,discovery_queue,region_codes_for_job
from collector.classify import classify_role,workplace_languages
from collector.adapters import Client
from collector.pipeline import reconcile
from scripts.import_geography import convert

class FakeClient:
    def __init__(self,responses):self.responses=responses;self.calls=[]
    def request(self,url,**kwargs):
        self.calls.append(url);return self.responses[url].encode(),200,url

def source():
    return dict(id='employer-example',employer='Example',allowed_hosts=['careers.example.com'],sitemaps=['https://careers.example.com/sitemap.xml'],job_url_pattern=r'/jobs/')

class EmployerPageTests(unittest.TestCase):
    def test_inventory_all_jobs_before_triage(self):
        s=source();url=s['sitemaps'][0]
        c=FakeClient({url:'<urlset><url><loc>https://careers.example.com/jobs/hr-intern</loc></url><url><loc>https://careers.example.com/jobs/software-engineer</loc></url></urlset>'})
        rows=sitemap_records(s,c);self.assertEqual(len(rows),2);self.assertTrue(all(r['needs_page'] for r in rows))

    def test_nested_sitemap_and_duplicate_urls(self):
        s=source();c=FakeClient({s['sitemaps'][0]:'<sitemapindex><sitemap><loc>https://careers.example.com/child.xml</loc></sitemap></sitemapindex>','https://careers.example.com/child.xml':'<urlset><url><loc>https://careers.example.com/jobs/hr-intern</loc></url><url><loc>https://careers.example.com/jobs/hr-intern</loc></url></urlset>'})
        self.assertEqual(len(sitemap_records(s,c)),1)

    def test_unapproved_sitemap_host_rejected_before_fetch(self):
        s=source();c=FakeClient({s['sitemaps'][0]:'<sitemapindex><sitemap><loc>https://localhost/secrets.xml</loc></sitemap></sitemapindex>'})
        with self.assertRaises(ValueError):sitemap_records(s,c)
        self.assertEqual(len(c.calls),1)

    def test_sitemap_limits_are_failure_not_truncation(self):
        s=source();s['max_job_urls']=1;c=FakeClient({s['sitemaps'][0]:'<urlset><url><loc>https://careers.example.com/jobs/a</loc></url><url><loc>https://careers.example.com/jobs/b</loc></url></urlset>'})
        with self.assertRaises(ValueError):sitemap_records(s,c)

    def test_jsonld_job_and_expiry(self):
        s=source();url='https://careers.example.com/jobs/hr-intern';record={'url':url}
        data={'@graph':[{'@type':'JobPosting','title':'HR Internship','description':'Fluent in English.','hiringOrganization':{'name':'Example'},'jobLocation':{'address':{'addressLocality':'Amsterdam','addressCountry':'NL'}},'datePosted':'2026-11-01','validThrough':'2026-11-30'}]}
        c=FakeClient({url:'<script type="application/ld+json">'+json.dumps(data)+'</script>'})
        result=page_record(record,s,c,datetime(2026,11,5,tzinfo=timezone.utc));self.assertEqual(result['country'],'NL');self.assertEqual(result['apply_url'],url)
        with self.assertRaises(ValueError):page_record(record,s,c,datetime(2026,12,1,tzinfo=timezone.utc))

    def test_slug_cannot_override_actual_role(self):
        s=source();url='https://careers.example.com/jobs/hr-intern'
        data={'@type':'JobPosting','title':'Software Engineer','description':'A permanent role.'}
        result=page_record({'url':url},s,FakeClient({url:'<script type="application/ld+json">'+json.dumps(data)+'</script>'}))
        self.assertIsNone(classify_role(result['title'],result['text']))

    def test_danone_reads_matching_fragment_only(self):
        s=source();s['page_format']='danone';url='https://careers.example.com/jobs/hr-intern.html'
        body='<article data-cmp-contentfragment-model="x/danone-job-model" key="other" title="Wrong" description="Not the job"></article><article data-cmp-contentfragment-model="x/danone-job-model" key="hr-intern" title="HR Intern" description="Je spreekt vloeiend Engels." country="Netherlands" city="Utrecht" locale="nl_NL" recruiteremail="private@example.com"></article>'
        result=page_record({'url':url},s,FakeClient({url:body}));self.assertEqual(result['title'],'HR Intern');self.assertEqual(result['language'],'nl_NL');self.assertNotIn('recruiteremail',result)

    def test_html_robots_is_not_treated_as_permission(self):
        c=Client(delay=0)
        with patch.object(c,'request',return_value=(b'<!doctype html><html>Home</html>',200,'https://x/robots.txt')):
            with self.assertRaises(ValueError):c.permitted('https://x/jobs')

    def test_procurement_sourcing_is_excluded(self):
        self.assertIsNone(classify_role('INTERNSHIP - Global Feed Sustainable Sourcing'))
        self.assertIsNone(classify_role('Sourcing Intern - Procurement'))
        self.assertIsNotNone(classify_role('Talent Sourcing Intern'))
        self.assertIsNotNone(classify_role('Intern - Manufacturing People Partnering'))

    def test_workplace_communication_and_presentation(self):
        self.assertEqual(workplace_languages('Excellent communication and presentation skills in English.')[0]['code'],'en')

class RegistryTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.g=json.loads((root/'data/geography.json').read_text());self.c=json.loads((root/'data/companies.json').read_text());self.s=json.loads((root/'data/sources.json').read_text())

    def test_actual_geography_is_complete_and_hierarchical(self):
        self.assertEqual(len({u['country'] for u in self.g['units']}),27)
        self.assertEqual(sum(u['level']==2 and u['country']=='NL' for u in self.g['units']),12)
        codes={u['code'] for u in self.g['units']}
        self.assertTrue(all(not u['parent'] or u['parent'] in codes for u in self.g['units']))

    def test_registry_valid_and_all_dutch_provinces_have_evidence(self):
        self.assertTrue(validate_registry(self.c,self.g,self.s))
        located={p['region_code'] for c in self.c for p in c['workplaces'] if p['country']=='NL'}
        provinces={u['code'] for u in self.g['units'] if u['country']=='NL' and u['level']==2}
        self.assertTrue(provinces<=located)

    def test_office_presence_does_not_create_fake_jobs(self):
        report=coverage_report(self.c,self.g,self.s,[],'2026-11-05')
        self.assertEqual(sum(r['open_listings'] or 0 for r in report['regions']),0)
        self.assertTrue(any(r['status']=='not-researched' for r in report['regions']))

    def test_regional_mapping_requires_city_and_employer(self):
        base={'employer':'Danone','city':'Utrecht','countries':['NL']}
        self.assertIn('NL35',region_codes_for_job(base,self.c))
        self.assertEqual(region_codes_for_job(dict(base,city='Remote'),self.c),[])
        self.assertEqual(region_codes_for_job(dict(base,employer='Unrelated'),self.c),[])

    def test_queue_prioritises_netherlands_and_marks_targets(self):
        report=coverage_report(self.c,self.g,self.s,[],'2026-11-05');queue=discovery_queue(self.g,report)
        self.assertEqual(queue[0]['country'],'NL');self.assertEqual(len({x['country'] for x in queue}),27)
        self.assertTrue(all(x['status']=='research-required' for x in queue))

    def test_career_page_proposes_ats_without_enabling(self):
        url='https://careers.example.com';c={'career_url':url}
        result=discover_channels(c,FakeClient({url:'<a href="https://jobs.lever.co/example/123">Apply</a>'}))
        self.assertEqual(result[0]['board'],'example');self.assertEqual(result[0]['status'],'requires-access-review')

    def test_unknown_location_codes_rejected(self):
        company=dict(self.c[0]);company['workplaces']=[{'country':'NL','region_code':'NLXX','location_confidence':'confirmed','evidence_url':'https://example.com'}]
        with self.assertRaises(ValueError):validate_registry([company],self.g,self.s)

if __name__=='__main__':unittest.main()
