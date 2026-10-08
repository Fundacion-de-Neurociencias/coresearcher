"""
python/discovery/semantic_bijectivity_auditor.py - ADR-DISCOVERY-048
Semantic Bijectivity & Formal Drift Auditor (Claim-to-Formal Isomorphism Gate).

Prevents Goodhart's Law in AI formalization (as revealed in the Navier-Stokes
OpenAI translation discrepancy) where an interactive theorem prover (Lean 4)
proves an altered, weakened, or shifted proposition rather than the exact
scientific claim stated in natural language mathematical prose.
"""

from __future__ import annotations

import re
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


class DriftType(str, Enum):
    """Classification of epistemic drift between prose and formal code."""
    EXACT_ISOMORPHISM = "EXACT_ISOMORPHISM"
    ASSUMPTION_WEAKENING = "ASSUMPTION_WEAKENING"
    EXTRA_REGULARITY_REQUIRED = "EXTRA_REGULARITY_REQUIRED"
    SIGNATURE_TAMPERING = "SIGNATURE_TAMPERING"
    BOUND_DISCREPANCY = "BOUND_DISCREPANCY"
    DOMAIN_RESTRICTION = "DOMAIN_RESTRICTION"
    UNMATCHED_PREMISES = "UNMATCHED_PREMISES"


@dataclass(frozen=True)
class MathematicalSpecification:
    """Extracted mathematical invariants from prose or Lean code."""
    target_name: str
    derivative_order: Optional[int] = None
    sobolev_regularity: Optional[float] = None
    dimension: Optional[int] = None
    bounds: List[str] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    raw_signature: str = ""
    frozen_signature_hash: str = ""


@dataclass(frozen=True)
class BijectivityVerdict:
    """Auditing verdict evaluating isomorphism between claim and formalization."""
    is_bijective: bool
    drift_type: DriftType
    drift_score: float  # 0.0 = perfect isomorphism, 1.0 = catastrophic goalpost shift
    prose_claim_name: str
    formal_theorem_name: str
    mismatches: List[str]
    frozen_hash_valid: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_bijective": self.is_bijective,
            "drift_type": self.drift_type.value,
            "drift_score": self.drift_score,
            "prose_claim_name": self.prose_claim_name,
            "formal_theorem_name": self.formal_theorem_name,
            "mismatches": self.mismatches,
            "frozen_hash_valid": self.frozen_hash_valid,
            "summary": self.summary,
        }


class SemanticBijectivityAuditor:
    """
    Audits bijectivity between human/scientific prose claims and Lean 4 types.
    Enforces frozen signature immutability to prevent tactic engines from
    mutating theorem goals into weakened variants.
    """

    @staticmethod
    def compute_signature_hash(signature: str) -> str:
        """Computes deterministic SHA-256 hash for a theorem type signature."""
        normalized = re.sub(r"\s+", " ", signature.strip())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @classmethod
    def extract_prose_specifications(
        cls,
        prose_text: str,
        claim_name: str = "Claim"
    ) -> MathematicalSpecification:
        """
        Parses natural language prose for mathematical parameters, Sobolev orders,
        and required derivative orders (e.g., '4 additional derivatives').
        """
        lower = prose_text.lower()
        deriv_order = None
        sobolev = None
        dim = None
        bounds = []
        hypotheses = []

        # Derivative orders: e.g. "4 additional derivatives", "four additional derivatives", "C^4", "4th derivative"
        num_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        deriv_match = re.search(r"(\d+|one|two|three|four|five|six)\s+(?:additional\s+)?derivatives?", lower)
        if deriv_match:
            val_str = deriv_match.group(1)
            deriv_order = int(val_str) if val_str.isdigit() else num_map.get(val_str, 0)
        else:
            c_match = re.search(r"c\^(\d+)", lower)
            if c_match:
                deriv_order = int(c_match.group(1))

        # Sobolev spaces: e.g. "H^s", "H^{5/2}", "H^4", "W^{k,p}"
        sob_match = re.search(r"h\^\{?(\d+(?:\.\d+)?|\d+/\d+)\}?", lower)
        if sob_match:
            raw_sob = sob_match.group(1)
            if "/" in raw_sob:
                num, denom = raw_sob.split("/")
                sobolev = float(num) / float(denom)
            else:
                sobolev = float(raw_sob)

        # Dimension: e.g. "in 3D", "R^3", "three dimensions"
        dim_match = re.search(r"(?:in\s+)?(\d+)d\b|r\^(\d+)", lower)
        if dim_match:
            d_val = dim_match.group(1) or dim_match.group(2)
            dim = int(d_val)

        # Bounds: e.g. "pressure-flux estimate", "energy bounded"
        if "pressure-flux" in lower or "flux" in lower:
            bounds.append("PRESSURE_FLUX_BOUND")
        if "energy" in lower and ("conserv" in lower or "bound" in lower):
            bounds.append("ENERGY_BOUND")

        # Hypotheses
        if "smooth" in lower or "c_infty" in lower or r"c^\infty" in lower:
            hypotheses.append("SMOOTH_INITIAL_DATA")
        if "compactly supported" in lower:
            hypotheses.append("COMPACT_SUPPORT")

        sig_repr = f"ProseSpec({claim_name}|deriv={deriv_order}|H={sobolev}|dim={dim}|bounds={bounds})"
        sig_hash = cls.compute_signature_hash(sig_repr)

        return MathematicalSpecification(
            target_name=claim_name,
            derivative_order=deriv_order,
            sobolev_regularity=sobolev,
            dimension=dim,
            bounds=bounds,
            hypotheses=hypotheses,
            raw_signature=sig_repr,
            frozen_signature_hash=sig_hash,
        )

    @classmethod
    def extract_lean_specifications(
        cls,
        lean_code: str,
        expected_theorem_name: Optional[str] = None
    ) -> MathematicalSpecification:
        """
        Parses Lean 4 theorem declaration to extract mathematical binders,
        Sobolev orders, and required smoothness assumptions.
        """
        # Match theorem declaration
        pattern = r"theorem\s+([A-Za-z0-9_]+)\s*(\([^)]*\)|\{[^}]*\}|\[[^\]]*\])*\s*:\s*([^:=]+):="
        match = re.search(pattern, lean_code)

        thm_name = expected_theorem_name or "UnknownTheorem"
        raw_sig = ""
        binders_and_prop = ""

        if match:
            thm_name = match.group(1)
            raw_sig = match.group(0).replace(":=", "").strip()
            binders_and_prop = match.group(0)
        else:
            binders_and_prop = lean_code

        lower = binders_and_prop.lower()
        deriv_order = None
        sobolev = None
        dim = None
        bounds = []
        hypotheses = []

        # Find derivative order assumptions in Lean binders, e.g.:
        # (h_deriv : C^5) or (deriv_order : Nat) (h : deriv >= 5) or "contDiff 5"
        diff_match = re.search(r"contdiff\s+(?:\w+\s+)?(\d+)|c\^(\d+)", lower)
        if diff_match:
            d_val = diff_match.group(1) or diff_match.group(2)
            deriv_order = int(d_val)
        else:
            num_match = re.search(r"(?:derivative|regularity)\s*[:=≥>=]\s*(\d+)", lower)
            if num_match:
                deriv_order = int(num_match.group(1))

        # Sobolev in Lean: e.g. "SobolevSpace 3" or "H^5"
        sob_match = re.search(r"sobolev(?:space)?\s+(\d+(?:\.\d+)?)|h\^\{?(\d+(?:\.\d+)?)\}?", lower)
        if sob_match:
            s_val = sob_match.group(1) or sob_match.group(2)
            sobolev = float(s_val)

        # Dimension in Lean: e.g. (d : Nat) (hd : d = 3) or Fin 3 or EuclideanSpace ℝ (Fin 3)
        dim_match = re.search(r"fin\s+(\d+)|euclidean\w*\s+ℝ\s*\(fin\s+(\d+)\)", lower)
        if dim_match:
            d_val = dim_match.group(1) or dim_match.group(2)
            dim = int(d_val)

        if "pressure" in lower or "flux" in lower:
            bounds.append("PRESSURE_FLUX_BOUND")
        if "energy" in lower:
            bounds.append("ENERGY_BOUND")

        sig_hash = cls.compute_signature_hash(raw_sig if raw_sig else lean_code)

        return MathematicalSpecification(
            target_name=thm_name,
            derivative_order=deriv_order,
            sobolev_regularity=sobolev,
            dimension=dim,
            bounds=bounds,
            hypotheses=hypotheses,
            raw_signature=raw_sig,
            frozen_signature_hash=sig_hash,
        )

    @classmethod
    def audit_bijective_alignment(
        cls,
        prose_spec: MathematicalSpecification,
        lean_spec: MathematicalSpecification,
        frozen_signature_hash: Optional[str] = None,
    ) -> BijectivityVerdict:
        """
        Audits correspondence between prose spec and Lean spec.
        Flags any goalpost shifting or assumption weakening.
        """
        mismatches: List[str] = []
        drift_score = 0.0
        drift_type = DriftType.EXACT_ISOMORPHISM

        # 1. Signature Hash Integrity Check (Frozen Immutability)
        frozen_valid = True
        if frozen_signature_hash:
            if lean_spec.frozen_signature_hash != frozen_signature_hash:
                frozen_valid = False
                drift_type = DriftType.SIGNATURE_TAMPERING
                drift_score += 0.8
                mismatches.append(
                    f"Frozen signature tampering: Expected hash '{frozen_signature_hash[:12]}...', "
                    f"found Lean signature hash '{lean_spec.frozen_signature_hash[:12]}...'."
                )

        # 2. Derivative Order Drift (The classic Navier-Stokes 4 vs 5 derivatives bug)
        if prose_spec.derivative_order is not None and lean_spec.derivative_order is not None:
            if lean_spec.derivative_order > prose_spec.derivative_order:
                diff = lean_spec.derivative_order - prose_spec.derivative_order
                drift_type = DriftType.EXTRA_REGULARITY_REQUIRED
                drift_score += min(1.0, 0.4 * diff)
                mismatches.append(
                    f"Assumption weakening (Extra regularity required): Natural prose claims {prose_spec.derivative_order} "
                    f"derivatives suffice, but Lean theorem demands {lean_spec.derivative_order} derivatives "
                    f"(a strictly weaker theorem proved by shifting the goalpost)."
                )
            elif lean_spec.derivative_order < prose_spec.derivative_order:
                # Stronger result claimed in Lean than in prose
                mismatches.append(
                    f"Regularity discrepancy: Natural prose assumes {prose_spec.derivative_order} "
                    f"derivatives, but Lean formalizes {lean_spec.derivative_order}."
                )
                drift_score += 0.2

        # 3. Sobolev Regularity Drift
        if prose_spec.sobolev_regularity is not None and lean_spec.sobolev_regularity is not None:
            if lean_spec.sobolev_regularity != prose_spec.sobolev_regularity:
                drift_type = DriftType.ASSUMPTION_WEAKENING
                drift_score += 0.5
                mismatches.append(
                    f"Sobolev index mismatch: Prose specifies H^{prose_spec.sobolev_regularity}, "
                    f"while Lean formalization operates on H^{lean_spec.sobolev_regularity}."
                )

        # 4. Dimension Mismatch
        if prose_spec.dimension is not None and lean_spec.dimension is not None:
            if prose_spec.dimension != lean_spec.dimension:
                drift_type = DriftType.DOMAIN_RESTRICTION
                drift_score += 0.9
                mismatches.append(
                    f"Dimension mismatch: Prose target is {prose_spec.dimension}D, "
                    f"while Lean theorem proves in {lean_spec.dimension}D."
                )

        # 5. Bound / Estimate Consistency
        missing_bounds = set(prose_spec.bounds) - set(lean_spec.bounds)
        if missing_bounds:
            drift_type = DriftType.BOUND_DISCREPANCY
            drift_score += 0.3
            mismatches.append(f"Prose estimates missing from Lean declaration: {list(missing_bounds)}")

        # Determine Final Isomorphism Verdict
        is_bijective = (len(mismatches) == 0) and (drift_score < 0.1) and frozen_valid

        if is_bijective:
            summary = (
                f"Bijective isomorphism verified: Formal Lean theorem '{lean_spec.target_name}' "
                f"faithfully matches mathematical prose claim '{prose_spec.target_name}' without goalpost shifting."
            )
        else:
            summary = (
                f"Epistemic Drift Detected ({drift_type.value}): Lean theorem deviates from the original "
                f"scientific claim with drift score {drift_score:.2f}. "
                f"Issues: {'; '.join(mismatches)}"
            )

        return BijectivityVerdict(
            is_bijective=is_bijective,
            drift_type=drift_type,
            drift_score=min(1.0, drift_score),
            prose_claim_name=prose_spec.target_name,
            formal_theorem_name=lean_spec.target_name,
            mismatches=mismatches,
            frozen_hash_valid=frozen_valid,
            summary=summary,
        )
