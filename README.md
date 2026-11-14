# PoshanGuide (sanjivani-sj-31-poshanguide)

| | |
|---|---|
| **Student** | Dhangar Gauri Yogesh - 2124UCEF2093 - CSE, Division SJ-31 |
| **Domain** | Health |
| **GitHub** | https://github.com/Gauri031 |

## Project card
- **Product:** Answers everyday eating questions - how much sugar, salt, oil or protein - strictly from ICMR-NIN's *Dietary Guidelines for Indians 2024*, with page citations.
- **User:** A first-year hostel student at Sanjivani who eats mess food, drinks sweet chai 4 times a day and wants to know if she needs protein powder for the gym.
- **Problem:** No quick, trustworthy, cited answers to everyday nutrition questions.
- **Data source:** DGI 2024 PDF (text-based, with portion-size and RDA tables) - https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf and https://nin.res.in/popular.html
- **Record fields:** `guideline_no, guideline_title, key_advice, number_limit, target_group, page_ref`
- **Tricky part:** Chunks must keep the guideline number so answers cite correctly; numbers must be quoted exactly, never invented.
- **Safety:** General nutrition information from ICMR-NIN guidelines, not medical advice. People with diabetes, kidney disease, pregnancy or other conditions should follow their doctor or dietitian.

### Sample questions
1. How much sugar per day is okay for an adult according to ICMR?
2. Should I take protein supplements to build muscle?
3. How much water should I drink in a day?
4. I drink 4 cups of chai with 2 spoons sugar each - am I over the limit and what should I change?
5. What should a pregnant woman eat extra and how is it different for elderly people?
6. Is the Patanjali chyawanprash brand better than Dabur for immunity? *(out of scope - should be declined)*

### Planned features
- **My plate check:** user lists what they ate today and sees a colour bar per food group vs the NIN "My Plate for the Day".
- **daily_sugar_salt_counter:** totals sugar/salt from a small CSV and compares with the 20-25 g limits.

---

## Progress by day

| Day | Folder | What was built |
|---|---|---|
| 1 | [`day01/`](day01/README.md) | Project card script (`day01_intro.py`) + while-loop menu (`day01_menu.py`) |
| 2 | [`day02/`](day02/README.md) | 20 sample records (JSON); `app/records.py` + `app/cli.py` |
| 3 | [`day03/`](day03/README.md) | FastAPI service, pandas `explore.py`, TF-IDF `smart_search.py` (tag `week-1`) |
| 4 | [`day04/`](day04/README.md) | NIN document fetch, DGI PDF ingest to 17 records, typed `Record` dataclass, and source checksum manifest |

## Exact file locations
```
sanjivani-sj-31-poshanguide/
|-- README.md                  <- this file (all days combined)
|-- .env                       <- GLOBAL settings (git-ignored; copy of .env.example)
|-- .env.example               <- template, committed
|-- .gitignore                 <- GLOBAL
|-- requirements.txt           <- GLOBAL, one install for all days
|-- .venv/                     <- GLOBAL virtual env (you create it; git-ignored)
|-- day01/
|   |-- README.md
|   |-- day01_intro.py
|   `-- day01_menu.py
|-- day02/
|   |-- README.md
|   |-- app/  (__init__.py, config.py, records.py, cli.py)
|   `-- data/sample_records.json
|-- day03/
|   |-- README.md
|   |-- app/  (__init__.py, config.py, records.py, cli.py, smart_search.py, main.py)
|   |-- analysis/explore.py
|   `-- data/sample_records.json
`-- day04/
    |-- README.md
    |-- app/  (__init__.py, config.py, records.py, models.py, fetch.py, ingest.py)
    `-- data/  (sample_records.json, records.json, source_manifest.json, raw/ for ignored downloads)
```
- **Global (repo root):** `.env`, `.env.example`, `.gitignore`, `requirements.txt`, `.venv`.
- **Per day:** its own `README.md`, code and `data/`.
- **`app/` folders:** Days 02-04 each have an `app/` package inside their own day folder (`day02/app`, `day03/app`, `day04/app`). Day 01 has none. Always `cd` into the day folder before running `python -m app...` or `uvicorn app.main:app`.

## Setup once (works for every day)
```bash
git clone https://github.com/Gauri031/sanjivani-sj-31-poshanguide.git
cd sanjivani-sj-31-poshanguide
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

## Run each day
```bash
cd day01 && python day01_intro.py && python day01_menu.py && cd ..
cd day02 && python -m app.cli && cd ..
cd day03 && python analysis/explore.py && uvicorn app.main:app --reload     # Ctrl+C to stop, then: cd ..
cd day04 && python -m app.fetch && python -m app.ingest && cd ..
```

## .env settings (root `.env`)
`APP_NAME, APP_ENV, SUGAR_LIMIT_G, SALT_LIMIT_G, SUGAR_PER_TSP_G, HOST, PORT, SEARCH_TOP_K, REQUEST_TIMEOUT`, plus a commented `ANTHROPIC_API_KEY` placeholder for later GenAI days. Never commit `.env`.
