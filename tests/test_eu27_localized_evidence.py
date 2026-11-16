"""Localized placement and language evidence must not promote work experience or CV text."""
import json,unittest
from pathlib import Path
from collector.classify import classify_role,workplace_languages,language_summary

class LocalizedEvidenceTests(unittest.TestCase):
    def test_polish_observed_role_and_gender_variants(self):
        for title in ['Stażysta/Stażystka w dziale HR','Stażystka HR','Stażyści HR','Stażystki HR']:
            with self.subTest(title=title):self.assertEqual(classify_role(title)['internship_type'],'internship')
    def test_polish_placement_headings_and_employment(self):
        for title in ['Staż HR','Płatny staż w HR','Letni staż HR','HR: staż','HR – staż']:
            with self.subTest(title=title):self.assertIsNotNone(classify_role(title))
        self.assertIsNotNone(classify_role('Human Resources',employment='Staż'))
    def test_work_experience_is_not_a_polish_placement(self):
        for title in ['Specjalista HR – wymagany staż pracy 5 lat','HR: staż pracy 2 lata','HR – letni staż pracy','HR manager']:
            with self.subTest(title=title):self.assertIsNone(classify_role(title,'Praca HR; staż pracy mile widziany'))
    def test_coordinator_of_interns_and_non_hr_student_roles_are_not_hr_internships(self):
        self.assertIsNone(classify_role('Koordynator stażystów HR'))
        self.assertIsNone(classify_role('Stażysta Marketing'))
        self.assertIsNone(classify_role('Stażysta Software Engineer','HR interview and onboarding'))
    def test_firstmind_missing_intern_does_not_justify_reclassifying_sales_roles(self):
        for title in ['Talent Advisor at FirstMind','Talent Associate at FirstMind','Sales Internship at FirstMind','Global Talent Intern']:
            self.assertIsNone(classify_role(title,'Sell talent assessment tools to customers'))
    def test_spanish_b2_requirement_does_not_prove_english_sufficiency(self):
        langs=workplace_languages('Inglés nivel B2.')
        self.assertEqual([l['code'] for l in langs],['en'])
        summary=language_summary('Inglés nivel B2.',langs)
        self.assertEqual(summary['required_languages'],['en']);self.assertEqual(summary['english_support'],'documented')
        self.assertEqual(summary['english_sufficiency'],'unknown')
    def test_actual_bsh_reduced_fixture_gains_language_metadata_only(self):
        from collector.universal import Document
        body=(Path(__file__).parent/'fixtures/bsh-publication/vacancy.html').read_bytes();text=Document(body,'https://jobs.bsh-group.de/job').text
        summary=language_summary(text);self.assertEqual(summary['english_support'],'documented');self.assertEqual(summary['english_sufficiency'],'unknown')
    def test_spanish_optional_levels_remain_optional(self):
        for text in ['Inglés nivel B2 deseable.','Valorable nivel B2 de inglés.','Preferible nivel alto de inglés.','Valorable: nivel B2 de inglés.','Deseable: inglés nivel B2.']:
            with self.subTest(text=text):
                langs=workplace_languages(text);self.assertEqual([l['requirement'] for l in langs],['preferred']);self.assertEqual(language_summary(text,langs)['english_support'],'unknown')
    def test_spanish_negated_levels_are_not_workplace_evidence(self):
        for text in ['No se requiere inglés nivel B2.','Inglés nivel B2 no es obligatorio.','No es necesario nivel B2 de inglés.']:
            with self.subTest(text=text):self.assertEqual(workplace_languages(text),[])
    def test_spanish_courses_are_not_required_languages(self):
        for text in ['Clases de inglés nivel B2 gratuitas.','Curso de inglés de nivel B2.','Cursos inglés nivel B2.']:
            with self.subTest(text=text):self.assertEqual(workplace_languages(text),[])
    def test_constructor_cv_language_and_classes_are_not_workplace_evidence(self):
        for text in ['Please send your resume in English only.','English classes (iTalki – $130 monthly).','Envía tu CV en inglés nivel B2.']:
            with self.subTest(text=text):self.assertEqual(workplace_languages(text),[])
    def test_other_language_clause_does_not_negate_english(self):
        langs=workplace_languages('No se requiere español, inglés nivel B2.')
        self.assertEqual([l['code'] for l in langs],['en'])

if __name__=='__main__':unittest.main()
