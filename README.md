# Day 06 - PoshanGuide: LLM Provider Wrapper, /chat Endpoint and Prompt Comparison

## 1. The Task (as given)

> **S1:** `app/llm.py` provider wrapper (Groq/Gemini) + `POST /chat` with a PoshanGuide system prompt; `.env` NOT committed, `.env.example` committed.
> **S2:** `prompts/` folder (system + 2 task prompts); `/chat` returns JSON (`answer`, `confidence`, `follow_up`); `eval/prompt_compare.md` compares 2 prompt versions on your 10 questions.

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| S1 | Provider wrapper for Groq / Gemini | `llm.py` | `app/` |
| S1 | `POST /chat` endpoint | `chat.py`, connected in `main.py` | `app/` |
| S1 | PoshanGuide system prompt | `system.md` | `prompts/` |
| S1 | `.env` is NOT committed | `.env` listed in `.gitignore` | repo root |
| S1 | `.env.example` IS committed | `.env.example` | `day06/` |
| S2 | 3 prompt files (system + 2 task prompts) | `system.md`, `task_v1.md`, `task_v2.md` | `prompts/` |
| S2 | `/chat` returns `answer`, `confidence`, `follow_up` | response model in `chat.py` | `app/` |
| S2 | Compare 2 prompt versions on 10 questions | `prompt_compare.md` (made by `run_compare.py`) | `eval/` |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .gitignore                      <- contains the line  .env
├── docs/                           <- Day 05 files
├── day02/                          <- Day 02 files
└── day06/
    ├── README.md                   <- this file
    ├── .env                        <- your real API key, LOCAL ONLY, never committed
    ├── .env.example                <- template without secrets, committed
    ├── app/
    │   ├── __init__.py             <- empty file, makes app a package
    │   ├── main.py                 <- FastAPI app, connects all endpoints
    │   ├── llm.py                  <- Groq / Gemini provider wrapper
    │   └── chat.py                 <- POST /chat endpoint
    ├── prompts/
    │   ├── system.md               <- PoshanGuide system prompt (rules and personality)
    │   ├── task_v1.md              <- task prompt version 1 (simple)
    │   └── task_v2.md              <- task prompt version 2 (structured)
    ├── eval/
    │   ├── questions.txt           <- the 10 test questions
    │   ├── run_compare.py          <- runs v1 and v2 on all questions
    │   └── prompt_compare.md       <- results table and my analysis
    └── data/
        └── nutrition.json          <- keyword data used by GET /ask (copied from day02)
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md` | `day06/` |
| `.env` | `day06/` (never push) |
| `.env.example` | `day06/` |
| `main.py`, `llm.py`, `chat.py`, `__init__.py` | `day06/app/` |
| `system.md`, `task_v1.md`, `task_v2.md` | `day06/prompts/` |
| `questions.txt`, `run_compare.py`, `prompt_compare.md` | `day06/eval/` |
| `nutrition.json` | `day06/data/` |

Important: file names must be exact. A downloaded file named `chat (1).py` or `questions (1).txt` must be renamed.

## 5. How the application works (flow)

```
User sends POST /chat  {"question": "...", "prompt_version": "v2"}
   -> chat.py validates the request (question must be at least 3 characters)
   -> loads prompts/system.md  (PoshanGuide rules)
   -> loads prompts/task_v1.md or task_v2.md and puts the question inside {question}
   -> llm.py sends both prompts to the chosen provider (Groq or Gemini)
   -> provider returns JSON text
   -> parse_json() turns the text into a dictionary
   -> chat.py cleans it: confidence must be high / medium / low
   -> API returns  {"answer": "...", "confidence": "...", "follow_up": "..."}
```

## 6. Each file explained

### 6.1 `app/llm.py` - provider wrapper
- Reads `LLM_PROVIDER` from `.env` (`groq` or `gemini`) and sends the prompt to that provider.
- `_groq()` calls the Groq chat completions API with JSON mode on.
- `_gemini()` calls the Gemini `generateContent` API with the JSON response type.
- `call_llm(system_prompt, user_prompt, temperature=0.2)` is the single function the rest of the app uses. Changing provider needs no code change, only the `.env` value.
- `parse_json(text)` removes Markdown code fences if the model adds them, then converts the text to a dictionary.
- `LLMError` is a custom error for a missing key, a network failure or a bad provider response.
- Keys are only read from environment variables. They are never written in code.

### 6.2 `app/chat.py` - the /chat endpoint
- `ChatRequest`: `question` (text, at least 3 characters) and `prompt_version` (`v1` or `v2`, default `v2`).
- `ChatResponse`: `answer` (text), `confidence` (`high`, `medium` or `low`) and `follow_up` (text).
- `run_prompt(question, version)` loads the system and task prompts, calls the LLM, parses the JSON and cleans the result. If the confidence value is invalid it is set to `low`. If the answer is empty a safe default message is returned.
- `chat()` is the endpoint. A provider problem returns HTTP 502 with a clear message. Invalid JSON from the model also returns 502.
- `run_prompt` is also reused by `eval/run_compare.py`, so the evaluation tests exactly what the API does.

### 6.3 `app/main.py` - the app
- Creates the FastAPI app and connects the chat router, so `POST /chat` is available.
- Also keeps the earlier endpoints: `GET /`, `GET /health` and `GET /ask` (keyword answers from `data/nutrition.json`).

### 6.4 `prompts/` - the three prompt files
| File | Purpose |
|------|---------|
| `system.md` | Gives PoshanGuide its role and rules: friendly nutrition assistant for families in India, simple language, common Indian foods, general guidance only (no diagnosis or medicine doses), say "I cannot answer" when information is unreliable or live/local/personal, never invent facts, always reply in one JSON object. |
| `task_v1.md` | Short, plain instruction: answer the question and reply in JSON with `answer`, `confidence`, `follow_up`. |
| `task_v2.md` | Structured instruction: exact JSON shape, answer limited to 2-4 short sentences, clear rules for high / medium / low confidence, a useful follow-up question, and an instruction to say plainly when the question cannot be answered. |

The placeholder `{question}` inside each task prompt is replaced with the user's question.

### 6.5 `eval/` - prompt comparison
- `questions.txt`: the 10 test questions, one per line.
- `run_compare.py`: runs prompt v1 and v2 on every question and writes the results table into `prompt_compare.md`.
- `prompt_compare.md`: the results table plus my own analysis.

## 7. The /chat API

### Request
```json
{
  "question": "Which foods are rich in iron for a 2-year-old?",
  "prompt_version": "v2"
}
```

### Response
```json
{
  "answer": "Give ragi porridge, dal, green leafy vegetables like palak, and eggs if the family eats them. Add a squeeze of lemon to help the body absorb iron.",
  "confidence": "high",
  "follow_up": "Does your child eat eggs or only vegetarian food?"
}
```
(Real answers will differ because they come from the model.)

### Error responses
| Code | Meaning |
|------|---------|
| 422 | Request is invalid, for example the question is too short |
| 502 | LLM provider problem: missing key, network error, or the model did not return valid JSON |

### Other endpoints in this app
| Endpoint | Purpose |
|----------|---------|
| `GET /` | Welcome message |
| `GET /health` | Health check and number of loaded data entries |
| `GET /ask?question=` | Answer from the local keyword data |
| `POST /chat` | Answer from the LLM (Day 06) |

## 8. Environment variables

`.env.example` (committed, no secrets):
```
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
```

| Variable | Meaning |
|----------|---------|
| `LLM_PROVIDER` | `groq` or `gemini` |
| `GROQ_API_KEY` | Free key from console.groq.com |
| `GEMINI_API_KEY` | Free key from aistudio.google.com/apikey |
| `GROQ_MODEL`, `GEMINI_MODEL` | Model names. If a model is retired, change the name here, no code change needed. |

### Security rules
- `.env` holds the real key and is **never committed**. It is listed in `.gitignore`.
- `.env.example` is committed so others know which variables are needed.
- If a key is ever pushed or shared by mistake, delete it on the provider's website and create a new one.

## 9. Setup and run (PowerShell, from the repo root)

```powershell
# 1. go into the folder
cd day06

# 2. install the packages
pip install fastapi "uvicorn[standard]" requests python-dotenv

# 3. create your .env from the template and paste your real key
Copy-Item .env.example .env
code .env

# 4. start the app
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs, click `POST /chat`, then **Try it out** and send:
```json
{"question": "What is a good weaning food at 6 months?"}
```

Always run `uvicorn` from inside `day06`, not from inside `app`, otherwise Python cannot find the `app` package.

## 10. Prompt comparison (S2 deliverable)

### Method
1. Both prompts use the **same** `system.md`. Only the task prompt differs, so the comparison is fair.
2. Run all 10 questions through **v1** and **v2** with the same model and temperature.
3. Record answer, confidence and follow-up for each.

### Run it
```powershell
cd day06
python eval/run_compare.py
```
The script fills `eval/prompt_compare.md` with a table:

| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. | v2 follow_up |
|---|----------|-----------|----------|-----------|----------|--------------|

### What to judge in the analysis
- Which version gave clearer and shorter answers?
- Did the confidence value make sense? Q6 (a question the data cannot answer, about a nutritionist near the village) should get **low** confidence and an honest "I cannot answer".
- Were the follow-up questions useful?
- Did either version break the JSON format?
- Which version is used as the default in `/chat`, and why? (Default is **v2**.)

The analysis section at the bottom of `prompt_compare.md` must be written in my own words.

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

(Replace with my own 10 questions from Day 05 if they differ, in `eval/questions.txt`.)

## 11. Git: commit and push

Run from the **repo root** (`sanjivani-sj-31-poshanguide`):

```powershell
git check-ignore -v day06/.env
git add -A day06
git add -A .env.example
git status
git commit -m "Day 06: LLM wrapper, /chat endpoint, prompts, prompt comparison"
git push origin main
```

Checks before committing:
- `git check-ignore -v day06/.env` must print a line mentioning `.gitignore`. If it prints nothing, run `Add-Content .gitignore "`n.env"`.
- In `git status`, `day06/.env` must **not** be listed.
- `day06/.env.example` **must** be listed (committed).

After pushing, open the repo on GitHub and check that `day06/` has `app`, `prompts`, `eval` and `.env.example`, and no `.env`.

## 12. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named app` | Run `uvicorn` from the `day06` folder, not from inside `app` |
| `No module named app.chat` | `chat.py` and `llm.py` are missing from `day06/app/` |
| `GROQ_API_KEY is missing` | Create `.env` in `day06/` and paste the key; check `LLM_PROVIDER` |
| 502 with a Groq/Gemini error | The key or model name is wrong; the message shows the provider's reason |
| 502 "Model did not return valid JSON" | Run the request again; check that the prompt files were not edited by mistake |
| `/health` shows `data_entries: 0` | `data/nutrition.json` is missing or in a different format |
| File names like `questions (1).txt` | Rename them to the exact names in section 3 |
| `.env` appears in `git status` | Do not commit. Add `.env` to `.gitignore` and check again |

## 13. Final checklist

- [ ] `app/llm.py` works with Groq or Gemini
- [ ] `POST /chat` returns `answer`, `confidence`, `follow_up`
- [ ] `prompts/` has `system.md`, `task_v1.md`, `task_v2.md`
- [ ] `.env` is NOT committed
- [ ] `.env.example` is committed
- [ ] `eval/questions.txt` has my 10 questions
- [ ] `eval/prompt_compare.md` generated and analysis written in my own words
- [ ] Everything pushed to GitHub inside the `day06/` folder