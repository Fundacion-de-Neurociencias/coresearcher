"""Benchmarks as regression tests: the cases, their frozen expectations and a fresh check (ADR-DISCOVERY-084)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import RegressionCheckRequest
from api.security import require_api_key
from python.discovery import capability_regression

router = APIRouter()


@router.get("/api/regression/cases")
def regression_cases():
    """The regression cases, with the version and SHA-256 of the frozen expectations and each case's frozen
    observations. Expectations change only through `coresearcher regression update`, never through the API."""
    try:
        data = capability_regression.load_expectations()
    except capability_regression.ExpectationsError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "expectations_version": data["version"],
        "expectations_sha256": capability_regression.expectations_sha256(data),
        "cases": [dict(c, expected=data["cases"].get(c["id"])) for c in capability_regression.describe()],
        "history": data["history"],
    }


@router.post("/api/regression/check", dependencies=[Depends(require_api_key)])
def regression_check(req: RegressionCheckRequest):
    """Runs the selected cases (all when `case_ids` is empty) offline and compares them with the frozen expectations.

    `status` is PASS only when every observation equals its expectation. Otherwise it is the worst of ERROR (a case
    could not run), REGRESSION, FIXTURE_CHANGED, CHANGED and IMPROVEMENT (better, but not yet frozen).
    """
    try:
        return capability_regression.check(req.case_ids or None)
    except KeyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except capability_regression.ExpectationsError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
