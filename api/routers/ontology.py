"""Ontology plan, apply and rollback endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Security  # noqa: F401

from api.schemas import (
    OntologyApplyPlanRequest,
    OntologyPlanChangeRequest,
    OntologyRollbackRequest,
)
from api.security import require_api_key
from api.state import (
    _global_ontology_engine,
)
from python.knowledge.ontology_plan_engine import (
    AxiomType,
    OntologicalAxiom,
)

router = APIRouter()


@router.post("/api/ontology/plan", dependencies=[Depends(require_api_key)])
def plan_ontology_change(req: OntologyPlanChangeRequest):
    """
    ADR-ONTOLOGY-035: Computes epistemic blast radius for proposed ontology mutations.
    """
    try:
        axioms = []
        for ax in req.proposed_axioms:
            ax_type = AxiomType(ax["axiom_type"])
            axioms.append(
                OntologicalAxiom(
                    axiom_id=ax.get("axiom_id", f"AX-{len(axioms)+1}"),
                    axiom_type=ax_type,
                    subject=ax.get("subject", ""),
                    predicate=ax.get("predicate", ""),
                    object_target=ax.get("object_target", ""),
                    metadata=ax.get("metadata", {}),
                )
            )
        report = _global_ontology_engine.plan_change(
            proposed_axioms=axioms, max_safe_blast_radius=req.max_safe_blast_radius or 100
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/ontology/apply", dependencies=[Depends(require_api_key)])
def apply_ontology_plan(req: OntologyApplyPlanRequest):
    """
    ADR-ONTOLOGY-035: Atomically applies an approved plan to the ontology state.
    """
    try:
        tx = _global_ontology_engine.apply_plan(plan_id=req.plan_id, force=req.force or False)
        return {
            "transaction_id": tx.transaction_id,
            "plan_id": tx.plan_id,
            "blast_radius": tx.blast_radius,
            "som_commit_hash": tx.som_commit_hash,
            "status": "APPLIED_SUCCESSFULLY",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/ontology/rollback", dependencies=[Depends(require_api_key)])
def rollback_ontology_transaction(req: OntologyRollbackRequest):
    """
    ADR-ONTOLOGY-035: Immediately rolls back a previously applied transaction.
    """
    try:
        success = _global_ontology_engine.rollback_transaction(transaction_id=req.transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Transaction '{req.transaction_id}' not found.")
        return {"transaction_id": req.transaction_id, "status": "ROLLED_BACK_SUCCESSFULLY"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
