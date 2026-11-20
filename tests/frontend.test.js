import test from 'node:test';
import assert from 'node:assert/strict';
import {completeRecentInventory,matches,rankJobs,stale,safeUrl,verifiedJob,applicationConfirmed,languageInfo,verificationMessage,opportunityCounts,provincialJobs,unverifiedFallback,shareableFilterParams,countryCounts,countBucket,countryLanguageCounts,languageBreakdown,NATIONAL_LANGUAGES} from '../src/logic.js';
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

test('opportunity counts separate archived, verified and opportunity types',()=>{
 const clock=Date.now();const jobs=[base,{...base,id:'2',status:'unverified'}, {...base,id:'3',status:'closed'}, {...base,id:'4',status:'unverified',internship_type:'working-student'}, {...base,id:'5',internship_type:'traineeship'}];
 assert.deepEqual(opportunityCounts(jobs,clock),{total:4,verified:2,applicationConfirmed:0,publicListings:0,unverified:2,verifiedInternships:1,verifiedWorkingStudents:0,verifiedTraineeships:1,closed:1,internships:2,workingStudents:1,traineeships:1});
 const selected=jobs.filter(j=>matches(j,{...f,unverified:true,country:'NL',type:'internship'}));
 assert.deepEqual(selected.map(j=>j.id),['1','2']);
 assert.equal(opportunityCounts(jobs,clock+49*60*60*1000).verified,0);
});
test('verification explanations are useful without exposing parser errors',()=>{
 assert.equal(verificationMessage({...base,status:'unverified',link_status:'review-required',review_note:'Published September intake needs confirmation.'}),'Published September intake needs confirmation.');
 assert.match(verificationMessage({...base,status:'unverified',verification:{state:'blocked'}}),/restricted/);
 assert.match(verificationMessage({...base,status:'unverified',link_status:'public-api-listed',verification:{state:'incomplete'}}),/official public employment service/);
 assert.match(verificationMessage({...base,status:'open',link_status:'public-api-active-listing',verification:{state:'verified',policy_version:2},last_verified_at:new Date(Date.now()-3600e3).toISOString()}),/Listed as open by an official public employment service/);
 assert.match(verificationMessage({...base,status:'unverified',verification:{reason:'Request budget exhausted'}}),/could not finish/);
 assert.match(verificationMessage({...base,status:'unverified',verification:{reason:'Invalid application deadline'}}),/closing date/);
 const text=verificationMessage({...base,status:'unverified',verification:{reason:'TypeError: sequence item expected str instance, NoneType found'}});
 assert.match(text,/may still be open/);assert.doesNotMatch(text,/TypeError|NoneType|sequence/);
 assert.match(verificationMessage({...base,last_verified_at:'2020-01-01T00:00:00Z'}),/more than 48 hours/);
 assert.match(verificationMessage(base),/listing is current/);
});

test('province jobs require workplace region and separate unverified internships',()=>{
  const report={region_code:'NL35',verified_hr_internship_ids:['1']};
  const local={...base,region_codes:['NL35']};
  const candidate={...local,id:'candidate',verification:{state:'unverified'},status:'unverified'};
  const otherProvince={...local,id:'elsewhere',region_codes:['NL13']};
  const programme={...candidate,id:'programme',internship_type:'traineeship'};
  const closed={...candidate,id:'closed',status:'closed'};
  const rows=[local,candidate,otherProvince,programme,closed];
  assert.deepEqual(provincialJobs(rows,report).map(j=>j.id),['1']);
  assert.deepEqual(provincialJobs(rows,report,{unverified:true}).map(j=>j.id),['1','candidate']);
  assert.equal(provincialJobs(rows,report,{unverified:true,ad:'nl'}).length,0);
  assert.deepEqual(provincialJobs(rows,report,{q:'Example'}).map(j=>j.id),['1']);
});

test('English advertisement alone proves neither workplace English nor sufficiency',()=>{
 const job={...base,advertisement_language:{code:'en',confidence:'confirmed'},workplace_languages:[],language_requirements:undefined};
 assert.equal(languageInfo(job).english_support,'unknown');
 assert.equal(languageInfo(job).english_sufficiency,'unknown');
 assert.equal(matches(job,{...f,english:true}),false);
 assert.equal(matches(job,{...f,englishOnly:true}),false);
 assert.ok(matches(job,f));
});
test('complete recent employer inventories differ from configured collection',()=>{
 const clock=Date.parse('2026-11-07T12:00:00Z');
 const company={source_ids:['board']},sources=[{id:'board',enabled:true}];
 const report={id:'board',status:'ok',complete:true,checked_at:'2026-11-07T10:00:00Z'};
 assert.ok(completeRecentInventory(company,sources,[report],clock));
 for(const change of [{status:'partial'},{complete:false},{checked_at:'2026-11-01T10:00:00Z'},{checked_at:'2026-11-08T10:00:00Z'}]){
  assert.equal(completeRecentInventory(company,sources,[{...report,...change}],clock),false);
 }
 assert.equal(completeRecentInventory(company,sources,[],clock),false);
 assert.equal(completeRecentInventory(company,[{id:'board',enabled:false}],[report],clock),false);
});

test('verified internship and working-student KPI subsets exclude stale and unverified roles',()=>{
 const clock=Date.now(), working={...base,id:'ws',internship_type:'working-student'};
 const jobs=[base,working,{...working,id:'unknown',status:'unverified'},{...working,id:'stale',last_verified_at:'2020-01-01T00:00:00Z'}];
 const counts=opportunityCounts(jobs,clock);
 assert.equal(counts.verifiedInternships,1);assert.equal(counts.verifiedWorkingStudents,1);
 assert.equal(counts.unverified,2);assert.equal(counts.workingStudents,3);

});

test('stale catalog shows archived leads as unverified without relaxing the 48-hour rule',()=>{
  const clock=Date.parse('2026-11-12T15:23:00Z');
  const expired={...base,id:'archive',last_verified_at:'2026-11-10T07:18:54Z'};
  const catalog={updated_at:'2026-11-10T07:28:10Z',jobs:[expired]};
  assert.equal(verifiedJob(expired,clock),false);
  assert.equal(unverifiedFallback(catalog,clock),true);
  assert.equal(unverifiedFallback({...catalog,updated_at:'2026-11-12T14:00:00Z'},clock),false);
  assert.equal(unverifiedFallback({...catalog,jobs:[{...expired,last_verified_at:'2026-11-12T14:00:00Z'}]},clock),false);
  assert.equal(unverifiedFallback({...catalog,jobs:[{...expired,status:'closed'}]},clock),false);
  assert.equal(unverifiedFallback({...catalog,jobs:[]},clock),false);
});

test('verified-only is default, even when an expired catalog has unverified leads',()=>{
  const clock=Date.parse('2026-11-12T19:49:00Z');
  const expired={...base,last_verified_at:'2026-11-10T07:18:54Z'};
  assert.equal(verifiedJob(expired,clock),false);
  assert.equal(matches(expired,f),false);
  assert.equal(matches(expired,{...f,unverified:true}),true);
  assert.equal(shareableFilterParams({...f,unverified:true},f).toString(),'');
  assert.equal(shareableFilterParams({...f,unverified:true,q:'recruitment'},f).toString(),'q=recruitment');
  assert.equal(shareableFilterParams({...f,unverified:false,country:'NL'},f).get('country'),'NL');
});

test('monitor counts verified HR internships only with current policy v2 and 48h evidence',()=>{
  const clock=Date.parse('2026-11-12T19:49:00Z');
  const fresh={...base,last_verified_at:'2026-11-12T18:00:00Z'};
  const stale={...base,id:'old',last_verified_at:'2026-11-10T07:00:00Z'};
  const unverified={...base,id:'uncertain',status:'unverified'};
  const closed={...base,id:'closed',status:'closed'};
  const wrongPolicy={...base,id:'old-policy',verification:{state:'verified',policy_version:1}};
  const working={...fresh,id:'working',internship_type:'working-student'};
  assert.equal(opportunityCounts([stale,unverified,closed,wrongPolicy,working],clock).verifiedInternships,0);
  assert.equal(opportunityCounts([fresh,stale,unverified,closed,wrongPolicy,working],clock).verifiedInternships,1);
  assert.equal(opportunityCounts([fresh,stale,unverified,closed,wrongPolicy,working],clock+49*60*60*1000).verifiedInternships,0);
});

test('historical external publisher records stay in JSON but never display as official leads',()=>{
 const mirrored={...base,id:'historical-referral',status:'unverified',
     source_id:'auto-tilburg-university',url:'https://www.nationalevacaturebank.nl/vacature/123',
     ownership_risk:{state:'historical-unreviewed-external-host',
                     original_source_id:'auto-tilburg-university',observed_host:'www.nationalevacaturebank.nl'}};
 assert.equal(matches(mirrored,{...f,unverified:true}),false);
 assert.equal(matches(mirrored,f),false);
 const counts=opportunityCounts([base,mirrored],Date.now());
 assert.equal(counts.total,1);
 assert.equal(counts.verifiedInternships,1);
 assert.equal(counts.unverified,0);
 assert.equal(counts.closed,0);
 const clock=Date.parse('2026-11-16T20:00:00Z');
 const staleCatalog={updated_at:'2026-11-12T00:00:00Z',jobs:[mirrored]};
 assert.equal(unverifiedFallback(staleCatalog,clock),false);
 assert.equal(unverifiedFallback({...staleCatalog,jobs:[mirrored,{...mirrored,id:'valid-lead',ownership_risk:undefined}]},clock),true);
});

test('map country counts separate verified and unverified, skip closed, count each listed country',()=>{
 const clock=Date.now();
 const jobs=[base,{...base,id:'2',countries:['NL','DE'],status:'unverified'},{...base,id:'3',status:'closed'},{...base,id:'4',countries:['FR'],ownership_risk:{state:'historical-unreviewed-external-host'}}];
 const counts=countryCounts(jobs,clock);
 assert.deepEqual(counts.NL,{verified:1,unverified:1,applicationConfirmed:0});
 assert.deepEqual(counts.DE,{verified:0,unverified:1,applicationConfirmed:0});
 assert.equal(counts.FR,undefined);
});
test('map colour buckets',()=>{assert.deepEqual([0,1,2,4,5,9,10,24,25,90].map(countBucket),[0,1,2,2,3,3,4,4,5,5]);});
test('country language counts: verified ads only, English and local languages first',()=>{
 const clock=Date.now();
 const jobs=[{...base,id:'a',countries:['IT'],advertisement_language:{code:'it'}},{...base,id:'b',countries:['IT'],advertisement_language:{code:'it'}},
  {...base,id:'c',countries:['IT'],advertisement_language:{code:'en'}},{...base,id:'d',countries:['IT'],advertisement_language:{code:'de'}},
  {...base,id:'e',countries:['IT'],advertisement_language:{code:null}},{...base,id:'f',countries:['IT'],status:'unverified',advertisement_language:{code:'it'}}];
 const byLang=countryLanguageCounts(jobs,clock);
 assert.deepEqual(byLang.IT,{it:2,en:1,de:1,unknown:1});
 assert.deepEqual(languageBreakdown('IT',byLang.IT).map(x=>[x.code,x.kind]),[['en','english'],['it','local'],['de','other'],['unknown','unknown']]);
 assert.equal(languageBreakdown('IE',{en:2})[0].kind,'english');
 assert.equal(NATIONAL_LANGUAGES.CH.includes('it'),true);
});

test('application filter and counts distinguish current public listings from application evidence',()=>{
  const confirmed={...base,application_verification:{method:'same-vacancy-applicant-form',url:'https://jobs.example.com/jobs/1/apply'}};
  const publicListing={...base,id:'public',link_status:'public-api-active-listing'};
  const publicWithConflictingEvidence={...confirmed,id:'conflict',verification:{...base.verification,policy:'public-api-active-listing'}};
  const lead={...confirmed,id:'lead',status:'unverified'};
  const invalidUrl={...confirmed,id:'invalid',application_verification:{...confirmed.application_verification,url:'javascript:alert(1)'}};
  const quarantined={...confirmed,id:'quarantined',ownership_risk:{state:'historical-unreviewed-external-host'}};
  const records=[confirmed,publicListing,publicWithConflictingEvidence,lead,invalidUrl,quarantined];
  const filter={...f,applicationConfirmed:true};
  assert.deepEqual(records.filter(j=>matches(j,filter)).map(j=>j.id),['1']);
  assert.equal(matches(publicListing,f),true);
  assert.equal(matches(lead,{...f,unverified:true}),true);
  assert.equal(matches(lead,{...filter,unverified:true}),false);
  assert.equal(applicationConfirmed({...confirmed,last_verified_at:'2020-01-01T00:00:00Z'}),false);
  assert.equal(opportunityCounts(records).applicationConfirmed,1);
  assert.equal(opportunityCounts(records).publicListings,2);
  assert.equal(countryCounts(records).NL.applicationConfirmed,1);
  assert.match(verificationMessage(confirmed),/application route were confirmed/);
  assert.match(verificationMessage(publicWithConflictingEvidence),/official public employment service/);
  assert.doesNotMatch(verificationMessage(invalidUrl),/route were confirmed/);
  assert.equal(shareableFilterParams({...f,applicationConfirmed:true},f).get('applicationConfirmed'),'true');
});
