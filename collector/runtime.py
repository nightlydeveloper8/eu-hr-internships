"""Bounded, host-throttled collection and temporary page metadata checkpoints."""
from contextlib import contextmanager
from datetime import datetime,timezone
import gzip,hashlib,json,os,threading,time
from pathlib import Path
from urllib.parse import urlsplit
from .adapters import Client
from .classify import canonical_url

class CollectionBudgetExceeded(RuntimeError):pass
_LOCK=threading.Lock();_HOST_LOCKS={};_LAST={};_DELAYS={};_ROBOTS={}
def host_lock(host):
    with _LOCK:return _HOST_LOCKS.setdefault(host,threading.RLock())

class BudgetClient(Client):
    def __init__(self,seconds=120,max_requests=100,delay=.5):
        super().__init__(delay);self.deadline=time.monotonic()+seconds;self.max_requests=max_requests;self.requests=0;self.bytes=0
        self.last=_LAST;self.host_delays=_DELAYS;self.robots=_ROBOTS;self.last_response_url=None
    def remaining(self):return max(0,self.deadline-time.monotonic())
    def check(self):
        if self.remaining()<.05:raise CollectionBudgetExceeded('Time budget exhausted; checkpoint retained')
        if self.requests>=self.max_requests:raise CollectionBudgetExceeded('Request budget exhausted; checkpoint retained')
    def pause(self,seconds):
        if seconds>=self.remaining():raise CollectionBudgetExceeded('Required host delay exceeds remaining budget; checkpoint retained')
        time.sleep(seconds)

    def request(self,url,method='GET',robots=True,timeout=12,attempts=1):
        url=canonical_url(url);self.check();lock=host_lock(urlsplit(url).netloc)
        if not lock.acquire(timeout=self.remaining()):raise CollectionBudgetExceeded('Host queue exceeded collection budget')
        try:
            self.check();self.requests+=1
            result=super().request(url,method=method,robots=robots,timeout=max(.05,min(timeout,self.remaining())),attempts=attempts)
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
