const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
const labels = {'collected':'Observed inventory read','partial':'Partial reading','discovery-incomplete':'Discovery incomplete','blocked-or-failed':'Blocked / failed','not-recently-checked':'No recent check','unconfigured':'Needs integration'};
const date = value => value ? new Date(value).toLocaleString('en-GB', {timeZone:'Europe/Amsterdam'}) : 'Not yet checked';
const sizeText = row => {
  const size = row.size;
  if (size.qualification === 'unknown' || !size.qualification) return 'Employee size awaiting verification';
  const scope = /site|establishment/.test(size.scope || '') ? 'documented establishment' : /seasonal/.test(size.scope || '') ? 'paid seasonal workforce' : 'employer / group';
  const number = Number.isFinite(size.employees_min) ? `At least ${size.employees_min.toLocaleString('en-GB')} employees` : 'Documented 50+ employee employer';
  return `${number} · ${scope}${size.source_date ? ` · evidence from ${size.source_date}` : ''}`;
};
const link = (url, text) => /^https:\/\//.test(url || '') ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(text)} ↗</a>` : escape(text);
try {
  const responses = await Promise.all(['friesland-coverage','catalog'].map(async name => {
    const response = await fetch(`./data/${name}.json`);
    if (!response.ok) throw new Error('Data temporarily unavailable');
    return response.json();
  }));
  const [report, catalog] = responses;
  const ids = new Set(report.verified_hr_internship_ids);
  const jobs = catalog.jobs.filter(job => ids.has(job.id) && job.status === 'open');
  document.querySelector('#friesland-summary').textContent = `${jobs.length} verified HR internships · ${report.summary.qualified_employers} employers with documented size · ${report.summary.size_unknown} candidates awaiting size checks · ${report.summary.attempted_recently}/${report.summary.employers} employer sites with a collection attempt within 48 hours. Updated ${date(report.generated_at)}.`;
  document.querySelector('#friesland-jobs').innerHTML = jobs.map(job => `<article class="job-card employer-card"><p class="eyebrow">${escape(job.city)}</p><h3>${escape(job.title)}</h3><p>${escape(job.employer)}</p><p>${link(job.url,'Read the internship and apply')}</p><p class="input-note">Link checked ${date(job.last_verified_at)}</p></article>`).join('') || '<p>No currently verified internship in this collection.</p>';
  document.querySelector('#friesland-programmes').innerHTML = report.research_opportunities.filter(item => item.kind === 'open_hr_internship_programme').map(item => `<article class="job-card employer-card"><h3>${escape(item.employer)}</h3><p>${escape(item.city)}</p><p>${link(item.url,'Read the HR internship programme')}</p><p class="input-note">Programme researched ${date(item.checked_at)}. Availability to confirm.</p></article>`).join('') || '<p>No programmes recorded yet.</p>';
  document.querySelector('#friesland-health').textContent = `For the ${report.summary.qualified_employers} employers with documented size: ${Object.entries(report.summary.qualified_collection_states).map(([state,count]) => `${count} ${labels[state] || state}`).join(' · ')}. Partial or blocked sources do not prove the absence of internships.`;
  document.querySelector('#friesland-municipalities').innerHTML = report.municipalities.map(m => `<tr><th scope="row">${escape(m.name)}</th><td>${m.qualified_employers}</td><td>${m.size_unknown}</td><td>${Object.entries(m.collection_states).map(([state,count]) => `${count} ${escape(labels[state] || state)}`).join('; ') || 'No employers researched yet'}</td></tr>`).join('');
  let employerLimit = 20;
  function renderEmployers() {
    const query = document.querySelector('#friesland-search').value.toLocaleLowerCase();
    const qualified = document.querySelector('#friesland-size').value === 'qualified';
    const rows = report.employers.filter(row => (!qualified || row.size.qualification === 'verified_50_plus') && [row.name,...row.workplaces.flatMap(place => [place.city, place.municipality])].join(' ').toLocaleLowerCase().includes(query));
    document.querySelector('#friesland-employer-count').textContent = `Showing ${Math.min(rows.length,employerLimit)} of ${rows.length} employers`;
    document.querySelector('#friesland-more').hidden = rows.length <= employerLimit;
    document.querySelector('#friesland-employers').innerHTML = rows.slice(0,employerLimit).map(row => `<article class="job-card employer-card"><h3>${escape(row.name)}</h3><p>${escape([...new Set(row.workplaces.map(place => place.city ? `${place.city} (${place.municipality})` : `${place.municipality} (town to confirm)`))].join(' · '))}</p><p>${escape(labels[row.state] || row.state)} · ${date(row.last_attempt_at)}</p><p>${link(row.career_url,'Official recruiting site')}</p><p class="input-note">${escape(sizeText(row))} ${row.size.source_url ? link(row.size.source_url,'Size evidence') : ''}</p>${row.errors.length ? `<details><summary>Collection issue</summary><p>${escape(row.errors.map(error => error.message).join('; '))}</p></details>` : ''}</article>`).join('') || '<p>No employers match these filters.</p>';
  }
  document.querySelector('#friesland-search').addEventListener('input',() => {employerLimit=20;renderEmployers();});
  document.querySelector('#friesland-size').addEventListener('change',() => {employerLimit=20;renderEmployers();});
  document.querySelector('#friesland-more').addEventListener('click',() => {employerLimit+=20;renderEmployers();});
  renderEmployers();
} catch (error) {
  document.querySelector('#friesland-summary').textContent = 'The local report could not be loaded. Please try again shortly.';
}
