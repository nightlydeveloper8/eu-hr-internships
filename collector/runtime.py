"""Bounded, host-throttled collection and temporary page metadata checkpoints."""
from contextlib import contextmanager
from datetime import datetime,timezone
import gzip,hashlib,json,os,threading,time
from pathlib import Path
from email.utils import parsedate_to_datetime
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from .adapters import Client
from .classify import canonical_url

class CollectionBudgetExceeded(RuntimeError):pass
_LOCK=threading.Lock();_HOST_LOCKS={};_LAST={};_DELAYS={};_ROBOTS={};_RATE_LIMITED_HOSTS=set()
def host_lock(host):
    with _LOCK:return _HOST_LOCKS.setdefault(host,threading.RLock())

class BudgetClient(Client):
    def __init__(self,seconds=120,max_requests=100,delay=.5):
        super().__init__(delay);self.deadline=time.monotonic()+seconds;self.max_requests=max_requests;self.requests=0;self.bytes=0
        self.last=_LAST;self.host_delays=_DELAYS;self.robots=_ROBOTS;self.last_response_url=None
        self.rate_limited_skips=0
        self.retry_hosts=frozenset()
        self.reuse_last_get=False
        self.last_get=None
        self.preserve_request_url=False
        self.retry_outcomes=Counter()
    @staticmethod
    def set_host_delays(delays):
        with _LOCK:
            for host, delay in delays.items():
                _DELAYS[host]=max(_DELAYS.get(host,0),delay)

    def remaining(self):return max(0,self.deadline-time.monotonic())
    def check(self):
        if self.remaining()<.05:raise CollectionBudgetExceeded('Time budget exhausted; checkpoint retained')
        if self.requests>=self.max_requests:raise CollectionBudgetExceeded('Request budget exhausted; checkpoint retained')
    def pause(self,seconds):
        if seconds>=self.remaining():raise CollectionBudgetExceeded('Required host delay exceeds remaining budget; checkpoint retained')
        time.sleep(seconds)

    def permitted(self,url):
        # Redirects call permitted() before following the destination. Keep
        # a previously rate-limited host closed even through another host's URL.
        if urlsplit(url).netloc in _RATE_LIMITED_HOSTS:
            self.rate_limited_skips+=1
            raise HTTPError(url,429,'Redirect target rate-limited earlier in this collection process',None,None)
        return super().permitted(url)

    def request(self,url,method='GET',robots=True,timeout=12,attempts=1,accept=None,body=None,content_type=None):
        if self.reuse_last_get and method=='GET' and robots and not accept and body is None:
            target=canonical_url(url)
            previous=self.last_get
            self.last_get=None
            if previous and previous[0]==target:
                return previous[1]
            result=self._request_once(url,method,robots,timeout,attempts,accept,body,content_type)
            self.last_get=(target,result)
            return result
        if method!='GET' or urlsplit(url).hostname not in self.retry_hosts:
            return self._request_once(url,method,robots,timeout,attempts,accept,body,content_type)
        for attempt in range(3):
            try:
                result=self._request_once(url,method,robots,timeout,1,accept,body,content_type)
            except (HTTPError, URLError, TimeoutError) as exc:
                if isinstance(exc,HTTPError) and exc.code==503:
                    reason='http-503'
                elif isinstance(exc,TimeoutError) or isinstance(getattr(exc,'reason',None),TimeoutError):
                    reason='timeout'
                else:
                    raise
                self.retry_outcomes[reason]+=1
                if attempt==2 or self.requests>=self.max_requests or self.remaining()<=2**(attempt+1)+.05:
                    self.retry_outcomes['exhausted']+=1
                    raise
                self.pause(2**(attempt+1))
            else:
                if attempt:self.retry_outcomes['recovered']+=1
                return result

    def retry_rate_limited_get(self, url, error):
        """Retry a single rejected GET after the host cooldown under its lock."""
        host = urlsplit(url).netloc
        if error.code != 429 or canonical_url(error.geturl()) != canonical_url(url):
            raise error
        retry_after = error.headers.get('Retry-After', '') if error.headers else ''
        wait = 60
        if retry_after.isdecimal():
            wait = max(wait, int(retry_after))
        elif retry_after:
            try:
                wait = max(wait, (parsedate_to_datetime(retry_after)-datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError, OverflowError):
                pass
        lock = host_lock(host)
        if not lock.acquire(timeout=self.remaining()):
            raise CollectionBudgetExceeded('Host queue exceeded collection budget')
        try:
            self.check()
            self.pause(wait)
            self.retry_outcomes['http-429'] += 1
            return self._request_once(url, 'GET', False, 12, 1, None, None, None,
                                      retry_rate_limit=True)
        finally:
            lock.release()

    def _request_once(self,url,method,robots,timeout,attempts,accept,body,content_type,*,retry_rate_limit=False):
        normalized=canonical_url(url)
        url=url if self.preserve_request_url else normalized
        host=urlsplit(url).netloc;self.check();lock=host_lock(host)
        if not lock.acquire(timeout=self.remaining()):raise CollectionBudgetExceeded('Host queue exceeded collection budget')
        try:
            self.check()
            # A 429 is a host-level rate limit, not a failed vacancy: do not
            # spend more requests on that host unless the scoped cooldown retry applies.
            # The shared set also protects subsequent employer clients/shards
            # within the same Python process. A fresh daily process resets it.
            if host in _RATE_LIMITED_HOSTS and not retry_rate_limit:
                self.rate_limited_skips+=1
                raise HTTPError(url,429,'Host rate-limited earlier in this collection process',None,None)
            self.requests+=1
            try:
                result=super().request(url,method=method,robots=robots,
                    timeout=max(.05,min(timeout,self.remaining())),attempts=attempts,accept=accept,body=body,content_type=content_type)
            except HTTPError as exc:
                if exc.code==429:
                    # Redirects may reach another approved host; quarantine the
                    # host that actually returned 429, not its referring host.
                    limited_host=urlsplit(exc.geturl() or url).netloc or host
                    with _LOCK:_RATE_LIMITED_HOSTS.add(limited_host)
                raise
            if retry_rate_limit and result[1] == 200:
                with _LOCK:_RATE_LIMITED_HOSTS.discard(host)
            self.bytes+=len(result[0]);self.last_response_url=result[2];return result
        finally:lock.release()

class PageCache:
    """Technical cache only: never copied to the public static dataset."""
    def __init__(self,source_id,root=None,revision=1):
        root=Path(root or os.environ.get('COLLECTOR_CACHE_DIR','.cache/collector'))
        self.root=root/hashlib.sha256(source_id.encode()).hexdigest()[:24];self.root.mkdir(parents=True,exist_ok=True)
        self.hits=0;self.writes=0;self.revision=revision
    def path(self,url):return self.root/(hashlib.sha256(url.encode()).hexdigest()+'.json.gz')
    def exists(self,url):return self.path(url).exists()
    def timestamp(self,url):
        try:return self.path(url).stat().st_mtime
        except OSError:return 0
    def get(self,url,lastmod=None,max_age_hours=72):
        try:
            with gzip.open(self.path(url),'rt',encoding='utf-8') as f:value=json.load(f)
            if value.get('revision',1)!=self.revision:return None
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(value['stored_at'])).total_seconds()/3600
            if age<0 or age>max_age_hours or (lastmod and value.get('lastmod')!=lastmod):return None
            record=value['record']
            # A cache hit is not a new observation of the vacancy. Legacy
            # entries have stored_at as their only available evidence time.
            for row in [record]+record.get('records',[]):
                original=row.get('_text_observation',{})
                row['_text_observation']=dict(kind='cache',
                    checked_at=original.get('checked_at',value['stored_at']),
                    origin=original.get('origin',original.get('kind','unknown')))
            self.hits+=1;return record
        except (OSError,ValueError,KeyError,TypeError):return None
    def put(self,url,record,lastmod=None):
        path=self.path(url);tmp=path.with_suffix('.tmp')
        with gzip.open(tmp,'wt',encoding='utf-8') as f:json.dump(dict(revision=self.revision,stored_at=datetime.now(timezone.utc).isoformat(),lastmod=lastmod,record=record),f,ensure_ascii=False)
        os.replace(tmp,path);self.writes+=1
    def state(self):
        try:return json.loads((self.root/'frontier.json').read_text())
        except (OSError,ValueError):return {}
    def save_state(self,value):
        path=self.root/'frontier.json';tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False));os.replace(tmp,path)
