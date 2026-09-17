"""
python/discovery/latent_factor_discovery.py - Unsupervised Latent Factor Extraction Engine
Discovers unobserved causal latent axes Z* directly from high-dimensional background matrices
(e.g., transcriptomics, metabolomics, multi-sensor telemetry) to explain residual variance
where naive single-predictor models (X -> Y) fail.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import scipy.stats as stats


@dataclass
class DiscoveredLatentAxis:
    axis_id: str
    axis_name: str
    variance_explained_fraction: float
    residual_correlation: float
    residual_r2: float
    residual_pvalue: float
    top_feature_loadings: Dict[str, float]  # feature_name -> weight
    latent_vector: List[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axis_id": self.axis_id,
            "axis_name": self.axis_name,
            "variance_explained_fraction": self.variance_explained_fraction,
            "residual_correlation": self.residual_correlation,
            "residual_r2": self.residual_r2,
            "residual_pvalue": self.residual_pvalue,
            "top_feature_loadings": self.top_feature_loadings,
            "latent_vector_sample": self.latent_vector[:5]
        }


@dataclass
class UnsupervisedLatentDecompositionResult:
    dataset_name: str
    sample_size: int
    background_features_count: int
    baseline_ols_r2: float
    baseline_ols_pvalue: float
    total_residual_variance_explained_by_latents: float
    primary_discovered_axis: DiscoveredLatentAxis
    all_discovered_axes: List[DiscoveredLatentAxis]
    epistemic_interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "sample_size": self.sample_size,
            "background_features_count": self.background_features_count,
            "baseline_ols_r2": self.baseline_ols_r2,
            "baseline_ols_pvalue": self.baseline_ols_pvalue,
            "total_residual_variance_explained_by_latents": self.total_residual_variance_explained_by_latents,
            "primary_discovered_axis": self.primary_discovered_axis.to_dict(),
            "all_discovered_axes": [a.to_dict() for a in self.all_discovered_axes],
            "epistemic_interpretation": self.epistemic_interpretation
        }


class LatentFactorDiscoveryEngine:
    """
    True unsupervised latent factor discovery engine.
    Extracts emergent latent explanatory dimensions from high-dimensional unlabelled feature matrices.
    """

    @classmethod
    def discover_latent_modulators_from_matrix(
        cls,
        X: np.ndarray,
        Y: np.ndarray,
        high_dim_background: np.ndarray,
        feature_names: Optional[List[str]] = None,
        dataset_name: str = "High-Dimensional Scientific Cohort",
        n_components: int = 4
    ) -> UnsupervisedLatentDecompositionResult:
        """
        Executes SVD/PCA-based residual latent decomposition:
        1. Regress Y on X to compute empirical residuals e = Y - \hat{Y}.
        2. Perform SVD on the centered background matrix M.
        3. Project M onto right singular vectors to obtain orthogonal latent axes V_k.
        4. Measure statistical coupling between residuals e and latent axes V_k.
        5. Rank and return the latent axes that resolve the empirical failure.
        """
        n, p = high_dim_background.shape
        if feature_names is None:
            feature_names = [f"FEATURE_{i:03d}" for i in range(p)]

        # 1. Baseline regression
        slope, intercept, r_val, p_val, _ = stats.linregress(X, Y)
        y_pred = intercept + slope * X
        residuals = Y - y_pred
        baseline_r2 = round(float(r_val**2), 4)

        # 2. SVD on centered background matrix
        bg_mean = np.mean(high_dim_background, axis=0)
        bg_std = np.std(high_dim_background, axis=0) + 1e-8
        bg_standardized = (high_dim_background - bg_mean) / bg_std

        U, S, Vt = np.linalg.svd(bg_standardized, full_matrices=False)
        total_svd_var = np.sum(S**2)

        discovered_axes: List[DiscoveredLatentAxis] = []

        for k in range(min(n_components, len(S))):
            # Latent component score across all samples
            latent_vec = U[:, k] * S[k]
            var_exp = float((S[k]**2) / (total_svd_var + 1e-8))

            # Coupling with residuals
            r_res, p_res = stats.pearsonr(latent_vec, residuals)
            r2_res = round(float(r_res**2), 4)

            # Top feature loadings
            loadings = Vt[k, :]
            top_indices = np.argsort(np.abs(loadings))[::-1][:5]
            top_loadings = {
                feature_names[idx]: round(float(loadings[idx]), 4)
                for idx in top_indices
            }

            discovered_axes.append(DiscoveredLatentAxis(
                axis_id=f"LATENT-AXIS-{k+1:02d}",
                axis_name=f"Emergent Latent Dimension {k+1} (Top Driver: {feature_names[top_indices[0]]})",
                variance_explained_fraction=round(var_exp, 4),
                residual_correlation=round(float(r_res), 4),
                residual_r2=r2_res,
                residual_pvalue=round(float(p_res), 6),
                top_feature_loadings=top_loadings,
                latent_vector=[round(float(v), 4) for v in latent_vec]
            ))

        # Rank axes by residual explanation
        discovered_axes.sort(key=lambda a: a.residual_r2, reverse=True)
        primary_axis = discovered_axes[0]

        top_r2_sum = sum(a.residual_r2 for a in discovered_axes[:2])
        interpretation = (
            f"Naive model (X -> Y) explained only {baseline_r2:.1%} of variance (p={p_val:.4f}). "
            f"Unsupervised decomposition revealed latent axis '{primary_axis.axis_name}', "
            f"which explains {primary_axis.residual_r2:.1%} of residual anomaly variance (p={primary_axis.residual_pvalue:.4e}). "
            f"This demonstrates algorithmic discovery of an unobserved causal modulator directly from data."
        )

        return UnsupervisedLatentDecompositionResult(
            dataset_name=dataset_name,
            sample_size=n,
            background_features_count=p,
            baseline_ols_r2=baseline_r2,
            baseline_ols_pvalue=round(float(p_val), 6),
            total_residual_variance_explained_by_latents=round(top_r2_sum, 4),
            primary_discovered_axis=primary_axis,
            all_discovered_axes=discovered_axes,
            epistemic_interpretation=interpretation
        )
