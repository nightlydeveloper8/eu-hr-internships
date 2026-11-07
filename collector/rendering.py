"""Read public rendered recruiting pages, following only safe pagination controls."""
import json,os,re,threading,time
from urllib.parse import urlsplit,parse_qs
from .adapters import AGENT
from .classify import canonical_url
from .runtime import CollectionBudgetExceeded
_BROWSER_SLOTS=threading.BoundedSemaphore(2)
MORE=re.compile(r'^(?:load more|show more|more jobs|next|next page|see more|carica altro|mostra altr[ei]|successiv[ao]|volgende|meer vacatures|mehr (?:anzeigen|stellen)|weiter|suivant|voir plus|cargar más|siguiente|próxim[ao]|pokaż więcej|następna|visa fler|nästa)(?:\s.*)?$',re.I)
BLOCK=re.compile(r'captcha|verify (?:you are|that you are) human|access denied|just a moment|security verification',re.I)

class BrowserUnavailable(RuntimeError):pass

def cegid_inventory_search(target,payload,page_url):
    """Only the observed public Cegid inventory POST, never candidate operations."""
    parsed=urlsplit(target);query=parse_qs(parsed.query)
    if (parsed.scheme!='https' or parsed.netloc!='api.digitalrecruiters.com'
        or parsed.path!='/public/v1/careers-site/job-ads'
        or set(query)!={'domainName','limit','page','locale'}
        or query['domainName']!=[urlsplit(page_url).hostname]
        or any(len(values)!=1 for values in query.values())):return False
    try:
        if not (1<=int(query['limit'][0])<=100 and 1<=int(query['page'][0])<=1000):return False
        data=json.loads(payload)
        if not isinstance(data,dict) or set(data)!={'filters','coordinates'}:return False
        filters=data['filters'];coordinates=data['coordinates']
        if not isinstance(filters,dict) or set(filters)!={'customFieldMcqChoice'}:return False
        choices=filters['customFieldMcqChoice']
        if not isinstance(choices,list) or not 1<=len(choices)<=50 or not all(isinstance(v,str) and v.isdigit() for v in choices):return False
        expected=parse_qs(urlsplit(page_url).query).get('customFieldMcqChoice',[])
        if len(expected)!=1 or set(choices)!=set(expected[0].split(',')):return False
        return (isinstance(coordinates,dict) and set(coordinates)=={'lat','lng'}
            and all(type(v) in (int,float) for v in coordinates.values())
            and -90<=coordinates['lat']<=90 and -180<=coordinates['lng']<=180)
    except (ValueError,TypeError,KeyError):return False

def render_pages(url,client,allowed,limit=5,*,cegid_search=False,cegid_responses=None):
    """A fresh browser has no user cookies or credentials; no applications submitted."""
    canonical_url(url)
    if not client.permitted(url):raise ValueError('robots.txt disallows browser navigation')
    if not _BROWSER_SLOTS.acquire(timeout=max(.05,client.remaining())):raise CollectionBudgetExceeded('Browser queue exceeded budget')
    try:
        try:from playwright.sync_api import sync_playwright
        except ImportError as e:raise BrowserUnavailable('Playwright is not installed') from e
        snapshots=[];complete=True
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--disable-dev-shm-usage'])
            context=browser.new_context(user_agent='Mozilla/5.0 (compatible; '+AGENT+')',ignore_https_errors=False)
            page=context.new_page();page.set_default_timeout(4000)
            def route_request(route):
                req=route.request;host=urlsplit(req.url).hostname or ''
                read_search=(req.method=='POST' and req.resource_type in ('xhr','fetch') and bool(re.search(r'/(?:jobs|search|positions|postings)(?:[/?]|$)',urlsplit(req.url).path,re.I)) and not re.search(r'apply|candidate|login|submit|mutation',req.url+' '+(req.post_data or ''),re.I))
                if cegid_search and req.method=='POST' and req.resource_type in ('xhr','fetch'):
                    read_search=read_search or cegid_inventory_search(req.url,req.post_data,url)
                if (req.method not in ('GET','HEAD') and not read_search) or req.resource_type in ('image','font','media') or re.search(r'google-analytics|googletagmanager|doubleclick|facebook|linkedin',host):return route.abort()
                if req.is_navigation_request() or req.resource_type in ('xhr','fetch'):
                    try:
                        client.check()
                        if req.is_navigation_request() and not allowed(req.url):return route.abort()
                        if not client.permitted(req.url):return route.abort()
                        client.requests+=1
                    except Exception:return route.abort()
                return route.continue_()
            context.route('**/*',route_request)
            try:
                client.check()
                if cegid_search:
                    # Wait for the public search, not a DOM snapshot that can still
                    # say Loading while robots/throttle checks delay its request.
                    with page.expect_response(lambda r: r.request.method=='POST' and cegid_inventory_search(r.url,r.request.post_data,url),
                            timeout=min(60000,max(1000,int(client.remaining()*1000)))) as inventory:
                        response=page.goto(url,wait_until='domcontentloaded',timeout=min(20000,max(1000,int(client.remaining()*1000))))
                    search=inventory.value
                    if search.status!=200:raise ValueError('Cegid public inventory HTTP '+str(search.status))
                    data=search.json()
                    if cegid_responses is not None:cegid_responses.append(data)
                else:
                    response=page.goto(url,wait_until='domcontentloaded',timeout=min(20000,max(1000,int(client.remaining()*1000))))
                if response and response.status in (401,403,429):raise ValueError('Rendered page access restricted: '+str(response.status))
                try:page.wait_for_load_state('networkidle',timeout=min(4000,max(500,int(client.remaining()*1000))))
                except Exception:pass
                seen=set()
                for index in range(limit):
                    client.check();text=page.locator('body').inner_text(timeout=3000)
                    if BLOCK.search(text[:3000]):raise ValueError('Browser access challenge; no bypass attempted')
                    html=page.content();signature=hash(html)
                    if signature in seen:break
                    seen.add(signature);snapshots.append((page.url,html.encode()))
                    buttons=page.get_by_role('button',name=MORE).or_(page.get_by_role('link',name=MORE))
                    target=None
                    for n in range(min(buttons.count(),8)):
                        b=buttons.nth(n)
                        if b.is_visible() and b.is_enabled():target=b;break
                    if target is None:break
                    if index==limit-1:complete=False;break
                    target.click(timeout=min(4000,max(500,int(client.remaining()*1000))))
                    try:page.wait_for_load_state('networkidle',timeout=min(3000,max(500,int(client.remaining()*1000))))
                    except Exception:pass
            finally:context.close();browser.close()
        return snapshots,complete
    finally:_BROWSER_SLOTS.release()
