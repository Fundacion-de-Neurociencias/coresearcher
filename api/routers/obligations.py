"""Obligation ledgers of claimed mathematical results and the audit of their proofs (ADR-DISCOVERY-076)."""

from fastapi import APIRouter, HTTPException

from python.discovery.proof_cases import CASES

router = APIRouter()


def _summary(case) -> dict:
    claim = case.ledger_data()["claim"]
    audit = case.audit()
    return {
        "case_id": case.case_id,
        "title": case.title,
        "claim_status": claim["status"],
        "is_proved": claim["is_proved"],
        "obligations": len(claim["obligations"]),
        "audit_ok": audit["ok"],
    }


@router.get("/api/obligations/cases")
def list_proof_cases():
    """Every registered proof case with its claim status (weakest-link roll-up) and whether its audit passes."""
    return {"cases": [_summary(c) for c in CASES.values()]}


@router.get("/api/obligations/cases/{case_id}")
def get_proof_case(case_id: str):
    """The case's ledger (claim, obligations, discharges) and the audit of its proofs: every report present and
    verified, hashes equal to the manifest, no proof STALE against its sources, consistent roll-up. A claim's status
    is only reported together with its audit."""
    case = CASES.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"unknown proof case: {case_id}")
    return {**_summary(case), "ledger": case.ledger_data(), "audit": case.audit()}
