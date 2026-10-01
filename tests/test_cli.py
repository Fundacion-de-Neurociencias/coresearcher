"""
tests/test_cli.py - Pytest suite for CoResearcher unified CLI (python/cli/main.py).
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.fast
def test_cli_info():
    """Verifies that coresearcher info executes cleanly and prints engine architecture."""
    cmd = [sys.executable, "-m", "python.cli.main", "info"]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert result.returncode == 0
    assert "CoResearcher Version:" in result.stdout
    assert "PhysicalCoherenceCourt" in result.stdout
    assert "RealityContactFirewall" in result.stdout


@pytest.mark.fast
def test_cli_verify_passed():
    """Verifies that a grounded claim with RCS >= 2.0 passes verification."""
    cmd = [
        sys.executable,
        "-m",
        "python.cli.main",
        "verify",
        "--claim",
        "Hubble constant measurement H0 = 67.4 km/s/Mpc",
        "--rcs",
        "2",
        "--anchors",
        "Planck 2018 Legacy Data Release",
    ]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert result.returncode == 0
    assert "[VERDICT: PASSED]" in result.stdout
    assert "PROMOTE_TO_INVARIANT_CONSTRAINT" in result.stdout


@pytest.mark.fast
def test_cli_verify_quarantined():
    """Verifies that an ungrounded claim (RCS < 2.0) is quarantined by the firewall."""
    cmd = [
        sys.executable,
        "-m",
        "python.cli.main",
        "verify",
        "--claim",
        "Perpetual motion generator with free energy COP > 2",
        "--rcs",
        "1",
    ]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert result.returncode == 1
    assert "[VERDICT: QUARANTINED]" in result.stdout
    assert "REJECT_PROMOTION_AND_DEMAND_PHYSICAL_BENCHMARK" in result.stdout
