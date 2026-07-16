"""
Coresearcher Observer - Main Entry Point
Observes repositories and generates scientific ledgers.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from observer.git_scanner import extract_commit_messages, reconstruct_ledger
from observer.evidence_extractor import extract_evidence, group_scientific_evidence
from observer.ledger_generator import generate_ledger, save_ledger


def run_observer(repo_path: str = "."):
    """Run full observer pipeline on a repository."""
    
    # Step 1: Extract commits
    commits = extract_commit_messages(repo_path)
    
    # Step 2: Classify evidence
    evidence = extract_evidence(commits)
    
    # Step 3: Group scientific evidence into objectives
    objectives = group_scientific_evidence(evidence.get("scientific", []))
    
    # Step 4: Generate artifacts (placeholder)
    artifacts = []
    
    # Step 5: Generate contributors (placeholder)
    contributors = []
    
    # Step 6: Build ledger
    ledger_md = generate_ledger(
        objectives=objectives,
        evidence=evidence,
        artifacts=artifacts,
        contributors=contributors
    )
    
    return ledger_md


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Observing repository: {repo}")
    print("=" * 70)
    
    ledger = run_observer(repo)
    
    # Save to ledger.md in repo
    save_ledger(ledger, "ledger.md")
    
    print("\nLedger generated: ledger.md")
    print(ledger[:1000])