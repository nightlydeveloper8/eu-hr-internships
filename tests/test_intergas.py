"""General multi-department internship routes must remain separate from HR vacancies."""
import unittest
from collector.classify import classify_role


class IntergasProgrammeTests(unittest.TestCase):
    def test_department_list_does_not_establish_specific_hr_internship(self):
        description = ('Stagiairs van alle studierichtingen: techniek, IT, logistiek, '
                       'finance, HR, communicatie. Welke afdeling en opdracht past bepalen we samen.')
        for title in ['Stageplaats bij Intergas 2027', 'Stageplaats bij Example 2028']:
            with self.subTest(title=title):
                self.assertIsNone(classify_role(title, description, 'internship'))

    def test_specific_hr_title_still_qualifies_without_company_name_rule(self):
        result = classify_role('HR Stage', 'Je ondersteunt HR en Recruitment.', 'internship')
        self.assertEqual(result['internship_type'], 'internship')
        self.assertIn('hr-generalist', result['categories'])


if __name__ == '__main__':
    unittest.main()
