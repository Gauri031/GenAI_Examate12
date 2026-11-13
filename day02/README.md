# Day 02 - Records + Refactor

## Task
**S1:** one record for each of the 17 DGI 2024 guidelines plus 3 records from the food-label guideline (17), stored as a list of dicts with fields `guideline_no, guideline_title, key_advice, number_limit, target_group, page_ref`; print all, search by keyword, count per category.
**S2:** refactor into `app/records.py` (`load_records, search, count_by, get_by_id`) + `app/cli.py`; add `.venv`, `requirements.txt`, `.gitignore`.

## Where is each file
`app/` is a normal Python package **inside this day folder**. It is a project convention, not a requirement.

| File | Exact path |
|---|---|
| Records data (S1) | `day02/data/sample_records.json` (20 records, plus an `id` field) |
| Record functions (S2) | `day02/app/records.py` |
| CLI (S2) | `day02/app/cli.py` |
| Settings loader | `day02/app/config.py` (reads the root `.env`) |
| Package marker | `day02/app/__init__.py` |
| `.venv`, `requirements.txt`, `.gitignore`, `.env` | **repo root**, see below |

## Global files (repo root, shared by ALL days)
These are NOT inside any day folder:
| File | Path | Purpose |
|---|---|---|
| Virtual env | `<repo>/.venv/` | one environment for all days |
| Dependencies | `<repo>/requirements.txt` | one install for all days |
| Settings | `<repo>/.env` (template: `.env.example`) | limits, port, timeout; git-ignored |
| Git ignore | `<repo>/.gitignore` | ignores `.venv`, `.env`, `__pycache__`, raw downloads |

## Run (from the repo root first, one-time setup)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env  (skip if .env already exists)
```

Then:
```bash
cd day02
python -m app.cli
```
Run it from inside `day02/` so that `app` is found.

> `page_ref` is `TBD` and some titles/limits must be verified against the PDF before submission (Day 04 ingest brings in real data).
