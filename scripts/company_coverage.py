"""Produce geographic research priorities and monitorable-company coverage."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.pipeline import read,write,now
from collector.company_registry import coverage_report,discovery_queue,discover_channels,country_research_progress,integration_queue
from collector.adapters import Client

ROOT=Path(__file__).resolve().parents[1]
def generate():
    companies=read(ROOT/'data/companies.json',[]);geography=read(ROOT/'data/geography.json',{});sources=read(ROOT/'data/sources.json',[]);jobs=read(ROOT/'data/catalog.json',{}).get('jobs',[])
    report=coverage_report(companies,geography,sources,jobs,now())
    plan=read(ROOT/'data/employer-research-plan.json',{})
    runs=read(ROOT/'data/coverage.json',{}).get('sources',[])
    progress=country_research_progress(companies,sources,plan,runs,report['generated_at'])
    for country in report['countries']:
        country.update(next(p for p in progress if p['code']==country['code']))
    write(ROOT/'docs/company-integration-queue.json',integration_queue(companies,sources,runs))
    write(ROOT/'docs/country-research-progress.json',dict(counting_basis=plan['counting_basis'],countries=progress))
    write(ROOT/'data/company-coverage.json',report);write(ROOT/'docs/company-discovery-queue.json',discovery_queue(geography,report,plan))
    print(report['company_count'],'companies;',report['monitored_companies'],'monitored;',len(report['regions']),'regional research areas')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--inspect-country');parser.add_argument('--limit',type=int,default=10);args=parser.parse_args()
    if args.inspect_country:
        companies=read(ROOT/'data/companies.json',[]);client=Client();results=[]
        for company in [c for c in companies if args.inspect_country in c.get('target_countries',[]) or any(p['country']==args.inspect_country for p in c.get('workplaces',[]))][:max(0,args.limit)]:
            row={'company_id':company['id'],'checked_at':now()}
            try:row.update(status='reviewed',proposed_channels=discover_channels(company,client))
            except Exception as exc:row.update(status='access-or-layout-review-required',error=str(exc)[:250])
            results.append(row)
        write(ROOT/'docs/company-channel-review.json',results)
    generate()
