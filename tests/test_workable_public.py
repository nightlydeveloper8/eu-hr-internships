import json, unittest
from urllib.error import HTTPError
from collector.workable_public import workable_public_records
from collector.verification import _verify_vacancy
from collector.dynamic_ats import MissingDynamicForm

SOURCE=dict(id='test',employer='Example',board='example',adapter='workable-public',feed_url='https://www.workable.com/api/accounts/example?details=true',allowed_hosts=['www.workable.com','apply.workable.com'],enabled=False)
JOB=dict(shortcode='7EAEC1444E',title='HR Intern',city='Athens',country='Greece',description='Student HR internship',url='https://apply.workable.com/j/7EAEC1444E',application_url='https://apply.workable.com/j/7EAEC1444E/apply')

class Client:
    def __init__(self,data,final=None): self.data=data;self.final=final;self.calls=[]
    def request(self,url,**kwargs):
        self.calls.append((url,kwargs))
        return json.dumps(self.data).encode(),200,self.final or url

class WorkablePublicTests(unittest.TestCase):
    def test_public_feed_returns_inventory_not_form_proof(self):
        client=Client({'jobs':[JOB]})
        rows=workable_public_records(SOURCE,client)
        self.assertEqual(rows[0]['external_id'],'7EAEC1444E')
        self.assertEqual(rows[0]['apply_url'],JOB['url'])
        self.assertEqual(rows[0]['observed_application_url'],JOB['application_url'])
        self.assertFalse(rows.stats['closure_complete'])
        self.assertEqual(client.calls,[(SOURCE['feed_url'],{'accept':'application/json'})])
        self.assertFalse(hasattr(client,'redirect_scope_allowed'))
    def test_duplicate_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):workable_public_records(SOURCE,Client({'jobs':[JOB,JOB]}))
    def test_different_posting_and_external_hosts_fail_closed(self):
        for field,value in [('application_url','https://apply.workable.com/j/3F368EAC02/apply'),('url','https://evil.test/j/7EAEC1444E'),('url','https://apply.workable.com/j/7EAEC1444E?utm_source=other')]:
            with self.subTest(field=field):
                with self.assertRaises(ValueError): workable_public_records(SOURCE,Client({'jobs':[dict(JOB,**{field:value})]}))
    def test_feed_scope_and_redirect_fail_closed(self):
        with self.assertRaises(ValueError):workable_public_records(dict(SOURCE,feed_url='https://www.workable.com/api/accounts/other?details=true'),Client({'jobs':[]}))
        with self.assertRaisesRegex(ValueError,'redirected'):workable_public_records(SOURCE,Client({'jobs':[]},'https://www.workable.com/api/accounts/other?details=true'))
    def test_only_exact_observed_redirect_is_permitted(self):
        class Redirect(Client):
            requests=0
            def check(self): pass
            def request(self,url,**kwargs):
                good='https://apply.workable.com/api/v1/widget/accounts/example?details=true'
                bad='https://apply.workable.com/api/v1/widget/accounts/other?details=true'
                assert self.redirect_scope_allowed(good)
                assert not self.redirect_scope_allowed(bad)
                assert not self.redirect_scope_allowed(good)
                return b'{"jobs":[]}',200,good
        client=Redirect({})
        self.assertEqual(len(workable_public_records(SOURCE,client)),0)
        self.assertEqual(client.requests,1)
    def test_missing_payload_and_title_fail_closed(self):
        for data in ({'jobs':None},{'jobs':[dict(JOB,title='')]},{'jobs':[],'next_page':'2'}):
            with self.assertRaises(ValueError):workable_public_records(SOURCE,Client(data))
    def test_rate_limit_is_propagated_without_retry(self):
        class Limited(Client):
            def request(self,url,**kwargs):
                self.calls.append(url)
                raise HTTPError(url,429,'Too Many Requests',{},None)
        client=Limited({})
        with self.assertRaises(HTTPError):workable_public_records(SOURCE,client)
        self.assertEqual(len(client.calls),1)
    def test_inventory_alone_does_not_verify_application(self):
        row=workable_public_records(SOURCE,Client({'jobs':[JOB]}))[0]
        class NoForm:
            def request(self,url,**kwargs):return b'<h1>HR Intern</h1>',200,url
        with self.assertRaises(MissingDynamicForm):
            _verify_vacancy(row,SOURCE,NoForm(),'2026-11-21T22:00:00+00:00')

if __name__=='__main__':unittest.main()
