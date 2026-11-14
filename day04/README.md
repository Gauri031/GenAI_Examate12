# Day 04 - Real DGI data, fetch, and records

## Task status

- [x] **S1:** Download the DGI 2024 PDF to `data/raw/`, extract the 17 guideline summaries into the project record fields, and save `data/records.json`.
- [x] **S2:** Define the record dataclass and download three NIN source documents with request timeouts, error reporting, and a source checksum manifest.
- [ ] **Review:** Spot-check extracted advice, numeric limits, and PDF page references against the source before using them as health guidance. Text extraction is best-effort, not a medical review.

## Files changed or generated

| File | Purpose |
|---|---|
| `app/fetch.py` | Downloads `popular.html`, the DGI PDF, and the NIN home page. Uses the official PDF URL first and a pinned Internet Archive copy if the current URL is unavailable. |
| `app/ingest.py` | Extracts source summaries for all 17 guidelines; exits with an error instead of silently substituting sample data. |
| `app/models.py` | Typed `Record` dataclass serialized into JSON. |
| `app/records.py` | Record helpers default to generated `data/records.json`; `SAMPLE_DATA_FILE` points to the separate sample fixture. |
| `app/config.py` | Loads shared settings, including `REQUEST_TIMEOUT`. |
| `app/__init__.py` | Makes `app` importable as a package. |
| `data/records.json` | Generated 17-record result committed with the project. |
| `data/source_manifest.json` | Committed download URLs, byte counts, timestamps, and SHA-256 hashes. |
| `data/sample_records.json` | Sample fixture; it is not used as an automatic ingest fallback. |
| `data/raw/` | Local source downloads; PDF and HTML files remain git-ignored. |
| Root `requirements.txt`, `.gitignore`, `.env.example` | Shared dependencies, ignore rules, and settings template. |

## Run from the repository root

Activate the root virtual environment and install dependencies once:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then fetch and ingest:

```powershell
cd day04
python -m app.fetch
python -m app.ingest
```

`fetch.py` requires internet access and exits non-zero if any source cannot be retrieved. The original DGI PDF URL currently returns 404; the fetcher uses the pinned archived copy as a fallback. The generated `data/source_manifest.json` records which URL was actually used and lets you verify the ignored raw files by SHA-256.

`ingest.py` requires the PDF in `data/raw/`. If it is missing, unreadable, or does not yield all 17 summaries, ingestion fails rather than creating a success-shaped sample output. `page_ref` is the 1-based PDF page number. Review `data/records.json` against the PDF before relying on its extracted health advice or numeric limits.
