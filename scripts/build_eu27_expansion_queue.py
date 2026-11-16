"""Build an offline EU27 preparation queue; never register or collect a source.

Run from any directory. Outputs only docs/eu27-expansion/{queue,batch-01}.json
and README.md. Research countries and indexed leads are not live coverage.
"""
from collections import Counter, defaultdict
import hashlib
import gzip
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.ats_channel_discovery import identify_channel, safe_url
from collector.classify import fold

EU27=('AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE')
FIRST=('NL','BE','DE','FR','IE')
SUPPORTED={'greenhouse','lever','personio-xml','recruitee'}
BLOCK=re.compile(r'robots|\b40[1369]\b|\b429\b|captcha|access (?:challenge|denied)|security verification',re.I)
AGGREGATORS=('nationalevacaturebank.nl','noorderlink.nl','linkedin.com','indeed.com','glassdoor.com')


def name_key(name):
    # Exact normalized names only; no fuzzy legal/group ownership inference.
    return re.sub(r'[^a-z0-9]+',' ',fold(name or '')).strip()


def channel(url):
    if not safe_url(url):return None
    host=urlsplit(url).hostname
    if any(host==h or host.endswith('.'+h) for h in AGGREGATORS):return None
    found=identify_channel(url)
    if found and found['adapter'] in SUPPORTED:
        return dict(key=found['channel_key'],adapter=found['adapter'],tenant=found['tenant'],url=url)
    # Unsupported ATS needs its employer tenant, never one shared host-wide key.
    p=urlsplit(url);parts=[x for x in p.path.split('/') if x]
    if host.endswith('.smartrecruiters.com') and parts:
        return dict(key='smartrecruiters:'+parts[0].lower(),adapter='smartrecruiters-review',tenant=parts[0],url=url)
    if host=='jobs.ashbyhq.com' and parts:
        return dict(key='ashby:'+parts[0].lower(),adapter='ashby-review',tenant=parts[0],url=url)
    return dict(key='official-host:'+host,adapter='universal-employer',tenant=None,url=url)


def build(companies,sources,catalog,scans,collection,progress,leads,base_commit,probe_report=None):
    by_company={c['id']:c for c in companies}
    source_by_id={s['id']:s for s in sources}
    probes={r['channel_key']:r for r in (probe_report or {}).get('rows',[])}
    owners=defaultdict(set)
    for company in companies:
        for sid in company.get('source_ids',[]):owners[sid].add(company['id'])
    # Older dedicated adapters omit company_id. Use the registry's explicit
    # one-to-one source mapping, never employer-name guesses or shared sources.
    source_company={sid:next(iter(cids)) for sid,cids in owners.items() if len(cids)==1
                    and source_by_id.get(sid,{}).get('company_id') in (None,next(iter(cids)))}
    jobs=defaultdict(list)
    for j in catalog['jobs']:
        cid=source_company.get(j['source_id'])
        if cid in by_company and j.get('internship_type')=='internship':jobs[cid].append(j)
    outcomes={r['company_id']:r for r in collection['employers']}
    names=defaultdict(set);keys=defaultdict(set)
    entries={};rejected=[]
    for c in companies:
        cid=c['id'];cs=set(c.get('target_countries',[]))&set(EU27)
        if not cs:continue
        row=dict(company_key=cid,name=c['name'],existing_company_id=cid,
                 research_countries=sorted(cs),country_basis='registry research targets; not workplace proof',
                 channels={},hr_evidence=[],size_evidence=[],identity_review_required=True,
                 existing_collection_state=outcomes.get(cid,{}).get('state','not-attempted'))
        for label in [c['name'],*c.get('aliases',[])]:
            if isinstance(label,str):names[name_key(label)].add(cid)
        urls=[c.get('career_url')]
        # Website-only companies remain discovery tasks, not fabricated channels.
        for sid in c.get('source_ids',[]):
            s=source_by_id.get(sid,{})
            urls.extend([s.get('career_url'),s.get('feed_url'),*s.get('start_urls',[])])
        for url in urls:
            ch=channel(url)
            if not ch:continue
            ch.setdefault('source_ids',[])
            for sid in c.get('source_ids',[]):
                s=source_by_id.get(sid,{})
                urls_s=[s.get('career_url'),s.get('feed_url'),*s.get('start_urls',[])]
                if any((channel(u) or {}).get('key')==ch['key'] for u in urls_s):ch['source_ids'].append(sid)
            ch.update(provenance=['registered-channel'],web_posting_urls=[],evidence_conflict=False)
            row['channels'].setdefault(ch['key'],ch)
            keys[ch['key']].add(cid)
        for j in jobs[cid]:
            s=source_by_id[j['source_id']];host=urlsplit(j['url']).hostname
            # Source-owned observed URLs are leads, not proof of a current opening.
            if host not in s.get('allowed_hosts',[]) or not channel(j['url']):continue
            row['hr_evidence'].append(dict(kind='historical-catalog',catalog_id=j['id'],title=j['title'],
                url=j['url'],countries=j.get('countries',[]),status=j['status'],
                reason=(j.get('verification') or {}).get('reason'),
                checked_at=(j.get('verification') or {}).get('checked_at'),source_id=j['source_id']))
        for field in ['friesland_research','drenthe_research','overijssel_research']:
            if isinstance(c.get(field),dict) and c[field].get('size'):row['size_evidence'].append(c[field]['size'])
        entries[cid]=row
    for scan in scans:
        cid=scan.get('company_id')
        if cid not in entries or scan.get('status')!='reviewed':continue
        c=by_company[cid]
        if scan.get('url') not in (c.get('website_url'),c.get('career_url')):continue
        # Cross-host redirects/embedded hints are not employer linkage proof.
        if urlsplit(scan.get('url','')).hostname!=urlsplit(scan.get('final_url','')).hostname:continue
        for url in scan.get('ats_links',[]):
            ch=channel(url)
            if not ch:continue
            ch.update(source_ids=[],provenance=['historical-official-page-scan'],
                      observed_from=scan['url'],web_posting_urls=[],evidence_conflict=False)
            entries[cid]['channels'].setdefault(ch['key'],ch);keys[ch['key']].add(cid)
    for lead in leads['leads']:
        ch=channel(lead['url'])
        if not ch or lead['country'] not in EU27:
            rejected.append(dict(url=lead['url'],reason='invalid URL, aggregator or non-EU target'));continue
        name_matches=names.get(name_key(lead['name']),set())
        channel_matches=keys.get(ch['key'],set())
        matches=name_matches|channel_matches
        # A shared tenant across known employers remains a review conflict.
        if len(name_matches)==1:
            cid=next(iter(name_matches))
        elif len(channel_matches)==1 and not name_matches:
            known_cid=next(iter(channel_matches))
            # Tenant reuse is a possible shared ATS, not proof that two names
            # identify the same legal employer. Repeated observations of our
            # same provisional lead can be joined; registry matches need review.
            cid=known_cid if known_cid.startswith('lead-') and name_key(entries[known_cid]['name'])==name_key(lead['name']) else 'lead-'+hashlib.sha256((name_key(lead['name'])+'|'+ch['key']).encode()).hexdigest()[:16]
        else:
            cid='lead-'+hashlib.sha256((name_key(lead['name'])+'|'+ch['key']).encode()).hexdigest()[:16]
        if cid not in entries:
            entries[cid]=dict(company_key=cid,name=lead['name'],existing_company_id=None,
                research_countries=[],country_basis='web posting workplace unless explicitly research-target-only',
                channels={},hr_evidence=[],size_evidence=[],identity_review_required=True,
                existing_collection_state='not-registered')
        row=entries[cid];row['research_countries']=sorted(set(row['research_countries'])|{lead['country']})
        ch.update(source_ids=[],provenance=['indexed-official-posting'],web_posting_urls=[],evidence_conflict=False)
        target=row['channels'].setdefault(ch['key'],ch)
        if lead['url'] not in target['web_posting_urls']:target['web_posting_urls'].append(lead['url'])
        if 'indexed-official-posting' not in target['provenance']:target['provenance'].append('indexed-official-posting')
        target['evidence_conflict']|=lead.get('page_open')=='404'
        if matches and matches!={cid}:target['shared_tenant_conflict']=sorted(matches)
        row['hr_evidence'].append(dict(kind='page-open' if lead.get('page_open')=='success' else 'indexed-search',
            title=lead['title'],url=lead['url'],countries=[lead['country']],
            country_basis=lead.get('country_evidence','research-target-only'),
            observed_on=lead.get('observed_on',leads['observed_on']),source_ref=lead['source_ref'],
            page_open=lead.get('page_open','not-attempted'),note=lead.get('note'),
            availability='unverified'))
        if lead.get('size_evidence'):row['size_evidence'].append(lead['size_evidence'])
        keys[ch['key']].add(cid)
    actions=[]
    for cid,row in entries.items():
        row['channels']=list(row['channels'].values())
        for ch in row['channels']:
            web=ch['web_posting_urls'];evidence=[e for e in row['hr_evidence'] if e['url'] in web or
                      (e.get('source_id') in ch['source_ids'])]
            current=[e for e in evidence if e.get('kind')=='historical-catalog' and e.get('status') not in ('closed','open')]
            open_existing=any(e.get('status')=='open' for e in evidence)
            existing_sources=[source_by_id[sid] for sid in ch['source_ids']]
            compatible=ch['adapter'] in SUPPORTED
            if web:action='new-employer-channel' if row['existing_company_id'] is None else ('existing-channel-new-evidence' if ch['source_ids'] else 'new-channel-existing-employer')
            elif current:action='existing-channel-recovery'
            elif compatible and not ch['source_ids']:action='new-channel-existing-employer'
            elif compatible and not any(s.get('adapter')==ch['adapter'] for s in existing_sources):action='adapter-upgrade-existing-employer'
            elif compatible and not open_existing:action='compatible-channel-screening'
            else:action='territorial-discovery'
            shared_owners=keys[ch['key']]
            preflight=probes.get(ch['key'])
            if preflight and preflight['url'] not in web:preflight=None
            probe_blocked=preflight and (preflight['state']=='not-established' or
                preflight['state']=='page-read-title-not-established' and ch['adapter']=='greenhouse')
            blocked=bool(ch['evidence_conflict'] or ch.get('shared_tenant_conflict') or len(shared_owners)>1 or probe_blocked)
            if not web:
                blocked|=row['existing_collection_state']=='blocked-or-failed'
                blocked|=bool(current) and all(BLOCK.search(e.get('reason') or '') for e in current)
            score=(100 if web else 50 if current else 10 if compatible else 0)+(30 if compatible else 0)
            if preflight and preflight['state']=='same-title-page-observed':score+=20
            observed_countries=sorted({c for e in evidence for c in e.get('countries',[]) if c in EU27 and e.get('country_basis')!='research-target-only'})
            action_row=dict(action_id=hashlib.sha256((cid+'|'+ch['key']).encode()).hexdigest()[:20],company_key=cid,
                name=row['name'],channel_key=ch['key'],channel_url=ch['url'],adapter=ch['adapter'],
                adapter_reusable=compatible,action=action,research_countries=row['research_countries'],
                vacancy_country_hints=observed_countries,country_coverage_verified=False,
                score=score,score_basis='100 indexed HR lead or 50 unverified catalog candidate or 10 compatible discovery; +30 reusable adapter; +20 same-title live page',
                hr_evidence=evidence,source_ids=ch['source_ids'],
                production_source_already_enabled=any(s.get('enabled') for s in existing_sources),
                access_review='not-performed-in-this-preparation',identity_review='required',
                enabled_by_this_queue=False,verified_vacancies_added=0,
                excluded_from_first_batch=blocked or action in ('existing-channel-recovery','compatible-channel-screening') or open_existing and not web,
                exclusion_reason='access restriction, live preflight failure or contradictory/shared identity evidence' if blocked else 'technical-recovery-backlog; not expansion' if action=='existing-channel-recovery' else 'already configured dedicated adapter; no incremental source' if action=='compatible-channel-screening' else 'already verified; no incremental lead' if open_existing and not web else None,
                budget_proposal=dict(max_requests=12,seconds=45,browser_renderings=0),
                next_action='Review official employer linkage and group identity, robots and current posting; then bounded inventory/application pilot. No host/rollout grant.',
                size_evidence=row['size_evidence'],size_band='unknown-unless-separately-reviewed')
            action_row['execution_lane']='adapter-review' if compatible else 'technical-discovery'
            action_row['integration_ready']=False
            if preflight:
                action_row['preflight']={k:preflight[k] for k in ('state','checked_at','title_match','applicant_form_present','error','final_url') if k in preflight}
                action_row['access_review']='one-page-preflight-only; no inventory/host/production grant'
            actions.append(action_row)
    actions.sort(key=lambda a:(a['excluded_from_first_batch'],-a['score'],a['company_key'],a['channel_key']))
    # Round-robin among the five countries, one employer/channel once overall.
    # Workplace hints take precedence; generic research targets are not coverage.
    selected=[];used_companies=set();used_channels=set();per=Counter()
    for _ in range(50):
        available=[]
        for country in FIRST:
            candidate=next((a for a in actions if not a['excluded_from_first_batch'] and a['score']>0
                and a['company_key'] not in used_companies and a['channel_key'] not in used_channels
                and country in (a['vacancy_country_hints'] or a['research_countries'])),None)
            if candidate:available.append((per[country],FIRST.index(country),country,candidate))
        if not available:break
        _,_,country,a=min(available,key=lambda x:(x[0],x[1]))
        a=dict(a,batch_country=country,rank=len(selected)+1)
        selected.append(a);used_companies.add(a['company_key']);used_channels.add(a['channel_key']);per[country]+=1
    country_progress={r['code']:r for r in progress['countries']}
    countries=[]
    for country in EU27:
        rows=[a for a in actions if country in a['research_countries']]
        countries.append(dict(code=country,first_batch_country=country in FIRST,
            baseline_target=100,
            existing_recent_complete_employers=country_progress.get(country,{}).get('companies_monitored_in_country',0),
            research_companies=sum(country in e['research_countries'] for e in entries.values()),channel_tasks=len(rows),
            new_web_hr_channel_tasks=sum(bool(a['hr_evidence']) and a['action']=='new-employer-channel' for a in rows),
            first_batch_tasks=per[country],research_complete=False,
            next_action='bounded-first-batch-review' if per[country] else 'discover official HR internship postings in local languages; do not assume existing group presence proves this country'))
    common=dict(schema_version=1,base_commit=base_commit,catalog_updated_at=catalog.get('updated_at'),
        collection_generated_at=collection.get('generated_at'),mode='offline-preparation-no-production-changes',
        source_observations_on=leads['observed_on'],new_live_verified=0,
        country_is='research target or explicitly labelled posting hint; never verified national coverage',
        preparation_cost=dict(search_queries=leads['search_queries'],page_open_attempts=leads['page_open_attempts'],
            collector_requests=(probe_report or {}).get('summary',{}).get('requests',0),collector_renderings=0,
            probe_summary=(probe_report or {}).get('summary'),monetary_cost=None),
        inputs=['data/companies.json','data/sources.json','data/catalog.json','docs/career-channel-scan.json',
            'data/employer-collection.json','docs/country-research-progress.json','docs/eu27-expansion/web-leads-2026-11-15.json'])
    # Full evidence is kept in the first batch and the source inputs. The
    # all-country index stores references, not another copy of the catalog.
    compact=[]
    for a in actions:
        row={key:a[key] for key in ('action_id','company_key','name','channel_key','channel_url','adapter','action','research_countries','vacancy_country_hints','score','source_ids','excluded_from_first_batch','exclusion_reason','execution_lane')}
        row['evidence_refs']=[e.get('catalog_id') or e['url'] for e in a['hr_evidence']]
        compact.append(row)
    queue=dict(common,countries=countries,summary=dict(companies=len(entries),channel_tasks=len(actions),
        new_web_employers=sum(e['existing_company_id'] is None for e in entries.values()),
        web_posting_observations=len(leads['leads']),rejected_web_leads=len(rejected)),actions=compact,rejected_web_leads=rejected,
        source_discovery_required=[dict(company_key=cid,name=e['name'],research_countries=e['research_countries']) for cid,e in entries.items() if not e['channels']])
    batch=dict(common,scope=list(FIRST),target_channel_count=50,actual_channel_count=len(selected),
        summary=dict(by_country=dict(per),by_action=dict(Counter(a['action'] for a in selected)),
            by_adapter=dict(Counter(a['adapter'] for a in selected)),
            with_web_hr_lead=sum(any(e['kind'] in ('indexed-search','page-open') for e in a['hr_evidence']) for a in selected),
            with_catalog_hr_lead=sum(any(e['kind']=='historical-catalog' for e in a['hr_evidence']) for a in selected),
            reusable_adapter_with_web_hr_lead=sum(a['adapter_reusable'] and any(e['kind'] in ('indexed-search','page-open') for e in a['hr_evidence']) for a in selected),
            size_unqualified=sum(a['size_band'].startswith('unknown') for a in selected)),
        proposed_pilot_budget_upper_bound=dict(max_requests=sum(a['budget_proposal']['max_requests'] for a in selected),
            source_seconds=sum(a['budget_proposal']['seconds'] for a in selected),browser_renderings=0,
            measured=False,description='Maximum ceilings for a later authorized bounded pilot, not actual cost or approved rollout'),
        rows=selected)
    batch['adapter_proposals']=[]
    for a in selected:
        if a['action']!='new-employer-channel' or not a['adapter_reusable']:continue
        parsed=identify_channel(a['channel_url'])
        proposal=dict(action_id=a['action_id'],name=a['name'],adapter=a['adapter'],
            observed_tenant=parsed['tenant'],observed_url=a['channel_url'],
            approved_for_production=False,enabled=False,
            required_reviews=['employer-to-ATS linkage and group ownership','robots/access for exact feed and vacancy hosts',
                'bounded inventory completeness and geography','same-vacancy application and freshness','language/intake/type requirements','documented size if known'],
            next_step='review and bounded pilot; do not load this proposal as a production source')
        if a['adapter']=='personio-xml':proposal['candidate_feed_url']='https://'+parsed['tenant']+'/xml'
        elif a['adapter']=='recruitee':proposal['candidate_feed_url']='https://'+parsed['tenant']+'/api/offers/'
        else:proposal['candidate_board']=parsed['tenant']
        batch['adapter_proposals'].append(proposal)
    return queue,batch


def render(queue,batch):
    lines=['# People Placement — coda UE27 e lotto 01','',
        'Coda generata offline con preflight live circoscritto separato; nessuna nuova fonte attiva, nessuna raccolta completa, nessuna nuova candidatura verificata.',
        'Le osservazioni web sono indizi e possono essere scadute. Paesi candidati, sedi delle vacancy e copertura operativa restano distinti.','',
        f"Base: `{queue['base_commit']}`; catalogo: {queue['catalog_updated_at']}; esiti raccolta: {queue['collection_generated_at']}.",'',
        f"Coda: {queue['summary']['companies']} identità di ricerca e {queue['summary']['channel_tasks']} attività su canali. "
        f"Nuove identità da rivedere: {queue['summary']['new_web_employers']}. Non sono aziende uniche giuridicamente accertate.",'',
        f"Lotto: {batch['actual_channel_count']} canali, una sola attività per datore e tenant; "
        f"{batch['summary']['with_web_hr_lead']} con nuovi indizi web HR, {batch['summary']['with_catalog_hr_lead']} con indizi di catalogo (possibile sovrapposizione).",'',
        f"{len(batch['adapter_proposals'])} bozze di adattatore riutilizzabile preparate in `batch-01.json`, tutte disabilitate e con review mancanti esplicite. "
        f"Obiettivo iniziale: {batch['target_channel_count']} canali; mancano {batch['target_channel_count']-batch['actual_channel_count']} candidati ammissibili, senza riempire il lotto con connettori già attivi o recuperi tecnici.",'',
        '## Paesi','', '| Paese | Datori operativi nel report corrente | Datori candidati | Attività canali | Lotto 01 |', '|---|---:|---:|---:|---:|']
    for c in queue['countries']:lines.append(f"| {c['code']} | {c['existing_recent_complete_employers']} | {c['research_companies']} | {c['channel_tasks']} | {c['first_batch_tasks']} |")
    lines+=['','## Primo lotto','', '| # | Paese del lotto | Datore | Canale | Attività | Indizio HR |','|---|---|---|---|---|---|']
    for a in batch['rows']:
        title=(a['hr_evidence'][0]['title'] if a['hr_evidence'] else 'Nessuna vacancy HR osservata; screening del canale').replace('|','/')
        lines.append(f"| {a['rank']} | {a['batch_country']} | {a['name']} | [{a['adapter']}]({a['channel_url']}) | {a['action']} | {title} |")
    lines+=['','## Ordine di esecuzione e limiti','',
        '1. Nuovi canali Recruitee/Personio/Lever/Greenhouse con indizi HR: verificare collegamento dal datore, identità/gruppo e robots; leggere inventario e candidatura nel perimetro consentito.',
        '2. Canali già censiti: includere solo un nuovo canale o conversione dal crawler generico a un connettore dedicato. Connettori dedicati già configurati e recuperi tecnici sono esclusi dal lotto di espansione.',
        '3. TikTok/Workday e gli altri host generici sono una coda tecnica separata; un riconoscimento ATS non autorizza host o rendering.',
        '4. Contraddizioni: Fidelity ha un hit indicizzato ma apertura 404; esclusa dal lotto operativo, conservata nella coda per ricercare un inventario attuale.',
        '5. Non iniziare dalle pagine di candidatura /c/new: risalire alla vacancy e confermare stessa identità. Alternance, HRIS consulenziale e ruoli misti richiedono classificazione.',
        '6. Dimensioni: tutti i band restano non qualificati in questa preparazione; soglie minime 55+ o 350+ non provano un intervallo 50–249 o 250–999. La quota PMI prevista dalla strategia non è ancora dimostrata dal lotto.',
        '7. Costo proposto per il futuro pilota: massimo 12 richieste/45 secondi per canale, senza browser; soglie da validare contro inventario e policy del singolo host. Il lotto non abilita né schedula quel pilota.',
        '8. Fermare un canale bloccato senza fermare gli altri. Produrre una PR di integrazione solo per fonti con prove sufficienti; merge/rollout separati.',
        '9. Misurare nei cicli ordinari autorizzati nuove candidature aperte distinte, freschezza e richieste/tempo per fonte. Nessun conteggio di lead sostituisce questo risultato.','',
        '## Riproduzione','', '`python3 scripts/build_eu27_expansion_queue.py`', '',
        'I report `probe-2026-11-16*.json` conservano il preflight originario e sei nuovi indizi successivi: un GET per pagina osservata, robots rispettato, scope redirect esatto, nessun browser o verifica di candidatura. La generazione della coda li legge senza ripetere le richieste.','',
        'I JSON includono score, evidenze, riferimenti, source ID esistenti, esclusioni, budget proposti e 27 attività nazionali ancora incomplete. Nessuna richiesta di rete viene eseguita.',
        'La coda completa è versionata come `queue.json.gz`; il comando rigenera anche `queue.json` leggibile. Questo evita di duplicare oltre un megabyte di dati derivati nel diff.','']
    return '\n'.join(lines)


def main():
    read=lambda p:json.loads((ROOT/p).read_text())
    import subprocess
    # A commit of these generated documents must not change input provenance.
    base=subprocess.check_output(['git','log','-1','--format=%H','--',
        'data/companies.json','data/sources.json','data/catalog.json',
        'docs/career-channel-scan.json','data/employer-collection.json',
        'docs/country-research-progress.json'],cwd=ROOT,text=True).strip()
    probe_reports=[read(p.relative_to(ROOT)) for p in sorted((ROOT/'docs/eu27-expansion').glob('probe-2026-11-16*.json'))]
    combined=None
    if probe_reports:
        results=sorted([r for report in probe_reports for r in report['rows']],key=lambda r:r['checked_at'])
        latest={r['channel_key']:r for r in results}
        combined=dict(rows=list(latest.values()),summary=dict(
            employers=len(latest),page_probe_attempts=len(results),
            requests=sum(r['requests'] for r in results),
            bytes_read=sum(r['bytes_read'] for r in results),
            source_seconds=round(sum(r['duration_seconds'] for r in results),3),
            wall_seconds_separate_runs=round(sum(report['summary']['wall_seconds'] for report in probe_reports),3),
            same_title_pages=sum(r['state']=='same-title-page-observed' for r in latest.values()),
            new_verified=0,new_enabled_sources=0))
    queue,batch=build(read('data/companies.json'),read('data/sources.json'),read('data/catalog.json'),
        read('docs/career-channel-scan.json'),read('data/employer-collection.json'),
        read('docs/country-research-progress.json'),read('docs/eu27-expansion/web-leads-2026-11-15.json'),base,combined)
    folder=ROOT/'docs/eu27-expansion';folder.mkdir(exist_ok=True)
    # One task per line keeps the large index reviewable without tens of
    # thousands of repeated default-field lines.
    index=dict(queue);actions=index.pop('actions')
    header=json.dumps(index,ensure_ascii=False,indent=2).rstrip()[:-1]
    (folder/'queue.json').write_text(header+',"actions":[\n'+',\n'.join(json.dumps(a,ensure_ascii=False,separators=(',',':')) for a in actions)+'\n]}\n')
    (folder/'queue.json.gz').write_bytes(gzip.compress((folder/'queue.json').read_bytes(),mtime=0))
    (folder/'batch-01.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
    (folder/'README.md').write_text(render(queue,batch))
    print(json.dumps(dict(queue=queue['summary'],batch=batch['summary'],count=batch['actual_channel_count']),ensure_ascii=False))


if __name__=='__main__':main()
