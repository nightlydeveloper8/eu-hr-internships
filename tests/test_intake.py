"""Offline regressions through the real adapter, verification and daily finalize."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from collector.intake import extract_intake
from collector.pipeline import ROOT, finalize, process_source, read
from collector.verification import verified_job

STAMP = '2026-11-08T12:00:00+00:00'
SOURCE = dict(id='intake-example', employer='Example', adapter='greenhouse',
              board='example', allowed_hosts=['example.org'])


class VacancyClient:
    def __init__(self, text, page_text=None, form=True):
        self.text = text
        self.page_text = text if page_text is None else page_text
        self.form = form

    def json(self, url):
        return dict(jobs=[dict(id=1, title='HR Intern', location=dict(name='Amsterdam'),
                              content=self.text, absolute_url='https://example.org/jobs/1')])

    def request(self, url):
        form = ('<form id="application"><input name="name"><input type="email" name="email">'
                '<input name="cv" type="file"><button type="submit">Apply</button></form>') if self.form else ''
        return ('<h1>HR Intern</h1><p>' + self.page_text + '</p>' + form).encode(), 200, url


class IntakeTests(unittest.TestCase):
    def cycle(self, previous, text, stamp=STAMP, **kwargs):
        part = process_source(SOURCE, VacancyClient(text, **kwargs), stamp)
        self.assertEqual(len(part['jobs']), 1)
        with TemporaryDirectory() as directory:
            result, _ = finalize([SOURCE], [SOURCE], previous, {}, [part], stamp, Path(directory))
        return result

    def test_two_daily_collections_keep_supported_start_and_are_idempotent(self):
        text = 'HR internship. Een leerzame stage vanaf februari 2027 voor minimaal vier maanden.'
        initial = self.cycle({'jobs': []}, text)
        original = deepcopy(initial['jobs'][0])
        for stamp in (STAMP, '2026-11-09T12:00:00+00:00', '2026-11-10T12:00:00+00:00'):
            result = self.cycle(initial, text, stamp)
            job = result['jobs'][0]
            self.assertEqual(job['intake']['published_start'], '2027-02')
            self.assertEqual(job['intake']['checked_at'], stamp)
            self.assertEqual(job['id'], original['id'])
            self.assertEqual(job['source_id'], original['source_id'])
            self.assertEqual(job['first_discovered_at'], original['first_discovered_at'])
            self.assertTrue(verified_job(job, stamp))
            self.assertEqual(self.cycle(result, text, stamp), result)
            initial = result

    def test_current_vacancy_supersedes_old_feed_even_without_application_form(self):
        previous = self.cycle({'jobs': []}, 'Stage vanaf februari 2027.')
        for form in (True, False):
            for page, expected in [('Startdatum: 1 maart 2027.', '2027-03-01'),
                                   ('Start in overleg.', None)]:
                result = self.cycle(previous, 'Stage vanaf februari 2027.', page_text=page, form=form)
                job = result['jobs'][0]
                self.assertEqual(job.get('intake', {}).get('published_start'), expected)
                self.assertEqual(job['status'], 'open' if form else 'unverified')

    def test_past_start_never_rolls_forward_and_month_without_year_stays_unknown(self):
        for text, expected, state in [
            ('Startdatum: 1 september 2026.', '2026-09-01', 'past-start'),
            ('Stage vanaf september 2026.', '2026-09', 'past-start'),
            ('Je kan per september starten.', 'september (year unspecified)', 'year-unconfirmed'),
            ('Starting on 2026-09-01.', '2026-09-01', 'past-start'),
        ]:
            with self.subTest(text=text):
                job = self.cycle({'jobs': []}, text)['jobs'][0]
                self.assertEqual(job['intake']['published_start'], expected)
                self.assertEqual(job['intake']['state'], state)
        self.assertEqual(extract_intake('Stage vanaf november 2026.', STAMP)['state'], 'documented-future-start')
        self.assertEqual(extract_intake('Stage vanaf november 2026.', '2026-12-01T12:00:00Z')['state'], 'past-start')

    def test_no_intake_invented_from_deadline_age_duration_or_invalid_date(self):
        for text in ['Published February 2027. Apply before September 2027.',
                     'Stage 3 maanden geleden. Duur 5 of 10 maanden.',
                     'Startdatum: 31 februari 2027.', 'Start in overleg.',
                     'Established in February 2027.', 'Applications start February 2027.',
                     'Solliciteren vanaf februari 2027.', 'Not starting February 2027.']:
            with self.subTest(text=text):
                self.assertIsNone(extract_intake(text, STAMP))
        proof = extract_intake('Startdatum februari 2027. Starting March 2027.', STAMP)
        self.assertEqual(proof['state'], 'conflicting-starts')
        self.assertEqual(proof['published_start'], '2027-02 / 2027-03')
        self.assertEqual(extract_intake('Stage vanaf februari 2027 of maart 2027.', STAMP)['state'],
                         'conflicting-starts')

    def test_incomplete_or_failed_inventory_preserves_observation_without_refreshing_it(self):
        previous = self.cycle({'jobs': []}, 'Stage vanaf februari 2027.')
        for status in ('partial', 'failed'):
            part = dict(report=dict(id=SOURCE['id'], status=status, records_inspected=0), jobs=[], closure_eligible=[])
            for stamp in ('2026-11-09T12:00:00+00:00', '2026-11-11T12:00:00+00:00'):
                with TemporaryDirectory() as directory:
                    result, _ = finalize([SOURCE], [SOURCE], previous, {}, [part], stamp, Path(directory))
                self.assertEqual(result['jobs'][0]['intake'], previous['jobs'][0]['intake'])
                self.assertEqual(result['jobs'][0].get('missing_count'), 0)
                if stamp.startswith('2026-11-11'):
                    self.assertFalse(verified_job(result['jobs'][0], stamp))

    def test_expired_deadline_closes_despite_future_intake(self):
        part = process_source(SOURCE, VacancyClient('Stage vanaf februari 2027.'), STAMP)
        part['jobs'][0]['valid_through'] = '2026-10-15'
        with TemporaryDirectory() as directory:
            result, _ = finalize([SOURCE], [SOURCE], {'jobs': []}, {}, [part], STAMP, Path(directory))
        job = result['jobs'][0]
        self.assertEqual(job['intake']['published_start'], '2027-02')
        self.assertEqual(job['status'], 'closed')
        self.assertFalse(verified_job(job, STAMP))

    def test_official_feed_intake_without_verification_does_not_open_vacancy(self):
        part = process_source(SOURCE, VacancyClient('Stage vanaf februari 2027.'), STAMP, verify=False)
        self.assertEqual(part['jobs'][0]['intake']['published_start'], '2027-02')
        self.assertEqual(part['jobs'][0]['status'], 'unverified')

    def test_recorded_utrecht_primary_evidence(self):
        vacancies = read(ROOT/'docs/utrecht-recovery-vacancies.json', {})['vacancies']
        for vacancy in vacancies:
            text = ' '.join(vacancy['date_evidence'])
            expected = vacancy['intake']['published_start']
            actual = extract_intake(text, STAMP)
            if expected == 'February 2027':
                self.assertEqual(actual['published_start'], '2027-02')
            elif expected == '2026-09-01':
                self.assertEqual(actual['state'], 'past-start')
            elif expected and 'year unspecified' in expected:
                self.assertEqual(actual['state'], 'year-unconfirmed')
            else:
                self.assertIsNone(actual)

    def test_complete_missing_inventory_keeps_history_but_unverifies(self):
        previous = self.cycle({'jobs': []}, 'Stage vanaf februari 2027.')
        part = dict(report=dict(id=SOURCE['id'], status='ok', explicit_empty=True), jobs=[], closure_eligible=[SOURCE['id']])
        with TemporaryDirectory() as directory:
            result, _ = finalize([SOURCE], [SOURCE], previous, {}, [part], STAMP, Path(directory))
        self.assertEqual(result['jobs'][0]['intake'], previous['jobs'][0]['intake'])
        self.assertEqual(result['jobs'][0]['status'], 'unverified')

    def test_published_324_records_ownership_policy_and_review_blocks_survive(self):
        prior = read(ROOT/'data/catalog.json', {})
        self.assertEqual(len(prior['jobs']), 324)
        # Replay at the publication timestamp so freshness does not introduce
        # legitimate changes unrelated to this regression.
        stamp = prior['last_attempt_at']
        with TemporaryDirectory() as directory:
            result, _ = finalize([], [], deepcopy(prior), {}, [], stamp, Path(directory))
        self.assertEqual([j['id'] for j in result['jobs']], [j['id'] for j in prior['jobs']])
        for old, current in zip(prior['jobs'], result['jobs']):
            for field in ('status', 'source_id', 'employer', 'first_discovered_at', 'intake',
                          'ownership', 'region_codes', 'review_note'):
                self.assertEqual(current.get(field), old.get(field), (old['id'], field))
            self.assertEqual(current.get('verification', {}).get('policy_version'),
                             old.get('verification', {}).get('policy_version'))
        blocked = [j for j in prior['jobs'] if j.get('review_note') and any(
            name in j['employer'].lower() for name in ('trunkrs', 'domino', 'var ', 'meerpaal'))]
        self.assertEqual(len(blocked), 2)
        opportunities = read(ROOT/'data/flevoland-opportunities.json', [])
        flv = [j for j in opportunities if j['employer'] in ('Van Amersfoort Racing', 'Meerpaal')]
        self.assertEqual(len(flv), 2)
        for candidate in flv:
            self.assertIsNone(candidate['catalog_id'])
            template = deepcopy(blocked[0])
            template.update(id=candidate['candidate_id'], employer=candidate['employer'],
                            source_id='test-' + candidate['candidate_id'],
                            source_posting_id=None, identity_aliases=[],
                            url=candidate['url'], apply_url=candidate['url'], valid_through=None)
            template['review_note'] = next(r['reason'] for r in read(ROOT/'data/listing-reviews.json', [])
                                           if r['url'] == candidate['url'])
            blocked.append(template)
        for day in ('08', '09'):
            stamp = f'2026-11-{day}T12:00:00+00:00'
            fresh = deepcopy(blocked)
            for job in fresh:
                job.update(status='open', link_status='verified', last_seen_at=stamp, last_verified_at=stamp,
                           intake=extract_intake('Startdatum: 1 september 2026.' if day == '08' else 'Startdatum: 1 februari 2027.', stamp),
                           verification=dict(state='verified', policy_version=2, checked_at=stamp))
            parts = [dict(report=dict(id=j['source_id'], status='partial', records_inspected=1),
                          jobs=[j], closure_eligible=[]) for j in fresh]
            with TemporaryDirectory() as directory:
                result, _ = finalize([], [], prior, {}, parts, stamp, Path(directory))
            by_id = {j['id']: j for j in result['jobs']}
            self.assertEqual(set(by_id), {j['id'] for j in prior['jobs']} | {j['id'] for j in blocked})
            for job in blocked:
                current = by_id[job['id']]
                self.assertFalse(verified_job(current, stamp))
                self.assertEqual(current['status'], 'unverified')
                self.assertEqual(current['review_note'], job['review_note'])
                self.assertEqual(current['source_id'], job['source_id'])
                self.assertEqual(current['verification']['policy_version'], 2)
            prior = result


if __name__ == '__main__':
    unittest.main()
