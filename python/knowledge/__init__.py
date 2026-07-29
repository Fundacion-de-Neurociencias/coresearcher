"""
Knowledge Network - Sprint 8-16
Scientific knowledge infrastructure with translation layer.
"""

from .claim_registry import (
    ClaimRegistry,
    ClaimStatus,
    HypothesisRegistry,
    EvidenceRegistry,
)

from .contradiction_registry import (
    ContradictionRegistry,
)

from .ontology import (
    CSOConcept,
    CSO_VERSION,
    CONCEPT_DEFINITIONS,
    get_concept_uri,
    get_concept_definition,
    list_concepts,
    validate_claim_structure,
    validate_hypothesis_structure,
    format_citation,
    format_hypothesis_citation,
    OntologyManager,
)

from .trust_framework import (
    TrustScore,
    ClaimTrustFramework,
    KnowledgeHierarchy,
)

from .researcher_registry import (
    ResearcherRegistry,
    InstitutionRegistry,
    ConsensusEngine,
)

from .api import ScientificKnowledgeAPI

from .interop_layer import (
    MeasurementRegistry,
    FrameworkRegistry,
    SemanticUnitRegistry,
)

from .translation_layer import (
    ConceptRegistry,
    ConversionRegistry,
    ScientificTranslationEngine,
)

from .finding_registry import (
    FindingRegistry,
    KnowledgeDistillationEngine,
)

from .contracts import (
    KnowledgeProducerContract,
    KnowledgeConsumerContract,
    KnowledgeExchangeFormat,
    DSLRegistry,
    NEURODIAGNOSES_CONSUMER,
    MEDICALIA_CONSUMER,
    GENEFORGE_CONSUMER,
    VADEMECUM_CONSUMER,
)

from .evidence_combiner import (
    EvidenceCombiner,
    DiagnosticModelBuilder,
)

from .question_registry import (
    QuestionRegistry,
)

__all__ = [
    # Knowledge Assets (Universal)
    "ClaimRegistry",
    "ClaimStatus",
    "HypothesisRegistry",
    "EvidenceRegistry",
    "FindingRegistry",
    "QuestionRegistry",
    "ContradictionRegistry",
    
    # Ontology
    "CSOConcept",
    "CSO_VERSION",
    "CONCEPT_DEFINITIONS",
    "get_concept_uri",
    "get_concept_definition",
    "list_concepts",
    "validate_claim_structure",
    "validate_hypothesis_structure",
    "format_citation",
    "format_hypothesis_citation",
    "OntologyManager",
    
    # Trust Framework
    "TrustScore",
    "ClaimTrustFramework",
    "KnowledgeHierarchy",
    
    # Researcher Identity
    "ResearcherRegistry",
    "InstitutionRegistry",
    "ConsensusEngine",
    
    # API
    "ScientificKnowledgeAPI",
    
    # Interoperability Layer
    "MeasurementRegistry",
    "FrameworkRegistry",
    "SemanticUnitRegistry",
    
    # Translation Layer
    "ConceptRegistry",
    "ConversionRegistry",
    "ScientificTranslationEngine",
    
    # Knowledge Distillation
    "KnowledgeDistillationEngine",
    
    # Knowledge Contracts (Sprint 16)
    "KnowledgeProducerContract",
    "KnowledgeConsumerContract",
    "KnowledgeExchangeFormat",
    "DSLRegistry",
    "NEURODIAGNOSES_CONSUMER",
    "MEDICALIA_CONSUMER",
    "GENEFORGE_CONSUMER",
    "VADEMECUM_CONSUMER",
    
    # Scientific Reasoning (Sprint 17)
    "EvidenceCombiner",
    "DiagnosticModelBuilder",
]
