"""Import names/codes only from the official Eurostat GISCO NUTS 2024 attribute table."""
import argparse,csv,io,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collector.classify import COUNTRIES, EU27
from collector.adapters import Client
from collector.pipeline import now,write

URL='https://gisco-services.ec.europa.eu/distribution/v2/nuts/csv/NUTS_AT_2024.csv'
ITL1={'TLC':'North East (England)','TLD':'North West (England)','TLE':'Yorkshire and The Humber','TLF':'East Midlands (England)','TLG':'West Midlands (England)','TLH':'East of England','TLI':'London','TLJ':'South East (England)','TLK':'South West (England)','TLL':'Wales','TLM':'Scotland','TLN':'Northern Ireland'}

def convert(csv_text):
    units=[]
    for row in csv.DictReader(io.StringIO(csv_text)):
        country={'EL':'GR'}.get(row['CNTR_CODE'],row['CNTR_CODE'])
        if country not in COUNTRIES:continue
        code=row['NUTS_ID'];level=len(code)-2
        if level not in range(4):continue
        units.append(dict(code=code,country=country,level=level,parent=code[:-1] if level else None,name=row['NUTS_NAME'],latin_name=row['NAME_LATN'],extra_region='extra-regio' in row['NAME_LATN'].lower()))
    if {u['country'] for u in units}!=set(EU27)|{'CH'}:raise ValueError('Not all EU27 countries and Switzerland present')
    # The UK left NUTS: its International Territorial Level 1 regions (ONS, ITL 2021) are added by hand.
    units.append(dict(code='GB',country='GB',level=0,parent=None,name='United Kingdom',latin_name='United Kingdom',extra_region=False))
    for code,name in ITL1.items():units.append(dict(code=code,country='GB',level=1,parent='GB',name=name,latin_name=name,extra_region=False))
    codes={u['code'] for u in units}
    codes|={'GB'}|set(ITL1)
    if any(u['parent'] and u['parent'] not in codes for u in units):raise ValueError('Broken geographic hierarchy')
    return {'schema_version':1,'classification':'NUTS 2024','imported_at':now(),'source_url':URL,'attribution':'Source: European Commission, Eurostat/GISCO, NUTS 2024 attribute table (EU-27 and Switzerland); United Kingdom: ONS International Territorial Levels (ITL 2021), level 1. Names and codes only; no boundary geometries.','licence_reference':'https://ec.europa.eu/eurostat/web/main/help/copyright-notice','administrative_note':'NUTS statistical levels do not have identical administrative meanings in every country. Dutch provinces are level 2; level 3 is a smaller statistical area.','units':sorted(units,key=lambda u:u['code'])}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--from-csv');args=p.parse_args()
    raw=Path(args.from_csv).read_text() if args.from_csv else Client().request(URL)[0].decode('utf-8-sig')
    result=convert(raw);write(Path(__file__).resolve().parents[1]/'data/geography.json',result)
    from collections import Counter
    print(dict(Counter(u['level'] for u in result['units'])))
