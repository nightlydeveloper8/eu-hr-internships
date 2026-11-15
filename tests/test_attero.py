"""Count-matched Attero inventory excludes generic landing pages, not programmes."""
import unittest
from collector.employer_pages import index_records
from collector.pipeline import ROOT, read


class AtteroInventoryTests(unittest.TestCase):
    def setUp(self):
        self.source = dict(read(ROOT / 'data/drenthe-source-overrides.json', {})[
            'auto-attero'], id='auto-attero', employer='Attero',
            allowed_hosts=['www.attero.nl'])
        self.url = self.source['index_urls'][0]
        self.specific = self.url + '3657887-sheq-officer/'
        self.general = self.url + '3449027-stagiair/'

    def inventory(self, heading):
        page = (heading + '<a href="' + self.specific + '">SHEQ Officer</a>'
                + '<a href="' + self.specific + '">Bekijk de vacature</a>'
                + '<a href="' + self.general + '">Stagiair</a>'
                + '<a href="' + self.url + 'stageplek/">Stage mogelijkheden</a>')
        url = self.url

        class Client:
            def request(self, _):
                return page.encode(), 200, url

        return index_records(self.source, Client())

    def test_distinct_numbered_posts_match_count_without_inferred_closure(self):
        result = self.inventory('Aantal vacatures: 2')
        self.assertEqual({r['url'] for r in result}, {self.specific.rstrip('/'), self.general.rstrip('/')})
        self.assertTrue(result.stats['complete'])
        self.assertFalse(result.stats['closure_complete'])
        # Inventory membership establishes neither an HR role nor its workplace.
        self.assertTrue(all(r['needs_page'] and r['city'] is None for r in result))

    def test_missing_or_unmatched_published_total_never_reports_complete(self):
        for heading in ['Aantal vacatures: 3', 'Vacatures']:
            with self.subTest(heading=heading):
                with self.assertRaises(ValueError):
                    self.inventory(heading)


if __name__ == '__main__':
    unittest.main()
