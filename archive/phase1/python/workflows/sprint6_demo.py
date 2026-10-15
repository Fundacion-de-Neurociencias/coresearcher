"""
Sprint 6 Demo - Ecosystem Architecture Layer
Demonstrates all Sprint 6 components working together.
"""

import sys
from datetime import datetime

# Add ecosystem to path
sys.path.insert(0, "python")

from ecosystem import (

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    DomainPackRegistry,
    CapabilityRegistry,
    DependencyEngine,
    ProvenanceDashboard,
    ProvenanceStep,
    ProvenanceTree,
    ResearchProject,
    ProjectManager,
    NEURODIAGNOSES_PACK,
    GENOMICS_PACK,
    CLINICAL_EVIDENCE_PACK,
    GENE_FORGE_PACK,
    MEDICALIA_PACK,
    PACK_DEPENDENCIES,
)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demo_domain_pack_registry():
    """Demonstrate Domain Pack Registry."""
    print_header("1. Domain Pack Registry")
    
    registry = DomainPackRegistry()
    
    # Register all packs
    print("\nRegistering domain packs...")
    registry.register(NEURODIAGNOSES_PACK)
    registry.register(GENOMICS_PACK)
    registry.register(CLINICAL_EVIDENCE_PACK)
    registry.register(GENE_FORGE_PACK)
    registry.register(MEDICALIA_PACK)
    
    print(f"Total packs registered: {len(registry.list())}")
    
    # Show packs
    for pack in registry.list():
        deps = pack.get("depends_on", [])
        print(f"\n  {pack['id']}:")
        print(f"    Version: {pack['version']}")
        print(f"    Entities: {len(pack.get('entities', []))}")
        print(f"    Workflows: {len(pack.get('workflows', []))}")
        if deps:
            print(f"    Depends on: {deps}")


def demo_capability_registry():
    """Demonstrate Capability Registry."""
    print_header("2. Capability Registry")
    
    registry = CapabilityRegistry()
    
    # Register capabilities
    registrations = [
        ("Discovery", "neurodiagnoses", ["research_scout", "hypothesis_discovery"], ["co-scientist"]),
        ("Discovery", "geneforge", ["drug_discovery"], ["autoscientist"], 40),
        ("LiteratureReview", "neurodiagnoses", ["literature_review"], ["reviewer"]),
        ("GrantWriting", "neurodiagnoses", ["grant_writer"], ["co-scientist"]),
        ("ClinicalEvidence", "clinical_evidence", ["clinical_evidence"], ["reviewer"]),
        ("DrugDiscovery", "geneforge", ["drug_discovery"], ["autoscientist"]),
        ("BiomarkerDiscovery", "neurodiagnoses", ["biomarker_discovery"], ["co-scientist"]),
        ("GenomicsAnalysis", "genomics", ["genomics_analysis"], ["co-scientist"]),
    ]
    
    print("\nRegistering capabilities...")
    for cap, pack, workflows, agents, *rest in registrations:
        priority = rest[0] if rest else 50
        registry.register(cap, pack, workflows, agents, priority)
    
    print(f"\nTotal capabilities: {len(registry.list())}")
    
    # Show capability lookups
    for cap in ["Discovery", "DrugDiscovery", "GenomicsAnalysis", "GrantWriting"]:
        best = registry.get_best_pack(cap)
        workflows = registry.get_workflows(cap)
        print(f"\n  {cap}:")
        print(f"    Best pack: {best}")
        print(f"    Workflows: {workflows}")


def demo_dependency_engine():
    """Demonstrate Cross-Pack Dependency Engine."""
    print_header("3. Cross-Pack Dependency Engine")
    
    engine = DependencyEngine()
    
    # Register dependencies from configuration
    print("\nRegistering dependencies...")
    for pack_id, config in PACK_DEPENDENCIES.items():
        engine.add_dependency(pack_id, config["depends_on"])
    
    # Validate
    valid = engine.validate()
    print(f"\nDependency graph valid: {valid}")
    
    # Dependency graph
    graph = engine.resolve()
    print(f"\nGraph nodes: {len(graph['nodes'])}")
    print(f"Graph edges: {len(graph['edges'])}")
    
    # Show load order
    print("\nLoad order for 'neurodiagnoses':")
    order = engine.get_load_order(["neurodiagnoses"])
    for i, p in enumerate(order):
        print(f"  {i+1}. {p}")


def demo_provenance_dashboard():
    """Demonstrate Provenance Dashboard."""
    print_header("4. Provenance Dashboard")
    
    dashboard = ProvenanceDashboard()
    
    # Create flow
    flow_id = dashboard.create_flow(project_id="plasma_ptau217")
    print(f"\nCreated provenance flow: {flow_id}")
    
    # Add steps
    print("\nAdding provenance steps...")
    
    steps = [
        (ProvenanceStep.PAPER, "paper_doi:10.1234/ptau217", None, 1.0, 1.0, 
         {"doi": "10.1234/ptau217", "title": "Plasma pTau217 for AD diagnosis"}),
        (ProvenanceStep.CLAIM, "claim_001", "qwen", 0.92, 0.95,
         {"text": "pTau217 predicts Alzheimer onset with 85% accuracy"}),
        (ProvenanceStep.EVIDENCE, "evidence_001", "qwen", 0.88, 1.0,
         {"p_value": 0.001, "sample_size": 1200, "effect_size": 0.75}),
        (ProvenanceStep.HYPOTHESIS, "hyp_001", "gpt", 0.85, None,
         {"statement": "Plasma pTau217 predicts Alzheimer onset"}),
        (ProvenanceStep.CRITIC_REVIEW, "critique_001", "claude", None, None,
         {"objections": ["confounding_by_age"], "survives": True}),
        (ProvenanceStep.TOURNAMENT_RANK, "rank_001", "gpt", None, None,
         {"elo_score": 1450, "rank": 1}),
        (ProvenanceStep.GRANT_SECTION, "grant_section_001", "gpt", None, None,
         {"section": "Specific Aims", "hypothesis": "hyp_001"}),
    ]
    
    for step, artifact, model, confidence, evidence_score, metadata in steps:
        dashboard.add_step(flow_id, step, artifact, model, confidence, evidence_score, metadata)
    
    # Visualization
    print("\nProvenance Chain Visualization:")
    flow = dashboard.get_flow(flow_id)
    print(ProvenanceTree.format_tree(flow["steps"]))
    
    # Mermaid diagram
    print("\nMermaid Diagram:")
    print(ProvenanceTree.to_mermaid(flow))
    
    # Check completion
    complete = dashboard.complete_chain(flow_id)
    print(f"\nComplete chain (Paper → Grant): {complete}")


def demo_project_container():
    """Demonstrate Research Project Container."""
    print_header("5. Research Project Container")
    
    manager = ProjectManager()
    
    # Create project
    project = manager.create_from_template(
        "biomarker_discovery",
        "Plasma pTau217"
    )
    
    proj = project.get(project._project_id)
    print(f"\nProject: {proj['name']}")
    print(f"  Packs: {proj['packs']}")
    print(f"  Workflows: {[w['id'] for w in proj['workflows']]}")
    
    # Model configuration
    print("\nModel Configuration:")
    for model in proj['models']:
        print(f"  {model['purpose']}: {model['model']}")
    
    # Simulate workflow run
    run_id = project.add_workflow_run(
        project._project_id,
        "research_scout",
        {"hypotheses": 12, "top_ranked": 3, "runtime": "45s"}
    )
    print(f"\nWorkflow run recorded: {run_id}")
    
    # Complete project
    project.complete(project._project_id)
    print(f"Project status: {project.get(project._project_id)['status']}")


def demo_full_ecosystem():
    """Demonstrate full ecosystem integration."""
    print_header("Full Ecosystem Integration")
    
    print("\nCreating integrated ecosystem...")
    
    # 1. Register domain packs
    pack_registry = DomainPackRegistry()
    for pack in [NEURODIAGNOSES_PACK, GENOMICS_PACK, CLINICAL_EVIDENCE_PACK, GENE_FORGE_PACK, MEDICALIA_PACK]:
        pack_registry.register(pack)
    
    # 2. Register capabilities
    capability_registry = CapabilityRegistry()
    capability_registry.register("Discovery", "neurodiagnoses", 
                               ["research_scout", "hypothesis_discovery"],
                               ["co-scientist"], priority=80)
    capability_registry.register("GenomicsAnalysis", "genomics",
                               ["genomics_analysis"], ["co-scientist"])
    capability_registry.register("GrantWriting", "neurodiagnoses",
                               ["grant_writer"], ["co-scientist"])
    
    # 3. Setup dependencies
    engine = DependencyEngine()
    for pack_id, config in PACK_DEPENDENCIES.items():
        engine.add_dependency(pack_id, config["depends_on"])
    
    # 4. Create project
    project = ResearchProject.create(
        name="Plasma pTau217",
        packs=["neurodiagnoses", "genomics"],
        workflows=[
            {"id": "research_scout", "packId": "neurodiagnoses"},
            {"id": "genomics_analysis", "packId": "genomics"},
            {"id": "grant_writer", "packId": "neurodiagnoses"},
        ],
        models=[
            {"id": "critique_model", "purpose": "critique", "model": "claude"},
            {"id": "ranking_model", "purpose": "ranking", "model": "gpt"},
            {"id": "extraction_model", "purpose": "extraction", "model": "qwen"},
        ]
    )
    
    # 5. Create provenance flow
    dashboard = ProvenanceDashboard()
    flow_id = dashboard.create_flow(project_id=project._project_id)
    
    print(f"\nEcosystem Summary:")
    print(f"  Packs: {len(pack_registry.list())}")
    print(f"  Capabilities: {len(capability_registry.list())}")
    print(f"  Dependencies resolved: {len(engine.resolve()['edges'])}")
    print(f"  Project: {project.get(project._project_id)['name']}")
    print(f"  Provenance flow: {flow_id}")
    
    # Show capability routing
    print(f"\nCapability Routing for 'Discovery':")
    print(f"  Best pack: {capability_registry.get_best_pack('Discovery')}")
    
    # Show dependency check
    print(f"\nDependency check for project packs:")
    for pack in project.get(project._project_id)['packs']:
        deps = engine.get_transitive_dependencies(pack)
        print(f"  {pack}: dependencies = {deps}")


if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 6 Demo - Ecosystem Architecture Layer")
    print("=" * 70)
    
    demo_domain_pack_registry()
    demo_capability_registry()
    demo_dependency_engine()
    demo_provenance_dashboard()
    demo_project_container()
    demo_full_ecosystem()
    
    print("\n" + "=" * 70)
    print("Sprint 6 Demo Complete!")
    print("=" * 70)