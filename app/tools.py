"""Day 09 / S1 - the agent tool: daily_sugar_salt_counter."""
import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "sugar_salt_items.csv"

GRAMS_PER_TSP = 4.0        # 1 level teaspoon of sugar ~ 4 g
SUGAR_LIMIT_LOW_G = 20.0   # guideline range 20-25 g/day  (EDIT to match YOUR guidelines)
SUGAR_LIMIT_HIGH_G = 25.0
SALT_LIMIT_G = 5.0         # EDIT to match YOUR guidelines


def load_catalog(path: Path = CSV_PATH) -> dict:
    catalog = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            catalog[row["item"].strip().lower()] = {
                "sugar_tsp": float(row["sugar_tsp"] or 0),
                "salt_g": float(row["salt_g"] or 0),
            }
    return catalog


def _sugar_status(total_g: float) -> str:
    if total_g > SUGAR_LIMIT_HIGH_G:
        return "over"
    if total_g >= SUGAR_LIMIT_LOW_G:
        return "at_limit"
    return "under"


def daily_sugar_salt_counter(items: list) -> dict:
    """items: [{"name": "cola can", "servings": 2}, ...]
    You may also pass "sugar_tsp" / "salt_g" per serving instead of a CSV name."""
    catalog = load_catalog()
    rows, unknown = [], []
    sugar_tsp = salt_g = 0.0

    for it in items:
        name = str(it.get("name", "")).strip()
        qty = float(it.get("servings", 1))
        if "sugar_tsp" in it or "salt_g" in it:
            per = {"sugar_tsp": float(it.get("sugar_tsp", 0)), "salt_g": float(it.get("salt_g", 0))}
        elif name.lower() in catalog:
            per = catalog[name.lower()]
        else:
            unknown.append(name)
            continue
        s, g = per["sugar_tsp"] * qty, per["salt_g"] * qty
        sugar_tsp += s
        salt_g += g
        rows.append({"name": name, "servings": qty, "sugar_tsp": s, "salt_g": g})

    sugar_g = sugar_tsp * GRAMS_PER_TSP
    return {
        "items": rows,
        "unknown_items": unknown,
        "sugar_total_tsp": round(sugar_tsp, 2),
        "sugar_total_g": round(sugar_g, 1),
        "sugar_limit_g": f"{SUGAR_LIMIT_LOW_G:g}-{SUGAR_LIMIT_HIGH_G:g}",
        "sugar_status": _sugar_status(sugar_g),
        "salt_total_g": round(salt_g, 2),
        "salt_limit_g": SALT_LIMIT_G,
        "salt_status": "over" if salt_g > SALT_LIMIT_G else "under",
    }


TOOL_SPECS = {
    "daily_sugar_salt_counter": (
        'Totals a day of food items and compares with sugar/salt limits. '
        'input: {"items": [{"name": "cola can", "servings": 2}]}'
    ),
    "rag_search": 'Searches the guidelines knowledge base. input: {"query": "..."}',
}
