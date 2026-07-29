"""
Scientific Network Schema - Sprint 31
Represents networks connecting artifacts, contributors, organizations, and standards.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict


@dataclass
class NetworkNode:
    id: str
    type: str  # contributor | organization | standard | dataset | artifact
    name: str = ""
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NetworkEdge:
    source: str
    target: str
    relation: str  # authored | affiliated_with | governs | references | cites

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScientificNetwork:
    network_id: str
    nodes: List[NetworkNode] = field(default_factory=list)
    edges: List[NetworkEdge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "network_id": self.network_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }