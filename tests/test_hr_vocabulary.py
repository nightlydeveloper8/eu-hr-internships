import json
import unittest
from pathlib import Path

from collector.classify import (CATEGORIES, LANGUAGES, VOCABULARY, classify_role, vocabulary_pattern,
                                vocabulary_categories, fold)
from collector.public_sources import EURES_QUERIES, JOBTECH_QUERIES

ROOT = Path(__file__).resolve().parents[1]


class VocabularyFileTests(unittest.TestCase):
    def test_categories_and_languages_are_known(self):
        data = json.loads((ROOT / 'data' / 'hr-vocabulary.json').read_text())
        for key, entry in data['categories'].items():
            self.assertIn(key, CATEGORIES)
            for block in ('strong', 'contextual'):
                for language, terms in entry.get(block, {}).items():
                    self.assertIn(language, LANGUAGES, f'{key}/{block}/{language}')
                    self.assertTrue(all(isinstance(t, str) and t.strip() for t in terms))
        for block in ('placement_terms', 'hr_terms'):
            self.assertTrue(set(data['search'][block]) <= set(LANGUAGES))

    def test_every_strong_term_matches_itself(self):
        for key, entry in VOCABULARY['categories'].items():
            for terms in entry.get('strong', {}).values():
                for term in terms:
                    self.assertTrue(vocabulary_pattern([term]).search(fold(term.rstrip('*'))), term)


class PatternTests(unittest.TestCase):
    def test_whole_words_prefixes_and_required_ampersand(self):
        self.assertTrue(vocabulary_pattern(['personalentwicklung*']).search('personalentwicklungsprogramm'))
        self.assertFalse(vocabulary_pattern(['werving']).search('fondsenwerving'))
        self.assertTrue(vocabulary_pattern(['aus- und weiterbildung']).search('praktikum aus und weiterbildung'))
        self.assertTrue(vocabulary_pattern(['p&o']).search('stagiair p & o'))
        self.assertFalse(vocabulary_pattern(['d&i']).search('assistente di negozio'))
        self.assertTrue(vocabulary_pattern(['nóminas']).search(fold('Prácticas Nóminas')))


class ClassificationTests(unittest.TestCase):
    def test_national_language_specialties_are_recognised(self):
        cases = {
            'Stage Formazione e Sviluppo': 'learning-development',
            'Tirocinio Paghe e Contributi': 'compensation-benefits',
            'Becario Selección de Personal': 'talent-acquisition',
            'Praktikant Personalmarketing': 'employer-branding',
            'Staż w dziale kadr i płac': 'compensation-benefits',
            'DEI Intern': 'diversity-inclusion',
            'Estagiário de Recursos Humanos': 'hr-generalist',
        }
        for title, category in cases.items():
            self.assertEqual(classify_role(title)['category'], category, title)

    def test_contextual_terms_need_hr_in_title_or_same_sentence(self):
        self.assertIsNone(classify_role('Stage Formazione'))
        self.assertIsNotNone(classify_role('Stage Formazione', "Supporterai l'ufficio risorse umane nella formazione interna."))
        self.assertIsNone(classify_role('Stage Formazione', "Formazione per i clienti. Invia il CV all'ufficio risorse umane."))
        self.assertIsNone(classify_role('Tirocinio Formazione docenti', "L'ufficio risorse umane organizza la formazione."))
        self.assertEqual(vocabulary_categories(fold('stage formazione hr'), ''), ['hr-generalist', 'learning-development'])

    def test_new_placement_words(self):
        for title in ('Pflichtpraktikum Personalabteilung', 'Stagiu resurse umane', 'Praktikantas personalo skyriuje',
                      'Praktikplads i HR', 'Estagiária de RH'):
            self.assertIsNotNone(classify_role(title), title)


class QueryGenerationTests(unittest.TestCase):
    def test_queries_cover_national_languages(self):
        self.assertEqual(len(EURES_QUERIES), 22)
        self.assertTrue(any('tirocinio' in q and 'paghe' in q for q in EURES_QUERIES))
        self.assertTrue(any('staż' in q and 'kadry' in q for q in EURES_QUERIES))
        self.assertIn('+praktik +rekrytering', JOBTECH_QUERIES)


if __name__ == '__main__':
    unittest.main()


class VetoTests(unittest.TestCase):
    def test_veto_does_not_block_corporate_training_words(self):
        self.assertIsNotNone(classify_role('Praktikum Schulungsmanagement', 'Du unterstützt die Personalabteilung bei Schulungen für Mitarbeitende.'))
        self.assertIsNone(classify_role('Praktikum Schulung Grundschule', 'Die Personalabteilung organisiert Schulungen.'))
