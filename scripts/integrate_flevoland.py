"""Integrate reviewed Issue #9 employers with existing provincial machinery."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.pipeline import ROOT, read, write
from scripts.integrate_province import integrate_employers


def integrate(companies, sources, geography, rows):
    companies, sources, regional = integrate_employers(companies, sources, geography, rows, slug='flevoland')
    overrides = read(ROOT/'data/flevoland-source-overrides.json', {})
    for source in sources:
        if source['id'] in overrides: source.update(overrides[source['id']])
    return companies, sources, regional


def main():
    rows = read(ROOT/'docs/flevoland-research-employers.json', {})['employers']
    companies, sources, regional = integrate(read(ROOT/'data/companies.json', []),
        read(ROOT/'data/sources.json', []), read(ROOT/'data/flevoland-geography.json', {}), rows)
    write(ROOT/'data/companies.json', companies)
    write(ROOT/'data/sources.json', sources)
    write(ROOT/'data/flevoland-employers.json', regional)
    print(len(regional), 'reviewed employers; existing IDs and sources reused')


if __name__ == '__main__': main()
