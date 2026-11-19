# Day 08 - PoshanGuide: RAG Answers with Citations, "I don't know", and Evaluation

## 1. The Task (as given)

> **S1:** `app/rag.py` + `POST /ask`: answer PoshanGuide questions from retrieved chunks **with citations**; must say **"I don't know"** for Q6.
> **S2:** `eval/eval_set.json` (**15 rows**) + `eval/run_eval.py`; run **2 configs (chunk size / top-k)** and put the **winner table in README**.

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| S1 | Answer from retrieved chunks | `rag.py` | `app/` |
| S1 | `POST /ask` endpoint | `ask.py`, connected in `main.py` | `app/` |
| S1 | Citations (source, page, title) in every answer | built in `rag.py`, returned by `ask.py` | `app/` |
| S1 | Say "I don't know" for Q6 | score check + prompt rule + citation check in `rag.py`; prompts in `rag_system.md`, `rag_task.md` | `app/`, `prompts/` |
| S2 | Evaluation set with 15 rows | `eval_set.json` | `eval/` |
| S2 | Script that runs the evaluation | `run_eval.py` | `eval/` |
| S2 | 2 configs (chunk size / top-k) | `CONFIGS` list inside `run_eval.py` | `eval/` |
| S2 | Winner table in this README | section 10 (filled automatically by `run_eval.py`) | `README.md` |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .gitignore                      <- contains the lines  .env  and  chroma_db/
├── docs/                           <- Day 05 files
├── day02/ ... day07/               <- earlier days
└── day08/
    ├── README.md                   <- this file (winner table inside)
    ├── requirements.txt            <- packages
    ├── .env                        <- your real API key, LOCAL ONLY, never committed
    ├── .env.example                <- template without secrets, committed
    ├── app/
    │   ├── __init__.py             <- empty file, makes app a package
    │   ├── main.py                 <- FastAPI app, connects all routers
    │   ├── rag.py                  <- NEW  retrieve + prompt + citations + "I don't know"
    │   ├── ask.py                  <- NEW  POST /ask
    │   ├── chunking.py             <- Day 07, now with configurable chunk size
    │   ├── embed.py                <- Day 07, text -> embeddings
    │   ├── vectorstore.py          <- Day 07, one Chroma collection per chunk size
    │   ├── search.py               <- Day 07, GET /search/semantic
    │   ├── llm.py                  <- Day 06, Groq / Gemini wrapper
    │   └── chat.py                 <- Day 06, POST /chat
    ├── prompts/
    │   ├── rag_system.md           <- NEW  rules for answering only from context
    │   ├── rag_task.md             <- NEW  context + question + JSON answer format
    │   ├── system.md               <- Day 06 (used by /chat)
    │   ├── task_v1.md              <- Day 06
    │   └── task_v2.md              <- Day 06
    ├── documents/                  <- PUT YOUR PoshanGuide DOCUMENTS HERE
    │   ├── infant_feeding.md       <- SAMPLE, replace with real documents
    │   ├── maternal_nutrition.md   <- SAMPLE
    │   ├── child_nutrition.md      <- SAMPLE
    │   └── common_foods.md         <- SAMPLE
    ├── eval/
    │   ├── eval_set.json           <- NEW  15 evaluation rows
    │   ├── run_eval.py             <- NEW  runs 2 configs, writes results + README table
    │   └── eval_results.md         <- NEW  all answers and pass/fail (generated)
    └── chroma_db/                  <- created automatically, NOT committed
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md`, `requirements.txt`, `.env`, `.env.example` | `day08/` |
| `main.py`, `rag.py`, `ask.py`, `chunking.py`, `embed.py`, `vectorstore.py`, `search.py`, `llm.py`, `chat.py`, `__init__.py` | `day08/app/` |
| `rag_system.md`, `rag_task.md`, `system.md`, `task_v1.md`, `task_v2.md` | `day08/prompts/` |
| my PoshanGuide documents (PDF, md, txt, json) | `day08/documents/` |
| `eval_set.json`, `run_eval.py`, `eval_results.md` | `day08/eval/` |

Important: file names must be exact. A downloaded file named `rag (1).py` must be renamed to `rag.py`.

## 5. How the application works (flow)

```
POST /ask  {"question": "...", "top_k": 4}
   -> ask.py        checks the input (question at least 3 characters, top_k 1 to 10)
   -> rag.py
        1. semantic_search()     get the top_k closest chunks from Chroma (Day 07)
        2. score filter          chunks below the minimum score (0.20) are dropped
                                 nothing left -> "I don't know" (the LLM is not even called)
        3. build prompt          numbered passages [1] [2] ... with source, page, title
                                 + rules from prompts/rag_system.md
        4. call_llm()            temperature 0, reply must be JSON
                                 {"answerable": ..., "answer": "... [1]", "sources": [1]}
        5. validate              not answerable, empty answer, or no valid citation
                                 -> "I don't know"
        6. build citations       source, page, title, score, snippet for each passage used
   -> JSON: question, answer, answerable, citations
```

### Three layers that make the system say "I don't know" (Q6)
1. **Score filter:** if no retrieved chunk is close enough to the question, the answer is "I don't know" without calling the LLM.
2. **Prompt rule:** the model is told to answer only from the passages and to set `answerable` to `false` for local doctors, prices, medicine doses and anything the passages do not cover.
3. **Citation check:** an answer that does not cite at least one real passage is replaced with "I don't know". This stops confident answers made from the model's own memory.

## 6. Each new file explained

### 6.1 `app/rag.py`
- `answer_question(question, top_k=4, max_chars=700, min_score=0.20)` is the whole pipeline.
- `IDK_ANSWER` is the fixed reply: *"I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre."*
- `_build_context()` writes the passages as `[1] (source: file, page N, title: ...)` followed by the text.
- Citations are built from the passage numbers the model used. If the model forgets the `sources` list, the numbers written as `[n]` inside the answer are used.
- `RAG_MIN_SCORE` can be changed in `.env` if the filter is too strict or too loose.
- Returns extra fields (`retrieved`, `config`) that `run_eval.py` uses for scoring.

### 6.2 `app/ask.py`
- `POST /ask` with `question` and optional `top_k`.
- Response model: `question`, `answer`, `answerable` (true/false), `citations` (list).
- Provider problems return **502** with a clear message.

### 6.3 `app/main.py`
- Connects the ask, chat and search routers.
- The old Day 05 `GET /ask` (keyword answers) is kept but marked deprecated. The new `POST /ask` is the real endpoint. Both can share the same path because the methods differ.

### 6.4 Changes in Day 07 files
- `chunking.py`: `chunk_documents(max_chars=..., overlap=...)` so chunk size can be tested.
- `vectorstore.py`: `index_all(max_chars=...)` and `semantic_search(q, k, max_chars)`. Each chunk size has its own Chroma collection (`poshanguide`, `poshanguide_c400`, ...), so two configs can be compared without overwriting each other.

### 6.5 `prompts/rag_system.md` and `prompts/rag_task.md`
- `rag_system.md`: answer only from numbered passages, no outside knowledge, 2 to 4 simple sentences, cite with `[n]`, no diagnosis or medicine doses, say "I don't know" when the passages do not contain the answer, reply in one JSON object.
- `rag_task.md`: the template with `{context}` and `{question}` and the exact JSON shape (`answerable`, `answer`, `sources`).

## 7. The POST /ask API

### Request
```json
{
  "question": "Which foods are rich in iron for a 2-year-old?",
  "top_k": 4
}
```

### Response when the documents have the answer (example)
```json
{
  "question": "Which foods are rich in iron for a 2-year-old?",
  "answer": "Give dal, green leafy vegetables, ragi, dates and eggs [1]. A squeeze of lemon on the meal helps the body absorb iron [1].",
  "answerable": true,
  "citations": [
    {
      "id": 1,
      "source": "child_nutrition.md",
      "page": 1,
      "title": "Nutrition for Young Children (SAMPLE)",
      "score": 0.58,
      "snippet": "Growing children need protein in every meal. ..."
    }
  ]
}
```
(Real answers and scores will differ.)

### Response for Q6 (the documents cannot answer)
```json
{
  "question": "Which nutritionist near my village is free this week?",
  "answer": "I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre.",
  "answerable": false,
  "citations": []
}
```

### Error responses
| Code | Meaning |
|------|---------|
| 422 | Invalid input, for example the question is too short or `top_k` is outside 1 to 10 |
| 502 | LLM provider problem: missing key, network error, or the model did not return valid JSON |

### All endpoints in this app
| Endpoint | Purpose |
|----------|---------|
| `GET /` | Welcome message |
| `GET /health` | Health check |
| `GET /ask?question=` | OLD keyword answer (Day 05, deprecated) |
| `POST /ask` | **RAG answer with citations or "I don't know" (Day 08)** |
| `POST /chat` | LLM answer with `answer`, `confidence`, `follow_up` (Day 06) |
| `GET /search/semantic?q=&k=` | Semantic search over chunks (Day 07) |
| `POST /search/reindex` | Rebuild the Chroma index (Day 07) |

## 8. The evaluation (S2)

### 8.1 `eval/eval_set.json` - 15 rows
Each row has:

| Field | Meaning |
|-------|---------|
| `id` | `e01` ... `e15` |
| `question` | the user question |
| `answerable` | `true` if the documents contain the answer, `false` if the correct reply is "I don't know" |
| `expected_source` | the document file that should be retrieved and cited (`null` for unanswerable rows) |
| `expected_keywords` | words of which at least one must appear in a correct answer (empty for unanswerable rows) |

The set has **12 answerable** and **3 unanswerable** rows (Q6 nutritionist near my village, price of tomatoes today, paracetamol dose for a child). The rows match the 4 sample documents. **If I replace the sample documents with my real ones, I must update `expected_source` and `expected_keywords`, and keep 15 rows.**

### 8.2 The 2 configurations (in `run_eval.py`)
| Config | Chunk size | Top-k | Idea |
|--------|-----------|-------|------|
| A | 400 characters | 3 | small, precise chunks, fewer of them |
| B | 700 characters | 5 | bigger chunks with more context, more of them |

The list can be edited at the top of `run_eval.py` (`CONFIGS`). Both configs use the same documents, the same model and temperature 0, so only chunk size and top-k change.

### 8.3 How a row passes
- **Answerable row:** the answer is not "I don't know", it cites the expected source file, and it contains at least one expected keyword.
- **Unanswerable row:** the answer must be "I don't know".

### 8.4 Metrics in the table
| Column | Meaning |
|--------|---------|
| Pass | rows passed out of 15 (the main score) |
| Retrieval hit | answerable rows where the expected file was among the retrieved chunks |
| Citation ok | answerable rows where the answer cited the expected file |
| Correct "I don't know" | unanswerable rows answered with "I don't know" (good) |
| False refusals | answerable rows wrongly answered with "I don't know" (bad) |
| Avg sec/question | average time per question |

**Winner rule:** most rows passed; if tied, more retrieval hits; if still tied, the smaller top-k (cheaper).

### 8.5 Run it
```powershell
cd day08
python eval/run_eval.py
```
It builds one index per chunk size, asks all 15 questions for both configs (about 30 LLM calls, roughly 1 to 3 minutes), writes `eval/eval_results.md` with every answer, and **fills the winner table in section 10 of this README automatically**.

## 9. Setup and run (PowerShell)

```powershell
# 1. from the repo root: put the files in day08 (only if you downloaded the zip)
Expand-Archive -Path "$env:USERPROFILE\Downloads\poshanguide_day08.zip" -DestinationPath day08 -Force

# 2. create .env (needed: /ask and the evaluation call the LLM)
Copy-Item day08\.env.example day08\.env
code day08\.env
```
Paste a real key in `.env`:
```
LLM_PROVIDER=groq
GROQ_API_KEY=your_real_key_here
```
Free key: console.groq.com (or aistudio.google.com/apikey for Gemini).

```powershell
# 3. install packages and build the index
cd day08
pip install -r requirements.txt
python -m app.vectorstore

# 4. start the app
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs, choose **POST /ask**, click **Try it out**, and test:
- `Which foods are rich in iron for a 2-year-old?` -> answer with citations
- `Which nutritionist near my village is free this week?` -> "I don't know" (Q6)

```powershell
# 5. run the evaluation (fills the table below)
python eval/run_eval.py
```

Always run commands from inside `day08`, not from inside `app`.

## 10. Evaluation results: winner table

<!-- EVAL_TABLE_START -->
| Config | Chunk size | Top-k | Chunks | Pass | Retrieval hit | Citation ok | Correct "I don't know" | False refusals | Avg sec/question |
|--------|-----------|-------|--------|------|---------------|-------------|------------------------|----------------|------------------|
| A **(winner)** | 400 | 3 | 20 | 14/15 (93%) | 12/12 | 12/12 | 3/3 | 0/12 | 2.4 |
| B | 700 | 5 | 10 | 14/15 (93%) | 11/12 | 11/12 | 3/3 | 0/12 | 8.2 |

**Winner: Config A** (chunk size 400, top-k 3) with 14/15 questions passed.

_Run on 2026-11-19._
<!-- EVAL_TABLE_END -->

### My analysis (EDIT: write in your own words after running)
- **Which config won and why do I think so?** [EDIT]
- **Which questions failed, and what was the reason (retrieval, citation, keyword check, wrong "I don't know")?** [EDIT]
- **Did Q6 get "I don't know" in both configs?** [EDIT]
- **What would I change next (chunk size, top-k, minimum score, more documents)?** [EDIT]

## 11. Git: commit and push

Run from the **repo root** (`sanjivani-sj-31-poshanguide`):

```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
Add-Content .gitignore "`nchroma_db/"
git check-ignore -v day08/.env
git add -A day08 .gitignore
git status
git commit -m "Day 08: RAG with citations, POST /ask, eval set and winner table"
git push origin main
```

Checks before committing:
- `git check-ignore -v day08/.env` must print a line mentioning `.gitignore`.
- In `git status`, `day08/.env` and `day08/chroma_db/` must **not** be listed.
- `day08/.env.example`, `day08/app/`, `day08/eval/` and `day08/README.md` **must** be listed.

## 12. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named app` | Run commands from the `day08` folder, not from inside `app` |
| `GROQ_API_KEY is missing` (502) | Create `day08/.env` and paste the key; check `LLM_PROVIDER` |
| Every answer is "I don't know" | Lower the filter: add `RAG_MIN_SCORE=0.10` to `.env`, or check that `python -m app.vectorstore` created the index |
| Q6 gets a real answer | Raise `RAG_MIN_SCORE` (for example 0.30) and read the retrieved text in `eval/eval_results.md` |
| Many `ERROR` rows in the evaluation | Provider rate limit: wait a minute and run again, or raise `PAUSE` in `run_eval.py` |
| Table in README not updated | The `EVAL_TABLE_START` / `EVAL_TABLE_END` lines were deleted: put them back or paste the table by hand |
| Changed documents but results look old | Run `python -m app.vectorstore`; `run_eval.py` rebuilds its own indexes every time |
| `No module named chromadb` | Activate the virtual environment, then `pip install -r requirements.txt` |
| `.env` or `chroma_db/` shows in `git status` | Do not commit. Fix `.gitignore` and check again |
| File names like `rag (1).py` | Rename them to the exact names in section 3 |

## 13. Final checklist

- [ ] `app/rag.py` answers only from retrieved chunks and returns citations
- [ ] `POST /ask` works in `/docs`
- [ ] Q6 returns "I don't know" with no citations
- [ ] `eval/eval_set.json` has 15 rows that match my documents
- [ ] `python eval/run_eval.py` ran for both configs
- [ ] Winner table is in section 10 and my analysis is written in my own words
- [ ] `.env` and `chroma_db/` are NOT committed
- [ ] Everything is pushed to GitHub inside the `day08/` folder