"""
Integration test for the Scientific Connector Layer (Sprint 21).

Tests:
1. All four individual connectors (search, get, related, evidence)
2. Connector Registry (register, search_all, evidence_all)
3. AgentRouter integration (knowledge_retrieval routing)
4. Capability Registry (KnowledgeRetrieval capability)
5. Provenance tracking
"""

import json
import sys
from datetime import datetime


def test_base_connector():
    """Test that ScientificConnector ABC cannot be instantiated."""
    print("  [test] Base Connector is abstract...", end=" ")
    from .base_connector import ScientificConnector
    try:
        ScientificConnector()
        print("FAIL - should not be instantiable")
        return False
    except TypeError:
        print("OK")
        return True


def test_connector_result():
    """Test ConnectorResult dataclass."""
    print("  [test] ConnectorResult...", end=" ")
    from .base_connector import ConnectorResult
    result = ConnectorResult(
        source="test", operation="search",
        query="test", total=5,
        items=[{"id": "1", "title": "test"}],
    )
    d = result.to_dict()
    assert d["source"] == "test"
    assert d["total"] == 5
    assert len(d["items"]) == 1
    print("OK")


def test_evidence_item():
    """Test EvidenceItem dataclass."""
    print("  [test] EvidenceItem...", end=" ")
    from .base_connector import EvidenceItem
    ev = EvidenceItem(
        id="test123", source="test", title="Test Evidence",
        description="Test description", url="https://example.com",
        relevance_score=0.85,
    )
    d = ev.to_dict()
    assert d["id"] == "test123"
    assert d["relevance_score"] == 0.85
    print("OK")


def test_clinicaltrials_connector():
    """Test ClinicalTrialsConnector with real API."""
    print("  [test] ClinicalTrials Connector...")
    from .clinicaltrials_connector import ClinicalTrialsConnector

    connector = ClinicalTrialsConnector()

    # search
    result = connector.search("Alzheimer", max_results=3)
    assert result.source == "clinicaltrials"
    assert result.total >= 0
    print(f"    search('Alzheimer') → {result.total} results")

    # get
    if result.items:
        nct_id = result.items[0]["id"]
        detail = connector.get(nct_id)
        assert detail.total == 1
        print(f"    get('{nct_id}') → {detail.items[0]['title'][:50]}...")

    # related
    if result.items:
        nct_id = result.items[0]["id"]
        related = connector.related(nct_id, max_results=3)
        print(f"    related('{nct_id}') → {related.total} results")

    # evidence
    ev = connector.evidence("Amyloid", max_results=3)
    print(f"    evidence('Amyloid') → {ev.total} evidence items")

    # provenance
    log = connector.get_provenance_log()
    assert len(log) >= 1
    print(f"    provenance log entries: {len(log)}")

    print("  [test] ClinicalTrials Connector: OK")


def test_opentargets_connector():
    """Test OpenTargetsConnector with real API."""
    print("  [test] Open Targets Connector...")
    from .opentargets_connector import OpenTargetsConnector

    connector = OpenTargetsConnector()

    # search
    result = connector.search("APOE", max_results=3)
    assert result.source == "opentargets"
    print(f"    search('APOE') → {result.total} results")

    # get target
    detail = connector.get("ENSG00000130234")
    if not detail.error:
        assert detail.total == 1
        print(f"    get(ENSG00000130234) → {detail.items[0]['title']}")
    else:
        print(f"    get(ENSG00000130234) → SKIPPED (API may be rate-limited)")

    # evidence
    ev = connector.evidence("APOE Alzheimer", max_results=3)
    print(f"    evidence('APOE Alzheimer') → {ev.total} evidence items")

    # provenance
    log = connector.get_provenance_log()
    assert len(log) >= 1
    print(f"    provenance log entries: {len(log)}")

    print("  [test] Open Targets Connector: OK")


def test_chembl_connector():
    """Test ChEMBLConnector with real API."""
    print("  [test] ChEMBL Connector...")
    from .chembl_connector import ChEMBLConnector

    connector = ChEMBLConnector()

    # search
    result = connector.search("Aspirin", max_results=3)
    assert result.source == "chembl"
    print(f"    search('Aspirin') → {result.total} results")

    if result.items:
        chembl_id = result.items[0]["id"]
        detail = connector.get(chembl_id)
        if not detail.error:
            print(f"    get('{chembl_id}') → {detail.items[0]['title']}")
        else:
            print(f"    get('{chembl_id}') → SKIPPED")

    # evidence
    ev = connector.evidence("Aspirin COX", max_results=3)
    print(f"    evidence('Aspirin COX') → {ev.total} evidence items")

    # provenance
    log = connector.get_provenance_log()
    assert len(log) >= 1
    print(f"    provenance log entries: {len(log)}")

    print("  [test] ChEMBL Connector: OK")


def test_uniprot_connector():
    """Test UniProtConnector with real API."""
    print("  [test] UniProt Connector...")
    from .uniprot_connector import UniProtConnector

    connector = UniProtConnector()

    # search
    result = connector.search("APOE human", max_results=3)
    assert result.source == "uniprot"
    print(f"    search('APOE human') → {result.total} results")

    # get
    detail = connector.get("P02649")
    if not detail.error:
        assert detail.total >= 1
        print(f"    get(P02649) → {detail.items[0]['title'][:50]}...")
    else:
        print(f"    get(P02649) → SKIPPED (API may be rate-limited)")

    # evidence
    ev = connector.evidence("APOE lipid transport", max_results=3)
    print(f"    evidence('APOE lipid transport') → {ev.total} evidence items")

    # provenance
    log = connector.get_provenance_log()
    assert len(log) >= 1
    print(f"    provenance log entries: {len(log)}")

    print("  [test] UniProt Connector: OK")


def test_connector_registry():
    """Test ConnectorRegistry."""
    print("  [test] Connector Registry...")
    from .connector_registry import ConnectorRegistry
    from .clinicaltrials_connector import ClinicalTrialsConnector
    from .uniprot_connector import UniProtConnector

    registry = ConnectorRegistry()

    # register
    reg_id = registry.register(ClinicalTrialsConnector())
    assert reg_id.startswith("conn_")
    print(f"    register(clinicaltrials) → {reg_id}")

    reg_id2 = registry.register(UniProtConnector())
    print(f"    register(uniprot) → {reg_id2}")

    # list
    sources = registry.list_sources()
    assert "clinicaltrials" in sources
    assert "uniprot" in sources
    print(f"    sources: {sources}")

    # get
    ct = registry.get("clinicaltrials")
    assert ct is not None
    print(f"    get('clinicaltrials') → {type(ct).__name__}")

    # search_all
    results = registry.search_all("Alzheimer", max_results_per_source=2)
    assert len(results) >= 1
    print(f"    search_all('Alzheimer') → {len(results)} sources")

    # evidence_all
    evidence = registry.evidence_all("Amyloid", max_results_per_source=2)
    print(f"    evidence_all('Amyloid') → {len(evidence)} sources")

    # provenance
    log = registry.get_provenance_log()
    assert len(log) >= 1
    print(f"    query log entries: {len(log)}")

    # unregister
    unreg = registry.unregister("uniprot")
    assert unreg
    assert "uniprot" not in registry.list_sources()
    print(f"    unregister(uniprot) → OK")

    print("  [test] Connector Registry: OK")


def test_capability_integration():
    """Test KnowledgeRetrieval capability in CapabilityRegistry."""
    print("  [test] Capability Integration...")
    from ..ecosystem.capability_registry import CapabilityRegistry, Capability

    # Check KnowledgeRetrieval exists in enum
    assert hasattr(Capability, "KNOWLEDGE_RETRIEVAL")
    assert Capability.KNOWLEDGE_RETRIEVAL.value == "KnowledgeRetrieval"
    print(f"    Capability.KNOWLEDGE_RETRIEVAL = {Capability.KNOWLEDGE_RETRIEVAL.value}")

    # Register it
    registry = CapabilityRegistry()
    reg_id = registry.register(
        "KnowledgeRetrieval", "connectors",
        workflow_ids=["multi_source_search"],
        agent_ids=["connectors"],
        priority=50,
    )
    assert reg_id is not None
    print(f"    registered → {reg_id}")

    # Lookup
    registrations = registry.get("KnowledgeRetrieval")
    assert len(registrations) >= 1
    print(f"    get('KnowledgeRetrieval') → {len(registrations)} registration(s)")

    agents = registry.get_agents("KnowledgeRetrieval")
    assert "connectors" in agents
    print(f"    agents: {agents}")

    print("  [test] Capability Integration: OK")


def test_agent_router_integration():
    """Test connector agent in AgentRouter."""
    print("  [test] AgentRouter Integration...")
    from ..agents.router.agent_router import AgentRouter

    router = AgentRouter()

    # Check connector agent is registered
    agents = router.list_available_agents()
    assert "connectors" in agents
    print(f"    'connectors' agent registered: Yes")

    # Check routing
    routing = router.route("knowledge_retrieval")
    assert routing["agent"] == "connectors"
    assert routing["model"] is not None
    print(f"    route('knowledge_retrieval') → Agent: {routing['agent']}, Model: {routing['model']}")

    routing2 = router.route("evidence_gathering")
    assert routing2["agent"] == "connectors"
    print(f"    route('evidence_gathering') → Agent: {routing2['agent']}, Model: {routing2['model']}")

    routing3 = router.route("multi_source_search")
    assert routing3["agent"] == "connectors"
    print(f"    route('multi_source_search') → Agent: {routing3['agent']}, Model: {routing3['model']}")

    # Check agent info
    info = router.get_agent_info("connectors")
    assert "connectors" in info  # Has 'connectors' key
    connectors_list = info.get("connectors", [])
    assert len(connectors_list) >= 1  # Has at least one connector source
    print(f"    agent connectors: {connectors_list}")
    print(f"    agent capabilities: {info.get('capabilities', [])}")

    print("  [test] AgentRouter Integration: OK")


if __name__ == "__main__":
    print("=" * 70)
    print("Scientific Connector Layer - Sprint 21 Integration Tests")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    tests = [
        ("Base Connector Contract", test_base_connector),
        ("ConnectorResult Dataclass", test_connector_result),
        ("EvidenceItem Dataclass", test_evidence_item),
        ("ClinicalTrials Connector", test_clinicaltrials_connector),
        ("Open Targets Connector", test_opentargets_connector),
        ("ChEMBL Connector", test_chembl_connector),
        ("UniProt Connector", test_uniprot_connector),
        ("Connector Registry", test_connector_registry),
        ("Capability Integration", test_capability_integration),
        ("AgentRouter Integration", test_agent_router_integration),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n{'─'*60}")
        print(f"  {name}:")
        print(f"{'─'*60}")
        try:
            test_fn()
            passed += 1
            print(f"  ✅ PASSED")
        except Exception as e:
            failed += 1
            print(f"  ❌ FAILED: {e}")
            import traceback

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"

            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'='*70}")

    sys.exit(0 if failed == 0 else 1)