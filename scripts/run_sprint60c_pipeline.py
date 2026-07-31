#!/usr/bin/env python3
"""
SPRINT 60C: Master pipeline to run full trajectory reconstruction.
Orchestrates extract -> classify -> link -> reconstruct -> evaluate.
"""
import json
import os
import sys
import argparse
import subprocess
from datetime import datetime
from typing import Dict

def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and report success/failure."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"FAILED: {description}")
        return False
    else:
        print(f"SUCCESS: {description}")
        return True

def run_sprint60c_pipeline(repo: str, output_dir: str, token: str = None) -> Dict:
    """Run full SPRINT 60C pipeline on a repository."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Define pipeline steps
    repo_safe = repo.replace("/", "_")
    token_arg = f"--token {token}" if token else ""
    steps = [
        {
            "name": "Extract Decisions",
            "cmd": f"python scripts/extract_decisions.py --repo {repo} --output {output_dir}/decisions_raw.jsonl" + (f" --token {token}" if token else ""),
            "output": f"{output_dir}/decisions_raw.jsonl"
        },
        {
            "name": "Classify Decisions",
            "cmd": f"python scripts/classify_decisions.py --input {output_dir}/decisions_raw.jsonl --output {output_dir}/decisions_classified.jsonl",
            "output": f"{output_dir}/decisions_classified.jsonl"
        },
        {
            "name": "Link Decisions",
            "cmd": f"python scripts/link_decisions.py --input {output_dir}/decisions_classified.jsonl --output {output_dir}/edges.jsonl",
            "output": f"{output_dir}/edges.jsonl"
        },
        {
            "name": "Reconstruct Trajectories",
            "cmd": f"python scripts/reconstruct_trajectory.py --decisions {output_dir}/decisions_classified.jsonl --edges {output_dir}/edges.jsonl --output {output_dir}/trajectory_graph.json --repository {repo} --graph-id EG-{repo_safe} --request-id ER-{repo_safe}",
            "output": f"{output_dir}/trajectory_graph.json"
        },
        {
            "name": "Evaluate Extraction",
            "cmd": f"python scripts/evaluate_extraction.py --decisions {output_dir}/decisions_classified.jsonl --trajectories {output_dir}/trajectory_graph.json --output {output_dir}/evaluation_report.json",
            "output": f"{output_dir}/evaluation_report.json"
        }
    ]
    
    results = {
        "repository": repo,
        "pipeline_run_at": datetime.utcnow().isoformat() + "Z",
        "steps": [],
        "success": True
    }
    
    for step in steps:
        success = run_command(step["cmd"], step["name"])
        
        step_result = {
            "name": step["name"],
            "success": success,
            "output": step["output"]
        }
        results["steps"].append(step_result)
        
        if not success:
            results["success"] = False
            print(f"\nPipeline stopped at: {step['name']}")
            break
    
    # Save pipeline results
    results_path = os.path.join(output_dir, "pipeline_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"Repository: {repo}")
    print(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
    print(f"Results: {results_path}")
    
    if results["success"]:
        print("\nSPRINT 60C pipeline completed successfully")
    else:
        print("\nSPRINT 60C pipeline failed")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="SPRINT 60C: Run full trajectory reconstruction pipeline")
    parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    parser.add_argument("--output", default=None, help="Output directory (default: data/trajectories/{repo})")
    parser.add_argument("--token", help="GitHub token (optional)")
    
    args = parser.parse_args()
    
    # Set default output directory
    if not args.output:
        repo_safe = args.repo.replace("/", "_")
        args.output = f"data/trajectories/{repo_safe}"
    
    # Run pipeline
    results = run_sprint60c_pipeline(args.repo, args.output, args.token)
    
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()