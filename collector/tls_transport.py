"""Modern TLS transport for systems with an older Python SSL library.

Called only by Client.request, after its normal robots and delay checks. This
does not change certificates, authentication, access restrictions or robots.
"""
from urllib.error import HTTPError


def request(url,method,headers,timeout):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context=p.request.new_context(ignore_https_errors=False,extra_http_headers=headers)
        try:
            response=context.fetch(url,method=method,timeout=max(1,int(timeout*1000)),max_redirects=10)
            if response.status>=400:
                raise HTTPError(response.url,response.status,response.status_text,response.headers,None)
            if not response.url.startswith('https://'):raise ValueError('Unsafe redirect')
            body=response.body()
            if len(body)>20_000_000:raise ValueError('Response exceeds size limit')
            return body,response.status,response.url
        finally:context.dispose()
