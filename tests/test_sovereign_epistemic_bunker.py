"""
Tests for Sovereign Epistemic Bunker & Air-Gap Verification Gate (ADR-SOVEREIGNTY-041).
"""

import pytest
from python.discovery.sovereign_epistemic_bunker import (
    AirGapAuditReport,
    AirGapVerificationGate,
    EpistemicExpropriationBreach,
    NotarizedThoughtRecord,
    SovereignEpistemicBunker,
)


def test_cryptographic_thought_notarization():
    bunker = SovereignEpistemicBunker(author_id="dr_manuel_menendez")
    hypothesis = "Novel non-linear topological soliton coupling in high-Tc superconducting phases."

    record = bunker.notarize_intellectual_claim(hypothesis)

    assert isinstance(record, NotarizedThoughtRecord)
    assert len(record.thought_hash_sha256) == 64
    assert record.author_id == "dr_manuel_menendez"
    assert record.is_airgapped is True
    assert record.merkle_anchor is not None
    assert record.thought_hash_sha256 in bunker.ledger


def test_airgap_gate_blocks_centralized_harvesters():
    gate = AirGapVerificationGate()

    # Allowed local/sovereign endpoints
    assert gate.verify_target_endpoint("http://localhost:11434/api/generate") is True
    assert gate.verify_target_endpoint("http://127.0.0.1:1234/v1/chat/completions") is True

    # Cloud thought-harvester endpoints must raise EpistemicExpropriationBreach
    with pytest.raises(EpistemicExpropriationBreach):
        gate.verify_target_endpoint("https://api.openai.com/v1/chat/completions")

    with pytest.raises(EpistemicExpropriationBreach):
        gate.verify_target_endpoint("https://api.anthropic.com/v1/messages")


def test_session_perimeter_audit():
    bunker = SovereignEpistemicBunker()

    # Purely sovereign endpoints
    safe_endpoints = [
        "http://localhost:11434/api/generate",
        "http://127.0.0.1:1234/v1/chat/completions",
    ]
    report_safe = bunker.audit_session_perimeter(safe_endpoints)

    assert isinstance(report_safe, AirGapAuditReport)
    assert report_safe.is_fully_airgapped is True
    assert report_safe.leak_probability == 0.0
    assert "AIR-GAP CONFIRMED" in report_safe.security_verdict
    assert len(report_safe.blocked_remote_hosts) == 0

    # Compromised session with external cloud leak
    compromised_endpoints = [
        "http://localhost:11434/api/generate",
        "https://api.openai.com/v1/chat/completions",
    ]
    report_compromised = bunker.audit_session_perimeter(compromised_endpoints)

    assert report_compromised.is_fully_airgapped is False
    assert report_compromised.leak_probability == 1.0
    assert len(report_compromised.blocked_remote_hosts) == 1
    assert "SECURITY ALERT" in report_compromised.security_verdict
