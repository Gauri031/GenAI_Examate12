# Day 07 - git steps (from the repo root)

```powershell
Add-Content .gitignore "`nchroma_db/"
git check-ignore -v day07/.env
git add -A day07 .gitignore
git status
git commit -m "Day 07: chunking, embeddings, Chroma vectorstore, semantic search"
git push origin main
```
Before committing, `day07/.env` and `day07/chroma_db/` must NOT appear in `git status`.
