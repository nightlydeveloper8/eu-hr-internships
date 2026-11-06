"""Modern TLS transport for systems with an older Python SSL library.

Called only by Client.request, after its normal robots and delay checks. This
does not change certificates, authentication, access restrictions or robots.
"""
from urllib.error import HTTPError


def request(url,method,headers,timeout,client=None,robots=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context=p.request.new_context(ignore_https_errors=False,extra_http_headers=headers)
        try:
            # No automatic redirects: each destination goes through Client and robots.
            response=context.fetch(url,method=method,timeout=max(1,int(timeout*1000)),max_redirects=0)
            if response.status in (301,302,303,307,308):
                raise ValueError('TLS transport redirect requires review; no unchecked navigation')
            if response.status>=400:
                raise HTTPError(response.url,response.status,response.status_text,response.headers,None)
            if not response.url.startswith('https://'):raise ValueError('Unsafe redirect')
            body=response.body()
            if len(body)>20_000_000:raise ValueError('Response exceeds size limit')
            return body,response.status,response.url
        finally:context.dispose()
