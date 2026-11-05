"""Read the public Amazon.jobs search response used by its recruiting website.

The published search URL returns JSON to the collector's JSON Accept header.
Every result page is checked against its reported start and total hit count.
"""
import json
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode,urljoin
from .classify import canonical_url,plain,country_codes

def search_records(source,client):
    records={}
    for search in source['search_urls']:
        base=canonical_url(search);p=urlsplit(base)
        if p.hostname not in ('www.amazon.jobs','amazon.jobs') or not p.path.endswith('/search'):raise ValueError('Unapproved Amazon search URL')
        offset=0;total=None;seen=set()
        while True:
            params=dict(parse_qsl(p.query));params.update(result_limit='100',offset=str(offset))
            url=urlunsplit((p.scheme,p.netloc,p.path,urlencode(params),''));data=client.json(url)
            if data.get('error') or not isinstance(data.get('jobs'),list):raise ValueError('Invalid public Amazon search response')
            jobs=data['jobs'];hits=data.get('hits')
            if not isinstance(hits,int) or hits<0:raise ValueError('Missing Amazon inventory total')
            if total is None:total=hits
            elif hits!=total:raise ValueError('Amazon inventory changed during pagination')
            request=data.get('job_posting_search_request')
            request=json.loads(request) if isinstance(request,str) else request
            try:confirmed_start=int(request.get('jobPostingSearchRequest',{}).get('start'))
            except (TypeError,ValueError,AttributeError):raise ValueError('Amazon pagination position not confirmed')
            if confirmed_start!=offset:raise ValueError('Amazon pagination position not confirmed')
            if not jobs and offset<total:raise ValueError('Incomplete public Amazon inventory')
            for j in jobs:
                identifier=str(j.get('id_icims') or j.get('id') or '')
                if not identifier or identifier in seen:raise ValueError('Missing or repeated Amazon job ID')
                seen.add(identifier)
                job_url=canonical_url(urljoin(base,j.get('job_path') or ''))
                if urlsplit(job_url).hostname not in source['allowed_hosts'] or '/jobs/' not in urlsplit(job_url).path:raise ValueError('Unapproved published Amazon job URL')
                countries=set();cities=[];modes=set()
                for location in j.get('locations') or []:
                    location=json.loads(location) if isinstance(location,str) else location
                    if not isinstance(location,dict):continue
                    if location.get('type'):modes.add(location['type'])
                    countries.update(country_codes('',location.get('countryIso2a') or location.get('countryIso3a') or location.get('normalizedCountryCode')))
                    city=location.get('city') or location.get('normalizedCityName')
                    if city and city not in cities:cities.append(city)
                if not countries:countries.update(country_codes('',j.get('country_code')))
                if not cities and j.get('city'):cities.append(j['city'])
                posted=None
                try:posted=datetime.strptime(j.get('posted_date',''),'%B %d, %Y').replace(tzinfo=timezone.utc).isoformat()
                except ValueError:pass
                text=' '.join(plain(j.get(k,'')) for k in ('description','basic_qualifications','preferred_qualifications'))
                records[identifier]=dict(source_id=source['id'],external_id=identifier,posting_identifier=identifier,employer=plain(j.get('company_name')) or source['employer'],title=plain(j.get('title')),text=text,location=plain(j.get('location')),city='; '.join(cities) or None,countries=sorted(countries),country=None,url=job_url,apply_url=job_url,language=None,published_at=posted,employment='',work_mode={'ONSITE':'on-site','REMOTE':'remote','HYBRID':'hybrid'}.get(next(iter(modes))) if len(modes)==1 else None,needs_page=False)
            offset+=len(jobs)
            if offset==total:break
            if offset>total or offset>10000:raise ValueError('Amazon inventory count mismatch or safety limit')
    return list(records.values())
