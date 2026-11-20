"""My plate check (ui/plate.py) and saved feedback (ui/feedback.py)."""
import feedback
import plate


def totals(text):
    parsed = plate.parse_meal(text)
    result = plate.compute_plate(parsed)
    return {g["key"]: g["eaten_g"] for g in result["groups"]}, parsed, result


def test_example_meal_adds_up_per_group():
    t, parsed, result = totals(plate.EXAMPLE_MEAL)
    assert t["cereals"] == 110          # 2 roti (60) + 1 katori rice (50)
    assert t["protein"] == 30
    assert t["vegetables"] == 100
    assert t["milk"] == 200
    assert t["fruits"] == 100
    assert t["fats"] == 13              # dal 3 + sabzi 5 + ghee 5
    assert result["limit_servings"] == 1
    assert parsed["unrecognised"] == []


def test_quantities_and_units_are_read():
    assert totals("5 almonds")[0]["nuts"] == 6.0
    assert totals("2 eggs")[0]["protein"] == 100
    assert totals("200 ml milk")[0]["milk"] == 200
    assert totals("half katori dal")[0]["protein"] == 15
    assert totals("1 tbsp ghee")[0]["fats"] == 15
    assert totals("1 handful peanuts")[0]["nuts"] == 30


def test_longest_food_name_wins_and_plurals_work():
    assert totals("masala dosa")[0]["vegetables"] == 60
    assert totals("aloo sabzi")[0]["vegetables"] == 100
    assert totals("3 rotis")[0]["cereals"] == 90


def test_unknown_foods_are_listed_not_guessed():
    parsed = plate.parse_meal("xyz food, 1 roti")
    assert parsed["unrecognised"] == ["xyz food"]


def test_status_colours_follow_the_rules():
    assert plate.classify(0.3, True) == "low"
    assert plate.classify(0.7, True) == "almost"
    assert plate.classify(1.0, True) == "ontrack"
    assert plate.classify(1.6, True) == "high"
    assert plate.classify(1.6, False) == "above"


def test_reference_matches_the_nin_plate():
    ref = {g["key"]: g["target_g"] for g in plate.load_reference()["groups"]}
    assert ref == {"cereals": 250, "vegetables": 400, "fruits": 100, "protein": 85,
                   "milk": 300, "nuts": 35, "fats": 27}


def test_feedback_is_saved_and_counted(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback, "DATA_DIR", tmp_path)
    monkeypatch.setattr(feedback, "FEEDBACK_FILE", tmp_path / "feedback.jsonl")
    feedback.save_feedback({"message_id": "m1", "rating": "up", "question": "q", "answer": "a"})
    feedback.save_feedback({"message_id": "m2", "rating": "down", "question": "q", "answer": "a"})
    feedback.save_feedback({"message_id": "m2", "rating": "up", "question": "q", "answer": "a"})
    assert feedback.feedback_stats() == {"up": 2, "down": 0, "total": 2}
    assert len(feedback.load_feedback()) == 3
