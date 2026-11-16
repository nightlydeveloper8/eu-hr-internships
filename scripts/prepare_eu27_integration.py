"""Prepare a disabled integration bundle from bounded reviews, offline only.

Never changes data/companies.json, data/sources.json or data/catalog.json.
The bundle is deliberately outside the runtime registry: inserting a company
with no enabled source would trigger daily.provision's generic crawler.
"""
from collections import Counter
from datetime import datetime
import gzip,json,sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from collector.company_registry import company_key
from collector.classify import canonical_url,classify_role,workplace_languages,language_summary
from collector.public_feeds import recruitee_records
from collector.intake import extract_intake
from collector.verification import verify_vacancy


def prepare(scratch=Path('/tmp/pp-eu27-feed-review-20261116')):
    folder=ROOT/'docs/eu27-expansion';read=lambda name:json.loads((folder/name).read_text())
    feeds=read('feed-review-2026-11-16.json');batch=read('batch-01.json')
    ownership=[read(name) for name in ['ownership-review-2026-11-16.json','ownership-review-2026-11-16-addendum.json']]
    applications=[read(name) for name in ['strict-application-review-2026-11-16.json','strict-application-review-2026-11-16-addendum.json']]
    owned={r['name']:r for report in ownership for r in report['rows'] if r['ownership_state']=='exact-employer-page-ats-link-observed'}
    apps={r['name']:r for report in applications for r in report['rows'] if r['proofs']}
    proposal={r['name']:r for r in batch['adapter_proposals']}
    existing_companies=json.loads((ROOT/'data/companies.json').read_text());existing_sources=json.loads((ROOT/'data/sources.json').read_text());catalog=json.loads((ROOT/'data/catalog.json').read_text())
    existing_ids={c['id'] for c in existing_companies};source_ids={s['id'] for s in existing_sources}
    existing_urls={canonical_url(j['url']) for j in catalog['jobs']}
    rows=[];companies=[];sources=[];jobs=[]
    for row in feeds['rows']:
        name=row['name'];result=dict(name=name,action_id=row['action_id'],inventory=row['inventory_state'],records=row.get('records'),
            hr_student_roles=len(row['jobs']),ownership_confirmed=name in owned,admissible=False,reasons=[])
        if row['inventory_state']!='complete-feed-read':result['reasons'].append(row.get('error','Feed incomplete'))
        if name not in owned:result['reasons'].append('Official employer→exact ATS relationship not established by this review')
        if name not in apps:result['reasons'].append('No strict visible same-posting application proof')
        if not row['jobs']:result['reasons'].append('No HR student role classified from feed; indexed vacancy is not a substitute. HRIS may require classification review.')
        if name in owned and name in apps and row['inventory_state']=='complete-feed-read':
            cid=company_key(name);sid='recruitee-'+cid
            if cid in existing_ids or sid in source_ids:raise ValueError('Existing identity must be reconciled, not overwritten: '+name)
            s=dict(row['source_proposal'],id=sid,company_id=cid,application_check='recruitee-linked',
                enabled=False,report_feed_scope=True,target_countries=sorted({c for j in row['jobs'] for c in j['countries']}),
                reviewed_on='2026-11-16',permission_basis='Official corporate page publishes exact tenant; public offers feed and observed application entry; robots enforced each request',
                discovery_scope='All published offers returned by the reviewed feed; actual posting geography and role determine inclusion')
            source=proposal[name];corp=owned[name]
            companies.append(dict(id=cid,name=name,website_url=corp['url'],career_url=source['observed_url'],
                evidence_url=corp['url'],source_ids=[sid],target_countries=s['target_countries'],
                workplaces=[],review_status='publication-identity-reviewed',
                group_identity='not asserted beyond reviewed publishing scope',size={'qualification':'unknown'},
                hr_internship_evidence='live bounded review; not a production catalog entry'))
            sources.append(s)
            for a in apps[name]['proofs']:
                # Re-run the final strict code on the already captured documents
                # without renewing any timestamp or calling the network.
                event=next(e for e in row['events'] if '/api/offers' in e['url'] and e.get('scratch_file'))
                feed=gzip.decompress((scratch/row['action_id']/event['scratch_file']).read_bytes())
                class Feed:
                    def request(self,url):return feed,200,event['final_url']
                record=next(x for x in recruitee_records(s,Feed()) if x['external_id']==a['posting_identifier'])
                phase='strict-application-addendum' if name=='Ibexa' else 'strict-application-phase'
                responses={canonical_url(e['url']):e for e in apps[name]['events'] if e.get('scratch_file')}
                class Replay:
                    def request(self,url):
                        e=responses[canonical_url(url)];body=gzip.decompress((scratch/phase/row['action_id']/e['scratch_file']).read_bytes())
                        return body,e['status'],e['final_url']
                proof=verify_vacancy(record,s,Replay(),row['checked_at'])
                role=classify_role(record['title'],record['text'],record.get('employment',''))
                if not role or role['internship_type']!='internship':raise ValueError('Not an internship: '+name)
                jobs.append(dict(employer=name,company_id=cid,source_id=sid,title=a['title'],url=record['url'],
                    application_url=proof['url'],posting_identifier=a['posting_identifier'],countries=a['countries'],city=record.get('city'),
                    method=proof['method'],original_feed_checked_at=row['checked_at'],
                    final_code_replayed_without_renewing_evidence=True,
                    workplace_languages=workplace_languages(record['text']),
                    intake=extract_intake(record['text'],row['checked_at']),
                    already_in_catalog=canonical_url(record['url']) in existing_urls,
                    published_in_production=False))
            result.update(admissible=True,reasons=[],source_id=sid)
        rows.append(result)
    costs=dict(requests=feeds['summary']['requests']+sum(r['summary']['additional_requests'] for r in ownership)+sum(r['summary']['requests'] for r in applications),
        source_seconds=round(feeds['summary']['source_seconds']+sum(r['summary']['source_seconds'] for r in ownership+applications),3),
        wall_seconds_separate_phases=round(feeds['summary']['wall_seconds']+sum(r['summary']['wall_seconds'] for r in ownership+applications),3),
        renderings=0,web_search_queries=16,web_open_find_commands=7,monetary_cost=None)
    bundle=dict(schema_version=1,mode='reviewed-disabled-integration-bundle',reviewed_on='2026-11-16',
        runtime_reads_this_file=False,activation_authorized=False,
        warning='Do not add these disabled companies alone: daily.provision would auto-enable generic sources. Apply company+reviewed-source atomically only under explicit activation authorization.',
        companies=companies,sources=sources,reviewed_internships=jobs,
        summary=dict(proposals_reviewed=len(rows),admissible_sources=len(sources),live_same_posting_internships=len(jobs),
            distinct_new_catalog_urls=sum(not j['already_in_catalog'] for j in jobs),production_sources_enabled=0,production_catalog_delta=0),
        costs=costs,remaining=rows)
    (folder/'reviewed-integration-bundle.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    lines=['# Verifica dei 29 canali UE27','',
        f"**{len(sources)} fonti ammissibili preparate, {len(jobs)} stage distinti con prova live e candidatura visibile.** Nessuna fonte attivata e nessun annuncio aggiunto al sito.",'',
        'Le vecchie 10 prove tecniche non sono 10 stage verificati: le offerte Recruitee possono includere un modulo in una scheda nascosta. Il controllo nuovo richiede l’URL pubblicato nel feed, lo stesso ID/titolo/datore e un modulo visibile abilitato. È opt-in per le nuove fonti; i connettori esistenti non cambiano.','',
        '| Datore | Paese | Stage | Candidatura |','|---|---|---|---|']
    for j in jobs:lines.append(f"| {j['employer']} | {', '.join(j['countries'])} | {j['title']} | [Pagina ufficiale]({j['application_url']}) |")
    lines+=['','## Esito di tutte le proposte','','| Datore | Inventario letto | Ruoli HR studenti classificati | Ammissibile | Lavoro mancante |','|---|---:|---:|---|---|']
    for r in rows:lines.append(f"| {r['name']} | {r.get('records') if r.get('records') is not None else 'non stabilito'} | {r['hr_student_roles']} | {'sì, non attiva' if r['admissible'] else 'no'} | {'; '.join(r['reasons']) or 'Attivazione separata; dimensioni societarie sconosciute'} |")
    lines+=['','## Costi e limiti','',
        f"29 feed tentati, 21 letti dall’adattatore, 366 record, 20 ruoli HR per studenti classificati. Totale delle fasi: {costs['requests']} richieste logiche, {costs['source_seconds']} secondi-fonte, {costs['wall_seconds_separate_phases']} secondi a muro cumulati dei processi, zero rendering. Le richieste comprendono robots; i redirect non hanno un contatore HTTP separato.",'',
        'Quattro fonti hanno risposto 429, senza nuovi tentativi. XML Personio 404 non aggirati. Nessun CAPTCHA, login o invio di candidatura. La pubblicazione resta subordinata al merge/rollout autorizzato e alle nuove letture della raccolta ordinaria; non si importano nel catalogo snapshot o replay di questo pilota.','',
        'Collegamenti societari e dimensioni non sono qualificati come PMI. LOOK UP SPACE è uno stage di diritto sociale a supporto HR: il sottotipo resta esplicito. Altares e Toreon non presentano lo stage HR indicizzato nel feed corrente; non è prova generale della chiusura. threon HRIS richiede review della classificazione; l’assenza dal filtro non prova zero stage HR.','',
        'Il bundle è fuori dai registri runtime. Aggiungere solo aziende con fonti disabilitate attiverebbe il provisioner generico: l’eventuale integrazione autorizzata deve applicare aziende e fonti approvate in modo atomico. Nessuna nuova schedulazione.','',
        '## Riproduzione offline','','`python3 scripts/prepare_eu27_integration.py` richiede i raw GET temporanei usati per le prove e non effettua rete. Le fixture ridotte reali e i test validano il controllo riutilizzabile senza richiedere quei raw file.','']
    (folder/'REVIEW.md').write_text('\n'.join(lines))
    print(json.dumps(dict(summary=bundle['summary'],costs=costs),ensure_ascii=False))

if __name__=='__main__':prepare()
