import json
from pathlib import Path
import unittest
from collector.classify import *

class ClassificationTests(unittest.TestCase):
    def test_manual_evaluation(self):
        rows=json.loads((Path(__file__).resolve().parents[1]/'data/evaluation.json').read_text())
        for row in rows:
            with self.subTest(row=row['title']):
                actual=classify_role(row['title'],row.get('text',''),row.get('employment',''))
                self.assertEqual(actual is not None,row['include'])
                if row.get('category'): self.assertIn(row['category'],actual['categories'])

    def test_language_is_not_ad_language(self):
        self.assertEqual(workplace_languages('We are an international team. Please submit your application in English.'),[])
        self.assertEqual(workplace_languages('Free English language classes and a friendly environment.'),[])
        self.assertEqual(workplace_languages('Dutch language skills are not required.'),[])

    def test_explicit_multilingual_requirement(self):
        result=workplace_languages('You are fluent in English and Dutch.')
        self.assertEqual({r['code'] for r in result},{'en','nl'})
        self.assertTrue(all(r['evidence'] for r in result))

    def test_additional_languages_do_not_make_english_optional(self):
        result=workplace_languages('Proficient in English (additional languages are a plus).')
        self.assertEqual(result[0]['requirement'],'required-or-working')

    def test_vacation_is_not_internship_duration(self):
        self.assertIsNone(extract_metadata('We offer 5 weeks paid vacation. Welcome to our internship.')['duration'])

    def test_multilingual_statements(self):
        for statement,expected in [('Vous avez un niveau professionnel en anglais.','en'),('Sehr gute Deutschkenntnisse und fließend Englisch.','en'),('Je spreekt vloeiend Nederlands en Engels.','nl'),('Buona conoscenza della lingua italiana.','it'),('Fluency in Romanian.','ro')]:
            with self.subTest(statement=statement): self.assertIn(expected,{r['code'] for r in workplace_languages(statement)})

    def test_language_unknown_and_source_hint(self):
        self.assertIsNone(advertisement_language('abc')['code'])
        self.assertEqual(advertisement_language('abc','fr-FR')['code'],'fr')
        self.assertEqual(advertisement_language('the and your with will our are have')['code'],'en')

    def test_country_precision(self):
        self.assertEqual(len(COUNTRIES),27)
        for location,country in [('Amsterdam','NL'),('Lisbon','PT'),('Berlin','DE'),('Riga','LV')]: self.assertEqual(country_codes(location),[country])
        self.assertEqual(country_codes('Paris, Texas, United States'),[])
        self.assertEqual(country_codes('Remote'),[])
        self.assertEqual(country_codes('Berlin','US'),[])
        self.assertEqual(country_codes('France; Netherlands'),['FR','NL'])
        self.assertEqual(country_codes('Paris','FRA'),['FR'])
        self.assertEqual(country_codes('Amsterdam','Netherlands'),['NL'])

    def test_url_validation(self):
        self.assertEqual(canonical_url('https://jobs.lever.co/a/b?utm_source=x&trid=4#apply'),'https://jobs.lever.co/a/b')
        for url in ['http://x.com/job','javascript:alert(1)','https://localhost/job','https://127.0.0.1/job','https://a:b@x.com/job']:
            with self.subTest(url=url),self.assertRaises(ValueError):canonical_url(url)

    def test_duration_enrollment_workmode(self):
        result=extract_metadata('A 6 months internship. You must be enrolled at a Dutch university. Hybrid work.')
        self.assertEqual(result['duration'],'6 months');self.assertIn('enrolled',result['enrollment']);self.assertEqual(result['work_mode'],'hybrid')

    def test_stable_id(self):
        self.assertEqual(stable_id('a','1'),stable_id('a',1));self.assertNotEqual(stable_id('a',1),stable_id('b',1))

if __name__=='__main__':unittest.main()
