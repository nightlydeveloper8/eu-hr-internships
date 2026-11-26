import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import updateIssue from '../scripts/discovery-issue.cjs';

const workflow = fs.readFileSync('.github/workflows/discovery.yml', 'utf8');

test('discovery serializes publication with collect and uploads before committing', () => {
  for (const file of ['collect', 'discovery']) {
    const contents = fs.readFileSync(`.github/workflows/${file}.yml`, 'utf8');
    assert.match(contents, /concurrency:\n  group: employer-catalog\n  cancel-in-progress: false/);
  }
  assert.match(workflow, /Update the weekly issue\n        if: always\(\) && !cancelled\(\)/);
  assert.ok(workflow.indexOf('Retain the per-host observations') <
            workflow.indexOf('Save the reviewed activation or rollback'));
});

test('publication rebases before each retry and stops at three pushes', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'discovery-git-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const log = path.join(dir, 'calls');
  fs.writeFileSync(path.join(dir, 'git'), `#!/bin/bash
echo "$*" >> "$TEST_GIT_LOG"
if [ "$1" = push ]; then
  test "$(grep -c '^push ' "$TEST_GIT_LOG")" -ge "$TEST_SUCCESS_AT"
fi
`, {mode: 0o755});
  for (const successAt of [2, 4]) {
    fs.writeFileSync(log, '');
    const result = spawnSync('bash', ['scripts/publish-discovery.sh'], {
      env: {...process.env, PATH: dir + ':' + process.env.PATH,
            TEST_GIT_LOG: log, TEST_SUCCESS_AT: String(successAt)}
    });
    assert.equal(result.status, successAt === 2 ? 0 : 1);
    const calls = fs.readFileSync(log, 'utf8').trim().split('\n');
    assert.deepEqual(calls, Array.from({length: Math.min(successAt, 3)},
      () => ['pull --rebase origin main', 'push origin HEAD:main']).flat());
  }
});

test('a failed push still creates one weekly issue and labels proposals honestly', async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'discovery-issue-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  fs.mkdirSync(path.join(dir, 'discovery'));
  fs.writeFileSync(path.join(dir, 'discovery/reports.json'), JSON.stringify({
    '2026-W48': {activation: '### Fonti attivate automaticamente\n- Girteka', funnel: 'Imbuto', hold: ''}
  }));
  const issues = [];
  const github = {paginate: async () => issues, rest: {issues: {
    listForRepo: {},
    create: async (issue) => issues.push({...issue, number: 1}),
    update: async () => assert.fail('identical updates should be skipped')
  }}};
  const context = {repo: {owner: 'test', repo: 'test'}, eventName: 'workflow_dispatch', runId: 1};
  const previous = {RUNNER_TEMP: process.env.RUNNER_TEMP, PUBLISH_OUTCOME: process.env.PUBLISH_OUTCOME};
  process.env.RUNNER_TEMP = dir;
  process.env.PUBLISH_OUTCOME = 'failure';
  t.after(() => {
    for (const [key, value] of Object.entries(previous)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  });
  await updateIssue({github, context});
  await updateIssue({github, context});
  assert.equal(issues.length, 1);
  assert.equal(issues[0].title, 'Scoperta fonti – settimana 48');
  assert.match(issues[0].body, /Imbuto[\s\S]+Attivazioni o rientri proposti[\s\S]+Salvataggio non riuscito/);
});
