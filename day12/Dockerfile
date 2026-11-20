# One image for the API (default) and the Streamlit UI.
# Works locally (docker compose), on Render (sets $PORT) and on Hugging Face Spaces (port 8000).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/code \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# run as a normal user (uid 1000), not as root: safer, and required by Hugging Face Spaces
RUN useradd --create-home --uid 1000 app

WORKDIR /code

# install packages first, so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app app ./app
COPY --chown=app:app ui ./ui
COPY --chown=app:app prompts ./prompts
COPY --chown=app:app documents ./documents
COPY --chown=app:app data ./data
RUN mkdir -p /code/chroma_db && chown -R app:app /code

USER app

# download the embedding model once at build time (about 80 MB), then build the search index,
# so the public service starts fast and /health answers straight away
RUN python -c "from app.embed import embed_texts; embed_texts(['warm up'])" \
    || echo "embedding model warm-up skipped: it will download on first use"
RUN python -m app.vectorstore \
    || echo "search index not built now: it is built on the first question"

EXPOSE 8000 8501

# $PORT is set by Render; Hugging Face Spaces and local Docker use 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
