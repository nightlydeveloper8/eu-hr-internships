"""Run every configured provincial source, retaining the rest of the shared catalog."""
import argparse,logging,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.daily import collect_shard
from collector.pipeline import ROOT,read,finalize,now
from collector.provinces import generate_province


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('province',choices=['friesland','groningen','drenthe','utrecht'])
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    companies=read(ROOT/'data/companies.json',[])
    ids=sorted({sid for company in companies if company.get(args.province+'_research') for sid in company['source_ids']})
    payload=collect_shard(shards=1,workers=args.workers,source_ids=ids,
        output=ROOT/'.staging'/args.province/'collection.json')
    sources=read(ROOT/'data/sources.json',[])
    selected=[s for s in sources if s['id'] in ids and s.get('enabled')]
    finalize(sources,selected,read(ROOT/'data/catalog.json',{}),read(ROOT/'data/coverage.json',{}),
        payload['parts'],now(),ROOT/'data')
    print(generate_province(args.province)['summary'])


if __name__=='__main__':main()
