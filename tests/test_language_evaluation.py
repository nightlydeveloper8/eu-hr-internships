import json
from pathlib import Path
import unittest
from collector.classify import workplace_languages,language_summary

class LanguageEvaluation(unittest.TestCase):
    def test_labelled_language_cases(self):
        for row in json.loads((Path(__file__).resolve().parents[1]/'data/language-evaluation.json').read_text()):
            with self.subTest(text=row['text']):
                langs=workplace_languages(row['text']);summary=language_summary(row['text'],langs)
                self.assertEqual(summary['required_languages'],row['required'])
                self.assertEqual(sorted(l['code'] for l in langs if l['requirement']=='preferred'),row['preferred'])
                self.assertEqual(summary['alternative_languages'],row['alternatives'])
                self.assertEqual(summary['english_support']=='documented',row['english_supported'])
                self.assertEqual(summary['english_sufficiency']=='documented',row['english_alone'])
