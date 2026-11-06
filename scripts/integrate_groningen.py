"""Idempotently integrate reviewed Groningen research into the shared registries.

Run after updating docs/groningen-research-{city,municipalities}.json. Unknown
localities and ambiguous matches fail instead of assigning a guessed municipality.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.pipeline import ROOT,read,write
from scripts.integrate_province import integrate_employers


def integrate(companies,sources,geography,rows):
    companies,sources,regional=integrate_employers(companies,sources,geography,rows,slug='groningen')
    source_by_id={s['id']:s for s in sources}
    def configure(cid,**fields):
        company=next(c for c in companies if c['id']==cid)
        source=source_by_id[company['source_ids'][0]];source.update(fields)
        source.update(access_reviewed_on='2026-11-06',permission_basis='Official employer-published public listings and linked application pages; robots and approved hosts checked on every read; no forms submitted')
    configure('hanos',adapter='employer-index',index_urls=['https://www.werkenbijhanos.nl/werkgebieden/HR'],job_url_pattern=r'^https://www\.werkenbijhanos\.nl/vacatures/[^/?]+-\d+$',application_check='hanos-rendered',report_index_scope=True,inventory_scope_complete=True,discovery_scope='All four observed job links in the official HR department list; excludes other departments and group brands.',max_requests=100,collection_seconds=160)
    configure('ikea-ingka-group',adapter='employer-index',allowed_hosts=['jobs.ikea.com','ikea.avature.net'],index_urls=['https://jobs.ikea.com/en/location/jobs/22908/2750405-2755249-2755251/4/1'],job_url_pattern=r'^https://jobs\.ikea\.com/en/job/groningen/[^/]+/\d+/\d+$',index_job_count_pattern=r'(\d+) jobs in Groningen',employer_tokens=['ingka'],application_check='avature-linked',report_index_scope=True,inventory_scope_complete=True,discovery_scope='Official Groningen city list, all observed postings; link count must equal the live published total. Province sites outside the city require separate discovery.',max_requests=100,collection_seconds=180)
    configure('fotofabriek',adapter='employer-index',index_urls=['https://www.werkenbijfotofabriek.nl/jobs'],job_url_pattern=r'^https://www\.werkenbijfotofabriek\.nl/jobs/detail/[^/?]+-\d+$',job_id_pattern=r'-(\d+)$',index_page_pattern=r'^https://www\.werkenbijfotofabriek\.nl/jobs/page/\d+\?',page_format='odoo-visible',reviewed_workplace_labels={'Fotofabriek':dict(city='Groningen',country='NL',address_evidence='Osloweg 75, 9723 BJ Groningen')},application_check='odoo',report_index_scope=True,inventory_scope_complete=True,discovery_scope='Official HTML vacancy list and all observed numbered pages; each form identifies vacancy and workplace label, resolved to the published Groningen campus address.',max_requests=140,collection_seconds=240)
    # Shared group feed already exists. Reuse it for the parent and shipyard;
    # do not download or count a second group feed.
    shared='auto-wagenborg-passagiersdiensten'
    if shared in source_by_id:
        source_by_id[shared]['employer']='Royal Wagenborg'
        wpd=next(c for c in companies if c['id']=='wagenborg-passagiersdiensten')
        wpd['aliases']=sorted(set(wpd.get('aliases',[])+['Royal Wagenborg']))
        removed=set()
        for cid in ('royal-wagenborg','royal-niestern-sander'):
            company=next(c for c in companies if c['id']==cid)
            removed.update(sid for sid in company['source_ids'] if sid!=shared);company['source_ids']=[shared]
        sources=[s for s in sources if s['id'] not in removed]
    return companies,sources,regional


def main():
    rows=[]
    for filename in ('groningen-research-city.json','groningen-research-municipalities.json'):
        rows.extend(read(ROOT/'docs'/filename,{})['employers'])
    companies,sources,regional=integrate(read(ROOT/'data/companies.json',[]),read(ROOT/'data/sources.json',[]),read(ROOT/'data/groningen-geography.json',{}),rows)
    write(ROOT/'data/companies.json',companies);write(ROOT/'data/sources.json',sources)
    write(ROOT/'data/groningen-employers.json',regional)
    print(len(regional),'provincial employers;',sum(r['size']['qualification']=='verified_50_plus' for r in regional),'qualified')

if __name__=='__main__':main()
