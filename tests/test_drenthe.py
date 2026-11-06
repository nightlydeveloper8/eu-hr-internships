"""Cross-province integrity and CBS locality boundaries for Drenthe imports."""
import unittest
from collector.pipeline import ROOT,read
from scripts.integrate_drenthe import integrate


class DrentheImportTests(unittest.TestCase):
    def fixture(self):
        geography=read(ROOT/'data/drenthe-geography.json',{})
        row=dict(name='Example',existing_company_id='stable-example',website_url='https://example.org',career_url='https://example.org/jobs',presence_source_url='https://example.org/address',municipality='Assen',locality='Assen',checked_on='2026-11-06',size={'qualification':'unknown'},employer_type='private')
        company=dict(id='stable-example',name='Example',website_url='https://example.org',source_ids=['existing-feed'],workplaces=[dict(country='DE',region_code='DE11',city='Stuttgart',location_confidence='confirmed')],groningen_research={'size':{'qualification':'unknown'}},target_countries=['DE'])
        source=dict(id='existing-feed',company_id='stable-example',employer='Example',adapter='employer-index',enabled=True,allowed_hosts=['example.org'])
        return geography,row,company,source

    def test_existing_feed_and_other_province_are_preserved_idempotently(self):
        geography,row,company,source=self.fixture()
        c,s,regional=integrate([company],[source],geography,[row])
        c2,s2,_=integrate(c,s,geography,[row])
        self.assertEqual((c,s),(c2,s2))
        self.assertEqual(s,[source]);self.assertEqual(c[0]['source_ids'],['existing-feed'])
        self.assertEqual(c[0]['workplaces'][0],company['workplaces'][0])
        self.assertEqual(c[0]['groningen_research'],company['groningen_research'])
        self.assertEqual(c[0]['workplaces'][1]['region_code'],'NL13')
        self.assertEqual(c[0]['workplaces'][1]['municipality_code'],'GM0106')
        self.assertEqual(regional[0]['company_id'],'stable-example')
        self.assertEqual(company.get('drenthe_research'),None)

    def test_wrong_municipality_and_unknown_existing_id_fail(self):
        geography,row,company,source=self.fixture()
        wrong=dict(row,locality='Emmen')
        with self.assertRaisesRegex(ValueError,'Unresolved CBS locality'):
            integrate([company],[source],geography,[wrong])
        with self.assertRaisesRegex(ValueError,'Unknown existing company ID'):
            integrate([company],[source],geography,[dict(row,existing_company_id='typo')])

    def test_all_cbs_municipalities_and_unique_settlement_codes(self):
        geography=read(ROOT/'data/drenthe-geography.json',{})
        self.assertEqual(geography['province']['nuts2_code'],'NL13')
        self.assertEqual(geography['municipality_count'],12)
        codes=[p['code'] for m in geography['municipalities'] for p in m['settlements']]
        self.assertEqual(len(codes),227);self.assertEqual(len(set(codes)),227)
        self.assertEqual(sum(m['settlement_count'] for m in geography['municipalities']),227)
        self.assertEqual({m['name'] for m in geography['municipalities']},{'Aa en Hunze','Assen','Borger-Odoorn','Coevorden','De Wolden','Emmen','Hoogeveen','Meppel','Midden-Drenthe','Noordenveld','Tynaarlo','Westerveld'})


if __name__=='__main__':unittest.main()
