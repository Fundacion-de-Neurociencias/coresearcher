"""
Coresearcher Observer - Main Entry Point
Observes high-priority repositories and generates scientific ledgers.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from observer.git_scanner import extract_commit_messages, reconstruct_ledger
from observer.evidence_extractor import extract_evidence, group_scientific_evidence
from observer.ledger_generator import generate_ledger, save_ledger
from observer.priority_discovery import generate_priority_ledger


def run_observer(repo_path: str = ".") -> str:
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


def run_priority_discovery() -> None:
    """Discover and rank high-priority scientific objects for observation."""
    print("=" * 70)
    print("CORESEARCHER PRIORITY DISCOVERY")
    print("=" * 70)
    
    ledger = generate_priority_ledger()
    
    print(f"\nTotal objects discovered: {ledger['total_objects']}")
    print(f"  - Papers: {ledger['by_type']['papers']}")
    print(f"  - Ecosystems: {ledger['by_type']['ecosystems']}")
    
    print("\nTop 20 Priority Objects for Observation:")
    print("=" * 70)
    
    for i, obj in enumerate(ledger['top_20'], 1):
        print(f"\n{i}. [{obj['final_score']:.2f}] {obj.get('name', obj.get('title', 'Unknown')[:50])}")
        print(f"   Type: {obj['type']}, Source: {obj['source']}")
        
        if obj['type'] == 'ecosystem':
            print(f"   Repo: {obj['repo']}")
            print(f"   Domain: {obj['domain']}")
        elif obj['type'] == 'paper':
            print(f"   Citations: {obj.get('citations', 0)}")
            print(f"   Year: {obj.get('year', 'Unknown')}")
            if obj.get('github_url'):
                print(f"   GitHub: {obj['github_url']}")
    
    # Save priority list as ledger
    save_ledger(
        f"# Priority Observation Queue\n\n" + 
        f"Total objects: {ledger['total_objects']}\n\n" +
        f"## Top Objects\n\n" +
        "\n".join([
            f"- [{o['final_score']:.2f}] {o.get('name') or o.get('title', 'Unknown')[:60]}"
            for o in ledger['top_20']
        ]),
        "priority_ledger.md"
    )
    
    print("\nPriority ledger saved: priority_ledger.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--priority":
        run_priority_discovery()
    else:
        repo = sys.argv[1] if len(sys.argv) > 1 else "."
        
        print(f"Observing repository: {repo}")
        print("=" * 70)
        
        ledger = run_observer(repo)
        
        # Save to ledger.md in repo
        save_ledger(ledger, "ledger.md")
        
        print("\nLedger generated: ledger.md")
        print(ledger[:1000])
