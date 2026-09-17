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


class EpistemicGitRepo:
    """
    Manages the immutable scientific commit graph across research campaigns.
    """

    def __init__(self, repo_name: str = "coresearcher-epistemic-repo"):
        self.repo_name = repo_name
        self.commits: Dict[str, ScientificCommit] = {}
        self.head_by_entity: Dict[str, str] = {}  # entity_id -> latest commit_sha

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
        parent_commit_sha: Optional[str] = None
    ) -> ScientificCommit:
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
        return sc

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
