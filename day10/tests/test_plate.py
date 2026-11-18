"""Quick checks for the plate logic and feedback storage.  Run:  python -m unittest discover -s tests"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ui"))

import feedback  # noqa: E402
import plate  # noqa: E402


def totals(text):
    parsed = plate.parse_meal(text)
    result = plate.compute_plate(parsed)
    return {g["key"]: g["eaten_g"] for g in result["groups"]}, parsed, result


class PlateTests(unittest.TestCase):
    def test_example_meal(self):
        t, parsed, result = totals(plate.EXAMPLE_MEAL)
        self.assertEqual(t["cereals"], 110)       # 2 roti (60) + 1 katori rice (50)
        self.assertEqual(t["protein"], 30)        # 1 katori dal
        self.assertEqual(t["vegetables"], 100)
        self.assertEqual(t["milk"], 200)
        self.assertEqual(t["fruits"], 100)
        self.assertEqual(t["fats"], 13)           # dal 3 + sabzi 5 + ghee 5
        self.assertEqual(result["limit_servings"], 1)
        self.assertEqual(parsed["unrecognised"], [])

    def test_quantities(self):
        self.assertEqual(totals("5 almonds")[0]["nuts"], 6.0)
        self.assertEqual(totals("2 eggs")[0]["protein"], 100)
        self.assertEqual(totals("200 ml milk")[0]["milk"], 200)
        self.assertEqual(totals("100 g curd")[0]["milk"], 100)
        self.assertEqual(totals("half katori dal")[0]["protein"], 15)
        self.assertEqual(totals("2 tsp ghee")[0]["fats"], 10)
        self.assertEqual(totals("1 tbsp ghee")[0]["fats"], 15)
        self.assertEqual(totals("1 handful peanuts")[0]["nuts"], 30)
        self.assertEqual(totals("1/2 glass milk")[0]["milk"], 100)

    def test_matching(self):
        t, parsed, _ = totals("masala dosa")
        self.assertEqual(t["vegetables"], 60)     # 'masala dosa' beats 'dosa'
        t, _, _ = totals("aloo sabzi")
        self.assertEqual(t["vegetables"], 100)    # one dish, vegetables counted once
        t, _, _ = totals("dal rice")
        self.assertEqual((t["protein"], t["cereals"]), (30, 50))
        t, _, _ = totals("3 rotis")
        self.assertEqual(t["cereals"], 90)        # plural works

    def test_unrecognised_and_limit(self):
        parsed = plate.parse_meal("xyz food, 1 roti")
        self.assertEqual(parsed["unrecognised"], ["xyz food"])
        self.assertEqual(plate.compute_plate(plate.parse_meal("2 samosa, 1 cold drink"))["limit_servings"], 3)
        self.assertEqual(plate.parse_meal("1 glass water")["items"][0]["grams"], {})

    def test_status_colours(self):
        self.assertEqual(plate.classify(0.3, True), "low")
        self.assertEqual(plate.classify(0.7, True), "almost")
        self.assertEqual(plate.classify(1.0, True), "ontrack")
        self.assertEqual(plate.classify(1.6, True), "high")
        self.assertEqual(plate.classify(1.6, False), "above")
        result = plate.compute_plate(plate.parse_meal(""))
        self.assertTrue(all(g["status"] == "none" for g in result["groups"]))

    def test_reference_matches_nin(self):
        ref = {g["key"]: g["target_g"] for g in plate.load_reference()["groups"]}
        self.assertEqual(ref, {"cereals": 250, "vegetables": 400, "fruits": 100, "protein": 85,
                               "milk": 300, "nuts": 35, "fats": 27})

    def test_needs_more_sorted(self):
        result = plate.compute_plate(plate.parse_meal("4 roti, 1 banana"))
        keys = [g["key"] for g in result["needs_more"]]
        self.assertIn("vegetables", keys)
        self.assertNotIn("fruits", keys)


class FeedbackTests(unittest.TestCase):
    def test_save_and_stats(self):
        with tempfile.TemporaryDirectory() as d:
            feedback.DATA_DIR = Path(d)
            feedback.FEEDBACK_FILE = Path(d) / "feedback.jsonl"
            feedback.save_feedback({"message_id": "m1", "rating": "up", "question": "q", "answer": "a"})
            feedback.save_feedback({"message_id": "m2", "rating": "down", "question": "q", "answer": "a"})
            feedback.save_feedback({"message_id": "m2", "rating": "up", "question": "q", "answer": "a"})
            self.assertEqual(feedback.feedback_stats(), {"up": 2, "down": 0, "total": 2})
            self.assertEqual(len(feedback.load_feedback()), 3)


if __name__ == "__main__":
    unittest.main()
