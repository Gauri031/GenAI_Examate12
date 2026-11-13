# Day 03 - FastAPI service + analysis + TF-IDF search

## Task
**S1:** `app/main.py` FastAPI service: GET `/health`, `/records?limit=`, `/records/{id}` (404 if missing), `/search?q=`, POST `/questions`. README "How to run".
**S2:** `analysis/explore.py` prints 3 facts with pandas; `app/smart_search.py` ranks records with TF-IDF + cosine and powers `/search`. Tag `week-1`.

## Where is each file
`app/` is inside this day folder. It holds copies of Day 02's `records.py` and `cli.py` so Day 03 runs on its own.

| File | Exact path |
|---|---|
| FastAPI service (S1) | `day03/app/main.py` |
| TF-IDF search (S2) | `day03/app/smart_search.py` |
| Pandas analysis (S2) | `day03/analysis/explore.py` (outside `app/`) |
| Records loader | `day03/app/records.py` |
| Settings loader | `day03/app/config.py` (reads the root `.env`) |
| Data | `day03/data/sample_records.json` |
| `.venv`, `requirements.txt`, `.gitignore`, `.env` | **repo root** |

## Global files (repo root, shared by ALL days)
These are NOT inside any day folder:
| File | Path | Purpose |
|---|---|---|
| Virtual env | `<repo>/.venv/` | one environment for all days |
| Dependencies | `<repo>/requirements.txt` | one install for all days |
| Settings | `<repo>/.env` (template: `.env.example`) | limits, port, timeout; git-ignored |
| Git ignore | `<repo>/.gitignore` | ignores `.venv`, `.env`, `__pycache__`, raw downloads |


## How to run
## Run (from the repo root first, one-time setup)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env  (skip if .env already exists)
```

Then:
```bash
cd day03
python analysis/explore.py
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs. Port and `SEARCH_TOP_K` can be changed in the root `.env`.

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | status + record count |
| GET | `/records?limit=` | list records |
| GET | `/records/{id}` | one record, 404 if missing |
| GET | `/search?q=` | TF-IDF ranked search |
| POST | `/questions` | body `{"question": "..."}`; returns best advice + citation |

Git tag: `git tag week-1 && git push origin week-1`
