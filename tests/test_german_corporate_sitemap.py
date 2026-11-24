"""German held sitemap ingestion and compressed index handling."""
import gzip
import unittest
from unittest.mock import Mock

from collector.adapters import collect
from collector.daily import provision
from collector.employer_pages import sitemap_records
from collector.pipeline import ROOT, read


class GermanCorporateSitemapTests(unittest.TestCase):
    def test_db_reads_compressed_inventory_and_selects_only_stage_slugs(self):
        source = self.source()
        sitemap = source['sitemaps'][0]
        child = 'https://db.jobs//jobs.xml.gz'
        stage = 'https://db.jobs/de-de/Suche/Pflichtpraktikum-HR--12345'
        student_job = 'https://db.jobs/de-de/Suche/Praktikum-Werkstudent-HR--12346'
        child_xml = (
            f'<urlset><url><loc>{stage}</loc></url>'
            f'<url><loc>{student_job}</loc></url></urlset>'
        ).encode()
        client = Mock()
        client.request.side_effect = [
            (f'<sitemapindex><sitemap><loc>{child}</loc></sitemap></sitemapindex>'.encode(), 200, sitemap),
            (gzip.compress(child_xml), 200, child),
        ]
        records = sitemap_records(source, client)
        self.assertEqual([record['url'] for record in records], [stage])
        self.assertTrue(records[0]['agency_sitemap_current'])
        self.assertEqual(client.request.call_count, 2)

    def test_hold_blocks_collection_and_provisioning_is_idempotent(self):
        source = self.source()
        self.assertFalse(source['enabled'])
        client = Mock()
        with self.assertRaisesRegex(ValueError, 'collection activation hold'):
            collect(dict(source, enabled=True), client)
        self.assertEqual(client.mock_calls, [])
        companies = read(ROOT / 'data/companies.json', [])
        sources = read(ROOT / 'data/sources.json', [])
        self.assertEqual(provision(companies, sources), (companies, sources))

    def source(self):
        return next(source for source in read(ROOT / 'data/sources.json', [])
                    if source['id'] == 'held-deutsche-bahn-de-jobposting')
