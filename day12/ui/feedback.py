"""Save thumbs up / thumbs down for every PoshanGuide answer (one JSON line per rating)."""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"


def save_feedback(record: dict) -> None:
    """Append one rating. record needs: message_id, rating ('up' or 'down'), question, answer."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record}
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_feedback() -> list[dict]:
    if not FEEDBACK_FILE.exists():
        return []
    rows = []
    for line in FEEDBACK_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def feedback_stats() -> dict:
    """Counts of thumbs up / down (the latest rating of each message counts)."""
    latest = {}
    for row in load_feedback():
        latest[row.get("message_id")] = row.get("rating")
    up = sum(1 for r in latest.values() if r == "up")
    down = sum(1 for r in latest.values() if r == "down")
    return {"up": up, "down": down, "total": up + down}
