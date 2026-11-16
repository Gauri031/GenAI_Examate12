from app.tools import daily_sugar_salt_counter


def test_totals_and_status():
    r = daily_sugar_salt_counter([{"name": "cola can", "servings": 2}, {"name": "instant noodles", "servings": 1}])
    assert r["sugar_total_tsp"] == 17.5
    assert r["sugar_total_g"] == 70.0
    assert r["sugar_status"] == "over"
    assert r["salt_total_g"] == 4.0
    assert r["salt_status"] == "under"


def test_unknown_item():
    r = daily_sugar_salt_counter([{"name": "dragon fruit"}])
    assert r["unknown_items"] == ["dragon fruit"]
