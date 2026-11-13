"""Cleans the DGI 2024 PDF into records. Run from day04/: python -m app.ingest

Heuristic: finds 'Guideline N' headings in the PDF text, takes the following lines as advice.
Bad rows are skipped (try/except). If nothing parses, falls back to data/sample_records.json.
ALWAYS spot-check data/records.json against the PDF.
"""
import json
import re
from pathlib import Path

from app.models import Record

BASE = Path(__file__).resolve().parent.parent
PDF = BASE / "data" / "raw" / "DGI24thJune2024fin.pdf"
OUT = BASE / "data" / "records.json"
SAMPLE = BASE / "data" / "sample_records.json"
NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:g|mg|kg|ml|l|%|tsp|teaspoons?|kcal|months?|years?)\b", re.I)
HEAD_RE = re.compile(r"^\s*(?:Dietary\s+)?Guideline\s+(\d{1,2})\s*[:.\-]?\s*(.*)$", re.I)


def extract_pages(pdf_path):
    from pypdf import PdfReader
    return [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(str(pdf_path)).pages)]


def parse(pages):
    records, seen = [], set()
    for page_no, text in pages:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for idx, line in enumerate(lines):
            try:
                m = HEAD_RE.match(line)
                if not m:
                    continue
                no = int(m.group(1))
                if not 1 <= no <= 17 or no in seen:
                    continue
                title = m.group(2) or (lines[idx + 1] if idx + 1 < len(lines) else "")
                body = " ".join(lines[idx + 1: idx + 6])
                nums = NUM_RE.findall(body)
                seen.add(no)
                records.append(Record(no, title.strip(), body[:300], "; ".join(nums[:2]), "All Indians", str(page_no)))
            except Exception as e:  # bad row: skip, keep going
                print(f"skip bad row on page {page_no}: {e}")
    return records


def main():
    records = []
    try:
        records = [r.to_dict() for r in parse(extract_pages(PDF))]
    except FileNotFoundError:
        print(f"{PDF.name} missing - run: python -m app.fetch")
    except Exception as e:
        print(f"PDF read failed: {e}")
    if not records:
        print("Nothing parsed - using sample_records.json as fallback")
        records = json.loads(SAMPLE.read_text(encoding="utf-8"))
    for i, r in enumerate(records, 1):
        r["id"] = i
    OUT.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} records to {OUT}")


if __name__ == "__main__":
    main()
