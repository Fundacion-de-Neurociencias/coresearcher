"""
Cross-Pack Dependency Engine - CoResearcher OS Sprint 6
Resolves dependencies between domain packs in the ecosystem.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from collections import defaultdict

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


# Registry storage
REGISTRY_DIR = Path("ecosystem/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
DEPENDENCIES_FILE = REGISTRY_DIR / "dependencies.json"


class DependencyEngine:
    """
    Resolves cross-pack dependencies for the ecosystem.
    
    Builds a dependency graph and ensures:
    - No circular dependencies
    - All transitive dependencies are resolved
    - Packs can be loaded in correct order
    """
    
    def __init__(self, pack_registry: 'DomainPackRegistry' = None):
        self._dependencies: dict = self._load()
        self._pack_registry = pack_registry
        self._graph_cache: Optional[dict] = None
    
    def _load(self) -> dict:
        """Load dependencies from disk."""
        if DEPENDENCIES_FILE.exists():
            with open(DEPENDENCIES_FILE, 'r') as f:
                return json.load(f)
        return {"edges": {}, "next_id": 1}
    
    def _save(self):
        """Save dependencies to disk."""
        with open(DEPENDENCIES_FILE, 'w') as f:
            json.dump(self._dependencies, f, indent=2)
    
    def add_dependency(self, pack_id: str, depends_on: list[str], 
                       dependency_type: str = "requires"):
        """
        Add a dependency for a pack.
        
        Args:
            pack_id: The pack that has the dependency
            depends_on: List of pack IDs it depends on
            dependency_type: Type of dependency (requires, extends, recommends)
        """
        if pack_id not in self._dependencies["edges"]:
            self._dependencies["edges"][pack_id] = []
        
        for dep_id in depends_on:
            edge = {
                "dep_id": dep_id,
                "type": dependency_type,
                "added_at": datetime.now().isoformat(),
            }
            self._dependencies["edges"][pack_id].append(edge)
        
        self._dependencies["next_id"] += 1
        self._save()
        self._graph_cache = None  # Invalidate cache
    
    def resolve(self) -> dict:
        """
        Build and return the dependency graph.
        
        Returns:
            Dependency graph with nodes, edges, and resolution status
        """
        if self._graph_cache:
            return self._graph_cache
        
        # Build graph from dependencies
        nodes = set()
        edges = []
        
        for pack_id, deps in self._dependencies["edges"].items():
            nodes.add(pack_id)
            for dep in deps:
                nodes.add(dep["dep_id"])
                edges.append({
                    "from": pack_id,
                    "to": dep["dep_id"],
                    "type": dep["type"],
                })
        
        self._graph_cache = {
            "nodes": list(nodes),
            "edges": edges,
            "resolved": True,
        }
        
        return self._graph_cache
    
    def get_transitive_dependencies(self, pack_id: str) -> list[str]:
        """
        Get all transitive dependencies for a pack.
        
        Returns packs in load order (dependencies first).
        """
        # Get direct dependencies
        direct_deps = self._dependencies["edges"].get(pack_id, [])
        direct_dep_ids = [d["dep_id"] for d in direct_deps]
        
        # BFS to find all transitive dependencies
        all_deps = []
        visited = set()
        to_visit = list(direct_dep_ids)
        
        while to_visit:
            dep_id = to_visit.pop(0)
            if dep_id in visited:
                continue
            visited.add(dep_id)
            all_deps.append(dep_id)
            
            # Add nested dependencies
            nested = self._dependencies["edges"].get(dep_id, [])
            for n in nested:
                if n["dep_id"] not in visited:
                    to_visit.append(n["dep_id"])
        
        return all_deps
    
    def validate(self) -> bool:
        """
        Validate the dependency graph for issues.
        
        Checks for:
        - Circular dependencies
        - Missing dependencies (referenced packs don't exist)
        
        Returns:
            True if valid, False otherwise
        """
        # Check for missing packs if registry provided
        if self._pack_registry:
            for pack_id in self._dependencies["edges"].keys():
                if not self._pack_registry.get(pack_id):
                    print(f"Warning: Pack {pack_id} not found in registry")
                    return False
                
                for dep in self._dependencies["edges"][pack_id]:
                    if not self._pack_registry.get(dep["dep_id"]):
                        print(f"Warning: Dependency {dep['dep_id']} for {pack_id} not found")
                        return False
        
        # Check for circular dependencies
        for pack_id in self._dependencies["edges"].keys():
            if self._has_circular_dependency(pack_id, set()):
                print(f"Error: Circular dependency detected involving {pack_id}")
                return False
        
        return True
    
    def _has_circular_dependency(self, pack_id: str, visiting: set) -> bool:
        """Check if pack_id has a circular dependency."""
        if pack_id in visiting:
            return True
        
        visiting.add(pack_id)
        
        deps = self._dependencies["edges"].get(pack_id, [])
        for dep in deps:
            if self._has_circular_dependency(dep["dep_id"], visiting.copy()):
                return True
        
        return False
    
    def get_load_order(self, pack_ids: list[str]) -> list[str]:
        """
        Get packs in correct load order (topological sort).
        
        Returns:
            Ordered list of pack IDs
        """
        # Build adjacency list
        order = []
        visited = set()
        
        def visit(pack_id: str):
            if pack_id in visited:
                return
            visited.add(pack_id)
            
            # Visit dependencies first
            for dep in self._dependencies["edges"].get(pack_id, []):
                visit(dep["dep_id"])
            
            order.append(pack_id)
        
        for pack_id in pack_ids:
            visit(pack_id)
        
        return order
    
    def get_dependents(self, pack_id: str) -> list[str]:
        """Get packs that depend on the given pack."""
        dependents = []
        for other_id, deps in self._dependencies["edges"].items():
            for dep in deps:
                if dep["dep_id"] == pack_id:
                    dependents.append(other_id)
        return dependents


# =============================================================================
# Cross-Pack Dependency Configuration
# =============================================================================

# Example dependencies from the recommendation:
# Neurodiagnoses depends on Genomics + ClinicalEvidence
# GeneForge depends on Genomics + Protein
# Medicalia depends on ClinicalEvidence

PACK_DEPENDENCIES = {
    "neurodiagnoses": {
        "depends_on": ["genomics", "clinical_evidence"],
        "description": "Neurodiagnoses uses genomics for biomarkers and clinical evidence for validation",
    },
    "geneforge": {
        "depends_on": ["genomics"],
        "description": "GeneForge uses genomics for target discovery",
    },
    "medicalia": {
        "depends_on": ["clinical_evidence"],
        "description": "Medicalia uses clinical evidence for treatment optimization",
    },
    "clinical_evidence": {
        "depends_on": [],
        "description": "Clinical evidence is a foundational pack",
    },
    "genomics": {
        "depends_on": [],
        "description": "Genomics is a foundational pack",
    },
}


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Cross-Pack Dependency Engine - Sprint 6")
    print("=" * 70)
    
    engine = DependencyEngine()
    
    # Register dependencies from configuration
    print("\nRegistering dependencies...")
    for pack_id, config in PACK_DEPENDENCIES.items():
        engine.add_dependency(pack_id, config["depends_on"])
        print(f"  {pack_id} -> {config['depends_on']}")
    
    # Validate
    print("\n" + "=" * 70)
    print("Validation:")
    print("=" * 70)
    valid = engine.validate()
    print(f"Graph valid: {valid}")
    
    # Get load order
    print("\n" + "=" * 70)
    print("Load Order:")
    print("=" * 70)
    
    packs_to_load = ["neurodiagnoses", "geneforge", "medicalia"]
    order = engine.get_load_order(packs_to_load)
    print(f"\nLoading {packs_to_load}:")
    for i, p in enumerate(order):
        deps = engine.get_transitive_dependencies(p)
        print(f"  {i+1}. {p} (deps: {deps})")
    
    # Get dependents
    print("\n" + "=" * 70)
    print("Dependents:")
    print("=" * 70)
    print(f"\nPacks that depend on 'genomics': {engine.get_dependents('genomics')}")
    print(f"Packs that depend on 'clinical_evidence': {engine.get_dependents('clinical_evidence')}")
    
    print("\n" + "=" * 70)
    print("Dependency Engine complete!")
    print("=" * 70)