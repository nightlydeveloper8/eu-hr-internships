import test from 'node:test';
import assert from 'node:assert/strict';
import {matches,rankJobs,stale,safeUrl,verifiedJob,languageInfo} from '../src/logic.js';
const base={id:'1',title:'Talent Acquisition Intern',employer:'Example',city:'Amsterdam',countries:['NL'],categories:['talent-acquisition'],workplace_languages:[{code:'en',confidence:'confirmed',requirement:'required-or-working'},{code:'nl',confidence:'confirmed',requirement:'required-or-working'}],advertisement_language:{code:'en'},internship_type:'internship',work_mode:'hybrid',status:'open',verification:{state:'verified',policy_version:2},last_verified_at:new Date().toISOString(),published_at:'2026-10-20T12:00:00Z',first_discovered_at:'2026-11-01T00:00:00Z'};
const f={q:'',country:'',category:'',workplace:'',english:false,ad:'',type:'',workMode:'',unverified:false,saved:false,mode:'nl',sort:'relevance'};
test('all independent filters compose',()=>{assert.ok(matches(base,{...f,q:'talent Amsterdam',country:'NL',category:'talent-acquisition',workplace:'nl',english:true,ad:'en',type:'internship',workMode:'hybrid'}));assert.equal(matches(base,{...f,country:'MT'}),false);assert.equal(matches(base,{...f,q:'payroll'}),false);});
test('English ad alone never matches English workplace filter',()=>{assert.equal(matches({...base,workplace_languages:[]},{...f,english:true}),false);});
test('closed always hidden and unverified optional',()=>{assert.equal(matches({...base,status:'closed'},{...f,unverified:true}),false);assert.equal(matches({...base,status:'unverified'},f),false);assert.ok(matches({...base,status:'unverified'},{...f,unverified:true}));});
test('saved jobs filter uses local IDs',()=>{assert.ok(matches(base,{...f,saved:true},new Set(['1'])));assert.equal(matches(base,{...f,saved:true}),false);});
test('Netherlands priority is independent from country filtering',()=>{const newer={...base,id:'2',countries:['FR'],published_at:'2026-11-02'};assert.equal(rankJobs([newer,base],f)[0].id,'1');assert.equal(rankJobs([newer,base],{...f,mode:'eu',sort:'recent'})[0].id,'2');assert.ok(matches(newer,f));});
test('keyword relevance ranks title matches',()=>{const other={...base,id:'2',title:'HR Intern',city:'Talent City'};assert.equal(rankJobs([other,base],{...f,q:'talent'})[0].id,'1');});
test('accent-insensitive keyword search',()=>{assert.ok(matches({...base,title:'Stage Chargé de Recrutement'},{...f,q:'charge recrutement'}));});
test('all multi-country locations match independently',()=>{assert.ok(matches({...base,countries:['FR','NL']},{...f,country:'FR'}));});
test('unknown dates sort after known recency',()=>{assert.equal(rankJobs([{...base,id:'2',published_at:null},base],{...f,sort:'recent'})[0].id,'1');});
test('stale and malformed timestamps warn',()=>{const clock=Date.parse('2026-11-05T12:00:00Z');assert.ok(stale('2026-11-01',clock));assert.ok(stale(null,clock));assert.ok(stale('invalid',clock));assert.equal(stale('2026-11-05T10:00:00Z',clock),false);});
test('unsafe link protocols rejected',()=>{assert.equal(safeUrl('javascript:alert(1)'),null);assert.equal(safeUrl('http://example.com'),null);assert.equal(safeUrl('https://a:b@example.com'),null);assert.equal(safeUrl('https://jobs.lever.co/a/1'),'https://jobs.lever.co/a/1');});

test('regional filters require an explicitly mapped region',()=>{assert.ok(matches({...base,region_codes:['NL35']},{...f,region:'NL35'}));assert.equal(matches(base,{...f,region:'NL35'}),false);assert.equal(matches({...base,region_codes:['NL35']},{...f,region:'NL32'}),false);});

test('unknown language requirements remain discoverable',()=>{
 const unknown={...base,workplace_languages:[]};
 assert.ok(matches(unknown,{...f,workplace:'unknown'}));
 assert.equal(matches(base,{...f,workplace:'unknown'}),false);
 assert.ok(matches(unknown,f));
});
test('preferred English does not prove work support; alternatives are explicit choices',()=>{
 for(const requirement of ['preferred','alternative']){
  const job={...base,workplace_languages:[{code:'en',confidence:'confirmed',requirement}]};
  assert.equal(matches(job,{...f,english:true}),requirement==='alternative');
  assert.equal(matches(job,{...f,workplace:'en'}),false);
 }
 assert.equal(matches(base,{...f,englishOnly:true}),false);
 assert.ok(matches({...base,language_requirements:{english_sufficiency:'documented'}},{...f,englishOnly:true}));
});
test('legacy, future and stale verification never appears as verified',()=>{
 const clock=Date.parse('2026-11-06T12:00:00Z');
 assert.equal(verifiedJob({...base,verification:undefined},clock),false);
 assert.equal(verifiedJob({...base,last_verified_at:'2026-11-07T00:00:00Z'},clock),false);
 assert.equal(verifiedJob({...base,last_verified_at:'2026-11-01T00:00:00Z'},clock),false);
 assert.ok(verifiedJob({...base,last_verified_at:'2026-11-06T10:00:00Z'},clock));
 assert.equal(matches({...base,verification:undefined},f),false);
 assert.ok(matches({...base,verification:undefined},{...f,unverified:true}));
});
