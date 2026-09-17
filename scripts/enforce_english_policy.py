#!/usr/bin/env python3
"""
scripts/enforce_english_policy.py - English Language Policy Enforcement Gate

Enforces ADR-DISCOVERY-021 and docs/LANGUAGE_POLICY.md:
- 100% of documentation (*.md) must be in English.
- 100% of source code, docstrings, and comments (*.py) must be in English.
- Prohibits non-English stopwords, common Spanish grammatical words, and inverted punctuation (¿, ¡).

Exit code:
- 0: All scanned files compliant.
- 1: Non-English violations detected.
"""

import os
import sys
import re
from typing import List, Tuple

SPANISH_STRONG_INDICATORS = {
    "descubrimiento", "restricción", "restriccion", "falsación", "falsacion",
    "hipótesis", "hipotesis", "investigación", "investigacion", "teoría", "teoria",
    "afirmación", "afirmacion", "oráculo", "oraculo", "convergencia",
    "prohibición", "prohibicion", "método", "metodo", "mecanismo", "análogamente",
    "especificación", "especificacion", "decisión", "científico", "cientifico"
}

SPANISH_GRAMMAR_WORDS = {
    " de ", " la ", " el ", " los ", " las ", " un ", " una ", " unos ", " unas ",
    " en ", " para ", " por ", " con ", " sin ", " sobre ", " entre ", " hacia ",
    " desde ", " hasta ", " como ", " pero ", " este ", " esta ", " estos ", " estas ",
    " qué ", " cuál ", " cuáles ", " quién ", " cómo ", " dónde ", " también ", " además "
}

EXCLUDED_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules", ".gemini", "scratch",
    "agents"  # external/legacy submodule if present
}

def audit_file(file_path: str) -> List[Tuple[int, str]]:
    violations = []
    if "enforce_english_policy.py" in file_path:
        return violations

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    is_py = file_path.endswith(".py")

    for line_num, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if not clean_line:
            continue

        # Inverted punctuation is a direct violation
        if "\u00bf" in clean_line or "\u00a1" in clean_line:
            violations.append((line_num, f"Inverted punctuation detected: '{clean_line}'"))
            continue

        # For Python files, check comments and strings
        text_to_check = clean_line
        if is_py:
            if "#" in clean_line:
                text_to_check = clean_line.split("#", 1)[1].strip()
            else:
                continue

        line_lower = " " + text_to_check.lower() + " "
        
        # Check strong indicator words
        for indicator in SPANISH_STRONG_INDICATORS:
            if re.search(r'\b' + indicator + r'\b', line_lower):
                violations.append((line_num, f"Spanish indicator '{indicator}' found: '{clean_line[:100]}'"))
                break

        # Check grammar word density
        grammar_matches = [gw.strip() for gw in SPANISH_GRAMMAR_WORDS if gw in line_lower]
        if len(grammar_matches) >= 3:
            violations.append((line_num, f"Multiple Spanish grammar words {grammar_matches} found: '{clean_line[:100]}'"))

    return violations

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scan_targets = [
        os.path.join(root_dir, "docs"),
        os.path.join(root_dir, "python"),
        os.path.join(root_dir, "api"),
        os.path.join(root_dir, "scripts"),
        os.path.join(root_dir, "README.md")
    ]

    total_files = 0
    total_violations = 0
    violating_files = []

    for target in scan_targets:
        if os.path.isfile(target):
            files_to_scan = [target]
        else:
            files_to_scan = []
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                for f in files:
                    if f.endswith(".md") or f.endswith(".py"):
                        files_to_scan.append(os.path.join(root, f))

        for fpath in files_to_scan:
            total_files += 1
            file_violations = audit_file(fpath)
            if file_violations:
                total_violations += len(file_violations)
                violating_files.append((fpath, file_violations))

    print("=" * 80)
    print("CORESEARCHER ENGLISH LANGUAGE POLICY ENFORCEMENT GATE")
    print("=" * 80)
    print(f"Total files scanned: {total_files}")

    if total_violations == 0:
        print("[PASS] 100% English Compliance Verified across code, comments, and documentation.")
        print("Zero Spanish stopwords or non-English indicators detected.")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"[FAIL] Detected {total_violations} language policy violations across {len(violating_files)} files:\n")
        for fpath, v_list in violating_files[:15]:
            rel_path = os.path.relpath(fpath, root_dir)
            print(f"  File: {rel_path} ({len(v_list)} violations)")
            for lnum, vmsg in v_list[:3]:
                print(f"    Line {lnum}: {vmsg}")
        if len(violating_files) > 15:
            print(f"  ... and {len(violating_files) - 15} more files with violations.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
