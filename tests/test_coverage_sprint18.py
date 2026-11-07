"""Real official snapshots plus failure mutations; no network or live evidence refresh."""
import gzip
import hashlib
import json
import unittest
from unittest.mock import patch

from collector.adapters import collect
from collector.applications import ApplicationClosed
from collector.pipeline import reconcile
from collector.verification import applicant_form, verify_vacancy
from scripts.coverage_sprint18 import FIXTURES
from scripts.replay_sprint18 import Replay, legacy_applicant_form, run


class FormSemanticsTests(unittest.TestCase):
    def test_boolean_attributes_and_semantic_ids(self):
        body = b'''<form id="application" novalidate>
          <input id="first_name" required><input id="email" required>
          <input id="resume" type="file"><button type="submit">Apply</button></form>'''
        self.assertTrue(applicant_form(body))
        with self.assertRaises(TypeError):
            legacy_applicant_form(body)
        self.assertFalse(applicant_form(body.replace(b'id="application"', b'id="newsletter"').replace(b'<input id="resume" type="file">', b'')))
        self.assertFalse(applicant_form(body.replace(b'id="email"', b'id="email" disabled')))
        self.assertFalse(applicant_form(body.replace(b'type="submit"', b'type="submit" disabled')))

    def test_autocomplete_and_accessible_labels(self):
        body = b'''<form id="application"><input autocomplete="given-name">
            <input aria-label="Email"><button type="submit">Apply</button></form>'''
        self.assertTrue(applicant_form(body))
        self.assertFalse(applicant_form(body.replace(b'aria-label="Email"', b'aria-label="Phone"')))

    def test_fields_cannot_be_combined_across_forms(self):
        self.assertFalse(applicant_form(b'''<form id="application"><input id="first_name">
            <button>Apply</button></form><form id="newsletter"><input id="email"><button>Subscribe</button></form>'''))


class RealCoverageTests(unittest.TestCase):
    def greenhouse(self):
        return Replay(FIXTURES/'hunter-douglas-talent-programs/capture.json')

    def test_full_before_after_two_collections_preserve_catalog(self):
        report = run()
        self.assertEqual((report['verified_before'], report['verified_after']), (0, 1))
        self.assertEqual(report['newly_discovered_hr'], 0)
        live=next(r['fresh_live_confirmation'] for r in report['rows'] if 'fresh_live_confirmation' in r)
        self.assertEqual(len(live['proofs']),1)
        self.assertEqual(live['proofs'][0]['inventory'],'current-employer-feed')
        inventory = report['inventory_replay']
        self.assertEqual((inventory['before_report']['status'], inventory['after_report']['status']), ('partial', 'ok'))
        self.assertEqual(inventory['global_after']['open']-inventory['global_before']['open'], 1)
        self.assertTrue(inventory['two_collections_idempotent'])
        self.assertTrue(inventory['identities_and_existing_open_preserved'])

    def test_current_title_deadline_redirect_challenge_and_form_required(self):
        client = self.greenhouse()
        data = client.payload
        body, status, final = client.request(data['record']['url'])
        invalid = [body.replace(data['record']['title'].encode(), b'Software Intern'),
                   b'<h1>'+data['record']['title'].encode()+b'</h1>',
                   b'<h1>'+data['record']['title'].encode()+b'</h1>Verify you are human']
        for changed in invalid:
            with self.subTest(changed=changed[:80]), patch.object(client, 'request', return_value=(changed,status,final)):
                with self.assertRaises(ValueError):
                    verify_vacancy(data['record'],data['source'],client,data['stamp'])
        expired = b'<script type="application/ld+json">'+json.dumps(dict(
            **{'@type':'JobPosting'},title=data['record']['title'],validThrough='2020-01-01')).encode()+b'</script>'
        with patch.object(client,'request',return_value=(body+expired,status,final)):
            with self.assertRaises(ApplicationClosed):
                verify_vacancy(data['record'],data['source'],client,data['stamp'])
        with patch.object(client,'request',return_value=(body,status,final+'/different')):
            with self.assertRaisesRegex(ValueError,'redirected'):
                verify_vacancy(data['record'],data['source'],client,data['stamp'])

    def test_incomplete_inventory_page_is_rejected(self):
        client = self.greenhouse()
        url = next(r['url'] for r in client.payload['responses'] if '/jobs?content=true' in r['url'])
        listing = client.json(url)
        listing['jobs'] = listing['jobs'][:1]
        with patch.object(client,'json',return_value=listing):
            with self.assertRaisesRegex(ValueError,'Incomplete Greenhouse'):
                collect(client.payload['source'],client)

    def test_cache_alone_never_refreshes_verification(self):
        client = self.greenhouse()
        data = client.payload
        with patch.object(client,'request',side_effect=ValueError('robots.txt disallows current read')) as request:
            with self.assertRaisesRegex(ValueError,'robots'):
                verify_vacancy(dict(data['record'],_text_observation={'kind':'cache'}),data['source'],client,data['stamp'])
            request.assert_called_once()

    def test_closed_legacy_is_not_reopened_by_absence(self):
        old = dict(id='legacy',source_id='test',url='https://example.org/jobs/123',status='closed',first_discovered_at='2020-01-01')
        self.assertEqual(reconcile([old],[],{'test'},'2026-11-07T12:00:00+00:00'),[old])

    def test_shortlist_and_capture_scope_and_provenance(self):
        selection = json.loads((FIXTURES.parents[2]/'docs/coverage-sprint18/shortlist.json').read_text())
        self.assertEqual(len(selection['shortlist']),25)
        batch = {r['company_id'] for r in selection['shortlist'] if r['batch']}
        self.assertEqual(batch, {p.parent.name for p in FIXTURES.glob('*/capture.json')})
        for path in FIXTURES.glob('*/capture.json'):
            data = json.loads(path.read_text())
            confirmation=path.parent/'confirmation/result.json'
            extra=json.loads(confirmation.read_text()) if confirmation.exists() else {'requests':0}
            self.assertLessEqual(data['requests']+extra['requests'],8)
            for response in data['responses']:
                body = gzip.decompress((path.parent/response['file']).read_bytes())
                self.assertEqual(hashlib.sha256(body).hexdigest(),response['sha256'])
        self.assertFalse(batch & {r['company_id'] for r in selection['excluded']})
