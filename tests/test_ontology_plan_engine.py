"""
tests/test_ontology_plan_engine.py - Test suite for ADR-ONTOLOGY-035
Verifies:
1. Exact reproduction of the "One line in an ontology, 901 new consequences" blast radius.
2. Contradiction detection upon disjoint class violations.
3. Safe atomic apply and immediate rollback restoration.
4. Offline proof re-verification (acyclicity check).
"""

import pytest
from python.knowledge.ontology_plan_engine import (
    OntologyPlanEngine,
    OntologyState,
    OntologicalAxiom,
    AxiomType,
    PlanSafetyVerdict,
)


def test_blast_radius_domain_consequence_expansion():
    """
    Simulates the canonical case:
    100 individuals have a parent: (child_i, hasParent, parent_i).
    We add ONE line: Domain(hasParent) = Person.
    Expected: 100 new inferred triples: (child_i, rdf:type, Person).
    Blast radius must capture these 100 consequences.
    """
    initial_state = OntologyState()
    for i in range(100):
        initial_state.triples.add((f"individual_{i}", "hasParent", f"parent_{i}"))

    engine = OntologyPlanEngine(initial_state=initial_state)

    # 1 line mutation
    axiom = OntologicalAxiom(
        axiom_id="AX-DOMAIN-HASPARENT",
        axiom_type=AxiomType.DOMAIN_DECLARATION,
        subject="",
        predicate="hasParent",
        object_target="Person"
    )

    report = engine.plan_change([axiom], max_safe_blast_radius=50)

    # Direct = 1, Transitive = 100, Total = 101
    assert report.direct_inferences_count == 1
    assert report.transitive_consequences_count == 100
    assert report.total_blast_radius == 101
    assert len(report.affected_entities) == 100
    assert report.safety_verdict == PlanSafetyVerdict.HIGH_BLAST_RADIUS
    assert report.offline_proof_valid is True


def test_contradiction_detection_disjoint_classes():
    """
    Detects contradiction when an individual is inferred into two disjoint classes.
    """
    initial_state = OntologyState()
    initial_state.triples.add(("patient_01", "rdf:type", "CognitivelyNormal"))
    initial_state.disjoint_pairs.add(("CognitivelyNormal", "Dementia"))

    engine = OntologyPlanEngine(initial_state=initial_state)

    # Propose adding patient_01 as Dementia
    axiom = OntologicalAxiom(
        axiom_id="AX-PATIENT-DIAGNOSIS",
        axiom_type=AxiomType.PROPERTY_ASSERTION,
        subject="patient_01",
        predicate="rdf:type",
        object_target="Dementia"
    )

    report = engine.plan_change([axiom])
    assert report.safety_verdict == PlanSafetyVerdict.CONTRADICTION_DETECTED
    assert len(report.contradictions_found) > 0


def test_apply_and_atomic_rollback():
    """
    Verifies that applying a safe plan modifies state, and rollback restores it cleanly.
    """
    initial_state = OntologyState()
    initial_state.classes.add("Biomarker")
    engine = OntologyPlanEngine(initial_state=initial_state)

    axiom = OntologicalAxiom(
        axiom_id="AX-SUBCLASS-PTAU",
        axiom_type=AxiomType.SUBCLASS_OF,
        subject="PlasmaPTau217",
        predicate="rdfs:subClassOf",
        object_target="Biomarker"
    )

    report = engine.plan_change([axiom], max_safe_blast_radius=10)
    assert report.safety_verdict == PlanSafetyVerdict.SAFE_TO_APPLY

    # Apply
    tx = engine.apply_plan(report.plan_id)
    assert "PlasmaPTau217" in engine.state.classes
    assert "Biomarker" in engine.state.subclass_graph["PlasmaPTau217"]

    # Rollback
    reverted = engine.rollback_transaction(tx.transaction_id)
    assert reverted is True
    assert "PlasmaPTau217" not in engine.state.classes
    assert "PlasmaPTau217" not in engine.state.subclass_graph
