"""Provider wrapper for Groq / Gemini (Day 06).

Pick the provider with LLM_PROVIDER in .env (groq or gemini).
Keys are read from environment variables - never hard-code them.
"""
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

TIMEOUT = 40


class LLMError(RuntimeError):
    """Raised when the LLM provider call fails."""


def _groq(system_prompt: str, user_prompt: str, temperature: float) -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY is missing. Add it to your .env file.")
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        },
        timeout=TIMEOUT,
    )
    if not response.ok:
        raise LLMError(f"Groq error {response.status_code}: {response.text[:300]}")
    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Groq returned an unexpected response.") from exc
    if not isinstance(content, str) or not content.strip():
        raise LLMError("Groq returned an empty response.")
    return content


def _gemini(system_prompt: str, user_prompt: str, temperature: float) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is missing. Add it to your .env file.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key},
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        },
        timeout=TIMEOUT,
    )
    if not response.ok:
        raise LLMError(f"Gemini error {response.status_code}: {response.text[:300]}")
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Gemini returned an unexpected response.") from exc


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Send a prompt to the selected provider and return the raw text reply."""
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    try:
        if provider == "groq":
            return _groq(system_prompt, user_prompt, temperature)
        if provider == "gemini":
            return _gemini(system_prompt, user_prompt, temperature)
    except requests.RequestException as exc:
        raise LLMError(f"Network error talking to {provider}: {exc}") from exc
    raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use 'groq' or 'gemini'.")


def parse_json(text: str) -> dict:
    """Turn the model's reply into a dict (strips ```json fences if present)."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON response: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON response must be an object.")
    return value


def generate_response(prompt: str) -> str:
    """Retain the original single-prompt Groq helper."""
    try:
        return _groq("", prompt, temperature=0.2)
    except LLMError as exc:
        return f"Groq error: {exc}"
