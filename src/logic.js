export const fold = value => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export function languageInfo(job) {
  const explicit = (job.workplace_languages || []).filter(l => l.confidence === 'confirmed' && ['required','required-or-working','working','alternative'].includes(l.requirement));
  return job.language_requirements || {requirements_status:explicit.length ? 'explicit' : 'unknown', english_support:(job.workplace_languages || []).some(l=>l.code==='en' && l.confidence==='confirmed' && ['required','required-or-working','working','alternative'].includes(l.requirement)) ? 'documented' : 'unknown', english_sufficiency:'unknown'};
}
export function verifiedJob(job, clock = Date.now()) {
  const stamp=Date.parse(job.last_verified_at || '');
  return job.status === 'open' && job.verification?.state === 'verified' && job.verification?.policy_version === 2 && Number.isFinite(stamp) && stamp <= clock && clock-stamp <= 48*60*60*1000;
}
// Emergency degraded view: expose archived records only as unverified when daily checks are stale.
// This must never change verifiedJob(), policy v2, or the 48-hour freshness threshold.
export function unverifiedFallback(catalog, clock = Date.now()) {
  return stale(catalog?.updated_at, clock) && Array.isArray(catalog?.jobs)
    && catalog.jobs.some(job => job.status !== 'closed')
    && !catalog.jobs.some(job => verifiedJob(job, clock));
}

export function matches(job, filters, saved = new Set()) {
  if (job.status === 'closed' || (!filters.unverified && !verifiedJob(job))) return false;
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
  const haystack = fold([job.title, job.employer, job.city, ...job.countries, ...(job.search_terms || [])].join(' '));
  return fold(filters.q).split(/\s+/).filter(Boolean).every(word => haystack.includes(word));
}
export function rankJobs(jobs, filters) {
  const terms = fold(filters.q).split(/\s+/).filter(Boolean);
  const score = job => terms.reduce((sum, t) => sum + (fold(job.title).includes(t) ? 4 : 0) + (fold(job.employer).includes(t) ? 2 : 0), 0);
  const date = (job, field) => { const parsed = Date.parse(job[field] || ''); return Number.isFinite(parsed) ? parsed : 0; };
  return [...jobs].sort((a,b) => {
    if (filters.mode === 'nl') { const nl = Number(b.countries.includes('NL')) - Number(a.countries.includes('NL')); if (nl) return nl; }
    if (filters.sort === 'relevance') { const delta = score(b) - score(a); if (delta) return delta; }
    const field = filters.sort === 'discovered' ? 'first_discovered_at' : 'published_at';
    return date(b, field) - date(a, field) || a.employer.localeCompare(b.employer) || a.id.localeCompare(b.id);
  });
}
export function stale(updatedAt, clock = Date.now()) { return !updatedAt || clock - Date.parse(updatedAt) > 36*60*60*1000 || !Number.isFinite(Date.parse(updatedAt)) || Date.parse(updatedAt) > clock; }
export function safeUrl(value) { try {const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;} catch {return null;} }

export function verificationMessage(job, clock = Date.now()) {
  if (verifiedJob(job, clock)) return 'The current vacancy and its application route were confirmed within the last 48 hours.';
  if (job.status === 'closed') return 'The employer has closed this listing.';
  if (job.link_status === 'review-required' && job.review_note) return job.review_note;
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
  const active = jobs.filter(job => job.status !== 'closed');
  return {total:active.length,verified:active.filter(job => verifiedJob(job,clock)).length,
    unverified:active.filter(job => !verifiedJob(job,clock)).length,
    verifiedInternships:active.filter(job => verifiedJob(job,clock) && job.internship_type==='internship').length,
    verifiedWorkingStudents:active.filter(job => verifiedJob(job,clock) && job.internship_type==='working-student').length,
    verifiedTraineeships:active.filter(job => verifiedJob(job,clock) && job.internship_type==='traineeship').length,
    closed:jobs.length-active.length,
    internships:active.filter(job => job.internship_type==='internship').length,
    workingStudents:active.filter(job => job.internship_type==='working-student').length,
    traineeships:active.filter(job => job.internship_type==='traineeship').length};
}

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
