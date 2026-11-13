# Day 01 - Project Card + Menu

## Task
Create public repo `sanjivani-sj-31-poshanguide` and clone it. README.md = PoshanGuide project card. `day01_intro.py` prints the card with variables + f-strings and asks name and question with `input()`. `day01_menu.py` = while-loop menu (1 About, 2 Sample questions, 3 one if/elif rule check, 0 Exit). Push.

## Project card
| Field | Details |
|---|---|
| Product | PoshanGuide: answers everyday eating questions strictly from ICMR-NIN Dietary Guidelines for Indians 2024, with page citations |
| User | First-year Sanjivani hostel student who eats mess food, drinks sweet chai 4 times a day, wonders if she needs protein powder |
| Problem | No quick, trustworthy, cited answers to everyday nutrition questions |
| Data source | DGI 2024 PDF (text-based, with portion-size and RDA tables) |

## Where is each file
| File | Exact path |
|---|---|
| Project card (repo) | `README.md` (repo root) |
| Intro script | `day01/day01_intro.py` |
| Menu script | `day01/day01_menu.py` |
| Day README | `day01/README.md` |

Day 01 has **no `app/` folder**; both scripts are plain files in `day01/`.

## Global files (repo root, shared by ALL days)
These are NOT inside any day folder:
| File | Path | Purpose |
|---|---|---|
| Virtual env | `<repo>/.venv/` | one environment for all days |
| Dependencies | `<repo>/requirements.txt` | one install for all days |
| Settings | `<repo>/.env` (template: `.env.example`) | limits, port, timeout; git-ignored |
| Git ignore | `<repo>/.gitignore` | ignores `.venv`, `.env`, `__pycache__`, raw downloads |

## Run (from the repo root first, one-time setup)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env  (skip if .env already exists)
```

Then:
```bash
cd day01
python day01_intro.py
python day01_menu.py
```
Day 01 works without installing anything. `day01_menu.py` reads `SUGAR_LIMIT_G` and `SUGAR_PER_TSP_G` from the root `.env` when python-dotenv is installed, otherwise it uses defaults (25 and 4).
