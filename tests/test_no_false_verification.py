"""Regression tests: an engine must never report a verification it did not perform."""

import shutil

from python.discovery.exact_symbolic_court import (
    EpistemicLemmaStatus,
    ExactLemmaNode,
    ExactProofDAG,
    ExactSymbolicCourt,
    ExactSymbolicVerdict,
)
from python.discovery.lean_formalization_engine import LeanFormalizationEngine, LeanProofStatus
from python.discovery.result_family_orchestrator import ResultFamilyOrchestrator, ResultRole
from python.observer.scientific_ledger import ScientificLedger


def _dag(theorem_id: str) -> ExactProofDAG:
    dag = ExactProofDAG(theorem_id=theorem_id)
    dag.add_lemma(ExactLemmaNode(lemma_id="L1", statement="anything", status=EpistemicLemmaStatus.PROVEN_LEMMA))
    return dag


def test_exact_court_without_target_is_not_verified():
    report = ExactSymbolicCourt.audit_exact_proof(_dag("NO-TARGET"))
    assert report.verdict == ExactSymbolicVerdict.NO_CHECKABLE_TARGET
    assert report.is_sound is False


def test_exact_court_sequence_without_recurrence_is_not_verified():
    report = ExactSymbolicCourt.audit_exact_proof(_dag("SEQ-ONLY"), sequence_benchmark=[1, 1, 2, 3, 5])
    assert report.verdict == ExactSymbolicVerdict.NO_CHECKABLE_TARGET


def test_exact_court_still_verifies_a_true_identity():
    report = ExactSymbolicCourt.audit_exact_proof(_dag("ID"), lhs_target="(x+1)**2", rhs_target="x**2+2*x+1")
    assert report.verdict == ExactSymbolicVerdict.VERIFIED_EXACT_THEOREM
    assert report.is_sound is True


def test_lean_without_binary_is_not_kernel_verified():
    report = LeanFormalizationEngine.audit_lean_source("T", "theorem T : 1 + 1 = 2 := by norm_num")
    if shutil.which("lean") is None:
        assert report.status == LeanProofStatus.NOT_KERNEL_CHECKED
        assert report.is_kernel_sound is False


def test_synthesized_scaffold_never_counts_as_formalization():
    orchestrator = ResultFamilyOrchestrator("FAM-SCAFFOLD", "Scaffold only")
    orchestrator.add_manuscript_node(
        node_id="N1",
        title="Prose claim",
        role=ResultRole.CORE_THEOREM,
        statement="A claim with no Lean file",
        has_lean_formalization=True,
    )
    verdict = orchestrator.audit_family_epistemic_integrity()
    assert verdict.formalized_nodes_count == 0
    assert verdict.is_epistemically_sound is False


def test_holonomy_is_checked_when_parallel_paths_exist():
    orchestrator = ResultFamilyOrchestrator("FAM-DIAMOND", "Diamond")
    orchestrator.add_manuscript_node(node_id="A", title="A", role=ResultRole.CORE_THEOREM, statement="a")
    orchestrator.add_manuscript_node(
        node_id="B", title="B", role=ResultRole.BRIDGE_LEMMA, statement="b", parent_lemma_ids=["A"]
    )
    orchestrator.add_manuscript_node(
        node_id="C", title="C", role=ResultRole.BRIDGE_LEMMA, statement="c", parent_lemma_ids=["A"]
    )
    orchestrator.add_manuscript_node(
        node_id="D", title="D", role=ResultRole.ALTERNATIVE_PROOF, statement="d", parent_lemma_ids=["B", "C"]
    )
    verdict = orchestrator.audit_family_epistemic_integrity()
    assert verdict.holonomy_checked is True


def test_ledger_record_event_is_recorded():
    ledger = ScientificLedger(ledger_id="L", name="test")
    entry = ledger.record_event("TEST_EVENT", {"question_id": "Q-1", "value": 3})
    assert entry["artifact_id"] == "Q-1"
    assert entry["verdict_type"] == "TEST_EVENT"
    assert ledger.artifacts[-1]["som_merkle_hash"].startswith("sha256:")
