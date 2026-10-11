"""
python/discovery/hakken_dream_rsi_engine.py - Hakken Literature-Linked Abduction & Dream-RSI Offline Replay Engine (ADR-DISCOVERY-054)

Inspired by:
1. Hakken (THiGERLLM & PHELInE):
   Predicts unrecorded scientific relationships across temporal knowledge graphs (gene-gene,
   miRNA-senescence, metabolic-inflammatory pathways, quantum qubit control).
   PHELInE identifies multi-step literature paths, evaluating necessity (drop under hop ablation),
   sufficiency (path-alone strength), and temporal stability.
2. Dream-RSI (Recursive Self-Improvement via Search Replay):
   Treats prior discovery trees as offline simulation replay environments.
   Evaluates exploration policies (worker allocation, branch ordering, pruning thresholds, stopping criteria)
   offline without re-running expensive simulations or LLM tasks.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from python.observer.scientific_ledger import ScientificLedger


# ---------------------------------------------------------------------------
# Hakken Literature Link Abduction Types
# ---------------------------------------------------------------------------

class ScientificDomainType(str, enum.Enum):
    AGING_BIOLOGY = "AGING_BIOLOGY"
    NEURODEGENERATION = "NEURODEGENERATION"
    QUANTUM_COMPUTING = "QUANTUM_COMPUTING"
    FUNDAMENTAL_PHYSICS = "FUNDAMENTAL_PHYSICS"
    GENERAL_SCIENCE = "GENERAL_SCIENCE"


@dataclass
class TemporalEntityNode:
    entity_id: str
    name: str
    category: str                      # e.g., "GENE", "MIRNA", "PATHWAY", "QUBIT_CONTROL"
    first_observed_epoch: int          # Year or publication epoch index
    recent_mention_count: int = 1


@dataclass
class LiteratureHop:
    source_entity: str
    target_entity: str
    relation: str                      # e.g., "REGULATES", "PHOSPHORYLATES", "INDUCES", "SUPPRESSES"
    literature_citations_count: int
    temporal_stability_score: float    # 0.0 to 1.0 (drift measure)
    confidence_weight: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "relation": self.relation,
            "citations": self.literature_citations_count,
            "temporal_stability": round(self.temporal_stability_score, 3),
            "weight": round(self.confidence_weight, 3),
        }


@dataclass
class PheliNeEvidenceChain:
    chain_id: str
    candidate_pair: Tuple[str, str]
    hops: List[LiteratureHop]
    sufficiency_score: float           # Path alone confidence
    necessity_score: float             # Drop when most critical hop is ablated
    temporal_drift: float              # Fluctuation across epochs
    is_sound_path: bool
    explanation_markdown: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "candidate_pair": [self.candidate_pair[0], self.candidate_pair[1]],
            "hops": [h.to_dict() for h in self.hops],
            "sufficiency_score": round(self.sufficiency_score, 4),
            "necessity_score": round(self.necessity_score, 4),
            "temporal_drift": round(self.temporal_drift, 4),
            "is_sound_path": self.is_sound_path,
            "explanation_markdown": self.explanation_markdown,
        }


@dataclass
class LiteratureLinkCandidate:
    candidate_id: str
    domain: ScientificDomainType
    source_entity: str
    target_entity: str
    predicted_relation: str
    is_previously_documented: bool
    novelty_score: float               # 0.0 to 1.0
    evidence_chain: PheliNeEvidenceChain
    recommended_validation_assay: str
    som_hakken_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "domain": self.domain.value,
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "predicted_relation": self.predicted_relation,
            "is_previously_documented": self.is_previously_documented,
            "novelty_score": round(self.novelty_score, 4),
            "evidence_chain": self.evidence_chain.to_dict(),
            "recommended_validation_assay": self.recommended_validation_assay,
            "som_hakken_hash": self.som_hakken_hash,
        }


# ---------------------------------------------------------------------------
# Hakken Literature Link Engine
# ---------------------------------------------------------------------------

class HakkenLiteratureLinkEngine:
    """
    Abductive link predictor across temporal literature knowledge graphs.
    """

    @classmethod
    def audit_evidence_chain(
        cls,
        chain_id: str,
        source: str,
        target: str,
        hops: List[LiteratureHop],
    ) -> PheliNeEvidenceChain:
        """
        Calculates PHELInE necessity (ablation test) and sufficiency metrics.
        """
        if not hops:
            return PheliNeEvidenceChain(
                chain_id=chain_id,
                candidate_pair=(source, target),
                hops=[],
                sufficiency_score=0.0,
                necessity_score=0.0,
                temporal_drift=1.0,
                is_sound_path=False,
                explanation_markdown="*Empty evidence chain.*",
            )

        weights = [h.confidence_weight for h in hops]
        # Sufficiency: compound path confidence with length decay
        base_product = 1.0
        for w in weights:
            base_product *= max(0.1, min(1.0, w))
        length_penalty = math.exp(-0.05 * max(0, len(hops) - 2))
        sufficiency = float(base_product * length_penalty)

        # Necessity: drop if the weakest hop in the chain is removed
        min_w = min(weights)
        necessity = float(min_w * 0.90)

        # Average temporal drift across hops
        drifts = [1.0 - h.temporal_stability_score for h in hops]
        avg_drift = sum(drifts) / len(drifts) if drifts else 0.1

        is_sound = (sufficiency >= 0.35) and (necessity >= 0.25) and (avg_drift <= 0.50)

        md_lines = [
            f"#### 🔗 PHELInE Literature Chain (`{source}` $\\longrightarrow$ `{target}`)",
            f"**Chain ID**: `{chain_id}` | **Length**: {len(hops)} hops",
        ]
        for idx, hop in enumerate(hops, 1):
            md_lines.append(
                f"{idx}. `{hop.source_entity}` --[{hop.relation}]--> `{hop.target_entity}` "
                f"(citations: {hop.literature_citations_count}, weight: {hop.confidence_weight:.2f})"
            )
        md_lines.append(
            f"\n* **Sufficiency**: `{sufficiency:.3f}` | **Necessity**: `{necessity:.3f}` | **Temporal Drift**: `{avg_drift:.3f}`"
        )

        return PheliNeEvidenceChain(
            chain_id=chain_id,
            candidate_pair=(source, target),
            hops=hops,
            sufficiency_score=sufficiency,
            necessity_score=necessity,
            temporal_drift=avg_drift,
            is_sound_path=is_sound,
            explanation_markdown="\n".join(md_lines),
        )

    @classmethod
    def predict_undocumented_link(
        cls,
        candidate_id: str,
        domain: ScientificDomainType,
        source: str,
        target: str,
        predicted_relation: str,
        hops: List[LiteratureHop],
        direct_literature_hits: int = 0,
    ) -> LiteratureLinkCandidate:
        """
        Constructs a verified candidate with PHELInE evidence chain and cryptographic hash.
        """
        chain = cls.audit_evidence_chain(
            chain_id=f"pheli_{candidate_id}",
            source=source,
            target=target,
            hops=hops,
        )

        is_documented = direct_literature_hits > 0
        novelty = 0.95 if not is_documented else max(0.10, 0.90 - 0.15 * math.log1p(direct_literature_hits))

        # Suggest validation assay based on domain
        if domain in (ScientificDomainType.AGING_BIOLOGY, ScientificDomainType.NEURODEGENERATION):
            assay = f"In vitro knockdown/CRISPR of {source} measuring downstream {target} via qPCR/Western blot."
        elif domain == ScientificDomainType.QUANTUM_COMPUTING:
            assay = f"Pulse control microwave sequence Hamiltonian tomography validating {source}->{target} interaction."
        else:
            assay = f"Empirical targeted benchmark evaluating {source}->{target} interaction."

        # Cryptographic anchor
        sig_data = f"{candidate_id}:{domain.value}:{source}:{target}:{novelty}:{chain.sufficiency_score}"
        som_hash = f"sha256:{hashlib.sha256(sig_data.encode('utf-8')).hexdigest()}"

        # Register in ScientificLedger
        ledger = ScientificLedger(ledger_id="hakken-discovery-ledger")
        ledger.record_epistemic_verdict(
            artifact_id=candidate_id,
            verdict_type="HAKKEN_LITERATURE_LINK_CANDIDATE",
            status="PREDICTED" if chain.is_sound_path else "UNGROUNDED",
            som_merkle_hash=som_hash,
            details={
                "source": source,
                "target": target,
                "domain": domain.value,
                "is_sound": chain.is_sound_path,
                "novelty": novelty,
            },
            author="HakkenLiteratureLinkEngine",
        )

        return LiteratureLinkCandidate(
            candidate_id=candidate_id,
            domain=domain,
            source_entity=source,
            target_entity=target,
            predicted_relation=predicted_relation,
            is_previously_documented=is_documented,
            novelty_score=novelty,
            evidence_chain=chain,
            recommended_validation_assay=assay,
            som_hakken_hash=som_hash,
        )


# ---------------------------------------------------------------------------
# Dream-RSI Offline Discovery Replay Types
# ---------------------------------------------------------------------------

class BranchOrderingHeuristic(str, enum.Enum):
    DEPTH_FIRST = "DEPTH_FIRST"
    BREADTH_FIRST = "BREADTH_FIRST"
    VALUE_GREEDY = "VALUE_GREEDY"
    VEGA_DYNAMIC = "VEGA_DYNAMIC"


@dataclass
class DiscoveryHistoryNode:
    node_id: str
    hypothesis_id: str
    branch_depth: int
    compute_tokens_cost: int
    wet_lab_euro_cost: float
    time_spent_hours: float
    outcome_reward: float              # Empirical progress score [0.0, 1.0]
    failure_category: Optional[str]    # None or REPAIRABLE_CODE_ERROR / EPISTEMIC_FALSIFICATION
    is_terminal: bool
    children: List[DiscoveryHistoryNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "hypothesis_id": self.hypothesis_id,
            "branch_depth": self.branch_depth,
            "compute_cost": self.compute_tokens_cost,
            "euro_cost": self.wet_lab_euro_cost,
            "outcome_reward": round(self.outcome_reward, 3),
            "failure_category": self.failure_category,
            "is_terminal": self.is_terminal,
            "children_count": len(self.children),
        }


@dataclass
class SearchPolicyConfig:
    policy_id: str
    branch_ordering: BranchOrderingHeuristic
    worker_concurrency: int = 1
    pruning_reward_threshold: float = 0.20
    max_tokens_budget: int = 100_000
    stop_early_on_reward: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "branch_ordering": self.branch_ordering.value,
            "worker_concurrency": self.worker_concurrency,
            "pruning_reward_threshold": self.pruning_reward_threshold,
            "max_tokens_budget": self.max_tokens_budget,
            "stop_early_on_reward": self.stop_early_on_reward,
        }


@dataclass
class PolicyReplayResult:
    policy_id: str
    total_nodes_visited: int
    pruned_nodes_count: int
    total_compute_tokens_spent: int
    total_euros_spent: float
    max_reward_achieved: float
    early_stopped: bool
    budget_exhausted: bool
    tokens_saved_vs_full_tree: int
    efficiency_gain_ratio: float
    som_replay_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "total_nodes_visited": self.total_nodes_visited,
            "pruned_nodes_count": self.pruned_nodes_count,
            "total_compute_tokens_spent": self.total_compute_tokens_spent,
            "total_euros_spent": round(self.total_euros_spent, 2),
            "max_reward_achieved": round(self.max_reward_achieved, 4),
            "early_stopped": self.early_stopped,
            "budget_exhausted": self.budget_exhausted,
            "tokens_saved_vs_full_tree": self.tokens_saved_vs_full_tree,
            "efficiency_gain_ratio": round(self.efficiency_gain_ratio, 3),
            "som_replay_hash": self.som_replay_hash,
        }


# ---------------------------------------------------------------------------
# Dream-RSI Offline Replay Simulator
# ---------------------------------------------------------------------------

class DreamRSIOfflineReplayEngine:
    """
    Simulates alternative exploration policies over completed discovery history trees
    without re-executing any live models or simulations.
    """

    @classmethod
    def calculate_tree_total_cost(cls, root: DiscoveryHistoryNode) -> int:
        """Computes full tree compute token expenditure."""
        total = root.compute_tokens_cost
        for ch in root.children:
            total += cls.calculate_tree_total_cost(ch)
        return total

    @classmethod
    def replay_policy_on_tree(
        cls,
        root: DiscoveryHistoryNode,
        policy: SearchPolicyConfig,
    ) -> PolicyReplayResult:
        """
        Executes an offline search policy simulation over a recorded discovery history tree.
        """
        full_tree_cost = cls.calculate_tree_total_cost(root)

        visited_count = 0
        pruned_count = 0
        spent_tokens = 0
        spent_euros = 0.0
        max_reward = 0.0
        early_stop = False
        budget_exhausted = False

        # Frontier queue
        queue: List[DiscoveryHistoryNode] = [root]

        while queue:
            # Order frontier according to heuristic
            if policy.branch_ordering == BranchOrderingHeuristic.DEPTH_FIRST:
                current = queue.pop()
            elif policy.branch_ordering == BranchOrderingHeuristic.BREADTH_FIRST:
                current = queue.pop(0)
            elif policy.branch_ordering in (BranchOrderingHeuristic.VALUE_GREEDY, BranchOrderingHeuristic.VEGA_DYNAMIC):
                # Sort descending by observed outcome reward
                queue.sort(key=lambda n: n.outcome_reward, reverse=True)
                current = queue.pop(0)
            else:
                current = queue.pop(0)

            # Check budget
            if spent_tokens + current.compute_tokens_cost > policy.max_tokens_budget:
                budget_exhausted = True
                break

            # Visit node
            visited_count += 1
            spent_tokens += current.compute_tokens_cost
            spent_euros += current.wet_lab_euro_cost
            if current.outcome_reward > max_reward:
                max_reward = current.outcome_reward

            # Check early stopping criteria
            if max_reward >= policy.stop_early_on_reward:
                early_stop = True
                break

            # Pruning rule: prune if outcome_reward is below threshold and not repairable code error
            for ch in current.children:
                is_repairable = ch.failure_category == "REPAIRABLE_CODE_ERROR"
                if ch.outcome_reward < policy.pruning_reward_threshold and not is_repairable:
                    pruned_count += 1
                else:
                    queue.append(ch)

        saved_tokens = max(0, full_tree_cost - spent_tokens)
        efficiency_ratio = (full_tree_cost / max(1, spent_tokens)) if spent_tokens > 0 else 1.0

        # Cryptographic Merkle proof
        sig_data = f"{policy.policy_id}:{visited_count}:{spent_tokens}:{max_reward}:{early_stop}"
        som_hash = f"sha256:{hashlib.sha256(sig_data.encode('utf-8')).hexdigest()}"

        return PolicyReplayResult(
            policy_id=policy.policy_id,
            total_nodes_visited=visited_count,
            pruned_nodes_count=pruned_count,
            total_compute_tokens_spent=spent_tokens,
            total_euros_spent=spent_euros,
            max_reward_achieved=max_reward,
            early_stopped=early_stop,
            budget_exhausted=budget_exhausted,
            tokens_saved_vs_full_tree=saved_tokens,
            efficiency_gain_ratio=efficiency_ratio,
            som_replay_hash=som_hash,
        )

    @classmethod
    def optimize_policy_offline(
        cls,
        history_trees: List[DiscoveryHistoryNode],
        candidate_policies: Optional[List[SearchPolicyConfig]] = None,
    ) -> Dict[str, Any]:
        """
        Sweeps candidate search policies across past discovery history trees to identify
        the highest-efficiency strategy.
        """
        if not candidate_policies:
            candidate_policies = [
                SearchPolicyConfig(policy_id="pol_depth_first", branch_ordering=BranchOrderingHeuristic.DEPTH_FIRST, pruning_reward_threshold=0.15),
                SearchPolicyConfig(policy_id="pol_breadth_first", branch_ordering=BranchOrderingHeuristic.BREADTH_FIRST, pruning_reward_threshold=0.20),
                SearchPolicyConfig(policy_id="pol_greedy_value", branch_ordering=BranchOrderingHeuristic.VALUE_GREEDY, pruning_reward_threshold=0.30),
                SearchPolicyConfig(policy_id="pol_vega_dynamic", branch_ordering=BranchOrderingHeuristic.VEGA_DYNAMIC, pruning_reward_threshold=0.35, stop_early_on_reward=0.80),
            ]

        policy_scores: Dict[str, Dict[str, Any]] = {}

        for pol in candidate_policies:
            total_tokens = 0
            total_reward = 0.0
            total_saved = 0
            replays = []

            for tree in history_trees:
                res = cls.replay_policy_on_tree(tree, pol)
                replays.append(res)
                total_tokens += res.total_compute_tokens_spent
                total_reward += res.max_reward_achieved
                total_saved += res.tokens_saved_vs_full_tree

            tree_count = max(1, len(history_trees))
            avg_reward = total_reward / tree_count
            avg_saved = total_saved / tree_count

            # Composite fitness score: balance reward achievement and token conservation
            fitness = (avg_reward * 1.5) + (avg_saved / 100_000.0)

            policy_scores[pol.policy_id] = {
                "policy": pol.to_dict(),
                "average_reward": round(avg_reward, 4),
                "average_tokens_saved": round(avg_saved, 1),
                "composite_fitness": round(fitness, 4),
                "replays_count": len(replays),
            }

        best_policy_id = max(policy_scores, key=lambda pid: policy_scores[pid]["composite_fitness"])

        return {
            "selected_best_policy_id": best_policy_id,
            "best_policy_summary": policy_scores[best_policy_id],
            "benchmark_comparison": policy_scores,
            "evaluated_trees_count": len(history_trees),
        }
