"""Authentication, webhook signature verification and rate limiting for the API.

Configuration is read from environment variables at request time:

- ``CORESEARCHER_API_KEY``: shared secret sent in the ``X-API-Key`` header. Every
  POST, PUT and DELETE endpoint requires it. If it is unset, those endpoints
  refuse every request (fail closed).
- ``CORESEARCHER_GITHUB_WEBHOOK_SECRET``: secret used to verify the
  ``X-Hub-Signature-256`` header that GitHub sends with each webhook delivery.
- ``CORESEARCHER_RATE_LIMIT_PER_MINUTE``: maximum requests per client IP per
  minute (default 120).
"""

import hashlib
import hmac
import os
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

API_KEY_ENV = "CORESEARCHER_API_KEY"
WEBHOOK_SECRET_ENV = "CORESEARCHER_GITHUB_WEBHOOK_SECRET"
RATE_LIMIT_ENV = "CORESEARCHER_RATE_LIMIT_PER_MINUTE"
DEFAULT_RATE_LIMIT = 120

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Rejects write requests unless ``X-API-Key`` matches the configured key."""
    expected = os.environ.get(API_KEY_ENV, "")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail=f"Write endpoints are disabled until {API_KEY_ENV} is configured.",
        )
    if not api_key or not hmac.compare_digest(api_key, expected):
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")


async def verify_github_signature(request: Request) -> None:
    """Rejects webhook deliveries whose HMAC-SHA256 signature does not match the body."""
    secret = os.environ.get(WEBHOOK_SECRET_ENV, "")
    if not secret:
        raise HTTPException(
            status_code=503,
            detail=f"GitHub webhook is disabled until {WEBHOOK_SECRET_ENV} is configured.",
        )
    body = await request.body()
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    received = request.headers.get("X-Hub-Signature-256", "")
    if not hmac.compare_digest(received, expected):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature.")


def _rate_limit_per_minute() -> int:
    try:
        return int(os.environ.get(RATE_LIMIT_ENV, DEFAULT_RATE_LIMIT))
    except ValueError:
        return DEFAULT_RATE_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window limit per client IP, kept in process memory."""

    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with self._lock:
            hits = self._hits[client]
            while hits and now - hits[0] > 60:
                hits.popleft()
            if len(hits) >= _rate_limit_per_minute():
                return JSONResponse(
                    {"detail": "Rate limit exceeded. Try again in a minute."},
                    status_code=429,
                    headers={"Retry-After": "60"},
                )
            hits.append(now)
        return await call_next(request)
