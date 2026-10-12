"""Security controls of the HTTP API: write authentication, webhook HMAC, CORS and rate limiting."""

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from api.security import API_KEY_ENV, RATE_LIMIT_ENV, WEBHOOK_SECRET_ENV
from api.server import app

WRITE_URL = "/api/discovery/system-one/triage-pr?diff_text=print(1)"
WEBHOOK_URL = "/api/discovery/github/audit-pr-webhook"
API_KEY = "test-key-123"


@pytest.fixture
def anonymous_client() -> TestClient:
    return TestClient(app, client=("10.1.1.1", 1234))


@pytest.fixture
def configured_key(monkeypatch) -> str:
    monkeypatch.setenv(API_KEY_ENV, API_KEY)
    return API_KEY


def test_write_without_key_is_rejected(anonymous_client, configured_key):
    response = anonymous_client.post(WRITE_URL)
    assert response.status_code == 401


def test_write_with_wrong_key_is_rejected(anonymous_client, configured_key):
    response = anonymous_client.post(WRITE_URL, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_write_with_valid_key_is_accepted(anonymous_client, configured_key):
    response = anonymous_client.post(WRITE_URL, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200


def test_writes_fail_closed_when_no_key_is_configured(anonymous_client, monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    response = anonymous_client.post(WRITE_URL, headers={"X-API-Key": "anything"})
    assert response.status_code == 503


def test_read_endpoints_stay_public(anonymous_client):
    assert anonymous_client.get("/api/health").status_code == 200


def test_cors_allows_default_local_origin_only(anonymous_client):
    # CORS origins are read when the app is created, so this checks the defaults.
    allowed = anonymous_client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    denied = anonymous_client.get("/api/health", headers={"Origin": "https://evil.example"})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers


def _sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_webhook_disabled_without_secret(anonymous_client, monkeypatch):
    monkeypatch.delenv(WEBHOOK_SECRET_ENV, raising=False)
    response = anonymous_client.post(WEBHOOK_URL, content=b"{}", headers={"X-Hub-Signature-256": "sha256=x"})
    assert response.status_code == 503


def test_webhook_rejects_bad_signature(anonymous_client, monkeypatch):
    monkeypatch.setenv(WEBHOOK_SECRET_ENV, "gh-secret")
    body = json.dumps({"action": "opened"}).encode("utf-8")
    response = anonymous_client.post(
        WEBHOOK_URL, content=body, headers={"X-Hub-Signature-256": _sign("other-secret", body)}
    )
    assert response.status_code == 401


def test_webhook_rejects_missing_signature(anonymous_client, monkeypatch):
    monkeypatch.setenv(WEBHOOK_SECRET_ENV, "gh-secret")
    response = anonymous_client.post(WEBHOOK_URL, content=b"{}")
    assert response.status_code == 401


def test_webhook_accepts_valid_signature(anonymous_client, monkeypatch):
    monkeypatch.setenv(WEBHOOK_SECRET_ENV, "gh-secret")
    body = json.dumps({"action": "opened"}).encode("utf-8")
    response = anonymous_client.post(
        WEBHOOK_URL, content=body, headers={"X-Hub-Signature-256": _sign("gh-secret", body)}
    )
    # The signature passes; any remaining status comes from the payload model, not auth.
    assert response.status_code not in (401, 503)


def test_rate_limit_returns_429_after_threshold(monkeypatch):
    monkeypatch.setenv(RATE_LIMIT_ENV, "3")
    client = TestClient(app, client=("10.9.9.9", 4321))
    statuses = [client.get("/api/health").status_code for _ in range(4)]
    assert statuses[:3] == [200, 200, 200]
    assert statuses[3] == 429
