"""Browser smoke check of all researched provinces and EU/country filters."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse, json, threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/utrecht-ui-verification.json')
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'dist')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port);errors=[];results=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            for slug,count in [('friesland',18),('groningen',10),('drenthe',12),('utrecht',26)]:
                for width in [1280,390]:
                    page.set_viewport_size({'width':width,'height':900})
                    page.goto(base+'/'+slug+'.html')
                    page.wait_for_function("document.querySelector('[id$=\"-summary\"]').textContent.includes('Updated')")
                    assert page.locator('#'+slug+'-municipalities tr').count()==count
                    page.locator('#'+slug+'-size').select_option('all')
                    page.locator('#'+slug+'-search').fill('NoSuchEmployer987654321')
                    assert '0 of 0' in page.locator('#'+slug+'-employer-count').inner_text()
                    page.locator('#'+slug+'-search').fill('')
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    results.append({'province':slug,'width':width,'summary':page.locator('#'+slug+'-summary').inner_text(),'municipalities':count})
                    if slug=='utrecht':
                        verified=page.locator('#utrecht-jobs article').count()
                        page.locator('#utrecht-unverified').check()
                        assert page.locator('#utrecht-jobs article').count()>=verified
                        page.locator('#utrecht-job-search').fill('NoSuchInternship987654321')
                        assert page.locator('#utrecht-jobs article').count()==0
                        page.locator('#utrecht-job-search').fill('')
                        page.locator('#utrecht-ad-language').select_option('en')
                        for text in page.locator('#utrecht-jobs article').all_inner_texts():assert 'Advertisement: English' in text
                        page.locator('#utrecht-ad-language').select_option('')
                        page.locator('#utrecht-unverified').uncheck()
                        (ROOT/'.staging/utrecht').mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(ROOT/'.staging/utrecht'/('ui-'+str(width)+'.png')),full_page=True)
            page.set_viewport_size({'width':1280,'height':900});page.goto(base)
            page.wait_for_function("document.getElementById('jobs').getAttribute('aria-busy')==='false'")
            assert page.locator('#country option').count()==28
            page.locator('#include-unverified').check();total=int(page.locator('#result-count').inner_text());assert total>0
            page.locator('#country').select_option('NL');page.locator('#region').select_option('NL13')
            regional=int(page.locator('#result-count').inner_text())
            page.locator('#country').select_option('PT');assert int(page.locator('#result-count').inner_text())<=total
            page.locator('#reset').click();page.locator('#include-unverified').check();assert int(page.locator('#result-count').inner_text())==total
            page.set_viewport_size({'width':390,'height':844});page.locator('#filter-toggle').click();assert page.locator('#country').is_visible()
            page.locator('#filters-done').click();assert not page.locator('#country').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1');assert not errors,errors
            results.append({'catalog_total_including_unverified':total,'drenthe_including_unverified':regional,'country_options':27,'errors':errors})
            browser.close()
    finally:server.shutdown()
    args.output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print('UI OK: four provinces desktop/mobile, municipal rows, employer search, EU/country/region filters, mobile filters, no page errors or overflow')
if __name__=='__main__':main()
