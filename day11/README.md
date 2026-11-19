# Day 11 - PoshanGuide: Tests, Lint (ruff) and Docker

## 1. The Task (as given)

> **S1:** `tests/` with **8+ pytest tests** (records, search, `/health`, `/ask` with a fake LLM, and your agent tool); **`ruff check .` passes**.
> **S2:** `Dockerfile` + `.dockerignore` + `docker-compose.yml` so the PoshanGuide **API and UI start with `docker compose up`**; README **"Run with Docker"**.

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| S1 | 8+ pytest tests | 35 tests in 6 files | `tests/` |
| S1 | Test records | `test_records.py` (document chunk records keep source, page, title) | `tests/` |
| S1 | Test search | `test_search.py` | `tests/` |
| S1 | Test `/health` | `test_api.py` | `tests/` |
| S1 | Test `/ask` with a fake LLM | `test_api.py`, `test_rag.py`, fakes in `conftest.py` | `tests/` |
| S1 | Test the agent tool | `test_agent_tool.py` (tools in `app/tools.py`) | `tests/` |
| S1 | `ruff check .` passes | `ruff.toml` (rules E4, E7, E9, F) | project root |
| S2 | Dockerfile | `Dockerfile` (one image for API and UI) | project root |
| S2 | .dockerignore | `.dockerignore` | project root |
| S2 | docker-compose.yml | `docker-compose.yml` (services `api` and `ui`) | project root |
| S2 | README "Run with Docker" | section 7 of this file | `README.md` |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .gitignore
├── day08/ day10/ ...               <- earlier days (not needed by Docker)
└── day11/
    ├── README.md                   <- this file
    ├── Dockerfile                  <- builds the image
    ├── .dockerignore               <- files NOT copied into the image
    ├── docker-compose.yml          <- starts API + UI with one command
    ├── requirements.txt            <- packages for the app (API + UI)
    ├── requirements-dev.txt        <- adds pytest, httpx, ruff for testing
    ├── pytest.ini                  <- tells pytest where the tests and code are
    ├── ruff.toml                   <- lint rules
    ├── .env                        <- your real API key, LOCAL ONLY, never committed
    ├── .env.example                <- template without secrets, committed
    ├── app/                        <- the API (from day08) + tools.py
    │   ├── __init__.py
    │   ├── main.py                 <- FastAPI app: /health, /ask ...
    │   ├── rag.py                  <- retrieve + prompt + citations + "I don't know"
    │   ├── ask.py                  <- POST /ask
    │   ├── search.py               <- GET /search/semantic
    │   ├── chat.py                 <- POST /chat
    │   ├── chunking.py             <- document chunk records (source, page, title)
    │   ├── embed.py                <- text -> vectors
    │   ├── vectorstore.py          <- Chroma index + semantic_search()
    │   ├── llm.py                  <- Groq / Gemini wrapper
    │   └── tools.py                <- NEW  agent tools (search_documents, nin_plate_amounts)
    ├── ui/                         <- the Streamlit UI (from day10)
    │   ├── app.py
    │   ├── plate.py
    │   └── feedback.py
    ├── prompts/                    <- rag_system.md, rag_task.md, system.md, task_v1.md, task_v2.md
    ├── documents/                  <- PoshanGuide documents that are indexed
    ├── data/                       <- foods.json, plate_reference.json, feedback.jsonl (created by the UI)
    └── tests/
        ├── conftest.py             <- fake LLM, fake retrieval, test client
        ├── test_records.py
        ├── test_search.py
        ├── test_api.py
        ├── test_rag.py
        ├── test_agent_tool.py
        └── test_plate.py
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md`, `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, `ruff.toml`, `.env.example` | `day11/` |
| `main.py`, `rag.py`, `ask.py`, `search.py`, `chat.py`, `chunking.py`, `embed.py`, `vectorstore.py`, `llm.py`, `tools.py`, `__init__.py` | `day11/app/` |
| `app.py`, `plate.py`, `feedback.py` | `day11/ui/` |
| the 5 prompt files | `day11/prompts/` |
| my documents | `day11/documents/` |
| `foods.json`, `plate_reference.json` | `day11/data/` |
| `conftest.py` and the six `test_*.py` files | `day11/tests/` |

File names must be exact. A downloaded file named `Dockerfile (1)` must be renamed to `Dockerfile` (no extension).

## 5. The tests (S1)

### 5.1 How they work
- **No real LLM, no API key, no internet.** `conftest.py` has a `FakeLLM` that replaces `app.rag.call_llm` and returns a reply I script. A `fake_retrieval` helper replaces the search with a fixed list of chunks.
- Tests use pytest's `monkeypatch` to swap functions only for one test, then restore them.
- `pytest.ini` puts `day11/` and `day11/ui/` on the Python path, so the tests can `import app` and `import plate`.

### 5.2 What is tested (35 tests)

| File | Tests | What it checks |
|------|-------|----------------|
| `test_records.py` | 7 | every chunk keeps source, page and title; page numbers follow `<!-- page -->`; title comes from the first heading; chunk ids are unique; long text is split without losing text; empty folder gives no chunks; JSON entries become pages |
| `test_search.py` | 4 | `semantic_search` ranks hits and scores them as `1 - distance`; builds the index when it is empty; `GET /search/semantic` returns hits; it rejects a missing `q` or `k=0` |
| `test_api.py` | 7 | `/health` returns ok; `/ask` answers with citations; Q6 gets "I don't know" with no citations; the LLM is not called when nothing is close; a too-short question gives 422; LLM failure gives 502; bad JSON from the LLM gives 502 |
| `test_rag.py` | 5 | no citation becomes "I don't know"; citations are read from `[1]` marks in the answer; an invalid source number becomes "I don't know"; a model that says "I don't know" is respected; the config is reported back |
| `test_agent_tool.py` | 5 | the search tool returns compact results; it passes the query and k; it rejects an empty query; an unknown tool raises `KeyError`; the NIN tool returns the 7 plate amounts |
| `test_plate.py` | 7 | My plate check totals, quantities and units, longest-name matching, unknown foods, colour rules, NIN reference amounts, and saved feedback |

### 5.3 About "records" and "agent tool"
- **Records:** the records tested are the document chunk records (source, page, title) made by `chunking.py`. If my Day 04 `records.py` has its own functions, add a `tests/test_day04_records.py` for them in the same style.
- **Agent tool:** `app/tools.py` holds two small tools (`search_documents`, `nin_plate_amounts`) and a `run_tool(name, **args)` helper. If my Day 09 agent has its own tool functions, add them to `TOOLS` and copy the pattern in `test_agent_tool.py`.

### 5.4 Run the tests
```powershell
cd day11
pip install -r requirements-dev.txt
pytest
```
All tests should pass. Useful variations: `pytest -v` (names), `pytest tests/test_api.py` (one file), `pytest -k i_dont_know` (tests with that word).

## 6. Lint with ruff (S1)

```powershell
cd day11
ruff check .
```
It must print `All checks passed!`. The rules are in `ruff.toml`: E4 (imports), E7 (statements), E9 (syntax errors) and F (pyflakes: unused imports and variables, undefined names).

| Problem ruff reports | Fix |
|----------------------|-----|
| `F401` imported but unused | delete the import, or run `ruff check . --fix` |
| `F841` local variable assigned but never used | delete the variable |
| `E402` import not at top of file | move the import to the top (or add `# noqa: E402` if a `sys.path` change must come first) |
| `E722` bare `except` | write `except Exception:` |

`ruff check . --fix` repairs the simple ones automatically. If I run `ruff check .` from the **repo root**, it also checks older days; fix those files the same way.

## 7. Run with Docker

### 7.1 What each Docker file does
| File | Purpose |
|------|---------|
| `Dockerfile` | Builds one image from `python:3.11-slim`. Installs `requirements.txt`, copies `app/`, `ui/`, `prompts/`, `documents/` and `data/`, downloads the embedding model at build time so start-up is fast, and by default starts the API. |
| `.dockerignore` | Keeps `.env` (my key), `.git`, `.venv`, caches, `chroma_db`, `tests` and docs out of the image. This makes the image smaller and keeps the secret key out. |
| `docker-compose.yml` | Starts two services from the same image: **api** (FastAPI on port 8000) and **ui** (Streamlit on port 8501). |

### 7.2 The two services
| Service | Command | Port | Notes |
|---------|---------|------|-------|
| `api` | rebuilds the search index from `documents/`, then runs `uvicorn app.main:app` | 8000 | reads the key from `.env`; has a health check on `/health`; the Chroma index is kept in a Docker volume |
| `ui` | `streamlit run ui/app.py` | 8501 | reaches the API at `http://api:8000` (the service name works as the address inside Docker); starts only after the API is healthy |

`./documents` and `./data` are shared with the containers, so I can edit documents without rebuilding, and thumbs up/down feedback from the UI is saved in my own `data/feedback.jsonl`.

### 7.3 Steps
1. **Install Docker Desktop** and start it. Wait until it says "Engine running". (On Windows it needs WSL 2, which Docker Desktop offers to set up.)
2. **Create the `.env` file with my key** (the API needs it for answers):
   ```powershell
   cd day11
   Copy-Item .env.example .env
   code .env
   ```
   Set `GROQ_API_KEY` to my real key and keep `GROQ_MODEL=llama-3.1-8b-instant`. Save the file.
3. **Start everything:**
   ```powershell
   docker compose up --build
   ```
   The first build takes a few minutes (packages and the embedding model are downloaded). Later starts take seconds.
4. **Open the apps** when the log shows the API and Streamlit are running:
   - UI: http://localhost:8501
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
5. **Stop:** press `Ctrl + C` in the terminal, then run `docker compose down`.

### 7.4 Useful commands
| Command | What it does |
|---------|--------------|
| `docker compose up --build` | build and start (use after changing code or requirements) |
| `docker compose up -d` | start in the background |
| `docker compose ps` | show the services and their health |
| `docker compose logs -f api` | follow the API log (use `ui` for the UI log) |
| `docker compose down` | stop and remove the containers |
| `docker compose down -v` | also delete the saved search index (it is rebuilt on the next start) |
| `docker compose build --no-cache` | rebuild the image from zero |

### 7.5 Expected result
`docker compose ps` should list both services as running, and the API as healthy:
```
NAME               SERVICE   STATUS                    PORTS
poshanguide-api    api       Up (healthy)              0.0.0.0:8000->8000/tcp
poshanguide-ui     ui        Up                        0.0.0.0:8501->8501/tcp
```
In the UI, the sidebar shows **Backend is running** (green). Ask a question and a "Sources" box appears under the answer.

### 7.6 Troubleshooting Docker
| Problem | Fix |
|---------|-----|
| `Cannot connect to the Docker daemon` / `docker: command not found` | Docker Desktop is not running or not installed. Start it and wait for "Engine running" |
| `port is already allocated` | Another program uses port 8000 or 8501. Close it, or change the left number in `ports:` (for example `"8001:8000"`) |
| UI shows "Backend not reachable" | The API is still starting (the first start needs about a minute). Wait, then refresh. Check `docker compose logs api` |
| `/ask` returns 502 mentioning the key or the model | Check `day11/.env`, then run `docker compose up -d --force-recreate api` |
| `No chunks found` in the API log | `documents/` is empty. Add documents and run `docker compose restart api` |
| `env file .env not found` (old Docker) | Create `.env` (step 2), or update Docker Desktop |
| Build fails while downloading packages | Check the internet connection and run again. `docker compose build --no-cache` retries from zero |
| I changed code but see the old behaviour | Run `docker compose up --build` |

## 8. Application flow

```
docker compose up
   ├── api  (port 8000)
   │     1. python -m app.vectorstore  -> chunks documents/, embeds, stores in the Chroma volume
   │     2. uvicorn app.main:app       -> /health, POST /ask, /chat, /search/semantic
   │           POST /ask: search chunks -> prompt -> LLM -> citations or "I don't know"
   │
   └── ui   (port 8501, starts when api is healthy)
         Streamlit app -> POST http://api:8000/ask  -> answer + sources + thumbs up/down
         My plate check -> colour bars vs ICMR-NIN My Plate (no API needed)
```

## 9. Git: commit and push

Run from the **repo root** (`sanjivani-sj-31-poshanguide`):
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
Add-Content .gitignore "`n.env`nchroma_db/`n__pycache__/`n.pytest_cache/`n.ruff_cache/"
git check-ignore -v day11/.env
git add -A day11
git status
git commit -m "Day 11: pytest tests, ruff check and Docker compose"
git push origin main
```
Checks before committing:
- `git check-ignore -v day11/.env` must print a line mentioning `.gitignore`.
- In `git status`, `day11/.env`, `day11/chroma_db/`, `__pycache__` and `.pytest_cache` must **not** be listed.
- `day11/Dockerfile`, `day11/docker-compose.yml`, `day11/.dockerignore`, `day11/tests/` and `day11/README.md` **must** be listed.

## 10. Troubleshooting (tests and lint)

| Problem | Fix |
|---------|-----|
| `pytest: command not found` | Activate `.venv`, then `pip install -r requirements-dev.txt` |
| `ModuleNotFoundError: No module named 'app'` | Run `pytest` from inside the `day11` folder (where `pytest.ini` is) |
| `ModuleNotFoundError: httpx` | `pip install httpx` (the API tests need it) |
| `ModuleNotFoundError: chromadb` | `pip install -r requirements.txt` |
| `ruff: command not found` | `pip install ruff` |
| A test about `/ask` fails with `RAG_MIN_SCORE` | Remove `RAG_MIN_SCORE` from the environment or `.env`, or set it to `0.20` |

## 11. Final checklist

- [ ] `pytest` passes (35 tests)
- [ ] `ruff check .` prints "All checks passed!"
- [ ] `docker compose up --build` starts both services
- [ ] UI opens at http://localhost:8501 and shows "Backend is running"
- [ ] API docs open at http://localhost:8000/docs
- [ ] `.env` and `chroma_db/` are NOT committed
- [ ] README has the "Run with Docker" section (section 7)
- [ ] Pushed to GitHub inside the `day11/` folder
