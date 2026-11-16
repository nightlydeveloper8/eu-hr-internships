"""Meaningful queue regressions: ownership, country scope and non-activation."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.build_eu27_expansion_queue import build, channel, EU27, ROOT
from scripts.probe_eu27_batch import probe, select


def lead(name='New Employer',url='https://new.recruitee.com/o/hr-intern',country='BE',**extra):
    return dict(name=name,country=country,url=url,title='HR Intern',source_ref='fixture-only',**extra)


class QueueTests(unittest.TestCase):
    def run_build(self,leads,companies=None,sources=None,jobs=None,probes=None):
        return build(companies or [],sources or [],dict(jobs=jobs or [],updated_at='2026-11-16'),[],
                     dict(employers=[]),dict(countries=[]),dict(observed_on='2026-11-15',search_queries=0,
                     page_open_attempts=0,leads=leads),'fixture-base',probes)

    def test_same_tenant_translations_are_one_channel_and_never_verified(self):
        leads=[lead(),lead(url='https://new.recruitee.com/l/fr/o/hr-intern?lang=fr')]
        before=copy.deepcopy(leads)
        q,b=self.run_build(leads)
        self.assertEqual(q['summary']['new_web_employers'],1)
        self.assertEqual(len(b['rows']),1)
        self.assertEqual(len(b['rows'][0]['hr_evidence']),2)
        self.assertFalse(b['rows'][0]['enabled_by_this_queue'])
        self.assertFalse(b['rows'][0]['country_coverage_verified'])
        self.assertEqual(b['new_live_verified'],0)
        self.assertFalse(b['adapter_proposals'][0]['enabled'])
        self.assertEqual(leads,before)

    def test_shared_tenant_names_are_not_merged_into_one_employer(self):
        q,b=self.run_build([lead(name='One Employer'),lead(name='Other Employer')])
        self.assertEqual(q['summary']['new_web_employers'],2)
        self.assertEqual(b['rows'],[])
        self.assertTrue(all(a['excluded_from_first_batch'] for a in q['actions']))

    def test_registry_source_mapping_works_without_legacy_company_id(self):
        c=dict(id='old',name='Existing',source_ids=['dedicated'],target_countries=['BE'],career_url='https://old.recruitee.com')
        s=dict(id='dedicated',adapter='recruitee',career_url=c['career_url'],enabled=True,allowed_hosts=['old.recruitee.com'])
        j=dict(id='job',source_id='dedicated',internship_type='internship',url='https://old.recruitee.com/o/hr',
               title='HR Intern',countries=['BE'],status='unverified',verification=dict(reason='Missing form'))
        q,b=self.run_build([],companies=[c],sources=[s],jobs=[j])
        self.assertEqual(q['actions'][0]['evidence_refs'],['job'])
        self.assertEqual(q['actions'][0]['action'],'existing-channel-recovery')
        self.assertEqual(b['rows'],[])

    def test_conflicting_explicit_source_owner_cannot_supply_hr_evidence(self):
        c=dict(id='old',name='Existing',source_ids=['source'],target_countries=['BE'],career_url='https://old.recruitee.com')
        s=dict(id='source',company_id='different-owner',adapter='recruitee',career_url=c['career_url'],enabled=True,allowed_hosts=['old.recruitee.com'])
        j=dict(id='foreign-job',source_id='source',internship_type='internship',url='https://old.recruitee.com/o/hr',title='HR Intern',countries=['BE'],status='unverified')
        q,_=self.run_build([],companies=[c],sources=[s],jobs=[j])
        self.assertEqual(q['actions'][0]['evidence_refs'],[])

    def test_configured_adapter_does_not_pad_expansion_but_upgrade_does(self):
        c=dict(id='old',name='Existing',source_ids=['auto'],target_countries=['NL'],career_url='https://old.recruitee.com')
        s=dict(id='auto',adapter='recruitee',career_url=c['career_url'],enabled=True)
        _,b=self.run_build([],companies=[c],sources=[s])
        self.assertEqual(b['rows'],[])
        s['adapter']='universal-employer'
        _,b=self.run_build([],companies=[c],sources=[s])
        self.assertEqual(b['rows'][0]['action'],'adapter-upgrade-existing-employer')

    def test_404_and_shared_registry_identity_are_excluded(self):
        _,b=self.run_build([lead(page_open='404')])
        self.assertEqual(b['rows'],[])
        c=dict(id='old',name='Different Name',source_ids=['s'],target_countries=['BE'],career_url='https://new.recruitee.com')
        q,b=self.run_build([lead()],companies=[c])
        self.assertEqual(q['summary']['new_web_employers'],1)
        self.assertEqual(b['rows'],[])

    def test_all_27_country_tasks_include_companies_without_career_channels(self):
        c=dict(id='no-channel',name='No channel',source_ids=[],target_countries=['CY'])
        q,b=self.run_build([],companies=[c])
        self.assertEqual({r['code'] for r in q['countries']},set(EU27))
        cy=next(r for r in q['countries'] if r['code']=='CY')
        self.assertEqual(cy['research_companies'],1)
        self.assertFalse(cy['research_complete'])
        self.assertEqual(len(q['source_discovery_required']),1)

    def test_country_target_does_not_become_a_confirmed_workplace(self):
        _,b=self.run_build([lead(country='NL',country_evidence='research-target-only')])
        r=b['rows'][0]
        self.assertEqual(r['research_countries'],['NL'])
        self.assertEqual(r['vacancy_country_hints'],[])
        self.assertFalse(r['country_coverage_verified'])

    def test_preflight_is_bound_to_its_exact_observed_url(self):
        p=dict(channel_key='recruitee:new.recruitee.com',url='https://new.recruitee.com/o/old',state='not-established',checked_at='2026-11-16')
        _,b=self.run_build([lead()],probes=dict(rows=[p]))
        self.assertEqual(len(b['rows']),1)
        self.assertNotIn('preflight',b['rows'][0])
        p['url']=lead()['url']
        _,b=self.run_build([lead()],probes=dict(rows=[p]))
        self.assertEqual(b['rows'],[])

    def test_aggregators_unsafe_urls_and_separate_vendor_tenants(self):
        for url in ['http://company.example/jobs','https://linkedin.com/jobs/123','https://a:secret@company.example/jobs']:
            self.assertIsNone(channel(url))
        self.assertNotEqual(channel('https://jobs.smartrecruiters.com/One')['key'],channel('https://jobs.smartrecruiters.com/Two')['key'])


class ProbeTests(unittest.TestCase):
    def row(self,url='https://new.recruitee.com/o/hr'):
        return dict(company_key='new',name='New',channel_key='recruitee:new.recruitee.com',adapter='recruitee',
                    hr_evidence=[dict(kind='indexed-search',title='HR Intern',url=url)])

    def test_application_only_url_is_not_requested(self):
        with patch('socket.create_connection',side_effect=AssertionError('No network')):
            r=probe(self.row('https://new.recruitee.com/o/hr/c/new'))
        self.assertEqual(r['requests'],0)
        self.assertEqual(r['state'],'not-established')

    def test_form_or_title_does_not_promote_or_grant_redirect_scope(self):
        calls=[]
        class Client:
            requests=1;bytes=200
            def __init__(self,**kwargs):self.kwargs=kwargs
            def request(self,url):
                calls.append(url)
                if self.redirect_scope_allowed('https://evil.example/apply'):raise AssertionError('Overbroad scope')
                body=b'<h1>HR Intern</h1><form id="application"><input name="name"><input type="email"><button>Apply</button></form>'
                return body,200,url
        r=probe(self.row(),Client)
        self.assertEqual(len(calls),1)
        self.assertEqual(r['state'],'same-title-page-observed')
        self.assertEqual(r['availability'],'unverified')
        self.assertFalse(r['integration_ready'])
        self.assertFalse(r['production_enabled'])


if __name__=='__main__':unittest.main()
