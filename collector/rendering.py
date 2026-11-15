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

def unigarant_inventory_search(target,payload,page_url):
    """Observed public vacancy pagination, with exactly one numeric form field."""
    target=urlsplit(target);page=urlsplit(page_url)
    if (target.scheme!='https' or target.netloc!='werkenbijunigarant.nl'
        or target.path!='/vacatures-ajax' or target.query or target.fragment
        or page.scheme!='https' or page.netloc!=target.netloc
        or page.path.rstrip('/')!='/vacatures' or page.query):return False
    return isinstance(payload,str) and bool(re.fullmatch(
        r'--(?P<boundary>[-A-Za-z0-9]+)\r\nContent-Disposition: form-data; name="page"\r\n\r\n'
        r'[1-9]\d{0,2}\r\n--(?P=boundary)--\r\n',payload))

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

def render_pages(url,client,allowed,limit=5,*,cegid_search=False,cegid_responses=None,unigarant_search=False,index_error_pattern=None,unigarant_responses=None,application_read=False,application_toggle=False,metrics=None):
    """A fresh browser has no user cookies or credentials; no applications submitted."""
    if application_read and (cegid_search or unigarant_search):
        raise ValueError('Application reads cannot enable inventory POSTs')
    metrics = metrics if metrics is not None else {}
    metrics.update(browser_requests=0, blocked_requests=0,browser_bytes=0,suppressed_resources=0)
    canonical_url(url)
    if not client.permitted(url):raise ValueError('robots.txt disallows browser navigation')
    if not _BROWSER_SLOTS.acquire(timeout=max(.05,client.remaining())):raise CollectionBudgetExceeded('Browser queue exceeded budget')
    try:
        try:from playwright.sync_api import sync_playwright
        except ImportError as e:raise BrowserUnavailable('Playwright is not installed') from e
        snapshots=[];complete=True
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--disable-dev-shm-usage'],
                **({'timeout':min(20000,max(50,int(client.remaining()*1000)))} if application_read else {}))
            context=browser.new_context(user_agent='Mozilla/5.0 (compatible; '+AGENT+')',ignore_https_errors=False,
                **({'service_workers':'block'} if application_read else {}))
            page=context.new_page();page.set_default_timeout(4000)
            denied=[]
            def strict_route(route):
                req=route.request
                # No search POST exception in application mode. Every resource,
                # including scripts, styles and frames, uses the existing budget.
                if req.method not in ('GET','HEAD'):
                    metrics['blocked_requests']+=1
                    denied.append('non-read-method');return route.abort()
                if req.resource_type in ('image','font','media') or re.search(r'google-analytics|googletagmanager|doubleclick|facebook|linkedin|^analytics\.',urlsplit(req.url).hostname or ''):
                    metrics['suppressed_resources']+=1
                    return route.abort()
                try:
                    canonical_url(req.url)
                    if 'authorization' in req.headers:raise ValueError('authentication-excluded')
                    if not allowed(req.url):raise ValueError('unapproved-host-or-navigation: '+urlsplit(req.url).netloc+urlsplit(req.url).path)
                    if req.is_navigation_request() and canonical_url(req.url)!=canonical_url(url):raise ValueError('application-navigation-or-redirect')
                    if re.search(r'/(?:login|signin|oauth|authenticate)(?:/|$)',urlsplit(req.url).path,re.I):raise ValueError('authentication-excluded')
                    if not client.permitted(req.url):raise ValueError('robots.txt disallows browser resource')
                    from .runtime import host_lock
                    host=urlsplit(req.url).netloc
                    lock=host_lock(host)
                    if not lock.acquire(timeout=client.remaining()):raise CollectionBudgetExceeded('Dynamic host queue exceeded budget')
                    try:
                        client.check()
                        client.pause(max(0,client.host_delays.get(host,client.delay)-(time.monotonic()-client.last.get(host,0))))
                        client.check();client.last[host]=time.monotonic();client.requests+=1
                        metrics['browser_requests']+=1
                        # Playwright route handlers do not intercept every redirect
                        # hop. Fetch with zero redirects, then fulfill the same
                        # browser request; never let Chromium follow unseen hosts.
                        response=route.fetch(max_redirects=0,max_retries=0,
                            timeout=max(50,int(client.remaining()*1000)))
                        try:
                            if not 200<=response.status<300:raise ValueError('Dynamic resource HTTP '+str(response.status)+'; redirects excluded')
                            data=response.body();metrics['browser_bytes']+=len(data)
                            if metrics['browser_bytes']>20_000_000:raise ValueError('Dynamic resource memory budget exceeded')
                            client.check()
                            return route.fulfill(response=response,body=data)
                        finally:response.dispose()
                    finally:lock.release()
                except Exception as exc:
                    metrics['blocked_requests']+=1;denied.append(str(exc))
                    metrics['denied']=denied[:8]
                    return route.abort()

            def route_request(route):
                req=route.request;host=urlsplit(req.url).hostname or ''
                read_search=(req.method=='POST' and req.resource_type in ('xhr','fetch') and bool(re.search(r'/(?:jobs|search|positions|postings)(?:[/?]|$)',urlsplit(req.url).path,re.I)) and not re.search(r'apply|candidate|login|submit|mutation',req.url+' '+(req.post_data or ''),re.I))
                if cegid_search and req.method=='POST' and req.resource_type in ('xhr','fetch'):
                    read_search=read_search or cegid_inventory_search(req.url,req.post_data,url)
                if unigarant_search and req.method=='POST' and req.resource_type in ('xhr','fetch'):
                    read_search=read_search or unigarant_inventory_search(req.url,req.post_data,url)
                if (req.method not in ('GET','HEAD') and not read_search) or req.resource_type in ('image','font','media') or re.search(r'google-analytics|googletagmanager|doubleclick|facebook|linkedin',host):return route.abort()
                if req.is_navigation_request() or req.resource_type in ('xhr','fetch'):
                    try:
                        client.check()
                        if req.is_navigation_request() and not allowed(req.url):return route.abort()
                        if not client.permitted(req.url):return route.abort()
                        client.requests+=1
                    except Exception:return route.abort()
                return route.continue_()
            context.route('**/*',strict_route if application_read else route_request)
            if application_read:
                context.route_web_socket('**/*',lambda socket: socket.close())
                page.on('response',lambda response: denied.append('HTTP '+str(response.status)) if response.status>=400 else None)
            try:
                client.check()
                if cegid_search or unigarant_search:
                    # Wait for the public search, not a DOM snapshot that can still
                    # say Loading while robots/throttle checks delay its request.
                    search_check=cegid_inventory_search if cegid_search else unigarant_inventory_search
                    with page.expect_response(lambda r: r.request.method=='POST' and search_check(r.url,r.request.post_data,url),
                            timeout=min(60000,max(1000,int(client.remaining()*1000)))) as inventory:
                        response=page.goto(url,wait_until='domcontentloaded',timeout=min(20000,max(1000,int(client.remaining()*1000))))
                    search=inventory.value
                    if search.status not in ((200,202) if unigarant_search else (200,)):
                        raise ValueError('Public inventory HTTP '+str(search.status))
                    if unigarant_search:
                        data=search.json()
                        if (not isinstance(data,dict) or data.get('success') is not True
                            or type(data.get('total')) is not int or data['total']<0
                            or not isinstance(data.get('vacancies'),list)):
                            raise ValueError('Unigarant public inventory success/count/records unavailable')
                        if unigarant_responses is not None:unigarant_responses.append(data)
                    if cegid_search:
                        data=search.json()
                        if cegid_responses is not None:cegid_responses.append(data)
                else:
                    response=page.goto(url,wait_until='domcontentloaded',timeout=min(20000,max(1000,int(client.remaining()*1000))))
                if response and response.status in (401,403,429):raise ValueError('Rendered page access restricted: '+str(response.status))
                try:page.wait_for_load_state('networkidle',timeout=min(4000,max(500,int(client.remaining()*1000))))
                except Exception:pass
                if application_read and application_toggle:
                    # Observed Ubeeo non-submit div, never an arbitrary Apply button.
                    toggles=page.locator('div.btn[onclick^="toggleForm("]')
                    for n in range(min(toggles.count(),8)):
                        toggle=toggles.nth(n)
                        if (re.fullmatch(r"toggleForm\('[\w-]+'\)",toggle.get_attribute('onclick') or '')
                            and toggle.inner_text().strip().lower()=='solliciteer direct'
                            and toggle.is_visible()
                            and toggle.locator('xpath=ancestor::form').count()==0):
                            toggle.click(timeout=min(4000,max(50,int(client.remaining()*1000))))
                            try:page.wait_for_load_state('networkidle',timeout=min(4000,max(50,int(client.remaining()*1000))))
                            except Exception:pass
                            break
                if application_read and denied:raise ValueError('Dynamic browser request denied: '+denied[0])
                seen=set()
                for index in range(limit):
                    client.check();text=page.locator('body').inner_text(timeout=3000)
                    if BLOCK.search(text[:3000]):raise ValueError('Browser access challenge; no bypass attempted')
                    if index_error_pattern and re.search(index_error_pattern,text,re.I):
                        raise ValueError('Official vacancy inventory reports a loading error; not an empty list')
                    html=page.content();signature=hash(html)
                    if signature in seen:break
                    seen.add(signature)
                    if application_read and len(html.encode())>20_000_000:raise ValueError('Rendered DOM exceeds memory limit')
                    snapshots.append((page.url,html.encode()))
                    if application_read:break
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
