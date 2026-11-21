import json
import unittest
from pathlib import Path
from collector.daily import provision
from collector.company_registry import validate_registry

ROOT=Path(__file__).resolve().parents[1]
SOURCES={'recruitee-climeworks-ch':'climeworks-ch', 'recruitee-peripass-be':'peripass-be', 'greenhouse-fanatics-collectibles-gb':'fanatics-collectibles-gb'}

class SevenATSHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.companies=json.loads((ROOT/'data/companies.json').read_text())
        cls.sources=json.loads((ROOT/'data/sources.json').read_text())
        cls.geography=json.loads((ROOT/'data/geography.json').read_text())

    def test_sources_remain_disabled_after_provision(self):
        self.assertTrue(validate_registry(self.companies,self.geography,self.sources))
        companies,sources=provision(self.companies,self.sources)
        self.assertEqual({s['id'] for s in self.sources if s.get('enabled')},{s['id'] for s in sources if s.get('enabled')})
        for sid,cid in SOURCES.items():
            company=next(c for c in companies if c['id']==cid)
            source=next(s for s in sources if s['id']==sid)
            self.assertIs(company['collection_activation_hold'],True)
            self.assertIs(source['collection_activation_hold'],True)
            self.assertIs(source['enabled'],False)
            self.assertIn(sid,company['source_ids'])
            self.assertFalse(any(s.get('enabled') for s in sources if s.get('company_id')==cid))
            self.assertNotIn('auto-'+cid,{s['id'] for s in sources})
        self.assertEqual(provision(companies,sources),(companies,sources))

    def test_hold_rejects_accidental_enablement(self):
        sources=[dict(s,enabled=True) if s['id']=='recruitee-climeworks-ch' else s for s in self.sources]
        with self.assertRaisesRegex(ValueError,'Held employer has an enabled source'):
            provision(self.companies,sources)

if __name__=='__main__': unittest.main()
