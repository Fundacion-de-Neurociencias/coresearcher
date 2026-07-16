"""
Entity Resolver
Links activity across multiple sources to identify scientific programs.

Focus: Not commits, but Scientific Artifacts and Objectives.
"""

from typing import List, Dict
import re


def resolve_entities(sources: Dict) -> List[Dict]:
    """
    Resolve what belongs to the same scientific program.
    
    Sources can include:
    - commits (from git)
    - files (markdown, python, etc)
    - issues/prs
    - agent sessions
    - artifacts (papers, figures, datasets)
    """
    
    entities = []
    
    # Extract objectives from multiple sources
    objectives = extract_from_files(sources.get("files", []))
    objectives.extend(extract_from_commits(sources.get("commits", [])))
    objectives.extend(extract_from_artifacts(sources.get("artifacts", [])))
    
    # Group into programs
    programs = group_into_programs(objectives)
    
    return programs


def extract_from_files(files: List[Dict]) -> List[Dict]:
    """Extract scientific objectives from file content."""
    
    objectives = []
    
    objective_indicators = [
        r"objective[s]?:?\s*(.+)",
        r"goal[s]?:?\s*(.+)",
        r"aim[s]?:?\s*(.+)",
        r"we\s+propose",
        r"our\s+approach",
        r"main\s+contribution"
    ]
    
    for f in files:
        path = f.get("path", "")
        content = f.get("content", "")
        
        # Prioritize scientific files
        if is_scientific_file(path):
            for pattern in objective_indicators:
                matches = re.findall(pattern, content, re.I)
                for match in matches:
                    objectives.append({
                        "source": f"file:{path}",
                        "text": match[:100],
                        "type": "objectives"
                    })
    
    return objectives


def extract_from_commits(commits: List[Dict]) -> List[Dict]:
    """Extract objectives from commit messages (grouped evidence)."""
    
    objectives = []
    
    # Group commits by theme first
    themes = group_commits_by_theme(commits)
    
    for theme, commits_group in themes.items():
        # Look for objective signals in theme
        if is_scientific_theme(theme):
            objectives.append({
                "source": f"commits:{len(commits_group)}",
                "text": theme,
                "type": "development-effort",
                "evidence_count": len(commits_group)
            })
    
    return objectives


def extract_from_artifacts(artifacts: List[Dict]) -> List[Dict]:
    """Extract objectives from generated artifacts."""
    
    objectives = []
    
    for artifact in artifacts:
        artifact_type = artifact.get("type", "")
        
        if artifact_type in ["paper", "ontology", "dataset", "figure"]:
            objectives.append({
                "source": f"artifact:{artifact_type}",
                "text": artifact.get("description", "")[:100],
                "type": "output"
            })
    
    return objectives


def is_scientific_file(path: str) -> bool:
    """Identify files likely to contain scientific content."""
    
    scientific_paths = [
        "paper", "manuscript", "ontology", "dataset",
        "figure", "analysis", "model", "mechanism",
        "hypothesis", "results", "methods"
    ]
    
    path_lower = path.lower()
    return any(s in path_lower for s in scientific_paths)


def group_commits_by_theme(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Group commits by emerging themes instead of treating each as separate."""
    
    themes = {}
    
    # Extract themes from commit messages
    theme_keywords = {
        "ontology": ["ontology", "ontological"],
        "biomarker": ["biomarker", "marker", "protein"],
        "diagnosis": ["diagnosis", "diagnostic", "classification"],
        "genetics": ["gene", "genetic", "dna", "rna"],
        "mechanism": ["mechanism", "pathway", "cascade"],
        "validation": ["validation", "experiment", "test"],
        "paper": ["paper", "manuscript", "write"]
    }
    
    for commit in commits:
        msg = commit.get("message", "").lower()
        
        for theme, keywords in theme_keywords.items():
            if any(kw in msg for kw in keywords):
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append(commit)
    
    return themes


def is_scientific_theme(theme: str) -> bool:
    """Determine if a theme represents scientific effort."""
    
    non_scientific = ["refactor", "test", "ci/cd", "docker", "infrastructure", "bugfix"]
    
    return not any(ns in theme for ns in non_scientific)


def group_into_programs(objectives: List[Dict]) -> List[Dict]:
    """Group objectives into program structures."""
    
    # Simple clustering - in reality would use embedding similarity
    programs = []
    
    for obj in objectives:
        # Find or create program
        program = find_or_create_program(obj, programs)
        program["objectives"].append(obj)
    
    return programs


def find_or_create_program(obj: Dict, programs: List[Dict]) -> Dict:
    """Find existing program or create new one."""
    
    obj_text = obj.get("text", "").lower()
    
    # Check for domain keywords
    domains = {
        "neuro": "Neuroscience",
        "alzheimer": "Neurodegeneration",
        "parkinson": "Neurodegeneration",
        "gene": "Genetics",
        "drug": "Pharmacology",
        "mechanism": "Mechanism Discovery",
        "ontology": "Knowledge Representation"
    }
    
    for key, domain in domains.items():
        if key in obj_text:
            # Find or create program for this domain
            for p in programs:
                if p.get("domain") == domain:
                    return p
            
            # Create new program
            program = {
                "id": f"PROGRAM-{len(programs)+1:06d}",
                "domain": domain,
                "objectives": []
            }
            programs.append(program)
            return program
    
    # Default program
    if not programs:
        program = {"id": "PROGRAM-000001", "domain": "General", "objectives": []}
        programs.append(program)
    else:
        program = programs[0]
    
    return program


if __name__ == "__main__":
    # Test with sample data
    test_sources = {
        "commits": [
            {"message": "feat: add biomarker ontology"},
            {"message": "add: APOE4 mechanism analysis"},
            {"message": "fix: paper formatting"}
        ],
        "files": [
            {"path": "papers/main.md", "content": "Our main objective is diagnostic classification"}
        ]
    }
    
    programs = resolve_entities(test_sources)
    
    for p in programs[:3]:
        print(f"\n{p['id']}: {p['domain']}")
        for obj in p['objectives']:
            print(f"  - {obj['source']}: {obj['text'][:50]}...")