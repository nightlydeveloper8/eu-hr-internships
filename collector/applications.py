"""Read-only availability checks for individually reviewed application templates."""
from html.parser import HTMLParser
import re
from urllib.parse import parse_qs, urljoin, urlsplit
from .classify import canonical_url, plain, fold


class ApplicationClosed(ValueError):
    pass


class FormFields(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.forms = []
        self.inputs = []
        self.feed(body.decode('utf-8', 'replace'))

    def handle_starttag(self, tag, attrs):
        if tag == 'form': self.forms.append(dict(attrs))
        if tag in ('input', 'textarea'): self.inputs.append(dict(attrs))


class ApplicantForms(HTMLParser):
    def __init__(self, body, strict=False):
        super().__init__();self.forms=[];self.current=None;self.strict=strict;self.scopes=[]
        self.feed(body.decode('utf-8','replace'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        blocked=('disabled' in a or 'disabled' in a.get('class','').split() or 'hidden' in a or a.get('aria-hidden')=='true'
                 or a.get('aria-disabled')=='true' or bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',a.get('style',''),re.I)))
        inherited=any(value for _,value in self.scopes) if self.strict else False
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.scopes.append((tag,blocked))
        if tag=='form':
            self.current=dict(attrs=a,fields=[],submit=False);self.forms.append(self.current)
        if self.current is not None and not (self.strict and (blocked or inherited)) and 'disabled' not in a and a.get('aria-disabled')!='true' and 'disabled' not in a.get('class','').split():
            if tag in ('input','textarea'):self.current['fields'].append(a)
            if (tag=='button' and a.get('type','submit')=='submit') or (tag=='input' and a.get('type')=='submit') or (tag=='a' and bool({'o_website_form_send','s_website_form_send'} & set(a.get('class','').split()))):self.current['submit']=True
    def handle_endtag(self,tag):
        if tag=='form':self.current=None
        for index in range(len(self.scopes)-1,-1,-1):
            if self.scopes[index][0]==tag:
                del self.scopes[index:];break


class JobPortalTitle(HTMLParser):
    """Reviewed publication form title, excluding its introductory small tag."""
    def __init__(self,body):
        super().__init__(convert_charrefs=True);self.stack=[];self.values=[];self.current=None
        self.feed(body.decode('utf-8','replace'))
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='h2' and 'vacancy-title' in attrs.get('class','').split():self.current=[]
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append(tag)
    def handle_data(self,value):
        if self.current is not None and 'small' not in self.stack:self.current.append(value)
    def handle_endtag(self,tag):
        if tag=='h2' and self.current is not None:
            self.values.append(plain(' '.join(self.current)));self.current=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]==tag:del self.stack[i:];break


def publication_application(record,source,client,body,doc):
    """Observed publication -> same-ID application -> visible enabled form."""
    from .verification import applicant_form,same_title
    vacancy=urlsplit(doc.url)
    match=re.fullmatch(r'/(\d+)-([^/]+)/[a-z]{2}/job\.html',vacancy.path)
    if (source.get('adapter')!='employer-index' or not match
        or not same_title(doc,record['title']) or str(record.get('external_id'))!=match.group(1)):
        raise ValueError('Current publication title and posting ID required')
    publication=match.group(1)+'-'+match.group(2)
    path='/jobs/'+publication+'/job_application/new'
    targets={canonical_url(urljoin(doc.url,href)) for href,_,_ in doc.links
             if urlsplit(urljoin(doc.url,href)).hostname==vacancy.hostname
             and urlsplit(urljoin(doc.url,href)).path==path}
    if len(targets)!=1:raise ValueError('Observed same-publication application entry missing or ambiguous')
    target=targets.pop()
    if urlsplit(target).query and not re.fullmatch(r'persist_lang=[a-z]{2}',urlsplit(target).query):
        raise ValueError('Unreviewed publication application query')
    app_body,app=checked_document(target,source,client)
    final=urlsplit(app.url)
    # This portal adds its interface locale during an ordinary GET redirect.
    # No session, authentication or different posting redirect is accepted.
    if (final.hostname!=vacancy.hostname or final.path!=path
        or (final.query and not re.fullmatch(r'persist_lang=[a-z]{2}',final.query))
        or final.fragment or JobPortalTitle(app_body).values!=[record['title']]):
        raise ValueError('Publication application identity or title differs')
    forms=[f for f in ApplicantForms(app_body,strict=True).forms
           if f['attrs'].get('id')=='new_job_application']
    expected='/jobs/'+publication+'/job_application'
    required_fields={'job_application[applicant_core][user][firstname]',
                     'job_application[applicant_core][user][lastname]',
                     'job_application[applicant_core][account][email]'}
    if (len(forms)!=1 or urlsplit(urljoin(app.url,forms[0]['attrs'].get('action',''))).hostname!=vacancy.hostname
        or urlsplit(urljoin(app.url,forms[0]['attrs'].get('action',''))).path!=expected
        or not forms[0]['submit'] or not required_fields.issubset({f.get('name') for f in forms[0]['fields']})
        or not any(f.get('type')=='file' and f.get('id')=='file-upload-curriculum_vitae' for f in forms[0]['fields'])
        or not applicant_form(app_body,strict=True)):
        raise ValueError('Visible enabled same-publication applicant form not established')
    return dict(url=canonical_url(app.url),method='official-publication-same-posting-visible-form')



def checked_document(url, source, client):
    from .universal import Document
    if urlsplit(url).hostname not in source['allowed_hosts']:
        raise ValueError('Unreviewed application host')
    body, _, final = client.request(url)
    if urlsplit(final).hostname not in source['allowed_hosts']:
        raise ValueError('Unreviewed application redirect')
    doc = Document(body, final)
    try:ensure_open_document(doc)
    except ApplicationClosed as exc:
        # The verifier still needs to identify this document and capture changed
        # metadata before propagating the same closure decision.
        exc.document=doc;exc.body=body
        raise
    return body, doc


def ensure_open_document(doc):
    from .universal import CHALLENGE
    if CHALLENGE.search(doc.text[:3000]): raise ValueError('Application access challenge')
    # Official career pages sometimes retain a valid-looking JobPosting after
    # closing the vacancy (observed Electrolux JR81378: HTTP 200 plus "filled").
    # The visible closure takes precedence over residual structured metadata.
    text = fold(doc.text)
    if re.search(r'(?:vacature|vacancy|position|job|posting).{0,45}(?:niet (?:meer )?beschikbaar|niet meer open|is gesloten|is closed|has closed|has (?:now )?expired|no longer available|no longer accepting)|solliciteren.{0,25}niet meer mogelijk|offre.{0,30}(?:expiree|pourvue)|stelle.{0,30}(?:besetzt|geschlossen)', text, re.I) or re.search(
        r'\b(?:job|position|vacancy|posting)\b.{0,90}\b(?:has been filled|is already filled|is filled)\b', text, re.I):
        raise ApplicationClosed('Official application page says the posting is closed')


def odoo_application(doc, source, client, title):
    targets = [canonical_url(urljoin(doc.url, href)) for href, _, _ in doc.links
        if re.fullmatch(r'/jobs/apply/(?:[^/?]+-)?\d+', urlsplit(urljoin(doc.url, href)).path)]
    if not targets: raise ValueError('Reviewed Odoo application link missing')
    # Use the primary call to action; old templates can retain a stale secondary link.
    body, form_doc = checked_document(targets[0], source, client)
    forms=[f for f in ApplicantForms(body).forms if f['attrs'].get('id')=='hr_recruitment_form' and f['attrs'].get('data-model_name')=='hr.applicant']
    if not forms:raise ValueError('Odoo application form missing')
    if not any(f['submit'] and {'partner_name','email_from'}.issubset({i.get('name') for i in f['fields']}) for f in forms):
        raise ValueError('Odoo applicant fields or enabled submit unavailable')
    if title not in form_doc.text or not re.search(r'\bVacature\s+' + re.escape(title) + r'\s+Locatie\b', form_doc.text):
        raise ValueError('Odoo form does not identify the same vacancy')
    return form_doc


def verify_application(record, source, client, vacancy_document=None):
    kind = source.get('application_check')
    if not kind: return None
    body, doc = vacancy_document if kind=='publication-linked' and vacancy_document else checked_document(record['url'], source, client)
    if kind=='publication-linked':return publication_application(record,source,client,body,doc)
    if kind=='recruitee-linked':
        from .verification import same_title, structured_identifiers, applicant_form, expired
        from .ownership import employer_matches
        from datetime import datetime, timezone
        expected=str(record.get('posting_identifier') or '')
        target=record.get('observed_application_url')
        if (source.get('adapter')!='recruitee' or record.get('inventory_evidence')!='current-employer-feed' or not expected.isdigit()
            or not target or not same_title(doc,record['title'])
            or structured_identifiers(doc,record['title'])!={expected}):
            raise ValueError('Current Recruitee feed and vacancy identity required')
        vacancy=urlsplit(doc.url);application=urlsplit(target)
        if (vacancy.hostname!=application.hostname or application.query
            or application.fragment or application.path.rstrip('/')!=vacancy.path.rstrip('/')+'/c/new'):
            raise ValueError('Observed Recruitee entry does not retain the same vacancy')
        app_body,app=checked_document(target,source,client)
        if canonical_url(app.url)!=canonical_url(target) or not same_title(app,record['title']):
            raise ValueError('Recruitee application redirected or identifies another vacancy')
        if structured_identifiers(app,record['title'])!={expected}:
            raise ValueError('Recruitee application posting identifier differs')
        for page in (doc,app):
            posts=[post for post in page.jobposts() if fold(plain(post.get('title')))==fold(record['title'])]
            for post in posts:
                organisation=post.get('hiringOrganization')
                name=organisation.get('name') if isinstance(organisation,dict) else organisation
                if not name or not employer_matches(plain(name),source,page.url):
                    raise ValueError('Recruitee posting belongs to another or unknown employer')
        stamp=datetime.now(timezone.utc).isoformat()
        if any(expired(post.get('validThrough'),stamp) for post in app.jobposts()
               if fold(plain(post.get('title')))==fold(record['title'])):
            raise ApplicationClosed('Recruitee application deadline has passed')
        # The vacancy can contain an inactive hidden tab. Only the observed
        # application entry with visible enabled applicant fields establishes it.
        if not applicant_form(app_body,strict=True):
            raise ValueError('Visible enabled Recruitee application form not established')
        return dict(url=canonical_url(app.url),method='official-recruitee-same-posting-visible-form')
    if kind == 'hlb-email':
        address = 'personeel@hlbbv.nl'
        if (source.get('application_email') != address
            or not any(href.lower().split('?')[0] == 'mailto:' + address for href, _, _ in doc.links)
            or 'Je cv en motivatiebrief mogen gestuurd worden naar ' + address not in doc.text):
            raise ValueError('HLB vacancy-specific CV and motivation email instructions unavailable')
        return dict(url=record['url'], method='official-vacancy-email-instructions',
                    application_email=address, delivery_verified=False)
    if kind == 'official-email':
        # The address must be both reviewed and currently published with an
        # instruction to send application documents on this identified vacancy.
        address = source.get('application_email', '')
        observed = any(href.lower().split('?')[0] == 'mailto:' + address.lower()
                       for href, _, _ in doc.links)
        instructions = re.search(r'(?:stuur|send|mail).{0,200}(?:cv|resume).{0,100}'
                                 + re.escape(address), doc.text, re.I)
        # An explicit invitation to apply directly is sufficient even when the
        # employer does not prescribe a CV. Mere contact/questions are not.
        direct_application = re.search(
            r'\b(?:wil je|wilt u)\s+direct reageren\?\s*(?:neem contact op|mail|stuur)'
            r'[^.!?]{0,160}\b(?:via|naar)\s*'+re.escape(address), doc.text, re.I)
        if direct_application and re.search(r'\b(?:niet|geen|vragen)\b',direct_application.group(0),re.I):
            direct_application=None
        if not address or not observed or not (instructions or direct_application):
            raise ValueError('Vacancy-specific email application instructions unavailable')
        return dict(url=record['url'], method='official-vacancy-email-instructions',
                    application_email=address, delivery_verified=False)
    if kind == 'formie-linked':
        expected=str(record.get('posting_identifier') or '')
        targets=[canonical_url(urljoin(doc.url,href)) for href,label,_ in doc.links
                 if re.search(r'solliciteer|solliciteren|apply',label,re.I)
                 and parse_qs(urlsplit(href).query).get('vacature')==[expected]]
        if not expected or not targets:raise ValueError('Matching Formie application entry missing')
        app_body,app=checked_document(targets[0],source,client)
        if canonical_url(app.url)!=targets[0] or 'Solliciteren voor: '+record['title'] not in app.text:
            raise ValueError('Formie application identifies a different vacancy')
        for form in ApplicantForms(app_body).forms:
            fields={field.get('name'):field for field in form['fields']}
            if ('applicationForm' in form['attrs'].get('data-form-handle','') and form['submit']
                and fields.get('fields[vacancyId]',{}).get('value')==expected
                and {'fields[firstName]','fields[email]'}.issubset(fields)):
                return dict(url=app.url,method='official-formie-same-requisition-form')
        raise ValueError('Formie applicant fields, requisition or submit unavailable')
    if kind == 'odoo':
        form = odoo_application(doc, source, client, record['title'])
        return dict(url=canonical_url(form.url), method='official-vacancy-specific-form')
    if kind == 'avature-linked':
        links = [canonical_url(urljoin(doc.url, href)) for href, label, _ in doc.links
            if urlsplit(urljoin(doc.url, href)).hostname in source['allowed_hosts']
            and '/External/JobDetail' in href and re.search(r'apply|solliciteer', label, re.I)]
        if not links: raise ValueError('Official Avature application button missing')
        target = links[0]
        identifier = parse_qs(urlsplit(target).query).get('jobId')
        expected=record.get('posting_identifier')
        if not expected:
            for post in doc.jobposts():
                value=post.get('identifier')
                if isinstance(value,dict):value=value.get('value')
                if value is not None:expected=str(value);record['posting_identifier']=expected;break
        if not expected or identifier != [str(expected)]:
            raise ValueError('Application requisition differs from the vacancy')
        _, application = checked_document(target, source, client)
        if record['title'] not in application.h1:
            raise ValueError('Application title does not match')
        if not any('/External/Login' in href and parse_qs(urlsplit(href).query).get('jobId') == identifier
            and re.search(r'solliciteren|apply', label, re.I) for href, label, _ in application.links):
            raise ValueError('Same-requisition Avature application entry unavailable')
        return dict(url=target, method='official-requisition-application-entry', account_required=True)
    if kind == 'watson-rendered':
        from .rendering import render_pages
        expected=str(record.get('posting_identifier') or '')
        if not re.fullmatch(r'req\d+',expected):raise ValueError('Reviewed Watson requisition missing')
        targets=[canonical_url(urljoin(doc.url,href)) for href,label,_ in doc.links
                 if re.search(r'solliciteer|solliciteren',label,re.I)
                 and urlsplit(urljoin(doc.url,href)).hostname in source['allowed_hosts']
                 and urlsplit(href).path=='/vacatures-solliciteer'
                 and parse_qs(urlsplit(href).query).get('req')==[expected[3:]]]
        if not targets:raise ValueError('Watson same-requisition application link missing')
        snapshots,_=render_pages(targets[0],client,
            lambda target:urlsplit(target).hostname in source['allowed_hosts'],limit=1)
        if not snapshots:raise ValueError('Watson application form could not be rendered')
        final,body=snapshots[-1]
        if canonical_url(final)!=targets[0]:raise ValueError('Watson application redirected')
        from .universal import Document
        application=Document(body,final)
        ensure_open_document(application)
        if 'Je solliciteert op de functie '+record['title'] not in application.text:
            raise ValueError('Watson application title differs from vacancy')
        for form in ApplicantForms(body).forms:
            fields={f.get('name'):f for f in form['fields']}
            if (form['attrs'].get('id')=='watson-apply-form' and form['submit']
                and fields.get('ReqId',{}).get('value')==expected
                and {'FirstName','LastName','Email','Resume'}.issubset(fields)):
                return dict(url=final,method='rendered-watson-same-requisition-form')
        raise ValueError('Watson applicant fields, requisition or submit unavailable')
    if kind == 'hanos-rendered':
        from .rendering import render_pages
        snapshots, _ = render_pages(record['url'], client,
            lambda target: urlsplit(target).hostname in source['allowed_hosts'], limit=1)
        if not snapshots: raise ValueError('Application form could not be rendered')
        forms=[f for f in ApplicantForms(snapshots[0][1]).forms if f['attrs'].get('name')=='apply-form']
        if not forms:raise ValueError('HANOS application form unavailable')
        if not any(f['submit'] and {'first-name','last-name','email-address'}.issubset({i.get('id') for i in f['fields']}) for f in forms):
            raise ValueError('HANOS applicant fields or enabled submit unavailable')
        return dict(url=record['url'], method='rendered-official-application-form')
    raise ValueError('Unreviewed application template: ' + str(kind))
