"""Manuscript audit endpoint: citation gate and import obligations (ADR-DISCOVERY-077, ADR-DISCOVERY-082)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import ManuscriptAuditRequest
from api.security import require_api_key
from python.discovery import manuscript_audit
from python.discovery.formal_hypothesis import FormalHypothesisError

router = APIRouter()


@router.post("/api/manuscripts/audit", dependencies=[Depends(require_api_key)])
def audit_manuscript(req: ManuscriptAuditRequest):
    """Seams of one manuscript: unresolved citations and every import from a cited source as an OPEN obligation.

    `citation_gate.status` is PASS, FAIL, or NO_BIBLIOGRAPHY (then `formal_status` is UNDECIDED: the gate cannot
    judge, which is a non-verdict, never a pass). `imports` lists CONVENTION_TRANSFER, HYPOTHESIS_MATCH (MATCHED,
    UNMATCHED or NO_ENTRY against the optional `registry`), DEPENDENCY and EFFECTIVE_CONSTANT obligations with file
    and line. Detection is lexical; obligations are never discharged here. `claim_trust` is a view beside the report:
    a prose claim stays CLAIMED.
    """
    entries = [r.model_dump() for r in req.registry]
    if req.use_registry:
        from api.routers.registry import registry

        entries += registry().as_import_list()
    try:
        report = manuscript_audit.audit(
            req.files,
            entries,
            req.manuscript_status,
            req.collection,
            req.claim,
        )
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    view = manuscript_audit.claim_trust(report, req.claim)
    return {**report, "claim_trust": view["claim_trust"], "trust_relays": view["mandatory_relays"]}
