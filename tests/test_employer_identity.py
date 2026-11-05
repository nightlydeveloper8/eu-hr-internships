import json,unittest
from collector.employer_identity import organisation_evidence
class IdentityMetadataTests(unittest.TestCase):
 def body(self,**kwargs):
  obj=dict({'@type':'Organization','url':'https://company.example/','address':dict(addressLocality='Padova',addressRegion='PD',addressCountry='Italia')},**kwargs)
  return ('<script type="application/ld+json">'+json.dumps(obj)+'</script>').encode()
 def test_official_explicit_address_confirms_country_and_reviewed_region(self):
  p=organisation_evidence(self.body(),'https://company.example','2026-11-05')[0]
  self.assertEqual((p['country'],p['region_code'],p['city']),('IT','ITH3','Padova'))
 def test_third_party_organisation_is_not_employer_workplace(self):
  self.assertEqual(organisation_evidence(self.body(),'https://different.example','2026-11-05'),[])
 def test_country_and_city_are_required_not_inferred_from_domain(self):
  for address in [dict(addressLocality='Padova'),dict(addressCountry='IT')]:
   self.assertEqual(organisation_evidence(self.body(address=address),'https://company.example','2026-11-05'),[])
 def test_unknown_region_stays_unknown(self):
  p=organisation_evidence(self.body(address=dict(addressLocality='Bologna',addressRegion='Emilia-Romagna',addressCountry='IT')),'https://company.example','2026-11-05')[0]
  self.assertIsNone(p['region_code'])
if __name__=='__main__':unittest.main()
