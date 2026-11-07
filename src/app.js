import { matches, rankJobs, stale, safeUrl, languageInfo, verifiedJob, verificationMessage, opportunityCounts } from './logic.js';
const $ = id => document.getElementById(id);
const defaults = {q:'',country:'',region:'',category:'',workplace:'',english:false,englishOnly:false,ad:'',type:'',workMode:'',unverified:false,saved:false,mode:'nl',sort:'relevance'};
const filters = {...defaults};
let catalog, coverage, registry, geography, limit = 20, saved = new Set(), persistent = true;
try { const stored = JSON.parse(localStorage.getItem('people-placement:saved') || '[]'); if (Array.isArray(stored)) saved = new Set(stored.filter(x => typeof x === 'string')); } catch {persistent = false;}
const bindings = {'search':'q','country':'country','region':'region','category':'category','workplace-language':'workplace','english':'english','english-only':'englishOnly','ad-language':'ad','type':'type','work-mode':'workMode','include-unverified':'unverified','sort':'sort'};
function el(tag, cls, text) { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; }
function option(select, value, text) { const o = document.createElement('option'); o.value = value; o.textContent = text; select.append(o); }
function date(value) { if (!value) return 'Unknown'; const d = new Date(value); return Number.isFinite(d.valueOf()) ? d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',...(/^\d{4}-\d{2}-\d{2}$/.test(value) ? {} : {hour:'2-digit',minute:'2-digit',timeZoneName:'short'})}) : 'Unknown'; }
function displayMode(mode) { return {'hybrid':'Hybrid','on-site':'On-site','remote':'Remote','unspecified':'Arrangement unspecified'}[mode] || 'Arrangement unspecified'; }
function fillRegions() { const select=$('region');select.replaceChildren();option(select,'','All regions / unknown');for(const u of geography.units.filter(u=>u.level===2&&!u.extra_region&&(!filters.country||u.country===filters.country)).sort((a,b)=>a.name.localeCompare(b.name)))option(select,u.code,filters.country?u.name:`${u.name} · ${catalog.countries[u.country]}`); }
function syncControls() { fillRegions(); for (const [id,key] of Object.entries(bindings)) { if ($(id).type === 'checkbox') $(id).checked = filters[key]; else $(id).value = filters[key]; } for (const input of document.querySelectorAll('[name="mode"]')) input.checked = input.value === filters.mode; }
function updateSaved() { $('saved-count').textContent = saved.size; $('saved-nav').setAttribute('aria-pressed',filters.saved); }
function save(id, button) { if (saved.has(id)) saved.delete(id); else saved.add(id); try {localStorage.setItem('people-placement:saved',JSON.stringify([...saved]));} catch {persistent = false; notice();} updateSaved(); if (filters.saved) render(); else {button.setAttribute('aria-pressed',saved.has(id)); button.textContent = saved.has(id) ? '♥' : '♡'; button.setAttribute('aria-label',`${saved.has(id) ? 'Unsave' : 'Save'} this internship`);} }
function reset() { Object.assign(filters,defaults); limit=20; syncControls();render(); }
function card(job) {
  const article = el('article','job-card');
  const heading = el('div','card-heading'); heading.append(el('div','company-monogram',job.employer[0]));
  const titleWrap = el('div'); const company = el('div','company-line',job.employer); company.append(el('span','country-tag',job.countries.map(c=>c).join(' · '))); titleWrap.append(company);
  const h3 = el('h3'); const titleLink = el('a','',job.title); titleLink.href = safeUrl(job.url) || '#'; titleLink.target = '_blank'; titleLink.rel = 'noopener noreferrer'; h3.append(titleLink); titleWrap.append(h3);heading.append(titleWrap);
  const bookmark = el('button','save-button',saved.has(job.id) ? '♥' : '♡'); bookmark.type='button';bookmark.setAttribute('aria-label',`${saved.has(job.id) ? 'Unsave' : 'Save'} ${job.title}`);bookmark.setAttribute('aria-pressed',saved.has(job.id)); bookmark.addEventListener('click',()=>save(job.id,bookmark));heading.append(bookmark);article.append(heading);
  const locations = el('div','job-location');locations.append(el('span','',`⌖ ${job.city || catalog.countries[job.country]}`),el('span','',`◷ ${job.duration || 'Duration unspecified'}`),el('span','',`◌ ${displayMode(job.work_mode)}`));article.append(locations);
  const tags = el('div','job-tags');tags.append(el('span','tag',catalog.categories[job.category]));
  const langs = job.workplace_languages;
  const requirementLabel = requirement => ({preferred:'preferred',alternative:'alternative requirement',working:'working language','required-or-working':'required / working',required:'required'}[requirement] || 'unspecified');
  const info=languageInfo(job);
  if (info.english_support==='documented') tags.append(el('span','tag english','English: explicit evidence'));
  if (info.english_sufficiency==='documented') tags.append(el('span','tag english','English alone: documented'));
  for (const code of [...new Set(langs.map(l=>l.code))].filter(c=>c!=='en')) tags.append(el('span','tag',`${catalog.languages[code]} · ${requirementLabel(langs.find(l=>l.code===code)?.requirement)}`));
  if (info.requirements_status==='unknown') tags.append(el('span','tag','Workplace language unspecified'));
  if (!verifiedJob(job)) tags.append(el('span','tag unverified',job.verification?.state==='blocked' ? 'Source blocked' : 'Verification incomplete'));
  article.append(tags);
  if (!verifiedJob(job)) article.append(el('p','verification-explanation',verificationMessage(job)));
  const bottom = el('div','card-bottom'); bottom.append(el('p','',job.published_at ? `Posted ${date(job.published_at)}` : `Found ${date(job.first_discovered_at)} · Posting date unknown`));
  const apply = el('a','apply-link');apply.append(el('span','', 'View at employer'),el('span','', '↗'));apply.href=safeUrl(job.apply_url)||safeUrl(job.url)||'#';apply.target='_blank';apply.rel='noopener noreferrer';apply.setAttribute('aria-label',`View ${job.title} at ${job.employer}`);bottom.append(apply);article.append(bottom);
  const details=el('details','job-details');details.append(el('summary','','Language evidence & practical details'));
  const dl=el('dl');function row(k,v,cls){dl.append(el('dt','',k),el('dd',cls,v));}
  row('Internship type',`${job.internship_type.replaceAll('-',' ')} · ${job.internship_confidence}`);
  row('Advertisement',job.advertisement_language.code ? `${catalog.languages[job.advertisement_language.code]}${job.advertisement_language.confidence==='uncertain' ? ' · estimated' : ''}` : 'Unknown');
  for (const lang of langs) row(catalog.languages[lang.code],`“${lang.evidence}” · ${requirementLabel(lang.requirement)}`,'evidence');
  if (!langs.length) row('Workplace language','No explicit statement extracted. Check the original posting.');
  row('Student enrolment',job.enrollment||'Unspecified. Check the employer’s requirements.');row('Source',`${job.source_name} · ${job.source_type}`);row('Last seen on board',date(job.last_seen_at));row('Last verification attempt',date(job.verification?.checked_at));row('Vacancy last verified',job.verification?.state==='verified' && job.verification?.policy_version===2 ? date(job.last_verified_at) : 'No current verification');row('Availability evidence',verificationMessage(job));row('English alone',info.english_sufficiency==='documented' ? 'Explicitly documented' : 'Unknown; English evidence does not establish sufficiency');
  details.append(dl);article.append(details);return article;
}
function urlState() { const params=new URLSearchParams();for(const [k,v] of Object.entries(filters)) if(v!==defaults[k]) params.set(k,String(v)); try {history.replaceState(null,'',`${location.pathname}${params.size?'?'+params:''}${location.hash}`);}catch{} }
function render() {
  const selection=opportunityCounts(catalog.jobs.filter(j=>matches(j,{...filters,unverified:true},saved)));
  const jobs=rankJobs(catalog.jobs.filter(j=>matches(j,filters,saved)),filters);
  const shown=opportunityCounts(jobs);
  $('verified-view').setAttribute('aria-pressed',String(!filters.unverified));
  $('unverified-view').setAttribute('aria-pressed',String(filters.unverified));
  $('include-unverified').checked=filters.unverified;
  $('verified-view-count').textContent=`(${selection.verified})`;
  $('unverified-view-count').textContent=`(${selection.total})`;
  $('unverified-notice').hidden=!filters.unverified;
  $('verification-counts').textContent=`In this selection: ${selection.verified} verified · ${selection.unverified} unverified. Matching types: ${shown.internships} internship${shown.internships===1?'':'s'}, ${shown.workingStudents} working-student role${shown.workingStudents===1?'':'s'} and ${shown.traineeships} traineeship${shown.traineeships===1?'':'s'}.`;
  const archive=opportunityCounts(catalog.jobs);
  $('catalog-counts').textContent=`${catalog.jobs.length} archived records across all countries and types; ${archive.closed} closed listing${archive.closed===1?'':'s'} excluded. An archived record is not a confirmed opening.`;
  $('result-count').textContent=jobs.length;$('result-label').textContent=filters.saved ? (jobs.length===1 ? 'saved opportunity' : 'saved opportunities') : jobs.length===1 ? 'opportunity' : 'opportunities';
  $('scope-label').textContent=filters.country ? catalog.countries[filters.country] : filters.mode==='nl' ? 'The Netherlands first, then the rest of the EU' : 'Across all 27 European Union countries';
  const host=$('jobs');host.replaceChildren();host.setAttribute('aria-busy','false');
  if (!jobs.length) {const empty=el('div','empty-state');empty.append(el('div','empty-icon',filters.saved?'♡':'◎'),el('h3','',filters.saved?'Your next chapter, saved here.':'A little room to explore.'),el('p','',filters.saved?'Save internships with the heart button. Your shortlist stays in this browser.':'No matching opportunities in our current collection. Try another country or widen your filters.'));const clear=el('button','', 'Show all opportunities');clear.addEventListener('click',reset);empty.append(clear);host.append(empty);}else for(const job of jobs.slice(0,limit)) host.append(card(job));
  $('load-more').hidden=jobs.length<=limit;
  $('show-all').hidden=jobs.length<=limit;
  $('show-all').textContent=`Show all ${jobs.length} matching opportunities`;
  $('result-pagination').textContent=`Showing ${Math.min(jobs.length,limit)} of ${jobs.length} matching opportunities.`;
  $('active-filters').replaceChildren();
  for(const [key,value] of Object.entries(filters)){if(value===defaults[key]||['mode','sort'].includes(key))continue;let label={q:`“${value}”`,country:catalog.countries[value],region:geography.units.find(u=>u.code===value)?.name,category:catalog.categories[value],workplace:value==='unknown'?'Language requirements unknown':`Work: ${catalog.languages[value]}`,ad:`Ad: ${catalog.languages[value]}`,english:'English evidence',englishOnly:'English alone documented',saved:'Saved only',unverified:'Including unverified',type:String(value).replaceAll('-',' '),workMode:displayMode(value)}[key]||String(value);const chip=el('button','chip',label+' ×');chip.type='button';chip.setAttribute('aria-label',`Remove ${label} filter`);chip.addEventListener('click',()=>{filters[key]=defaults[key];syncControls();render();});$('active-filters').append(chip);}
  updateSaved();urlState();
}
function notice() {
  const messages=[];
  if(stale(catalog.updated_at)) messages.push('The collection is older than 36 hours. Check the employer’s posting for current availability.');
  if(catalog.update_status==='failed')messages.push('The latest collection failed. Previously collected listings remain available; confirm availability with the employer.');
  if(!persistent)messages.push('Browser storage is unavailable. Saved jobs will last only for this visit.');
  $('data-notice').hidden=!messages.length;$('data-notice').textContent=messages.join(' ');
  const limited=['partial','failed'].includes(catalog.update_status);
  $('collection-status').hidden=!limited;
  if(limited){
    const runs=coverage.sources || [];
    const completed=runs.filter(source=>source.status==='ok').length;
    const partial=runs.filter(source=>source.status==='partial').length;
    const failed=runs.filter(source=>!['ok','partial'].includes(source.status)).length;
    $('collection-status-title').textContent=catalog.update_status==='failed' ? 'Latest collection failed · saved listings remain available' : 'Collection coverage · some employer checks are incomplete';
    $('collection-status-detail').textContent=`Last published ${date(catalog.updated_at)}. Source checks: ${completed} completed, ${partial} partial, ${failed} failed or blocked. Some recruiting sites restrict automated access or could not be read completely. Previously collected listings are kept. Use “Include unverified opportunities” to explore listings whose current availability or application route could not be confirmed.`;
  }
}
function showCoverage() {if(!$('coverage-table').children.length){for(const c of coverage.countries){const tr=el('tr');tr.append(el('td','',c.name),el('td','',catalog.jobs.filter(j=>verifiedJob(j)&&j.internship_type==='internship'&&j.countries.includes(c.code)).length),el('td','',c.sources_with_observed_jobs));$('coverage-table').append(tr);}for(const text of [`${catalog.jobs.filter(j=>verifiedJob(j)&&j.internship_type==='internship').length} verified HR internships`,`${catalog.jobs.filter(j=>verifiedJob(j)&&j.internship_type==='working-student').length} working-student roles`,`${catalog.jobs.filter(j=>verifiedJob(j)&&j.internship_type==='traineeship').length} traineeships`,`${catalog.jobs.filter(j=>verifiedJob(j)&&languageInfo(j).english_support==='documented').length} verified roles with English evidence`])$('quality-summary').append(el('span','',text));const reports=new Map(coverage.sources.map(s=>[s.id,s]));for(const source of registry){const report=reports.get(source.id);const p=el('p','',`${source.employer} · ${source.adapter} · ${source.enabled ? report?.access_state||report?.status||'not checked' : source.status||'discovery only'}`);p.append(el('small','',report?.error||source.review_notes||`${report?.records_inspected??report?.collected??0} public job records read; ${catalog.jobs.filter(j=>verifiedJob(j)&&j.internship_type==='internship'&&(j.source_id===source.id||j.duplicate_source_ids?.includes(source.id))).length} verified HR internships in the catalog`));const a=el('a','','Employer board ↗');a.href=safeUrl(source.career_url)||'#';a.target='_blank';a.rel='noopener noreferrer';p.append(a);$('source-health').append(p);}}$('coverage-dialog').showModal(); }
async function init(){try {const responses=await Promise.all(['catalog','coverage','sources','geography'].map(name=>fetch(`./data/${name}.json`,{cache:'no-cache'})));if(responses.some(r=>!r.ok))throw new Error('Data could not be loaded');[catalog,coverage,registry,geography]=await Promise.all(responses.map(r=>r.json()));
  if(catalog.schema_version!==1||!Array.isArray(catalog.jobs))throw new Error('Unsupported dataset');
  for(const [code,name] of Object.entries(catalog.countries).sort((a,b)=>a[1].localeCompare(b[1])))option($('country'),code,name);
  for(const [code,name] of Object.entries(catalog.categories))option($('category'),code,name);
  for(const [code,name] of Object.entries(catalog.languages).sort((a,b)=>a[1].localeCompare(b[1]))){option($('workplace-language'),code,name);option($('ad-language'),code,name);}
  for(const job of catalog.jobs)job.search_terms=[...job.countries.map(c=>catalog.countries[c]),...job.categories.map(c=>catalog.categories[c])];
  const params=new URLSearchParams(location.search);for(const [key,def]of Object.entries(defaults)){if(!params.has(key))continue;filters[key]=typeof def==='boolean'?params.get(key)==='true':params.get(key);}
  fillRegions();
  for(const [id,key]of Object.entries(bindings))if($(id).tagName==='SELECT'&&![...$(id).options].some(o=>o.value===filters[key]))filters[key]=defaults[key];if(!['eu','nl'].includes(filters.mode))filters.mode='nl';
  syncControls();for(const [id,key]of Object.entries(bindings))$(id).addEventListener(id==='search'?'input':'change',()=>{filters[key]=$(id).type==='checkbox'?$(id).checked:$(id).value;if(key==='country'){filters.region='';fillRegions();}limit=20;render();});
  for(const [id,include] of [['verified-view',false],['unverified-view',true]])$(id).addEventListener('click',()=>{filters.unverified=include;limit=20;syncControls();render();});
  for(const radio of document.querySelectorAll('[name="mode"]'))radio.addEventListener('change',()=>{filters.mode=radio.value;render();});$('reset').addEventListener('click',reset);$('saved-nav').addEventListener('click',()=>{filters.saved=!filters.saved;render();$('opportunities').scrollIntoView();});$('load-more').addEventListener('click',()=>{limit+=20;render();});$('show-all').addEventListener('click',()=>{limit=catalog.jobs.length;render();});
  $('filter-toggle').addEventListener('click',()=>{const open=$('filters').classList.toggle('is-open');$('filter-toggle').setAttribute('aria-expanded',open);if(open)$('filters').scrollIntoView({block:'start'});});
  $('filters-done').addEventListener('click',()=>{$('filters').classList.remove('is-open');$('filter-toggle').setAttribute('aria-expanded','false');document.querySelector('.results').scrollIntoView({block:'start'});});
  $('source-status').addEventListener('click',showCoverage);$('coverage-nav').addEventListener('click',showCoverage);$('coverage-inline').addEventListener('click',showCoverage);$('close-dialog').addEventListener('click',()=>$('coverage-dialog').close());$('coverage-dialog').addEventListener('click',e=>{if(e.target===$('coverage-dialog')){const rect=e.target.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)e.target.close();}});
  $('updated-label').textContent=`Last collected ${date(catalog.updated_at)}`;notice();render();
} catch(error){$('jobs').setAttribute('aria-busy','false');$('jobs').replaceChildren(el('div','empty-state','We couldn’t load the employer collection. Please refresh or download the dataset using the link below.'));$('updated-label').textContent='Data unavailable';console.error(error);}}
init();
