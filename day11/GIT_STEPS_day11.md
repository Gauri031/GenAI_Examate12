# Day 11 - git steps (from the repo root)

```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
git rev-parse --show-toplevel                 # must end with sanjivani-sj-31-poshanguide
Add-Content .gitignore "`n.env`nchroma_db/`n__pycache__/`n.pytest_cache/`n.ruff_cache/"
git check-ignore -v day11/.env                # must print a .gitignore line
git add -A day11
git status                                    # no .env, chroma_db or __pycache__ listed
git commit -m "Day 11: pytest tests, ruff check and Docker compose"
git push origin main
```
Run `pytest` and `ruff check .` inside day11 BEFORE committing.
