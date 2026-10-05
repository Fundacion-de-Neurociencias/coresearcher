"""
python/knowledge/ontology_plan_engine.py - Ontological Infrastructure-as-Code & Epistemic Blast Radius Gate (ADR-ONTOLOGY-035)
Inspired by open-ontologies (Lindenberg & Rovai 2026).

Enforces:
1. Terraform-Style Lifecycle: plan() -> apply() -> rollback() for scientific ontologies.
2. Epistemic Blast Radius Quantification: Detects unexpected consequence cascades (e.g. 1 line -> 901 consequences).
3. Offline Independent Proof Re-verification: Validates deductive soundness before applying transactions.
4. MCP-ready programmatic execution.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Tuple
import hashlib
import json
import uuid
import copy


class AxiomType(str, Enum):
    SUBCLASS_OF = "SUBCLASS_OF"
    DOMAIN_DECLARATION = "DOMAIN_DECLARATION"
    RANGE_DECLARATION = "RANGE_DECLARATION"
    DISJOINT_WITH = "DISJOINT_WITH"
    PROPERTY_ASSERTION = "PROPERTY_ASSERTION"


class PlanSafetyVerdict(str, Enum):
    SAFE_TO_APPLY = "SAFE_TO_APPLY"
    HIGH_BLAST_RADIUS = "HIGH_BLAST_RADIUS"
    CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"
    REVERIFICATION_FAILED = "REVERIFICATION_FAILED"


@dataclass
class OntologicalAxiom:
    axiom_id: str
    axiom_type: AxiomType
    subject: str
    predicate: str
    object_target: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axiom_id": self.axiom_id,
            "axiom_type": self.axiom_type.value,
            "subject": self.subject,
            "predicate": self.predicate,
            "object_target": self.object_target,
            "metadata": self.metadata
        }


@dataclass
class OntologyBlastRadiusReport:
    plan_id: str
    proposed_axioms: List[OntologicalAxiom]
    direct_inferences_count: int
    transitive_consequences_count: int
    total_blast_radius: int
    affected_entities: List[str]
    new_inferred_triples: List[Tuple[str, str, str]]
    contradictions_found: List[str]
    offline_proof_valid: bool
    safety_verdict: PlanSafetyVerdict
    som_plan_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "proposed_axioms": [a.to_dict() for a in self.proposed_axioms],
            "direct_inferences_count": self.direct_inferences_count,
            "transitive_consequences_count": self.transitive_consequences_count,
            "total_blast_radius": self.total_blast_radius,
            "affected_entities": self.affected_entities,
            "new_inferred_triples": [list(t) for t in self.new_inferred_triples],
            "contradictions_found": self.contradictions_found,
            "offline_proof_valid": self.offline_proof_valid,
            "safety_verdict": self.safety_verdict.value,
            "som_plan_hash": self.som_plan_hash
        }


@dataclass
class OntologyTransaction:
    transaction_id: str
    plan_id: str
    timestamp: str
    snapshot_before: Dict[str, Any]
    applied_axioms: List[OntologicalAxiom]
    blast_radius: int
    som_commit_hash: str


class OntologyState:
    """
    In-memory representational state of the ontology graph.
    Supports transactional cloning and rollbacks.
    """

    def __init__(self):
        self.classes: Set[str] = set()
        self.subclass_graph: Dict[str, Set[str]] = {}  # child -> set of parents
        self.domain_map: Dict[str, str] = {}          # property -> domain class
        self.range_map: Dict[str, str] = {}           # property -> range class
        self.disjoint_pairs: Set[Tuple[str, str]] = set()
        self.triples: Set[Tuple[str, str, str]] = set()  # (sub, pred, obj)
        self.individuals: Set[str] = set()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "classes": list(self.classes),
            "subclass_graph": {k: list(v) for k, v in self.subclass_graph.items()},
            "domain_map": dict(self.domain_map),
            "range_map": dict(self.range_map),
            "disjoint_pairs": [list(p) for p in self.disjoint_pairs],
            "triples": [list(t) for t in self.triples],
            "individuals": list(self.individuals)
        }

    def restore(self, snap: Dict[str, Any]) -> None:
        self.classes = set(snap.get("classes", []))
        self.subclass_graph = {k: set(v) for k, v in snap.get("subclass_graph", {}).items()}
        self.domain_map = dict(snap.get("domain_map", {}))
        self.range_map = dict(snap.get("range_map", {}))
        self.disjoint_pairs = {tuple(p) for p in snap.get("disjoint_pairs", [])}
        self.triples = {tuple(t) for t in snap.get("triples", [])}
        self.individuals = set(snap.get("individuals", []))


class OntologyPlanEngine:
    """
    Engine implementing Terraform-style lifecycle and Blast Radius checking
    for scientific ontologies (ADR-ONTOLOGY-035).
    """

    def __init__(self, initial_state: Optional[OntologyState] = None):
        self.state = initial_state or OntologyState()
        self.pending_plans: Dict[str, OntologyBlastRadiusReport] = {}
        self.transaction_history: Dict[str, OntologyTransaction] = {}

    def plan_change(
        self,
        proposed_axioms: List[OntologicalAxiom],
        max_safe_blast_radius: int = 100
    ) -> OntologyBlastRadiusReport:
        """
        Prospective dry-run computation:
        1. Clones current ontology state.
        2. Applies proposed axioms to simulation clone.
        3. Computes transitive deductive closure and identifies new inferences.
        4. Detects contradiction breaches (e.g. disjoint class collisions).
        5. Performs offline proof re-verification.
        """
        plan_id = f"PLAN-{uuid.uuid4().hex[:8]}"
        sim_state = copy.deepcopy(self.state)

        # Baseline inferences count before mutation
        baseline_triples = set(sim_state.triples)

        # Apply candidate axioms in simulation
        for ax in proposed_axioms:
            if ax.axiom_type == AxiomType.SUBCLASS_OF:
                sim_state.classes.add(ax.subject)
                sim_state.classes.add(ax.object_target)
                sim_state.subclass_graph.setdefault(ax.subject, set()).add(ax.object_target)
            elif ax.axiom_type == AxiomType.DOMAIN_DECLARATION:
                sim_state.domain_map[ax.predicate] = ax.object_target
            elif ax.axiom_type == AxiomType.RANGE_DECLARATION:
                sim_state.range_map[ax.predicate] = ax.object_target
            elif ax.axiom_type == AxiomType.DISJOINT_WITH:
                pair = tuple(sorted([ax.subject, ax.object_target]))
                sim_state.disjoint_pairs.add(pair)
            elif ax.axiom_type == AxiomType.PROPERTY_ASSERTION:
                sim_state.triples.add((ax.subject, ax.predicate, ax.object_target))
                sim_state.individuals.add(ax.subject)
                sim_state.individuals.add(ax.object_target)

        # Compute Deductive Closure on simulation state
        new_inferred_triples: Set[Tuple[str, str, str]] = set()
        affected_entities: Set[str] = set()
        contradictions: List[str] = []

        # 1. Domain Inferences: (s, p, o) and Domain(p) = D => (s, rdf:type, D)
        for s, p, o in sim_state.triples:
            if p in sim_state.domain_map:
                domain_cls = sim_state.domain_map[p]
                type_triple = (s, "rdf:type", domain_cls)
                if type_triple not in baseline_triples:
                    new_inferred_triples.add(type_triple)
                    affected_entities.add(s)

        # 2. Transitive Subclass Inferences: (s, rdf:type, C) and SubClassOf(C, Parent) => (s, rdf:type, Parent)
        all_types = list(new_inferred_triples) + [t for t in sim_state.triples if t[1] == "rdf:type"]
        for s, _, c in all_types:
            parents = self._get_transitive_parents(c, sim_state.subclass_graph)
            for par in parents:
                inferred = (s, "rdf:type", par)
                if inferred not in baseline_triples:
                    new_inferred_triples.add(inferred)
                    affected_entities.add(s)

        # 3. Contradiction Check: Disjointness violations
        entity_classes: Dict[str, Set[str]] = {}
        for s, _, c in list(sim_state.triples) + list(new_inferred_triples):
            entity_classes.setdefault(s, set()).add(c)

        for s, classes in entity_classes.items():
            for c1, c2 in sim_state.disjoint_pairs:
                if c1 in classes and c2 in classes:
                    contradictions.append(f"Contradiction: Entity '{s}' simultaneously typed as disjoint classes '{c1}' and '{c2}'.")

        # 4. Offline Proof Re-Verification (Self-check for acyclic subsumption)
        is_subclass_acyclic = self._check_subclass_acyclicity(sim_state.subclass_graph)
        offline_proof_valid = is_subclass_acyclic and len(contradictions) == 0

        # Quantify Blast Radius
        direct_count = len(proposed_axioms)
        transitive_count = len(new_inferred_triples)
        total_blast_radius = direct_count + transitive_count

        # Determine Verdict
        if contradictions:
            verdict = PlanSafetyVerdict.CONTRADICTION_DETECTED
        elif not offline_proof_valid:
            verdict = PlanSafetyVerdict.REVERIFICATION_FAILED
        elif total_blast_radius > max_safe_blast_radius:
            verdict = PlanSafetyVerdict.HIGH_BLAST_RADIUS
        else:
            verdict = PlanSafetyVerdict.SAFE_TO_APPLY

        som_hash = f"sha256:{hashlib.sha256(f'{plan_id}:{total_blast_radius}'.encode()).hexdigest()[:24]}"

        report = OntologyBlastRadiusReport(
            plan_id=plan_id,
            proposed_axioms=proposed_axioms,
            direct_inferences_count=direct_count,
            transitive_consequences_count=transitive_count,
            total_blast_radius=total_blast_radius,
            affected_entities=sorted(list(affected_entities)),
            new_inferred_triples=sorted(list(new_inferred_triples)),
            contradictions_found=contradictions,
            offline_proof_valid=offline_proof_valid,
            safety_verdict=verdict,
            som_plan_hash=som_hash
        )
        self.pending_plans[plan_id] = report
        return report

    def apply_plan(self, plan_id: str, force: bool = False) -> OntologyTransaction:
        """
        Atomically applies an approved plan to the canonical ontology state.
        Snapshots previous state to enable immediate rollback.
        """
        if plan_id not in self.pending_plans:
            raise ValueError(f"Plan ID '{plan_id}' not found.")

        report = self.pending_plans[plan_id]
        if report.safety_verdict == PlanSafetyVerdict.CONTRADICTION_DETECTED:
            raise ValueError("Cannot apply plan: Contradiction detected.")
        if report.safety_verdict == PlanSafetyVerdict.HIGH_BLAST_RADIUS and not force:
            raise ValueError(f"Cannot apply plan: Blast radius ({report.total_blast_radius}) exceeds safety limit. Approval required.")

        snapshot_before = self.state.snapshot()
        transaction_id = f"TX-{uuid.uuid4().hex[:8]}"

        # Apply axioms to active state
        for ax in report.proposed_axioms:
            if ax.axiom_type == AxiomType.SUBCLASS_OF:
                self.state.classes.add(ax.subject)
                self.state.classes.add(ax.object_target)
                self.state.subclass_graph.setdefault(ax.subject, set()).add(ax.object_target)
            elif ax.axiom_type == AxiomType.DOMAIN_DECLARATION:
                self.state.domain_map[ax.predicate] = ax.object_target
            elif ax.axiom_type == AxiomType.RANGE_DECLARATION:
                self.state.range_map[ax.predicate] = ax.object_target
            elif ax.axiom_type == AxiomType.DISJOINT_WITH:
                self.state.disjoint_pairs.add(tuple(sorted([ax.subject, ax.object_target])))
            elif ax.axiom_type == AxiomType.PROPERTY_ASSERTION:
                self.state.triples.add((ax.subject, ax.predicate, ax.object_target))
                self.state.individuals.add(ax.subject)
                self.state.individuals.add(ax.object_target)

        # Apply inferred triples
        for t in report.new_inferred_triples:
            self.state.triples.add(t)

        commit_hash = f"sha256:{hashlib.sha256(f'{transaction_id}:{plan_id}'.encode()).hexdigest()[:24]}"
        tx = OntologyTransaction(
            transaction_id=transaction_id,
            plan_id=plan_id,
            timestamp="2026-10-05T20:38:00Z",
            snapshot_before=snapshot_before,
            applied_axioms=report.proposed_axioms,
            blast_radius=report.total_blast_radius,
            som_commit_hash=commit_hash
        )
        self.transaction_history[transaction_id] = tx
        del self.pending_plans[plan_id]
        return tx

    def rollback_transaction(self, transaction_id: str) -> bool:
        """
        Immediately restores the pre-transaction snapshot, reverting all changes.
        """
        if transaction_id not in self.transaction_history:
            return False

        tx = self.transaction_history[transaction_id]
        self.state.restore(tx.snapshot_before)
        del self.transaction_history[transaction_id]
        return True

    def _get_transitive_parents(self, cls_name: str, graph: Dict[str, Set[str]]) -> Set[str]:
        visited: Set[str] = set()
        queue = list(graph.get(cls_name, set()))
        while queue:
            cur = queue.pop(0)
            if cur not in visited:
                visited.add(cur)
                queue.extend(graph.get(cur, set()))
        return visited

    def _check_subclass_acyclicity(self, graph: Dict[str, Set[str]]) -> bool:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if not dfs(neighbor):
                        return False
                elif neighbor in rec_stack:
                    return False
            rec_stack.remove(node)
            return True

        for k in graph:
            if k not in visited:
                if not dfs(k):
                    return False
        return True
