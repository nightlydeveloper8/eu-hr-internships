"""Optional local browser smoke test; uses the existing Playwright dependency."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import copy,json,threading
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url='http://127.0.0.1:'+str(server.server_port)
    errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':1280,'height':900})
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(url);page.wait_for_function("document.getElementById('jobs').getAttribute('aria-busy')==='false'")
            assert page.locator('#result-count').inner_text()=='0','Legacy HEAD flags must not appear verified'
            page.locator('#coverage-nav').click()
            assert '0 verified HR internships' in page.locator('#quality-summary').inner_text()
            page.locator('#close-dialog').click()
            page.locator('#include-unverified').check()
            assert int(page.locator('#result-count').inner_text())>0
            page.locator('#workplace-language').select_option('unknown')
            assert int(page.locator('#result-count').inner_text())>0
            catalog=json.loads((ROOT/'data/catalog.json').read_text());job=copy.deepcopy(catalog['jobs'][0])
            job.update(status='open',link_status='verified',verification={'state':'verified','policy_version':2,'checked_at':datetime.now(timezone.utc).isoformat(),'reason':'same-vacancy-applicant-form'},last_verified_at=datetime.now(timezone.utc).isoformat(),countries=['FR'],country='FR',categories=['employee-relations'],category='employee-relations',workplace_languages=[{'code':'en','confidence':'confirmed','requirement':'working','evidence':'We work in English.'}],language_requirements={'requirements_status':'explicit','english_support':'documented','english_sufficiency':'unknown'})
            catalog['jobs']=[job];catalog['categories']['employee-relations']='Employee & labour relations'
            page.route('**/data/catalog.json',lambda route:route.fulfill(json=catalog))
            page.goto(url);page.wait_for_function("document.getElementById('jobs').getAttribute('aria-busy')==='false'")
            page.locator('#country').select_option('FR');page.locator('#category').select_option('employee-relations');page.locator('#workplace-language').select_option('en');page.locator('#english').check()
            assert page.locator('#result-count').inner_text()=='1'
            page.locator('#english-only').check();assert page.locator('#result-count').inner_text()=='0'
            page.locator('#english-only').uncheck();page.locator('.job-details summary').click()
            assert page.locator('.job-details').inner_text().find('English alone')>=0
            assert page.locator('.apply-link').get_attribute('href')==job['apply_url']
            page.screenshot(path='/tmp/people-placement-evidence-desktop.png',full_page=True)
            page.set_viewport_size({'width':390,'height':844});page.locator('#filter-toggle').click()
            assert page.locator('#workplace-language').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),'Mobile horizontal overflow'
            page.screenshot(path='/tmp/people-placement-evidence-mobile.png',full_page=True)
            assert not errors,errors
            browser.close()
    finally:server.shutdown()
    print('UI OK: legacy migration, unknown languages, country/specialisation/language composition, English sufficiency, original link, desktop/mobile, no page errors')
if __name__=='__main__':main()
