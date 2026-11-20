---
title: PoshanGuide API
emoji: 🥗
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# PoshanGuide API

Nutrition Q&A for families, answered only from PoshanGuide documents, with citations.

- Health check: `/health`
- Interactive API docs: `/docs`
- Ask a question: `POST /ask` with `{"question": "Which foods are rich in iron for a 2-year-old?"}`

Set the secret `GROQ_API_KEY` (and the variables `LLM_PROVIDER=groq`, `GROQ_MODEL=llama-3.1-8b-instant`) in the Space settings.
