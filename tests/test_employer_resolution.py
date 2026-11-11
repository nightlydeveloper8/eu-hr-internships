"""An official recruiting relationship is a scoped grant, never a group-wide alias."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collector.employer_resolution import (
    is_reviewed_publisher, reviewed_source, validate_reviews,
)
from collector.ownership import employer_matches, owned_record
from collector.pipeline import ROOT, read, finalize
from collector.universal import job_from_json
from tests.test_all_employers import posting


class ScopedEmployerIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=read(ROOT/'data/sources.json',[])
        cls.reviews=read(ROOT/'data/employer-identity-reviews.json',[])
        cls.companies=read(ROOT/'data/companies.json',[])
        cls.by_id={s['id']:s for s in cls.sources}

    def test_official_review_registry_validates_against_existing_source_and_host(self):
        self.assertTrue(validate_reviews(self.reviews,self.sources))
        self.assertEqual(len(self.reviews),2)
        self.assertEqual({r['relation'] for r in self.reviews},
                         {'official-recruiting-publisher','group-parent'})

    def test_achmea_exact_publisher_on_reviewed_official_host_only(self):
        original=self.by_id['auto-centraal-beheer-achmea']
        s=reviewed_source(original,self.reviews)
        job_url='https://www.werkenbijachmea.nl/vacatures/hr-stage-123'
        info=posting(hiringOrganization={'name':'Achmea'})
        self.assertIsNone(job_from_json(info,job_url,original))
        r=job_from_json(info,job_url,s)
        self.assertIsNotNone(r)
        self.assertEqual(r['employer'],'Achmea')
        self.assertEqual(r['source_id'],original['id'])
        self.assertTrue(owned_record(r,s))
        self.assertNotIn('_reviewed_identity_hosts',original)
        self.assertFalse(employer_matches('Achmea',s,'https://another.example/vacatures/hr-stage-123'))
        self.assertIsNone(job_from_json(info,'https://another.example/jobs/hr',s))

    def test_brand_alias_is_not_automatically_a_publisher(self):
        s=reviewed_source(self.by_id['auto-centraal-beheer-achmea'],self.reviews)
        url='https://www.werkenbijachmea.nl/vacatures/hr-stage-123'
        self.assertFalse(employer_matches('FBTO',s,url))
        self.assertFalse(employer_matches('De Friesland',s,url))
        self.assertIsNone(job_from_json(posting(hiringOrganization={'name':'FBTO'}),url,s))

    def test_nonstructured_visible_or_unowned_feed_cannot_inherit_publisher(self):
        s=reviewed_source(self.by_id['auto-centraal-beheer-achmea'],self.reviews)
        url='https://www.werkenbijachmea.nl/vacatures/hr-stage-123'
        r=dict(employer='Achmea',url=url)
        self.assertFalse(owned_record(r,s))
        self.assertFalse(owned_record(dict(r,employer_identity_evidence='unreviewed-feed'),s))
        self.assertTrue(owned_record(dict(r,employer_identity_evidence='jobposting-hiring-organization'),s))

    def test_parent_group_does_not_own_subsidiary_inventory(self):
        s=reviewed_source(self.by_id['auto-oosterwolde-plastic-industrie-b-v'],self.reviews)
        url='https://werkenbijopackgroup.nl/vacatures/stage-employer-branding-giessen-385'
        self.assertFalse(employer_matches('OPACKGROUP',s,url))
        self.assertIsNone(job_from_json(posting(hiringOrganization={'name':'OPACKGROUP'}),url,s))
        self.assertTrue(employer_matches(s['employer'],s,url))
        self.assertEqual(s['_reviewed_identity_hosts'],{})

    def test_wrong_tilburg_ats_tenant_is_not_published_by_university(self):
        s=reviewed_source(self.by_id['auto-tilburg-university'],self.reviews)
        self.assertFalse(employer_matches('Trunkrs',s,'https://trunkrs.recruitee.com/o/hr-stage'))
        self.assertIsNone(job_from_json(posting(hiringOrganization={'name':'Trunkrs'}),
                                         'https://trunkrs.recruitee.com/o/hr-stage',s))

    def test_unknown_official_host_and_source_spoof_fail_closed(self):
        base=dict(self.reviews[0])
        cases=[
            dict(base,host='attacker.example'),
            dict(base,evidence_url='https://attacker.example/achmea'),
            dict(base,source_id='unknown'),
            dict(base,company_id='another-company'),
            dict(base,source_employer='Other'),
            dict(base,reviewed_on='not-a-date'),
            dict(base,relation='global-alias'),
            dict(base,published_name=''),
            dict(base,host='WWW.WERKENBIJACHMEA.NL'),
        ]
        for rule in cases:
            with self.subTest(rule=rule),self.assertRaises(ValueError):
                validate_reviews([rule],self.sources)

    def test_duplicate_or_cross_source_alias_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            validate_reviews([self.reviews[0],dict(self.reviews[0])],self.sources)
        s=reviewed_source(self.by_id['auto-bentacera'],self.reviews)
        self.assertFalse(is_reviewed_publisher('Achmea',s,
                                              'https://www.werkenbijachmea.nl/vacatures/hr-stage'))

    def test_all_historical_ids_preserved_without_migration_or_verification(self):
        """Registration must not rewrite historical advertisements or force open."""
        prior=read(ROOT/'data/catalog.json',{})
        before=copy.deepcopy(prior)
        for name in ('auto-centraal-beheer-achmea',
                     'auto-oosterwolde-plastic-industrie-b-v',
                     'auto-tilburg-university'):
            reviewed_source(self.by_id[name],self.reviews)
        self.assertEqual(prior,before)
        self.assertEqual(len({j['id'] for j in prior['jobs']}),len(prior['jobs']))
        self.assertTrue(all(j['status']=='unverified' for j in prior['jobs']
                            if j['id'] in {'e83537f80a3c4be51eae','994018cb6659595e818f'}))

    def test_two_finalizations_retain_ids_and_group_name_on_synthetic_record(self):
        catalog=read(ROOT/'data/catalog.json',{})
        registry=self.sources
        review=reviewed_source(self.by_id['auto-centraal-beheer-achmea'],self.reviews)
        url='https://www.werkenbijachmea.nl/vacatures/synthetic-hr-intern'
        extracted=job_from_json(posting(hiringOrganization={'name':'Achmea'}),url,review)
        self.assertEqual(extracted['employer'],'Achmea')
        # No invented application evidence: a publisher match alone is never open.
        self.assertFalse(extracted.get('verification'))
        part=dict(report=dict(id=review['id'],status='partial',complete=False,closure_complete=False,
                              checked_at=catalog['last_attempt_at'],records_inspected=0),
                  jobs=[],closure_eligible=[])
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            a,_=finalize(registry,[review],catalog,{},[part],catalog['last_attempt_at'],out)
            b,_=finalize(registry,[review],a,{},[part],catalog['last_attempt_at'],out)
        self.assertEqual(a['jobs'],b['jobs'])
        self.assertEqual({j['id'] for j in catalog['jobs']},{j['id'] for j in b['jobs']})


if __name__=='__main__':unittest.main()
