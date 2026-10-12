"""Helpers for exercising the API in tests and demo scripts."""

import os
import secrets

from fastapi.testclient import TestClient

from api.security import API_KEY_ENV


def authenticated_client(app) -> TestClient:
    """Returns a TestClient that sends ``X-API-Key``.

    Uses ``CORESEARCHER_API_KEY`` when it is already configured; otherwise it
    generates a random key for the current process so write endpoints still work.
    """
    key = os.environ.setdefault(API_KEY_ENV, secrets.token_urlsafe(32))
    return TestClient(app, headers={"X-API-Key": key})
