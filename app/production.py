"""
app/production.py  -  Day 13 production layer for PoshanGuide

One pure-ASGI middleware, so NO endpoint code has to change. It adds:

  1. Input limits            -> 413 (request body too big) / 422 (question too long)
  2. Prompt-injection guard  -> 400 (pattern check, runs BEFORE any LLM call)
  3. Simple cache            -> in-memory TTL cache for /ask and /chat (header X-Cache: HIT / MISS)
  4. Latency + token log     -> one JSON line per request in logs/requests.jsonl
  5. GET /metrics            -> summary (p50 / p95 latency, tokens, cache hit rate)

Hook it up in app/main.py with two lines:

    from app.production import install
    install(app)

Token counts: if app/llm.py calls record_usage(prompt_tokens, completion_tokens)
the REAL provider numbers are logged. If it does not, tokens are ESTIMATED
(about 4 characters = 1 token) and the log marks tokens_estimated = true.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
import time
from collections import OrderedDict
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs

# --------------------------------------------------------------------------
# Settings (change here, or override with environment variables / .env)
# --------------------------------------------------------------------------
MAX_QUESTION_CHARS = int(os.getenv("MAX_QUESTION_CHARS", "500"))   # input limit on the question
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", "10000"))         # input limit on the whole request body
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))     # how long a cached answer lives
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "200"))     # cache size
LOG_FILE = Path(os.getenv("REQUEST_LOG", "logs/requests.jsonl"))

GUARDED_PATHS = {"/ask", "/chat", "/agent"}   # paths the layer protects and logs
CACHEABLE_PATHS = {"/ask", "/chat"}           # /agent is NOT cached (it has memory + approval)

# --------------------------------------------------------------------------
# Prompt-injection guard (first line of defence, simple pattern list)
# --------------------------------------------------------------------------
_INJECTION_PATTERNS = [
    r"ignore (all |any |the )*(previous|prior|above|earlier|preceding) (instructions?|prompts?|rules?|messages?)",
    r"disregard (all |any |the )*(previous|prior|above|earlier|system) ?(instructions?|prompts?|rules?)?",
    r"forget (all |everything |your )*(previous |prior )?(instructions?|rules?)",
    r"(reveal|show|print|repeat|display|leak|tell me) (me )?(your |the )?(system|hidden|initial|original) (prompt|instructions?|message)",
    r"what (is|are) your (system|hidden|initial) (prompt|instructions?)",
    r"you are now (a|an|in) ",
    r"act as (an? )?(dan|unrestricted|jailbroken|evil)",
    r"pretend (that )?you (have no|are not bound|are free)",
    r"override (your )?(rules|safety|instructions|guidelines)",
    r"\bdeveloper mode\b",
    r"\bjailbreak",
    r"<\s*/?\s*system\s*>",
    r"begin system prompt",
]
INJECTION_REGEX = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def find_injection(text: str):
    """Return the matched text if the question looks like a prompt injection, else None."""
    for rx in INJECTION_REGEX:
        m = rx.search(text)
        if m:
            return m.group(0)
    return None


# --------------------------------------------------------------------------
# Token recording (called from app/llm.py)
# --------------------------------------------------------------------------
_usage: ContextVar = ContextVar("poshan_usage", default=None)


def record_usage(prompt_tokens=None, completion_tokens=None):
    """Call this from llm.py after each provider call. Safe to call outside a request."""
    u = _usage.get()
    if u is None:
        return
    u["calls"] += 1
    if prompt_tokens is not None or completion_tokens is not None:
        u["prompt"] += int(prompt_tokens or 0)
        u["completion"] += int(completion_tokens or 0)
        u["real"] = True


def _est_tokens(text: str) -> int:
    return max(1, round(len(text) / 4)) if text else 0


# --------------------------------------------------------------------------
# Simple cache: in-memory, TTL + size limit
# --------------------------------------------------------------------------
class TTLCache:
    def __init__(self, ttl: int, max_entries: int):
        self.ttl, self.max_entries = ttl, max_entries
        self._data: "OrderedDict[str, tuple[float, bytes]]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            expires, value = item
            if expires < time.time():
                del self._data[key]
                return None
            self._data.move_to_end(key)
            return value

    def set(self, key, value: bytes):
        with self._lock:
            self._data[key] = (time.time() + self.ttl, value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_entries:
                self._data.popitem(last=False)

    def clear(self):
        with self._lock:
            self._data.clear()

    def __len__(self):
        return len(self._data)


cache = TTLCache(CACHE_TTL_SECONDS, CACHE_MAX_ENTRIES)


def _normalise_question(q: str) -> str:
    return " ".join(q.lower().split())


def _cache_key(method: str, path: str, payload: dict) -> str:
    norm = dict(payload)
    if isinstance(norm.get("question"), str):
        norm["question"] = _normalise_question(norm["question"])
    raw = f"{method}|{path}|{json.dumps(norm, sort_keys=True, ensure_ascii=False)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Request log (JSON lines)
# --------------------------------------------------------------------------
_log_lock = threading.Lock()


def _write_log(rec: dict):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _log_lock, LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass  # logging must never break the API


def _token_fields(usage, question, resp_bytes):
    if usage["real"]:
        p, c, est = usage["prompt"], usage["completion"], False
    else:
        answer = ""
        try:
            data = json.loads(resp_bytes or b"{}")
            if isinstance(data, dict):
                answer = str(data.get("answer", ""))
        except ValueError:
            pass
        p, c, est = _est_tokens(question or ""), _est_tokens(answer), True
    return {"prompt_tokens": p, "completion_tokens": c, "total_tokens": p + c,
            "tokens_estimated": est, "llm_calls": usage["calls"]}


# --------------------------------------------------------------------------
# ASGI helpers
# --------------------------------------------------------------------------
async def _send_bytes(send, status: int, body: bytes, extra_headers: dict):
    headers = [(b"content-type", b"application/json"),
               (b"content-length", str(len(body)).encode())]
    for k, v in extra_headers.items():
        headers.append((k.lower().encode(), str(v).encode()))
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def _ms(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000, 1)


# --------------------------------------------------------------------------
# The middleware
# --------------------------------------------------------------------------
class ProductionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (scope["type"] != "http" or scope["path"] not in GUARDED_PATHS
                or scope["method"] not in ("GET", "POST")):
            await self.app(scope, receive, send)
            return

        t0 = time.perf_counter()
        path, method = scope["path"], scope["method"]
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "path": path, "method": method}
        zero_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                       "tokens_estimated": False, "llm_calls": 0}

        # ---- 1. read the body (POST) and enforce the body-size limit -------
        body = b""
        if method == "POST":
            more = True
            while more:
                msg = await receive()
                if msg["type"] == "http.disconnect":
                    return
                body += msg.get("body", b"")
                more = msg.get("more_body", False)
                if len(body) > MAX_BODY_BYTES:
                    await self._block(send, t0, rec, zero_tokens, 413, "request_too_large",
                                      f"Request body is larger than {MAX_BODY_BYTES} bytes.")
                    return

        # ---- 2. find the question ------------------------------------------
        payload, question = None, None
        if method == "POST":
            try:
                payload = json.loads(body) if body else {}
            except ValueError:
                payload = None          # invalid JSON: let the app answer with its own 422
            if isinstance(payload, dict):
                question = payload.get("question")
        else:
            params = parse_qs(scope.get("query_string", b"").decode("utf-8", "ignore"))
            payload = {k: v[0] for k, v in params.items()}
            question = payload.get("question")

        # ---- 3. input limit + injection guard (before any LLM call) --------
        if isinstance(question, str):
            rec["question_chars"] = len(question)
            if len(question) > MAX_QUESTION_CHARS:
                await self._block(send, t0, rec, zero_tokens, 422, "input_too_long",
                                  f"Question is longer than {MAX_QUESTION_CHARS} characters.")
                return
            hit = find_injection(question)
            if hit:
                await self._block(send, t0, rec, zero_tokens, 400, "prompt_injection",
                                  "This request looks like a prompt-injection attempt, so it was blocked. "
                                  "Please ask a nutrition question.")
                return

        # ---- 4. cache lookup ------------------------------------------------
        key = None
        if path in CACHEABLE_PATHS and isinstance(question, str) and isinstance(payload, dict):
            key = _cache_key(method, path, payload)
            cached = cache.get(key)
            if cached is not None:
                latency = _ms(t0)
                await _send_bytes(send, 200, cached,
                                  {"x-cache": "HIT", "x-latency-ms": f"{latency:.0f}"})
                rec.update(status=200, latency_ms=latency, cache="hit", **zero_tokens)
                _write_log(rec)
                return

        # ---- 5. call the real app, capture status / body / tokens -----------
        usage = {"prompt": 0, "completion": 0, "calls": 0, "real": False}
        token = _usage.set(usage)
        out = {"status": 500, "chunks": [], "ctype": ""}

        replayed = False

        async def app_receive():
            nonlocal replayed
            if method == "POST" and not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        async def app_send(message):
            if message["type"] == "http.response.start":
                out["status"] = message["status"]
                headers = list(message.get("headers", []))
                for k, v in headers:
                    if k.lower() == b"content-type":
                        out["ctype"] = v.decode("latin-1")
                headers.append((b"x-cache", b"MISS" if key else b"SKIP"))
                headers.append((b"x-latency-ms", f"{_ms(t0):.0f}".encode()))
                message = {**message, "headers": headers}
            elif message["type"] == "http.response.body":
                out["chunks"].append(message.get("body", b""))
            await send(message)

        try:
            await self.app(scope, app_receive, app_send)
        except Exception:
            rec.update(status=500, latency_ms=_ms(t0), cache="error",
                       **_token_fields(usage, question, b""))
            _write_log(rec)
            raise
        finally:
            _usage.reset(token)

        resp_bytes = b"".join(out["chunks"])
        if key and out["status"] == 200 and "json" in out["ctype"]:
            cache.set(key, resp_bytes)
        rec.update(status=out["status"], latency_ms=_ms(t0),
                   cache="miss" if key else "skip",
                   **_token_fields(usage, question if isinstance(question, str) else "", resp_bytes))
        _write_log(rec)

    async def _block(self, send, t0, rec, zero_tokens, status, reason, message):
        latency = _ms(t0)
        body = json.dumps({"detail": message, "blocked": reason}).encode()
        await _send_bytes(send, status, body, {"x-cache": "BLOCKED", "x-latency-ms": f"{latency:.0f}"})
        rec.update(status=status, latency_ms=latency, cache="blocked",
                   blocked_reason=reason, **zero_tokens)
        _write_log(rec)


# --------------------------------------------------------------------------
# Log summary (used by GET /metrics and eval/summarize_logs.py)
# --------------------------------------------------------------------------
def read_log(path=None):
    path = Path(path or LOG_FILE)
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    return rows


def percentile(values, p):
    if not values:
        return None
    s = sorted(values)
    return s[max(0, math.ceil(p / 100 * len(s)) - 1)]


def summarize(path=None):
    rows = read_log(path)
    total = len(rows)
    blocked = [r for r in rows if r.get("cache") == "blocked"]
    ok = [r for r in rows if r.get("status") == 200]
    miss = [r for r in ok if r.get("cache") in ("miss", "skip")]
    hit = [r for r in ok if r.get("cache") == "hit"]
    cacheable = len(miss) + len(hit)
    miss_lat = [r["latency_ms"] for r in miss]
    hit_lat = [r["latency_ms"] for r in hit]
    miss_tok = [r.get("total_tokens", 0) for r in miss]

    def avg(v):
        return round(sum(v) / len(v), 1) if v else None

    return {
        "requests_total": total,
        "requests_ok": len(ok),
        "requests_blocked": len(blocked),
        "blocked_by_reason": {k: sum(1 for r in blocked if r.get("blocked_reason") == k)
                              for k in sorted({r.get("blocked_reason") for r in blocked if r.get("blocked_reason")})},
        "cache_hits": len(hit),
        "cache_hit_rate_pct": round(100 * len(hit) / cacheable, 1) if cacheable else None,
        "latency_ms_uncached_p50": percentile(miss_lat, 50),
        "latency_ms_uncached_p95": percentile(miss_lat, 95),
        "latency_ms_uncached_avg": avg(miss_lat),
        "latency_ms_cache_hit_avg": avg(hit_lat),
        "tokens_per_uncached_request_avg": avg(miss_tok),
        "tokens_total": sum(r.get("total_tokens", 0) for r in rows),
        "tokens_estimated_share_pct": round(100 * sum(1 for r in miss if r.get("tokens_estimated")) / len(miss), 1) if miss else None,
    }


# --------------------------------------------------------------------------
# Hook-up helper
# --------------------------------------------------------------------------
def install(app):
    """Call once in app/main.py:  install(app)"""
    from fastapi import APIRouter   # imported here so this module also works without FastAPI

    router = APIRouter()

    @router.get("/metrics")
    def metrics():
        return summarize()

    app.add_middleware(ProductionMiddleware)
    app.include_router(router)
