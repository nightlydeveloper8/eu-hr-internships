import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const index = readFileSync(new URL('../src/index.html', import.meta.url), 'utf8');
const app = readFileSync(new URL('../src/app.js', import.meta.url), 'utf8');
const sourceList = readFileSync(new URL('../data/sources.json', import.meta.url), 'utf8');

test('EURES is a clearly separated outbound search, not a claimed verified vacancy', () => {
  const section = index.match(/<aside class="external-discovery"[\s\S]*?<\/aside>/)?.[0];
  assert.ok(section, 'Dedicated, user-visible EURES search panel must exist');
  assert.match(section, /href="https:\/\/europa\.eu\/eures\/portal\/jv-se\/home\?lang=en"/);
  assert.match(section, /target="_blank" rel="noopener noreferrer external"/);
  assert.match(section, /People Placement filters do not transfer/);
  assert.match(section, /have not been verified by our policy-v2 checks/);
  assert.doesNotMatch(section, /<article|class="job-card"|Verified opportunities/);
});

test('EURES is not integrated as an ingestion endpoint or a catalog/source registry input', () => {
  assert.doesNotMatch(app, /fetch\([^\n]*eures|eures.*\.json/i);
  assert.doesNotMatch(sourceList, /"adapter"\s*:\s*"eures"|api\.eures\.|europa\.eu\/eures\/api/i);
});
