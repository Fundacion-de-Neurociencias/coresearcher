"""
tests/test_english_policy.py - Automated enforcement of the English Language Policy.
Ensures zero non-English or Spanish keywords in code, comments, and docs.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.policy
@pytest.mark.fast
def test_english_language_policy_compliance():
    """Executes the canonical English policy enforcement script."""
    script_path = REPO_ROOT / "scripts" / "enforce_english_policy.py"
    assert script_path.is_file(), f"Policy enforcement script missing at {script_path}"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"English language policy violation detected!\n" f"STDOUT:\n{result.stdout}\n" f"STDERR:\n{result.stderr}"
    )
    assert "[PASS] 100% English Compliance Verified" in result.stdout
