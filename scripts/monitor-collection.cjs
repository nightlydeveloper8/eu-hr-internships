// Compare consecutive finalized cycles using the catalog's published status.
const HOUR = 60 * 60 * 1000;

function freshnessLine(updatedAt, now = Date.now()) {
  const age = (now - Date.parse(updatedAt)) / HOUR;
  if (!Number.isFinite(age)) return 'Catalog timestamp unavailable or invalid.';
  if (age > 36) return `Catalog age: ${age.toFixed(2)} hours (limit 36), updated ${updatedAt}.`;
  return null;
}

function collectionLines(before, after, previousCoverage, coverage) {
  const ids = new Set(after.jobs.map(job => job.id));
  const lost = new Set(before.jobs.filter(job => !ids.has(job.id)).map(job => job.id));
  const open = catalog => catalog.jobs.filter(job =>
    job.status === 'open' && job.internship_type === 'internship').length;
  const previousOpen = open(before);
  const currentOpen = open(after);
  const lines = [];
  if (lost.size) lines.push(`Lost catalog IDs: ${lost.size} (${before.jobs.length} → ${after.jobs.length} records).`);
  if ((previousOpen - currentOpen) * 100 > previousOpen * 15) {
    lines.push(`Open HR internships: ${previousOpen} → ${currentOpen} (drop greater than 15%).`);
  }

  // Coverage carries forward older reports for sources absent from this cycle.
  const previous = new Map(previousCoverage.sources.map(report => [report.id, report]));
  const current = coverage.sources.filter(report => {
    const checked = Date.parse(report.checked_at);
    return checked > Date.parse(previousCoverage.generated_at) &&
      checked <= Date.parse(coverage.generated_at);
  });
  const eures = current.find(report => report.id === 'public-eu-eures');
  if (eures?.status === 'failed') lines.push('EURES collection failed (result count unavailable).');
  else if (eures?.collected === 0) lines.push('EURES returned 0 postings.');

  const eligible = current.filter(report => {
    const prior = previous.get(report.id);
    const age = Date.parse(coverage.generated_at) - Date.parse(prior?.checked_at);
    return age >= 0 && age <= 48 * HOUR &&
      (prior.status === 'ok' || (prior.status === 'partial' &&
        (prior.records_inspected > 0 || prior.explicit_empty)));
  });
  const failed = eligible.filter(report => report.status === 'failed').length;
  if (failed * 100 > eligible.length * 20) {
    lines.push(`Recently successful sources failed: ${failed}/${eligible.length} (limit 20%).`);
  }
  return lines;
}

async function upsertAlert(github, context, title, lines, action) {
  if (!lines.length) return;
  const repo = context.repo;
  const run = `https://github.com/${repo.owner}/${repo.repo}/actions/runs/${context.runId}`;
  const body = [...lines, `[Workflow run](${run})`, `First action: ${action}`].join('\n');
  const issues = await github.paginate(github.rest.issues.listForRepo, {
    ...repo, state: 'open', creator: 'github-actions[bot]', per_page: 100
  });
  const existing = issues.find(issue => !issue.pull_request && issue.title === title);
  if (existing) {
    await github.rest.issues.update({...repo, issue_number: existing.number, body});
  } else {
    await github.rest.issues.create({...repo, title, body});
  }
}

module.exports = {freshnessLine, collectionLines, upsertAlert};
