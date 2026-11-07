"""Full sitemap -> PageCache -> page parser -> verification -> finalize, offline."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from collector.pipeline import finalize, process_source
from collector.runtime import PageCache
from collector.verification import verified_job

BASE = datetime(2026, 11, 8, 0, tzinfo=timezone.utc)
URL = 'https://example.org/jobs/hr-intern'
SOURCE = dict(id='intake-sitemap', employer='Example', adapter='employer-sitemap',
              allowed_hosts=['example.org'], sitemaps=['https://example.org/sitemap.xml'],
              job_url_pattern=r'/jobs/')


class Clock(datetime):
    current = BASE

    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz) if tz else cls.current.replace(tzinfo=None)


class SitemapClient:
    def __init__(self, text='Stage vanaf februari 2027.', deadline='2099-01-01', blocked=False, closed=False):
        self.text, self.deadline, self.blocked, self.closed = text, deadline, blocked, closed
        self.calls = []

    def request(self, url):
        self.calls.append(url)
        if url.endswith('sitemap.xml'):
            return f'<urlset><url><loc>{URL}</loc></url></urlset>'.encode(), 200, url
        if self.blocked:
            raise ValueError('robots.txt disallows vacancy')
        post = dict(**{'@type': 'JobPosting'}, title='HR Intern', description=self.text,
                    hiringOrganization=dict(name='Example'),
                    jobLocation=dict(address=dict(addressLocality='Amsterdam', addressCountry='NL')),
                    validThrough=self.deadline)
        body = ('<h1>HR Intern</h1><p>' + self.text + '</p><script type="application/ld+json">'
                + json.dumps(post) + '</script><form id="application"><input name="name">'
                '<input name="email" type="email"><input name="cv" type="file">'
                '<button type="submit">Apply</button></form>')
        if self.closed:
            body += '<p>This vacancy has now expired.</p>'
        return body.encode(), 200, url


class IntakePipelineTests(unittest.TestCase):
    def cycle(self, prior, client, cache, root, clock):
        Clock.current = clock
        stamp = clock.isoformat()
        with patch('collector.runtime.datetime', Clock):
            part = process_source(SOURCE, client, stamp, cache=cache)
        self.assertEqual(len(part['jobs']), 1)
        result, _ = finalize([SOURCE], [SOURCE], prior, {}, [part], stamp, root)
        self.assertEqual(part['closure_eligible'], [])  # sitemap is never full inventory
        return result

    def test_blocked_page_cache_12_and_36_hours_keeps_original_evidence_time(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            cache = PageCache(SOURCE['id'], root/'cache')
            prior = self.cycle({'jobs': []}, SitemapClient(), cache, root, BASE)
            original = prior['jobs'][0]
            self.assertEqual(original['intake']['provenance'], 'live')
            cached_bytes = cache.path(URL).read_bytes()
            for hours in (12, 36):
                clock = BASE + timedelta(hours=hours)
                blocked = SitemapClient(blocked=True)
                result = self.cycle(prior, blocked, cache, root, clock)
                job = result['jobs'][0]
                self.assertEqual(job['intake']['checked_at'], BASE.isoformat())
                self.assertEqual(job['intake']['provenance'], 'cache')
                self.assertEqual(job['intake']['observed_via'], 'live')
                self.assertEqual(job['intake']['published_start'], '2027-02')
                self.assertEqual(job['last_verified_at'], original['last_verified_at'])
                self.assertFalse(verified_job(job, clock.isoformat()))
                self.assertEqual(job['id'], original['id'])
                self.assertEqual(job['source_id'], SOURCE['id'])
                self.assertEqual(job['verification']['policy_version'], 2)
                self.assertEqual(blocked.calls, [SOURCE['sitemaps'][0], URL])
                self.assertEqual(cache.path(URL).read_bytes(), cached_bytes)
                self.assertEqual(self.cycle(result, blocked, cache, root, clock), result)
                prior = result

    def test_legacy_cache_and_recache_do_not_reset_original_observation(self):
        from collector.employer_pages import sitemap_records, page_record
        with TemporaryDirectory() as directory:
            root = Path(directory)
            cache = PageCache(SOURCE['id'], root/'cache')
            client = SitemapClient()
            record = page_record(sitemap_records(SOURCE, client)[0], SOURCE, client, clock=BASE)
            Clock.current = BASE
            with patch('collector.runtime.datetime', Clock):
                cache.put(URL, record)  # legacy entry has only stored_at
            prior = {'jobs': []}
            for hours in (12, 36):
                clock = BASE + timedelta(hours=hours)
                prior = self.cycle(prior, SitemapClient(blocked=True), cache, root, clock)
                self.assertEqual(prior['jobs'][0]['intake']['checked_at'], BASE.isoformat())
                with patch('collector.runtime.datetime', Clock):
                    hit = cache.get(URL)
                    cache.put(URL, hit)  # technical rewrite must not become evidence
                self.assertEqual(prior['jobs'][0]['intake']['provenance'], 'cache')

    def test_live_changed_then_removed_start_supersedes_cached_text_even_when_expired(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            cache = PageCache(SOURCE['id'], root/'cache')
            prior = self.cycle({'jobs': []}, SitemapClient(), cache, root, BASE)
            for hours, text, deadline, expected in [
                (12, 'Startdatum: 1 maart 2027.', '2099-01-01', '2027-03-01'),
                (36, 'Start in overleg.', '2026-10-15', None),
            ]:
                clock = BASE + timedelta(hours=hours)
                result = self.cycle(prior, SitemapClient(text, deadline), cache, root, clock)
                job = result['jobs'][0]
                self.assertEqual(job.get('intake', {}).get('published_start'), expected)
                self.assertEqual(job['status'], 'open' if expected else 'closed')
                if expected:
                    self.assertEqual(job['intake']['provenance'], 'live')
                    self.assertEqual(job['intake']['checked_at'], clock.isoformat())
                self.assertEqual(self.cycle(result, SitemapClient(text, deadline), cache, root, clock), result)
                prior = result

    def test_uncached_expired_page_and_closed_banner_still_replace_intake(self):
        for closed in (False, True):
            with self.subTest(closed=closed), TemporaryDirectory() as directory:
                root = Path(directory)
                cache = PageCache(SOURCE['id'], root/'cache')
                prior = self.cycle({'jobs': []}, SitemapClient(), cache, root, BASE)
                cache.path(URL).unlink()
                result = self.cycle(prior, SitemapClient('Start in overleg.', '2026-10-15', closed=closed),
                                    cache, root, BASE + timedelta(days=1))
                self.assertNotIn('intake', result['jobs'][0])
                self.assertEqual(result['jobs'][0]['status'], 'closed')
                self.assertEqual(result['jobs'][0]['id'], prior['jobs'][0]['id'])

    def test_non_intake_dates_are_not_published_through_full_pipeline(self):
        negatives = [
            'Solliciteer vanaf februari 2027.',
            'Per februari 2027 bedraagt de stagevergoeding 500 euro.',
            'Applications start February 2027.',
            'Publication starting February 2027.',
            'Stagevergoeding vanaf februari 2027 bedraagt 500 euro.',
            'Our marketing campaign starts February 2027.',
            'Beschikbaar vanaf februari 2027.',
            'Stage vanaf februari 2027 of maart 2027.',
        ]
        for text in negatives:
            with self.subTest(text=text), TemporaryDirectory() as directory:
                root = Path(directory)
                cache = PageCache(SOURCE['id'], root/'cache')
                prior = self.cycle({'jobs': []}, SitemapClient(), cache, root, BASE)
                for hours in (12, 36):
                    result = self.cycle(prior, SitemapClient(text), cache, root, BASE + timedelta(hours=hours))
                    self.assertIsNone(result['jobs'][0].get('intake', {}).get('published_start'))
                    prior = result

    def test_valid_start_variants_still_work_through_full_pipeline(self):
        for text in ['Stage vanaf februari 2027 met een stagevergoeding van 500 euro.', 'Je kan per februari 2027 starten.',
                     'Starting in February 2027.', 'Startdatum: februari 2027.',
                     'Deze stage is vanaf februari 2027 voor vijf maanden.',
                     'Kom jij ons team vanaf februari 2027 versterken als stagiair?']:
            with self.subTest(text=text), TemporaryDirectory() as directory:
                root = Path(directory)
                cache = PageCache(SOURCE['id'], root/'cache')
                prior = {'jobs': []}
                for hours in (0, 24):
                    prior = self.cycle(prior, SitemapClient(text), cache, root, BASE + timedelta(hours=hours))
                    self.assertEqual(prior['jobs'][0]['intake']['published_start'], '2027-02')
