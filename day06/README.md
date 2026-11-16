# PoshanGuide: Day 06 (LLM API + Prompt Engineering)

> Student: Dhangar Gauri Yogesh
> Project: PoshanGuide, a nutrition guidance assistant based on the ICMR-NIN Dietary Guidelines for Indians (DGI 2024)
> Day 06 theme: connect the project to a real LLM API and learn to control it with prompts

---

## 1. What is the Day 06 task?

Until Day 05, PoshanGuide worked with **fixed data and rules**: it downloaded the DGI document (Day 03/04), turned it into `records.json`, and searched it. It could not *talk*.

On Day 06 the task is to make PoshanGuide **answer questions in natural language** by calling an LLM (a large language model) through an API. The task has two parts.

**Part S1: Build the chat feature**
- `app/llm.py`: a small *provider wrapper* that talks to an LLM service (Groq or Gemini). I use **Groq**.
- `POST /chat`: an API endpoint that receives a user question and returns the answer.
- A **PoshanGuide system prompt**, so the model behaves like a nutrition guide and not like a general chatbot.
- `.env` holds the secret API key and is **never committed**. `.env.example` is a template with no real key and **is committed**.

**Part S2: Engineer and compare prompts**
- A `prompts/` folder with 1 system prompt and 2 task prompts (**v1** and **v2**).
- `/chat` must return structured **JSON** with three fields: `answer`, `confidence`, `follow_up`.
- `eval/prompt_compare.md`: I run the same **10 PoshanGuide questions** through both prompt versions, save the real answers in a table, and write **my own analysis** (which prompt is better, how Q6 was handled, how reliable the confidence values were).

---

## 2. Why is this required? Why do we need it?

| Need | Reason |
|---|---|
| **LLM API** | A normal program can only return text it already has. An LLM can read the user's question and write a clear, friendly answer. |
| **Provider wrapper (`llm.py`)** | All API-specific code lives in one file. If I switch from Groq to Gemini, only this file changes and the rest of the app stays the same. |
| **System prompt** | Without it the model may answer anything, in any style. The system prompt fixes its role: a careful nutrition guide that follows the DGI. |
| **Task prompts v1/v2** | The same question can give very different answers depending on how the instruction is written. Two versions let me measure the difference instead of guessing. |
| **Structured JSON** | A program cannot reliably use free text. With `answer`, `confidence` and `follow_up`, a website or app can show the answer, warn the user when confidence is low, and suggest the next question. |
| **`.env` + `.env.example`** | An API key is a password. If it reaches GitHub, anyone can use it. The real key stays on my computer in `.env`; the template shows others which variables they need. |
| **Prompt comparison file** | It is the evidence: real answers, side by side, with my judgement. This is how prompt engineering is done in real projects (evaluation, not opinion). |
| **Q6 handling** | One of the 10 questions is a hard case (for example unclear, risky or outside the DGI). It tests whether the assistant stays safe and honest instead of making things up. |

---

## 3. Flow: how a question travels through the system

```
 User (browser / PowerShell / app)
        |
        |  POST /chat   {"message": "How much salt per day?"}
        v
 +----------------------------+
 |  FastAPI server            |   handles the /chat route
 |  (app/main.py or similar)  |
 +-------------+--------------+
               |
               |  1. load system prompt + task prompt (v1 or v2) from prompts/
               |  2. add the user's question
               v
 +----------------------------+
 |  app/llm.py (wrapper)      |   reads GROQ_API_KEY from .env
 |                            |   sends the request to the Groq API
 +-------------+--------------+
               |
               v
        Groq LLM (cloud)
               |
               |  raw model reply
               v
 +----------------------------+
 |  Parse + validate JSON     |   checks answer / confidence / follow_up exist
 +-------------+--------------+
               |
               v
 Response to the user:
 {
   "answer": "...",
   "confidence": "high | medium | low",
   "follow_up": "..."
 }
```

**Evaluation flow (S2):**

```
 eval/run_compare.py
     for each of the 10 questions:
         ask with prompt v1  -> save answer
         ask with prompt v2  -> save answer
     write results table  -> eval/prompt_compare.md
 I then add my own analysis at the bottom of that file.
```

---

## 4. Where is everything stored? (project layout)

Day 06 was **moved to the repo root**, so there is no `day06/` folder anymore.

```
sanjivani-sj-31-poshanguide/
├── app/
│   ├── llm.py                 # Groq/Gemini provider wrapper
│   ├── config.py              # settings read from .env
│   └── ...                    # API routes incl. POST /chat
├── prompts/
│   ├── system.txt             # PoshanGuide system prompt (role + rules)
│   ├── task_v1.txt            # task prompt, version 1
│   └── task_v2.txt            # task prompt, version 2
├── eval/
│   ├── run_compare.py         # runs 10 questions x 2 prompts
│   └── prompt_compare.md      # real answers table + my analysis
├── day04/                     # earlier work (fetch, ingest, data/records.json)
├── .env                       # REAL secret key (on my PC only, NOT in git)
├── .env.example               # template, committed (no real key)
├── .gitignore                 # lists .env so it is never committed
├── requirements.txt
└── README.md
```

> The exact file names inside `prompts/` and the main API file may differ slightly in my project. The folders above are what the checker looks for.

**Where the important things live**

| Item | Location | In Git? |
|---|---|---|
| Groq API key | `.env` at repo root | **No** |
| Variable template | `.env.example` | Yes |
| LLM wrapper | `app/llm.py` | Yes |
| Prompts | `prompts/` | Yes |
| Comparison results + analysis | `eval/prompt_compare.md` | Yes |
| DGI data from Day 03/04 | `day04/data/` | Yes |

---

## 5. Setup and how to run (Windows PowerShell)

**1. Open the repo and activate the virtual environment**
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
.\.venv\Scripts\Activate.ps1
```

**2. Install packages**
```powershell
pip install -r requirements.txt
```

**3. Create `.env` and add the key**
```powershell
copy .env.example .env
code .env
```
Add one line at the bottom of `.env` (no quotes, no spaces around `=`, no `#` in front):
```
GROQ_API_KEY=your_key_from_console.groq.com
```
Get a free key at https://console.groq.com, under **API Keys**.

**4. Check that the key loads**
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('KEY FOUND' if os.getenv('GROQ_API_KEY') else 'KEY MISSING')"
```

**5. Start the server** (adjust the module name if mine differs)
```powershell
uvicorn app.main:app --reload
```

**6. Test `/chat`** (in a second terminal)
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body '{"message":"How much salt should I eat per day?"}'
```
Expected: JSON with `answer`, `confidence`, `follow_up`.

**7. Run the prompt comparison**
```powershell
python -m eval.run_compare
```
Then check that nothing is broken:
```powershell
findstr /C:"missing" eval\prompt_compare.md
findstr /C:"[EDIT]" eval\prompt_compare.md
```
Both commands must print nothing.

---

## 6. Security rules I follow

- The real key is only in `.env`, and `.env` is listed in `.gitignore`.
- `.env.example` has the variable name but **no real value**.
- Before every commit I run `git status` and make sure `.env` is not listed.
- If a key is ever shown in a chat, screenshot or commit, I delete it on console.groq.com and create a new one.

---

## 7. Prompt design notes

**System prompt (same for both versions)**
- Role: a careful nutrition guide for Indian dietary guidelines.
- Uses the DGI as its source and does not invent numbers.
- Says clearly when it does not know or when a doctor should be consulted.
- Always replies in the required JSON format.

**Task prompt v1:** a short, simple instruction.

**Task prompt v2:** a more detailed instruction (for example: cite the guideline number, keep the answer short, state the limit with units, set confidence honestly, suggest a useful follow-up).

> Fill in the real differences from my own files in `prompts/`.

---

## 8. Evaluation: 10 questions x 2 prompts

The full table of real answers is in `eval/prompt_compare.md`. That file must have:
- 20 real answers (10 questions x 2 prompts), with no "GROQ_API_KEY is missing" text
- my own analysis, with no `[EDIT]` placeholders left

### My analysis (write in my own words after reading the table)

**Which prompt is better, v1 or v2?**
Prompt v__ is better because: (1) ______ (2) ______ (3) ______

**How was Q6 handled?**
Q6 was: "______". With v1 the model ______. With v2 the model ______. I would change ______.

**Was the confidence value realistic?**
The confidence values were ______. For example, in Q__ it said "______" but the answer was ______.

**One improvement I would make next**
______

---

## 9. Common problems and fixes

| Problem | Cause | Fix |
|---|---|---|
| "GROQ_API_KEY is missing" in answers | Key not in `.env`, or `.env` has errors | Put `GROQ_API_KEY=...` in `.env`, test with the KEY FOUND command, rerun `run_compare` |
| `python-dotenv could not parse statement` | A line in `.env` is not `NAME=value`, `# comment` or empty | Open `.env` and fix the line it names |
| `ModuleNotFoundError: No module named 'app'` | Script run as a file instead of a module | Use `python -m eval.run_compare` from the repo root |
| `401 Unauthorized` | Wrong or deleted key | Create a new key and update `.env` |
| `429` rate limit | Too many requests | Wait a minute and rerun |
| `.env` shows in `git status` | Not ignored | `git rm --cached .env` and add `.env` to `.gitignore` |
| `no upstream branch` | First push of the branch | `git push --set-upstream origin main` |

---

## 10. Git steps for Day 06

```powershell
git add -A
git status          # .env must NOT be listed
git commit -m "day-06: real Groq answers, my analysis and README"
git push
```

The checker reruns every morning, so earlier days turn OK once the fix is pushed.

---

## 11. Day 06 checklist

- [ ] `app/llm.py` wrapper works with Groq
- [ ] `POST /chat` returns JSON with `answer`, `confidence`, `follow_up`
- [ ] `prompts/` has system + task v1 + task v2
- [ ] `.env` is on my PC only; `.env.example` is committed
- [ ] `eval/prompt_compare.md` has 20 real answers (no "missing" errors)
- [ ] My own analysis is written (better prompt, Q6, confidence)
- [ ] Everything is at the repo root, not inside `day06/`
- [ ] Commit starts with `day-06:` and is pushed