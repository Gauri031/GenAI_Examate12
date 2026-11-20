# Day 12 - PoshanGuide: CI (GitHub Actions), Pull Request and Public Deployment

[![CI](https://github.com/Gauri031/GenAI_Examate12/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Gauri031/GenAI_Examate12/actions/workflows/ci.yml)

## Live deployment

- **Live API:** https://poshanguide-api.onrender.com
- **Health check (public):** https://poshanguide-api.onrender.com/health
- **API docs (public):** https://poshanguide-api.onrender.com/docs

> The free Render plan puts the service to sleep after 15 minutes without visitors. The first request after a sleep takes about a minute. Open `/health` once before showing it to someone.

## 1. The Task (as given)

> **S1:** `.github/workflows/ci.yml` (ruff, pytest, docker build); **green badge in README**; **1 PR from a feature branch merged after CI is green**.
> **S2:** **deploy PoshanGuide (Render / Hugging Face Spaces)**; **live URL in README and in the tracker**; **`/health` works publicly**.

## 2. What the task includes

| # | Requirement | Deliverable | Location |
|---|-------------|-------------|----------|
| S1 | CI workflow with ruff, pytest, docker build | `ci.yml` (3 jobs) | `.github/workflows/` at the **repo root** |
| S1 | Green badge in README | badge line at the top of this file and of the root README | `README.md` |
| S1 | 1 PR from a feature branch, merged after CI is green | branch `feature/ci-and-deploy`, steps in section 7 | GitHub |
| S2 | Deploy to Render or Hugging Face Spaces | `Dockerfile` (reads `$PORT`), steps in section 8 | `day12/` |
| S2 | Live URL in README | "Live deployment" section at the top | `README.md` |
| S2 | Live URL in the tracker | paste the same URL in the course tracker | tracker |
| S2 | `/health` works publicly | `GET /health` in `app/main.py`, checked by the CI and by Render | `app/main.py` |

## 3. Folder structure (where every file is stored)

```
sanjivani-sj-31-poshanguide/        <- repo root
├── .github/
│   └── workflows/
│       └── ci.yml                  <- THE CI FILE: must be here, at the repo root
├── .gitignore
├── README.md                       <- root README: add the badge and live URL here too
├── day11/ ...                      <- earlier days
└── day12/                          <- the project that CI tests and Render deploys
    ├── README.md                   <- this file
    ├── Dockerfile                  <- image for API and UI (non-root, reads $PORT, index built in)
    ├── .dockerignore
    ├── docker-compose.yml          <- run API + UI locally
    ├── requirements.txt            <- packages for the app
    ├── requirements-dev.txt        <- adds pytest, httpx, ruff
    ├── pytest.ini
    ├── ruff.toml
    ├── .env                        <- your real keys, LOCAL ONLY, never committed
    ├── .env.example                <- template without secrets, committed
    ├── app/                        <- the API
    │   ├── main.py                 <- /health, /ask ...
    │   ├── rag.py  ask.py  search.py  chat.py  tools.py
    │   ├── chunking.py  embed.py  vectorstore.py  llm.py
    │   └── __init__.py
    ├── ui/                         <- Streamlit UI (app.py, plate.py, feedback.py)
    ├── prompts/                    <- 5 prompt files
    ├── documents/                  <- PoshanGuide documents (indexed)
    ├── data/                       <- foods.json, plate_reference.json
    ├── deploy/
    │   └── huggingface/README.md   <- Space README with the settings block (Hugging Face option)
    ├── docs/screenshots/           <- ci-green.png, live-health.png, live-docs.png (my screenshots)
    └── tests/                      <- 42 tests (conftest.py + 7 test files)
```

## 4. Where to save each file

| File | Folder |
|------|--------|
| **`ci.yml`** | **`.github/workflows/` at the repo root** (next to `day12`, NOT inside it) |
| `README.md`, `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, `ruff.toml`, `.env.example` | `day12/` |
| `main.py`, `rag.py`, `ask.py`, `search.py`, `chat.py`, `tools.py`, `chunking.py`, `embed.py`, `vectorstore.py`, `llm.py`, `__init__.py` | `day12/app/` |
| `app.py`, `plate.py`, `feedback.py` | `day12/ui/` |
| prompts, documents, data files | `day12/prompts/`, `day12/documents/`, `day12/data/` |
| `conftest.py` and the `test_*.py` files | `day12/tests/` |
| `README.md` for Hugging Face | `day12/deploy/huggingface/` |
| my screenshots | `day12/docs/screenshots/` |

GitHub only runs workflows found in `.github/workflows/` at the **top** of the repository. A `ci.yml` placed inside `day12/` is ignored.

## 5. The CI workflow (S1)

File: `.github/workflows/ci.yml`. It runs the commands inside the `day12` folder (`defaults.run.working-directory: day12`).

### 5.1 When it runs
| Trigger | Meaning |
|---------|---------|
| `push` to `main` | after every merge or push to main |
| `pull_request` into `main` | on every pull request, so the PR shows green or red checks |
| `workflow_dispatch` | a "Run workflow" button in the Actions tab |

Running twice on the same branch cancels the older run (`concurrency`).

### 5.2 The three jobs
| Job (check name) | What it does | Fails when |
|------------------|--------------|------------|
| **ruff** | `pip install ruff`, then `ruff check .` | ruff finds unused imports, unused variables, syntax problems |
| **pytest** | installs `requirements-dev.txt` (with pip cache), then `pytest` | any of the 42 tests fails |
| **docker build** | runs only after ruff and pytest pass. `docker build -t poshanguide:ci .`, starts the container and calls `/health` for up to 60 seconds | the image does not build, or `/health` does not answer |

### 5.3 The green badge
```markdown
[![CI](https://github.com/Gauri031/GenAI_Examate12/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Gauri031/GenAI_Examate12/actions/workflows/ci.yml)
```
- It is at the top of this README. Add the same line at the top of the **root** `README.md`.
- The badge turns green after the workflow has passed on `main`, which happens when the pull request is merged (section 7).

## 6. What changed from Day 11 (for deployment)

| File | Change | Why |
|------|--------|-----|
| `Dockerfile` | `CMD` uses `--port ${PORT:-8000}` | Render gives a port in `$PORT`; Hugging Face and local Docker use 8000 |
| `Dockerfile` | runs as the user `app` (uid 1000), not root | safer; Hugging Face Spaces runs containers as uid 1000 |
| `Dockerfile` | downloads the embedding model and builds the search index while building the image | the public service starts fast and `/health` answers at once |
| `app/search.py` | `POST /search/reindex` needs the header `X-Admin-Token` equal to the `ADMIN_TOKEN` variable; without that variable it is disabled (403) | on a public server nobody else should be able to start a heavy re-index |
| `.dockerignore` | also ignores `deploy/` | keeps deploy files out of the image |
| `tests/test_deploy.py` | 5 new tests: Dockerfile uses `$PORT`, does not run as root, `.dockerignore` keeps `.env` out, `.env.example` has no real key, `ci.yml` has ruff, pytest and docker build | stops the deployment settings from breaking by accident |
| `tests/test_search.py` | 2 new tests for the reindex protection | same |

## 7. The pull request (S1)

The workflow and the deployment files go into **one pull request from a feature branch**. The PR must be merged only after the three checks are green.

### 7.1 Create the branch and put the files in
Run in the VS Code terminal from the repo root:
```powershell
cd C:\Users\Rakesh\Desktop\sanjivani-sj-31-poshanguide
git rev-parse --show-toplevel          # must end with sanjivani-sj-31-poshanguide
git checkout main
git pull origin main
git checkout -b feature/ci-and-deploy
```
Put the files in place (from the zip, run at the repo root; it creates `day12/` and `.github/`):
```powershell
Expand-Archive -Path "$env:USERPROFILE\Downloads\poshanguide_day12.zip" -DestinationPath . -Force
```

### 7.2 Check locally before pushing
```powershell
cd day12
pip install -r requirements-dev.txt
ruff check .
pytest
cd ..
```
`ruff check .` must print `All checks passed!` and `pytest` must pass. Fixing problems now saves red checks later.

### 7.3 Add the badge and live URL to the root README
Open the root `README.md` and paste the two lines from `ROOT_README_SNIPPET.md` at the very top. Save.

### 7.4 Commit and push the branch
```powershell
Add-Content .gitignore "`n.env`nchroma_db/`n__pycache__/`n.pytest_cache/`n.ruff_cache/"
git check-ignore -v day12/.env         # must print a .gitignore line
git add -A day12 .github README.md .gitignore
git status
git commit -m "Day 12: add CI workflow, deployment config and README badge"
git push -u origin feature/ci-and-deploy
```
In `git status`, `day12/.env` and `chroma_db/` must not be listed.

### 7.5 Open the pull request on GitHub
1. Open https://github.com/Gauri031/GenAI_Examate12. A yellow bar says **"feature/ci-and-deploy had recent pushes"**. Click **Compare & pull request**.
2. Title: `Day 12: add CI and deployment`. Write one or two sentences in the description about what the PR adds.
3. Click **Create pull request**.
4. Scroll down to the checks box. Wait a few minutes until it lists **ruff**, **pytest** and **docker build**, each with a green tick, and says **"All checks have passed"**.
5. Only when all three are green, click **Merge pull request**, then **Confirm merge**. Then click **Delete branch**.
6. If a check is red, click **Details**, read the error, fix it on the same branch, commit and push. The PR re-runs the checks by itself.

### 7.6 Update your computer
```powershell
git checkout main
git pull origin main
```
After the merge, the workflow runs again on `main`. Open the **Actions** tab. When it is green, the badge on the README page is green too.

## 8. Deployment (S2)

The API is the part that must be public, because `/health` is the public check. The Streamlit UI is an optional second service.

### 8.1 Option A: Render (free, easiest)

1. Go to https://render.com and sign up with GitHub.
2. Click **New +** then **Web Service**, and connect the repo `Gauri031/GenAI_Examate12`.
3. Fill in the settings:

| Setting | Value |
|---------|-------|
| Name | `poshanguide-api` |
| Branch | `main` |
| Root Directory | `day12` |
| Runtime / Language | `Docker` |
| Dockerfile Path | `./Dockerfile` |
| Instance Type | `Free` |
| Health Check Path | `/health` |

4. Add environment variables (under **Environment**):

| Key | Value |
|-----|-------|
| `LLM_PROVIDER` | `groq` |
| `GROQ_MODEL` | `llama-3.1-8b-instant` |
| `GROQ_API_KEY` | my real Groq key (enter it only in Render, never in the repo) |

5. Click **Create Web Service**. The first build takes 5 to 10 minutes.
6. The live address is shown at the top of the service page, like `https://poshanguide-api.onrender.com`. Open `/health` on it. It should show `{"status":"ok","data_entries":...}`. Also open `/docs`.
7. Render deploys again automatically each time `main` changes, including when the pull request is merged.

**Optional: the UI as a second service.** Create another Web Service with the same repo and settings, name it `poshanguide-ui`, set **Docker Command** to
`sh -c "streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0"`
and add the variable `POSHAN_API_URL` = the live API address from step 6.

**Free-plan limits:** 512 MB of memory, sleep after 15 minutes without visitors, and the disk is wiped at every restart (fine here, because the index is built into the image). If the log says the service ran out of memory, use Option B.

### 8.2 Option B: Hugging Face Spaces (free, 16 GB memory)
1. Go to https://huggingface.co, sign up, and click **New Space**. Name it `poshanguide`, choose **Docker** as the SDK and **Blank**, then **Create Space**.
2. Open the Space **Settings → Variables and secrets**. Add the secret `GROQ_API_KEY`, and the variables `LLM_PROVIDER=groq` and `GROQ_MODEL=llama-3.1-8b-instant`.
3. Clone the Space and copy the project into it (replace `YOUR-HF-NAME` with my Hugging Face user name):
   ```powershell
   cd C:\Users\Rakesh\Desktop
   git clone https://huggingface.co/spaces/YOUR-HF-NAME/poshanguide
   Copy-Item sanjivani-sj-31-poshanguide\day12\* poshanguide\ -Recurse -Force -Exclude ".env","chroma_db","tests","docs"
   Copy-Item sanjivani-sj-31-poshanguide\day12\deploy\huggingface\README.md poshanguide\README.md -Force
   cd poshanguide
   git add .
   git commit -m "Deploy PoshanGuide API"
   git push
   ```
   When asked for a password, use a Hugging Face access token with **write** permission (Settings → Access Tokens).
4. The Space builds, then runs. The live address is `https://YOUR-HF-NAME-poshanguide.hf.space`. Open `/health` on it.

The settings block at the top of `deploy/huggingface/README.md` (`sdk: docker`, `app_port: 8000`) tells Hugging Face how to run the container.

### 8.3 After the deployment is live
1. Test it from outside: open `<live URL>/health` in the browser, then `<live URL>/docs`, and try `POST /ask` with `Which foods are rich in iron for a 2-year-old?`. A question outside the documents must answer "I don't know".
2. Put the real live URL in the **"Live deployment"** section at the top of this README and of the root README (all three lines).
3. Paste the same live URL in the **tracker**.
4. Save two screenshots in `docs/screenshots/`: `ci-green.png` (the PR checks or Actions run with green ticks) and `live-health.png` (the live `/health` page).

![CI green](docs/screenshots/ci-green.png)

![Live health check](docs/screenshots/live-health.png)

## 9. Flow of the whole task

```
feature branch  ->  push  ->  Pull Request
                                 │
                                 ▼  GitHub Actions (.github/workflows/ci.yml)
                     ┌───────────┴───────────┐
                     ▼                       ▼
                  ruff check             pytest (42 tests)
                     └───────────┬───────────┘
                                 ▼
                    docker build + start container + GET /health
                                 │  all green
                                 ▼
                          merge into main
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
        CI runs on main                  Render deploys main automatically
        badge turns green                live URL:  /health  /docs  POST /ask
```

## 10. Tests (42)

| File | Tests | Covers |
|------|-------|--------|
| `test_records.py` | 7 | chunk records keep source, page, title |
| `test_search.py` | 6 | search ranking and scores, auto-index, `/search/semantic`, reindex protection |
| `test_api.py` | 7 | `/health`, `/ask` with a fake LLM, "I don't know" for Q6, 422 and 502 cases |
| `test_rag.py` | 5 | citation rules |
| `test_agent_tool.py` | 5 | agent tools |
| `test_plate.py` | 7 | My plate check and saved feedback |
| `test_deploy.py` | 5 | Dockerfile, `.dockerignore`, `.env.example`, `ci.yml` |

Run: `cd day12`, then `pytest`. Lint: `ruff check .`.

## 11. Run it locally with Docker (same as Day 11)
```powershell
cd day12
Copy-Item .env.example .env
code .env
docker compose up --build
```
UI: http://localhost:8501. API: http://localhost:8000/docs. Stop with `Ctrl + C` and `docker compose down`.

## 12. Security notes
- Real keys live only in `day12/.env` on my computer and in the Render or Hugging Face settings. `.env` is in `.gitignore` and `.dockerignore`, so it is never committed and never copied into the image.
- If a key was ever pushed or shown to someone, delete it on the provider's website and make a new one.
- The public API uses my Groq key. Anyone can call `/ask`, which counts against my Groq limits. If that becomes a problem, switch the service off in the Render dashboard.
- `POST /search/reindex` is disabled unless `ADMIN_TOKEN` is set.

## 13. Troubleshooting

| Problem | Fix |
|---------|-----|
| The Actions tab shows no workflow | `ci.yml` is not at `.github/workflows/ci.yml` at the repo root, or it was not pushed. Run `git ls-files .github` |
| **ruff** check is red | Run `ruff check .` in `day12`, then `ruff check . --fix`, commit and push |
| **pytest** check is red | Run `pytest` in `day12` and read the first failure; fix, commit and push |
| **docker build** is red at "check /health" | Open the job log. It prints `docker logs`. Look for a Python error at the start |
| The badge says "no status" | The workflow has not run on `main` yet. Merge the PR and wait 5 minutes, then press Ctrl + F5 |
| The badge is red | Open the Actions tab, open the latest run on `main` and read the failed job |
| Render build fails: Dockerfile not found | Set Root Directory to `day12`, or leave Root Directory empty and set Dockerfile Path to `day12/Dockerfile` |
| Render: "Port scan timeout" / no open port | The `CMD` must use `$PORT`. Check `Dockerfile` still contains `${PORT:-8000}` |
| Render: out of memory | The free plan has 512 MB. Use Hugging Face Spaces (Option B) or a paid Render plan |
| `/health` takes about a minute | The free service was asleep. Wait and refresh |
| `/ask` returns 502 on the live site | `GROQ_API_KEY` or `GROQ_MODEL` is wrong in the Render environment variables |
| Hugging Face: "Missing app_port" or wrong page | `README.md` in the Space must start with the settings block from `deploy/huggingface/README.md` |
| PR cannot merge: conflicts | `git checkout feature/ci-and-deploy`, `git pull origin main`, fix the conflicts, push |
| `git push` rejected | `git pull origin <branch> --rebase`, then push again |

## 14. Final checklist

- [ ] `.github/workflows/ci.yml` is at the repo root and has ruff, pytest and docker build
- [ ] `ruff check .` and `pytest` pass inside `day12`
- [ ] Feature branch `feature/ci-and-deploy` pushed, pull request opened
- [ ] All 3 checks (ruff, pytest, docker build) were green before I merged
- [ ] The pull request is merged into `main`
- [ ] The CI badge is at the top of `day12/README.md` and of the root `README.md`, and it is green
- [ ] The service is deployed on Render or Hugging Face Spaces
- [ ] `<live URL>/health` opens in a browser on a different device or private window
- [ ] The live URL is in the README (the three "Live deployment" lines match the real URL)
- [ ] The live URL is pasted in the tracker
- [ ] Screenshots `ci-green.png` and `live-health.png` are in `docs/screenshots/`
- [ ] `.env` and `chroma_db/` are NOT committed
