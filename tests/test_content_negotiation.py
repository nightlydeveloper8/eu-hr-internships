"""Document CMS fragments must not hide career links; API and robots types stay explicit."""
import json,unittest
from unittest.mock import patch
from urllib.error import URLError
from collector.adapters import Client,AGENT
from collector.runtime import BudgetClient,CollectionBudgetExceeded
from collector.eu_directory_discovery import SeedClient
from collector.universal import Document

class Response:
    def __init__(self,url,body):self.url=url;self.body=body;self.status=200
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):assert limit==20_000_000;return self.body
class Server:
    def __init__(self,robots=b'User-agent: *\nAllow: /'):self.calls=[];self.robots=robots
    def open(self,req,timeout):
        accept=req.get_header('Accept');self.calls.append((req.full_url,accept,req.get_header('User-agent'),req.get_method()))
        if req.full_url.endswith('/robots.txt'):body=self.robots
        elif 'application/json' in accept:body=json.dumps({'content':'CMS API fragment without global career navigation'}).encode()
        else:body=b'<a href="https://employer.recruitee.com">Careers</a>'
        return Response(req.full_url,body)

class NegotiationTests(unittest.TestCase):
    def test_html_document_exposes_navigation_instead_of_cms_fragment(self):
        server=Server();client=Client(delay=0)
        with patch('collector.adapters.build_opener',return_value=server):body,_,url=client.request('https://negotiation.test/careers')
        self.assertIn('text/html',server.calls[-1][1]);self.assertNotIn('application/json',server.calls[-1][1])
        self.assertEqual(Document(body,url).links[0][0],'https://employer.recruitee.com')
        self.assertEqual(server.calls[0][1],'text/plain');self.assertTrue(all(x[2]==AGENT and x[3]=='GET' for x in server.calls))
    def test_explicit_json_reader_keeps_json_representation(self):
        server=Server();client=Client(delay=0)
        with patch('collector.adapters.build_opener',return_value=server):result=client.json('https://negotiation.test/api/jobs')
        self.assertEqual(result,{'content':'CMS API fragment without global career navigation'})
        self.assertEqual(server.calls[-1][1],'application/json');self.assertEqual(server.calls[0][1],'text/plain')
    def test_budget_wrapper_forwards_types_and_counts_robots(self):
        from collector import runtime
        server=Server()
        with patch.dict(runtime._ROBOTS,{},clear=True),patch.dict(runtime._LAST,{},clear=True),patch('collector.adapters.build_opener',return_value=server):
            client=BudgetClient(seconds=5,max_requests=2,delay=0);client.json('https://negotiation.test/api/jobs')
            self.assertEqual(client.requests,2)
            with self.assertRaises(CollectionBudgetExceeded):client.request('https://negotiation.test/other')
        self.assertEqual([x[1] for x in server.calls],['text/plain','application/json'])
    def test_robots_disallow_still_stops_document_and_api_fetches(self):
        for as_json in [False,True]:
            server=Server(b'User-agent: *\nDisallow: /private');client=Client(delay=0)
            with patch('collector.adapters.build_opener',return_value=server):
                with self.assertRaisesRegex(ValueError,'robots.txt disallows'):
                    (client.json if as_json else client.request)('https://negotiation.test/private')
            self.assertEqual(len(server.calls),1)
    def test_reviewed_seed_scope_accepts_internal_plaintext_robots_only(self):
        from collector import runtime
        server=Server()
        with patch.dict(runtime._ROBOTS,{},clear=True),patch('collector.adapters.build_opener',return_value=server):
            client=SeedClient({'url':'https://seed.test/careers'});client.pause=lambda _:None
            client.request('https://seed.test/careers')
            with self.assertRaises(ValueError):client.request('https://other.test/careers')
        self.assertEqual(server.calls[0][1],'text/plain');self.assertNotIn('application/json',server.calls[-1][1])
    def test_modern_tls_fallback_preserves_selected_accept_and_bot_identity(self):
        opener=Server();opener.open=lambda *a,**k:(_ for _ in ()).throw(URLError('TLSV1_ALERT_INTERNAL_ERROR'))
        client=Client(delay=0)
        with patch('collector.adapters.build_opener',return_value=opener),patch('collector.tls_transport.request',return_value=(b'{}',200,'https://negotiation.test/api')) as fallback:
            client.request('https://negotiation.test/api',robots=False,accept='application/json')
        args=fallback.call_args.args;self.assertEqual(args[2]['Accept'],'application/json');self.assertEqual(args[2]['User-Agent'],AGENT)

if __name__=='__main__':unittest.main()
