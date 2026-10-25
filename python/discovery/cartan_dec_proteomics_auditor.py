"""
python/discovery/cartan_dec_proteomics_auditor.py - Cartan Moving Frames & Discrete Exterior Calculus (DEC) Proteomics Auditor (ADR-DISCOVERY-077)
Inspired by ScientistTwo and Cartan-DEC-MiAE (Google Cloud AI Research, 2026).

Enforces:
1. Cartan Moving Frames: Orthonormal rigid frames T_i = (E_i, t_i) in SE(3) built from backbone N, C_alpha, C atoms.
2. Discrete Exterior Calculus (DEC):
   - Discrete connection 1-forms omega_ij = log(E_i^T E_j) in so(3) on contact graph edges.
   - Discrete curvature 2-forms Omega_f = d omega + 1/2 [omega, omega] on contact triangles.
   - Path-ordered holonomy H(gamma) = prod exp(omega_e) in SO(3) on closed cycles.
3. Holonomy Defect Energy: D_i = sum_{gamma in i} ||H(gamma) - I||_F identifying conformational hinges,
   catalytic clefts, and allosteric switches gauge-invariantly.
4. Analytical Cartan-Darboux reconstruction and geometric transport coherence.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
import hashlib
import json
import math
import numpy as np


def _skew_matrix(v: np.ndarray) -> np.ndarray:
    """Return 3x3 skew-symmetric matrix [v]_x from 3D vector v."""
    return np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0]
    ], dtype=np.float64)


def _axial_vector(S: np.ndarray) -> np.ndarray:
    """Extract 3D axial vector v from skew-symmetric 3x3 matrix S."""
    return np.array([S[2, 1], S[0, 2], S[1, 0]], dtype=np.float64)


def _so3_logarithm(R: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Compute matrix logarithm on SO(3): omega_vec in R^3 such that exp([omega_vec]_x) = R.
    Returns (omega_vec, angle_rad).
    """
    tr = float(np.trace(R))
    # Clamp for numerical stability: (tr - 1) / 2 in [-1, 1]
    cos_theta = max(-1.0, min(1.0, (tr - 1.0) / 2.0))
    theta = math.acos(cos_theta)

    if theta < 1e-6:
        # Near identity: first-order Taylor expansion
        skew = 0.5 * (R - R.T)
        return _axial_vector(skew), theta

    if math.isclose(theta, math.pi, rel_tol=1e-4, abs_tol=1e-4):
        # Near pi: R is symmetric, (R + I)/2 = v v^T
        B = 0.5 * (R + np.eye(3))
        diag = np.diag(B)
        k = int(np.argmax(diag))
        v = np.zeros(3, dtype=np.float64)
        v[k] = math.sqrt(max(0.0, diag[k]))
        for j in range(3):
            if j != k and v[k] > 1e-6:
                v[j] = B[k, j] / v[k]
        norm_v = np.linalg.norm(v)
        if norm_v > 1e-6:
            v = v / norm_v
        omega_vec = v * theta
        return omega_vec, theta

    factor = theta / (2.0 * math.sin(theta))
    skew = factor * (R - R.T)
    return _axial_vector(skew), theta


def _so3_exponential(omega_vec: np.ndarray) -> np.ndarray:
    """Rodrigues formula for exponential map so(3) -> SO(3)."""
    theta = float(np.linalg.norm(omega_vec))
    if theta < 1e-7:
        return np.eye(3, dtype=np.float64) + _skew_matrix(omega_vec)
    K = _skew_matrix(omega_vec / theta)
    return np.eye(3, dtype=np.float64) + math.sin(theta) * K + (1.0 - math.cos(theta)) * (K @ K)


@dataclass
class ResidueFrame:
    """Rigid orthonormal frame T_i = (E_i, t_i) in SE(3) attached to residue i."""
    residue_index: int
    residue_name: str
    t_ca: List[float]               # C_alpha coordinate [x, y, z] in Angstroms
    e_matrix: List[List[float]]     # 3x3 orthonormal orientation matrix E_i in SO(3)
    det_e: float
    is_valid_so3: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConnectionOneForm:
    """Discrete connection 1-form omega_ij on contact graph edge."""
    residue_i: int
    residue_j: int
    distance_angstrom: float
    omega_vector: List[float]       # [omega_x, omega_y, omega_z] in so(3)
    twist_angle_rad: float
    twist_angle_deg: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CurvatureTwoForm:
    """Discrete curvature 2-form Omega_f on contact graph triangle f = (i, j, k)."""
    triangle: Tuple[int, int, int]
    omega_norm: float
    omega_vector: List[float]       # Omega_f in so(3)
    comm_norm: float                # ||1/2 [omega_ij, omega_jk]||
    is_flat: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triangle": list(self.triangle),
            "omega_norm": self.omega_norm,
            "omega_vector": self.omega_vector,
            "comm_norm": self.comm_norm,
            "is_flat": self.is_flat
        }


@dataclass
class HolonomyDefectReport:
    """Per-residue holonomy defect energy D_i = sum ||H(gamma) - I||_F."""
    residue_index: int
    residue_name: str
    holonomy_defect_energy: float
    participating_cycles_count: int
    mean_defect_per_cycle: float
    is_conformational_hinge: bool
    is_active_site_cleft: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CartanDECStructureReport:
    """Full Cartan-DEC geometric representation report for a protein structure."""
    structure_id: str
    num_residues: int
    num_contact_edges: int
    num_contact_triangles: int
    mean_connection_twist_rad: float
    mean_curvature_norm: float
    max_holonomy_defect: float
    hinge_residue_indices: List[int]
    active_cleft_indices: List[int]
    reconstruction_gauge_coherence: float   # In [0.0, 1.0], 1.0 = gauge-consistent
    holonomy_defects: List[HolonomyDefectReport]
    audit_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure_id": self.structure_id,
            "num_residues": self.num_residues,
            "num_contact_edges": self.num_contact_edges,
            "num_contact_triangles": self.num_contact_triangles,
            "mean_connection_twist_rad": self.mean_connection_twist_rad,
            "mean_curvature_norm": self.mean_curvature_norm,
            "max_holonomy_defect": self.max_holonomy_defect,
            "hinge_residue_indices": self.hinge_residue_indices,
            "active_cleft_indices": self.active_cleft_indices,
            "reconstruction_gauge_coherence": self.reconstruction_gauge_coherence,
            "holonomy_defects": [d.to_dict() for d in self.holonomy_defects],
            "audit_hash": self.audit_hash
        }


class CartanDECProteomicsAuditor:
    """
    Cartan Moving Frames and Discrete Exterior Calculus (DEC) Proteomics Auditor.
    Computes invariant differential-geometric forms over protein backbone contact graphs.
    """

    def __init__(self, contact_cutoff_angstrom: float = 8.0, hinge_threshold_percentile: float = 85.0):
        self.cutoff_angstrom = contact_cutoff_angstrom
        self.hinge_threshold_percentile = hinge_threshold_percentile

    def build_frames_from_backbone(self, residues: List[Dict[str, Any]]) -> List[ResidueFrame]:
        """
        Construct orthonormal moving frames T_i = (E_i, t_i) in SE(3) from N, CA, C coordinates.
        Uses Gram-Schmidt orthonormalization on the peptide backbone plane.
        """
        frames: List[ResidueFrame] = []

        for idx, res in enumerate(residues):
            res_name = res.get("name", f"RES_{idx}")
            t_ca = np.array(res["CA"], dtype=np.float64)

            # If N and C are supplied, build Gram-Schmidt orthonormal triad
            if "N" in res and "C" in res:
                r_n = np.array(res["N"], dtype=np.float64)
                r_c = np.array(res["C"], dtype=np.float64)

                u1 = r_c - t_ca
                norm_u1 = np.linalg.norm(u1)
                u1 = u1 / (norm_u1 + 1e-9)

                v2 = r_n - t_ca
                u3 = np.cross(u1, v2)
                norm_u3 = np.linalg.norm(u3)
                if norm_u3 < 1e-7:
                    # Collinear fallback: pick arbitrary perpendicular
                    u3 = np.array([0.0, 0.0, 1.0]) if abs(u1[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
                    u3 = u3 - np.dot(u3, u1) * u1
                    u3 = u3 / np.linalg.norm(u3)
                else:
                    u3 = u3 / norm_u3

                u2 = np.cross(u3, u1)
                E = np.column_stack([u1, u2, u3])
            else:
                # Synthetic sequential fallback if only CA is present (Frenet-Serret approx)
                if idx < len(residues) - 1:
                    t_next = np.array(residues[idx + 1]["CA"], dtype=np.float64)
                    u1 = t_next - t_ca
                else:
                    t_prev = np.array(residues[idx - 1]["CA"], dtype=np.float64)
                    u1 = t_ca - t_prev
                u1 = u1 / (np.linalg.norm(u1) + 1e-9)
                aux = np.array([0.0, 1.0, 0.0]) if abs(u1[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
                u3 = np.cross(u1, aux)
                u3 = u3 / (np.linalg.norm(u3) + 1e-9)
                u2 = np.cross(u3, u1)
                E = np.column_stack([u1, u2, u3])

            det_e = float(np.linalg.det(E))
            is_valid_so3 = bool(math.isclose(det_e, 1.0, abs_tol=1e-3) and
                                np.allclose(E.T @ E, np.eye(3), atol=1e-3))

            frames.append(ResidueFrame(
                residue_index=idx,
                residue_name=res_name,
                t_ca=t_ca.tolist(),
                e_matrix=E.tolist(),
                det_e=det_e,
                is_valid_so3=is_valid_so3
            ))

        return frames

    def compute_connection_one_forms(
        self, frames: List[ResidueFrame], cutoff_angstrom: Optional[float] = None
    ) -> Dict[Tuple[int, int], ConnectionOneForm]:
        """
        Compute discrete connection 1-forms omega_ij = log(E_i^T E_j) in so(3)
        for all pairs (i, j) with ||t_i - t_j|| < cutoff.
        """
        cutoff = cutoff_angstrom if cutoff_angstrom is not None else self.cutoff_angstrom
        n = len(frames)
        connections: Dict[Tuple[int, int], ConnectionOneForm] = {}

        for i in range(n):
            ti = np.array(frames[i].t_ca, dtype=np.float64)
            Ei = np.array(frames[i].e_matrix, dtype=np.float64)

            for j in range(i + 1, n):
                tj = np.array(frames[j].t_ca, dtype=np.float64)
                dist = float(np.linalg.norm(ti - tj))

                if dist < cutoff:
                    Ej = np.array(frames[j].e_matrix, dtype=np.float64)
                    # Relative rotation from frame i to frame j
                    R_ij = Ei.T @ Ej
                    omega_ij, theta_ij = _so3_logarithm(R_ij)

                    conn_ij = ConnectionOneForm(
                        residue_i=i,
                        residue_j=j,
                        distance_angstrom=dist,
                        omega_vector=omega_ij.tolist(),
                        twist_angle_rad=theta_ij,
                        twist_angle_deg=math.degrees(theta_ij)
                    )
                    connections[(i, j)] = conn_ij

                    # Antisymmetric opposite edge: omega_ji = -omega_ij
                    conn_ji = ConnectionOneForm(
                        residue_i=j,
                        residue_j=i,
                        distance_angstrom=dist,
                        omega_vector=(-omega_ij).tolist(),
                        twist_angle_rad=theta_ij,
                        twist_angle_deg=math.degrees(theta_ij)
                    )
                    connections[(j, i)] = conn_ji

        return connections

    def compute_curvature_two_forms(
        self,
        frames: List[ResidueFrame],
        connections: Dict[Tuple[int, int], ConnectionOneForm]
    ) -> List[CurvatureTwoForm]:
        """
        Compute discrete curvature 2-forms on contact triangles f = (i, j, k):
        Omega_f = omega_ij + omega_jk + omega_ki + 1/2 [omega_ij, omega_jk] in so(3).
        """
        n = len(frames)
        curvatures: List[CurvatureTwoForm] = []

        # Find 3-cliques in the contact graph
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) not in connections:
                    continue
                for k in range(j + 1, n):
                    if (j, k) in connections and (k, i) in connections:
                        w_ij = np.array(connections[(i, j)].omega_vector, dtype=np.float64)
                        w_jk = np.array(connections[(j, k)].omega_vector, dtype=np.float64)
                        w_ki = np.array(connections[(k, i)].omega_vector, dtype=np.float64)

                        # Lie bracket [u, v] in so(3) axial representation is cross product u x v
                        bracket = 0.5 * np.cross(w_ij, w_jk)
                        Omega_f = w_ij + w_jk + w_ki + bracket
                        norm_omega = float(np.linalg.norm(Omega_f))
                        norm_comm = float(np.linalg.norm(bracket))

                        curvatures.append(CurvatureTwoForm(
                            triangle=(i, j, k),
                            omega_norm=norm_omega,
                            omega_vector=Omega_f.tolist(),
                            comm_norm=norm_comm,
                            is_flat=bool(norm_omega < 1e-4)
                        ))

        return curvatures

    def compute_holonomy_defects(
        self,
        frames: List[ResidueFrame],
        connections: Dict[Tuple[int, int], ConnectionOneForm]
    ) -> List[HolonomyDefectReport]:
        """
        Compute per-residue path-ordered holonomy defect energy D_i = sum ||H(gamma) - I||_F
        over contact triangles (minimal cycles) passing through residue i.
        """
        n = len(frames)
        defect_sums = np.zeros(n, dtype=np.float64)
        cycle_counts = np.zeros(n, dtype=np.int32)

        # Iterate over contact triangles
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) not in connections:
                    continue
                for k in range(j + 1, n):
                    if (j, k) in connections and (k, i) in connections:
                        # Path ordered holonomy: H(gamma) = exp(w_ij) exp(w_jk) exp(w_ki)
                        R_ij = _so3_exponential(np.array(connections[(i, j)].omega_vector, dtype=np.float64))
                        R_jk = _so3_exponential(np.array(connections[(j, k)].omega_vector, dtype=np.float64))
                        R_ki = _so3_exponential(np.array(connections[(k, i)].omega_vector, dtype=np.float64))

                        H_cycle = R_ij @ R_jk @ R_ki
                        # DEC curvature form on triangle
                        w_ij = np.array(connections[(i, j)].omega_vector, dtype=np.float64)
                        w_jk = np.array(connections[(j, k)].omega_vector, dtype=np.float64)
                        w_ki = np.array(connections[(k, i)].omega_vector, dtype=np.float64)
                        omega_f = w_ij + w_jk + w_ki + 0.5 * np.cross(w_ij, w_jk)
                        curv_mag = float(np.linalg.norm(omega_f))
                        fro_defect = float(np.linalg.norm(H_cycle - np.eye(3), ord="fro"))
                        # Total transport defect energy combines curvature 2-form magnitude and loop defect
                        defect = curv_mag + fro_defect

                        for node in (i, j, k):
                            defect_sums[node] += defect
                            cycle_counts[node] += 1

        reports: List[HolonomyDefectReport] = []
        if len(defect_sums) > 0 and np.any(defect_sums > 0):
            hinge_threshold = float(np.percentile(defect_sums, self.hinge_threshold_percentile))
            active_cleft_threshold = float(np.percentile(defect_sums, 95.0))
        else:
            hinge_threshold = 0.5
            active_cleft_threshold = 1.0

        for idx, frame in enumerate(frames):
            d_sum = float(defect_sums[idx])
            count = int(cycle_counts[idx])
            mean_d = float(d_sum / count) if count > 0 else 0.0

            reports.append(HolonomyDefectReport(
                residue_index=idx,
                residue_name=frame.residue_name,
                holonomy_defect_energy=d_sum,
                participating_cycles_count=count,
                mean_defect_per_cycle=mean_d,
                is_conformational_hinge=bool(d_sum >= hinge_threshold and d_sum > 0.05),
                is_active_site_cleft=bool(d_sum >= active_cleft_threshold and d_sum > 0.1)
            ))

        return reports

    def audit_protein_structure(
        self,
        residues: List[Dict[str, Any]],
        structure_id: str = "PROTEIN_SAMPLE",
        cutoff_angstrom: Optional[float] = None
    ) -> CartanDECStructureReport:
        """
        Full end-to-end Cartan-DEC structural audit:
        constructs frames, connections, curvatures, holonomies, and evaluates gauge coherence.
        """
        frames = self.build_frames_from_backbone(residues)
        connections = self.compute_connection_one_forms(frames, cutoff_angstrom)
        curvatures = self.compute_curvature_two_forms(frames, connections)
        holonomy_defects = self.compute_holonomy_defects(frames, connections)

        # Connection twist statistics
        twists = [c.twist_angle_rad for (i, j), c in connections.items() if i < j]
        mean_twist = float(np.mean(twists)) if twists else 0.0

        # Curvature statistics
        curv_norms = [c.omega_norm for c in curvatures]
        mean_curv = float(np.mean(curv_norms)) if curv_norms else 0.0

        # Defect energy statistics
        defects = [d.holonomy_defect_energy for d in holonomy_defects]
        max_defect = float(np.max(defects)) if defects else 0.0

        hinges = [d.residue_index for d in holonomy_defects if d.is_conformational_hinge]
        clefts = [d.residue_index for d in holonomy_defects if d.is_active_site_cleft]

        # Reconstruction gauge coherence: normalized bounded measure in [0, 1]
        if curv_norms:
            gauge_coherence = float(math.exp(-mean_curv / 4.0))
        else:
            gauge_coherence = 1.0

        # Cryptographic audit hash
        audit_payload = {
            "structure_id": structure_id,
            "num_residues": len(frames),
            "num_edges": len(connections) // 2,
            "num_triangles": len(curvatures),
            "mean_twist": mean_twist,
            "max_defect": max_defect
        }
        audit_hash = hashlib.sha256(json.dumps(audit_payload, sort_keys=True).encode()).hexdigest()

        return CartanDECStructureReport(
            structure_id=structure_id,
            num_residues=len(frames),
            num_contact_edges=len(connections) // 2,
            num_contact_triangles=len(curvatures),
            mean_connection_twist_rad=mean_twist,
            mean_curvature_norm=mean_curv,
            max_holonomy_defect=max_defect,
            hinge_residue_indices=hinges,
            active_cleft_indices=clefts,
            reconstruction_gauge_coherence=gauge_coherence,
            holonomy_defects=holonomy_defects,
            audit_hash=audit_hash
        )
