import hashlib
import html
import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode, quote

COUNTRIES = dict(AT='Austria', BE='Belgium', BG='Bulgaria', HR='Croatia', CY='Cyprus', CZ='Czechia', DK='Denmark', EE='Estonia', FI='Finland', FR='France', DE='Germany', GR='Greece', HU='Hungary', IE='Ireland', IT='Italy', LV='Latvia', LT='Lithuania', LU='Luxembourg', MT='Malta', NL='Netherlands', PL='Poland', PT='Portugal', RO='Romania', SK='Slovakia', SI='Slovenia', ES='Spain', SE='Sweden')
EU27 = dict(COUNTRIES)
# Non-EU countries in scope (Phase 4): internships there need a permit or visa for most students.
NON_EU = dict(CH='Switzerland', GB='United Kingdom')
COUNTRIES.update(NON_EU)
LANGUAGES = dict(en='English', nl='Dutch', fr='French', de='German', es='Spanish', it='Italian', pt='Portuguese', pl='Polish', sv='Swedish', da='Danish', fi='Finnish', el='Greek', cs='Czech', ro='Romanian', hu='Hungarian', bg='Bulgarian', hr='Croatian', sk='Slovak', sl='Slovenian', et='Estonian', lv='Latvian', lt='Lithuanian', mt='Maltese', ga='Irish', uk='Ukrainian')
CATEGORIES = {
 'talent-acquisition': ('Talent acquisition & recruitment', r'talent acquisition|recruit(?:ment|ing|er)?|recrutement|recrutamento|reclutamiento|reclutamento|werving|rekrut|rekryter|personalgewinnung|(?:talent|candidate) sourc(?:ing|er)'),
 'people-operations': ('People operations & culture', r'people (?:operations|ops|and culture|& culture|& organisation|& organization|process)|personalkultur'),
 'learning-development': ('Learning & development', r'learning (?:and|&) development|learning and organisational development|apprentissage et developpement|formation et developpement|\bl&d\b|people development|talent development|personalentwicklung|formation rh|formazione del personale'),
 'employer-branding': ('Employer branding', r'employer brand|marque employeur|arbeidsmarktcommunicatie'),
 'people-analytics': ('HR & people analytics', r'(?:hr|people|workforce|personal) (?:analytics|data|analysis|controlling)|hr controlling'),
 'compensation-benefits': ('Compensation & benefits', r'compensation|\bbenefits\b|total rewards?|remuneration|payroll|\bpaie\b|salaris|loonadministratie'),
 'employee-relations': ('Employee & labour relations', r'employee relations|labou?r relations|industrial relations|relazioni (?:industriali|sindacali)|relations sociales|arbeidsverhoudingen|mitbestimmung'),
 'employee-experience': ('Employee experience & engagement', r'(?:employee|people) (?:experience|engagement)|mitarbeiterbindung'),
 'organizational-development': ('Organizational development', r'organi[sz]ational development|organi[sz]ation development|organisationsentwicklung'),
 'hr-administration': ('HR administration', r'hr admin|personnel admin|administration du personnel|personaladministration|personeelsadministratie|amministrazione del personale'),
 'diversity-inclusion': ('Diversity, equity & inclusion', r'diversity,? equity (?:and|&) inclusion|diversity (?:and|&) inclusion|\bd&i\b'),
 'hr-generalist': ('Human resources & generalist', r'\bhr(?:bp|m)?\b|human resources|ressources humaines|risorse umane|recursos humanos|personalwesen|human resource|personalsach|personeelszaken|menselijke hulpbronnen|\brh\b|people (?:&|and) talent|people partner(?:ing)?|people intern|insan kaynak|ανθρωπιν|ανθρώπιν|resurse umane|zasobow ludzkich|zasoby ludzkie|ljudsk|lidsk|emberi eroforras|personalo|personali')
}
PLACEMENT_TITLE = r'\bintern\b|\binternship|\bstag(?:e|es|iair|iaire|ista|io)\b|praktik|placement|tirocin|estagi|practicas|stagiu|meewerkstage|afstudeer'
STUDENT_PLACEMENT = r'curricular|currently (?:enrolled|pursuing|studying)|enrolled (?:in|at|as)|still (?:a )?student|during your stud|as part of your (?:studies|degree|programme|program)|ingeschreven|studerende|nel corso degli studi|iscritt[oaie] (?:a|al|ad|presso)|convention de stage|pflichtpraktikum|learning agreement|stageovereenkomst|internship agreement|university placement|placement year|sandwich year|in het kader van je (?:studie|opleiding)|im rahmen (?:deines|ihres) studiums'
STUDENT_JOB = r'werkstud(?:ent|ierende)\w*|working.students?|student(?:ische)? (?:assistant|hilfskraft|aushilfe|job)|studentenjob|studentermedhjaelper'
INTERNSHIP = r'\b(?:meewerk|afstudeer)stage\b|\bintern(?:ship|ships|s)?\b|\btrainee(?:ship)?\b|\bstag(?:e|es|iair|iaire|iaires|eplaats|ista|io)\b|\bpraktik(?:ant|antin|um|a|plads|plats)?\b|praktikant(?:en|er|s|as|ai|e)?\b|praktikum\b|\bwerkstudent\b|working.student|student (?:placement|assistant)|\bpraktijkstage\b|\bpraktyk(?:i|a|ant(?:ka|ki|ow)?)?\b|\bbeca(?:rio|ria)?\b|\btirocin(?:io|ante|anti|i)\b|\bestagi(?:o|os|ari[oa]s?)\b|\bstagi(?:u|ar|ara|ari)\b|\bstazist(?:a|ka|i|ky)\b|\bodborna praxe\b|\bstrucna praksa\b|\bstudentska praksa\b|\ben practicas\b|\bgyakornok|\bπρακτικ|\bстаж|\bpripravnik|\bprakse\b|\bpraktika\b|\bharjoittel'
# Placement nouns are distinct from Polish 'staz pracy' (work experience).
POLISH_PLACEMENT = r'\bstaz(?:ysta|ystka|ysci|ystki)\b|(?:^|[|:–—-]\s*)(?:(?:p[łl]atny|letni|wakacyjny|studencki)\s+)?staz\b(?!\s+pracy\b)'

CITY_COUNTRIES = {
 'NL': 'amsterdam|rotterdam|utrecht|eindhoven|hoofddorp|oegstgeest|amersfoort|wageningen|haarlem|zaandam|leiden|den haag|hilversum|breda|delft|nijmegen|groningen|tilburg|enschede|apeldoorn|arnhem|den bosch',
 'DE':'berlin|munich|munchen|hamburg|frankfurt|cologne|koln|dusseldorf|stuttgart|leipzig|karlsruhe|walldorf|heidelberg', 'FR':'paris|rueil.malmaison|neuilly|nanterre|saint.ouen|saint.denis|lyon|marseille|bordeaux|lille|toulouse|nantes|boulogne|issy|clichy',
 'BE':'brussels|bruxelles|brussel|antwerp|antwerpen|ghent|gent|leuven|vorst', 'PT':'lisbon|lisboa|porto|braga', 'ES':'madrid|barcelona|valencia|malaga|sevilla', 'IT':'milan|milano|roma|rome|torino|turin|bologna',
 'PL':'warsaw|warszawa|krakow|kraków|wroclaw|wrocław|poznan|poznán|gdansk|gdańsk', 'AT':'vienna|wien|salzburg|graz|linz', 'IE':'dublin|cork|galway', 'SE':'stockholm|gothenburg|goteborg|malmo', 'DK':'copenhagen|kobenhavn|aarhus', 'FI':'helsinki|espoo|tampere', 'GR':'athens|thessaloniki', 'HU':'budapest', 'CZ':'prague|praha|brno', 'RO':'bucharest|bucuresti|cluj', 'BG':'sofia|varna', 'HR':'zagreb|split', 'CY':'limassol|nicosia', 'EE':'tallinn|tartu', 'LV':'riga', 'LT':'vilnius|kaunas', 'LU':'luxembourg', 'MT':'valletta|sliema|st julian', 'SK':'bratislava|kosice', 'SI':'ljubljana|maribor',
 'CH':'zurich|zürich|geneva|geneve|genève|genf|basel|lausanne|bern|lugano|zug|winterthur|st. gallen', 'GB':'london|manchester|edinburgh|birmingham|glasgow|bristol|leeds|cardiff|belfast'
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
    return urlunsplit(('https',p.netloc.lower(),quote(p.path.rstrip('/'),safe="/%:@!$&'()*+,;=-._~"),urlencode(query),''))

def country_codes(location, explicit=None):
    iso3 = dict(zip('AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE CHE GBR'.split(),COUNTRIES))
    if explicit:
        explicit={'nederland':'NL','deutschland':'DE','osterreich':'AT','schweiz':'CH','suisse':'CH','svizzera':'CH','uk':'GB','great britain':'GB','england':'GB','scotland':'GB','wales':'GB'}.get(fold(explicit),explicit)
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
    if re.search(r'\b(?:schweiz|suisse|svizzera)\b',value):return ['CH']
    if re.search(r'\b(?:uk|england|scotland|wales|northern ireland|great britain)\b',value):return ['GB']
    # Reject known out-of-scope locations before city matching (e.g. Paris, Texas; London, Ontario).
    if re.search(r'united states|\busa\b|canada|ontario|india|australia|singapore|brazil|toronto|san francisco|new york|\btexas\b',value): return []
    return [c for c, cities in CITY_COUNTRIES.items() if re.search(r'\b(?:'+fold(cities)+r')\b',value)]

def _vocabulary():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / 'data' / 'hr-vocabulary.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'categories': {}}


def vocabulary_pattern(terms):
    """Compile natural-language terms into one folded, whole-word regex."""
    parts = []
    for term in terms:
        value = fold(str(term).strip())
        if not value:
            continue
        prefix = value.endswith('*')
        value = value.rstrip('*')
        # '&' is required where written ("d&i" must never match "di"); other
        # separators (space, hyphen, slash) are interchangeable.
        segments = [[re.escape(w) for w in re.split(r'[\s\-/]+', seg) if w] for seg in value.split('&')]
        if not all(segments):
            continue
        joined = r'\s*&\s*'.join(r'[\s\-/]+'.join(words) for words in segments)
        parts.append(r'(?<!\w)' + joined + (r'' if prefix else r'(?!\w)'))
    return re.compile('|'.join(parts)) if parts else None


def _compile_vocabulary(data):
    by_language = lambda block: [t for terms in (block or {}).values() if isinstance(terms, list) for t in terms]
    strong, contextual = {}, {}
    for key, entry in data.get('categories', {}).items():
        strong[key] = vocabulary_pattern(by_language(entry.get('strong')))
        contextual[key] = vocabulary_pattern(by_language(entry.get('contextual')))
    generalist = by_language(data.get('categories', {}).get('hr-generalist', {}).get('strong'))
    context = vocabulary_pattern(generalist + by_language({k: v for k, v in data.get('hr_context', {}).items() if k != 'note'}))
    veto = vocabulary_pattern(data.get('non_hr_domain', {}).get('terms', []))
    return strong, contextual, context, veto


VOCABULARY = _vocabulary()
VOCAB_STRONG, VOCAB_CONTEXTUAL, HR_CONTEXT, NON_HR_DOMAIN = _compile_vocabulary(VOCABULARY)
APPLICATION_SENTENCE = r'\b(?:cv|curriculum|resume|candidat\w*|apply|application|bewerb\w*|postul\w*|sollicit\w*|inviare|send|envoy\w*|enviar|stuur)\b'


def vocabulary_categories(title, text):
    """Categories from data/hr-vocabulary.json. Inputs are already folded."""
    cats = [k for k, pattern in VOCAB_STRONG.items() if pattern and pattern.search(title)]
    if NON_HR_DOMAIN and NON_HR_DOMAIN.search(title):
        return cats
    sentences = None
    for key, pattern in VOCAB_CONTEXTUAL.items():
        if key in cats or not pattern or not pattern.search(title) or not HR_CONTEXT:
            continue
        if HR_CONTEXT.search(pattern.sub(' ', title)):
            cats.append(key)
            continue
        if sentences is None:
            sentences = [s for s in re.split(r'(?<=[.!?;:])\s+|\n', text) if not re.search(APPLICATION_SENTENCE, s)]
        if any(pattern.search(s) and HR_CONTEXT.search(s) for s in sentences):
            cats.append(key)
    return cats



def classify_role(title, text='', employment=''):
    # Preserve the accent to distinguish Czech/Slovak stáž from Polish staż.
    # Match the role label, rather than a mention of prior experience.
    localized_title = plain(title).lower()
    hr_placement = re.match(r'^hr\s+stáž\b', localized_title) and not re.search(
        r'\b(?:werkstud\w*|working[ -]student|trainee(?:ship)?|graduate)\b', localized_title
    )
    title, text, employment = map(fold,(localized_title,plain(text),plain(employment)))
    extra = vocabulary_categories(title, text)
    cats = [k for k,(_,p) in CATEGORIES.items() if re.search(p,title) or k in extra]
    if re.search(r'(?:software|sales|account executive|business development|marketing) (?:engineer|developer|intern|trainee|manager).{0,30}(?:hr|human resources)|(?:hr|human resources) (?:software|saas) (?:engineer|developer|sales)',title): return None
    if (not cats and VOCAB_CONTEXTUAL['people-operations'].search(title)
            and not NON_HR_DOMAIN.search(title)
            and re.search(r'\b(?:hr-projekte|hr-teilprojekte|personalstammdaten|employee records)\b', text)):
        cats = ['people-operations']
    if not cats and re.search(r'people (?:&|and) events',title) and re.search(r'personalbetreuung|personalentwicklung|human resources|hr administration',text):cats=['hr-generalist']
    # A People & Organisation internship is HR only when the description
    # actually establishes an HR function, not from generic organisation work.
    if re.search(r'people (?:&|and) organi[sz]ation',title) and not re.search(r'\b(?:human resources|recruitment|personnel|payroll|hr service(?:desk)?)\b',text):
        return None
    if re.search(r'benefits|compensation|reward',title) and not re.search(r'hr|human resources|employee|payroll|compensation (?:&|and) benefits|total rewards|remuneration',title+' '+text):
        cats=[c for c in cats if c!='compensation-benefits']
    if re.search(r'talent (?:community|pool|network)|open application|general (?:internship|student) programme|internship opportunities|internships (?:at|within)',title):return None
    # Graduate employment is distinct from a university placement.
    if re.search(r'graduate (?:program|programme|scheme)|management trainee',title) and not re.search(r'\binternship\b|\bplacement\b',title):return None
    # Department metadata alone cannot turn a sustainability/software role into HR.
    if not cats: return None
    # Dutch 'intern' can mean an in-house permanent employee. Require actual
    # student/placement evidence when the surrounding text is Dutch.
    if re.search(r'\bintern\b',title) and re.search(r'\b(?:jij|jouw|werkervaring|salarisverwerking|medewerkers)\b',text):
        if not re.search(r'\bstag(?:e|iair|iaire|iairs|iaires)|\binternship|\bstudent|\bmeewerk|\bafstudeer|\binschrev',title+' '+text):return None
    # Internal, international and interview must never count as 'intern'.
    # Part-time student jobs (Werkstudent, working student) are not placements:
    # they count only when the title also names an internship.
    if re.search(STUDENT_JOB,title) and not re.search(INTERNSHIP,re.sub(STUDENT_JOB,' ',title)):return None
    signal = re.search(INTERNSHIP,re.sub(STUDENT_JOB,' ',title+' '+employment))
    # Spanish placement titles use 'Prácticas'. A phrase about good practices
    # inside a permanent HR title/description is not a placement signal.
    signal = signal or re.search(r'^practicas\b',title) or re.search(r'^practicas\b',employment)
    signal = signal or re.search(POLISH_PLACEMENT,title) or re.search(POLISH_PLACEMENT,employment)
    if not signal and not hr_placement: return None
    # Traineeships are usually graduate jobs, out of scope (owner decision 18/11/2026).
    # A trainee title counts only when the text documents a student placement.
    if re.search(r'trainee',title) and not re.search(PLACEMENT_TITLE,title) and not re.search(STUDENT_PLACEMENT,fold(plain(text))):return None
    kind = 'internship'
    return {'categories':cats,'category':cats[0], 'internship_type':kind,'internship_confidence':'confirmed'}

LANG_ALIASES = {
 'en':r'english|anglais(?:e)?|englisch|engels(?:e)?|inglese|ingles|angielski|angielska', 'nl':r'dutch|nederlands(?:e)?|neerlandais|ollandese', 'fr':r'french|francais(?:e)?|franzosisch|frans|francese', 'de':r'german|deutsch(?:kenntnisse)?|allemand|duits|tedesco|aleman', 'es':r'spanish|espanol|espagnol|spanisch|spaans', 'it':r'italian|italian[oa]|italien|italiaans', 'pt':r'portuguese|portugues|portugais', 'pl':r'polish|polski|polonais', 'sv':r'swedish|svenska', 'da':r'danish|dansk', 'fi':r'finnish|suomi', 'el':r'greek|ελληνικ', 'cs':r'czech|cestina', 'ro':r'romanian|romana', 'hu':r'hungarian|magyar', 'bg':r'bulgarian|български', 'hr':r'croatian|hrvatski', 'sk':r'slovak|slovencina', 'sl':r'slovenian|slovenscina', 'et':r'estonian|eesti', 'lv':r'latvian|latviesu', 'lt':r'lithuanian|lietuviu', 'mt':r'maltese|malti', 'ga':r'irish|gaeilge', 'uk':r'ukrainian|українськ'
}

def workplace_languages(text):
    evidence = []
    for sentence in re.split(r'(?<=[.!?;])\s+|[\n•]', plain(text)):
        s = fold(sentence)
        # Application language / language classes / marketing are not workplace evidence.
        if re.search(r'(?:applications?|cv|resume|cover letter).{0,45}(?:in english|in french)|language (?:classes|courses)|(?:english|french|german).{0,15}(?:lessons|classes|courses)',s): continue
        cue = r'arbeitssprache|langue de travail|voertaal|lingua di lavoro|preferred|preferably|nice.to.have|a plus|von vorteil|required|mandatory|essential|must|requis|obligatoire|verplicht|vereist|parl(?:ez|er)|couramment|\bfluen|proficien|command of|(?:official|corporate|company|business|main|working) language|working (?:proficiency|in)|work in|communication(?: and \w+)? skills|communicat\w* (?:in|skills)|spea[kc]|written and (?:verbal|spoken)|oral and written|writ\w* strong|comfortable.{0,30}english|maitrise|courant|biling|kenntnisse|beherrschen|vloeiend|beheers|niveau|livello|conoscenza|dominio|competencia'
        # Spanish level requirements are workplace evidence; language courses
        # and CV language instructions are not.
        if re.search(r'\b(?:clases|cursos?)\s+(?:de\s+)?(?:ingles|frances|aleman|idiomas)\b|(?:cv|curriculum|carta de presentacion|solicitud).{0,60}\ben ingles\b',s):continue
        if not re.search(cue+r'|\bnivel\b',s): continue
        for code,pattern in LANG_ALIASES.items():
            m = re.search(r'\b(?:'+pattern+r')\b',s)
            if not m: continue
            # Scope negation/optional cues to this language clause, never the next one.
            start=max(s.rfind(',',0,m.start()),s.rfind(' but ',0,m.start()),s.rfind(' maar ',0,m.start()))
            local = s[max(start+1,m.start()-45):m.end()+65]
            following=re.search(r',|\b(?:but|maar|mais|aber)\b',s[m.end():])
            if following:local=s[max(start+1,m.start()-45):m.end()+following.start()]
            if re.search(r'not (?:required|necessary|essential|mandatory)|(?:do not|don.t) (?:need|require)|no need to (?:speak|know)|no .{0,20}(?:required|necessary)|nicht erforderlich|niet vereist|pas (?:requis|necessaire)|no (?:se )?(?:requiere|exige)|no (?:es )?(?:necesario|obligatorio|requerido|imprescindible)',local): continue
            tail = local[local.find(m.group(0))+len(m.group(0)):]
            next_language = '|'.join(LANG_ALIASES.values())
            tail = re.split(r'\b(?:additional languages|other languages|'+next_language+r')\b',tail,maxsplit=1)[0]
            optional = bool(re.search(r'plus|advantage|bonus|preferred|nice.to.have|appreciated|souhait|apprecie|von vorteil|deseable|valorable|preferible',tail))
            optional = optional or bool(re.match(r'preferred languages?(?: are)?\s*:',s) or re.match(r'preferred languages? are\b',s))
            optional = optional or bool(re.search(r'(?:preferred|preferably|nice.to.have|ideally)\s+(?:\w+\s+){0,2}$',s[max(start+1,m.start()-35):m.start()]))
            optional = optional or bool(re.search(r'(?:deseable|valorable|preferible)\s*:?\s*(?:\w+\s+){0,5}$',s[max(start+1,m.start()-65):m.start()]))
            mentions=sorted((x.start(),x.end()) for p in LANG_ALIASES.values() for x in re.finditer(r'\b(?:'+p+r')\b',s))
            alternative=any(re.fullmatch(r'\s+(?:or|and\s*/\s*or|oder|of|en\s*/\s*of|ou|oppure)\s+',s[a[1]:b[0]]) and m.start() in (a[0],b[0]) for a,b in zip(mentions,mentions[1:]))
            working=bool(re.search(r'arbeitssprache|langue de travail|voertaal|lingua di lavoro|(?:working|corporate|company|business|official|main) language|work in',local))
            if re.search(r'\b(?:required|mandatory|must|verplicht|vereist|requis)\b',s[m.end():m.end()+35]):working=False
            excerpt = sentence[max(0,m.start()-100):m.end()+120]
            item = {'code':code, 'confidence':'confirmed','requirement':'preferred' if optional else 'alternative' if alternative else 'working' if working else 'required-or-working','method':'explicit-language-pattern','evidence':excerpt}
            if not any(e['code']==code and e['requirement']==item['requirement'] for e in evidence): evidence.append(item)
    return evidence

def language_summary(text, languages=None):
    languages=workplace_languages(text) if languages is None else languages
    supported=[l for l in languages if l['requirement'] in ('required-or-working','required','working')]
    required=sorted({l['code'] for l in supported if l['requirement']!='working'})
    english=any(l['code']=='en' and l['requirement']!='preferred' for l in languages)
    sufficiency=re.search(r'english is the only (?:required|working) language|no (?:other|additional) languages? (?:is |are )?required',fold(plain(text)))
    only=english and not any(c!='en' for c in required) and bool(sufficiency)
    return dict(requirements_status='explicit' if any(l['requirement']!='preferred' for l in languages) else 'unknown',required_languages=required,
                alternative_languages=sorted({l['code'] for l in languages if l['requirement']=='alternative'}),
                english_support='documented' if english else 'unknown',english_sufficiency='documented' if only else 'unknown',english_sufficiency_evidence=sufficiency.group(0) if only else None)


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
        for candidate in re.finditer(r'\b\d+(?:\s*[-–]\s*\d+|\s+(?:of|or)\s+\d+)?\s*(?:months?|maanden|mois|monate|meses|mesi|weeks?|weken)\b',sentence,re.I):
            # Posting age can share a sentence with the title or requirements.
            # Skip that match, while retaining later legitimate durations.
            if re.match(r'\s+(?:geleden|ago)\b',sentence[candidate.end():],re.I): continue
            duration = candidate
            break
        if duration: break
    enrollment = next((s for s in re.split(r'(?<=[.!?])\s+',text) if re.search(r'enroll|ingeschreven|inscrit|immatrikul|convention de stage|learning agreement|\bje volgt\b.{0,100}\bopleiding\b|\bvolg jij\b.{0,100}\bstudie\b|\bstudie\b.{0,100}\bvolgt\b',s,re.I)),None)
    if work_mode not in ('remote','hybrid','on-site'):
        work_mode = 'hybrid' if re.search(r'\bhybrid\b',text,re.I) else 'on-site' if re.search(r'\bon.site\b',text,re.I) else 'unspecified'
    return {'duration':duration.group(0) if duration else None,'enrollment':enrollment[:260] if enrollment else None,'work_mode':work_mode}

def explicitly_admits_enrolled_students(text):
    return bool(re.search(
        r'\b(?:currently pursuing|enrolled in|currently enrolled|current(?:ly)?(?: full-time)? students?|'
        r'immatrikuliert\w*|eingeschrieben\w*|du studierst|'
        r'du absolvierst (?:aktuell |derzeit )?ein studium)\b',
        plain(text), re.I))


def also_open_to_recent_graduates(text):
    """Require an explicit alternative to current study in the same statement."""
    patterns = (
        r'(?:currently pursuing|enrolled in)\b[^.!?]{0,100}\bor\s+recently (?:completed|graduated)',
        r'\b(?:recent graduates?|recent graduate)\s+or\s+(?:an?\s+)?students?\b',
        r'\bdu studierst\b[^.!?]{0,160}\boder hast dein studium bereits\b[^.!?]{0,55}\babgeschlossen\b',
    )
    return any(re.search(pattern, plain(text), re.I) for pattern in patterns)


def stable_id(source_id, external_id):
    return hashlib.sha256((source_id+':'+str(external_id)).encode()).hexdigest()[:20]
