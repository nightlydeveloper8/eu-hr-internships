module.exports = async function updateDiscoveryIssue({github, context}) {
  const fs = require('node:fs');
  const path = require('node:path');
  const reportPath = path.join(process.env.RUNNER_TEMP, 'discovery', 'reports.json');
  const scanEvent = context.eventName !== 'workflow_run';
  if (!fs.existsSync(reportPath) && !scanEvent) return;
  const date = new Date(new Date().toLocaleDateString('en-CA', {timeZone: 'Europe/Amsterdam'}) + 'T00:00:00Z');
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
  const isoWeek = Math.ceil(((date - Date.UTC(date.getUTCFullYear(), 0, 1)) / 86400000 + 1) / 7);
  const weekKey = `${date.getUTCFullYear()}-W${String(isoWeek).padStart(2, '0')}`;
  const reports = fs.existsSync(reportPath) ? JSON.parse(fs.readFileSync(reportPath)) :
    {[weekKey]: {funnel: 'Imbuto non disponibile: consolidamento della scoperta interrotto.', hold: ''}};
  for (const [week, report] of Object.entries(reports)) {
    const title = `Scoperta fonti – settimana ${Number(week.slice(-2))}`;
    const marker = `<!-- discovery:${week} -->`;
    const existing = await github.paginate(github.rest.issues.listForRepo, {
      ...context.repo, state: 'all', creator: 'github-actions[bot]', per_page: 100
    });
    const issue = existing.find(item => item.body?.startsWith(marker));
    if (issue && report.ran === false && issue.body?.includes('### Stage aggiunti per paese')) continue;
    if (!issue && report.hold === undefined && !report.activation.includes(' — Rientro:')) continue;
    function section(name, value, limit) {
      if (value === undefined) {
        return issue?.body?.split(`<!-- ${name}:start -->\n`)[1]
          ?.split(`\n<!-- ${name}:end -->`)[0] ?? '';
      }
      return value.length <= limit ? value :
        value.slice(0, limit) + `\n\n[Elenco completo nell’artefatto della scoperta](${run}).`;
    }
    const run = `https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`;
    const scan = report.hold === undefined ? '' : `\n\n[Scoperta e artefatto](${run})`;
    const failed = process.env.PUBLISH_OUTCOME !== 'success';
    const baseline = '[Imbuto storico del primo run](https://github.com/' +
      context.repo.owner + '/' + context.repo.repo + '/blob/main/docs/staging/discovery-funnel-20261126.md)';
    const activation = failed && report.activation !== undefined
      ? report.activation.replace('Fonti attivate automaticamente', 'Attivazioni o rientri proposti')
        + '\n\nSalvataggio non riuscito. Verificare il log del run.'
      : report.activation;
    const body = [
      marker,
      `<!-- funnel:start -->\n${section('funnel', report.funnel === undefined ? undefined : report.funnel + '\n\n' + baseline, 6000)}\n<!-- funnel:end -->`,
      `<!-- activation:start -->\n${section('activation', activation, 8000)}\n<!-- activation:end -->`,
      `<!-- hold:start -->\n${section('hold', report.hold === undefined ? undefined : '### Fonti in attesa di decisione' + report.hold + scan, 41000)}\n<!-- hold:end -->`,
      `<!-- collection:start -->\n${section('collection', report.collection === undefined ? undefined : '### Stage aggiunti per paese' + report.collection, 5000)}\n<!-- collection:end -->`,
    ].join('\n\n');
    if (!issue) await github.rest.issues.create({...context.repo, title, body});
    else if (issue.body !== body) {
      await github.rest.issues.update({...context.repo, issue_number: issue.number, body});
    }
  }
};
