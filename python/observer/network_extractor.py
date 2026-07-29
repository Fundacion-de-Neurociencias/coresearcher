"""
Network Extractor - Sprint 31
Extracts scientific network signals from ScientificArtifact objects.
"""

from __future__ import annotations

from typing import List, Dict, Set
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact
from observer.scientific_network import ScientificNetwork, NetworkNode, NetworkEdge


def _standard_tokens(text: str) -> Set[str]:
    tokens = set()
    keywords = [
        "bids", "brain imaging data structure", "neuroimaging", "meg", "eeg",
        "source localization", "ica", "time-frequency", "connectivity",
        "openneuro", "fmri", "mri", "dataset", "layout", "derivatives",
    ]
    lower = text.lower()
    for kw in keywords:
        if kw in lower:
            tokens.add(kw)
    return tokens


def extract_network(artifacts: List[ScientificArtifact], network_id: str) -> ScientificNetwork:
    network = ScientificNetwork(network_id=network_id)
    artifact_nodes = {}
    contributor_nodes = {}
    standard_nodes = {}

    for a in artifacts:
        aid = a.artifact_id
        artifact_nodes[aid] = NetworkNode(
            id=aid,
            type="artifact",
            name=a.title,
            metadata={"artifact_type": a.type, "doi": a.doi, "github_repo": a.github_repo},
        )
        network.nodes.append(artifact_nodes[aid])
        for c in a.contributors:
            cid = f"contributor:{c.name.strip().lower()}"
            if cid not in contributor_nodes:
                contributor_nodes[cid] = NetworkNode(
                    id=cid,
                    type="contributor",
                    name=c.name,
                    metadata={"orcid": c.orcid, "github": c.github, "affiliation": c.affiliation},
                )
                network.nodes.append(contributor_nodes[cid])
            network.edges.append(NetworkEdge(source=cid, target=aid, relation="authored"))
        for token in _standard_tokens(a.title + " " + (a.notes or "")):
            sid = f"standard:{token}"
            if sid not in standard_nodes:
                standard_nodes[sid] = NetworkNode(id=sid, type="standard", name=token)
                network.nodes.append(standard_nodes[sid])
            network.edges.append(NetworkEdge(source=aid, target=sid, relation="references"))

    return network


def artifact_neighborhoods(artifacts: List[ScientificArtifact]) -> Dict[str, Set[str]]:
    neighborhoods = {}
    for a in artifacts:
        neighbors: Set[str] = set()
        for c in a.contributors:
            neighbors.add(f"contributor:{c.name.strip().lower()}")
        for token in _standard_tokens(a.title + " " + (a.notes or "")):
            neighbors.add(f"standard:{token}")
        neighborhoods[a.artifact_id] = neighbors
    return neighborhoods