"""Offline regression tests for approved, same-posting Recruitee XML records."""
import unittest
from html import escape

from collector.classify import classify_role
from collector.public_feeds import recruitee_records


FEED = 'https://careers.example.org/api/feeds/offers.xml'
VACANCY = 'https://careers.example.org/o/internship-people-organisation-1'
APPLY = VACANCY + '/c/new'


def xml(*, apply=APPLY, identifier='2822573', title='Internship People & Organisation'):
    return (f'<offers><offer><id>{identifier}</id><title>{escape(title)}</title>'
            '<city>Delft</city><country_code>NL</country_code>'
            '<description>Support the Human Resources team and HR ServiceDesk.</description>'
            f'<careers_url>{escape(VACANCY)}</careers_url><apply_url>{escape(apply)}</apply_url>'
            '</offer></offers>').encode()


def source(**kw):
    return dict(id='staging-company-nl', adapter='recruitee',
                employer='Example Operations B.V.',
                feed_format='recruitee-public-xml', application_check='recruitee-linked',
                allowed_hosts=['careers.example.org'], feed_url=FEED, target_countries=['NL'],
                **kw)


class FakeClient:
    def __init__(self,body):
        self.body=body
        self.calls=[]
    def request(self,url):
        self.calls.append(url)
        return self.body,200,url


class RecruiteeXMLTests(unittest.TestCase):
    def test_official_feed_maps_exact_published_apply_id_without_closure(self):
        client=FakeClient(xml())
        records=recruitee_records(source(),client)
        self.assertEqual(client.calls,[FEED])
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['external_id'],'2822573')
        self.assertEqual(records[0]['posting_identifier'],'2822573')
        self.assertEqual(records[0]['observed_application_url'],APPLY)
        self.assertEqual(records[0]['inventory_evidence'],'current-employer-feed')
        self.assertEqual(records[0]['country'],'NL')
        self.assertEqual(classify_role(records[0]['title'],records[0]['text'])['internship_type'],'internship')
        self.assertFalse(records.stats['closure_complete'])
        self.assertFalse(records.stats['complete'])

    def test_repeated_same_feed_is_stable(self):
        a=recruitee_records(source(),FakeClient(xml()))
        b=recruitee_records(source(),FakeClient(xml()))
        self.assertEqual([r['external_id'] for r in a],[r['external_id'] for r in b])
        self.assertEqual([r['observed_application_url'] for r in a],[r['observed_application_url'] for r in b])

    def test_official_apply_cannot_point_to_other_position(self):
        for apply in (VACANCY.replace('1','2')+'/c/new',
                      VACANCY+'/c/new?ref=unreviewed',
                      'https://evil.example.com/o/internship-people-organisation-1/c/new',
                      VACANCY):
            with self.subTest(apply=apply):
                with self.assertRaises(ValueError):
                    recruitee_records(source(),FakeClient(xml(apply=apply)))

    def test_no_invented_apply_link(self):
        with self.assertRaises(ValueError):
            recruitee_records(source(),FakeClient(xml(apply='')))

    def test_duplicated_ids_fail_closed(self):
        one=xml()[len(b'<offers>'):-len(b'</offers>')]
        with self.assertRaises(ValueError):
            recruitee_records(source(),FakeClient(b'<offers>'+one+one+b'</offers>'))

    def test_doctype_rejected(self):
        with self.assertRaises(ValueError):
            recruitee_records(source(),FakeClient(b'<!DOCTYPE offers SYSTEM "fake"><offers/>'))

    def test_hr_signal_required_for_people_organisation(self):
        self.assertIsNone(classify_role('Internship People & Organisation','Organize art exhibitions.'))
        self.assertIsNotNone(classify_role('Internship People & Organisation',
                                          'Support the Human Resources team.'))

    def test_existing_json_recruitee_path_stays_unaffected(self):
        import json
        payload=json.dumps({'offers':[{'id':12,'status':'published',
                                      'title':'HR Internship','careers_url':VACANCY,
                                      'description':'Human Resources onboarding','country_code':'NL',
                                      'careers_apply_url':APPLY}]}).encode()
        client=FakeClient(payload)
        cfg=source()
        cfg.pop('feed_format')
        cfg['application_check']='recruitee-linked'
        rec=recruitee_records(cfg,client)
        self.assertEqual(rec[0]['posting_identifier'],'12')


if __name__=='__main__':unittest.main()
