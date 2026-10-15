"""
Research Program Registry - Canonical Scientific Namespace Management

This module implements the PROGRAM_CONSTITUTION.md definition.
Every Research Program must be anchored to the CSO ontology.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ProgramStatus(Enum):
    PROSPECTIVE = "prospective"  # Proposed, not yet active
    ACTIVE = "active"            # Currently producing knowledge
    MAINTAINED = "maintained"    # Stable, ongoing monitoring
    ARCHIVED = "archived"      # Completed or superseded
    DEPRECATED = "deprecated"    # Scientifically invalidated


class KnowledgeStrategy(Enum):
    PRIVATE = "private"
    PROTECTED = "protected"
    PATENT_PENDING = "patent-pending"
    PUBLISHED = "published"
    CONSENSUS = "consensus"


@dataclass
class ResearchProgram:
    """
    A Research Program is the fundamental organizational unit of scientific production.
    
    See: docs/PROGRAM_CONSTITUTION.md
    """
    program_id: str  # PROGRAM-XXXXXX
    ontological_path: str  # e.g., "Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers"
    lead_researcher: str  # RES-XXXXXX
    co_leads: List[str] = field(default_factory=list)
    status: ProgramStatus = ProgramStatus.PROSPECTIVE
    knowledge_strategy: KnowledgeStrategy = KnowledgeStrategy.PRIVATE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Multi-domain membership
    secondary_domains: List[str] = field(default_factory=list)
    
    # Activity tracking
    actions: List[str] = field(default_factory=list)
    claims: List[str] = field(default_factory=list)
    mechanisms: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    
    # Metadata
    description: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    
    def add_action(self, action_id: str) -> None:
        """Record an ACTION-XXXXXX under this program."""
        if action_id not in self.actions:
            self.actions.append(action_id)
            self.updated_at = datetime.utcnow()
    
    def add_claim(self, claim_id: str) -> None:
        """Register a CLAIM-XXXXXX produced by this program."""
        if claim_id not in self.claims:
            self.claims.append(claim_id)
            self.updated_at = datetime.utcnow()
    
    def get_canonical_uri(self) -> str:
        """Generate the canonical URI for this program."""
        # Convert ontological path to URI-friendly format
        slug = self.ontological_path.replace(" ", "-").replace("/", "--")
        return f"https://cso.coresearcher.org/program/{slug}"


class ProgramRegistry:
    """
    Central registry for all Research Programs.
    Enforces ontological anchoring and prevents duplication.
    """
    
    def __init__(self):
        self._programs: Dict[str, ResearchProgram] = {}
        self._ontology_index: Dict[str, str] = {}  # path -> program_id
    
    def create_program(
        self,
        ontological_path: str,
        lead_researcher: str,
        description: Optional[str] = None,
        secondary_domains: Optional[List[str]] = None,
    ) -> ResearchProgram:
        """
        Create a new Research Program with ontological anchoring.
        
        Requires:
        1. Ontological placement justification
        2. Non-duplication verification
        3. Domain steward approval (checked externally)
        4. Lead researcher assignment
        
        Raises:
            ValueError: If ontological path already has a program
        """
        # Check for duplication
        if ontological_path in self._ontology_index:
            existing_id = self._ontology_index[ontological_path]
            raise ValueError(
                f"Program already exists for path '{ontological_path}': {existing_id}"
            )
        
        # Generate program ID
        program_id = f"PROGRAM-{str(uuid.uuid4())[:6].upper()}"
        
        program = ResearchProgram(
            program_id=program_id,
            ontological_path=ontological_path,
            lead_researcher=lead_researcher,
            description=description,
            secondary_domains=secondary_domains or [],
        )
        
        self._programs[program_id] = program
        self._ontology_index[ontological_path] = program_id
        
        return program
    
    def get_program(self, program_id: str) -> Optional[ResearchProgram]:
        """Retrieve a program by ID."""
        return self._programs.get(program_id)
    
    def get_program_by_path(self, ontological_path: str) -> Optional[ResearchProgram]:
        """Retrieve a program by its ontological path."""
        program_id = self._ontology_index.get(ontological_path)
        if program_id:
            return self._programs.get(program_id)
        return None
    
    def list_programs(self) -> List[ResearchProgram]:
        """List all programs."""
        return list(self._programs.values())
    
    def find_duplicate(self, ontological_path: str) -> Optional[str]:
        """Check if a similar program already exists."""
        # Normalize path for comparison
        normalized = ontological_path.lower().strip()
        
        for existing_path, program_id in self._ontology_index.items():
            # Check for path overlap or similarity
            if normalized in existing_path.lower() or existing_path.lower() in normalized:
                return f"Potential duplicate: {program_id} ({existing_path})"
        
        return None
    
    def validate_ontological_placement(self, ontological_path: str) -> bool:
        """
        Validate that the path exists in CSO ontology.
        (Placeholder - integrate with actual CSO validation)
        """
        # TODO: Integrate with CSO ontology service
        # For now, accept any path that follows the expected format
        parts = ontological_path.split("/")
        return len(parts) >= 2 and parts[0].lower() == "science"


# Singleton registry instance
_registry: Optional[ProgramRegistry] = None


def get_registry() -> ProgramRegistry:
    """Get the singleton ProgramRegistry instance."""
    global _registry
    if _registry is None:
        _registry = ProgramRegistry()
    return _registry


# Convenience functions
def create_program(
    ontological_path: str,
    lead_researcher: str,
    description: Optional[str] = None,
    secondary_domains: Optional[List[str]] = None,
) -> ResearchProgram:
    """Create a new program in the canonical registry."""
    registry = get_registry()
    return registry.create_program(
        ontological_path,
        lead_researcher,
        description,
        secondary_domains,
    )


def get_program(program_id: str) -> Optional[ResearchProgram]:
    """Get a program by ID."""
    registry = get_registry()
    return registry.get_program(program_id)


def list_programs() -> List[ResearchProgram]:
    """List all programs in the registry."""
    registry = get_registry()
    return registry.list_programs()


if __name__ == "__main__":
    # Demo: Create Alzheimer Biomarker Program
    registry = get_registry()
    
    try:
        program = registry.create_program(
            ontological_path="Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers",
            lead_researcher="RES-000001",
            description="Investigation of blood and CSF biomarkers for Alzheimer's disease",
            secondary_domains=[
                "Science/Life Sciences/Genomics",
                "Science/Methods/Statistics",
            ],
        )
        print(f"Created: {program.program_id}")
        print(f"URI: {program.get_canonical_uri()}")
    except ValueError as e:
        print(f"Error: {e}")