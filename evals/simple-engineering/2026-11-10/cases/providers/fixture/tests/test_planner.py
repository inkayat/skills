import unittest
from planner import make_plan

class ExistingPlanTests(unittest.TestCase):
    def test_default(self):
        self.assertEqual(make_plan("ship"), {"task": "ship", "assistant": "claude", "stages": ["build", "review"]})
    def test_custom_stages(self):
        self.assertEqual(make_plan("ship", {"stages": ["test"]})["stages"], ["test"])
