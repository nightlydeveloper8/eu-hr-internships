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
    def __init__(self, body):
        super().__init__();self.forms=[];self.current=None
        self.feed(body.decode('utf-8','replace'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            self.current=dict(attrs=a,fields=[],submit=False);self.forms.append(self.current)
        if self.current is not None and 'disabled' not in a and a.get('aria-disabled')!='true' and 'disabled' not in a.get('class','').split():
            if tag in ('input','textarea'):self.current['fields'].append(a)
            if (tag=='button' and a.get('type','submit')=='submit') or (tag=='input' and a.get('type')=='submit') or (tag=='a' and bool({'o_website_form_send','s_website_form_send'} & set(a.get('class','').split()))):self.current['submit']=True
    def handle_endtag(self,tag):
        if tag=='form':self.current=None



def checked_document(url, source, client):
    from .universal import Document, CHALLENGE
    if urlsplit(url).hostname not in source['allowed_hosts']:
        raise ValueError('Unreviewed application host')
    body, _, final = client.request(url)
    if urlsplit(final).hostname not in source['allowed_hosts']:
        raise ValueError('Unreviewed application redirect')
    doc = Document(body, final)
    if CHALLENGE.search(doc.text[:3000]): raise ValueError('Application access challenge')
    if re.search(r'(?:vacature|position|job|posting).{0,45}(?:niet meer beschikbaar|niet meer open|is gesloten|is closed|has closed|no longer available|no longer accepting|has expired)|solliciteren.{0,25}niet meer mogelijk|offre.{0,30}(?:expiree|pourvue)|stelle.{0,30}(?:besetzt|geschlossen)', fold(doc.text), re.I):
        raise ApplicationClosed('Official application page says the posting is closed')
    return body, doc


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


def verify_application(record, source, client):
    kind = source.get('application_check')
    if not kind: return None
    body, doc = checked_document(record['url'], source, client)
    if kind == 'official-email':
        # The address must be both reviewed and currently published with an
        # instruction to send application documents on this identified vacancy.
        address = source.get('application_email', '')
        observed = any(href.lower().split('?')[0] == 'mailto:' + address.lower()
                       for href, _, _ in doc.links)
        instructions = re.search(r'(?:stuur|send|mail).{0,200}(?:cv|resume).{0,100}'
                                 + re.escape(address), doc.text, re.I)
        if not address or not observed or not instructions:
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
