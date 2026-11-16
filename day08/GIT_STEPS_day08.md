# Day 08 - git steps (from the repo root)

```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
Add-Content .gitignore "`nchroma_db/"
git check-ignore -v day08/.env
git add -A day08 .gitignore
git status
git commit -m "Day 08: RAG with citations, POST /ask, eval set and winner table"
git push origin main
```
Before committing, `day08/.env` and `day08/chroma_db/` must NOT appear in `git status`.

After running `python eval/run_eval.py` (it updates README.md and eval/eval_results.md), push again:
```powershell
git add -A day08
git commit -m "Day 08: add evaluation results and winner table"
git push origin main
```
