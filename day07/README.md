# Day 07 - PoshanGuide: Chunking, Embeddings, Chroma Vector Store and Semantic Search

## 1. The Task (as given)

> **S1:** `app/chunking.py` + `app/embed.py`: chunk your PoshanGuide documents keeping **source, page and title**; semantic search for your **10 questions**; record hits in `eval/search_results.md`.
> **S2:** `app/vectorstore.py` indexes all chunks into a **persistent Chroma collection**; `GET /search/semantic?q=`.

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| S1 | Chunk documents and keep source, page and title for every chunk | `chunking.py` | `app/` |
| S1 | Turn chunks and questions into embeddings | `embed.py` | `app/` |
| S1 | Semantic search for the 10 questions | `run_search.py` | `eval/` |
| S1 | Record the hits | `search_results.md` (written by `run_search.py`) | `eval/` |
| S2 | Index all chunks into a persistent Chroma collection | `vectorstore.py` (saved in the `chroma_db/` folder) | `app/` |
| S2 | `GET /search/semantic?q=` endpoint | `search.py`, connected in `main.py` | `app/` |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .gitignore                      <- contains the lines  .env  and  chroma_db/
├── docs/                           <- Day 05 files
├── day02/                          <- Day 02 files
├── day06/                          <- Day 06 files
└── day07/
    ├── README.md                   <- this file
    ├── requirements.txt            <- packages needed for Day 07
    ├── .env                        <- your real API key, LOCAL ONLY, never committed
    ├── .env.example                <- template without secrets, committed
    ├── app/
    │   ├── __init__.py             <- empty file, makes app a package
    │   ├── main.py                 <- FastAPI app, connects all routers
    │   ├── chunking.py             <- loads documents and splits them into chunks
    │   ├── embed.py                <- text -> embedding vectors
    │   ├── vectorstore.py          <- Chroma index + semantic_search()
    │   ├── search.py               <- GET /search/semantic and POST /search/reindex
    │   ├── llm.py                  <- Day 06 LLM wrapper (unchanged)
    │   └── chat.py                 <- Day 06 POST /chat (unchanged)
    ├── prompts/                    <- Day 06 prompts (unchanged)
    │   ├── system.md
    │   ├── task_v1.md
    │   └── task_v2.md
    ├── documents/                  <- PUT YOUR PoshanGuide DOCUMENTS HERE
    │   ├── README.txt
    │   ├── infant_feeding.md       <- SAMPLE, replace with real documents
    │   ├── maternal_nutrition.md   <- SAMPLE
    │   ├── child_nutrition.md      <- SAMPLE
    │   └── common_foods.md         <- SAMPLE
    ├── eval/
    │   ├── questions.txt           <- the 10 questions
    │   ├── run_search.py           <- runs the search and writes the results file
    │   └── search_results.md       <- recorded hits + my analysis
    └── chroma_db/                  <- created automatically, NOT committed
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md`, `requirements.txt`, `.env`, `.env.example` | `day07/` |
| `main.py`, `chunking.py`, `embed.py`, `vectorstore.py`, `search.py`, `llm.py`, `chat.py`, `__init__.py` | `day07/app/` |
| `system.md`, `task_v1.md`, `task_v2.md` | `day07/prompts/` |
| my PoshanGuide documents (PDF, md, txt, json) | `day07/documents/` |
| `questions.txt`, `run_search.py`, `search_results.md` | `day07/eval/` |

Important: file names must be exact. A downloaded file named `chunking (1).py` or `questions (1).txt` must be renamed.

## 5. How the application works (flow)

### 5.1 Building the index (done once, or after documents change)
```
documents/  (.pdf  .md  .txt  .json)
   -> chunking.py     read every file page by page
                      split each page into chunks of about 700 characters
                      (120 characters overlap between neighbouring chunks)
                      every chunk keeps: source, page, title, chunk_index
   -> embed.py        turn each chunk into a vector of numbers
                      (all-MiniLM-L6-v2, runs on my own computer)
   -> vectorstore.py  store text + vector + metadata in a Chroma collection
                      saved on disk in the chroma_db/ folder
```

### 5.2 Searching
```
GET /search/semantic?q=iron rich foods for toddlers&k=5
   -> search.py checks the input (q at least 2 characters, k between 1 and 20)
   -> vectorstore.semantic_search():
        - if the index is empty, build it automatically
        - embed the question with the same model
        - Chroma returns the k closest chunks (cosine similarity)
   -> JSON: rank, score, text, source, page, title, chunk_id
```

## 6. Key ideas (in my own words)

- **Chunking:** a whole document is too big to search precisely. Cutting it into small pieces lets the search point to the exact paragraph that answers a question.
- **Overlap:** the last part of a chunk is repeated at the start of the next one, so a sentence at the border does not lose its meaning.
- **Metadata (source, page, title):** stored with every chunk so any result can say where it came from. This is needed later to show sources in answers.
- **Embedding:** a text turned into a list of numbers. Texts with similar meaning get similar numbers, even if they use different words. "Foods rich in iron" can match a chunk about "dal, ragi and green leafy vegetables".
- **Semantic search vs keyword search:** keyword search needs the same words (the `/ask` endpoint works this way). Semantic search compares meaning.
- **Persistent Chroma:** the index is saved on disk, so it does not need to be rebuilt every time the app starts.
- **Score:** cosine similarity between question and chunk. Higher means closer in meaning. A low score for every hit (for example Q6) is a sign the documents do not contain the answer.

## 7. Each file explained

### 7.1 `app/chunking.py`
- `Chunk` is a small data class with: `id`, `text`, `source`, `page`, `title`, `chunk_index`.
- `load_documents()` reads every file in `documents/` and returns one entry per page.
  - **PDF:** real page numbers (uses `pypdf`). Title comes from the PDF metadata, otherwise from the file name.
  - **.md / .txt:** pages are separated by a line `<!-- page -->`. Title is the first `# heading`.
  - **.json:** each entry in the list becomes one page.
  - Files that start with `_` or `.`, files named README, and other file types are skipped.
- `chunk_text()` packs paragraphs into chunks of up to 700 characters (`MAX_CHARS`) with 120 characters of overlap (`OVERLAP`). A very long paragraph is split at sentence ends.
- `chunk_documents()` returns all chunks. The chunk id looks like `child_nutrition_md-p1-c0` (file, page, chunk number).
- Quick test: `python -m app.chunking` prints how many documents and chunks were found.

### 7.2 `app/embed.py`
- Uses Chroma's built-in `DefaultEmbeddingFunction`, which is the model **all-MiniLM-L6-v2** (ONNX).
- Runs locally, needs **no API key**. The first run downloads about 80 MB once.
- `embed_texts(texts)` embeds many chunks in batches of 64. `embed_query(query)` embeds one question.
- The same model must be used for chunks and questions, so both come from this one file.

### 7.3 `app/vectorstore.py`
- `get_client()` opens a **PersistentClient** that stores data in `chroma_db/`.
- `get_collection()` returns the collection named `poshanguide`, using cosine distance.
- `index_all(reset=True)` chunks all documents, embeds them and stores them with `upsert` in batches of 200. Each chunk is stored with its text, vector and metadata (`source`, `page`, `title`, `chunk_index`). With `reset=True` the old collection is deleted first so the index always matches the documents.
- `semantic_search(q, k=5)` embeds the question, asks Chroma for the closest chunks and returns a list of hits. Score is `1 - distance`. If the collection is empty it builds the index first.
- Build from the terminal: `python -m app.vectorstore`

### 7.4 `app/search.py`
- `GET /search/semantic` with `q` (required, at least 2 characters) and `k` (default 5, between 1 and 20).
- `POST /search/reindex` rebuilds the whole index from `documents/`.
- If `documents/` has nothing usable, the API returns **503** with a clear message.

### 7.5 `app/main.py`
- Creates the FastAPI app and connects the chat router (Day 06) and the search router (Day 07).
- Keeps `GET /`, `GET /health` and `GET /ask` (keyword answers). It looks for `nutrition.json` in `day07/data/`, then `day06/data/`, then `day02/data/`.

### 7.6 `eval/run_search.py`
- Reads every question in `eval/questions.txt`, runs semantic search (top 3 hits each) and writes `eval/search_results.md`.
- The output has: a header (date, model, number of chunks), a summary table with the top hit per question, a table of all hits per question, and an analysis section to fill in.

### 7.7 Day 06 files kept in this folder
`llm.py`, `chat.py` and `prompts/` are copied from Day 06 unchanged, so `POST /chat` still works in Day 07.

## 8. Documents

- Put my real PoshanGuide documents in `day07/documents/`. Supported: **PDF, .md, .txt, .json**.
- The 4 `.md` files included are **samples** (marked `(SAMPLE)` in their titles) so the project runs on a fresh install. Replace them or delete them once my real documents are added.
- For `.md` or `.txt` files, mark page breaks with a line `<!-- page -->`. Without it the whole file counts as page 1.
- After adding or changing documents, rebuild the index:
  ```powershell
  python -m app.vectorstore
  ```
  (or call `POST /search/reindex`).

## 9. The search API

### Request
```
GET /search/semantic?q=iron rich foods for toddlers&k=3
```

| Parameter | Required | Meaning |
|-----------|----------|---------|
| `q` | yes | The question, at least 2 characters |
| `k` | no | Number of chunks to return, 1 to 20, default 5 |

### Response (example, real numbers will differ)
```json
{
  "q": "iron rich foods for toddlers",
  "k": 3,
  "count": 3,
  "hits": [
    {
      "rank": 1,
      "score": 0.61,
      "text": "Growing children need protein in every meal. ...",
      "source": "child_nutrition.md",
      "page": 1,
      "title": "Nutrition for Young Children (SAMPLE)",
      "chunk_id": "child_nutrition_md-p1-c0"
    }
  ]
}
```

### Error responses
| Code | Meaning |
|------|---------|
| 422 | Invalid input, for example `q` is missing or `k` is outside 1 to 20 |
| 503 | No chunks could be built, because `documents/` is empty or has no supported files |

### All endpoints in this app
| Endpoint | Purpose |
|----------|---------|
| `GET /` | Welcome message |
| `GET /health` | Health check and number of keyword data entries |
| `GET /ask?question=` | Keyword answer from `nutrition.json` (Day 05) |
| `POST /chat` | LLM answer with `answer`, `confidence`, `follow_up` (Day 06) |
| `GET /search/semantic?q=&k=` | Semantic search over document chunks (Day 07) |
| `POST /search/reindex` | Rebuild the Chroma index (Day 07) |

## 10. Setup and run (PowerShell)

Run from the **repo root** first, then from inside `day07`:

```powershell
# 1. put the files in day07 (only if you downloaded the zip)
Expand-Archive -Path "$env:USERPROFILE\Downloads\poshanguide_day07.zip" -DestinationPath day07 -Force

# 2. copy the key file from Day 06 (stays on my computer)
Copy-Item day06\.env day07\.env

# 3. go into the folder and install the packages
cd day07
pip install -r requirements.txt

# 4. check the chunking
python -m app.chunking

# 5. build the Chroma index (first run downloads about 80 MB)
python -m app.vectorstore

# 6. start the app
uvicorn app.main:app --reload
```

Packages in `requirements.txt`: `fastapi`, `uvicorn[standard]`, `requests`, `python-dotenv`, `chromadb`, `pypdf`.

Then open http://127.0.0.1:8000/docs and try:
- `GET /search/semantic` with `q = iron rich foods for toddlers`
- `GET /search/semantic` with `q = what to give a baby at 6 months` and `k = 3`
- `POST /search/reindex`

Always run `uvicorn` and `python -m ...` from inside `day07`, not from inside `app`, otherwise Python cannot find the `app` package. Use Python 3.11 or 3.12 if the `chromadb` install fails.

## 11. Record the hits for the 10 questions (S1 deliverable)

```powershell
cd day07
python eval/run_search.py
```

The script searches all 10 questions and writes the top 3 hits (source, page, title, score, snippet) to `eval/search_results.md`. Then I open that file and:
1. Fill the **Relevant? (Y/N)** column by reading each top hit and deciding if it really answers the question.
2. Write the **My analysis** section in my own words.

### The 10 questions
1. What should a pregnant woman eat in the second trimester?
2. Which foods are rich in iron for a 2-year-old?
3. How much protein does a 10-year-old need daily?
4. What is a good weaning food at 6 months?
5. Is jaggery better than sugar for anaemia?
6. Which nutritionist near my village is free this week? (data cannot answer)
7. What can I give my child instead of milk if he is lactose intolerant?
8. How many calories are in one roti?
9. Which vegetables are cheap and rich in vitamin A?
10. What are signs of malnutrition in a toddler?

Replace these in `eval/questions.txt` with my own 10 questions from Day 05 if they differ.

### What to look for in the analysis
- Which questions got a clearly correct top hit, and what the score was.
- Which questions were weak or missed, and why (for example the information is missing from the documents, or the chunk is too big or too small).
- **Q6:** semantic search always returns the closest chunks, even when nothing is relevant. Note what it returned and how low the scores were. This shows why a minimum score or an "I cannot answer" rule is needed later.
- One thing I would change: chunk size, overlap, more documents, or a score cut-off.

## 12. Git: commit and push

Run from the **repo root** (`sanjivani-sj-31-poshanguide`):

```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
Add-Content .gitignore "`nchroma_db/"
git check-ignore -v day07/.env
git add -A day07 .gitignore
git status
git commit -m "Day 07: chunking, embeddings, Chroma vectorstore, semantic search"
git push origin main
```

Checks before committing:
- `git check-ignore -v day07/.env` must print a line mentioning `.gitignore`.
- In `git status`, `day07/.env` and `day07/chroma_db/` must **not** be listed.
- `day07/.env.example`, `day07/documents/`, `day07/eval/` and `day07/app/` **must** be listed.

After pushing, open the repo on GitHub and check the `day07/` folder.

## 13. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named app` | Run commands from the `day07` folder, not from inside `app` |
| `No module named chromadb` | Activate the virtual environment, then `pip install -r requirements.txt` |
| Install of `chromadb` fails on Windows | Use Python 3.11 or 3.12 and read the full error message |
| First run is very slow | The embedding model (about 80 MB) is downloading, this happens once |
| Model download fails | Check the internet connection or proxy, then run again |
| `No chunks found` / 503 error | `documents/` is empty or has only unsupported files |
| Results do not match my new documents | Rebuild with `python -m app.vectorstore` or `POST /search/reindex` |
| All pages show as page 1 | The `.md` or `.txt` file has no `<!-- page -->` lines |
| `No module named app.chat` | `chat.py` and `llm.py` are missing from `day07/app/` |
| `.env` or `chroma_db/` shows in `git status` | Do not commit. Fix `.gitignore` and check again |
| File names like `run_search (1).py` | Rename them to the exact names in section 3 |

## 14. Final checklist

- [ ] My real PoshanGuide documents are in `documents/` (or the samples are kept)
- [ ] `chunking.py` keeps source, page and title for every chunk
- [ ] `embed.py` and `vectorstore.py` work, and `chroma_db/` is created
- [ ] `GET /search/semantic?q=` returns hits in `/docs`
- [ ] `eval/questions.txt` has my 10 questions
- [ ] `eval/search_results.md` is generated and the analysis is in my own words
- [ ] `.env` and `chroma_db/` are NOT committed
- [ ] Everything is pushed to GitHub inside the `day07/` folder