export const fold = value => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export function matches(job, filters, saved = new Set()) {
  if (job.status === 'closed' || (!filters.unverified && job.status !== 'open')) return false;
  if (filters.saved && !saved.has(job.id)) return false;
  if (filters.country && !job.countries.includes(filters.country)) return false;
  if (filters.region && !(job.region_codes || []).includes(filters.region)) return false;
  if (filters.category && !job.categories.includes(filters.category)) return false;
  if (filters.workplace && !job.workplace_languages.some(l => l.code === filters.workplace && l.confidence === 'confirmed')) return false;
  if (filters.english && !job.workplace_languages.some(l => l.code === 'en' && l.confidence === 'confirmed')) return false;
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
export function stale(updatedAt, clock = Date.now()) { return !updatedAt || clock - Date.parse(updatedAt) > 36*60*60*1000 || !Number.isFinite(Date.parse(updatedAt)); }
export function safeUrl(value) { try {const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;} catch {return null;} }
