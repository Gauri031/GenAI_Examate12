# Checkpoint 2 - live demo of PoshanGuide

## Before the demo (5 minutes)
1. Terminal 1 - backend (from the folder that has `POST /ask`, i.e. day08):
   ```powershell
   cd day08
   uvicorn app.main:app --reload
   ```
2. Terminal 2 - UI:
   ```powershell
   cd day10
   pip install -r requirements.txt
   streamlit run ui/app.py
   ```
3. Open http://localhost:8501. The sidebar must show **"Backend is running"** in green.
4. Ask one question first (warm-up), so the embedding model is loaded and the first answer is fast.

## Demo script (about 5 minutes)
| Step | What I do | What I say |
|------|-----------|------------|
| 1 | Ask "Which foods are rich in iron for a 2-year-old?" | The UI calls `POST /ask`. The answer comes only from our documents. |
| 2 | Open the **Sources** expander | Every answer shows source file, page, title and the matching text. |
| 3 | Click **thumbs up** | The rating is saved to `data/feedback.jsonl`; the sidebar counter goes up. |
| 4 | Ask "Which nutritionist near my village is free this week?" (Q6) | The documents cannot answer this, so PoshanGuide says "I don't know". No sources. Click **thumbs down**. |
| 5 | Switch to **My plate check**, click **Load example meal** | This is my signature feature. It reads what I ate today. |
| 6 | Point at the colour bars | Each bar is one food group against the ICMR-NIN My Plate for the Day amount (250 g cereals, 400 g vegetables, 100 g fruits, 85 g pulses/eggs/flesh foods, 300 ml milk/curd, 35 g nuts/seeds, 27 g fats/oils). The dark line is 100%. Red = low, amber = almost, green = on track, orange = too much. |
| 7 | Edit the text, for example add "2 more roti", and press Ctrl+Enter | The bars update at once. No LLM is used here, so it also works offline. |
| 8 | Click **Ask PoshanGuide about vegetables** | The weakest group becomes a question in the chat, with citations. |

## One function to explain (if asked)
`compute_plate()` in `ui/plate.py`: adds up the grams eaten for each food group, divides by the NIN target to get a ratio, and gives it a status (low under 50%, almost 50-89%, on track 90-125%, above over 125%). Cereals, nuts and fats count as "too much" when above 125%, vegetables and fruit do not.

## If something fails during the demo
| Problem | Do this |
|---------|---------|
| Sidebar shows "Backend not reachable" | Start `uvicorn` in terminal 1 (see above), then refresh the page |
| Chat shows an API error 502 | Check `day08/.env` has a valid key and `GROQ_MODEL=llama-3.1-8b-instant` |
| No internet or no API key | Show the **My plate check** view (works fully offline) and the screenshots in the README |

## Tag
After the demo files are committed:
```powershell
git tag checkpoint-2
git push origin checkpoint-2
```
