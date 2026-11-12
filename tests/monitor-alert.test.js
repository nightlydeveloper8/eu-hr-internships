// Exercise the actual GitHub Actions github-script bodies against in-memory Issues.
// Never contacts GitHub APIs, changes the production catalog, or triggers collection.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {dirname, resolve} from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const nodeRequire = createRequire(import.meta.url);
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
const alertTitle = '[monitor] Zero currently verified HR internships';
const sources = [
  '.github/workflows/stale.yml',
  '.github/workflows/collect.yml'
];

function workflowScript(path) {
  const source = readFileSync(resolve(root, path), 'utf8');
  const marker = '          script: |';
  const start = source.lastIndexOf(marker);
  assert.ok(start >= 0, 'Missing github-script step: ' + path);
  const lines = source.slice(start + marker.length).split(/\r?\n/);
  const result = [];
  for (const line of lines) {
    if (line.trim() && !line.startsWith('            ')) break;
    result.push(line.startsWith('            ') ? line.slice(12) : '');
  }
  const script = result.join('\n');
  assert.match(script, /Zero currently verified HR internships/);
  return script;
}

function catalog(jobs) {
  return {updated_at: new Date().toISOString(), jobs};
}

function fixtureRecords() {
  const now = Date.now();
  const verified = (id, type = 'internship') => ({
    id, status: 'open', internship_type: type,
    verification: {state: 'verified', policy_version: 2},
    last_verified_at: new Date(now - 60_000).toISOString()
  });
  return {
    fresh: verified('fresh'),
    working: verified('working', 'working-student'),
    expired: {
      ...verified('expired'),
      last_verified_at: new Date(now - 49 * 60 * 60_000).toISOString()
    },
    wrongPolicy: {
      ...verified('old-policy'),
      verification: {state: 'verified', policy_version: 1}
    },
    closed: {...verified('closed'), status: 'closed'},
    unverified: {...verified('pending'), status: 'unverified'}
  };
}

function harness(path) {
  const script = workflowScript(path);
  // Executes the unmodified workflow script, including the real ES-module import.
  const execute = new AsyncFunction('require', 'github', 'context', 'core', 'process', script);
  let issues = [];
  let nextNumber = 1000;
  let currentCatalog = catalog([]);
  const calls = [];
  const issuesApi = {
    listForRepo: async ({state, creator}) => {
      assert.equal(state, 'open');
      assert.equal(creator, 'github-actions[bot]');
      return {data: issues.filter(i => i.state === 'open' && i.user.login === creator)};
    },
    create: async ({title, body}) => {
      const issue = {
        number: nextNumber++, title, body, state: 'open',
        user: {login: 'github-actions[bot]'}
      };
      issues.push(issue);
      calls.push({action: 'create', title, number: issue.number});
      return {data: issue};
    },
    update: async ({issue_number, body, state}) => {
      const issue = issues.find(i => i.number === issue_number);
      assert.ok(issue, 'Cannot update nonexistent Issue');
      if (body !== undefined) issue.body = body;
      if (state !== undefined) issue.state = state;
      calls.push({
        action: state === 'closed' ? 'close' : 'update',
        title: issue.title, number: issue.number
      });
      return {data: issue};
    }
  };
  const github = {rest: {issues: issuesApi}};
  const context = {repo: {owner: 'nightlydeveloper8', repo: 'eu-hr-internships'}, runId: 1234};
  const core = {summary: {
    addHeading() {return this;},
    addRaw() {return this;},
    write() {return Promise.resolve();}
  }};
  const requireMock = spec => {
    if (spec !== 'fs') return nodeRequire(spec);
    return {readFileSync: file => {
      if (file === 'data/catalog.json') return JSON.stringify(currentCatalog);
      if (file === 'data/employer-collection.json') return JSON.stringify({summary: {}});
      throw Error('Unexpected file read: ' + file);
    }};
  };
  return {
    async run(nextCatalog) {
      currentCatalog = nextCatalog;
      const from = calls.length;
      await execute(requireMock, github, context, core, {env: {JOB_STATUS: 'success'}});
      return calls.slice(from).filter(x => x.title === alertTitle);
    },
    alerts() {return issues.filter(x => x.title === alertTitle);},
    openAlerts() {return issues.filter(x => x.title === alertTitle && x.state === 'open');}
  };
}

for (const path of sources) {
  test('Alert lifecycle is idempotent in ' + path, async () => {
    const h = harness(path);
    const rows = fixtureRecords();
    // All these records must be excluded from verified HR internships.
    const zero = catalog([
      rows.working, rows.expired, rows.wrongPolicy, rows.closed, rows.unverified
    ]);
    const created = await h.run(zero);
    assert.deepEqual(created.map(x => x.action), ['create']);
    assert.match(h.openAlerts()[0].body, /Verified HR internships: 0/);
    assert.equal(h.openAlerts().length, 1);

    const repeated = await h.run(zero);
    assert.deepEqual(repeated.map(x => x.action), ['update']);
    assert.equal(repeated[0].number, created[0].number);
    assert.equal(h.alerts().length, 1);

    const recovered = catalog([...zero.jobs, rows.fresh]);
    const closed = await h.run(recovered);
    assert.deepEqual(closed.map(x => x.action), ['close']);
    assert.equal(closed[0].number, created[0].number);
    assert.equal(h.openAlerts().length, 0);

    const stable = await h.run(recovered);
    assert.deepEqual(stable, []);
    assert.equal(h.openAlerts().length, 0);

    // A new outage after recovery must be reported again, never hidden.
    const relapse = await h.run(zero);
    assert.deepEqual(relapse.map(x => x.action), ['create']);
    assert.equal(h.openAlerts().length, 1);
    assert.equal(h.alerts().length, 2); // Historical closed issue retained.
  });
}
