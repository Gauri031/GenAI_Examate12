"""My plate check: compare what a person ate today with ICMR-NIN 'My Plate for the Day'.

No Streamlit code in this file, so it can be tested on its own:
    python -m unittest discover -s tests
"""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NUMBER_WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "half": 0.5}
UNIT_ALIAS_WORDS = ["handful", "mutthi", "tablespoon", "tbsp", "teaspoon", "tsp"]

# traffic-light colours for the bars
COLOURS = {"low": "#d9534f", "almost": "#f0ad4e", "ontrack": "#3cb371", "above": "#4a90d9", "high": "#e8743b", "none": "#9aa0a6"}
STATUS_TEXT = {"low": "Low", "almost": "Almost there", "ontrack": "On track",
               "above": "Above the plate", "high": "Above the plate: cut back", "none": "Nothing eaten yet"}


def load_reference() -> dict:
    return json.loads((DATA_DIR / "plate_reference.json").read_text(encoding="utf-8"))


def load_foods() -> list[dict]:
    return json.loads((DATA_DIR / "foods.json").read_text(encoding="utf-8"))


# ---------- matching food names ----------
class FoodIndex:
    """All food names, longest first, so 'masala dosa' wins over 'dosa'."""

    def __init__(self, foods: list[dict]):
        self.foods = foods
        pairs = [(name.lower(), food) for food in foods for name in food["names"]]
        pairs.sort(key=lambda p: len(p[0]), reverse=True)
        self.patterns = [(re.compile(r"\b" + re.escape(n) + r"(?:s|es)?\b"), n, food) for n, food in pairs]

    def find(self, text: str) -> list[tuple[int, dict]]:
        """Return (position, food) for every food named in the text, without overlaps."""
        taken: list[tuple[int, int]] = []
        found = []
        for pattern, _name, food in self.patterns:
            for m in pattern.finditer(text):
                if any(m.start() < e and m.end() > s for s, e in taken):
                    continue
                taken.append((m.start(), m.end()))
                found.append((m.start(), food))
        return sorted(found, key=lambda x: x[0])


_INDEX: FoodIndex | None = None


def _index() -> FoodIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = FoodIndex(load_foods())
    return _INDEX


# ---------- reading one line of the meal ----------
def _to_number(token: str) -> float:
    token = token.strip().lower()
    if token in NUMBER_WORDS:
        return float(NUMBER_WORDS[token])
    if "/" in token:
        a, b = token.split("/", 1)
        return float(a) / float(b)
    return float(token)


def _split_items(text: str) -> list[str]:
    parts = re.split(r"[\n,;+]|\band\b|\bwith\b", text.lower())
    return [p.strip(" .-\t") for p in parts if p.strip(" .-\t")]


def _read_item(raw: str) -> tuple[float | None, float | None, str]:
    """Return (quantity, explicit_grams, rest_of_text)."""
    s = re.sub(r"[()]", " ", raw.lower()).strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:g|gm|gms|gram|grams|ml)\b\s*(?:of\s+)?(.*)$", s)
    if m:
        return None, float(m.group(1)), m.group(2)
    m = re.match(r"^(\d+(?:\.\d+)?\s*/\s*\d+|\d+(?:\.\d+)?|half|one|two|three|four|five|six|seven|eight|an|a)\b\s*(.*)$", s)
    if m:
        return _to_number(m.group(1).replace(" ", "")), None, m.group(2)
    return None, None, s


def _food_total_g(food: dict) -> float:
    return sum(c["g"] for c in food["components"] if c["group"] != "limit") or 0.0


def parse_meal(text: str, index: FoodIndex | None = None) -> dict:
    """Turn 'what I ate' text into grams per food group.

    Returns {"items": [...], "unrecognised": [...]}. Each item has the original text,
    the food it was matched to, and grams per group.
    """
    index = index or _index()
    items, unrecognised = [], []
    for raw in _split_items(text):
        qty, explicit_g, rest = _read_item(raw)
        found = index.find(rest)
        if not found:
            unrecognised.append(raw)
            continue

        # one dish usually = one food: keep only the first match of each plate group
        kept, seen = [], set()
        for pos, food in found:
            primary = food["components"][0]["group"] if food["components"] else "none"
            if primary in seen:
                continue
            seen.add(primary)
            kept.append(food)

        for n, food in enumerate(kept):
            amount = (qty if qty is not None else 1.0) if n == 0 else 1.0
            factor = amount
            alias_used = None
            if n == 0 and explicit_g is not None and _food_total_g(food) > 0 and food["components"][0]["group"] != "limit":
                factor = explicit_g / _food_total_g(food)
            elif n == 0:
                for word in UNIT_ALIAS_WORDS:
                    if re.search(r"\b" + word + r"\b", rest) and word in food.get("unit_alias", {}):
                        alias_used = word
                        factor = amount * food["unit_alias"][word] / _food_total_g(food)
                        break
            grams: dict[str, float] = {}
            for comp in food["components"]:
                grams[comp["group"]] = grams.get(comp["group"], 0.0) + comp["g"] * factor
            items.append({"text": raw, "food": food["names"][0], "unit": food["unit"],
                          "amount": round(factor, 2), "grams": {k: round(v, 1) for k, v in grams.items()},
                          "alias": alias_used})
    return {"items": items, "unrecognised": unrecognised}


# ---------- compare with the plate ----------
def classify(ratio: float, over_is_warning: bool) -> str:
    if ratio < 0.5:
        return "low"
    if ratio < 0.9:
        return "almost"
    if ratio <= 1.25:
        return "ontrack"
    return "high" if over_is_warning else "above"


def compute_plate(parsed: dict, reference: dict | None = None) -> dict:
    """Sum grams per group and compare each with the NIN target."""
    reference = reference or load_reference()
    eaten = {g["key"]: 0.0 for g in reference["groups"]}
    limit_servings, limit_items = 0.0, []
    for item in parsed["items"]:
        for group, g in item["grams"].items():
            if group in eaten:
                eaten[group] += g
            elif group == "limit":
                limit_servings += g
                limit_items.append(item["food"])

    total_target = sum(g["target_g"] for g in reference["groups"])
    total_eaten = sum(eaten.values())
    groups = []
    for g in reference["groups"]:
        e = eaten[g["key"]]
        ratio = e / g["target_g"]
        status = "none" if e == 0 else classify(ratio, g["over_is_warning"])
        groups.append({
            "key": g["key"], "label": g["label"], "target_g": g["target_g"], "unit": g["unit"],
            "eaten_g": round(e, 1), "ratio": round(ratio, 3), "status": status,
            "colour": COLOURS[status], "status_text": STATUS_TEXT[status],
            "gap_g": round(max(g["target_g"] - e, 0), 1), "excess_g": round(max(e - g["target_g"], 0), 1),
            "share_eaten_pct": round(100 * e / total_eaten, 1) if total_eaten else 0.0,
            "share_plate_pct": round(100 * g["target_g"] / total_target, 1),
            "ask": g.get("ask", ""),
        })
    on_track = sum(1 for g in groups if g["status"] == "ontrack" or (g["status"] == "above"))
    needs = sorted((g for g in groups if g["ratio"] < 0.9), key=lambda g: g["ratio"])
    return {"groups": groups, "on_track": on_track, "total_groups": len(groups),
            "needs_more": needs, "limit_servings": int(round(limit_servings)),
            "limit_items": limit_items, "kcal": reference["kcal"], "source": reference["source"]}


def foods_help() -> list[dict]:
    """Rows for the 'foods I understand' table."""
    rows = []
    for food in load_foods():
        groups = sorted({c["group"] for c in food["components"]})
        rows.append({"food": ", ".join(food["names"][:4]), "counts as": ", ".join(groups) or "no group",
                     "one unit": food["unit"]})
    return rows


EXAMPLE_MEAL = "2 roti\n1 katori rice\n1 katori dal\n1 katori sabzi\n1 glass milk\n1 banana\n1 tsp ghee\n1 samosa"
