"""
python/discovery/scientific_git_history.py - Scientific Git History & Epistemic Version Control
Tracks theories, constraints, and biological programs as version-controlled commits with parent SHAs,
epistemic diffs, mutation triggers (what failed prediction forced the change), and SOM cryptographic provenance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
import json
import uuid


@dataclass
class EpistemicDiff:
    parameter_changes: Dict[str, Any]
    scope_changes: Dict[str, Any]
    auxiliary_assumptions_added: List[str]
    auxiliary_assumptions_removed: List[str]
    falsification_conditions_modified: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_changes": self.parameter_changes,
            "scope_changes": self.scope_changes,
            "auxiliary_assumptions_added": self.auxiliary_assumptions_added,
            "auxiliary_assumptions_removed": self.auxiliary_assumptions_removed,
            "falsification_conditions_modified": self.falsification_conditions_modified
        }


@dataclass
class ScientificCommit:
    commit_sha: str
    parent_commit_sha: Optional[str]
    timestamp: str
    author_role: str
    entity_type: str  # "HYPOTHESIS" | "CONSTRAINT" | "BIOLOGICAL_PROGRAM" | "REPRESENTATION"
    entity_id: str
    version_tag: str
    commit_message: str
    mutation_trigger: str  # What failed prediction, counterexample or evidence forced the commit
    epistemic_diff: EpistemicDiff
    som_lineage_hash: str
    payload_snapshot: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit_sha": self.commit_sha,
            "parent_commit_sha": self.parent_commit_sha,
            "timestamp": self.timestamp,
            "author_role": self.author_role,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "version_tag": self.version_tag,
            "commit_message": self.commit_message,
            "mutation_trigger": self.mutation_trigger,
            "epistemic_diff": self.epistemic_diff.to_dict(),
            "som_lineage_hash": self.som_lineage_hash,
            "payload_snapshot": self.payload_snapshot
        }


from enum import Enum


class BranchStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VERIFIED_INVARIANT = "VERIFIED_INVARIANT"
    PRUNED_DEAD_END = "PRUNED_DEAD_END"
    MERGED = "MERGED"


@dataclass
class OpenBranchEntry:
    """
    Agora Shared Memory: An active frontier branch in the epistemic hypothesis tree.
    Prevents autonomous agents from repeating ongoing or existing research directions.
    """
    branch_id: str
    head_commit_sha: str
    entity_id: str
    entity_type: str
    research_topic: str
    status: BranchStatus
    created_by_role: str
    created_at: str
    last_active_at: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "head_commit_sha": self.head_commit_sha,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "research_topic": self.research_topic,
            "status": self.status.value,
            "created_by_role": self.created_by_role,
            "created_at": self.created_at,
            "last_active_at": self.last_active_at,
            "tags": self.tags,
        }


@dataclass
class VerifiedClaimEntry:
    """
    Agora Shared Memory: An independently verified empirical claim or invariant constraint.
    Allows downstream agents to build upon solid verified foundations without re-verifying from scratch.
    """
    claim_id: str
    commit_sha: str
    entity_id: str
    statement: str
    rcs_score: int  # Reality Contact Score >= 2
    promoted_constraint_id: Optional[str]
    verification_evidence: Dict[str, Any]
    parent_commit_shas: List[str]
    verified_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "commit_sha": self.commit_sha,
            "entity_id": self.entity_id,
            "statement": self.statement,
            "rcs_score": self.rcs_score,
            "promoted_constraint_id": self.promoted_constraint_id,
            "verification_evidence": self.verification_evidence,
            "parent_commit_shas": self.parent_commit_shas,
            "verified_at": self.verified_at,
        }


class AgoraSharedIndex:
    """
    NVIDIA Agora-inspired distributed shared memory index for autonomous scientific agents.
    Maintains:
    1. Open branches (active exploration frontiers across all agents).
    2. Verified claims & invariants (reusable validated knowledge).
    3. Pruned boundaries / dead-ends (empirically falsified pathways).
    """

    def __init__(self):
        self.branches: Dict[str, OpenBranchEntry] = {}
        self.verified_claims: Dict[str, VerifiedClaimEntry] = {}
        self.pruned_dead_ends: List[Dict[str, Any]] = []

    def register_branch(self, entry: OpenBranchEntry) -> None:
        self.branches[entry.branch_id] = entry

    def update_branch_head(self, branch_id: str, new_commit_sha: str, status: Optional[BranchStatus] = None) -> None:
        if branch_id in self.branches:
            self.branches[branch_id].head_commit_sha = new_commit_sha
            self.branches[branch_id].last_active_at = datetime.now(timezone.utc).isoformat()
            if status:
                self.branches[branch_id].status = status

    def register_verified_claim(self, claim: VerifiedClaimEntry) -> None:
        self.verified_claims[claim.claim_id] = claim

    def register_dead_end(self, entity_id: str, commit_sha: str, falsification_reason: str) -> None:
        self.pruned_dead_ends.append({
            "entity_id": entity_id,
            "commit_sha": commit_sha,
            "falsification_reason": falsification_reason,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        })

    def get_open_branches(self) -> List[OpenBranchEntry]:
        return [b for b in self.branches.values() if b.status == BranchStatus.ACTIVE]

    def get_verified_claims(self) -> List[VerifiedClaimEntry]:
        return list(self.verified_claims.values())

    def get_dead_ends(self) -> List[Dict[str, Any]]:
        return list(self.pruned_dead_ends)


class EpistemicGitRepo:
    """
    Manages the immutable scientific commit graph across research campaigns,
    now augmented with the Agora Shared Memory Index for decentralized agent coordination.
    """

    def __init__(self, repo_name: str = "coresearcher-epistemic-repo"):
        self.repo_name = repo_name
        self.commits: Dict[str, ScientificCommit] = {}
        self.head_by_entity: Dict[str, str] = {}  # entity_id -> latest commit_sha
        self.branches: Dict[str, str] = {}  # branch_id -> head_commit_sha
        self.agora_index = AgoraSharedIndex()

    def create_branch(
        self,
        branch_id: str,
        start_commit_sha: str,
        entity_id: str,
        entity_type: str,
        research_topic: str,
        author_role: str = "Autonomous Worker",
        tags: Optional[List[str]] = None
    ) -> OpenBranchEntry:
        """
        Creates an explicit named branch rooted at a specific verified commit.
        """
        if start_commit_sha not in self.commits:
            raise ValueError(f"Commit {start_commit_sha} does not exist in repo.")

        now_iso = datetime.now(timezone.utc).isoformat()
        self.branches[branch_id] = start_commit_sha
        entry = OpenBranchEntry(
            branch_id=branch_id,
            head_commit_sha=start_commit_sha,
            entity_id=entity_id,
            entity_type=entity_type,
            research_topic=research_topic,
            status=BranchStatus.ACTIVE,
            created_by_role=author_role,
            created_at=now_iso,
            last_active_at=now_iso,
            tags=tags or []
        )
        self.agora_index.register_branch(entry)
        return entry

    def commit(
        self,
        author_role: str,
        entity_type: str,
        entity_id: str,
        version_tag: str,
        commit_message: str,
        mutation_trigger: str,
        epistemic_diff: EpistemicDiff,
        payload_snapshot: Dict[str, Any],
        parent_commit_sha: Optional[str] = None,
        branch_id: Optional[str] = None,
        rcs_score: Optional[int] = None,
        is_verified_invariant: bool = False
    ) -> ScientificCommit:
        # If committing to a branch, use branch head as parent by default
        if branch_id and branch_id in self.branches:
            parent_sha = parent_commit_sha or self.branches[branch_id]
        else:
            parent_sha = parent_commit_sha or self.head_by_entity.get(entity_id)

        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Deterministic SHA computation
        content_for_hash = f"{entity_id}:{version_tag}:{parent_sha}:{now_iso}:{commit_message}"
        commit_sha = f"sha1:{hashlib.sha1(content_for_hash.encode('utf-8')).hexdigest()[:16]}"
        som_hash = f"sha256:{hashlib.sha256(json.dumps(payload_snapshot, sort_keys=True).encode('utf-8')).hexdigest()[:24]}"

        sc = ScientificCommit(
            commit_sha=commit_sha,
            parent_commit_sha=parent_sha,
            timestamp=now_iso,
            author_role=author_role,
            entity_type=entity_type,
            entity_id=entity_id,
            version_tag=version_tag,
            commit_message=commit_message,
            mutation_trigger=mutation_trigger,
            epistemic_diff=epistemic_diff,
            som_lineage_hash=som_hash,
            payload_snapshot=payload_snapshot
        )

        self.commits[commit_sha] = sc
        self.head_by_entity[entity_id] = commit_sha

        # Update branch state in Agora Index
        if branch_id:
            self.branches[branch_id] = commit_sha
            status = BranchStatus.VERIFIED_INVARIANT if is_verified_invariant else BranchStatus.ACTIVE
            self.agora_index.update_branch_head(branch_id, commit_sha, status=status)

        # Register into Agora Verified Claims if verified or high RCS
        effective_rcs = rcs_score or (2 if entity_type == "CONSTRAINT" or is_verified_invariant else 1)
        if is_verified_invariant or effective_rcs >= 2:
            claim_entry = VerifiedClaimEntry(
                claim_id=f"CLAIM-{entity_id}-{version_tag}",
                commit_sha=commit_sha,
                entity_id=entity_id,
                statement=payload_snapshot.get("statement", commit_message),
                rcs_score=effective_rcs,
                promoted_constraint_id=entity_id if entity_type == "CONSTRAINT" else None,
                verification_evidence={
                    "som_lineage_hash": som_hash,
                    "mutation_trigger": mutation_trigger,
                    "author_role": author_role
                },
                parent_commit_shas=[parent_sha] if parent_sha else [],
                verified_at=now_iso
            )
            self.agora_index.register_verified_claim(claim_entry)

        return sc

    def cherry_pick_claim(
        self,
        target_branch_id: str,
        source_claim_id: str,
        author_role: str = "Autonomous Worker"
    ) -> ScientificCommit:
        """
        Agora Cherry-Pick: Adopts a verified claim from another branch as a new parent/ancestor commit
        in the target branch, allowing modular cross-pollination across independent discovery teams.
        """
        if source_claim_id not in self.agora_index.verified_claims:
            raise ValueError(f"Claim {source_claim_id} is not registered in Agora verified claims.")
        if target_branch_id not in self.branches:
            raise ValueError(f"Target branch {target_branch_id} does not exist.")

        claim = self.agora_index.verified_claims[source_claim_id]
        source_commit = self.commits[claim.commit_sha]
        target_head = self.branches[target_branch_id]

        cherry_diff = EpistemicDiff(
            parameter_changes={"imported_from_claim": source_claim_id},
            scope_changes={"scope_synthesized": True},
            auxiliary_assumptions_added=[f"AUX-IMPORTED-{claim.entity_id}"],
            auxiliary_assumptions_removed=[],
            falsification_conditions_modified=[]
        )

        merged_payload = {
            "statement": f"Synthesized invariant from {source_claim_id}: {claim.statement}",
            "source_claim_id": source_claim_id,
            "source_commit_sha": source_commit.commit_sha,
            "base_head_sha": target_head
        }

        return self.commit(
            author_role=author_role,
            entity_type="CONSTRAINT",
            entity_id=f"SYNTH-{claim.entity_id}",
            version_tag="cherry-pick",
            commit_message=f"Agora Cherry-pick: Integrated verified claim {source_claim_id} into {target_branch_id}",
            mutation_trigger=f"Cross-branch synthesis with verified invariant {source_claim_id}",
            epistemic_diff=cherry_diff,
            payload_snapshot=merged_payload,
            parent_commit_sha=target_head,
            branch_id=target_branch_id,
            rcs_score=claim.rcs_score,
            is_verified_invariant=True
        )

    def get_entity_history(self, entity_id: str) -> List[ScientificCommit]:
        """Returns the full commit lineage starting from head backwards."""
        history = []
        curr_sha = self.head_by_entity.get(entity_id)
        while curr_sha and curr_sha in self.commits:
            c = self.commits[curr_sha]
            history.append(c)
            curr_sha = c.parent_commit_sha
        return history

    @classmethod
    def create_canonical_tau_lineage(cls) -> "EpistemicGitRepo":
        """Pre-populates the canonical evolution history of the Tau-Connectome hypothesis."""
        repo = cls()

        # Commit 1: v1.0.0 Naive Linear Model
        diff1 = EpistemicDiff(
            parameter_changes={"linear_slope_beta": -2.1},
            scope_changes={"domain": "All age groups"},
            auxiliary_assumptions_added=["AUX-LINEARITY-GLOBAL"],
            auxiliary_assumptions_removed=[],
            falsification_conditions_modified=["Non-linear decay observed"]
        )
        c1 = repo.commit(
            author_role="Hypothesis Generator",
            entity_type="HYPOTHESIS",
            entity_id="HYP-TAU-CONNECTOME",
            version_tag="v1.0.0",
            commit_message="Initial formulation: Global scalar linearity between pTau217 and dementia progression",
            mutation_trigger="Initial research question RQ-2026-004 formulation",
            epistemic_diff=diff1,
            payload_snapshot={"statement": "Plasma pTau217 elevation linearly causes dementia progression in all subjects uniformly."}
        )

        # Commit 2: v1.1.0 Modus Tollens refutation of uniformity -> Introduction of connectome hubs
        diff2 = EpistemicDiff(
            parameter_changes={"connectome_weighting_applied": True},
            scope_changes={"domain": "Restricted to Braak III-IV preclinical cohort"},
            auxiliary_assumptions_added=["AUX-CONNECTOME-GRAPH-DIFFUSION"],
            auxiliary_assumptions_removed=["AUX-LINEARITY-GLOBAL"],
            falsification_conditions_modified=["Hub-sparing cognitive decline without tau elevation"]
        )
        c2 = repo.commit(
            author_role="Popper Auditor",
            entity_type="HYPOTHESIS",
            entity_id="HYP-TAU-CONNECTOME",
            version_tag="v1.1.0",
            commit_message="Refactor: Replace global scalar linearity with connectome hub nodal diffusion following Modus Tollens refutation",
            mutation_trigger="Failed prediction PRED-0-LINEAR-DECLINE on high-reserve resilient subgroup (n=38)",
            epistemic_diff=diff2,
            payload_snapshot={"statement": "Tau spreading rates and cognitive decline are governed by connectome hub vulnerability and synaptic flux."},
            parent_commit_sha=c1.commit_sha
        )

        # Commit 3: v2.0.0 Cross-cohort invariant promotion (ADNI, NACC, AIBL, OASIS)
        diff3 = EpistemicDiff(
            parameter_changes={"hub_threshold_cutoff": 0.65},
            scope_changes={"invariance_domain": "Universal across ATN-positive preclinical MCI"},
            auxiliary_assumptions_added=["AUX-LONGITUDINAL-MIXED-EFFECTS"],
            auxiliary_assumptions_removed=[],
            falsification_conditions_modified=["High-hub subject (>0.65) progressing to dementia within 36m"]
        )
        c3 = repo.commit(
            author_role="Constraint Discovery Engine",
            entity_type="CONSTRAINT",
            entity_id="CONST-INVARIANT-HUB-RESERVE",
            version_tag="v2.0.0",
            commit_message="Promote invariant boundary condition: High connectome hub reserve strictly prohibits 36m dementia transition",
            mutation_trigger="Cross-cohort stress test survival across 4 cohorts (628 subjects, 0 counterexamples)",
            epistemic_diff=diff3,
            payload_snapshot={"statement": "∀ω ∈ Ω, (Connectome_Hub_Strength(ω) > 0.65) ⟹ (Clinical_36m_Outcome(ω) ≠ Accelerated_Dementia)"},
            parent_commit_sha=c2.commit_sha
        )

        return repo
