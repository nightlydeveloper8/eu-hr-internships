"""Bounded Interzorg workplace review must not turn body mentions into locations."""
import unittest
from collector.employer_pages import page_record
from collector.pipeline import ROOT, read


class InterzorgWorkplaceTests(unittest.TestCase):
    def setUp(self):
        self.source = dict(read(ROOT / 'data/drenthe-source-overrides.json', {})[
            'auto-interzorg-noord-nederland'], allowed_hosts=['www.interzorg.nl'])
        self.url = 'https://www.interzorg.nl/je-bent-van-harte-welkom/vacatures/example'

    def parse(self, place, extra=''):
        body = ('<main><h1>Helpende</h1><p>Publicatiedatum 28 okt 2026 Plaats '
                + place + ' Arbeidsovereenkomst 1 jaar</p><p>'
                + 'Werk samen met bewoners en hun familie. ' * 10 + extra + '</p></main>').encode()
        url = self.url

        class Client:
            def request(self, _):
                return body, 200, url

        return page_record(dict(url=url), self.source, Client())

    def test_explicit_place_field_overrides_unrelated_city_mentions(self):
        for place, city in [('De Slinge - Assen', 'Assen'), ('Servicecentrum - Assen', 'Assen'),
                            ('Nieuw Graswijk - Assen', 'Assen'), ('De Hullen - Roden', 'Roden'),
                            ('De Hoprank - Peize', 'Peize'), ('Kornoeljehof - Vries', 'Vries')]:
            with self.subTest(place=place):
                record = self.parse(place, 'Andere locaties in Assen, Roden, Peize en Vries.')
                self.assertEqual((record['city'], record['country']), (city, 'NL'))

    def test_flexible_unknown_and_conflicting_place_fields_require_review(self):
        for place, extra in [('Assen en omgeving (flexibel / divers)', ''),
                             ('Nieuwe locatie - Assen', ''),
                             ('De Hullen - Roden', 'Plaats De Slinge - Assen Uren 24 uur')]:
            with self.subTest(place=place, extra=extra):
                with self.assertRaisesRegex(ValueError, 'workplace requires review'):
                    self.parse(place, extra)


if __name__ == '__main__':
    unittest.main()
