"""
Validation Targets for Observer
High-priority scientific repositories for reconstruction validation.
"""

# Reference scientific repositories for validation
VALIDATION_REPOSITORIES = {
    # Neurodiagnoses ecosystem
    "Neurodiagnoses": {
        "repo": "Fundacion-de-Neurociencias/neurodiagnoses",
        "domain": "Neuroscience",
        "expected_milestones": [
            "Manuscripts detected: 3",
            "Ontologies detected: Y",
            "Datasets detected: Z",
            "Workstreams active/dormant identified",
            "Timeline reconstructed"
        ],
        "validation_weight": 1.0
    },
    
    # GeneForge ecosystem
    "GeneForge": {
        "repo": "Fundacion-de-Neurociencias/geneforge",
        "domain": "Genetics",
        "expected_milestones": [
            "Papers generated detected",
            "Software modules detected",
            "Genetic focus identified"
        ],
        "validation_weight": 1.0
    },
    
    # High-impact neuroscience tools
    "Nilearn": {
        "repo": "nilearn/nilearn",
        "domain": "Neuroimaging",
        "expected_milestones": [
            "Functions detected",
            "Datasets integrated",
            "Paper citations linked"
        ],
        "validation_weight": 0.8
    },
    
    "BIDS": {
        "repo": "bids-standard/bids-specification",
        "domain": "Neuroscience",
        "expected_milestones": [
            "Specification versions detected",
            "Extension proposals tracked",
            "Community contributions mapped"
        ],
        "validation_weight": 0.8
    },
    
    # Computational biology
    "Scanpy": {
        "repo": "scverse/scanpy",
        "domain": "Bioinformatics",
        "expected_milestones": [
            "Analysis workflows detected",
            "Figure generation tracked",
            "Benchmarking notebooks found"
        ],
        "validation_weight": 0.7
    },
    
    # Medical AI
    "MONAI": {
        "repo": "Project-MONAI/MONAI",
        "domain": "Medical AI",
        "expected_milestones": [
            "Model modules detected",
            "Training scripts catalogued",
            "Dataset integrations mapped"
        ],
        "validation_weight": 0.9
    },
}

# Priority score for validation repositories (higher than discovery threshold)
VALIDATION_PRIORITY_THRESHOLD = 0.5


def get_validation_priority(repo_name: str) -> float:
    """Get priority score for a validation repository."""
    if repo_name in VALIDATION_REPOSITORIES:
        return VALIDATION_REPOSITORIES[repo_name]["validation_weight"]
    return 0.0


def is_validation_target(repo_name: str) -> bool:
    """Check if a repository is a validation target."""
    return repo_name in VALIDATION_REPOSITORIES


def get_all_validation_targets() -> list:
    """Get list of all validation repository names."""
    return list(VALIDATION_REPOSITORIES.keys())