import hashlib
import html
import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

COUNTRIES = dict(AT='Austria', BE='Belgium', BG='Bulgaria', HR='Croatia', CY='Cyprus', CZ='Czechia', DK='Denmark', EE='Estonia', FI='Finland', FR='France', DE='Germany', GR='Greece', HU='Hungary', IE='Ireland', IT='Italy', LV='Latvia', LT='Lithuania', LU='Luxembourg', MT='Malta', NL='Netherlands', PL='Poland', PT='Portugal', RO='Romania', SK='Slovakia', SI='Slovenia', ES='Spain', SE='Sweden')
LANGUAGES = dict(en='English', nl='Dutch', fr='French', de='German', es='Spanish', it='Italian', pt='Portuguese', pl='Polish', sv='Swedish', da='Danish', fi='Finnish', el='Greek', cs='Czech', ro='Romanian', hu='Hungarian', bg='Bulgarian', hr='Croatian', sk='Slovak', sl='Slovenian', et='Estonian', lv='Latvian', lt='Lithuanian', mt='Maltese', ga='Irish', uk='Ukrainian')
CATEGORIES = {
 'talent-acquisition': ('Talent acquisition & recruitment', r'talent acquisition|recruit(?:ment|ing|er)?|recrutement|recrutamento|reclutamiento|reclutamento|werving|rekrut|personalgewinnung|(?:talent|candidate) sourc(?:ing|er)'),
 'people-operations': ('People operations & culture', r'people (?:operations|ops|and culture|& culture|& organisation|& organization|process)|personalkultur'),
 'learning-development': ('Learning & development', r'learning (?:and|&) development|\bl&d\b|people development|talent development|personalentwicklung|formation rh|formazione del personale'),
 'employer-branding': ('Employer branding', r'employer brand|marque employeur|arbeidsmarktcommunicatie'),
 'people-analytics': ('HR & people analytics', r'(?:hr|people|workforce|personal) (?:analytics|data|analysis|controlling)|hr controlling'),
 'compensation-benefits': ('Compensation & benefits', r'compensation|benefits|reward|remuneration|payroll|paie|salaris|loonadministratie'),
 'employee-experience': ('Employee experience & engagement', r'(?:employee|people) (?:experience|engagement)|mitarbeiterbindung'),
 'organizational-development': ('Organizational development', r'organi[sz]ational development|organi[sz]ation development|organisationsentwicklung'),
 'hr-administration': ('HR administration', r'hr admin|personnel admin|administration du personnel|personaladministration|personeelsadministratie|amministrazione del personale'),
 'hr-generalist': ('Human resources & generalist', r'\bhr(?:bp|m)?\b|human resources|ressources humaines|risorse umane|recursos humanos|personalwesen|human resource|personalsach|personeelszaken|menselijke hulpbronnen|\brh\b|people (?:&|and) talent|people partner(?:ing)?|people intern|insan kaynak|ανθρωπιν|ανθρώπιν|resurse umane|zasobow ludzkich|zasoby ludzkie|ljudsk|lidsk|emberi eroforras|personalo|personali')
}
INTERNSHIP = r'\b(?:meewerk|afstudeer)stage\b|\bintern(?:ship|ships|s)?\b|\btrainee(?:ship)?\b|\bstag(?:e|es|iair|iaire|iaires|eplaats|ista|io)\b|\bpraktik(?:ant|antin|um|a)?\b|\bwerkstudent\b|working.student|student (?:placement|assistant)|\bpraktijkstage\b|\bpraktyk(?:i|a|ant(?:ka|ki|ow)?)?\b|\bbeca(?:rio|ria)?\b|\btirocin(?:io|ante)\b|\bestagio\b|\bgyakornok|\bπρακτικ|\bstaz\b|\bстаж|\bpripravnik|\bprakse\b|\bpraktika\b|\bharjoittel'
CITY_COUNTRIES = {
 'NL': 'amsterdam|rotterdam|utrecht|eindhoven|hoofddorp|oegstgeest|amersfoort|wageningen|haarlem|zaandam|leiden|den haag|hilversum|breda|delft|nijmegen|groningen|tilburg|enschede|apeldoorn|arnhem|den bosch',
 'DE':'berlin|munich|munchen|hamburg|frankfurt|cologne|koln|dusseldorf|stuttgart|leipzig|karlsruhe|walldorf|heidelberg', 'FR':'paris|rueil.malmaison|neuilly|nanterre|saint.ouen|saint.denis|lyon|marseille|bordeaux|lille|toulouse|nantes|boulogne|issy|clichy',
 'BE':'brussels|bruxelles|brussel|antwerp|antwerpen|ghent|gent|leuven|vorst', 'PT':'lisbon|lisboa|porto|braga', 'ES':'madrid|barcelona|valencia|malaga|sevilla', 'IT':'milan|milano|roma|rome|torino|turin|bologna',
 'PL':'warsaw|warszawa|krakow|kraków|wroclaw|wrocław|poznan|poznán|gdansk|gdańsk', 'AT':'vienna|wien|salzburg|graz|linz', 'IE':'dublin|cork|galway', 'SE':'stockholm|gothenburg|goteborg|malmo', 'DK':'copenhagen|kobenhavn|aarhus', 'FI':'helsinki|espoo|tampere', 'GR':'athens|thessaloniki', 'HU':'budapest', 'CZ':'prague|praha|brno', 'RO':'bucharest|bucuresti|cluj', 'BG':'sofia|varna', 'HR':'zagreb|split', 'CY':'limassol|nicosia', 'EE':'tallinn|tartu', 'LV':'riga', 'LT':'vilnius|kaunas', 'LU':'luxembourg', 'MT':'valletta|sliema|st julian', 'SK':'bratislava|kosice', 'SI':'ljubljana|maribor'
}

def plain(value):
    value = html.unescape(html.unescape(str(value or '')))
    value = re.sub(r'</(?:p|li|div|h\d)>|<br\s*/?>', '. ', value, flags=re.I)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', value)).strip()

def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))

def canonical_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise ValueError('Only public HTTPS job URLs are allowed')
    if p.hostname in ('localhost','127.0.0.1','::1') or re.match(r'^\d+\.\d+\.\d+\.\d+$',p.hostname):
        raise ValueError('IP addresses are not job hosts')
    query = [(k,v) for k,v in parse_qsl(p.query) if not k.startswith('utm_') and k not in ('trid','oga','gh_src','lever-source','lever-origin')]
    return urlunsplit(('https',p.netloc.lower(),p.path.rstrip('/'),urlencode(query),''))

def country_codes(location, explicit=None):
    iso3 = dict(zip('AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE'.split(),COUNTRIES))
    if explicit:
        explicit={'nederland':'NL','deutschland':'DE','osterreich':'AT'}.get(fold(explicit),explicit)
        explicit = iso3.get(explicit.upper(),next((c for c,n in COUNTRIES.items() if fold(n)==fold(explicit)),explicit))
    if explicit and explicit.upper() in COUNTRIES:
        return [explicit.upper()]
    if explicit and explicit.upper() not in ('','EU','EUROPE'):
        return []
    value = fold(location)
    codes = [c for c,n in COUNTRIES.items() if re.search(r'\b'+re.escape(fold(n))+r'\b',value)]
    if codes: return codes
    if re.search(r'\bdeutschland(?:weit)?\b',value):return ['DE']
    if re.search(r'\bnederland\b',value):return ['NL']
    # Reject known non-EU locations before city matching (e.g. Paris, Texas).
    if re.search(r'united (?:states|kingdom)|\busa\b|\buk\b|switzerland|canada|india|australia|singapore|brazil|london|zurich|toronto|san francisco|new york|\btexas\b',value): return []
    return [c for c, cities in CITY_COUNTRIES.items() if re.search(r'\b(?:'+fold(cities)+r')\b',value)]

def classify_role(title, text='', employment=''):
    title, text, employment = map(fold,(plain(title),plain(text),plain(employment)))
    cats = [k for k,(_,p) in CATEGORIES.items() if re.search(p,title)]
    if re.search(r'(?:software|sales|account executive|business development|marketing) (?:engineer|developer|intern|trainee|manager).{0,30}(?:hr|human resources)|(?:hr|human resources) (?:software|saas) (?:engineer|developer|sales)',title): return None
    if not cats and re.search(r'people (?:&|and) events',title) and re.search(r'personalbetreuung|personalentwicklung|human resources|hr administration',text):cats=['hr-generalist']
    # Department metadata alone cannot turn a sustainability/software role into HR.
    if not cats: return None
    # Dutch 'intern' can mean an in-house permanent employee. Require actual
    # student/placement evidence when the surrounding text is Dutch.
    if re.search(r'\bintern\b',title) and re.search(r'\b(?:jij|jouw|werkervaring|salarisverwerking|medewerkers)\b',text):
        if not re.search(r'\bstag(?:e|iair|iaire|iairs|iaires)|\binternship|\bstudent|\bmeewerk|\bafstudeer|\binschrev',title+' '+text):return None
    # Internal, international and interview must never count as 'intern'.
    signal = re.search(INTERNSHIP,title+' '+employment)
    if not signal: return None
    kind = 'working-student' if re.search(r'werkstud(?:ent|ierende)|working.student|student assistant',title+' '+employment) else 'traineeship' if re.search(r'trainee',title+' '+employment) else 'internship'
    return {'categories':cats,'category':cats[0], 'internship_type':kind,'internship_confidence':'confirmed'}

LANG_ALIASES = {
 'en':r'english|anglais|englisch|engels|inglese|ingles|angielski|angielska', 'nl':r'dutch|nederlands|neerlandais|ollandese', 'fr':r'french|francais|franzosisch|frans|francese', 'de':r'german|deutsch|allemand|duits|tedesco|aleman', 'es':r'spanish|espanol|espagnol|spanisch|spaans', 'it':r'italian|italian[oa]|italien|italiaans', 'pt':r'portuguese|portugues|portugais', 'pl':r'polish|polski|polonais', 'sv':r'swedish|svenska', 'da':r'danish|dansk', 'fi':r'finnish|suomi', 'el':r'greek|ελληνικ', 'cs':r'czech|cestina', 'ro':r'romanian|romana', 'hu':r'hungarian|magyar', 'bg':r'bulgarian|български', 'hr':r'croatian|hrvatski', 'sk':r'slovak|slovencina', 'sl':r'slovenian|slovenscina', 'et':r'estonian|eesti', 'lv':r'latvian|latviesu', 'lt':r'lithuanian|lietuviu', 'mt':r'maltese|malti', 'ga':r'irish|gaeilge', 'uk':r'ukrainian|українськ'
}

def workplace_languages(text):
    evidence = []
    for sentence in re.split(r'(?<=[.!?;])\s+|[\n•]', plain(text)):
        s = fold(sentence)
        # Application language / language classes / marketing are not workplace evidence.
        if re.search(r'(?:applications?|cv|resume|cover letter).{0,45}(?:in english|in french)|language (?:classes|courses)|(?:english|french|german).{0,15}(?:lessons|classes|courses)',s): continue
        cue = r'\bfluen|proficien|command of|(?:official|corporate|company|business|main|working) language|working (?:proficiency|in)|work in|communication(?: and \w+)? skills|communicat\w* (?:in|skills)|spea[kc]|written and (?:verbal|spoken)|oral and written|writ\w* strong|comfortable.{0,30}english|maitrise|courant|biling|kenntnisse|beherrschen|vloeiend|beheers|niveau|livello|conoscenza|dominio|competencia'
        if not re.search(cue,s): continue
        for code,pattern in LANG_ALIASES.items():
            m = re.search(r'\b(?:'+pattern+r')\b',s)
            if not m: continue
            local = s[max(0,m.start()-45):m.end()+65]
            if re.search(r'not (?:required|necessary)|no .{0,20}(?:required|necessary)|nicht erforderlich|niet vereist|pas (?:requis|necessaire)',local): continue
            tail = s[m.end():m.end()+65]
            next_language = '|'.join(LANG_ALIASES.values())
            tail = re.split(r'\b(?:additional languages|other languages|'+next_language+r')\b',tail,maxsplit=1)[0]
            optional = bool(re.search(r'plus|advantage|bonus|preferred|nice.to.have|appreciated|souhait|apprecie|von vorteil',tail))
            excerpt = sentence[max(0,m.start()-100):m.end()+120]
            item = {'code':code, 'confidence':'confirmed','requirement':'preferred' if optional else 'required-or-working','evidence':excerpt}
            if not any(e['code']==code and e['requirement']==item['requirement'] for e in evidence): evidence.append(item)
    return evidence

def advertisement_language(text, hint=None):
    if hint:hint=hint.replace('_','-')
    if hint and hint.lower().split('-')[0] in LANGUAGES:
        return {'code':hint.lower().split('-')[0], 'confidence':'confirmed','method':'source metadata'}
    words = set(re.findall(r'\b\w+\b',fold(text)))
    clues = {'en':'the and you your with will our are have','nl':'het een je jouw wij voor van zijn','fr':'les des vous votre nous pour une avec','de':'und sie wir mit fur der die das','es':'los las una para con nuestro tu como','it':'gli della il per con che una tuo','pt':'voce uma para com nosso que dos pelo','pl':'oraz jest sie dla twoje przez','sv':'och att med som din vara','da':'og med til dig vores den','fi':'ja on olet kanssa sinulla','ro':'si pentru este echipa care','hu':'es hogy vagy egy','cs':'se pro na nas'}
    scores = sorted(((len(words & set(v.split())),k) for k,v in clues.items()),reverse=True)
    if scores[0][0]>=3 and scores[0][0]>scores[1][0]: return {'code':scores[0][1],'confidence':'uncertain','method':'deterministic stopword heuristic'}
    return {'code':None,'confidence':'unspecified','method':'insufficient evidence'}

def extract_metadata(text, work_mode=None):
    text = plain(text)
    duration = None
    for sentence in re.split(r'(?<=[.!?])\s+',text):
        if re.search(r'holiday|vacation|annual leave|time off|paid leave|conges|vakantie|urlaub',sentence,re.I): continue
        if not re.search(r'intern|duration|placement|trainee|available|availability|stag|praktik|durée|duree|durata|duur|beschikbaar|periode|period of',sentence,re.I): continue
        duration = re.search(r'\b\d+(?:\s*[-–]\s*\d+)?\s*(?:months?|maanden|mois|monate|meses|mesi|weeks?|weken)\b',sentence,re.I)
        if duration: break
    enrollment = next((s for s in re.split(r'(?<=[.!?])\s+',text) if re.search(r'enroll|ingeschreven|inscrit|immatrikul|convention de stage',s,re.I)),None)
    if work_mode not in ('remote','hybrid','on-site'):
        work_mode = 'hybrid' if re.search(r'\bhybrid\b',text,re.I) else 'on-site' if re.search(r'\bon.site\b',text,re.I) else 'unspecified'
    return {'duration':duration.group(0) if duration else None,'enrollment':enrollment[:260] if enrollment else None,'work_mode':work_mode}

def stable_id(source_id, external_id):
    return hashlib.sha256((source_id+':'+str(external_id)).encode()).hexdigest()[:20]
