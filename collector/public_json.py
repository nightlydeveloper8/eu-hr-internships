"""Recognize the public JSON representation of an official recruiting page."""
from urllib.parse import urlsplit,urljoin
from .classify import canonical_url,plain,country_codes

def smartrecruiters_job(data,url,source):
    if urlsplit(url).hostname!='jobs.smartrecruiters.com':return None
    if not isinstance(data,dict) or not data.get('jobTitle') or not isinstance(data.get('content',{}).get('sections'),dict):return None
    if data.get('isApplyAvailable') is not True:
        return dict(records=[],links=[],empty=False,closed_urls=[canonical_url(url)] if data.get('isApplyAvailable') is False else [])
    sections=data['content']['sections'];text=' '.join(plain(s.get('text','')) for k,s in sections.items() if k!='companyDescription' and isinstance(s,dict))
    location=plain(data.get('jobAdLocation'));target=canonical_url(urljoin(url,data.get('applyUrl') or url))
    if urlsplit(target).hostname!='jobs.smartrecruiters.com':raise ValueError('Unexpected public SmartRecruiters posting host')
    employer=data.get('company',{}).get('name') or source['employer'];identifier=data.get('uuid') or target
    r=dict(source_id=source['id'],external_id=str(identifier),posting_identifier=str(identifier),employer=plain(employer),title=plain(data['jobTitle']),text=text,location=location,city=location if len(location)<=160 else None,countries=country_codes(location),country=None,url=target,apply_url=target,language=data.get('jobAdLanguageCode'),published_at=data.get('postedDate'),employment=plain(data.get('employmentType')),work_mode=None,needs_page=False,extraction_method='public-smartrecruiters-json')
    return dict(records=[r],links=[],empty=False)
