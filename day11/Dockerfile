# One image for both services: the API (port 8000) and the Streamlit UI (port 8501).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/code \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /code

# install packages first, so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY ui ./ui
COPY prompts ./prompts
COPY documents ./documents
COPY data ./data

# download the embedding model once at build time (about 80 MB), so start-up is fast
RUN python -c "from app.embed import embed_texts; embed_texts(['warm up'])" \
    || echo "embedding model warm-up skipped: it will download on first use"

EXPOSE 8000 8501

# default command = the API; docker-compose.yml starts the UI with its own command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
