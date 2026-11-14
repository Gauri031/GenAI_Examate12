# Checkpoint 1 – FastAPI is running

## How I ran it
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then opened: http://127.0.0.1:8000/docs

## Proof
![FastAPI /docs page](screenshots/fastapi-docs.png)

> **[EDIT]** Save your browser screenshot of `/docs` as `docs/screenshots/fastapi-docs.png`.

## One function explained  **[EDIT with your real function]**

```python
@app.get("/ask")
def ask(question: str):
    # 1. take the user's question from the URL
    # 2. search our data for matching info
    # 3. if nothing relevant is found -> say we can't answer
    # 4. otherwise return the answer
    ...
```

- **What it does:** receives a question and returns an answer from PoshanGuide data.
- **Input:** `question` (text) sent as a query parameter.
- **Output:** JSON like `{"answer": "..."}`.
- **Why it matters:** this is the entry point of the app; FastAPI reads the type hint (`str`) and auto-validates input and builds the `/docs` page.
- **Edge case:** if the data has no answer (like Q6), it must say so instead of guessing.
