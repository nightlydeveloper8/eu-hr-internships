"""Import an annual CBS province research frame, separately from daily collection."""
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
import re
from pathlib import Path
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.classify import fold
from collector.pipeline import ROOT, write

BASE = 'https://opendata.cbs.nl/ODataApi/OData/'


def rows(table, entity):
    url = BASE + table + '/' + entity
    result, seen = [], set()
    while url:
        if url in seen or urlsplit(url).hostname != 'opendata.cbs.nl':
            raise ValueError('Unexpected CBS pagination')
        seen.add(url)
        with urlopen(Request(url, headers={'Accept': 'application/json'}), timeout=60) as response:
            payload = json.load(response)
        result.extend(payload['value'])
        url = payload.get('odata.nextLink') or payload.get('@odata.nextLink')
    return result


def build(areas, links, names, province_code, nuts_code, checked_on):
    municipalities = {}
    for row in areas:
        if row['Code_28'].strip() != province_code or not row['Code_1'].strip().startswith('GM'):
            continue
        code = row['Code_1'].strip()
        municipalities[code] = dict(cbs_code=code, name=row['Naam_2'].strip(), province_code=province_code,
            province_name=row['Naam_29'].strip(), corop_code=row['Code_10'].strip(),
            corop_name=row['Naam_11'].strip(), inhabitants=row.get('Inwonertal_56'), settlements=[])
    name_for = {row['Key'].strip(): row['Title'].strip() for row in names}
    occurrences = defaultdict(list)
    for row in links:
        code = row['Woonplaatscode_1'].strip()
        name = name_for[code]
        search_name=re.sub(r'\s+(?:gn|nb|zh|nh|fr|gld|ov|dr|ut|lb|zld)$','',fold(name))
        occurrences[search_name].append(dict(name=name, municipality=row['Naam_2'].strip(),
            municipality_code=row['Code_3'].strip(), province=row['Naam_4'].strip(), province_code=row['Code_5'].strip()))
        if row['Code_5'].strip() != province_code:
            continue
        municipality = municipalities[row['Code_3'].strip()]
        if municipality['name'] != row['Naam_2'].strip():
            raise ValueError('CBS municipality tables disagree')
        municipality['settlements'].append(dict(code=code, name=name,
            search_name_variants=list(dict.fromkeys([name, fold(name), search_name]))))
    if not municipalities or not all(m['settlements'] for m in municipalities.values()):
        raise ValueError('Incomplete province frame')
    for municipality in municipalities.values():
        municipality['settlements'].sort(key=lambda p: fold(p['name']))
        municipality['settlement_count'] = len(municipality['settlements'])
        municipality['search_name_variants'] = [municipality['name']]
    ambiguous = [dict(name=items[0]['name'], occurrences=items,
        note='Require municipality/postcode or official street address; name alone is insufficient.')
        for items in occurrences.values() if len(items) > 1 and any(p['province_code'] == province_code for p in items)]
    province_name = next(iter(municipalities.values()))['province_name']
    settlements = sum(m['settlement_count'] for m in municipalities.values())
    return dict(schema_version=1, province=dict(official_name=province_name, cbs_code=province_code,
        nuts2_code=nuts_code, nuts_note='Province NUTS2 code; municipalities use CBS GM codes.'),
        checked_on=checked_on, administrative_reference_date='2026-01-01', municipality_count=len(municipalities),
        settlement_count=settlements, composition_status='complete-official-2026-municipal-membership',
        sources=dict(cbs_areas_table='https://www.cbs.nl/nl-nl/cijfers/detail/86247NED',
            cbs_settlements_table='https://www.cbs.nl/nl-nl/cijfers/detail/86312NED'),
        api_sources=dict(municipalities=BASE+'86247NED/TypedDataSet', settlement_links=BASE+'86312NED/TypedDataSet',
            settlement_names=BASE+'86312NED/Woonplaatsen'),
        import_audit=dict(national_area_rows=len(areas), national_settlement_rows=len(links),
            national_settlement_names=len(names), unique_provincial_settlement_codes=settlements),
        municipalities=sorted(municipalities.values(), key=lambda m: fold(m['name'])),
        ambiguous_settlement_names=ambiguous,
        name_disambiguation=['Groningen can mean the province, municipality or city; a provincial mention alone is not a city workplace.',
            'CBS suffixes such as Haren Gn, Harkstede GN and Lageland GN remain in statutory lookup names. Unsuffixed search variants require municipality/address confirmation.',
            'Former municipality names (for example Delfzijl, Leek, Haren) are not current CBS municipality assignments.'],
        limitations=['CBS annual BAG snapshot at 1 January 2026, provisional; not live boundary geometry.',
            'Search variants are normalisations, not alternative statutory names.',
            'A complete geographic frame does not establish a complete employer census.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--province-code', default='PV20')
    parser.add_argument('--nuts-code', default='NL11')
    parser.add_argument('--output', type=Path, default=ROOT/'data/groningen-geography.json')
    args = parser.parse_args()
    report = build(rows('86247NED', 'TypedDataSet'), rows('86312NED', 'TypedDataSet'),
        rows('86312NED', 'Woonplaatsen'), args.province_code, args.nuts_code, date.today().isoformat())
    write(args.output, report)
    print(report['province']['official_name'], report['municipality_count'], 'municipalities;', report['settlement_count'], 'settlements')


if __name__ == '__main__':
    main()
