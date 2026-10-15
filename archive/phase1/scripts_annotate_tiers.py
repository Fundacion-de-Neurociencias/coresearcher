#!/usr/bin/env python3
"""
Batch annotate all Python files with SECURITY_TIER.
Run this once to add the constant to every module.
"""

import ast
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from _tiers import MODULE_TIERS, get_tier

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = REPO_ROOT / "python"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def module_path_from_file(filepath: Path) -> str:
    rel = filepath.relative_to(REPO_ROOT)
    parts = list(rel.parts)
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def get_python_files():
    all_files = []
    for root, dirs, files in os.walk(PYTHON_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                all_files.append(Path(root) / f)
    for f in os.listdir(SCRIPTS_DIR):
        if f.endswith(".py") and f != "annotate_tiers.py":
            all_files.append(SCRIPTS_DIR / f)
    return all_files


def has_security_tier(content: str) -> bool:
    """Check if file already has SECURITY_TIER."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SECURITY_TIER":
                    return True
    return False


def add_annotation(filepath: Path):
    """Add SECURITY_TIER annotation to a file."""
    mod_path = module_path_from_file(filepath)
    tier = get_tier(mod_path)
    
    # Skip _tiers.py itself
    if filepath.name == "_tiers.py":
        return
    
    if tier == "UNCLASSIFIED":
        print(f"  SKIP (unclassified): {filepath.relative_to(REPO_ROOT)}")
        return

    content = filepath.read_text(encoding="utf-8")
    
    if has_security_tier(content):
        print(f"  EXISTS: {filepath.relative_to(REPO_ROOT)} ({tier})")
        return

    # Add annotation after the docstring, before imports
    lines = content.splitlines()
    
    # Find where to insert - after docstring (if any) and before imports
    insert_idx = 0
    in_docstring = False
    triple_quote_count = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith('"""') or stripped.startswith("'''"):
            # Check if it's a docstring start
            if not in_docstring:
                in_docstring = True
                triple_quote_count += 1
                # Check if docstring starts and ends on same line
                if (stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 3) or \
                   (stripped.startswith("'''") and stripped.endswith("'''") and len(stripped) > 3):
                    in_docstring = False
            else:
                in_docstring = False
                triple_quote_count += 1
        elif in_docstring:
            continue
        elif stripped.startswith(("import ", "from ")):
            insert_idx = i
            break
    
    # If we're past imports, find the last import
    last_import_idx = 0
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith(("import ", "from ")):
            last_import_idx = i + 1
            break
    
    if last_import_idx > 0:
        insert_idx = last_import_idx

    # Build annotation block
    annotation = f"\n# Security tier: {tier} — DO NOT MODIFY\n# See python/_tiers.py for classification\nSECURITY_TIER = \"{tier}\"\n"
    
    lines.insert(insert_idx, annotation)
    
    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ADDED: {filepath.relative_to(REPO_ROOT)} ({tier})")


def main():
    files = get_python_files()
    print(f"Found {len(files)} Python files")
    
    added = 0
    existed = 0
    skipped = 0
    
    for f in sorted(files):
        mod_path = module_path_from_file(f)
        tier = get_tier(mod_path)
        if tier == "UNCLASSIFIED":
            skipped += 1
            continue
        if has_security_tier(f.read_text(encoding="utf-8")):
            existed += 1
            continue
        add_annotation(f)
        added += 1
    
    print(f"\nDone: {added} annotated, {existed} already had annotation, {skipped} unclassified skipped")


if __name__ == "__main__":
    main()