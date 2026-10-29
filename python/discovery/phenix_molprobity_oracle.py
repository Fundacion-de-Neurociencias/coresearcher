"""
python/discovery/phenix_molprobity_oracle.py - Crystallographic & Cryo-EM Macromolecular Geometry Oracle (ADR-DISCOVERY-079)
Inspired by Lawrence Berkeley National Laboratory's (LBNL) OpenScientist and the PHENIX / MolProbity validation suite
(Adams et al., Acta Cryst. D66, 2010; Chen et al., Acta Cryst. D66, 2010; Davis et al., Nucleic Acids Res. 35, 2007).

Provides empirical, non-simulated geometric validation for macromolecular drug targets:
1. All-Atom Clashscore: Serious steric overlaps (>= 0.40 Angstroms) per 1000 atoms.
2. Ramachandran Backbone Conformation: Exact dihedral angles (phi, psi) mapped to Favored, Allowed, and Outlier regions.
3. Rotamer Dihedral Analysis: Side-chain conformation and steric hindrance (chi_1).
4. Composite MolProbity Score: Standard resolution-equivalent crystallographic metric.
5. Integration into Gate 2 (Structural Druggability) and PhysicalCoherenceCourt.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import math
import numpy as np


class RamachandranConformation(str, Enum):
    FAVORED = "FAVORED"
    ALLOWED = "ALLOWED"
    OUTLIER = "OUTLIER"


class StructuralQualityTier(str, Enum):
    EXCELLENT = "EXCELLENT"                                     # Clashscore <= 10, Rama outliers <= 0.5%, MolProbity <= 1.8
    ACCEPTABLE_DRUGGABLE = "ACCEPTABLE_DRUGGABLE"               # Clashscore <= 20, Rama outliers <= 2.0%, MolProbity <= 2.5
    MARGINAL_RELAXATION_REQUIRED = "MARGINAL_RELAXATION_REQUIRED" # Clashscore <= 30, Rama outliers <= 5.0%, MolProbity <= 3.5
    REJECTED_SEVERE_CLASHES = "REJECTED_SEVERE_CLASHES"         # Clashscore > 30, Rama outliers > 5.0%, or MolProbity > 3.5


# Canonical Bondi van der Waals radii in Angstroms (Bondi, 1964; Mantina et al., 2009)
BONDI_VDW_RADII: Dict[str, float] = {
    "H": 1.20,
    "C": 1.70,
    "N": 1.55,
    "O": 1.52,
    "P": 1.80,
    "S": 1.80,
    "FE": 1.80,
    "CA": 1.97,
    "MG": 1.73,
    "ZN": 1.39,
    "CL": 1.75,
    "F": 1.47,
    "BR": 1.85,
    "I": 1.98,
    "DEFAULT": 1.70
}

# Serious steric overlap cutoff (MolProbity standard: overlap >= 0.40 Angstroms)
SERIOUS_CLASH_CUTOFF_ANGSTROM: float = 0.40


@dataclass
class AtomCoordinate:
    """3D Cartesian coordinate of a macromolecular atom."""
    atom_name: str
    element: str
    x: float
    y: float
    z: float
    residue_seq: int
    residue_name: str
    chain_id: str = "A"

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    @property
    def vdw_radius(self) -> float:
        elem = self.element.strip().upper()
        return BONDI_VDW_RADII.get(elem, BONDI_VDW_RADII["DEFAULT"])


@dataclass
class ResidueBackboneAngles:
    """Backbone dihedral angles (phi, psi) and optional chi1 for a residue."""
    residue_seq: int
    residue_name: str
    phi_deg: Optional[float]
    psi_deg: Optional[float]
    chi1_deg: Optional[float] = None
    conformation: RamachandranConformation = RamachandranConformation.FAVORED
    is_rotamer_outlier: bool = False


@dataclass
class StericClashDetail:
    """Detailed record of a severe steric clash between two non-bonded atoms."""
    atom_1: str
    residue_1: str
    seq_1: int
    atom_2: str
    residue_2: str
    seq_2: int
    distance_angstrom: float
    vdw_sum_angstrom: float
    overlap_angstrom: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MolProbityReport:
    """Crystallographic & cryo-EM geometric validation report."""
    structure_id: str
    total_atoms: int
    num_clashes: int
    clashscore: float
    clash_details: List[StericClashDetail]
    total_residues_evaluated: int
    num_rama_favored: int
    num_rama_allowed: int
    num_rama_outliers: int
    rama_favored_pct: float
    rama_allowed_pct: float
    rama_outliers_pct: float
    num_rotamer_outliers: int
    rotamer_outliers_pct: float
    molprobity_score: float
    quality_tier: StructuralQualityTier
    is_crystallographically_sound: bool
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure_id": self.structure_id,
            "total_atoms": self.total_atoms,
            "num_clashes": self.num_clashes,
            "clashscore": self.clashscore,
            "clash_details": [c.to_dict() for c in self.clash_details],
            "total_residues_evaluated": self.total_residues_evaluated,
            "num_rama_favored": self.num_rama_favored,
            "num_rama_allowed": self.num_rama_allowed,
            "num_rama_outliers": self.num_rama_outliers,
            "rama_favored_pct": self.rama_favored_pct,
            "rama_allowed_pct": self.rama_allowed_pct,
            "rama_outliers_pct": self.rama_outliers_pct,
            "num_rotamer_outliers": self.num_rotamer_outliers,
            "rotamer_outliers_pct": self.rotamer_outliers_pct,
            "molprobity_score": self.molprobity_score,
            "quality_tier": self.quality_tier.value,
            "is_crystallographically_sound": self.is_crystallographically_sound,
            "rejection_reason": self.rejection_reason
        }


def compute_dihedral_angle(
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray
) -> float:
    """
    Compute exact dihedral angle (torsion) defined by 4 3D points in degrees [-180, 180].
    Uses the robust vector formula:
      b1 = p2 - p1, b2 = p3 - p2, b3 = p4 - p3
      n1 = b1 x b2, n2 = b2 x b3
      m = n1 x (b2 / ||b2||)
      angle = atan2(m . n2, n1 . n2)
    """
    b1 = p2 - p1
    b2 = p3 - p2
    b3 = p4 - p3

    b2_norm = np.linalg.norm(b2)
    if b2_norm < 1e-8:
        return 0.0

    b2_unit = b2 / b2_norm
    n1 = np.cross(b1, b2)
    n2 = np.cross(b2, b3)

    n1_norm = np.linalg.norm(n1)
    n2_norm = np.linalg.norm(n2)
    if n1_norm < 1e-8 or n2_norm < 1e-8:
        return 0.0

    m1 = np.cross(n1, b2_unit)
    x = float(np.dot(n1, n2))
    y = float(np.dot(m1, n2))

    angle_rad = math.atan2(y, x)
    return float(math.degrees(angle_rad))


def classify_ramachandran_region(phi_deg: float, psi_deg: float, res_name: str = "ALA") -> RamachandranConformation:
    """
    Classify backbone dihedral angles (phi, psi) into Ramachandran conformational regions
    (Core/Favored, Allowed, Outlier) based on Lovell et al. / MolProbity contours.
    """
    res = res_name.strip().upper()
    
    # Glycine has high conformational freedom
    if res == "GLY":
        if (-180 <= phi_deg <= 180) and (-180 <= psi_deg <= 180):
            # Glycine allowed almost everywhere except extreme sterics
            if (phi_deg > 0 and psi_deg > 0 and phi_deg < 60 and psi_deg < 60):
                return RamachandranConformation.OUTLIER
            return RamachandranConformation.FAVORED

    # Proline is rigid (phi restricted to -60 +/- 30)
    if res == "PRO":
        if not (-100 <= phi_deg <= -30):
            return RamachandranConformation.OUTLIER
        if (-60 <= psi_deg <= 0) or (100 <= psi_deg <= 180):
            return RamachandranConformation.FAVORED
        return RamachandranConformation.ALLOWED

    # General residues (alpha-helix, beta-sheet, left-handed alpha)
    # 1. Alpha-helical core: phi in [-120, -30], psi in [-70, -10]
    if (-120 <= phi_deg <= -30) and (-70 <= psi_deg <= -10):
        return RamachandranConformation.FAVORED

    # 2. Beta-sheet core: phi in [-160, -70], psi in [80, 180] or [-180, -160]
    if (-160 <= phi_deg <= -70) and ((80 <= psi_deg <= 180) or (-180 <= psi_deg <= -160)):
        return RamachandranConformation.FAVORED

    # 3. Left-handed alpha-helix: phi in [30, 90], psi in [10, 70]
    if (30 <= phi_deg <= 90) and (10 <= psi_deg <= 70):
        return RamachandranConformation.FAVORED

    # 4. Extended Allowed regions around alpha and beta basins
    if (-170 <= phi_deg <= -20) and (-90 <= psi_deg <= 180):
        return RamachandranConformation.ALLOWED
    if (20 <= phi_deg <= 110) and (-10 <= psi_deg <= 90):
        return RamachandranConformation.ALLOWED

    # All other configurations are non-canonical Ramachandran outliers (steric clash)
    return RamachandranConformation.OUTLIER


def classify_rotamer_outlier(chi1_deg: Optional[float], res_name: str = "LEU") -> bool:
    """
    Check if side-chain chi1 angle is a rotamer outlier.
    Canonical rotamers cluster around 60 (g+), 180 (t), and -60 / 300 (g-).
    """
    if chi1_deg is None:
        return False
    
    # Normalize to [-180, 180]
    angle = (chi1_deg + 180.0) % 360.0 - 180.0
    
    # Near g+ (60 +/- 30)
    if abs(angle - 60.0) <= 30.0:
        return False
    # Near t (180 +/- 30 or -180 +/- 30)
    if abs(abs(angle) - 180.0) <= 30.0:
        return False
    # Near g- (-60 +/- 30)
    if abs(angle - (-60.0)) <= 30.0:
        return False

    return True


class PhenixMolProbityOracle:
    """
    Empirical macromolecular stereochemistry and all-atom clash oracle.
    Implements MolProbity score and crystallographic validity evaluation.
    """

    def __init__(
        self,
        max_clashscore_tolerance: float = 30.0,
        max_rama_outliers_tolerance_pct: float = 5.0,
        max_molprobity_score_tolerance: float = 3.5
    ):
        self.max_clashscore = max_clashscore_tolerance
        self.max_rama_outliers_pct = max_rama_outliers_tolerance_pct
        self.max_molprobity_score = max_molprobity_score_tolerance

    def audit_structure_geometry(
        self,
        structure_id: str,
        atoms: List[AtomCoordinate],
        backbone_angles: Optional[List[ResidueBackboneAngles]] = None
    ) -> MolProbityReport:
        """
        Audit complete all-atom geometry, compute clashscore and MolProbity score.
        """
        if not atoms:
            return MolProbityReport(
                structure_id=structure_id,
                total_atoms=0,
                num_clashes=0,
                clashscore=0.0,
                clash_details=[],
                total_residues_evaluated=0,
                num_rama_favored=0,
                num_rama_allowed=0,
                num_rama_outliers=0,
                rama_favored_pct=0.0,
                rama_allowed_pct=0.0,
                rama_outliers_pct=0.0,
                num_rotamer_outliers=0,
                rotamer_outliers_pct=0.0,
                molprobity_score=0.0,
                quality_tier=StructuralQualityTier.EXCELLENT,
                is_crystallographically_sound=True
            )

        # 1. All-Atom Clash Analysis
        clash_details: List[StericClashDetail] = []
        n_atoms = len(atoms)

        # Pairwise distance sweep with covalent neighbor exclusion
        for i in range(n_atoms):
            a1 = atoms[i]
            r1 = a1.vdw_radius
            p1 = a1.pos
            for j in range(i + 1, n_atoms):
                a2 = atoms[j]
                
                # Exclude 1-2 and 1-3 bonded atom pairs in the same or immediately adjacent residues
                if a1.chain_id == a2.chain_id:
                    seq_diff = abs(a1.residue_seq - a2.residue_seq)
                    if seq_diff == 0:
                        # Same residue: exclude backbone-backbone or bonded bonded
                        continue
                    if seq_diff == 1:
                        # Adjacent residue: exclude peptide bond neighbors C_i - N_{i+1}
                        if (a1.atom_name == "C" and a2.atom_name == "N") or (a1.atom_name == "N" and a2.atom_name == "C"):
                            continue

                dist = float(np.linalg.norm(p1 - a2.pos))
                vdw_sum = r1 + a2.vdw_radius
                overlap = vdw_sum - dist

                # MolProbity threshold: overlap >= 0.40 A is a serious clash
                if overlap >= SERIOUS_CLASH_CUTOFF_ANGSTROM:
                    clash_details.append(StericClashDetail(
                        atom_1=a1.atom_name,
                        residue_1=a1.residue_name,
                        seq_1=a1.residue_seq,
                        atom_2=a2.atom_name,
                        residue_2=a2.residue_name,
                        seq_2=a2.residue_seq,
                        distance_angstrom=round(dist, 3),
                        vdw_sum_angstrom=round(vdw_sum, 3),
                        overlap_angstrom=round(overlap, 3)
                    ))

        num_clashes = len(clash_details)
        clashscore = float((num_clashes / max(n_atoms, 1)) * 1000.0)

        # 2. Ramachandran and Rotamer Analysis
        total_res = len(backbone_angles) if backbone_angles else 0
        num_favored = 0
        num_allowed = 0
        num_outliers = 0
        num_rot_outliers = 0

        if backbone_angles:
            for b in backbone_angles:
                if b.phi_deg is not None and b.psi_deg is not None:
                    conformation = classify_ramachandran_region(b.phi_deg, b.psi_deg, b.residue_name)
                    b.conformation = conformation
                    if conformation == RamachandranConformation.FAVORED:
                        num_favored += 1
                    elif conformation == RamachandranConformation.ALLOWED:
                        num_allowed += 1
                    else:
                        num_outliers += 1

                if b.chi1_deg is not None:
                    is_rot_out = classify_rotamer_outlier(b.chi1_deg, b.residue_name)
                    b.is_rotamer_outlier = is_rot_out
                    if is_rot_out:
                        num_rot_outliers += 1

        eval_res = max(total_res, 1)
        rama_fav_pct = float((num_favored / eval_res) * 100.0)
        rama_all_pct = float((num_allowed / eval_res) * 100.0)
        rama_out_pct = float((num_outliers / eval_res) * 100.0)
        rot_out_pct = float((num_rot_outliers / eval_res) * 100.0)

        # 3. Composite MolProbity Score
        # Formula: 0.42574*ln(1 + clashscore) + 0.32983*ln(1 + max(0, rama_out - 2)) + 0.2445*ln(1 + max(0, rot_out - 5))
        term_clash = 0.42574 * math.log(1.0 + clashscore)
        term_rama = 0.32983 * math.log(1.0 + max(0.0, rama_out_pct - 2.0))
        term_rot = 0.24450 * math.log(1.0 + max(0.0, rot_out_pct - 5.0))
        molprobity_score = float(term_clash + term_rama + term_rot)

        # 4. Quality Tier & Decision
        rejection_reason = None
        if clashscore > self.max_clashscore:
            rejection_reason = f"Clashscore {clashscore:.1f} exceeds threshold {self.max_clashscore:.1f} (severe atomic overlaps)."
        elif rama_out_pct > self.max_rama_outliers_pct:
            rejection_reason = f"Ramachandran outliers {rama_out_pct:.1f}% exceed tolerance {self.max_rama_outliers_pct:.1f}%."
        elif molprobity_score > self.max_molprobity_score:
            rejection_reason = f"MolProbity score {molprobity_score:.2f} exceeds threshold {self.max_molprobity_score:.2f}."

        is_sound = (rejection_reason is None)

        if not is_sound:
            tier = StructuralQualityTier.REJECTED_SEVERE_CLASHES
        elif clashscore <= 10.0 and rama_out_pct <= 0.5 and molprobity_score <= 1.8:
            tier = StructuralQualityTier.EXCELLENT
        elif clashscore <= 20.0 and rama_out_pct <= 2.0 and molprobity_score <= 2.5:
            tier = StructuralQualityTier.ACCEPTABLE_DRUGGABLE
        else:
            tier = StructuralQualityTier.MARGINAL_RELAXATION_REQUIRED

        return MolProbityReport(
            structure_id=structure_id,
            total_atoms=n_atoms,
            num_clashes=num_clashes,
            clashscore=round(clashscore, 2),
            clash_details=clash_details,
            total_residues_evaluated=total_res,
            num_rama_favored=num_favored,
            num_rama_allowed=num_allowed,
            num_rama_outliers=num_outliers,
            rama_favored_pct=round(rama_fav_pct, 2),
            rama_allowed_pct=round(rama_all_pct, 2),
            rama_outliers_pct=round(rama_out_pct, 2),
            num_rotamer_outliers=num_rot_outliers,
            rotamer_outliers_pct=round(rot_out_pct, 2),
            molprobity_score=round(molprobity_score, 3),
            quality_tier=tier,
            is_crystallographically_sound=is_sound,
            rejection_reason=rejection_reason
        )
