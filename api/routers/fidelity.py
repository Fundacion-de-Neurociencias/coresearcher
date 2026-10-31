"""Statement fidelity and trust-ladder endpoints (ADR-DISCOVERY-070, ADR-DISCOVERY-080)."""

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import FidelityCompareRequest, LeanLintRequest, TrustAssessRequest
from api.security import require_api_key
from python.discovery import fidelity_service, formal_trust
from python.discovery.formal_hypothesis import FormalHypothesisError

router = APIRouter()


@router.post("/api/fidelity/compare", dependencies=[Depends(require_api_key)])
def compare_statement_ranges(req: FidelityCompareRequest):
    """Paper range vs formal range of one theorem, decided by z3: the strength of the formal statement.

    `relation` is EQUIVALENT, STRONGER (the formal range is strictly larger), WEAKER or INCOMPARABLE, with a witness
    for every non-empty difference. When the solver gives up, or a division by zero is reachable in the encoding,
    `formal_status` is UNDECIDED and `undecided_reasons` says why; that is a non-verdict, never a relation.
    """
    spec = req.model_dump(exclude={"integer_values"})
    try:
        return fidelity_service.compare(spec, req.integer_values)
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/fidelity/lean-lint", dependencies=[Depends(require_api_key)])
def lint_lean_statement(req: LeanLintRequest):
    """Junk-value lint of a Lean statement file: every site of a total-function convention, DISCHARGED or OPEN.

    DISCHARGED names the statement text that rules the junk branch out; OPEN means a human decides. The lint is
    syntactic and never runs Lean, so the statement stays NOT_KERNEL_CHECKED.
    """
    try:
        return fidelity_service.lean_lint(req.source, req.file, [r.model_dump() for r in req.reviews])
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/trust/assess", dependencies=[Depends(require_api_key)])
def assess_claim_trust(req: TrustAssessRequest):
    """The trust-ladder rung of each claim, from recorded evidence, by mechanical rules.

    CLAIMED -> STATEMENT_PUBLIC -> STATEMENT_AUDITED -> KERNEL_CHECKED -> INDEPENDENTLY_REPRODUCED. Each rung reports
    whether it is met and, if not, which rule failed. NOT_KERNEL_CHECKED never counts as a kernel check.
    """
    try:
        assessments = [formal_trust.assess(item.model_dump(exclude_none=True)) for item in req.claims]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "schema": formal_trust.SCHEMA,
        "claim_trust": assessments,
        "mandatory_relays": formal_trust.relays(assessments),
    }
