"""Read explicit corporate address metadata from the declared official site.
No office or employer size is inferred from association membership or a URL suffix.
"""
from urllib.parse import urlsplit
from .employer_pages import PageParser
from .classify import COUNTRIES,fold

def organisation_evidence(body,final,stamp):
    parser=PageParser();parser.feed(body.decode('utf-8','replace'));places=[]
    def nodes(value):
        if isinstance(value,list):
            for x in value:yield from nodes(x)
        elif isinstance(value,dict):
            yield value
            if '@graph' in value:yield from nodes(value['@graph'])
    host=(urlsplit(final).hostname or '').removeprefix('www.')
    for script in parser.scripts:
        for obj in nodes(script):
            types=obj.get('@type',[]);types=[types] if isinstance(types,str) else types
            if not set(types).intersection({'Organization','Corporation','LocalBusiness','BankOrCreditUnion'}):continue
            own=(urlsplit(obj.get('url') or obj.get('@id') or '').hostname or '').removeprefix('www.')
            if own!=host:continue
            addresses=obj.get('address',[]);addresses=addresses if isinstance(addresses,list) else [addresses]
            for a in addresses:
                if not isinstance(a,dict) or not a.get('addressLocality'):continue
                country=a.get('addressCountry');country=country.get('name') if isinstance(country,dict) else country
                if not isinstance(country,str):continue
                aliases={fold(name):code for code,name in COUNTRIES.items()}
                aliases.update({'italia':'IT','nederland':'NL','deutschland':'DE'})
                country=aliases.get(fold(country),country.upper())
                if country not in COUNTRIES:continue
                region=None
                if country=='IT' and fold(str(a.get('addressRegion',''))) in {'veneto','pd','tv','ve','ro','vi','vr','bl','padova','treviso','venezia','rovigo','vicenza','verona','belluno'}:region='ITH3'
                place=dict(country=country,region_code=region,subregion_code=None,city=a['addressLocality'],evidence_url=final,location_confidence='confirmed',checked_on=stamp)
                if place not in places:places.append(place)
    return places
