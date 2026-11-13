"""Reads settings from the ONE global .env at the repo root (../../.env from this file)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
ENV_FILE = ROOT / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except ImportError:  # python-dotenv not installed: minimal fallback parser
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

APP_NAME = os.getenv("APP_NAME", "PoshanGuide")
APP_ENV = os.getenv("APP_ENV", "development")
SUGAR_LIMIT_G = float(os.getenv("SUGAR_LIMIT_G", "25"))
SALT_LIMIT_G = float(os.getenv("SALT_LIMIT_G", "5"))
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
