"""
Ecosystem Architecture Layer - CoResearcher OS Sprint 6

This module provides the ecosystem infrastructure:
- Domain Pack Registry
- Capability Registry  
- Cross-Pack Dependency Engine
- Provenance Dashboard
- Research Project Container
"""

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

from .domain_pack_registry import (
    DomainPackRegistry,
    NEURODIAGNOSES_PACK,
    GENOMICS_PACK,
    CLINICAL_EVIDENCE_PACK,
    GENE_FORGE_PACK,
    MEDICALIA_PACK,
)

from .capability_registry import (
    CapabilityRegistry,
    Capability,
)

from .dependency_engine import (
    DependencyEngine,
    PACK_DEPENDENCIES,
)

from .provenance_dashboard import (
    ProvenanceDashboard,
    ProvenanceStep,
    ProvenanceTree,
)

from .project_container import (
    ResearchProject,
    ProjectManager,
    PLASMA_PTAU217_PROJECT,
)

__all__ = [
    # Domain Pack Registry
    "DomainPackRegistry",
    "NEURODIAGNOSES_PACK",
    "GENOMICS_PACK",
    "CLINICAL_EVIDENCE_PACK",
    "GENE_FORGE_PACK",
    "MEDICALIA_PACK",
    
    # Capability Registry
    "CapabilityRegistry",
    "Capability",
    
    # Dependency Engine
    "DependencyEngine",
    "PACK_DEPENDENCIES",
    
    # Provenance Dashboard
    "ProvenanceDashboard",
    "ProvenanceStep",
    "ProvenanceTree",
    
    # Project Container
    "ResearchProject",
    "ProjectManager",
    "PLASMA_PTAU217_PROJECT",
]