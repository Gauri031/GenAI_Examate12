# Day 10 - PoshanGuide: Streamlit Chat UI + "My Plate Check"

## 1. The Task (as given)

> `ui/app.py` Streamlit chat for PoshanGuide that calls `/ask` or `/agent`, shows **citations**, saves **thumbs up/down**, and has a **signature feature: "My plate check" panel**: the user lists what they ate today and sees a **colour bar for each food group** against the **NIN "My Plate for the Day" proportions**. **Screenshot in README.** **Checkpoint 2 live demo. Tag `checkpoint-2`.**

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| 1 | Streamlit chat that calls `/ask` or `/agent` | `app.py` (sidebar switch between `/ask` and `/agent`) | `ui/` |
| 2 | Shows citations | "Sources" expander under every answer (source, page, title, score, snippet) | `ui/app.py` |
| 3 | Saves thumbs up / down | `feedback.py`, file `data/feedback.jsonl` | `ui/`, `data/` |
| 4 | Signature feature: My plate check | `plate.py` + "My plate check" view in `app.py` | `ui/` |
| 5 | Colour bar per food group vs NIN My Plate | `data/plate_reference.json` (NIN amounts), HTML bars in `app.py` | `data/`, `ui/` |
| 6 | Screenshot in README | section 9 (images in `docs/screenshots/`) | `docs/` |
| 7 | Checkpoint 2 live demo | demo script in `docs/checkpoint-2.md` | `docs/` |
| 8 | Tag `checkpoint-2` | git tag (section 12) | git |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .gitignore
├── day08/                          <- backend with POST /ask (keep running while using the UI)
├── day09/                          <- backend with /agent, if you have it
└── day10/
    ├── README.md                   <- this file (with screenshots)
    ├── requirements.txt            <- streamlit, requests
    ├── .env.example                <- POSHAN_API_URL (optional)
    ├── ui/
    │   ├── app.py                  <- the Streamlit app: chat + My plate check
    │   ├── plate.py                <- plate logic (reads meal text, compares with NIN)
    │   └── feedback.py             <- saves thumbs up / down
    ├── data/
    │   ├── plate_reference.json    <- ICMR-NIN My Plate for the Day amounts
    │   ├── foods.json              <- foods the plate check understands
    │   ├── feedback.jsonl          <- created by the app when you click thumbs
    │   └── README.txt
    ├── tests/
    │   └── test_plate.py           <- 8 quick tests for the plate logic and feedback
    └── docs/
        ├── checkpoint-2.md         <- live demo script
        └── screenshots/
            ├── chat.png            <- YOUR screenshot of the chat
            └── plate-check.png     <- YOUR screenshot of My plate check
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| `README.md`, `requirements.txt`, `.env.example` | `day10/` |
| `app.py`, `plate.py`, `feedback.py` | `day10/ui/` |
| `plate_reference.json`, `foods.json` | `day10/data/` |
| `test_plate.py` | `day10/tests/` |
| `checkpoint-2.md` | `day10/docs/` |
| `chat.png`, `plate-check.png` (my screenshots) | `day10/docs/screenshots/` |

The UI is a separate app. It does not contain the backend. It talks to the PoshanGuide API that is already in `day08` (or `day09`), so that API must be running.

## 5. How it works (flow)

```
Streamlit UI (day10/ui/app.py, port 8501)
 │
 ├─ Chat view
 │    question -> POST {api}/ask {"question", "top_k"}   (or POST {api}/agent)
 │             <- answer, answerable, citations
 │    show answer + "Sources" expander
 │    thumbs up / down -> feedback.py -> data/feedback.jsonl
 │
 └─ My plate check view   (no API, no LLM: works offline)
      text "2 roti, 1 katori dal, 1 banana ..."
        -> plate.parse_meal()     split into foods, read quantities, match foods.json
        -> plate.compute_plate()  grams per food group vs NIN amount -> ratio -> status
        -> colour bars, table of shares, next step
        -> button "Ask PoshanGuide about <weakest group>" -> sent to the chat view
```

## 6. The signature feature: My plate check

### 6.1 The NIN amounts (ICMR-NIN "My Plate for the Day", 2000 kcal adult)
| Food group | NIN amount per day |
|------------|--------------------|
| Cereals & millets | 250 g (raw weight) |
| Vegetables (incl. green leafy, roots, tubers) | 400 g |
| Fruits | 100 g |
| Pulses, eggs & flesh foods | 85 g (raw weight) |
| Milk & curd | 300 ml |
| Nuts & seeds | 35 g |
| Fats & oils | 27 g |

Source: ICMR-NIN *Dietary Guidelines for Indians 2024* and the ICMR-NIN "My Plate for the Day" policy brief (https://www.nin.res.in). The older 2023 NIN poster listed 270 g cereals and 90 g pulses. The amounts are in `data/plate_reference.json` and can be changed there if my teacher expects the poster values.

### 6.2 How the colour bar works
- One bar per food group. The bar length shows `eaten / NIN amount` (scale up to 150%). The dark line is 100%.
- Colours:

| Colour | Meaning | Rule |
|--------|---------|------|
| Red | Low | under 50% of the NIN amount |
| Amber | Almost there | 50% to 89% |
| Green | On track | 90% to 125% |
| Blue | Above the plate (fine) | over 125% for vegetables, fruits, pulses/eggs/flesh, milk |
| Orange | Above the plate, cut back | over 125% for cereals, nuts & seeds, fats & oils |
| Grey | Nothing eaten yet | 0 g |

- A table shows the **proportions**: my share of what I ate in each group versus the group's share of the NIN plate.
- Sweets, fried snacks, biscuits and soft drinks are not in My Plate, so they are counted separately as "foods outside the plate".
- The weakest groups get a "next step", and one button sends a question about the weakest group to the chat.

### 6.3 How the meal text is read
- One food per line, or separated by commas. Quantity first: `2 roti`, `1 katori dal`, `half glass milk`, `1/2 katori rice`.
- The number multiplies the food's usual unit (shown in the "Foods I understand" table): 1 roti = 30 g flour, 1 katori cooked rice = 50 g raw, 1 katori dal = 30 g raw dal, 1 katori sabzi = 100 g, 1 egg = 50 g, 1 glass milk = 200 ml.
- Grams also work: `150 g curd`, `200 ml milk`. `handful` works for nuts (30 g), `tbsp` for ghee and oil (15 g).
- Mixed dishes count in several groups (for example khichdi = cereals + pulses, sambar = pulses + vegetables, cooked dishes include typical cooking oil).
- If a food is not recognised, the app lists it instead of guessing. More foods can be added in `data/foods.json`.
- The household amounts are **rough estimates**, so the bars are a guide, not a measurement.

### 6.4 Limits (also shown in the app)
The plate is for a 2000 kcal adult. Children, pregnant and breastfeeding women, and people with medical conditions need different amounts. The app gives general information, not medical advice.

## 7. Each file explained

### 7.1 `ui/app.py`
- **Sidebar:** API address, endpoint (`/ask` or `/agent`), top-k slider, a green/red backend status, the saved thumbs-up/down counts, and a "Clear chat" button.
- **Chat view:** `ask_backend()` calls the API and normalises the reply (answer, answerable, citations). Messages are kept in `st.session_state`. Each answer has a Sources expander and 👍 / 👎 buttons. "I don't know" answers are marked and have no sources.
- **Plate view:** text box, example meal button, food list, colour bars (HTML), share table, "How I read your meal", next step.
- `/agent`: the app sends `{"question": ...}` and accepts an answer in `answer`, `response`, `final_answer` or `output`, and sources in `citations` or `sources`. If my agent uses another field name, change `AGENT_PAYLOAD_FIELD` at the top of the file.

### 7.2 `ui/plate.py`
- `parse_meal(text)`: splits the text, reads quantity or grams, matches food names (longest name first, plural works), and returns grams per food group plus the foods it did not recognise.
- `compute_plate(parsed)`: adds up each group, compares with the NIN amount, returns ratio, status, colour, gap, and shares.
- `classify(ratio, over_is_warning)`: the colour rules from section 6.2.
- Has no Streamlit code, so it is tested separately.

### 7.3 `ui/feedback.py`
- `save_feedback()` appends one JSON line per rating to `data/feedback.jsonl` with time, session, message id, rating (`up` or `down`), the question, the answer, whether it was answerable, the endpoint, and the cited sources.
- `feedback_stats()` counts thumbs up and down (the latest rating of a message counts).

### 7.4 `data/`
`plate_reference.json` (NIN amounts, labels, colours rules, example question per group) and `foods.json` (about 340 food names for 64 entries with their group amounts).

## 8. Setup and run (PowerShell, two terminals)

**Terminal 1: the backend (leave it running)**
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide\day08
uvicorn app.main:app --reload
```
(`day08\.env` must contain a valid key. If my `/agent` is in `day09`, run that folder instead.)

**Terminal 2: the UI**
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide\day10
pip install -r requirements.txt
streamlit run ui/app.py
```
Open http://localhost:8501. The sidebar should say **Backend is running**.

**Quick tests (optional)**
```powershell
cd day10
python -m unittest discover -s tests
```
All 8 tests should pass.

## 9. Screenshots

> **Take these from the running app and save them in `docs/screenshots/`, then check that they show up below.**
>
> 1. Chat: ask "Which foods are rich in iron for a 2-year-old?", open the **Sources** expander, then press **Win + Shift + S** and save as `docs/screenshots/chat.png`.
> 2. Plate check: switch to **My plate check**, click **Load example meal**, capture the colour bars and save as `docs/screenshots/plate-check.png`.

### Chat with citations and thumbs up/down
![PoshanGuide chat with sources](docs/screenshots/chat.png)

### My plate check: colour bars against NIN My Plate for the Day
![My plate check](docs/screenshots/plate-check.png)

## 10. Saved feedback

Every thumbs up or down is saved in `data/feedback.jsonl`, one line per rating, for example:
```json
{"time": "2026-11-20T09:15:02+00:00", "session_id": "a1b2c3d4", "message_id": "9f8e7d6c5b", "rating": "up", "question": "...", "answer": "...", "answerable": true, "endpoint": "/ask", "citations": ["child_nutrition.md p1"]}
```
The sidebar shows how many 👍 and 👎 are saved. Keep a few ratings in the file as proof for the demo.

## 11. My analysis (EDIT: write in your own words)
- **Why I chose these colour rules for the bars:** [EDIT]
- **One example meal and what the bars showed:** [EDIT]
- **What the thumbs-down feedback tells me about my answers:** [EDIT]
- **What I would improve next (more foods, children's plates, Hindi/Marathi):** [EDIT]

## 12. Checkpoint 2 and git

### Live demo
The full script is in `docs/checkpoint-2.md`. Start both terminals first (section 8).

### Commit, push and tag (from the repo root)
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
git rev-parse --show-toplevel
git add -A day10
git status
git commit -m "Day 10: Streamlit chat UI with citations, feedback and My plate check"
git push origin main
git tag checkpoint-2
git push origin checkpoint-2
```
In `git status`, `day10/.env` (if I made one) must not be listed. `git tag` should list `checkpoint-2`, and the tag should appear on GitHub under Tags.

## 13. Troubleshooting

| Problem | Fix |
|---------|-----|
| Sidebar: "Backend not reachable" | Start `uvicorn app.main:app --reload` in `day08` (terminal 1) and refresh the page |
| API error 502 in the chat | Check `day08/.env` (valid key, `GROQ_MODEL=llama-3.1-8b-instant`) |
| `/agent` gives 404 | The backend running does not have `/agent`. Run the folder that has it, or use `/ask` |
| `/agent` answer shows "(empty answer)" | Change `AGENT_PAYLOAD_FIELD` or the answer field names in `ask_backend()` |
| `streamlit` not found | Activate the virtual environment, then `pip install -r requirements.txt` |
| `No module named plate` | Start the app with `streamlit run ui/app.py` from the `day10` folder |
| Plate bars do not update | Press Ctrl+Enter or click outside the text box |
| "I did not recognise: ..." | Use names from the food list, or add the food in `data/foods.json` |
| Screenshots not visible in README | Check the exact names `chat.png` and `plate-check.png` in `docs/screenshots/` |
| `git tag` says the tag exists | `git tag -d checkpoint-2`, commit, then tag again |

## 14. Final checklist

- [ ] Backend runs and the sidebar shows "Backend is running"
- [ ] Chat answers with a Sources expander; Q6 says "I don't know"
- [ ] Thumbs up and down are saved in `data/feedback.jsonl`
- [ ] My plate check shows a colour bar for all 7 food groups
- [ ] `docs/screenshots/chat.png` and `plate-check.png` are saved and visible in the README
- [ ] My analysis (section 11) is written in my own words
- [ ] Checkpoint 2 demo practised (`docs/checkpoint-2.md`)
- [ ] Committed, pushed and tagged `checkpoint-2`
