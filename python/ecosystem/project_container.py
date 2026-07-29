"""
Research Project Container - CoResearcher OS Sprint 6
Project container that orchestrates packs, workflows, and models.
Inspired by Claude Science "Projects" and Google "Hypothesis Generation".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


# Projects storage
PROJECTS_DIR = Path("ecosystem/projects")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_FILE = PROJECTS_DIR / "projects.json"


class ResearchProject:
    """
    A research project container.
    
    Similar to Claude Science "Projects" or Google "Hypothesis Generation",
    this orchestrates:
    - Domain packs (neurodiagnoses, genomics, etc.)
    - Workflows (research_scout, hypothesis_discovery, etc.)
    - Models (claude, gpt, qwen for specific purposes)
    """
    
    def __init__(self, project_id: str = None):
        self._project_id = project_id
        self._projects: dict = self._load()
    
    def _load(self) -> dict:
        """Load projects from disk."""
        if PROJECTS_FILE.exists():
            with open(PROJECTS_FILE, 'r') as f:
                return json.load(f)
        return {"projects": {}, "next_id": 1}
    
    def _save(self):
        """Save projects to disk."""
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(self._projects, f, indent=2)
    
    @classmethod
    def create(cls, name: str, packs: list[str], workflows: list[dict],
               models: list[dict], description: str = None) -> 'ResearchProject':
        """
        Create a new research project.
        
        Args:
            name: Project name (e.g., "Plasma pTau217")
            packs: List of domain pack IDs
            workflows: List of workflow configs {"id": "...", "packId": "...", "config": {...}}
            models: List of model configs {"id": "...", "purpose": "...", "model": "...", "provider": "..."}
            description: Optional project description
        
        Returns:
            ResearchProject instance
        """
        project = {
            "id": f"proj_{uuid4().hex[:8]}",
            "name": name,
            "description": description,
            "packs": packs,
            "workflows": workflows,
            "models": models,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "created",
        }
        
        instance = cls(project["id"])
        instance._projects["projects"][project["id"]] = project
        instance._projects["next_id"] += 1
        instance._save()
        
        return instance
    
    def get(self, project_id: str) -> Optional[dict]:
        """Get a project by ID."""
        return self._projects["projects"].get(project_id)
    
    def list(self) -> list[dict]:
        """List all projects."""
        return list(self._projects["projects"].values())
    
    def add_workflow_run(self, project_id: str, workflow_id: str, 
                         result: dict) -> str:
        """
        Record a workflow run in the project.
        
        Returns:
            Run ID
        """
        project = self.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        run_id = f"run_{uuid4().hex[:8]}"
        run = {
            "id": run_id,
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
        
        if "runs" not in project:
            project["runs"] = []
        project["runs"].append(run)
        project["updated_at"] = datetime.now().isoformat()
        project["status"] = "running"
        
        self._save()
        return run_id
    
    def complete(self, project_id: str):
        """Mark project as complete."""
        project = self.get(project_id)
        if project:
            project["status"] = "completed"
            project["updated_at"] = datetime.now().isoformat()
            self._save()
    
    def get_model_for_purpose(self, project_id: str, purpose: str) -> Optional[str]:
        """
        Get the model configured for a specific purpose.
        
        Useful for routing tasks to the right model.
        """
        project = self.get(project_id)
        if not project:
            return None
        
        for model in project.get("models", []):
            if model.get("purpose") == purpose:
                return model.get("model")
        return None
    
    def get_workflow_packs(self, project_id: str) -> list[str]:
        """
        Get all pack IDs used by project workflows.
        """
        project = self.get(project_id)
        if not project:
            return []
        
        return [w.get("packId") for w in project.get("workflows", [])]


class ProjectManager:
    """
    Manager for research projects.
    
    Provides:
    - Project creation from templates
    - Project loading and validation
    - Cross-project reference
    """
    
    def __init__(self):
        self._projects = ResearchProject()
    
    def create_from_template(self, template: str, name: str, **kwargs) -> ResearchProject:
        """
        Create a project from a predefined template.
        
        Templates:
        - biomarker_discovery: Uses neurodiagnoses + genomics
        - drug_discovery: Uses geneforge + genomics + clinical_evidence
        - clinical_trial: Uses clinical_evidence + regulatory
        - genomics_only: Uses genomics pack
        """
        templates = {
            "biomarker_discovery": {
                "packs": ["neurodiagnoses", "genomics"],
                "workflows": [
                    {"id": "research_scout", "packId": "neurodiagnoses"},
                    {"id": "genomics_analysis", "packId": "genomics"},
                ],
                "default_models": {
                    "critique": "claude",
                    "ranking": "gpt",
                    "extraction": "qwen",
                },
            },
            "drug_discovery": {
                "packs": ["geneforge", "genomics"],
                "workflows": [
                    {"id": "drug_discovery", "packId": "geneforge"},
                ],
                "default_models": {
                    "critique": "claude",
                    "ranking": "gpt",
                    "extraction": "qwen",
                },
            },
            "clinical_trial": {
                "packs": ["clinical_evidence"],
                "workflows": [
                    {"id": "clinical_evidence", "packId": "clinical_evidence"},
                ],
                "default_models": {
                    "critique": "claude",
                    "review": "gpt",
                },
            },
        }
        
        template_config = templates.get(template)
        if not template_config:
            raise ValueError(f"Unknown template: {template}")
        
        models = []
        for purpose, model in template_config["default_models"].items():
            models.append({
                "id": f"{purpose}_model",
                "purpose": purpose,
                "model": model,
            })
        
        return ResearchProject.create(
            name=name,
            packs=template_config["packs"],
            workflows=template_config["workflows"],
            models=models,
            description=f"Created from {template} template",
        )
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """Get a project by ID."""
        return self._projects.get(project_id)
    
    def list_projects(self) -> list[dict]:
        """List all projects."""
        return self._projects.list()


# =============================================================================
# Plasma pTau217 Example Project
# =============================================================================

PLASMA_PTAU217_PROJECT = {
    "name": "Plasma pTau217",
    "packs": ["neurodiagnoses", "genomics"],
    "workflows": [
        {"id": "research_scout", "packId": "neurodiagnoses"},
        {"id": "hypothesis_discovery", "packId": "neurodiagnoses"},
    ],
    "models": {
        "critique": {"model": "claude", "purpose": "critique"},
        "ranking": {"model": "gpt", "purpose": "ranking"},
        "extraction": {"model": "qwen", "purpose": "extraction"},
    },
}


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Research Project Container - Sprint 6")
    print("=" * 70)
    
    manager = ProjectManager()
    
    # Create project from template
    print("\nCreating project from template...")
    project = manager.create_from_template(
        "biomarker_discovery",
        "Plasma pTau217"
    )
    
    print(f"\nProject: {project.get(project._project_id)['name']}")
    print(f"Packs: {project.get(project._project_id)['packs']}")
    print(f"Workflows: {[w['id'] for w in project.get(project._project_id)['workflows']]}")
    
    # Get models
    print("\n" + "=" * 70)
    print("Model Configuration:")
    print("=" * 70)
    
    proj = project.get(project._project_id)
    for model in proj.get("models", []):
        print(f"  {model['purpose']}: {model['model']}")
    
    # Test model lookup
    print("\n" + "=" * 70)
    print("Model Lookup:")
    print("=" * 70)
    
    critique_model = project.get_model_for_purpose(project._project_id, "critique")
    ranking_model = project.get_model_for_purpose(project._project_id, "ranking")
    
    print(f"\nCritique model: {critique_model}")
    print(f"Ranking model: {ranking_model}")
    
    # Simulate workflow run
    print("\n" + "=" * 70)
    print("Workflow Run:")
    print("=" * 70)
    
    run_id = project.add_workflow_run(
        project._project_id,
        "research_scout",
        {"hypotheses": 12, "top_ranked": 3}
    )
    print(f"\nRecorded run: {run_id}")
    
    project.complete(project._project_id)
    print(f"Project status: {project.get(project._project_id)['status']}")
    
    print("\n" + "=" * 70)
    print("Research Project Container complete!")
    print("=" * 70)