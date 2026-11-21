"""
eval/summarize_logs.py  -  prints a summary of logs/requests.jsonl

Run from the repo root:
    python eval/summarize_logs.py
    python eval/summarize_logs.py path\\to\\other_log.jsonl
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # repo root

from app.production import summarize, LOG_FILE   # noqa: E402


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else LOG_FILE
    if not path.exists():
        raise SystemExit(f"No log file at {path}. Send some requests to the API first.")
    s = summarize(path)
    print(json.dumps(s, indent=2))
    print("\nMarkdown table for the README:\n")
    print("| Measure | Value |")
    print("|---|---|")
    for k, v in s.items():
        if not isinstance(v, dict):
            print(f"| {k} | {v} |")


if __name__ == "__main__":
    main()
