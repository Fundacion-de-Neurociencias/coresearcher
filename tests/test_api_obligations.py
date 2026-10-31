"""API exposure of proof cases: ledger plus audit (ADR-076)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_proof_cases_listing_and_detail(api_client: TestClient):
    res = api_client.get("/api/obligations/cases")
    assert res.status_code == 200
    cases = {c["case_id"]: c for c in res.json()["cases"]}
    mahler = cases["mahler-scalar-input"]
    assert mahler["audit_ok"] is True and mahler["obligations"] == 24
    detail = api_client.get("/api/obligations/cases/mahler-scalar-input").json()
    assert detail["audit"]["ok"] and detail["ledger"]["claim"]["status"] == detail["claim_status"]
    assert set(detail["audit"]["steps"]) >= {"ranges", "segment_box", "segment_tails", "ledger"}
    assert api_client.get("/api/obligations/cases/nope").status_code == 404
