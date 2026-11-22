import json
from pathlib import Path
import unittest
from collections import Counter
from collector.classify import advertisement_language, workplace_languages, language_summary

DATA = Path(__file__).resolve().parents[1] / 'data' / 'language-evaluation.json'

class LanguageEvaluation(unittest.TestCase):
    def test_labelled_language_cases(self):
        for row in json.loads(DATA.read_text())['requirement_cases']:
            with self.subTest(text=row['text']):
                langs=workplace_languages(row['text']);summary=language_summary(row['text'],langs)
                self.assertEqual(summary['required_languages'],row['required'])
                self.assertEqual(sorted(l['code'] for l in langs if l['requirement']=='preferred'),row['preferred'])
                self.assertEqual(summary['alternative_languages'],row['alternatives'])
                self.assertEqual(summary['english_support']=='documented',row['english_supported'])
                self.assertEqual(summary['english_sufficiency']=='documented',row['english_alone'])

    def test_sample_identity_quota_and_evidence(self):
        rows = json.loads(DATA.read_text())['open_listings']
        counts = Counter(row['country'] for row in rows)
        self.assertGreaterEqual(len({row['id'] for row in rows}), 80)
        self.assertEqual(len({row['id'] for row in rows}), len(rows))
        for country in ('NL', 'FR', 'DE', 'IT', 'CH', 'BE'):
            self.assertGreaterEqual(counts[country], 10)
        self.assertTrue(all(item['excerpt'] for row in rows for item in row['requirements']))

    def test_full_bodies_support_bilingual_but_foreign_title_does_not(self):
        dutch = ('Je werkt met onze mensen en wij zorgen voor een goede plek waar jij het team '
                 'kan helpen met de taken van de afdeling. ') * 6
        french = ('Vous rejoignez notre équipe pour une mission avec des responsabilités. '
                  'Nous travaillons avec les équipes et vous développez votre expérience. ') * 7
        result = advertisement_language(dutch + french, page_hint='fr-BE')
        self.assertEqual((result['code'], result['codes']), ('bilingual', ['fr', 'nl']))
        self.assertEqual(advertisement_language('Human Resources Internship. ' + dutch)['code'], 'nl')
        self.assertEqual(advertisement_language('', ['de-CH', 'fr-CH'])['codes'], ['de', 'fr'])
        self.assertEqual(advertisement_language('', page_hint='it-IT')['method'], 'HTML lang')

    def test_explicit_evidence_and_english_sufficiency(self):
        for sentence, code in [('Fluent Dutch required', 'nl'), ('Deutsch C1', 'de'),
                               ("Maîtrise de l'anglais", 'en')]:
            with self.subTest(sentence=sentence):
                item, = workplace_languages(sentence)
                self.assertEqual((item['code'], item['evidence']), (code, sentence))
        self.assertEqual(workplace_languages('Candidates must join our Dutch office.'), [])
        self.assertEqual(language_summary('The role sits in our team.')['english_sufficiency'], 'unknown')
        self.assertEqual(language_summary('English is the only required language.')['english_sufficiency_evidence'],
                         'English is the only required language')
