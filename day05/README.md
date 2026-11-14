# Day 05 – PoshanGuide: How LLMs Work + Checkpoint 1

## 1. The Task (as given)
> `docs/how_llms_work.md` in your own words with 1 diagram. Add 10 real PoshanGuide user questions (start with your card's 6; Q6 must be one your data cannot answer). **Checkpoint 1:** run your FastAPI, show `/docs`, explain one function. Tag `checkpoint-1`.

## 2. What the task includes
| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| 1 | Explain how LLMs work in own words | `how_llms_work.md` | `docs/` |
| 2 | Include 1 diagram | Mermaid diagram inside `how_llms_work.md` | `docs/` |
| 3 | 10 real PoshanGuide user questions | Question table inside `how_llms_work.md` | `docs/` |
| 4 | Q1–Q6 come from my card | First 6 rows of the table | `docs/` |
| 5 | Q6 must be unanswerable by my data | Row 6 marked "No" with reason | `docs/` |
| 6 | Run FastAPI and show `/docs` | Screenshot `fastapi-docs.png` | `docs/screenshots/` |
| 7 | Explain one function | Section in `checkpoint-1.md` | `docs/` |
| 8 | Tag `checkpoint-1` | Git tag | Git (see section 6) |

## 3. Folder structure (where every file is stored)

```
day05/
├── README.md                      <- this file (project root)
├── GIT_STEPS.md                   <- commit + tag commands
├── requirements.txt               <- fastapi, uvicorn
├── .gitignore
├── app/
│   ├── __init__.py                <- my existing file
│   └── main.py                    <- my existing FastAPI app
├── data/                          <- my PoshanGuide data (csv / json)
└── docs/
    ├── how_llms_work.md           <- LLM explanation + diagram + 10 questions
    ├── checkpoint-1.md            <- FastAPI proof + one function explained
    └── screenshots/
        └── fastapi-docs.png       <- screenshot of http://127.0.0.1:8000/docs
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md` | `day05/` |
| `GIT_STEPS.md` | `day05/` |
| `requirements.txt` | `day05/` |
| `.gitignore` | `day05/` |
| `main.py`, `__init__.py` | `day05/app/` |
| data files | `day05/data/` |
| `how_llms_work.md` | `day05/docs/` |
| `checkpoint-1.md` | `day05/docs/` |
| `fastapi-docs.png` | `day05/docs/screenshots/` |

## 5. Data in this task

### 5.1 The 10 PoshanGuide user questions
(Full table with answers is in `docs/how_llms_work.md`.)

| # | Question | Answerable from data? |
|---|----------|-----------------------|
| 1 | What should a pregnant woman eat in the second trimester? | Yes |
| 2 | Which foods are rich in iron for a 2-year-old? | Yes |
| 3 | How much protein does a 10-year-old need daily? | Yes |
| 4 | What is a good weaning food at 6 months? | Yes |
| 5 | Is jaggery better than sugar for anaemia? | Partly |
| 6 | Which nutritionist near my village is free this week? | **No** – no live local data |
| 7 | What can I give my child instead of milk if he is lactose intolerant? | Yes |
| 8 | How many calories are in one roti? | Yes |
| 9 | Which vegetables are cheap and rich in vitamin A? | Partly |
| 10 | What are signs of malnutrition in a toddler? | Yes |

> Q1–Q6 must be replaced with the 6 questions from my own card. Q6 stays as the one my data cannot answer.

### 5.2 The diagram
One Mermaid flowchart in `how_llms_work.md`:
User question → Tokens → Embeddings → Transformer (attention) → Next-token probability → Pick token → (repeat) → Final answer.

### 5.3 LLM topics explained in `how_llms_work.md`
Tokens, embeddings, attention/transformer, next-token prediction, training vs inference, hallucination, and why PoshanGuide answers from its own data.

## 6. Application flow

```
User question
   -> FastAPI endpoint (app/main.py)
   -> Search / match in data/
   -> Data found?  yes -> build answer from data
                   no  -> "I can't answer this from my data"  (Q6 case)
   -> JSON response (viewable at /docs)
```

## 7. Methods / functions (my main.py)
| Function | File | Purpose |
|----------|------|---------|
| `[EDIT]` endpoint function | `app/main.py` | Receives the question and returns the answer |
| `[EDIT]` helper function | `app/main.py` | e.g. loads data / searches data |

The one function chosen for Checkpoint 1 is explained in `docs/checkpoint-1.md`.

## 8. How to run (Checkpoint 1)

Open the terminal in the `day05` folder (the project root, not inside `app`):
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
1. Open http://127.0.0.1:8000/docs
2. Try one endpoint with "Try it out"
3. Take a screenshot and save it as `docs/screenshots/fastapi-docs.png`

## 9. Git tag (submission)
```bash
git add .
git commit -m "Day 05: how_llms_work.md + checkpoint-1"
git tag checkpoint-1
git push origin main
git push origin checkpoint-1
```
Check with `git tag` – it should list `checkpoint-1`.

## 10. Final checklist
- [ ] `docs/how_llms_work.md` written in my own words
- [ ] 1 diagram included
- [ ] 10 questions added (Q1–Q6 from my card)
- [ ] Q6 is a question my data cannot answer
- [ ] FastAPI runs without errors
- [ ] `/docs` screenshot saved in `docs/screenshots/`
- [ ] One function explained in `docs/checkpoint-1.md`
- [ ] Tag `checkpoint-1` created and pushed