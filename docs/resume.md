# Resume bullets: PoshanGuide

**PoshanGuide** | Python, FastAPI, RAG, LangGraph, Streamlit, Groq / Gemini | [GitHub link](https://github.com/Gauri031/GenAI_Examate12)

## The 3 bullets (copy these into your resume)

- Built **PoshanGuide**, a nutrition assistant for Indian families: a FastAPI backend with guideline-grounded RAG answers and citations, a switchable Groq / Gemini LLM wrapper, and a Streamlit UI with feedback buttons and a "My Plate for the Day" check against NIN proportions.

- Designed a **LangGraph agent** with memory and a human-approval step that combines guideline search with a daily sugar and salt counter, and evaluated it on a ___-question test set (___ % grounded answers, ___ % with citations, ___ / ___ out-of-scope questions correctly refused).

- Hardened the service for production with a middleware that logs latency and token usage per request, caches repeat questions (**___ ms to ___ ms**, ___x faster, ___ % hit rate), enforces input limits, and blocks prompt injection (___ / ___ attacks stopped before any LLM call, ___ tests passing).

## How to finish this file

1. Take the numbers from `docs/day13_numbers.md` (run `python eval/bench_day13.py`) and from your `eval/run_eval.py` output.
2. Replace every `___` with a real number. If you do not have a number, delete that part of the sentence instead of guessing. An interviewer may ask where it came from.
3. Delete this "How to finish this file" section when you are done.

## Optional alternative wording (shorter, for a one-page resume)

- Built a RAG + agent nutrition assistant (FastAPI, LangGraph, Streamlit) that answers from official guidelines with citations; ___ % of ___ eval questions answered correctly.
- Added production safeguards: latency and token logging, response cache (___x faster on repeats), input limits and a prompt-injection guard (___ / ___ attacks blocked).

## Questions you should be ready to answer in an interview

- Why a cache for `/ask` and `/chat` but not for `/agent`? (The agent has memory and an approval step, so the same question can need a different answer.)
- How do you know the token numbers are right? (Real provider counts via `record_usage`; the log marks estimates.)
- What does your injection guard miss? (Rephrased attacks; a classifier and output filtering would be the next step.)
- What would you change to run this on several servers? (Move the cache to Redis, ship the logs to a monitoring tool.)
