"""Visible fields in individually reviewed employer templates.

Template fields, rather than URL slugs or navigation headings, provide the role
and workplace. A missing application form or changed layout fails explicitly.
"""
from html.parser import HTMLParser
import re
from .classify import plain,COUNTRIES


class AwarePage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.values={};self.application=False

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);classes=set(attrs.get('class','').split());field=None
        if tag=='form' and attrs.get('id','').startswith('formie-vacancyApply-'):
            self.application=True
        if tag=='h5' and 'heading-xxl' in classes and any('vacancy-hero' in c for _,c,_ in self.stack):field='title'
        elif tag=='span' and 'location' in classes and any('vacancy-hero' in c for _,c,_ in self.stack):field='city'
        elif 'vacancy-content' in classes:field='text'
        elif tag=='span' and 'category' in classes and any('vacancy-hero' in c for _,c,_ in self.stack):field='employment'
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append((tag,classes,field))

    def handle_data(self,data):
        if any(tag in ('script','style','svg') for tag,_,_ in self.stack):return
        for field in {field for _,_,field in self.stack if field}:
            self.values.setdefault(field,[]).append(data)

    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                self.stack=self.stack[:i];break


def aware_record(body,record,source):
    parser=AwarePage();parser.feed(body.decode('utf-8','replace'))
    fields={key:plain(' '.join(value)) for key,value in parser.values.items()}
    if not all(fields.get(k) for k in ('title','city','text')) or not parser.application:
        raise ValueError('A-ware reviewed title, workplace, description or application form missing')
    # This site also lists Belgian jobs; never assign NL from the employer HQ.
    country=source.get('reviewed_city_countries',{}).get(fields['city'])
    suffix=re.search(r'\(([A-Z]{2})\)$',fields['city'])
    if suffix and suffix.group(1) in COUNTRIES:country=suffix.group(1)
    if not country:raise ValueError('A-ware workplace country requires review: '+fields['city'])
    return dict(record,**fields,country=country,countries=[country],location=fields['city']+', '+country,language='nl')


class ReviewedTitle(HTMLParser):
    """Extract one source-reviewed heading tag/class, including nested spans."""
    def __init__(self, body, selector):
        super().__init__(convert_charrefs=True)
        self.selector=selector;self.depth=0;self.values=[];self.current=[]
        self.feed(body.decode('utf-8','replace'))

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if self.depth:
            if tag not in ('br','img','input','hr','meta','link','source','wbr'):self.depth+=1
        elif tag==self.selector.get('tag') and self.selector.get('class') in attrs.get('class','').split():
            self.depth=1;self.current=[]

    def handle_data(self,data):
        if self.depth:self.current.append(data)

    def handle_endtag(self,tag):
        if self.depth:
            self.depth-=1
            if self.depth==0:self.values.append(plain(' '.join(self.current)))


def reviewed_titles(body,source):
    selector=source.get('reviewed_title')
    if not selector:return []
    if selector.get('tag') not in ('h1','h2','h3') or not selector.get('class'):
        raise ValueError('Unreviewed visible title selector')
    return ReviewedTitle(body,selector).values
