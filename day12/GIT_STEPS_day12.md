# Day 12 - git steps: feature branch -> pull request -> merge

```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
git rev-parse --show-toplevel                 # must end with sanjivani-sj-31-poshanguide
git checkout main
git pull origin main
git checkout -b feature/ci-and-deploy

# put the files in place (creates day12/ and .github/)
Expand-Archive -Path "$env:USERPROFILE\Downloads\poshanguide_day12.zip" -DestinationPath . -Force

# check locally
cd day12
pip install -r requirements-dev.txt
ruff check .
pytest
cd ..

# commit and push the branch
Add-Content .gitignore "`n.env`nchroma_db/`n__pycache__/`n.pytest_cache/`n.ruff_cache/"
git check-ignore -v day12/.env                # must print a .gitignore line
git add -A day12 .github README.md .gitignore
git status                                    # no .env, chroma_db or __pycache__ listed
git commit -m "Day 12: add CI workflow, deployment config and README badge"
git push -u origin feature/ci-and-deploy
```

Then on GitHub: Compare & pull request -> Create pull request -> wait for ruff, pytest and docker build to be green -> Merge pull request -> Confirm -> Delete branch.

```powershell
git checkout main
git pull origin main
```
