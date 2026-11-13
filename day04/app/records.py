"""Record helpers for PoshanGuide (load, search, count, get by id)."""
import json
from collections import Counter
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"


def load_records(path=DATA_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def search(records, keyword):
    kw = keyword.lower()
    return [r for r in records if any(kw in str(v).lower() for v in r.values())]


def count_by(records, field="target_group"):
    return dict(Counter(r.get(field, "unknown") for r in records))


def get_by_id(records, rec_id):
    return next((r for r in records if r["id"] == rec_id), None)
