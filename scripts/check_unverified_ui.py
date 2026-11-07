"""Smoke-check verification views, counts and explanatory copy with deterministic data."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import copy,json,threading
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    catalog=json.loads((ROOT/'data/catalog.json').read_text())
    base=copy.deepcopy(catalog['jobs'][0]);stamp=datetime.now(timezone.utc).isoformat()
    base.update(id='verified-nl',title='Alpha HR Internship',employer='Alpha',city='Almere',countries=['NL'],country='NL',region_codes=['NL23'],categories=['hr-generalist'],category='hr-generalist',internship_type='internship',status='open',link_status='verified',verification={'state':'verified','policy_version':2,'checked_at':stamp},last_verified_at=stamp,workplace_languages=[],language_requirements={'requirements_status':'unknown','english_support':'unknown','english_sufficiency':'unknown'},url='https://example.org/jobs/1',apply_url='https://example.org/jobs/1')
    unverified=dict(base,id='unverified-nl',title='Beta HR Internship',employer='Beta',status='unverified',verification={'state':'incomplete','policy_version':2,'reason':'TypeError: sequence item 4 expected str instance, NoneType found'})
    catalog['jobs']=[base,unverified,dict(base,id='closed',status='closed'),dict(unverified,id='unverified-pt',title='Gamma Working Student',employer='Gamma',country='PT',countries=['PT'],region_codes=[],internship_type='working-student'),dict(base,id='verified-pt',title='Delta Traineeship',employer='Delta',country='PT',countries=['PT'],region_codes=[],internship_type='traineeship')]
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port);errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda error:errors.append(str(error)));page.route('**/data/catalog.json',lambda route:route.fulfill(json=catalog))
            page.goto(url);page.wait_for_function("() => document.getElementById('jobs').getAttribute('aria-busy')==='false'")
            assert page.locator('#result-count').inner_text()=='2'
            assert page.locator('#data-notice').is_hidden()
            assert page.locator('#collection-status').is_visible()
            page.locator('#collection-status summary').click();assert 'Source checks:' in page.locator('#collection-status-detail').inner_text()
            page.locator('#source-status').click();assert page.locator('#coverage-dialog').is_visible();page.locator('#close-dialog').click()
            assert page.locator('#verified-view-count').inner_text()=='(2)'
            assert page.locator('#unverified-view-count').inner_text()=='(4)'
            assert '5 archived records' in page.locator('#catalog-counts').inner_text()
            assert not page.locator('#unverified-notice').is_visible()
            page.locator('#unverified-view').focus();page.keyboard.press('Enter')
            assert page.locator('#result-count').inner_text()=='4'
            assert page.locator('#include-unverified').is_checked()
            assert page.locator('#unverified-view').get_attribute('aria-pressed')=='true'
            assert page.locator('#unverified-notice').is_visible()
            assert 'not confirmed closed' in page.locator('#unverified-notice').inner_text()
            assert '2 internships, 1 working-student role and 1 traineeship' in page.locator('#verification-counts').inner_text()
            assert not page.locator('#jobs').inner_text().find('TypeError')>=0
            assert 'unverified=true' in page.url
            page.locator('#country').select_option('NL');page.locator('#type').select_option('internship');assert page.locator('#result-count').inner_text()=='2'
            page.locator('#verified-view').click();assert page.locator('#result-count').inner_text()=='1';assert not page.locator('#include-unverified').is_checked()
            page.locator('#include-unverified').check();assert page.locator('#result-count').inner_text()=='2';assert page.locator('#unverified-view').get_attribute('aria-pressed')=='true'
            page.locator('#reset').click();assert page.locator('#result-count').inner_text()=='2';assert not page.locator('#unverified-notice').is_visible()
            page.goto(url+'/?unverified=true&country=NL');page.wait_for_function("() => document.getElementById('jobs').getAttribute('aria-busy')==='false'");assert page.locator('#result-count').inner_text()=='2';assert page.locator('#unverified-view').get_attribute('aria-pressed')=='true'
            page.set_viewport_size({'width':390,'height':844});assert page.locator('#unverified-view').is_visible();assert page.locator('#unverified-notice').is_visible();assert page.evaluate('() => document.documentElement.scrollWidth <= innerWidth+1')
            page.locator('#verified-view').click();assert page.locator('#result-count').inner_text()=='1';assert not page.locator('#unverified-notice').is_visible()
            catalog['jobs']=[dict(base,id='many-v1'),dict(base,id='many-v2',internship_type='working-student')]+[dict(unverified,id='many-'+str(i)) for i in range(25)]+[dict(base,id='many-closed',status='closed')]
            page.set_viewport_size({'width':1280,'height':900});page.goto(url+'/?unverified=true');page.wait_for_function("() => document.getElementById('jobs').getAttribute('aria-busy')==='false'")
            assert page.locator('#result-count').inner_text()=='27'
            assert page.locator('#jobs article').count()==20
            assert 'Showing 20 of 27' in page.locator('#result-pagination').inner_text()
            page.locator('#show-all').click();assert page.locator('#jobs article').count()==27
            assert page.locator('#show-all').is_hidden();assert page.locator('#load-more').is_hidden()
            assert 'Showing 27 of 27' in page.locator('#result-pagination').inner_text()
            assert not errors,errors;browser.close()
    finally:server.shutdown()
    print('UI OK: verification views/checkbox/URL/reset sync, type and status counts, composed filters, closed exclusions, plain explanations, keyboard, desktop/mobile, coverage disclosure, show-all pagination, no page errors or overflow')
if __name__=='__main__':main()
