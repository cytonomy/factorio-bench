"""Behavioral checks for the synthetic demonstration's evidence verifier."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_examples


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.examples = run_examples.build_examples()
        self.steady = self.examples["cases"][0]

    def test_examples_have_expected_outcomes_and_conserved_material(self):
        cases = self.examples["cases"]
        self.assertEqual([case["verdict"] for case in cases], ["pass", "fail", "fail"])
        self.assertEqual([sum(w["passed"] for w in case["windows"]) for case in cases], [5, 2, 0])
        self.assertEqual(cases[0]["totals"]["delivered"], 208)
        self.assertEqual(cases[1]["totals"]["mined"], 200)
        self.assertEqual(cases[1]["totals"]["delivered"], 94)
        self.assertEqual(cases[2]["totals"]["delivered"], 40)
        self.assertEqual(cases[2]["totals"]["manual_delivered"], 160)
        for case in cases:
            for window in case["windows"]:
                self.assertLessEqual(window["delivered"], window["smelted"])
                self.assertLessEqual(window["smelted"], window["mined"])

    def test_early_surplus_cannot_cover_later_failed_windows(self):
        events = run_examples.trace("spike", [(160, 160, 160, 0)] + [(0, 0, 0, 0)] * 4)
        result = run_examples.verify(events)
        self.assertEqual(result["totals"]["delivered"], 160)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(sum(w["passed"] for w in result["windows"]), 1)

    def test_manual_deposits_cannot_score_or_hide_intervention(self):
        events = run_examples.trace("intervention", [(40, 40, 40, 1)] * 5)
        result = run_examples.verify(events)
        self.assertEqual(result["totals"]["delivered"], 200)
        self.assertEqual(result["totals"]["manual_delivered"], 5)
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(any(w["passed"] for w in result["windows"]))

    def test_missing_or_off_power_fails_the_affected_window(self):
        for off in (False, True):
            events = deepcopy(self.steady["events"])
            if off:
                events[0]["quantity"] = 0
            else:
                events.pop(0)
            result = run_examples.verify(events)
            self.assertEqual(result["verdict"], "fail")
            self.assertFalse(result["windows"][0]["powered"])
            self.assertEqual(sum(w["passed"] for w in result["windows"]), 4)

    def test_duplicate_and_out_of_order_events_are_rejected(self):
        events = deepcopy(self.steady["events"])
        events.insert(2, deepcopy(events[1]))
        with self.assertRaises(ValueError):
            run_examples.verify(events)
        events = deepcopy(self.steady["events"])
        events[1], events[2] = events[2], events[1]
        with self.assertRaises(ValueError):
            run_examples.verify(events)

    def test_unknown_sources_and_invalid_quantities_are_rejected(self):
        for field, value in (("source", "player"), ("kind", "invented"), ("quantity", True), ("quantity", -1), ("quantity", 1.5), ("quantity", 0)):
            events = deepcopy(self.steady["events"])
            events[1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                run_examples.verify(events)

    def test_horizon_is_half_open_and_window_edges_belong_to_new_window(self):
        events = deepcopy(self.steady["events"])
        for tick in (53999, 72000, True):
            invalid = deepcopy(events)
            invalid[0]["tick"] = tick
            with self.subTest(tick=tick), self.assertRaises(ValueError):
                run_examples.verify(invalid)
        # A deposit on the exact boundary must affect the second window only.
        extra = {"id": "boundary", "tick": 57600, "kind": "manual-deliver", "quantity": 1, "source": "player"}
        events.append(extra)
        events.sort(key=lambda event: event["tick"])
        result = run_examples.verify(events)
        self.assertTrue(result["windows"][0]["passed"])
        self.assertFalse(result["windows"][1]["passed"])
        self.assertEqual(result["windows"][1]["manual_delivered"], 1)

    def test_material_cannot_appear_before_upstream_production(self):
        events = deepcopy(self.steady["events"])
        events[2]["quantity"] = events[1]["quantity"] + 1
        with self.assertRaises(ValueError):
            run_examples.verify(events)
        events = deepcopy(self.steady["events"])
        events[3]["quantity"] = events[2]["quantity"] + 1
        with self.assertRaises(ValueError):
            run_examples.verify(events)

    def test_duplicate_or_misplaced_power_markers_are_rejected(self):
        events = deepcopy(self.steady["events"])
        marker = dict(events[0], id="extra-power")
        events.insert(1, marker)
        with self.assertRaises(ValueError):
            run_examples.verify(events)
        events = deepcopy(self.steady["events"])
        events[0]["tick"] += 1
        with self.assertRaises(ValueError):
            run_examples.verify(events)

    def test_fixture_is_reproducible_and_scores_are_derived(self):
        expected = run_examples.serialized_examples()
        self.assertEqual(expected, run_examples.serialized_examples())
        self.assertEqual(run_examples.OUTPUT.read_text(encoding="utf-8"), expected)
        saved = json.loads(expected)
        for case in saved["cases"]:
            recalculated = run_examples.verify(case["events"])
            for field in ("verdict", "windows", "totals"):
                self.assertEqual(case[field], recalculated[field])


if __name__ == "__main__":
    unittest.main()
