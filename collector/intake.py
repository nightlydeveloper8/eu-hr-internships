"""Conservative start-date extraction from the current official vacancy text.

Never roll a month into a guessed year, reuse historical intake, or treat a
start date as application verification. Conflicting starts remain explicit.
"""
import calendar
from datetime import date, datetime
import re

from .classify import plain

MONTHS = {
    'january': 1, 'januari': 1, 'february': 2, 'februari': 2,
    'march': 3, 'maart': 3, 'april': 4, 'may': 5, 'mei': 5,
    'june': 6, 'juni': 6, 'july': 7, 'juli': 7, 'august': 8,
    'augustus': 8, 'september': 9, 'october': 10, 'oktober': 10,
    'november': 11, 'december': 12,
}
MONTH = '(?:' + '|'.join(sorted(MONTHS, key=len, reverse=True)) + ')'
DATE = rf'(?:\d{{4}}-\d{{2}}-\d{{2}}|(?:\d{{1,2}}\s+)?{MONTH}(?:\s+\d{{4}})?)'
DATES = rf'{DATE}(?:\s*(?:/|of|or|en|and|tot|to|[-–])\s*{DATE})*'
# Require an adjacent start cue; publication/deadline dates and bare months
# elsewhere in the description are not intake evidence.
START = re.compile(
    rf'\b(?:(?:start(?:datum|\s+date)?|starting|starts|begin(?:datum)?)\s*(?:is|on|in|from|:|-)?\s*'
    rf'|(?:vanaf|per)\s+|(?:available|beschikbaar)\s+(?:from|vanaf)\s+)'
    rf'(?P<date>{DATES})\b'
    rf'|\b(?P<before>{DATES})\s+(?:kan\s+)?(?:starten|beginnen|start)\b', re.I)


def extract_intake(text, stamp):
    text = plain(text)
    today = datetime.fromisoformat(stamp.replace('Z', '+00:00')).date()
    starts = {}
    evidence = []
    candidates = []
    for match in START.finditer(text):
        # Interpret cues inside their own clause, not the whole vacancy: a
        # salary/application sentence can mention a stage without starting it.
        before=re.split(r'[.!?;]',text[:match.start()])[-1]
        after=re.split(r'[.!?;]',text[match.end():])[0]
        clause=before+match.group(0)+after
        if re.search(r'\b(?:sollicit\w*|applications?|apply|deadline|closing|'
                     r'publication|published|posted|geplaatst|founded|opgericht|campaign|campagne)\b', clause, re.I):
            continue
        if re.search(r'\b(?:stagevergoeding|vergoeding|salary|salaris|compensation|loon|payment)\b',before,re.I):
            continue
        if re.search(r'\b(?:not|niet|geen)\s*$', before, re.I):
            continue
        cue=match.group(0).lower()
        if re.match(r'(?:vanaf|per|available|beschikbaar)\b',cue):
            # Generic availability/effective-from is insufficient. Require a
            # placement noun before the date or an actual start verb after it.
            placement=re.search(r'\b(?:stage|stagiair\w*|internship|placement)\b',before,re.I)
            starting=re.search(r'\b(?:starten|beginnen|starting|starts|start|stagiair\w*)\b',after,re.I)
            if not placement and not starting:
                continue
        evidence.append(match.group(0))
        candidates.extend(m.group(0) for m in re.finditer(DATE, match.group('date') or match.group('before'), re.I))
    for raw in candidates:
        try:
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
                end = date.fromisoformat(raw)
                value = end.isoformat()
                state = 'past-start' if end < today else 'documented-future-start'
            else:
                parts = re.fullmatch(rf'(?:(\d{{1,2}})\s+)?({MONTH})(?:\s+(\d{{4}}))?', raw, re.I)
                day, month, year = parts.groups()
                month = MONTHS[month.lower()]
                if not year:
                    if day: date(2000, month, int(day))
                    value = raw + ' (year unspecified)'
                    state = 'year-unconfirmed'
                else:
                    year = int(year)
                    end = date(year, month, int(day) if day else calendar.monthrange(year, month)[1])
                    value = f'{year:04d}-{month:02d}' + (f'-{int(day):02d}' if day else '')
                    state = 'past-start' if end < today else 'documented-future-start'
            starts[value] = state
        except ValueError:
            continue
    if not starts:
        return None
    return dict(published_start=next(iter(starts)) if len(starts)==1 else None,
                alternatives=sorted(starts) if len(starts)>1 else [],
                state=next(iter(starts.values())) if len(starts) == 1 else 'conflicting-starts',
                checked_at=stamp,
                evidence=list(dict.fromkeys(evidence)))
