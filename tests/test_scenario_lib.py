import json
from pathlib import Path
import unittest

from pacilab.scenario_lib import validate_scenario_obj, ScenarioValidationError


class ScenarioLibTest(unittest.TestCase):
    def test_v1_example_valid(self):
        raw = json.loads(Path("docs/scenario_v1.example.json").read_text(encoding="utf-8"))
        norm = validate_scenario_obj(raw)
        self.assertEqual(norm["id"], "allow_arp_regression_v1")

    def test_v2_example_valid(self):
        raw = json.loads(Path("docs/scenario_v2.example.json").read_text(encoding="utf-8"))
        norm = validate_scenario_obj(raw)
        self.assertEqual(norm.get("schema_version"), "v2")

    def test_bad_id_invalid(self):
        with self.assertRaises(ScenarioValidationError):
            validate_scenario_obj({"id": "bad id", "name": "x", "events": [{"name": "e", "packet": {"ethertype": "0x0800"}}]})


if __name__ == "__main__":
    unittest.main()
