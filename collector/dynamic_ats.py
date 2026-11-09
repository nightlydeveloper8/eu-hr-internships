"""Opt-in, bounded policy-v2 fallback; no stored HTML can authorize a live check."""
import logging
import os
import re
import threading
import time
from urllib.parse import urlsplit,urljoin
from .classify import canonical_url,fold
from .runtime import CollectionBudgetExceeded

LOG=logging.getLogger(__name__)
PILOTS=frozenset(('auto-bentacera','auto-oosterwolde-plastic-industrie-b-v','auto-centraal-beheer-achmea'))
ENABLE_VALUE='pilot-v1'
# A process handles a shard. At most three renders, one per pilot source/client.
_LOCK=threading.Lock()
_RENDERINGS=0
MAX_RENDERINGS=3
MAX_REQUESTS=32
MAX_SECONDS=25


class MissingDynamicForm(ValueError):
    def __init__(self,message,url,body):
        super().__init__(message);self.url=url;self.body=body


class RenderBudget:
    """A stricter window of the existing client, sharing robots, throttle and counts."""
    def __init__(self,client):
        self.client=client;self.deadline=time.monotonic()+min(MAX_SECONDS,client.remaining())
        self.start=client.requests
    def __getattr__(self,name):return getattr(self.client,name)
    @property
    def requests(self):return self.client.requests
    @requests.setter
    def requests(self,value):self.client.requests=value
    def remaining(self):return min(self.client.remaining(),max(0,self.deadline-time.monotonic()))
    def check(self):
        self.client.check()
        if self.remaining()<.05 or self.requests-self.start>=MAX_REQUESTS:
            raise CollectionBudgetExceeded('Dynamic rendering budget exhausted')
    def permitted(self,url):
        self.check()
        # Robots reads themselves go through BudgetClient. Their timeout is
        # constrained to this rendering window while it is active.
        original=self.client.deadline;original_limit=self.client.max_requests
        self.client.max_requests=min(original_limit,self.start+MAX_REQUESTS)
        self.client.deadline=min(original,self.deadline)
        try:return self.client.permitted(url)
        finally:self.client.deadline=original;self.client.max_requests=original_limit
    def pause(self,seconds):
        if seconds>=self.remaining():raise CollectionBudgetExceeded('Dynamic throttle exceeds budget')
        self.client.pause(seconds)


def marker(body):
    text=body.decode('utf-8','replace')
    toggle=bool(re.search(r'<div\b[^>]*\bonclick=["\']toggleForm\(',text,re.I)
                and re.search(r'id=["\']application-form-[\w-]+["\']',text))
    salesforce='cxsForm.init(' in text and 'cxsFormHolder' in text
    return toggle,salesforce


def exclusion(source,client,body,url):
    if source.get('id') not in PILOTS:return 'source-not-pilot'
    if os.environ.get('PEOPLE_PLACEMENT_DYNAMIC_ATS')!=ENABLE_VALUE:return 'pilot-disabled'
    from .universal import Document
    for href,label,_ in Document(body,url).links:
        if re.search(r'\bapply\b|solliciteer|solliciteren|bewerben|postuler|candidati|candidarsi|candidatar',fold(label)):
            target=urljoin(url,href)
            if urlsplit(target).hostname not in source['allowed_hosts']:
                return 'unapproved-application-host'
    from .applications import ApplicantForms
    for form in ApplicantForms(body).forms:
        attributes=' '.join(str(value or '') for value in form['attrs'].values())
        if re.search(r'apply|applica|recruit|candidate',attributes,re.I):
            return 'html-applicant-form-unavailable'
    toggle,salesforce=marker(body)
    if not (toggle or salesforce):return 'no-reviewed-javascript-marker'
    text=body.decode('utf-8','replace')
    if re.search(r'useCaptcha\s*:\s*["\']True["\']|g-recaptcha|h-captcha|verify you are human',text,re.I):return 'captcha'
    if not all(hasattr(client,k) for k in ('remaining','check','requests','deadline')):return 'bounded-client-required'
    if getattr(client,'dynamic_ats_attempted',False):return 'source-render-budget-exhausted'
    if client.remaining()<5 or client.max_requests-client.requests<4:return 'collection-budget-exhausted'
    return None


def verify_with_fallback(verifier,record,source,client,stamp,observation):
    event=dict(renderings=0,requests=0,browser_requests=0,blocked_requests=0,seconds=0)
    started=time.monotonic()
    try:
        try:
            proof=verifier(record,source,client,stamp,observation)
            event.update(outcome='excluded',reason='ordinary-html-sufficient')
            return proof
        except MissingDynamicForm as missing:
            from .verification import expired
            if expired(record.get('valid_through'),stamp):
                event.update(outcome='excluded',reason='expired-collected-deadline')
                raise ValueError('Dynamic fallback excluded: collected deadline has passed')
            reason=exclusion(source,client,missing.body,missing.url)
            if reason:
                event.update(outcome='excluded',reason=reason);raise
            global _RENDERINGS
            with _LOCK:
                if _RENDERINGS>=MAX_RENDERINGS:
                    event.update(outcome='excluded',reason='process-render-budget-exhausted');raise
                _RENDERINGS+=1;client.dynamic_ats_attempted=True
            from .rendering import render_pages
            from .universal import Document
            from .verification import same_title,structured_identifiers,expired,applicant_form
            from .applications import ensure_open_document,ApplicantForms
            target=canonical_url(missing.url)
            bounded=RenderBudget(client);count=client.requests;render_started=time.monotonic()
            event['renderings']=1
            try:
                snapshots,_=render_pages(target,bounded,
                    lambda url: urlsplit(url).hostname in source['allowed_hosts'],
                    limit=1,application_read=True,application_toggle=marker(missing.body)[0],metrics=event)
                if not snapshots:raise ValueError('Dynamic rendered DOM missing')
                final,body=snapshots[-1]
                if canonical_url(final)!=target:raise ValueError('Dynamic application redirected')
                rendered=Document(body,final);ensure_open_document(rendered)
                if re.search(rb'g-recaptcha|h-captcha|useCaptcha\s*:\s*[\"\']True',body,re.I):raise ValueError('Dynamic CAPTCHA; no bypass attempted')
                if not same_title(rendered,record['title']):raise ValueError('Dynamic title differs from vacancy')
                ids=structured_identifiers(rendered,record['title'])
                original_ids=structured_identifiers(Document(missing.body,target),record['title'])
                expected=original_ids or ({str(record['posting_identifier'])} if record.get('posting_identifier') else set())
                if ids and expected and ids!=expected:raise ValueError('Dynamic ATS ID differs from vacancy')
                for form in ApplicantForms(body,strict=True).forms:
                    action=form['attrs'].get('action')
                    # Explicit destinations are never implicitly approved by a
                    # form embedded on an otherwise approved vacancy page.
                    if action and urlsplit(canonical_url(urljoin(final,action))).hostname not in source['allowed_hosts']:
                        raise ValueError('Dynamic form action host is not approved')
                    for field in form['fields']:
                        if re.fullmatch(r'(?:fields\[)?(?:job|vacancy|requisition|posting|req)[_-]?id\]?',field.get('name') or field.get('id') or '',re.I):
                            value=field.get('value')
                            if expected and value and value not in expected:raise ValueError('Dynamic form ATS ID differs from vacancy')
                if not applicant_form(body,strict=True):raise ValueError('Dynamic applicant fields or enabled submit unavailable')
                class CurrentDOM:
                    def request(self,url):
                        if canonical_url(url)==target:return body,200,final
                        return client.request(url)
                # Reapply the ordinary policy, including identity, deadlines and
                # observed CTA relationship. This DOM exists only in this call.
                proof=verifier(record,source,CurrentDOM(),stamp,observation)
                event.update(outcome='verified',reason='rendered-'+proof['method'])
                return dict(proof,method=event['reason'])
            except Exception as exc:
                event.update(outcome='unverified',reason=str(exc)[:200]);raise
            finally:
                event.update(requests=client.requests-count,seconds=round(time.monotonic()-render_started,3))
    except Exception as exc:
        if 'outcome' not in event:event.update(outcome='excluded',reason='ordinary-verification-failed: '+str(exc)[:160])
        raise
    finally:
        event['total_seconds']=round(time.monotonic()-started,3)
        if observation is not None:observation['dynamic_ats']=event
        LOG.info('dynamic_ats source=%s url=%s metrics=%s',source.get('id'),record['url'],event)
