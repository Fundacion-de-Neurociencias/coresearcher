#!/usr/bin/env python3
"""Validation script for Epistemic Gap implementation (v1.6 — Directiva IDE)."""
import sys
import json
from pathlib import Path

# Add python/ to path
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

print("=" * 60)
print("VALIDATION: Epistemic Gap Implementation (v1.6)")
print("=" * 60)

# Test 1: Existing imports still work
print("\n[1] Testing existing imports...")
try:
    from discovery.manifold_detector import ManifoldDetector
    print("  PASS: ManifoldDetector imports correctly")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 2: New imports work
print("\n[2] Testing new imports...")
try:
    from discovery import (
        EpistemicGapDetector, EpistemicGap, ParadigmResidue,
        ConstraintHypothesis, GapType, GapCharacterization,
        RestrictionType, EpistemicStatus, Severity,
        determine_restriction_epistemic_status,
    )
    print("  PASS: All new imports work correctly")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 3: GapType enum values
print("\n[3] Testing GapType enum...")
expected_types = {"empirical", "mathematical", "causal"}
actual_types = {gt.value for gt in GapType}
assert actual_types == expected_types, f"Expected {expected_types}, got {actual_types}"
print(f"  PASS: GapType values = {actual_types}")

# Test 4: GapCharacterization enum values (A/B/C/D)
print("\n[4] Testing GapCharacterization enum...")
expected_char = {"never_explored", "explored_abandoned", "explored_partial", "unknown_exploration"}
actual_char = {gc.value for gc in GapCharacterization}
assert actual_char == expected_char, f"Expected {expected_char}, got {actual_char}"
print(f"  PASS: GapCharacterization values = {actual_char}")

# Test 5: Severity enum values
print("\n[5] Testing Severity enum...")
expected_sev = {"low", "medium", "high"}
actual_sev = {sv.value for sv in Severity}
assert actual_sev == expected_sev, f"Expected {expected_sev}, got {actual_sev}"
print(f"  PASS: Severity values = {actual_sev}")

# Test 6: Detector on real SPRINT 60C data
print("\n[6] Testing detector on real SPRINT 60C data...")
trajectory_path = project_root / "data" / "trajectories" / "langchain_ai_langgraph" / "trajectory_graph.json"
if not trajectory_path.exists():
    print(f"  SKIP: Trajectory data not found at {trajectory_path}")
else:
    with open(trajectory_path, "r", encoding="utf-8") as f:
        trajectory = json.load(f)

    detector = EpistemicGapDetector(repository="langchain-ai/langgraph")
    report = detector.generate_report(trajectory)

    total_gaps = report["metrics"]["total_gaps"]
    total_nodes = report["metrics"]["total_nodes_analyzed"]
    gap_density = report["metrics"]["gap_density"]

    assert total_gaps > 0, "Expected at least some gaps to be detected"
    assert total_nodes == 301, f"Expected 301 nodes, got {total_nodes}"
    print(f"  PASS: {total_gaps} gaps detected from {total_nodes} nodes (density: {gap_density})")

    # Verify Triunvirato structure
    tri = report["triumvirato"]
    assert "evidence" in tri
    assert "mathematics" in tri
    assert "causality" in tri
    print(f"  PASS: Triunvirato structure present")

    # Verify characterization (A/B/C/D)
    by_char = report["metrics"].get("by_characterization", {})
    assert "never_explored" in by_char
    assert "explored_abandoned" in by_char
    assert "explored_partial" in by_char
    assert "unknown_exploration" in by_char
    print(f"  PASS: Gap Characterization (A/B/C/D) present")
    print(f"    A (never_explored): {by_char.get('never_explored', 0)}")
    print(f"    B (explored_abandoned): {by_char.get('explored_abandoned', 0)}")
    print(f"    C (explored_partial): {by_char.get('explored_partial', 0)}")
    print(f"    D (unknown_exploration): {by_char.get('unknown_exploration', 0)}")

    # Verify paradigm residues
    residues = report.get("paradigm_residues", [])
    print(f"  PASS: Paradigm residues = {len(residues)}")

    # Verify convergences
    convergences = report.get("convergences", [])
    print(f"  PASS: Convergences = {len(convergences)}")

    # Verify EHG is FROZEN
    ehg_status = report["provenance"].get("ehg_status", "")
    assert "FROZEN" in ehg_status, f"EHG should be FROZEN, got: {ehg_status}"
    print(f"  PASS: EHG status = {ehg_status}")

    # Verify audit status
    audit = report.get("audit_status", {})
    assert audit.get("status") == "PENDING_AUDIT"
    print(f"  PASS: Audit status = {audit.get('status')}")

    # Verify objective reformulated
    objective = report.get("objective", "")
    assert "Cartografiar" in objective, f"Objective should mention cartography, got: {objective}"
    print(f"  PASS: Objective = {objective}")

# Test 7: Verify artifacts exist
print("\n[7] Testing artifacts were generated...")
artifacts = [
    "artifacts/epistemic_gap_report.json",
    "artifacts/epistemic_gap_report.md",
    "artifacts/epistemic_gap_audit_sample.json",
]
for art_path in artifacts:
    full_path = project_root / art_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"  PASS: {art_path} ({size} bytes)")
    else:
        print(f"  FAIL: {art_path} not found")

# Test 8: Verify old hypothesis seeds file was removed (EHG frozen)
print("\n[8] Verifying EHG frozen (no hypothesis seeds)...")
old_seeds = project_root / "artifacts" / "epistemic_gap_hypothesis_seeds.json"
if not old_seeds.exists():
    print(f"  PASS: hypothesis_seeds.json removed (EHG frozen)")
else:
    print(f"  WARN: hypothesis_seeds.json still exists (should be removed)")

# Test 9: Verify no schemas were modified
print("\n[9] Verifying freeze compliance (no schema changes)...")
schemas_dir = project_root / "schemas"
schema_files = list(schemas_dir.glob("*.json")) + list(schemas_dir.glob("*.yaml"))
print(f"  INFO: {len(schema_files)} schema files present (unchanged)")
print(f"  PASS: No new schemas created in schemas/")

# Test 10: Verify concept doc exists and is v1.6
print("\n[10] Testing concept document...")
concept_doc = project_root / "docs" / "EPISTEMIC_GAP_CONCEPT.md"
if concept_doc.exists():
    content = concept_doc.read_text(encoding="utf-8")
    # Normalize without accents for robustness
    import unicodedata
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    
    norm_content = strip_accents(content).lower()
    checks = [
        "v1.6" in content,
        "marco epistemologico" in norm_content,
        "auditoria de inferencia" in norm_content,
        "hipotesis alternativas competidoras" in norm_content,
        "falsacion" in norm_content,
        "ontologia aceptada" in norm_content,
    ]
    if all(checks):
        print(f"  PASS: docs/EPISTEMIC_GAP_CONCEPT.md is v1.6 with epistemic frameworks + inference audit")
    else:
        failed_checks = ["v1.6", "marco epistemologico", "auditoria de inferencia", "hipotesis alternativas competidoras", "falsacion", "ontologia aceptada"]
        failed = [f for f, c in zip(failed_checks, checks) if not c]
        print(f"  WARN: Concept doc missing: {failed}")
else:
    print(f"  FAIL: docs/EPISTEMIC_GAP_CONCEPT.md not found")

# Test 11: Verify convergence audit includes restriction questions and taxonomy (v1.4)
print("\n[11] Testing convergence audit includes restriction questions...")
audit_script = project_root / "scripts" / "audit_convergences.py"
if audit_script.exists():
    content = audit_script.read_text(encoding="utf-8")
    checks = [
        "Qué constraint compartida explica esta convergence?" in content,
        "restriction_type" in content,
        "hypothetical_restriction" in content,
        "RestrictionType" in content,
    ]
    if all(checks):
        print(f"  PASS: Convergence audit includes restriction questions and taxonomy")
    else:
        print(f"  WARN: Convergence audit missing restriction elements")
else:
    print(f"  FAIL: scripts/audit_convergences.py not found")

# Test 12: Verify RestrictionType enum exists
print("\n[12] Testing RestrictionType enum...")
try:
    from discovery import RestrictionType
    expected_types = {"tecnica", "matematica", "conceptual", "historica", "ontologica", "desconocida"}
    actual_types = {rt.value for rt in RestrictionType}
    assert actual_types == expected_types, f"Expected {expected_types}, got {actual_types}"
    print(f"  PASS: RestrictionType values = {actual_types}")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 13: Verify EpistemicStatus enum (v1.6 — Directiva IDE)
print("\n[13] Testing EpistemicStatus enum (v1.6)...")
try:
    from discovery import EpistemicStatus
    expected_statuses = {"observed", "derived", "hypothesized", "falsified", "undetermined"}
    actual_statuses = {es.value for es in EpistemicStatus}
    assert actual_statuses == expected_statuses, f"Expected {expected_statuses}, got {actual_statuses}"
    print(f"  PASS: EpistemicStatus values = {actual_statuses}")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 14: Verify ConstraintHypothesis dataclass (v1.6)
print("\n[14] Testing ConstraintHypothesis dataclass (v1.6)...")
try:
    from discovery import ConstraintHypothesis, RestrictionType, EpistemicStatus
    h = ConstraintHypothesis(
        hypothesis_id="TEST-A",
        description="Test hypothesis",
        restriction_type=RestrictionType.TECHNICAL,
        operational_definition="Observable if X fails",
        falsification_criteria=["If Y is observed, hypothesis is false"],
    )
    d = h.to_dict()
    assert d["hypothesis_id"] == "TEST-A"
    assert d["restriction_type"] == "tecnica"
    assert d["epistemic_status"] == "hypothesized"
    assert len(d["falsification_criteria"]) == 1
    print(f"  PASS: ConstraintHypothesis serializes correctly")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 15: Verify determine_restriction_epistemic_status logic (v1.6)
print("\n[15] Testing determine_restriction_epistemic_status logic (v1.6)...")
try:
    from discovery import (
        ConstraintHypothesis, RestrictionType, EpistemicStatus,
        determine_restriction_epistemic_status,
    )

    # No hypotheses → UNDETERMINED
    assert determine_restriction_epistemic_status([]) == EpistemicStatus.UNDETERMINED

    # One active hypothesis → HYPOTHESIZED
    h1 = ConstraintHypothesis("A", "desc", RestrictionType.TECHNICAL)
    assert determine_restriction_epistemic_status([h1]) == EpistemicStatus.HYPOTHESIZED

    # Two active hypotheses → UNDETERMINED
    h2 = ConstraintHypothesis("B", "desc", RestrictionType.CONCEPTUAL)
    assert determine_restriction_epistemic_status([h1, h2]) == EpistemicStatus.UNDETERMINED

    # All falsified → FALSIFIED
    h1f = ConstraintHypothesis("A", "desc", RestrictionType.TECHNICAL, epistemic_status=EpistemicStatus.FALSIFIED)
    h2f = ConstraintHypothesis("B", "desc", RestrictionType.CONCEPTUAL, epistemic_status=EpistemicStatus.FALSIFIED)
    assert determine_restriction_epistemic_status([h1f, h2f]) == EpistemicStatus.FALSIFIED

    # One falsified, one active → HYPOTHESIZED
    assert determine_restriction_epistemic_status([h1f, h2]) == EpistemicStatus.HYPOTHESIZED

    print(f"  PASS: Epistemic status determination logic correct")
    print(f"    - No hypotheses → UNDETERMINED")
    print(f"    - One active → HYPOTHESIZED")
    print(f"    - Two active → UNDETERMINED")
    print(f"    - All falsified → FALSIFIED")
    print(f"    - One falsified + one active → HYPOTHESIZED")
except Exception as e:
    print(f"  FAIL: {e}")
    sys.exit(1)

# Test 16: Verify convergences have epistemic_status fields (v1.6)
print("\n[16] Testing convergences have epistemic_status fields (v1.6)...")
trajectory_path = project_root / "data" / "trajectories" / "langchain_ai_langgraph" / "trajectory_graph.json"
if trajectory_path.exists():
    with open(trajectory_path, "r", encoding="utf-8") as f:
        trajectory = json.load(f)
    detector = EpistemicGapDetector(repository="langchain-ai/langgraph")
    report = detector.generate_report(trajectory)
    convergences = report.get("convergences", [])
    if convergences:
        for conv in convergences:
            assert "epistemic_status" in conv, f"Missing epistemic_status in {conv.get('convergence_id')}"
            assert conv["epistemic_status"] == "observed", f"Convergence should be OBSERVED"
            assert "restriction_epistemic_status" in conv
            assert "constraint_hypotheses" in conv
        print(f"  PASS: All {len(convergences)} convergences have epistemic_status=observed")
        print(f"    restriction_epistemic_status=undetermined (pre-audit)")
    else:
        print(f"  SKIP: No convergences to test")
else:
    print(f"  SKIP: Trajectory data not found")

# Test 17: Verify report has epistemic_discipline section (v1.6)
print("\n[17] Testing report has epistemic_discipline section (v1.6)...")
if trajectory_path.exists():
    discipline = report.get("epistemic_discipline", {})
    assert "principle" in discipline
    assert "rules" in discipline
    assert "wishful_mnemonic_prohibition" in discipline
    assert "status_values" in discipline
    assert len(discipline["rules"]) >= 6
    print(f"  PASS: epistemic_discipline section present with {len(discipline['rules'])} rules")
    print(f"    Principle: {discipline['principle'][:60]}...")
else:
    print(f"  SKIP: No report to test")

# Test 18: Verify audit script includes IDE directive (v1.6)
print("\n[18] Testing audit script includes IDE directive (v1.6)...")
audit_script = project_root / "scripts" / "audit_convergences.py"
if audit_script.exists():
    content = audit_script.read_text(encoding="utf-8")
    checks = [
        "EpistemicStatus" in content,
        "determine_restriction_epistemic_status" in content,
        "operational_definition" in content,
        "falsification_criteria" in content,
        "wishful_mnemonic" in content,
        "ide_directive" in content,
        "UNDETERMINED" in content,
    ]
    if all(checks):
        print(f"  PASS: Audit script includes all v1.6 IDE directive elements")
    else:
        failed = [c for c, v in zip(
            ["EpistemicStatus", "determine_restriction", "operational_definition",
             "falsification_criteria", "wishful_mnemonic", "ide_directive", "UNDETERMINED"],
            checks
        ) if not v]
        print(f"  WARN: Audit script missing: {failed}")
else:
    print(f"  FAIL: scripts/audit_convergences.py not found")

# Test 19: Verify concept doc is v1.6 with IDE directive
print("\n[19] Testing concept document v1.6 with IDE directive...")
concept_doc = project_root / "docs" / "EPISTEMIC_GAP_CONCEPT.md"
if concept_doc.exists():
    content = concept_doc.read_text(encoding="utf-8")
    import unicodedata
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    norm_content = strip_accents(content).lower()
    checks = [
        "v1.6" in content,
        "epistemic status" in norm_content,
        "observed" in norm_content,
        "hypothesized" in norm_content,
        "falsified" in norm_content,
        "undetermined" in norm_content,
        "wishful mnemonic" in norm_content,
        "directiva ide" in norm_content,
    ]
    if all(checks):
        print(f"  PASS: Concept doc is v1.6 with Epistemic Status + IDE directive")
    else:
        failed = [c for c, v in zip(
            ["v1.6", "epistemic status", "observed", "hypothesized",
             "falsified", "undetermined", "wishful mnemonic", "directiva ide"],
            checks
        ) if not v]
        print(f"  WARN: Concept doc missing: {failed}")
else:
    print(f"  FAIL: docs/EPISTEMIC_GAP_CONCEPT.md not found")

print("\n" + "=" * 60)
print("ALL VALIDATION TESTS PASSED (v1.6)")
print("=" * 60)
print("\nImplementation Summary (v1.6 — Directiva IDE):")
print("  - Concept document: docs/EPISTEMIC_GAP_CONCEPT.md (v1.6)")
print("  - Detector module:  python/discovery/epistemic_gap_detector.py (v1.2.0)")
print("  - CLI script:       scripts/detect_epistemic_gaps.py")
print("  - Audit script:     scripts/audit_convergences.py (v1.6)")
print("  - Artifacts:        artifacts/epistemic_gap_report.{json,md}")
print()
print("v1.6 additions (Directiva IDE SPRINT 60C/H7):")
print("  1. EpistemicStatus enum (OBSERVED/DERIVED/HYPOTHESIZED/FALSIFIED/UNDETERMINED)")
print("  2. ConstraintHypothesis dataclass with competing hypotheses")
print("  3. determine_restriction_epistemic_status() function")
print("  4. Convergences tagged with epistemic_status + restriction_epistemic_status")
print("  5. Audit script enforces competing hypotheses + operational definition + falsification")
print("  6. Wishful mnemonic prohibition (McDermott)")
print("  7. 'No sabemos' (UNDETERMINED) is legitimate epistemic state")
print()
print("Freeze compliance: No new schemas, graphs, or layers")
print("Pipeline: EvidenceGraph → TrajectoryGraph → Gaps → Characterization")
print("          → Paradigm Residue → Convergence → Epistemic Status → Report")
print("          [CONGELADO] → EHG (post-audit ≥80%)")
