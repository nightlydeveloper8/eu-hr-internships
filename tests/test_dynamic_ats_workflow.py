"""Offline configuration contract for the daily pilot rollout (no YAML dependency)."""
import ast
from pathlib import Path
import re
import unittest
from collector import dynamic_ats

ROOT = Path(__file__).resolve().parents[1]


class DynamicWorkflowTests(unittest.TestCase):
    def test_repository_variable_is_inherited_by_collect_only(self):
        workflow = (ROOT / '.github/workflows/collect.yml').read_text()
        collect = re.search(r'^  collect:\n(.*?)(?=^  \w+:|\Z)', workflow, re.M | re.S).group(1)
        env = re.search(r'^    env:\n((?:^      .+\n)+)', collect, re.M).group(1)
        binding = '      PEOPLE_PLACEMENT_DYNAMIC_ATS: ${{ vars.PEOPLE_PLACEMENT_DYNAMIC_ATS }}'
        self.assertIn(binding, env.splitlines())
        self.assertEqual(workflow.count('PEOPLE_PLACEMENT_DYNAMIC_ATS'), 2)
        self.assertNotIn('pilot-v1', workflow) # no hardcoded opt-in or default
        self.assertIn('run: python -m collector.daily collect --shard ${{ matrix.shard }} --shards 16 --workers 6', collect)
        # No step-level environment can shadow the job-level variable.
        self.assertIsNone(re.search(r'^        env:', collect, re.M))
        shards = re.search(r'^        shard: (\[.*\])$', collect, re.M).group(1)
        self.assertEqual(ast.literal_eval(shards), list(range(16)))
        self.assertIn('    timeout-minutes: 55', collect)
        self.assertEqual((dynamic_ats.MAX_RENDERINGS, dynamic_ats.MAX_REQUESTS, dynamic_ats.MAX_SECONDS), (3, 32, 25))


if __name__ == '__main__':
    unittest.main()
