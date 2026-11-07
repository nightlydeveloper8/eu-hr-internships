import json
from pathlib import Path
import unittest
from collector.company_registry import country_research_progress,discovery_queue
from collector.classify import COUNTRIES

ROOT=Path(__file__).resolve().parents[1]
class CountryPlanTests(unittest.TestCase):
 def test_all_countries_have_hundreds_as_target_and_local_queries(self):
  plan=json.loads((ROOT/'data/employer-research-plan.json').read_text())
  self.assertEqual({c['code'] for c in plan['countries']},set(COUNTRIES))
  self.assertEqual(len(plan['countries']),27)
  self.assertTrue(all(c['baseline_target']==100 and c['expansion_target']>=500 and len(c['research_terms'])>=2 for c in plan['countries']))
  self.assertEqual(sum(c['baseline_target'] for c in plan['countries']),2700)
 def test_candidates_and_duplicate_offices_do_not_inflate_confirmed_count(self):
  plan={'countries':[dict(code='IT',name='Italy',baseline_target=300,expansion_target=1500)]}
  companies=[dict(id='candidate',target_countries=['IT'],workplaces=[]),dict(id='located',target_countries=['IT'],workplaces=[dict(country='IT',location_confidence='confirmed'),dict(country='IT',location_confidence='confirmed')])]
  row=country_research_progress(companies,[],plan)[0]
  self.assertEqual(row['companies_identified'],2)
  self.assertEqual(row['companies_located'],1)
  self.assertEqual(row['baseline_gap'],300)
  self.assertEqual(row['size_unknown'],2)
 def test_country_gap_beats_fixed_netherlands_preference(self):
  geography={'units':[dict(code='NL1',country='NL',level=2,name='Dutch'),dict(code='IT1',country='IT',level=2,name='Italian')]}
  report={'countries':[dict(code='NL',companies_located=100,companies_monitored_in_country=5),dict(code='IT',companies_located=0)],'regions':[dict(code='NL1',companies_located=0),dict(code='IT1',companies_located=0)]}
  self.assertEqual(discovery_queue(geography,report)[0]['country'],'IT')
 def test_expansion_gap_used_after_country_baseline(self):
  geography={'units':[dict(code='NL1',country='NL',level=2,name='Dutch'),dict(code='IT1',country='IT',level=2,name='Italian')]}
  report={'countries':[dict(code='NL',companies_located=300,companies_monitored_in_country=300,expansion_target=800),dict(code='IT',companies_located=300,companies_monitored_in_country=300,expansion_target=1500)],'regions':[dict(code='NL1',companies_located=300),dict(code='IT1',companies_located=300)]}
  queue=discovery_queue(geography,report)
  self.assertEqual(queue[0]['country'],'IT');self.assertEqual(queue[0]['country_active_target'],1500)
if __name__=='__main__':unittest.main()

class OperationalCountryCoverageTests(unittest.TestCase):
 def test_only_recent_successful_actual_country_inventory_counts(self):
  plan={'collection_freshness_hours':48,'countries':[dict(code='IT',name='Italy',baseline_target=100,expansion_target=500)]}
  company=dict(id='a',target_countries=['DE'],source_ids=['board'],workplaces=[])
  sources=[dict(id='board',enabled=True)]
  report=dict(id='board',status='ok',checked_at='2026-11-05T10:00:00+00:00',observed_countries=['IT'])
  stamp='2026-11-05T12:00:00+00:00'
  row=country_research_progress([company],sources,plan,[report],stamp)[0]
  self.assertEqual(row['companies_monitored_in_country'],1);self.assertEqual(row['baseline_gap'],99)
  for change in [dict(complete=False),dict(checked_at='2026-11-06T10:00:00+00:00'),dict(status='partial'),dict(checked_at='2026-10-01T10:00:00+00:00'),dict(observed_countries=['DE'])]:
   row=country_research_progress([company],sources,plan,[dict(report,**change)],stamp)[0]
   self.assertEqual(row['companies_monitored_in_country'],0)
 def test_configured_without_run_does_not_satisfy_target(self):
  plan={'countries':[dict(code='IT',name='Italy',baseline_target=100,expansion_target=500)]}
  row=country_research_progress([dict(id='a',target_countries=['IT'],source_ids=['board'],workplaces=[])],[dict(id='board',enabled=True)],plan)[0]
  self.assertEqual(row['baseline_gap'],100)
