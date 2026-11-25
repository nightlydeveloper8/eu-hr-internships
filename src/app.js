import { corporateListingMetadata, agencyClientLabel, studentEligibilityLabel, adLanguageLabel, adLanguageName, START_WINDOW, LONG_ENOUGH, STUDENT_PLACEMENT, durationCompatibility, showDurationFilter, readFilterParams, publishedStart, applicationDeadline, evidenceSummary, matches, rankJobs, stale, safeUrl, languageInfo, verifiedJob, verificationMessage, applicationConfirmed, publicEmploymentListing, evidenceLevel, opportunityCounts, unverifiedFallback, shareableFilterParams, countryCounts, countryLanguageCounts, catalogueAdLanguages, languageBreakdown, PERMIT_NOTES } from './logic.js';
import { drawMap, describeCountry, describeLanguages, countryFacts } from './map.js';

const $ = id => document.getElementById(id);
const defaults = {q:'',country:'',region:'',category:'',workplace:'',english:false,englishOnly:false,ad:'',type:'',workMode:'',start:'',duration:'',hideUnknownTiming:false,unverified:false,applicationConfirmed:false,saved:false,mode:'nl',sort:'relevance'};
const advancedKeys = ['region','type','workMode','ad','english','englishOnly','unverified'];
const filters = {...defaults};
let catalog, coverage, registry, geography, sourceRegistry, limit = 20, saved = new Set(), persistent = true, mapView, counts = {}, languageCounts = {};
try { const stored = JSON.parse(localStorage.getItem('people-placement:saved') || '[]'); if (Array.isArray(stored)) saved = new Set(stored.filter(x => typeof x === 'string')); } catch { persistent = false; }
const bindings = {'search':'q','country':'country','region':'region','category':'category','workplace-language':'workplace','english':'english','english-only':'englishOnly','ad-language':'ad','type':'type','work-mode':'workMode','start-window':'start','duration':'duration','hide-unknown-timing':'hideUnknownTiming','include-unverified':'unverified','sort':'sort'};
const motion = () => matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';

function el(tag, cls, text) { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; }
function option(select, value, text) { const o = document.createElement('option'); o.value = value; o.textContent = text; select.append(o); }
function date(value) { if (!value) return 'Unknown'; const d = new Date(value); return Number.isFinite(d.valueOf()) ? d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',...(/^\d{4}-\d{2}-\d{2}$/.test(value) ? {timeZone:'UTC'} : {hour:'2-digit',minute:'2-digit',timeZoneName:'short'})}) : 'Unknown'; }
function shortDate(value) { const d = new Date(value || ''); return Number.isFinite(d.valueOf()) ? d.toLocaleDateString('en-GB',{day:'numeric',month:'short'}) : null; }
function ago(value) {
  const t = Date.parse(value || ''); if (!Number.isFinite(t)) return 'update time unknown';
  const minutes = Math.max(0, Math.round((Date.now() - t) / 60000));
  if (minutes < 60) return `updated ${minutes || 1} min ago`;
  const hours = Math.round(minutes / 60); if (hours < 36) return `updated ${hours} h ago`;
  return `updated ${Math.round(hours / 24)} days ago`;
}
function displayMode(mode) { return {'hybrid':'Hybrid','on-site':'On-site','remote':'Remote','unspecified':'Arrangement unspecified'}[mode] || 'Arrangement unspecified'; }
function fillRegions() { const select=$('region');select.replaceChildren();option(select,'','All regions / unknown');for(const u of geography.units.filter(u=>u.level===2&&!u.extra_region&&(!filters.country||u.country===filters.country)).sort((a,b)=>a.name.localeCompare(b.name)))option(select,u.code,filters.country?u.name:`${u.name} · ${catalog.countries[u.country]}`); }
function syncControls() { fillRegions(); for (const [id,key] of Object.entries(bindings)) { if ($(id).type === 'checkbox') $(id).checked = filters[key]; else $(id).value = filters[key]; } for (const input of document.querySelectorAll('[name="mode"]')) input.checked = input.value === filters.mode; }
function updateSaved() { $('saved-count').textContent = saved.size; $('saved-nav').setAttribute('aria-pressed',String(filters.saved)); }
function heart(on) { const s = document.createElementNS('http://www.w3.org/2000/svg','svg'); s.setAttribute('viewBox','0 0 24 24'); s.setAttribute('aria-hidden','true'); const p = document.createElementNS('http://www.w3.org/2000/svg','path'); p.setAttribute('d','M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z'); s.append(p); s.classList.toggle('filled', on); return s; }
function save(id, button, title) {
  if (saved.has(id)) saved.delete(id); else saved.add(id);
  try { localStorage.setItem('people-placement:saved',JSON.stringify([...saved])); } catch { persistent = false; notice(); }
  updateSaved();
  if (filters.saved) render();
  else { const on = saved.has(id); button.setAttribute('aria-pressed',String(on)); button.replaceChildren(heart(on)); button.setAttribute('aria-label',`${on ? 'Unsave' : 'Save'} ${title}`); button.classList.add('pulse'); setTimeout(() => button.classList.remove('pulse'), 400); }
}
function reset() { Object.assign(filters,defaults); limit=20; syncControls(); render(); }

const requirementLabel = requirement => ({preferred:'preferred',alternative:'alternative',working:'working language','required-or-working':'required',required:'required'}[requirement] || 'mentioned');
const EVIDENCE = {
  direct: {label:'Direct application verified', cta:'Apply on employer site'},
  public: {label:'Public employment service', cta:'View official listing'},
  current: {label:'Current listing', cta:'View at employer'},
  lead: {label:'Lead to check', cta:'Check at employer'},
};
function card(job) {
  const corporate = corporateListingMetadata(job, sourceRegistry.get(job.source_id));
  const level = evidenceLevel(job);
  const isPublic = publicEmploymentListing(job);
  const confirmed = applicationConfirmed(job);
  const undisclosedOnEures = /^Employer not disclosed(?: \(see EURES advertisement\))?$/i.test(job.employer?.trim())
    && (job.employer.toLowerCase().includes('eures') || /^EURES\b/i.test(job.source_name || ''));
  const publisher = undisclosedOnEures ? 'EURES' : job.employer;
  const article = el('article','job-card'); article.dataset.evidence = level;
  const heading = el('div','card-heading');
  const monogram = el('div','company-monogram',(publisher || '?').trim()[0]?.toUpperCase() || '?');
  monogram.setAttribute('aria-hidden', 'true'); heading.append(monogram);
  const org = el('div','card-org');
  const company = el('p','company-line',publisher);
  if (undisclosedOnEures) {
    company.classList.add('with-employer-note');
    company.append(el('span','job-employer-note','Employer not disclosed'));
  }
  org.append(company);
  const agencyLabel = agencyClientLabel(job);
  if (!corporate && agencyLabel) org.append(el('p','job-employer-note',agencyLabel));
  const eligibilityLabel = studentEligibilityLabel(job);
  if (!corporate && eligibilityLabel) org.append(el('p','job-employer-note',eligibilityLabel));
  const where = [job.city, ...(job.countries || []).map(c => catalog.countries[c] || c)].filter(Boolean);
  org.append(el('p','job-location',[...new Set(where)].join(' · ')));
  heading.append(org);
  const on = saved.has(job.id);
  const bookmark = el('button','save-button'); bookmark.type='button'; bookmark.append(heart(on));
  bookmark.setAttribute('aria-label',`${on ? 'Unsave' : 'Save'} ${job.title}`); bookmark.setAttribute('aria-pressed',String(on));
  bookmark.addEventListener('click',()=>save(job.id,bookmark,job.title));
  heading.append(bookmark); article.append(heading);

  const h3 = el('h3','job-title'); const titleLink = el('a','',job.title); titleLink.href = (corporate ? corporate.url : safeUrl(job.url)) || '#'; titleLink.target = '_blank'; titleLink.rel = 'noopener noreferrer'; h3.append(titleLink); article.append(h3);

  if (corporate) {
    const posted = shortDate(corporate.publishedAt);
    article.append(el('p','posted',posted ? `Posted ${posted}` : 'Publication date not stated'));
    return article;
  }

  const meta = [catalog.categories[job.category]];
  const start = publishedStart(job);
  const deadline = applicationDeadline(job);
  meta.push(start ? `Start: ${start}` : 'Start date not stated – ask the employer');
  if (job.duration) meta.push(job.duration);
  if (durationCompatibility(job) === 'unknown') meta.push('Confirm duration and hours with the employer');
  if (deadline) meta.push(`Apply by ${date(deadline)}`);
  if (job.work_mode && job.work_mode !== 'unspecified') meta.push(displayMode(job.work_mode));
  article.append(el('p','card-meta',meta.filter(Boolean).join(' · ')));

  const tags = el('div','job-tags');
  tags.append(el('span',`evidence-badge ${level}`, level === 'lead' && job.verification?.state === 'blocked' ? 'Source blocked · lead' : EVIDENCE[level].label));
  const info = languageInfo(job);
  const langs = job.workplace_languages || [];
  const languageTags = [];
  if (info.english_sufficiency === 'documented') languageTags.push(['tag lang english','English alone: documented']);
  else if (info.english_support === 'documented') languageTags.push(['tag lang english','English: documented']);
  for (const code of [...new Set(langs.map(l=>l.code))].filter(c=>c!=='en')) languageTags.push(['tag lang',`${catalog.languages[code] || code} · ${requirementLabel(langs.find(l=>l.code===code)?.requirement)}`]);
  for (const [cls, text] of languageTags.slice(0,3)) tags.append(el('span',cls,text));
  if (languageTags.length > 3) tags.append(el('span','tag lang',`+${languageTags.length - 3}`));
  if (info.requirements_status === 'unknown' && !languageTags.length) tags.append(el('span','tag muted','Language not specified'));
  if (job.also_open_to_recent_graduates === true) tags.append(el('span','tag','Also open to recent graduates'));
  article.append(tags);

  article.append(el('p',`verification-explanation${level === 'lead' ? ' warn' : ''}`,evidenceSummary(job)));
  for (const code of new Set(job.countries||[])) if (PERMIT_NOTES[code]) article.append(permitNote(code));

  const bottom = el('div','card-bottom');
  const posted = shortDate(job.published_at);
  bottom.append(el('p','posted',posted ? `Posted ${posted}` : `Found ${shortDate(job.first_discovered_at) || 'recently'} · post date unknown`));
  const destination = isPublic ? job.url : confirmed ? job.application_verification.url : job.apply_url;
  const apply = el('a',`apply-link ${level}`); apply.append(el('span','',EVIDENCE[level].cta),el('span','arrow','↗'));
  apply.href = safeUrl(destination) || safeUrl(job.url) || '#'; apply.target = '_blank'; apply.rel = 'noopener noreferrer';
  apply.setAttribute('aria-label',`${EVIDENCE[level].cta}: ${job.title}, ${undisclosedOnEures ? 'via EURES' : job.employer}`);
  bottom.append(apply); article.append(bottom);

  const details = el('details','job-details'); details.append(el('summary','','Details & language evidence'));
  const dl = el('dl'); function row(k,v,cls){ dl.append(el('dt','',k),el('dd',cls,v)); }
  row('Internship type',`${job.internship_type.replaceAll('-',' ')} · ${job.internship_confidence}`);
  row('Arrangement',displayMode(job.work_mode));
  row('Duration',job.duration || 'Unspecified');
  row('Advertisement',adLanguageLabel(job.advertisement_language, catalog.languages));
  for (const lang of langs) row(catalog.languages[lang.code],`“${lang.evidence}” · ${requirementLabel(lang.requirement)}`,'evidence');
  for (const excerpt of info.unnamed_language_evidence || []) row('Other language requirements', `“${excerpt}”`, 'evidence');
  if (!langs.length) row('Workplace language','No explicit statement extracted. Check the original posting.');
  row('English alone',info.english_sufficiency==='documented' ? 'Explicitly documented' : 'Unknown; English evidence does not establish sufficiency');
  row('Student enrolment',job.enrollment || 'Unspecified. Check the employer’s requirements.');
  row('Source',`${job.source_name} · ${job.source_type}`);
  row('Last seen on board',date(job.last_seen_at));
  row('Last verification attempt',date(job.verification?.checked_at));
  row('Vacancy last verified',verifiedJob(job) ? date(job.last_verified_at) : 'No current verification');
  row('Availability evidence',verificationMessage(job));
  if (job.intake) {
    row('Published start',job.intake.published_start || job.intake.alternatives?.join(' / ') || 'Not specified; confirm with the employer.');
    const provenance={live:'Official vacancy',feed:'Official feed',cache:'Historical cached evidence'}[job.intake.provenance];
    if (provenance) row('Start evidence',`${provenance} · observed ${date(job.intake.checked_at)}`);
  }
  details.append(dl); article.append(details);
  return article;
}
function permitNote(code) {
  const note = PERMIT_NOTES[code], p = el('p','permit-note',note.text+' ');
  const a = el('a','',`Source: ${note.source} ↗`); a.href = note.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; p.append(a); return p;
}
function scrollToResults() { $('opportunities').scrollIntoView({behavior: motion(), block: 'start'}); }
function selectCountry(code, scroll = true) {
  filters.country = code; filters.region = ''; limit = 20;
  syncControls(); render();
  if (scroll && code) scrollToResults();
}
function factList(c) {
  const list = el('ul','panel-facts');
  for (const fact of countryFacts(c)) { const li = el('li',`fact-${fact.kind}`); li.append(el('b','',String(fact.value)), el('span','',fact.label)); list.append(li); }
  return list;
}
const adShare = new Intl.NumberFormat('en', {style:'percent', maximumFractionDigits:1});
function languageSummary(mix, heading = 'h3') {
  const labels = {english:'English', local:'Local language', bilingual:'Bilingual', multilingual:'Multilingual', other:'Other languages', unknown:'Unknown'};
  const total = Object.values(mix).reduce((sum, count) => sum + count, 0);
  const summary = el('div','ad-language-summary');
  summary.append(el(heading,'ad-language-title','Language of current ads'));
  const bar = el('div','ad-language-bar'); bar.setAttribute('aria-hidden','true');
  const legend = el('ul','ad-language-legend');
  for (const [kind, label] of Object.entries(labels)) {
    const count = mix[kind] || 0;
    if (count) {
      const segment = el('span',kind);
      segment.style.flexGrow = String(count);
      bar.append(segment);
    }
    if (count || (kind !== 'other' && kind !== 'multilingual')) {
      const row = el('li',kind);
      row.append(el('span','',label), el('strong','',`${count} · ${adShare.format(total ? count / total : 0)}`));
      legend.append(row);
    }
  }
  summary.append(bar, legend, el('p','ad-language-note','Ad language and workplace requirements are separate.'));
  return summary;
}
function updatePanel() {
  const panel = $('country-panel'); panel.replaceChildren();
  const code = filters.country;
  $('top-section').hidden = Boolean(code);
  const languageSection = $('language-section');
  languageSection.hidden = Boolean(code) || !languageSection.querySelector('.ad-language-summary');
  if (!code) {
    panel.classList.remove('has-country');
    panel.append(el('p','panel-label','Start exploring'), el('p','panel-empty','Hover a country to preview it. Select it to see its internships — or start with a leader below.'));
    return;
  }
  panel.classList.add('has-country');
  const c = counts[code] || {verified:0, unverified:0, applicationConfirmed:0};
  const head = el('div','panel-head');
  head.append(el('p','panel-label','Selected country'));
  const clear = el('button','icon-button','×'); clear.type = 'button'; clear.setAttribute('aria-label','Clear country selection');
  clear.addEventListener('click', () => { filters.country = ''; filters.region = ''; syncControls(); render(); });
  head.append(clear);
  panel.append(head, el('h2','panel-country',catalog.countries[code] || code));
  if (c.verified || c.unverified) panel.append(factList(c));
  else panel.append(el('p','panel-empty','No openings observed yet. Our collection is still growing here — this does not mean there are no internships.'));
  const breakdown = languageBreakdown(code, languageCounts[code]);
  if (breakdown.length) {
    const mix = {};
    for (const {count, kind} of breakdown) mix[kind] = (mix[kind] || 0) + count;
    const langs = el('div','panel-languages'); langs.append(languageSummary(mix));
    const row = el('div','chip-row');
    for (const {code: lang, count, kind} of breakdown) {
      const b = el('button',`language-chip ${kind}`); b.type = 'button';
      b.append(el('span','',adLanguageName(lang, catalog.languages)), el('b','',String(count)));
      b.setAttribute('aria-label', `Show ${count} current ads in ${catalog.countries[code] || code} with advertisement language ${adLanguageName(lang, catalog.languages)}`);
      b.addEventListener('click', () => { filters.ad = lang; filters.unverified = false; filters.applicationConfirmed = false; selectCountry(code); });
      row.append(b);
    }
    if (row.children.length) langs.append(row);
    panel.append(langs);
  }
  if (PERMIT_NOTES[code]) panel.append(permitNote(code));
  const actions = el('div','panel-actions');
  const show = el('button','btn btn-primary', c.verified ? `Show ${c.verified} ${c.verified === 1 ? 'opening' : 'openings'} ↓` : c.unverified ? 'See leads to check ↓' : 'Show this country ↓');
  show.type = 'button';
  show.addEventListener('click', () => { filters.unverified = !c.verified && c.unverified > 0; filters.applicationConfirmed = false; selectCountry(code); });
  actions.append(show);
  if (c.applicationConfirmed) {
    const direct = el('button','btn btn-outline'); direct.type = 'button';
    direct.append(el('i','key-dot'), `Direct only (${c.applicationConfirmed})`);
    direct.addEventListener('click', () => { filters.unverified = false; filters.applicationConfirmed = true; selectCountry(code); });
    actions.append(direct);
  }
  panel.append(actions);
}
function urlState() { const params=shareableFilterParams(filters,defaults); try { history.replaceState(null,'',`${location.pathname}${params.size?'?'+params:''}${location.hash}`); } catch {} }

function render() {
  const selection=opportunityCounts(catalog.jobs.filter(j=>matches(j,{...filters,unverified:true,applicationConfirmed:false},saved)));
  const jobs=rankJobs(catalog.jobs.filter(j=>matches(j,filters,saved)),filters);
  $('verified-view').setAttribute('aria-pressed',String(!filters.unverified && !filters.applicationConfirmed));
  $('application-view').setAttribute('aria-pressed',String(filters.applicationConfirmed));
  $('application-view-count').textContent=selection.applicationConfirmed;
  $('unverified-view').setAttribute('aria-pressed',String(filters.unverified));
  $('include-unverified').checked=filters.unverified;
  $('verified-view-count').textContent=selection.verified;
  $('unverified-view-count').textContent=selection.total;
  $('unverified-notice').hidden=!filters.unverified;
  $('verification-counts').textContent=`${selection.applicationConfirmed} direct · ${selection.publicListings} via public employment services · ${selection.unverified} leads to check`;
  const archive=opportunityCounts(catalog.jobs);
  $('catalog-counts').textContent=`${catalog.jobs.length} archived records across all countries and types; ${archive.closed} closed listing${archive.closed===1?'':'s'} excluded. An archived record is not a confirmed opening.`;
  $('result-count').textContent=jobs.length;
  $('result-label').textContent=filters.saved ? (jobs.length===1 ? 'saved internship' : 'saved internships') : jobs.length===1 ? 'internship' : 'internships';
  $('scope-label').textContent=filters.country ? `in ${catalog.countries[filters.country]}` : filters.mode==='nl' ? 'across Europe · Netherlands first' : 'across Europe';
  const host=$('jobs'); host.replaceChildren(); host.setAttribute('aria-busy','false');
  if (!jobs.length) {
    const currentOpeningsAvailable = filters.applicationConfirmed && selection.verified > 0;
    const unverifiedLeadsAvailable = !filters.saved && !filters.unverified && selection.verified === 0 && selection.unverified > 0;
    const empty=el('div','empty-state');
    empty.append(
      el('div','empty-icon',filters.saved?'♡':'◎'),
      el('h3','',currentOpeningsAvailable?'No verified direct applications match':filters.saved?'Your shortlist lives here.':unverifiedLeadsAvailable?'No current openings match':'No matching internships'),
      el('p','',currentOpeningsAvailable?`${selection.verified} current openings match your other filters.`:filters.saved?'Save internships with the heart button. Your shortlist stays in this browser.':unverifiedLeadsAvailable?`There are ${selection.unverified} leads in this selection. These are NOT confirmed openings; check availability on the employer’s official website.`:'Nothing in our current collection matches. Try another country or widen your filters — an empty result does not mean no internships exist.')
    );
    const action=el('button','btn btn-outline');action.type='button';
    if(currentOpeningsAvailable){action.textContent='Show all current openings';action.addEventListener('click',()=>{filters.applicationConfirmed=false;limit=20;syncControls();render();});}
    else if(unverifiedLeadsAvailable){action.textContent='Explore leads to check';action.addEventListener('click',()=>{filters.unverified=true;filters.applicationConfirmed=false;limit=20;syncControls();render();});}
    else if(filters.saved){action.textContent='Back to all internships';action.addEventListener('click',()=>{filters.saved=false;render();});}
    else{action.textContent='Reset filters';action.addEventListener('click',reset);}
    empty.append(action); host.append(empty);
  } else {
    const fragment=document.createDocumentFragment();
    for(const job of jobs.slice(0,limit)) fragment.append(card(job));
    host.append(fragment);
  }
  $('load-more').hidden=jobs.length<=limit;
  $('show-all').hidden=jobs.length<=limit;
  $('show-all').textContent=`Show all ${jobs.length}`;
  $('result-pagination').textContent=jobs.length ? `Showing ${Math.min(jobs.length,limit)} of ${jobs.length} matching internships` : '';
  $('active-filters').replaceChildren();
  const labels = {q:v=>`“${v}”`,country:v=>catalog.countries[v],region:v=>geography.units.find(u=>u.code===v)?.name,category:v=>catalog.categories[v],workplace:v=>v==='unknown'?'Language requirements unknown':`Works in ${catalog.languages[v]}`,ad:v=>`Advertisement language: ${adLanguageName(v, catalog.languages)}`,english:()=>'English evidence',englishOnly:()=>'English alone documented',saved:()=>'Saved only',unverified:()=>'Including leads',applicationConfirmed:()=>'Direct application verified',type:v=>String(v).replaceAll('-',' '),workMode:v=>displayMode(v),start:()=>STUDENT_PLACEMENT.startLabel,duration:()=>STUDENT_PLACEMENT.durationLabel,hideUnknownTiming:()=>'Hide unclear timing'};
  let active = 0;
  for (const [key,value] of Object.entries(filters)) {
    if (value===defaults[key]||['mode','sort'].includes(key)) continue;
    active++;
    const label = labels[key]?.(value) || String(value);
    const chip=el('button','chip'); chip.type='button'; chip.append(el('span','',label), el('span','chip-x','×'));
    chip.setAttribute('aria-label',`Remove filter: ${label}`);
    chip.addEventListener('click',()=>{filters[key]=defaults[key];syncControls();render();});
    $('active-filters').append(chip);
  }
  if (active > 1) { const clear=el('button','link-button','Clear all'); clear.type='button'; clear.addEventListener('click',reset); $('active-filters').append(clear); }
  const advanced = advancedKeys.filter(k => filters[k] !== defaults[k]).length + (filters.mode !== defaults.mode ? 1 : 0);
  $('advanced-count').hidden = !advanced; $('advanced-count').textContent = advanced;
  host.classList.remove('is-updating'); void host.offsetWidth; host.classList.add('is-updating');
  mapView?.select(filters.country); updatePanel();
  updateSaved(); urlState();
}
function notice() {
  const messages=[];
  if(stale(catalog.updated_at)) messages.push('The collection is older than 36 hours. Check the employer’s posting for current availability.');
  if(unverifiedFallback(catalog)) messages.push('No listings currently pass the 48-hour verification rule. Previously collected records are available as leads to check, NOT confirmed openings.');
  if(catalog.update_status==='failed')messages.push('The latest collection failed. Previously collected listings remain available; confirm availability with the employer.');
  if(!persistent)messages.push('Browser storage is unavailable. Saved internships will last only for this visit.');
  $('data-notice').hidden=!messages.length;$('data-notice').textContent=messages.join(' ');
  const limited=['partial','failed'].includes(catalog.update_status);
  $('collection-status').hidden=!limited;
  if(limited){
    const runs=coverage.sources || [];
    const completed=runs.filter(source=>source.status==='ok').length;
    const partial=runs.filter(source=>source.status==='partial').length;
    const failed=runs.filter(source=>!['ok','partial'].includes(source.status)).length;
    $('collection-status-title').textContent=catalog.update_status==='failed' ? 'Latest collection failed · saved listings remain available' : 'Partial coverage · some employer checks are incomplete';
    $('collection-status-detail').textContent=`Last published ${date(catalog.updated_at)}. Source checks: ${completed} completed, ${partial} partial, ${failed} failed or blocked. Some recruiting sites restrict automated access or could not be read completely. Previously collected listings are kept. Use “Include leads to check” to explore listings whose current availability or application route could not be confirmed.`;
  }
}
function showCoverage() {
  if (!$('coverage-table').children.length) {
    const internships = catalog.jobs.filter(j => j.internship_type === 'internship');
    const totals = opportunityCounts(internships);
    for (const c of coverage.countries) {
      const country = opportunityCounts(internships.filter(j => j.countries.includes(c.code)));
      const tr = el('tr');
      for (const value of [c.name,country.verified,country.applicationConfirmed,c.sources_with_observed_jobs]) tr.append(el('td','',value));
      $('coverage-table').append(tr);
    }
    for (const [value, text] of [[totals.verified,'current HR internships'],[totals.applicationConfirmed,'with a verified direct application'],[totals.publicListings,'via public employment services']]) {
      const s = el('span'); s.append(el('b','',String(value)), ` ${text}`); $('quality-summary').append(s);
    }
    const reports = new Map(coverage.sources.map(s => [s.id,s]));
    for (const source of registry) {
      const report = reports.get(source.id);
      const status = source.enabled ? report?.access_state || report?.status || 'not checked' : source.status || 'discovery only';
      const p = el('p','',`${source.employer} · ${source.adapter} · ${status}`);
      const current = internships.filter(j => verifiedJob(j) && (j.source_id === source.id || j.duplicate_source_ids?.includes(source.id))).length;
      p.append(el('small','',report?.error || source.review_notes || `${report?.records_inspected ?? report?.collected ?? 0} public job records read; ${current} current HR internships in the catalog`));
      const a = el('a','','Source website ↗');
      a.href = safeUrl(source.career_url)||'#'; a.target='_blank'; a.rel='noopener noreferrer';
      p.append(a); $('source-health').append(p);
    }
  }
  $('coverage-dialog').showModal();
}

// Advanced filters drawer (side sheet on desktop, bottom sheet on mobile).
function setDrawer(open) {
  const drawer = $('filters');
  drawer.classList.toggle('is-open', open);
  drawer.inert = !open;
  $('drawer-backdrop').hidden = !open;
  document.body.classList.toggle('drawer-open', open);
  $('filter-toggle').setAttribute('aria-expanded', String(open));
  if (open) drawer.focus({preventScroll:true}); else if (drawer.contains(document.activeElement)) $('filter-toggle').focus({preventScroll:true});
}

function heroStats(totals, countries) {
  const host = $('map-stats'); host.replaceChildren();
  for (const [value, label, cls] of [[totals.verified,'current HR openings',''],[totals.applicationConfirmed,'direct applications verified','direct'],[countries, countries === 1 ? 'country with openings' : 'countries with openings','']]) {
    const box = el('div', cls); box.append(el('dt','',label), el('dd','',String(value))); host.append(box);
  }
}

async function init(){try {
  option($('start-window'), START_WINDOW, STUDENT_PLACEMENT.startLabel);
  const responses=await Promise.all(['catalog','coverage','sources','geography'].map(name=>fetch(`./data/${name}.json`,{cache:'no-cache'})));
  if(responses.some(r=>!r.ok))throw new Error('Data could not be loaded');
  [catalog,coverage,registry,geography]=await Promise.all(responses.map(r=>r.json()));
  sourceRegistry = new Map(registry.map(source => [source.id, source]));
  if(catalog.schema_version!==1||!Array.isArray(catalog.jobs))throw new Error('Unsupported dataset');
  if (showDurationFilter(catalog.jobs)) {
    option($('duration'), LONG_ENOUGH, STUDENT_PLACEMENT.durationLabel);
    $('duration-field').hidden = false;
  }
  for(const [code,name] of Object.entries(catalog.countries).sort((a,b)=>a[1].localeCompare(b[1])))option($('country'),code,name);
  for(const [code,name] of Object.entries(catalog.categories))option($('category'),code,name);
  for(const [code,name] of Object.entries(catalog.languages).sort((a,b)=>a[1].localeCompare(b[1]))){option($('workplace-language'),code,name);option($('ad-language'),code,name);}
  for (const code of ['bilingual', 'multilingual', 'unknown']) option($('ad-language'), code, adLanguageName(code, catalog.languages));
  for(const job of catalog.jobs)job.search_terms=[...job.countries.map(c=>catalog.countries[c]),...job.categories.map(c=>catalog.categories[c])];
  const params = new URLSearchParams(location.search);
  Object.assign(filters, readFilterParams(params, defaults));
  fillRegions();
  for(const [id,key]of Object.entries(bindings))if($(id).tagName==='SELECT'&&![...$(id).options].some(o=>o.value===filters[key]))filters[key]=defaults[key];
  if(!['eu','nl'].includes(filters.mode))filters.mode='nl';
  syncControls();
  for(const [id,key]of Object.entries(bindings))$(id).addEventListener(id==='search'?'input':'change',()=>{filters[key]=$(id).type==='checkbox'?$(id).checked:$(id).value;if(key==='country'){filters.region='';fillRegions();}if(key==='unverified')filters.applicationConfirmed=false;limit=20;render();});
  $('search').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('jobs').scrollIntoView({behavior:motion(),block:'start'});}});
  for (const id of ['verified-view','application-view','unverified-view']) $(id).addEventListener('click',()=>{filters.unverified = id === 'unverified-view'; filters.applicationConfirmed = id === 'application-view'; limit=20; syncControls(); render();});
  for(const radio of document.querySelectorAll('[name="mode"]'))radio.addEventListener('change',()=>{filters.mode=radio.value;render();});
  $('reset').addEventListener('click',reset);
  $('saved-nav').addEventListener('click',()=>{filters.saved=!filters.saved;limit=20;render();scrollToResults();});
  $('load-more').addEventListener('click',()=>{limit+=20;render();});
  $('show-all').addEventListener('click',()=>{limit=catalog.jobs.length;render();});
  $('filter-toggle').addEventListener('click',()=>setDrawer(!$('filters').classList.contains('is-open')));
  $('filters-close').addEventListener('click',()=>setDrawer(false));
  $('drawer-backdrop').addEventListener('click',()=>setDrawer(false));
  $('filters-done').addEventListener('click',()=>{setDrawer(false);$('jobs').scrollIntoView({behavior:motion(),block:'start'});});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('filters').classList.contains('is-open'))setDrawer(false);});
  setDrawer(params.get('view')==='advanced');
  for (const id of ['source-status','coverage-nav','coverage-inline','coverage-trust']) $(id).addEventListener('click',showCoverage);
  $('close-dialog').addEventListener('click',()=>$('coverage-dialog').close());
  $('coverage-dialog').addEventListener('click',e=>{if(e.target===$('coverage-dialog')){const rect=e.target.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)e.target.close();}});

  const clock = Date.now();
  counts = countryCounts(catalog.jobs, clock);
  languageCounts = countryLanguageCounts(catalog.jobs, clock);
  const {mix, byLanguage} = catalogueAdLanguages(catalog.jobs, clock);
  const languageSection = $('language-section');
  if (Object.keys(byLanguage).length) {
    languageSection.prepend(languageSummary(mix, 'h2'));
    languageSection.hidden = false;
  }
  for (const [lang, n] of Object.entries(byLanguage).sort((a, b) => (a[0] === 'en' ? -1 : b[0] === 'en' ? 1 : b[1] - a[1]))) {
    const chip = el('button',`language-chip${lang==='en'?' english':''}`); chip.type = 'button';
    chip.append(el('span','',adLanguageName(lang, catalog.languages)), el('b','',String(n)));
    chip.setAttribute('aria-label', `Show ${n} current ads with advertisement language ${adLanguageName(lang, catalog.languages)}`);
    chip.addEventListener('click', () => { filters.ad = lang; filters.country = ''; filters.region = ''; filters.unverified = false; filters.applicationConfirmed = false; limit = 20; syncControls(); render(); scrollToResults(); });
    $('language-totals').append(chip);
  }
  $('language-filters').hidden = !$('language-totals').children.length;
  const evidence = opportunityCounts(catalog.jobs);
  heroStats(evidence, Object.values(counts).filter(c => c.verified).length);
  $('freshness').textContent = `Live map · ${ago(catalog.updated_at)}`;
  mapView = drawMap({svg: $('eu-map'), tooltip: $('map-tooltip'), wrap: $('map-wrap'), benelux: $('map-benelux'), counts, names: catalog.countries, onSelect: code => selectCountry(code === filters.country ? '' : code, false), languages: code => describeLanguages(languageBreakdown(code, languageCounts[code]), catalog.languages)});
  const zoomed = f => { $('map-zoom-reset').hidden = f <= 1; };
  $('map-zoom-in').addEventListener('click', () => zoomed(mapView.zoom(1)));
  $('map-zoom-out').addEventListener('click', () => zoomed(mapView.zoom(-1)));
  $('map-zoom-reset').addEventListener('click', () => zoomed(mapView.reset()));
  const top = Object.entries(counts).filter(([code, c]) => c.verified && catalog.countries[code]).sort((a, b) => b[1].verified - a[1].verified || b[1].unverified - a[1].unverified).slice(0, 6);
  for (const [code, c] of top) { const chip = el('button','country-chip'); chip.type = 'button'; chip.append(el('span','',catalog.countries[code]), el('b','',String(c.verified))); if (c.applicationConfirmed) chip.append(el('i','key-dot')); chip.setAttribute('aria-label', `${catalog.countries[code]}: ${describeCountry(catalog.countries[code], c)}`); chip.addEventListener('click', () => selectCountry(code, false)); $('top-countries').append(chip); }
  $('browse-all').addEventListener('click', () => { filters.country = ''; filters.region = ''; syncControls(); render(); scrollToResults(); });
  $('direct-only').addEventListener('click', () => { filters.applicationConfirmed = true; filters.unverified = false; limit = 20; syncControls(); render(); scrollToResults(); });
  $('updated-label').textContent=`Last collected ${date(catalog.updated_at)}`;
  notice(); render();
} catch(error){$('jobs').setAttribute('aria-busy','false');$('jobs').replaceChildren(el('div','empty-state','We couldn’t load the employer collection. Please refresh or download the dataset using the link below.'));$('updated-label').textContent='Data unavailable';console.error(error);}}
init();
