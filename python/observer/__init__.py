"""
CoResearcher Observer Package
Observes high-priority scientific objects and generates scientific ledgers.
"""

from .priority_discovery import (
    priority_score,
    discover_from_openalex,
    discover_from_zenodo,
    discover_from_ecosystems,
    get_top_scientific_objects,
    generate_priority_ledger,
    generate_top_100_priority_list,
)

from .zenodo_connector import (
    search_zenodo_by_concept,
    get_zenodo_record,
    get_related_records,
    zenodo_score,
    discover_neuroscience_artifacts,
)

from .validation_targets import (
    VALIDATION_REPOSITORIES,
    VALIDATION_PRIORITY_THRESHOLD,
    get_validation_priority,
    is_validation_target,
    get_all_validation_targets,
)

__all__ = [
    # Priority discovery
    "priority_score",
    "discover_from_openalex",
    "discover_from_zenodo",
    "discover_from_ecosystems",
    "get_top_scientific_objects",
    "generate_priority_ledger",
    "generate_top_100_priority_list",
    
    # Zenodo
    "search_zenodo_by_concept",
    "get_zenodo_record",
    "get_related_records",
    "zenodo_score",
    "discover_neuroscience_artifacts",
    
    # Validation
    "VALIDATION_REPOSITORIES",
    "VALIDATION_PRIORITY_THRESHOLD",
    "get_validation_priority",
    "is_validation_target",
    "get_all_validation_targets",
]

__version__ = "0.1.0"