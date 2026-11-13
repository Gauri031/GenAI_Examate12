# Day 04 - Real data slice + models + fetch

## Task
**S1:** download the DGI 2024 data into `data/raw/`; `app/ingest.py` cleans it into the fields (try/except for bad rows) and saves `data/records.json`.
**S2:** dataclass in `app/models.py`; `app/fetch.py` downloads 3+ documents with `requests` (timeouts, error handling).

## Where is each file
| File | Exact path |
|---|---|
| Downloader (S2) | `day04/app/fetch.py` |
| Cleaner / ingest (S1) | `day04/app/ingest.py` |
| Dataclass (S2) | `day04/app/models.py` |
| Settings loader | `day04/app/config.py` (reads the root `.env`; `REQUEST_TIMEOUT`) |
| Downloaded raw files | `day04/data/raw/` (git-ignored; `.gitkeep` keeps the folder) |
| Cleaned output | `day04/data/records.json` (created by ingest) |
| Fallback data | `day04/data/sample_records.json` |
| `.venv`, `requirements.txt`, `.gitignore`, `.env` | **repo root** |

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
cd day04
python -m app.fetch      # needs internet; saves 3 files into data/raw/
python -m app.ingest     # writes data/records.json
```
Downloads: https://nin.res.in/popular.html, the DGI 2024 PDF, and https://www.nin.res.in/

`ingest.py` is a heuristic parser. Open the PDF and spot-check titles, numbers and `page_ref` in `data/records.json`. If the PDF is missing it falls back to the sample records.
