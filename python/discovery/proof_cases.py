"""
python/discovery/proof_cases.py - Registry of reproducible proof cases (proof_pipeline.py, ADR-DISCOVERY-076).

A case names its proof steps, its manifest and its ledger. The registry is what the CLI
(`scripts/cases/<case>_reproduce.py`), the API (`/api/obligations/cases`) and the tests share, so a new case
becomes auditable everywhere by adding one entry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from python.discovery import proof_pipeline as pp

ROOT = pp.ROOT


@dataclass
class ProofCase:
    case_id: str
    title: str
    steps: List[pp.ProofStep]
    manifest: str  # repository-relative
    ledger: str  # repository-relative

    def audit(self) -> Dict[str, Any]:
        path = ROOT / self.manifest
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        return pp.check(self.steps, manifest, self.ledger)

    def ledger_data(self) -> Dict[str, Any]:
        return json.loads((ROOT / self.ledger).read_text(encoding="utf-8"))


EX = "examples/mahler-obligations/"
D = "python/discovery/"
BASE = [D + "mahler_interval.py", D + "mahler_obligations.py"]
TAIL = BASE + [D + "mahler_tail.py"]
MAHLER_STEPS = [
    pp.ProofStep(
        "interval",
        "scripts/cases/mahler_interval_report.py",
        EX + "interval_proof.json",
        ["first_bullet.verified", "two_variable.verified"],
        BASE,
        minutes=20,
    ),
    pp.ProofStep("tail", "scripts/cases/mahler_tail_report.py", EX + "tail_proof.json", ["result.verified"], TAIL),
    pp.ProofStep(
        "twovar",
        "scripts/cases/mahler_twovar_report.py",
        EX + "twovar_proof.json",
        ["result.verified"],
        TAIL + [D + "mahler_twovar.py"],
        minutes=12,
    ),
    pp.ProofStep(
        "ranges",
        "scripts/cases/mahler_ranges_report.py",
        EX + "ranges_proof.json",
        ["window.verified", "tail.verified"],
        TAIL + [D + "mahler_ranges.py"],
        minutes=135,
    ),
    pp.ProofStep(
        "segment_box",
        "scripts/cases/mahler_segment_box_report.py",
        EX + "segment_box_proof.json",
        ["verified"],
        TAIL + [D + "mahler_ranges.py", D + "mahler_segment_box.py"],
        minutes=12,
    ),
    pp.ProofStep(
        "segment_tails",
        "scripts/cases/mahler_segment_tails_report.py",
        EX + "segment_tails_proof.json",
        ["verified"],
        TAIL
        + [
            D + "mahler_ranges.py",
            D + "mahler_segment_box.py",
            D + "mahler_segment_tails.py",
            D + "interval_engine.py",
        ],
        minutes=40,
    ),
    pp.ProofStep(
        "ledger",
        "scripts/cases/mahler_obligations_report.py",
        EX + "ledger.json",
        [],
        BASE
        + [D + "obligation_ledger.py", D + "mahler_segment.py"]
        + [EX + f for f in ("interval_proof.json", "tail_proof.json", "twovar_proof.json", "ranges_proof.json")]
        + [EX + "segment_box_proof.json", EX + "segment_tails_proof.json"],
        minutes=14,
    ),
]

CASES: Dict[str, ProofCase] = {
    "mahler-scalar-input": ProofCase(
        "mahler-scalar-input",
        "Scalar input of the Mahler conjecture for general convex bodies (openai/math)",
        MAHLER_STEPS,
        EX + "manifest.json",
        EX + "ledger.json",
    ),
}
