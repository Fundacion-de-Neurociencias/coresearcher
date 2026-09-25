"""
python/discovery/epistemic_stigmergy.py - Epistemic Stigmergy & Meta-Recursive Instrument Engine (ADR-DISCOVERY-027)
Inspired by Markus Buehler (MIT, SwarmWorld, arXiv 2608.26081) and harmonized with GeneForge & AIDataLab:
1. EpistemicPheromoneField: Converts the shared scientific git history (AgoraSharedIndex / EpistemicGitRepo)
   and CampaignLedger into active attractors and repulsors that steer autonomous agents without central planners.
2. MetaRecursiveInstrumentCompiler: Implements the Buehler loop (Representation -> Instrument -> Simulated World -> Law).
   Translates candidate hypotheses or formal representations into executable simulation worlds (ConstraintBox or dynamical solvers).
3. RealityContactFirewall: Anti-collective-hallucination firewall. Forbids self-referential closed-world theories
   by requiring an empirical Reality Contact Score (RCS >= 2.0) before promoting any emergent regularity into an invariant law.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import math
import hashlib
import json
import uuid

from python.discovery.scientific_git_history import EpistemicGitRepo, BranchStatus
from python.discovery.reality_contact_score import RealityContactLevel
from python.discovery.constraint_box import SyntheticWorldOracle, SyntheticConstraintRule, ConstraintTypeRule


class PheromoneType(str, Enum):
    ADVERSARIAL_ARBITRATION = "ADVERSARIAL_ARBITRATION"        # High uncertainty/conflict -> attracts Popper agents
    EPISTEMIC_GAP_EXPLORATION = "EPISTEMIC_GAP_EXPLORATION"    # Unmapped state space -> attracts Miners/Explorers
    EMPIRICAL_AUDIT_REQUIRED = "EMPIRICAL_AUDIT_REQUIRED"      # RCS < 2.0 -> attracts Validation Auditors
    INVARIANT_CONSOLIDATION = "INVARIANT_CONSOLIDATION"        # Stable branches -> attracts Formalizers for cherry-picking
    REFUTATION_REPULSION = "REFUTATION_REPULSION"              # Graveyard refutations -> repels agents from dead ends


@dataclass
class EpistemicPheromone:
    pheromone_id: str
    pheromone_type: PheromoneType
    intensity: float  # [0.0, 1.0]
    target_entity_id: str
    target_branch_id: Optional[str] = None
    source_commit_sha: Optional[str] = None
    epistemic_context: str = ""
    decay_rate_per_epoch: float = 0.05
    created_at_epoch: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pheromone_id": self.pheromone_id,
            "pheromone_type": self.pheromone_type.value,
            "intensity": round(self.intensity, 4),
            "target_entity_id": self.target_entity_id,
            "target_branch_id": self.target_branch_id,
            "source_commit_sha": self.source_commit_sha,
            "epistemic_context": self.epistemic_context,
            "decay_rate_per_epoch": self.decay_rate_per_epoch,
            "created_at_epoch": self.created_at_epoch,
        }


@dataclass
class PheromoneLandscapeReport:
    total_active_pheromones: int
    strongest_attractor: Optional[EpistemicPheromone]
    strongest_repulsor: Optional[EpistemicPheromone]
    attractors: List[Dict[str, Any]]
    repulsors: List[Dict[str, Any]]
    recommended_swarm_role: str
    som_landscape_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_active_pheromones": self.total_active_pheromones,
            "strongest_attractor": self.strongest_attractor.to_dict() if self.strongest_attractor else None,
            "strongest_repulsor": self.strongest_repulsor.to_dict() if self.strongest_repulsor else None,
            "attractors": self.attractors,
            "repulsors": self.repulsors,
            "recommended_swarm_role": self.recommended_swarm_role,
            "som_landscape_hash": self.som_landscape_hash,
        }


class EpistemicPheromoneField:
    """
    Computes and maintains active stigmergic pheromones across the shared EpistemicGitRepo.
    Enables autonomous agent swarms to organize without a central planner.
    """

    @classmethod
    def scan_git_repository(
        cls,
        repo: EpistemicGitRepo,
        uncertainty_threshold: float = 0.60
    ) -> PheromoneLandscapeReport:
        pheromones: List[EpistemicPheromone] = []

        # 1. Scan verified claims -> emit INVARIANT_CONSOLIDATION attractors
        verified_claims = list(repo.agora_index.verified_claims.values())
        for claim in verified_claims:
            p = EpistemicPheromone(
                pheromone_id=f"PHERO-CONSOL-{claim.claim_id[:12]}",
                pheromone_type=PheromoneType.INVARIANT_CONSOLIDATION,
                intensity=min(0.95, 0.40 + 0.20 * claim.rcs_score),
                target_entity_id=claim.entity_id,
                source_commit_sha=claim.commit_sha,
                epistemic_context=f"Verified invariant ({claim.statement[:40]}...) available for cross-branch cherry-picking."
            )
            pheromones.append(p)

        # 2. Scan open branches -> evaluate activity and unmapped frontiers
        open_branches = repo.agora_index.get_open_branches()
        for b in open_branches:
            if b.status == BranchStatus.ACTIVE:
                # Active branch with unresolved exploration
                p = EpistemicPheromone(
                    pheromone_id=f"PHERO-GAP-{b.branch_id[:12]}",
                    pheromone_type=PheromoneType.EPISTEMIC_GAP_EXPLORATION,
                    intensity=0.75,
                    target_entity_id=b.branch_id,
                    target_branch_id=b.branch_id,
                    source_commit_sha=b.head_commit_sha,
                    epistemic_context=f"Open branch topic '{b.research_topic[:35]}' needs candidate hypotheses."
                )
                pheromones.append(p)

        # 3. Scan commits for conflict/refutation -> emit ADVERSARIAL_ARBITRATION or REFUTATION_REPULSION
        for sha, commit in repo.commits.items():
            trigger = commit.mutation_trigger.lower()
            if "refut" in trigger or "counterexample" in trigger or "fail" in trigger:
                # Negative pheromone repelling exploration of dead ends
                p_rep = EpistemicPheromone(
                    pheromone_id=f"PHERO-REPEL-{sha[:10]}",
                    pheromone_type=PheromoneType.REFUTATION_REPULSION,
                    intensity=0.90,
                    target_entity_id=commit.entity_id,
                    source_commit_sha=sha,
                    epistemic_context=f"Hypothesis refuted by trigger: '{commit.mutation_trigger[:50]}'. Do not repeat."
                )
                pheromones.append(p_rep)
            elif "conflict" in trigger or "uncertainty" in trigger:
                # High uncertainty -> Popper adversarial arbitration
                p_arb = EpistemicPheromone(
                    pheromone_id=f"PHERO-ARB-{sha[:10]}",
                    pheromone_type=PheromoneType.ADVERSARIAL_ARBITRATION,
                    intensity=0.85,
                    target_entity_id=commit.entity_id,
                    source_commit_sha=sha,
                    epistemic_context=f"Conflicting evidence on {commit.entity_id}. Demands Modus Tollens audit."
                )
                pheromones.append(p_arb)

        # Separate attractors and repulsors
        attractors = [p for p in pheromones if p.pheromone_type != PheromoneType.REFUTATION_REPULSION]
        repulsors = [p for p in pheromones if p.pheromone_type == PheromoneType.REFUTATION_REPULSION]

        strongest_att = max(attractors, key=lambda x: x.intensity) if attractors else None
        strongest_rep = max(repulsors, key=lambda x: x.intensity) if repulsors else None

        # Determine recommended role spontaneously for an unassigned agent
        if strongest_att:
            if strongest_att.pheromone_type == PheromoneType.ADVERSARIAL_ARBITRATION:
                role = "POPPER_ADVERSARIAL_AUDITOR"
            elif strongest_att.pheromone_type == PheromoneType.EPISTEMIC_GAP_EXPLORATION:
                role = "HYPOTHESIS_EXPLORER"
            elif strongest_att.pheromone_type == PheromoneType.INVARIANT_CONSOLIDATION:
                role = "INVARIANT_FORMALIZER"
            else:
                role = "VALIDATION_AUDITOR"
        else:
            role = "AUTONOMOUS_SCOUT"

        # Generate cryptographic SOM landscape hash
        payload_repr = json.dumps([p.to_dict() for p in pheromones], sort_keys=True)
        som_hash = f"sha256:{hashlib.sha256(payload_repr.encode('utf-8')).hexdigest()[:24]}"

        return PheromoneLandscapeReport(
            total_active_pheromones=len(pheromones),
            strongest_attractor=strongest_att,
            strongest_repulsor=strongest_rep,
            attractors=[p.to_dict() for p in attractors],
            repulsors=[p.to_dict() for p in repulsors],
            recommended_swarm_role=role,
            som_landscape_hash=som_hash
        )


@dataclass
class MetaRecursiveInstrument:
    instrument_id: str
    target_representation_id: str
    simulated_world_id: str
    executable_rules: List[Dict[str, Any]]
    computational_cost_units: int
    is_compiled: bool
    som_instrument_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "target_representation_id": self.target_representation_id,
            "simulated_world_id": self.simulated_world_id,
            "executable_rules": self.executable_rules,
            "computational_cost_units": self.computational_cost_units,
            "is_compiled": self.is_compiled,
            "som_instrument_hash": self.som_instrument_hash,
        }


class MetaRecursiveInstrumentCompiler:
    """
    Implements the Buehler Meta-Recursive Loop:
    (Representation -> Instrument -> Simulated World -> Law -> Next-Scale Representation).
    Compiles candidate hypotheses into executable simulation worlds for agent swarm exploration.
    """

    @classmethod
    def compile_hypothesis_into_world(
        cls,
        representation_id: str,
        hypothesis_statement: str,
        key_variables: List[str]
    ) -> MetaRecursiveInstrument:
        inst_id = f"INST-{uuid.uuid4().hex[:8].upper()}"
        world_id = f"WORLD-SIM-{uuid.uuid4().hex[:6].upper()}"

        rules: List[Dict[str, Any]] = []

        # Parse cues into simulated constraints
        stmt_lower = hypothesis_statement.lower()
        if "necessary" in stmt_lower or "requires" in stmt_lower:
            var1 = key_variables[0] if len(key_variables) > 0 else "VAR_A"
            var2 = key_variables[1] if len(key_variables) > 1 else "VAR_B"
            rules.append({
                "rule_type": ConstraintTypeRule.NECESSARY_CONDITION.value,
                "operands": [var1, var2],
                "formal_logic": f"({var1} > 0.50 ∧ {var2} > 0.50) is necessary for activation",
                "threshold": 0.50
            })
        elif "inhibits" in stmt_lower or "suppress" in stmt_lower or "blocks" in stmt_lower:
            var = key_variables[0] if key_variables else "SUPPRESSOR_FACTOR"
            rules.append({
                "rule_type": ConstraintTypeRule.SUFFICIENT_TRIGGER.value,
                "operands": [var],
                "formal_logic": f"{var} > 0.70 sufficiently suppresses downstream activation",
                "threshold": 0.70
            })
        else:
            # Default boundary threshold rule
            var = key_variables[0] if key_variables else "BIOMARKER_ALPHA"
            rules.append({
                "rule_type": ConstraintTypeRule.BOUNDARY_THRESHOLD.value,
                "operands": [var],
                "formal_logic": f"{var} must not exceed critical boundary 0.85",
                "threshold": 0.85
            })

        # Cryptographic hash
        payload = json.dumps({
            "iid": inst_id,
            "rep": representation_id,
            "rules": rules
        }, sort_keys=True)
        som_hash = f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]}"

        return MetaRecursiveInstrument(
            instrument_id=inst_id,
            target_representation_id=representation_id,
            simulated_world_id=world_id,
            executable_rules=rules,
            computational_cost_units=len(rules) * 50,
            is_compiled=True,
            som_instrument_hash=som_hash
        )


@dataclass
class RealityContactFirewallReport:
    hypothesis_id: str
    rcs_level: int
    is_firewall_passed: bool
    rejection_reason: Optional[str] = None
    epistemic_directive: str = ""
    som_firewall_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "rcs_level": self.rcs_level,
            "is_firewall_passed": self.is_firewall_passed,
            "rejection_reason": self.rejection_reason,
            "epistemic_directive": self.epistemic_directive,
            "som_firewall_hash": self.som_firewall_hash,
        }


class RealityContactFirewall:
    """
    Anti-Collective-Hallucination Firewall.
    Enforces the mandatory rule: No simulation-derived law or emergent theory
    can be promoted to an active invariant unless RCS >= 2.0 (external empirical grounding).
    """

    MINIMUM_RCS_PROMOTION_THRESHOLD = RealityContactLevel.LEVEL_2_PROSPECTIVE_HOLDOUT

    @classmethod
    def audit_promotion_request(
        cls,
        hypothesis_id: str,
        claimed_regularity: str,
        rcs_level: int,
        empirical_anchors: List[str]
    ) -> RealityContactFirewallReport:
        passed = (rcs_level >= int(cls.MINIMUM_RCS_PROMOTION_THRESHOLD)) and (len(empirical_anchors) > 0)

        if not passed:
            reason = (
                f"BLOCKED: Swarm theory '{claimed_regularity[:50]}' achieved RCS Level {rcs_level}, "
                f"below required Level 2 (External Holdout / Physical Contact). "
                f"Theory remains quarantined as In-Silico Simulation speculation."
            )
            directive = "REJECT_PROMOTION_AND_DEMAND_PHYSICAL_BENCHMARK"
        else:
            reason = None
            directive = "PROMOTE_TO_INVARIANT_CONSTRAINT"

        raw = json.dumps({
            "hid": hypothesis_id,
            "rcs": rcs_level,
            "passed": passed,
            "anchors": sorted(empirical_anchors)
        }, sort_keys=True)
        som_hash = f"sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"

        return RealityContactFirewallReport(
            hypothesis_id=hypothesis_id,
            rcs_level=rcs_level,
            is_firewall_passed=passed,
            rejection_reason=reason,
            epistemic_directive=directive,
            som_firewall_hash=som_hash
        )
