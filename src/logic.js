export const fold = value => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export const unreviewedExternal = job => job.ownership_risk?.state === 'historical-unreviewed-external-host';
export function languageInfo(job) {
  const explicit = (job.workplace_languages || []).filter(l => l.confidence === 'confirmed' && ['required','required-or-working','working','alternative'].includes(l.requirement));
  return job.language_requirements || {requirements_status:explicit.length ? 'explicit' : 'unknown', english_support:(job.workplace_languages || []).some(l=>l.code==='en' && l.confidence==='confirmed' && ['required','required-or-working','working','alternative'].includes(l.requirement)) ? 'documented' : 'unknown', english_sufficiency:'unknown'};
}
export function verifiedJob(job, clock = Date.now()) {
  const stamp=Date.parse(job.last_verified_at || '');
  return job.status === 'open' && job.verification?.state === 'verified' && job.verification?.policy_version === 2 && Number.isFinite(stamp) && stamp <= clock && clock-stamp <= 48*60*60*1000;
}
export function publicEmploymentListing(job) {
  return ['public-api-active-listing', 'public-api-listed'].includes(job.link_status)
    || job.verification?.policy === 'public-api-active-listing';
}

export function applicationConfirmed(job, clock = Date.now()) {
  const evidence = job.application_verification;
  return !unreviewedExternal(job) && verifiedJob(job, clock) && !publicEmploymentListing(job)
    && Boolean(evidence?.method && safeUrl(evidence.url));
}

// Emergency degraded view: expose archived records only as unverified when daily checks are stale.
// This must never change verifiedJob(), policy v2, or the 48-hour freshness threshold.
export function unverifiedFallback(catalog, clock = Date.now()) {
  return stale(catalog?.updated_at, clock) && Array.isArray(catalog?.jobs)
    && catalog.jobs.some(job => job.status !== 'closed' && !unreviewedExternal(job))
    && !catalog.jobs.some(job => verifiedJob(job, clock));
}

// The unverified view is an explicit session choice, never a persistent emergency URL.
export function shareableFilterParams(filters, defaults) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (key !== 'unverified' && value !== defaults[key]) params.set(key, String(value));
  }
  return params;
}

export const STUDENT_PLACEMENT = Object.freeze({
  firstStart: '2027-01-05',
  lastStart: '2027-03-13',
  earliestEnd: '2027-05-31',
  minimumWeeks: 16,
  minimumVerifiedDurations: 10,
  startLabel: 'Starts Jan – mid-Mar 2027',
  durationLabel: 'Long enough (≈640 h)',
});

export const START_WINDOW = `${STUDENT_PLACEMENT.firstStart}-to-${STUDENT_PLACEMENT.lastStart}`;
export const LONG_ENOUGH = 'long-enough';

export function readFilterParams(params, defaults) {
  const filters = {...defaults};
  for (const [key, value] of Object.entries(defaults)) {
    if (key === 'unverified' || !params.has(key)) continue;
    filters[key] = typeof value === 'boolean' ? params.get(key) === 'true' : params.get(key);
  }
  return filters;
}

function isoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null;
  const date = new Date(value);
  return Number.isFinite(+date) && date.toISOString().slice(0, 10) === value ? value : null;
}

export function publishedStart(job) {
  const intake = job.intake;
  return intake?.provenance !== 'cache' ? intake?.published_start || null : null;
}

export function startCompatibility(job) {
  const value = publishedStart(job);
  const {firstStart, lastStart} = STUDENT_PLACEMENT;
  if (isoDate(value)) return value >= firstStart && value <= lastStart ? 'compatible' : 'incompatible';
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(value || '')) return 'unknown';

  // Compare the entire published month without assigning a start day.
  const firstMonth = firstStart.slice(0, 7);
  const lastMonth = lastStart.slice(0, 7);
  if (value < firstMonth || value > lastMonth) return 'incompatible';
  if (value > firstMonth && value < lastMonth) return 'compatible';
  const lastDay = new Date(Date.UTC(+value.slice(0, 4), +value.slice(5), 0)).getUTCDate();
  return `${value}-01` >= firstStart && `${value}-${lastDay}` <= lastStart ? 'compatible' : 'unknown';
}

export function applicationDeadline(job) {
  const value = job.valid_through;
  if (!value) return null;
  if (isoDate(value)) return value;
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})$/i.test(value)
      && Number.isFinite(Date.parse(value))) return isoDate(value.slice(0, 10));
  return null;
}

function explicitDuration(job) {
  return /^(\d+)(?:\s*(?:[-–]|of|or)\s*(\d+))?\s*(weeks?|weken|wochen|semaines?|months?|maanden?|monate?|mois|mesi|meses)(?:\s*\(?\s*(full[- ]time|voltijd|voltijds|vollzeit|temps plein|part[- ]time|deeltijd)\s*\)?)?$/i.exec(job.duration?.trim() || '');
}

export function showDurationFilter(jobs, clock = Date.now()) {
  let count = 0;
  for (const job of jobs) {
    if (job.internship_type !== 'internship' || unreviewedExternal(job) || !verifiedJob(job, clock)
        || !explicitDuration(job)) continue;
    count++;
    if (count >= STUDENT_PLACEMENT.minimumVerifiedDurations) return true;
  }
  return false;
}

export function durationCompatibility(job) {
  const {earliestEnd, minimumWeeks} = STUDENT_PLACEMENT;
  const end = job.intake?.provenance === 'cache' ? null : isoDate(job.intake?.published_end);
  if (end && end >= earliestEnd) return 'compatible';

  const match = explicitDuration(job);
  if (!match) return 'unknown';
  const [, first, last = first, unit, schedule] = match;
  const weeks = /^(?:week|weken|wochen|semaine)/i.test(unit);
  // Bounds preserve explicit calendar-month durations without inventing a start date.
  const minimumDays = Math.min(+first, +last) * (weeks ? 7 : 28);
  const maximumDays = Math.max(+first, +last) * (weeks ? 7 : 31);
  if (maximumDays < minimumWeeks * 7 || /^(?:part|deeltijd)/i.test(schedule || '')) return 'incompatible';
  if (minimumDays >= minimumWeeks * 7 && schedule) return 'compatible';
  return 'unknown';
}

export function matches(job, filters, saved = new Set()) {
  if (unreviewedExternal(job) || job.status === 'closed' || (!filters.unverified && !verifiedJob(job))) return false;
  if (filters.applicationConfirmed && !applicationConfirmed(job)) return false;
  if (filters.saved && !saved.has(job.id)) return false;
  if (filters.country && !job.countries.includes(filters.country)) return false;
  if (filters.region && !(job.region_codes || []).includes(filters.region)) return false;
  if (filters.category && !job.categories.includes(filters.category)) return false;
  const info=languageInfo(job);
  if (filters.workplace === 'unknown' && info.requirements_status !== 'unknown') return false;
  if (filters.workplace && filters.workplace !== 'unknown' && !job.workplace_languages.some(l => l.code === filters.workplace && l.confidence === 'confirmed' && ['required','required-or-working','working'].includes(l.requirement))) return false;
  if (filters.english && info.english_support !== 'documented') return false;
  if (filters.englishOnly && info.english_sufficiency !== 'documented') return false;
  if (filters.ad && job.advertisement_language.code !== filters.ad) return false;
  if (filters.type && job.internship_type !== filters.type) return false;
  if (filters.workMode && job.work_mode !== filters.workMode) return false;
  if (filters.start === START_WINDOW || filters.hideUnknownTiming) {
    const start = startCompatibility(job);
    if (filters.start === START_WINDOW && start === 'incompatible') return false;
    if (filters.hideUnknownTiming && start === 'unknown') return false;
  }
  if (filters.duration === LONG_ENOUGH || filters.hideUnknownTiming) {
    const duration = durationCompatibility(job);
    if (filters.duration === LONG_ENOUGH && duration === 'incompatible') return false;
    if (filters.hideUnknownTiming && duration === 'unknown') return false;
  }
  const haystack = fold([job.title, job.employer, job.city, ...job.countries, ...(job.search_terms || [])].join(' '));
  return fold(filters.q).split(/\s+/).filter(Boolean).every(word => haystack.includes(word));
}
export function rankJobs(jobs, filters, clock = Date.now()) {
  const terms = fold(filters.q).split(/\s+/).filter(Boolean);
  const score = job => terms.reduce((sum, t) => sum + (fold(job.title).includes(t) ? 4 : 0) + (fold(job.employer).includes(t) ? 2 : 0), 0);
  const date = (job, field) => { const parsed = Date.parse(job[field] || ''); return Number.isFinite(parsed) ? parsed : 0; };
  const direct = filters.sort === 'relevance' ? new Set(jobs.filter(job => applicationConfirmed(job, clock))) : null;
  const deadlines = filters.sort === 'deadline'
    ? new Map(jobs.map(job => [job, applicationDeadline(job) || '9999-99-99']))
    : null;
  const documentedStarts = direct && filters.start === START_WINDOW
    ? new Set(jobs.filter(job => startCompatibility(job) === 'compatible'))
    : null;
  return [...jobs].sort((a,b) => {
    if (documentedStarts) {
      const difference = Number(documentedStarts.has(b)) - Number(documentedStarts.has(a));
      if (difference) return difference;
    }
    if (deadlines) {
      const difference = deadlines.get(a).localeCompare(deadlines.get(b));
      if (difference) return difference;
    }
    if (filters.mode === 'nl') { const nl = Number(b.countries.includes('NL')) - Number(a.countries.includes('NL')); if (nl) return nl; }
    if (direct) {
      const delta = score(b) - score(a) || Number(direct.has(b)) - Number(direct.has(a));
      if (delta) return delta;
    }
    const field = filters.sort === 'discovered' ? 'first_discovered_at' : 'published_at';
    return date(b, field) - date(a, field) || a.employer.localeCompare(b.employer) || a.id.localeCompare(b.id);
  });
}
export function stale(updatedAt, clock = Date.now()) { return !updatedAt || clock - Date.parse(updatedAt) > 36*60*60*1000 || !Number.isFinite(Date.parse(updatedAt)) || Date.parse(updatedAt) > clock; }
export function safeUrl(value) { try {const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;} catch {return null;} }

export function evidenceSummary(job, clock = Date.now()) {
  const level = evidenceLevel(job, clock);
  if (level === 'direct') return 'Apply directly — the employer’s application route was checked in the last 48 hours.';
  if (level === 'public') {
    const service = /^EURES\b/i.test(job.source_name || '') || job.source_type === 'eures' ? 'EURES' : 'an official employment service';
    return `Listed on ${service} — check the employer’s page before applying.`;
  }
  if (level === 'current') return 'Open at the last check — read the original posting for application instructions.';
  return 'Availability unconfirmed — check the employer’s site for a current vacancy.';
}

export function verificationMessage(job, clock = Date.now()) {
  if (verifiedJob(job, clock) && publicEmploymentListing(job)) return 'Listed as open by an official public employment service within the last 48 hours. Check the official posting for application instructions.';
  if (applicationConfirmed(job, clock) && job.application_verification.method === 'personio-feed-same-id-static-form') {
    return 'The official Personio feed and the matching application form were checked within the last 48 hours. The submit button may start disabled.';
  }
  if (applicationConfirmed(job, clock)) return 'The current vacancy and its application route were confirmed within the last 48 hours.';
  if (verifiedJob(job, clock)) return 'The listing is current. Check the original posting for application instructions.';
  if (job.status === 'closed') return 'The employer has closed this listing.';
  if (job.link_status === 'review-required' && job.review_note) return job.review_note;
  if (job.link_status === 'public-api-listed') return 'Published by an official public employment service at the last check; the employer’s own application page was not checked. Confirm the details on the official advertisement.';
  const reason = job.verification?.reason || '';
  if (job.verification?.state === 'blocked' || /robots|captcha|access (?:challenge|restricted|denied)|HTTP Error: (?:401|403|429)/i.test(reason)) return 'Access to the employer’s recruiting site was restricted, so we could not confirm current availability or the application route.';
  const stamp = Date.parse(job.last_verified_at || '');
  if (Number.isFinite(stamp) && clock - stamp > 48*60*60*1000) return 'The last confirmation is more than 48 hours old. Check the original posting for current availability.';
  if (/older than|timestamp|stale/i.test(reason)) return 'The last confirmation is no longer current. Check the original posting for current availability.';
  if (/budget|timeout|timed out/i.test(reason)) return 'We could not finish the latest check. The listing may still be available; confirm it on the employer’s site.';
  if (/deadline/i.test(reason)) return 'The closing date could not be confirmed. Check the employer’s current deadline before applying.';
  return 'We could not confirm the current vacancy and its application route. The listing may still be open; check the original employer page.';
}
export function opportunityCounts(jobs, clock = Date.now()) {
  const active = jobs.filter(job => job.status !== 'closed' && !unreviewedExternal(job));
  return {total:active.length,verified:active.filter(job => verifiedJob(job,clock)).length,
    applicationConfirmed:active.filter(job => applicationConfirmed(job, clock)).length,
    publicListings:active.filter(job => verifiedJob(job, clock) && publicEmploymentListing(job)).length,
    unverified:active.filter(job => !verifiedJob(job,clock)).length,
    verifiedInternships:active.filter(job => verifiedJob(job,clock) && job.internship_type==='internship').length,
    verifiedWorkingStudents:active.filter(job => verifiedJob(job,clock) && job.internship_type==='working-student').length,
    verifiedTraineeships:active.filter(job => verifiedJob(job,clock) && job.internship_type==='traineeship').length,
    closed:jobs.filter(job => job.status === 'closed').length,
    internships:active.filter(job => job.internship_type==='internship').length,
    workingStudents:active.filter(job => job.internship_type==='working-student').length,
    traineeships:active.filter(job => job.internship_type==='traineeship').length};
}

// Per-country counts for the map: verified and not-yet-verified active listings.
// Closed listings and unreviewed external hosts are never counted. Multi-country listings count in each country.
export function countryCounts(jobs, clock = Date.now()) {
  const counts = {};
  for (const job of jobs || []) {
    if (job.status === 'closed' || unreviewedExternal(job)) continue;
    const verified = verifiedJob(job, clock);
    const confirmed = applicationConfirmed(job, clock);
    for (const code of new Set(job.countries || [])) {
      const entry = counts[code] || (counts[code] = {verified:0, unverified:0, applicationConfirmed:0});
      if (verified) entry.verified++; else entry.unverified++;
      if (confirmed) entry.applicationConfirmed++;
    }
  }
  return counts;
}
// Countries outside the EU: most students need a notification, permit or visa.
export const PERMIT_NOTES = {
  CH: {text: 'Switzerland is not in the EU. For EU/EFTA citizens the employer must notify an internship of up to 3 months per calendar year online; a longer internship needs a short-term L EU/EFTA permit before it starts. Students from other countries need a work permit.', url: 'https://www.sem.admin.ch/sem/en/home/themen/fza_schweiz-eu-efta/meldeverfahren.html', source: 'State Secretariat for Migration (SEM)'},
  GB: {text: 'The United Kingdom is not in the EU. Since 2021 EU students need a visa for an internship, usually the Government Authorised Exchange (Temporary Work) visa through an approved sponsor; a visitor visa does not allow internships.', url: 'https://www.gov.uk/government-authorised-exchange', source: 'GOV.UK'},
};

// Official languages per country, used to tell local-language ads from English ones.
export const NATIONAL_LANGUAGES = {AT:['de'],BE:['nl','fr','de'],BG:['bg'],HR:['hr'],CY:['el','tr'],CZ:['cs'],DK:['da'],EE:['et'],FI:['fi','sv'],FR:['fr'],DE:['de'],GR:['el'],HU:['hu'],IE:['en','ga'],IT:['it'],LV:['lv'],LT:['lt'],LU:['lb','fr','de'],MT:['mt','en'],NL:['nl'],PL:['pl'],PT:['pt'],RO:['ro'],SK:['sk'],SI:['sl'],ES:['es','ca','eu','gl'],SE:['sv'],CH:['de','fr','it','rm'],GB:['en']};

function adLanguageKind(code, countries) {
  if (code === 'en') return 'english';
  if (code === 'unknown') return 'unknown';
  return countries.some(country => NATIONAL_LANGUAGES[country]?.includes(code)) ? 'local' : 'other';
}

function currentAdLanguage(job, clock) {
  if (unreviewedExternal(job) || !verifiedJob(job, clock)) return null;
  return job.advertisement_language?.code || 'unknown';
}

// Each current ad counts once in the Europe-wide mix, even when it covers several countries.
export function catalogueAdLanguages(jobs, clock = Date.now()) {
  const mix = {english:0, local:0, other:0, unknown:0};
  const byLanguage = {};
  for (const job of jobs) {
    const code = currentAdLanguage(job, clock);
    if (!code) continue;
    mix[adLanguageKind(code, job.countries || [])]++;
    byLanguage[code] = (byLanguage[code] || 0) + 1;
  }
  return {mix, byLanguage};
}

// Verified listings per country and advertisement language: {NL:{nl:3,en:2,unknown:1}}.
export function countryLanguageCounts(jobs, clock = Date.now()) {
  const counts = {};
  for (const job of jobs || []) {
    const code = currentAdLanguage(job, clock);
    if (!code) continue;
    for (const country of new Set(job.countries || [])) {
      const entry = counts[country] || (counts[country] = {});
      entry[code] = (entry[code] || 0) + 1;
    }
  }
  return counts;
}

// English and local-language ads first, then any other language, then unknown.
export function languageBreakdown(country, byLanguage = {}) {
  const order = {english:0, local:1, other:2, unknown:3};
  return Object.entries(byLanguage).filter(([, n]) => n > 0)
    .map(([code, count]) => ({code, count, kind: adLanguageKind(code, [country])}))
    .sort((a, b) => order[a.kind] - order[b.kind] || b.count - a.count || a.code.localeCompare(b.code));
}

// Colour bucket for a verified count: 0 none, 1, 2-4, 5-9, 10-24, 25+.
export function countBucket(n) { return n <= 0 ? 0 : n === 1 ? 1 : n < 5 ? 2 : n < 10 ? 3 : n < 25 ? 4 : 5; }

export function provincialJobs(jobs, report, filters = {}) {
  const verifiedIds = new Set(report.verified_hr_internship_ids);
  return jobs.filter(job => (job.region_codes || []).includes(report.region_code)
    && job.internship_type === 'internship'
    && (verifiedIds.has(job.id) || (filters.unverified && !verifiedJob(job)))
    && matches(job, filters));
}

export function completeRecentInventory(company,sources,reports,clock=Date.now()) {
  const ids=company.source_ids.filter(id=>sources.some(s=>s.id===id && s.enabled));
  return ids.length>0 && ids.every(id=>{
    const report=reports.find(r=>r.id===id), checked=Date.parse(report?.checked_at || '');
    return report?.status==='ok' && report.complete!==false && Number.isFinite(checked) && checked<=clock && clock-checked<=48*60*60*1000;
  });

}

// Evidence level shown on cards and in counts. Never upgrades a record: 'direct' requires applicationConfirmed().
// 'direct' = verified application route · 'public' = current on a public employment service · 'current' = current listing,
// application route not confirmed · 'lead' = not currently verified.
export function evidenceLevel(job, clock = Date.now()) {
  if (applicationConfirmed(job, clock)) return 'direct';
  if (!verifiedJob(job, clock)) return 'lead';
  return publicEmploymentListing(job) ? 'public' : 'current';
}

// Display-only map zoom: a viewBox of `factor`× magnification centred on (cx, cy), clamped inside the base viewBox.
// The geographic dataset is never changed.
export function zoomViewBox(base, cx, cy, factor = 1) {
  const [bx, by, bw, bh] = String(base).trim().split(/[\s,]+/).map(Number);
  const f = Math.min(Math.max(Number(factor) || 1, 1), 6);
  const w = bw / f, h = bh / f;
  const x = Math.min(Math.max(cx - w / 2, bx), bx + bw - w);
  const y = Math.min(Math.max(cy - h / 2, by), by + bh - h);
  return [x, y, w, h].map(n => Math.round(n * 10) / 10);
}
