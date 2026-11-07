"""Reviewed HLB cards: the vacancy's labelled city, never the group headquarters."""
from html.parser import HTMLParser
from urllib.parse import urljoin
from .classify import plain, canonical_url
from .universal import Document, Inventory
from .applications import checked_document


class HLBIndex(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.card = None
        self.field = None
        self.cards = []
        self.feed(body.decode('utf-8', 'replace'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'div':
            if self.card is not None:
                self.depth += 1
            elif 'vacancies-overview-item' in a.get('class', '').split():
                self.card = dict(title=[], city=[], urls=[])
                self.depth = 1
        if self.card is None:
            return
        if tag == 'h3': self.field = 'title'
        if tag == 'span' and 'location-label' in a.get('class', '').split(): self.field = 'city'
        if tag == 'a' and a.get('href'): self.card['urls'].append(a['href'])

    def handle_data(self, value):
        if self.card is not None and self.field:
            self.card[self.field].append(value)

    def handle_endtag(self, tag):
        if tag in ('h3', 'span'): self.field = None
        if tag == 'div' and self.card is not None:
            self.depth -= 1
            if not self.depth:
                self.cards.append(self.card)
                self.card = None


def hlb_records(source, client):
    from .adapters import _record
    body, index = checked_document(source['career_url'], source, client)
    cards = HLBIndex(body).cards
    if not cards: raise ValueError('HLB vacancy cards unavailable')
    records = []
    for card in cards:
        title, city = (plain(' '.join(card[k])) for k in ('title', 'city'))
        urls = {canonical_url(urljoin(index.url, u)) for u in card['urls']}
        if not title or city not in source['reviewed_city_countries'] or len(urls) != 1:
            raise ValueError('HLB card title, labelled city or unique vacancy link requires review')
        url = urls.pop()
        _, doc = checked_document(url, source, client)
        if doc.h1 != [title]: raise ValueError('HLB card and vacancy title differ')
        records.append(_record(source, url, title, city + ', NL', doc.text, url,
            city=city, country=source['reviewed_city_countries'][city], language='nl',
            location_evidence_url=index.url))
    # Reading this observed list does not establish all group channels or absence.
    return Inventory(records, dict(status='partial', complete=False, closure_complete=False,
        pages_read=1+len(cards), discovery_scope='Observed official HLB career cards and linked details; broader group channels not established'))
