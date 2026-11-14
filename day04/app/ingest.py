"""Extract the DGI 2024 guideline summaries into data/records.json."""
import json
import re
from pathlib import Path

from pypdf.errors import PdfReadError

from app.models import Record

BASE = Path(__file__).resolve().parent.parent
PDF = BASE / "data" / "raw" / "DGI24thJune2024fin.pdf"
OUT = BASE / "data" / "records.json"
TITLE_BY_NUMBER = {
    1: "Eat a variety of foods to ensure a balanced diet",
    2: "Ensure provision of extra food and healthcare during pregnancy and lactation",
    3: "Ensure exclusive breastfeeding for the first six months and continue breastfeeding till two years and beyond",
    4: "Start feeding homemade semi-solid complementary foods to the infant soon after six months of age",
    5: "Ensure adequate and appropriate diets for children and adolescents both in health and sickness",
    6: "Eat plenty of vegetables and legumes",
    7: "Use oils/fats in moderation; choose a variety of oil seeds, nuts, nutricereals, and legumes to meet daily needs of fats and essential fatty acids (EFA)",
    8: "Obtain good quality proteins and essential amino acids (EAA) through appropriate combination of foods and avoid protein supplements to build muscle mass",
    9: "Adopt a healthy lifestyle to prevent abdominal obesity, overweight and overall obesity",
    10: "Be physically active and exercise regularly to maintain good health",
    11: "Restrict salt intake",
    12: "Consume safe and clean foods",
    13: "Adopt appropriate pre-cooking and cooking methods",
    14: "Drink adequate quantity of water",
    15: "Minimize the consumption of high fat, sugar, salt (HFSS) and ultra-processed foods (UPFs)",
    16: "Include nutrient-rich foods in the diets of the elderly for health and wellness",
    17: "Read information on food labels to make informed and healthy food choices",
}
TARGET_GROUP_BY_NUMBER = {
    2: "Pregnant and lactating women",
    3: "Infants and mothers",
    4: "Infants and young children",
    5: "Children and adolescents",
    16: "Older adults",
    17: "Consumers",
}
NUM_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:g|mg|kg|ml|l|%|tsp|teaspoons?|kcal|months?|years?)\b",
    re.I,
)
HEAD_RE = re.compile(r"\bGUIDELINE\s+(\d{1,2})\b")
SUMMARY_RE = re.compile(r"POINTS\s+TO\s+REGISTER", re.I)
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
PDF_FRONT_MATTER_PAGES = 10


def extract_pages(pdf_path):
    from pypdf import PdfReader
    return [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(str(pdf_path)).pages)]


def parse(pages):
    text_parts = []
    positions = []
    offset = 0
    seen = set()

    for page_no, text in pages:
        if page_no <= PDF_FRONT_MATTER_PAGES:
            continue
        normalized = CONTROL_CHARS_RE.sub(" ", text)
        text_parts.append(normalized)
        for match in HEAD_RE.finditer(normalized):
            number = int(match.group(1))
            if number not in TITLE_BY_NUMBER or number in seen:
                continue
            positions.append((number, page_no, offset + match.start()))
            seen.add(number)
        offset += len(normalized) + 1

    full_text = "\n".join(text_parts)
    records = []
    for index, (number, page_no, start) in enumerate(positions):
        try:
            end = positions[index + 1][2] if index + 1 < len(positions) else len(full_text)
            section = full_text[start:end]
            summary_match = SUMMARY_RE.search(section)
            if summary_match is None:
                raise ValueError("summary heading 'POINTS TO REGISTER' was not found")

            advice = section[summary_match.end():]
            next_title = TITLE_BY_NUMBER.get(number + 1)
            if next_title:
                title_pattern = re.compile(
                    r"\s+".join(re.escape(word) for word in next_title.split()),
                    re.I,
                )
                title_match = title_pattern.search(advice)
                if title_match is not None:
                    advice = advice[:title_match.start()]
            advice = re.sub(
                r"\s+\d{1,3}\s*ICMR-National Institute of Nutrition.*$",
                "",
                advice,
                flags=re.I | re.S,
            )
            advice = re.sub(r"\s*[\uFFFD\u2022\u00b7]\s+", "; ", advice)
            advice = advice.replace("\uFFFD", "-")
            advice = " ".join(advice.split()).strip(" -;")
            advice = re.sub(r"\s+\d{1,3}$", "", advice)
            if not advice:
                raise ValueError("summary text is empty")

            numbers = NUM_RE.findall(advice)
            if len(advice) > 1200:
                advice = advice[:1200].rsplit(" ", 1)[0].rstrip(" ;")
            records.append(
                Record(
                    guideline_no=number,
                    guideline_title=TITLE_BY_NUMBER[number],
                    key_advice=advice,
                    number_limit="; ".join(numbers[:2]),
                    target_group=TARGET_GROUP_BY_NUMBER.get(number, "All Indians"),
                    page_ref=str(page_no),
                    id=number,
                )
            )
        except ValueError as e:
            print(f"skip bad row for guideline {number} on PDF page {page_no}: {e}")

    found = {record.guideline_no for record in records}
    expected = set(TITLE_BY_NUMBER)
    missing = sorted(expected - found)
    if missing:
        raise ValueError(f"could not extract guidelines: {missing}")
    return records


def main():
    if not PDF.is_file():
        raise SystemExit(f"{PDF.name} is missing - run: python -m app.fetch")
    try:
        records = [record.to_dict() for record in parse(extract_pages(PDF))]
    except (OSError, PdfReadError, ValueError) as e:
        raise SystemExit(f"Could not ingest {PDF.name}: {e}") from e

    OUT.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(records)} records to {OUT}")


if __name__ == "__main__":
    main()
