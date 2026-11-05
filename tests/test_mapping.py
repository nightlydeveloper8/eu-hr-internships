import unittest
from scripts.map_employers import directory_rows
from collector.company_registry import validate_registry,discover_channels

class MappingTests(unittest.TestCase):
 def test_ikom_only_extracts_company_provenance(self):
  body='{id:"abc",fair_id:"fair",name:"Example GmbH",booth_number:"1",website_url:"https://example.org/",emails:["private@example.org"]}'
  self.assertEqual(list(directory_rows('ikom',body)),[('Example GmbH','https://example.org/','https://ikom-tum.de/de/messen/ikom/2026/aussteller/abc')])
 def test_candidate_can_have_website_without_fake_career_page(self):
  company=dict(id='example',name='Example',website_url='https://example.org/',career_url=None,evidence_url='https://university.example/fair',workplaces=[],source_ids=[])
  self.assertTrue(validate_registry([company],{'units':[]},[]))
  self.assertEqual(discover_channels(company,None),[])
 def test_missing_company_links_rejected(self):
  with self.assertRaises(ValueError):validate_registry([dict(id='empty',career_url=None)],{'units':[]},[])
if __name__=='__main__':unittest.main()

class IdentityTests(unittest.TestCase):
 def test_group_merge_preserves_channels_aliases_and_is_idempotent(self):
  from scripts.consolidate_employers import consolidate
  rows=[dict(id='parent',name='Parent',career_url='https://parent.example/jobs',target_countries=['DE'],source_ids=['source-a'],workplaces=[],review_status='monitoring'),dict(id='brand',name='Brand',career_url='https://brand.example/jobs',target_countries=['NL'],source_ids=[],workplaces=[],review_status='research-required')]
  rules=[dict(id='parent',name='Parent',members=['parent','brand'],evidence_url='https://parent.example/group')]
  merged=consolidate(rows,rules)
  self.assertEqual(len(merged),1)
  self.assertEqual(merged[0]['aliases'],['Brand'])
  self.assertEqual(merged[0]['source_ids'],['source-a'])
  self.assertEqual(merged[0]['target_countries'],['DE','NL'])
  self.assertEqual(consolidate(merged,rules),merged)
