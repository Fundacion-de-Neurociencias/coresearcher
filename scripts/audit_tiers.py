#!/usr/bin/env python3
"""
CoResearcher Security Tier Auditor
===================================

Enforces the Open Core + Scientific Network Moat strategy.

Checks:
1. Every Python module has a SECURITY_TIER constant
2. PRIVATE modules are never referenced in PUBLIC code
3. No PRIVATE documentation exists in docs/public/
4. Generates compliance report

Usage:
    python scripts/audit_tiers.py                     # Full audit
    python scripts/audit_tiers.py --check-private     # Only PRIVATE leak check
    python scripts/audit_tiers.py --check-annotations # Only missing annotations
    python scripts/audit_tiers.py --report            # Generate report only

Exit codes:
    0 - All clean
    1 - Warnings (missing annotations)
    2 - Critical (PRIVATE leak detected)
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Ensure we can import _tiers
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from _tiers import MODULE_TIERS, get_tier, is_private

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = REPO_ROOT / "python"
DOCS_PUBLIC = REPO_ROOT / "docs" / "public"
DOCS_PRIVATE = REPO_ROOT / "docs" / "private"


def get_python_files() -> List[Path]:
    """Get all Python files in the project (excluding __pycache__)."""
    all_files = []
    for root, dirs, files in os.walk(PYTHON_DIR):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                all_files.append(Path(root) / f)
    # Also check scripts
    scripts_dir = REPO_ROOT / "scripts"
    if scripts_dir.exists():
        for f in os.listdir(scripts_dir):
            if f.endswith(".py"):
                all_files.append(scripts_dir / f)
    return all_files


def module_path_from_file(filepath: Path) -> str:
    """Convert file path to module path (e.g., python/knowledge/claim_registry.py -> python.knowledge.claim_registry)."""
    rel = filepath.relative_to(REPO_ROOT)
    parts = list(rel.parts)
    # Remove extension
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    # Handle __init__.py -> just the package
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def check_annotation(filepath: Path) -> Tuple[bool, str]:
    """
    Check if file has SECURITY_TIER annotation.
    Returns (is_valid, current_or_expected_tier).
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False, "UNREADABLE"

    # Parse with AST to find SECURITY_TIER assignment
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False, "PARSE_ERROR"

    expected_tier = get_tier(module_path_from_file(filepath))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SECURITY_TIER":
                    if isinstance(node.value, ast.Constant):
                        actual = str(node.value.value)
                        if actual == expected_tier:
                            return True, expected_tier
                        else:
                            return False, f"MISMATCH: has {actual}, expected {expected_tier}"
    return False, f"MISSING (expected {expected_tier})"


def check_private_import_in_public(filepath: Path) -> List[str]:
    """
    Check if a PUBLIC module imports from a PRIVATE module.
    Returns list of violations.
    """
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, Exception):
        return violations

    file_module = module_path_from_file(filepath)
    file_tier = get_tier(file_module)

    # Only check PUBLIC files for PRIVATE leaks
    if file_tier != "PUBLIC":
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = alias.name
                imported_tier = get_tier(imported)
                if imported_tier == "PRIVATE":
                    violations.append(
                        f"PUBLIC file {filepath.name} imports PRIVATE module '{imported}'"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_tier = get_tier(node.module)
                if imported_tier == "PRIVATE":
                    violations.append(
                        f"PUBLIC file {filepath.name} imports from PRIVATE module '{node.module}'"
                    )
    return violations


def check_private_docs_in_public() -> List[str]:
    """Check that no PRIVATE documentation exists in public docs."""
    violations = []
    if not DOCS_PUBLIC.exists():
        return violations
    for root, dirs, files in os.walk(DOCS_PUBLIC):
        for f in files:
            filepath = Path(root) / f
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            if "PRIVATE" in content or "CONFIDENTIAL" in content:
                violations.append(
                    f"PRIVATE/CONFIDENTIAL content found in public docs: {filepath.relative_to(REPO_ROOT)}"
                )
    return violations


def run_audit() -> dict:
    """Run full audit and return results."""
    results = {
        "files_checked": 0,
        "annotations_valid": 0,
        "annotations_missing": [],
        "annotations_mismatch": [],
        "private_import_violations": [],
        "public_docs_private_content": [],
        "private_files_list": [],
        "public_files_list": [],
        "community_files_list": [],
    }

    for filepath in get_python_files():
        mod_path = module_path_from_file(filepath)
        tier = get_tier(mod_path)
        if tier == "UNCLASSIFIED":
            continue  # Skip unclassified files, they'll be caught by annotation check

        results["files_checked"] += 1
        is_valid, status = check_annotation(filepath)

        if is_valid:
            results["annotations_valid"] += 1
        else:
            if "MISSING" in status:
                results["annotations_missing"].append((str(filepath.relative_to(REPO_ROOT)), status))
            else:
                results["annotations_mismatch"].append((str(filepath.relative_to(REPO_ROOT)), status))

        # Categorize
        if tier == "PRIVATE":
            results["private_files_list"].append(str(filepath.relative_to(REPO_ROOT)))
        elif tier == "PUBLIC":
            results["public_files_list"].append(str(filepath.relative_to(REPO_ROOT)))
        elif tier == "COMMUNITY":
            results["community_files_list"].append(str(filepath.relative_to(REPO_ROOT)))

        # Check for PRIVATE imports in PUBLIC code
        vio = check_private_import_in_public(filepath)
        results["private_import_violations"].extend(vio)

    # Check docs/public/ for PRIVATE leaks
    results["public_docs_private_content"] = check_private_docs_in_public()

    return results


def print_report(results: dict):
    """Print a human-readable audit report."""
    print("=" * 70)
    print("  CoResearcher Security Tier Audit Report")
    print("=" * 70)
    print(f"\nFiles checked: {results['files_checked']}")
    print(f"  PUBLIC:     {len(results['public_files_list'])}")
    print(f"  COMMUNITY:  {len(results['community_files_list'])}")
    print(f"  PRIVATE:    {len(results['private_files_list'])}")
    print(f"  Annotations valid: {results['annotations_valid']}")

    if results["annotations_missing"]:
        print(f"\n⚠  MISSING SECURITY_TIER annotations ({len(results['annotations_missing'])}):")
        for path, status in results["annotations_missing"]:
            print(f"    {path}  ({status})")
        print("  → Add: SECURITY_TIER = \"PUBLIC\" | \"COMMUNITY\" | \"PRIVATE\"")

    if results["annotations_mismatch"]:
        print(f"\n✗ ANNOTATION MISMATCHES ({len(results['annotations_mismatch'])}):")
        for path, status in results["annotations_mismatch"]:
            print(f"    {path}  ({status})")

    if results["private_import_violations"]:
        print(f"\n🚨 PRIVATE IMPORT VIOLATIONS ({len(results['private_import_violations'])}):")
        for v in results["private_import_violations"]:
            print(f"    CRITICAL: {v}")
        print("  → PRIVATE modules must never be imported by PUBLIC modules!")

    if results["public_docs_private_content"]:
        print(f"\n🚨 PRIVATE CONTENT IN PUBLIC DOCS ({len(results['public_docs_private_content'])}):")
        for v in results["public_docs_private_content"]:
            print(f"    CRITICAL: {v}")

    # Summary
    critical = len(results["private_import_violations"]) + len(results["public_docs_private_content"])
    warnings = len(results["annotations_missing"]) + len(results["annotations_mismatch"])
    
    print(f"\n{'=' * 70}")
    if critical > 0:
        print(f"  RESULT: FAIL ({critical} critical violation(s))")
        sys.exit(2)
    elif warnings > 0:
        print(f"  RESULT: WARNING ({warnings} warning(s))")
        sys.exit(1)
    else:
        print(f"  RESULT: PASS - All tiers properly enforced")
        sys.exit(0)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CoResearcher Security Tier Auditor")
    parser.add_argument("--check-private", action="store_true", help="Only check for PRIVATE leaks")
    parser.add_argument("--check-annotations", action="store_true", help="Only check missing annotations")
    parser.add_argument("--report", action="store_true", help="Generate and print report")
    args = parser.parse_args()

    results = run_audit()

    if args.check_private:
        violations = results["private_import_violations"] + results["public_docs_private_content"]
        for v in violations:
            print(v)
        sys.exit(2 if violations else 0)
    elif args.check_annotations:
        for path, status in results["annotations_missing"] + results["annotations_mismatch"]:
            print(f"{path}: {status}")
        sys.exit(1 if results["annotations_missing"] or results["annotations_mismatch"] else 0)
    else:
        print_report(results)


if __name__ == "__main__":
    main()