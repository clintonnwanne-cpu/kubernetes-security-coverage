import copy
import unittest
from coverage_check import analyze
NOW='2026-10-08T12:00:00Z'
BASE={'inventory_complete':True,'nodes':[{'id':'a','supported':True}], 'observations':[{'node_id':'a','observed_at':NOW,'healthy':True}]}
class CoverageTests(unittest.TestCase):
 def run_case(self, data): return analyze(data,NOW)
 def test_healthy(self): self.assertEqual(self.run_case(BASE)['fleet_coverage_percent'],100)
 def test_incomplete(self):
  d=copy.deepcopy(BASE); d['inventory_complete']=False
  self.assertIsNone(self.run_case(d)['fleet_coverage_percent'])
 def test_empty(self): self.assertIsNone(self.run_case({'nodes':[],'observations':[],'inventory_complete':True})['fleet_coverage_percent'])
 def test_missing(self):
  d=copy.deepcopy(BASE); d['observations']=[]; self.assertEqual(self.run_case(d)['counts'],{'missing':1})
 def test_stale(self):
  d=copy.deepcopy(BASE); d['observations'][0]['observed_at']='2026-10-01T00:00:00Z'; self.assertEqual(self.run_case(d)['counts'],{'stale':1})
 def test_future(self):
  d=copy.deepcopy(BASE); d['observations'][0]['observed_at']='2027-10-01T00:00:00Z'; self.assertEqual(self.run_case(d)['counts'],{'unknown':1})
 def test_conflict(self):
  d=copy.deepcopy(BASE); d['observations'].append({**d['observations'][0],'healthy':False}); self.assertEqual(self.run_case(d)['counts'],{'unknown':1})
 def test_duplicate_inventory(self):
  d=copy.deepcopy(BASE); d['nodes']*=2
  with self.assertRaises(ValueError): self.run_case(d)
 def test_unsupported_in_denominator(self):
  d=copy.deepcopy(BASE); d['nodes'].append({'id':'b','supported':False}); self.assertEqual(self.run_case(d)['fleet_coverage_percent'],50)
 def test_orphan(self):
  d=copy.deepcopy(BASE); d['observations'].append({'node_id':'other'}); self.assertEqual(self.run_case(d)['orphan_observation_ids'],['other'])
 def test_bad_timestamp(self):
  d=copy.deepcopy(BASE); d['observations'][0]['observed_at']='bad'; self.assertEqual(self.run_case(d)['counts'],{'unknown':1})
 def test_unhealthy(self):
  d=copy.deepcopy(BASE); d['observations'][0]['healthy']=False; self.assertEqual(self.run_case(d)['counts'],{'missing':1})
if __name__=='__main__': unittest.main()
