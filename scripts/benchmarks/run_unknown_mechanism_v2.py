"""Unknown-mechanism benchmark v2, implementing docs/reference/benchmarks/UNKNOWN_MECHANISM_V2_PROTOCOL.md.

Usage:
    python scripts/benchmarks/run_unknown_mechanism_v2.py

Writes docs/reference/benchmarks/unknown_mechanism_v2_results.json with the per-world table,
the aggregate statistics and the SHA-256 of the protocol in force when the run happened.
The exit code is 0 whenever the run completes. The pre-registered criteria are recorded in the
output; they do not change the exit code.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.unknown_mechanism_benchmark import BlindWorldGenerator, HiddenLawArchetype  # noqa: E402

PROTOCOL = ROOT / "docs" / "reference" / "benchmarks" / "UNKNOWN_MECHANISM_V2_PROTOCOL.md"
RESULTS = ROOT / "docs" / "reference" / "benchmarks" / "unknown_mechanism_v2_results.json"
NULL_RESULTS = ROOT / "docs" / "reference" / "benchmarks" / "unknown_mechanism_v2_null_control.json"
ARCHETYPES = list(HiddenLawArchetype)
EXPECTED_FAMILY = {
    HiddenLawArchetype.HARMONIC_NONLINEAR: "additive_basis",
    HiddenLawArchetype.MULTIPLICATIVE_COUPLING: "interaction_Z1",
    HiddenLawArchetype.UNOBSERVED_LATENT_MANIFOLD: "latent_pc1",
    HiddenLawArchetype.REGIME_PHASE_SHIFT: "regime_Z1",
    HiddenLawArchetype.SIMPSONS_CAUSAL_INVERSION: "regime_Z2",
    HiddenLawArchetype.THRESHOLD_INVARIANT_GATE: None,
}
N_WORLDS = 100
N_ROWS = 240
BOOT_SEED = 20261012
BOOT_RESAMPLES = 10_000
OMEGAS = [0.4, 0.8, 1.2, 1.6]
Z_SCORE_95 = 1.959963984540054


def r2(y, yhat):
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def fit_predict(design_train, y_train, design_eval):
    coef, *_ = np.linalg.lstsq(design_train, y_train, rcond=None)
    return design_eval @ coef


def wilson(successes, trials):
    if trials == 0:
        return float("nan"), float("nan")
    p = successes / trials
    z2 = Z_SCORE_95**2
    centre = (p + z2 / (2 * trials)) / (1 + z2 / trials)
    half = Z_SCORE_95 * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / (1 + z2 / trials)
    return centre - half, centre + half


def build_splits(world):
    """Concatenates the generator's halves and returns index slices for the three splits."""
    X = np.concatenate([world.X_train, world.X_test])
    Z1 = np.concatenate([world.Z_train["Z_1"], world.Z_test["Z_1"]])
    Z2 = np.concatenate([world.Z_train["Z_2"], world.Z_test["Z_2"]])
    B = np.vstack([world.background_matrix_train, world.background_matrix_test])
    Y = np.concatenate([world.Y_train, world.Y_test])
    half = len(world.X_train)
    return {
        "X": X,
        "Z1": Z1,
        "Z2": Z2,
        "B": B,
        "Y": Y,
        "disc": slice(0, half // 2),
        "val": slice(half // 2, half),
        "test": slice(half, len(X)),
    }


def candidate_designs(d):
    """Design matrix of every library candidate. Medians and PCA use the discovery split only."""
    X, Z1, Z2, B = d["X"], d["Z1"], d["Z2"], d["B"]
    one = np.ones_like(X)
    disc = d["disc"]
    t1 = np.median(Z1[disc])
    t2 = np.median(Z2[disc])
    I1 = (Z1 > t1).astype(float)
    I2 = (Z2 > t2).astype(float)
    Bc = B - B[disc].mean(axis=0)
    _, _, vt = np.linalg.svd(Bc[disc], full_matrices=False)
    pc1 = Bc @ vt[0]
    designs = {
        "naive_linear": ("naive_linear", np.column_stack([one, X])),
        "interaction_Z1": ("interaction_Z1", np.column_stack([one, X, Z1, X * Z1])),
        "interaction_Z2": ("interaction_Z2", np.column_stack([one, X, Z2, X * Z2])),
        "quadratic_X": ("quadratic_X", np.column_stack([one, X, X**2])),
        "regime_Z1": ("regime_Z1", np.column_stack([one, X, I1, X * I1])),
        "regime_Z2": ("regime_Z2", np.column_stack([one, X, I2, X * I2])),
        "latent_pc1": ("latent_pc1", np.column_stack([one, X, pc1])),
    }
    for w in OMEGAS:
        designs[f"additive_basis_w{w}"] = (
            "additive_basis",
            np.column_stack([one, X, Z1, Z1**2, np.sin(w * X)]),
        )
    return designs


def flexible_design(d):
    X, Z1, Z2 = d["X"], d["Z1"], d["Z2"]
    one = np.ones_like(X)
    return np.column_stack(
        [
            one,
            X,
            Z1,
            Z2,
            X**2,
            Z1**2,
            Z2**2,
            X * Z1,
            X * Z2,
            Z1 * Z2,
            X**3,
            Z1**3,
            Z2**3,
        ]
    )


def run_world(i, null=False):
    archetype = ARCHETYPES[i % len(ARCHETYPES)]
    world = BlindWorldGenerator.generate_world(i, archetype, n=N_ROWS)
    d = build_splits(world)
    Y = d["Y"]
    if null:
        # Null control (added after the primary run, see protocol section 10): permuting Y within the
        # world destroys every X->Y relationship, so any "recovery" here is a false positive.
        Y = np.random.default_rng(7000 + i).permutation(Y)
        d["Y"] = Y
    disc, val, test = d["disc"], d["val"], d["test"]
    designs = candidate_designs(d)

    # 1. Selection uses only the validation split.
    scores = {}
    for name, (_, M) in designs.items():
        yhat_val = fit_predict(M[disc], Y[disc], M[val])
        scores[name] = (r2(Y[val], yhat_val), M.shape[1])
    selected = max(scores, key=lambda k: (round(scores[k][0], 12), -scores[k][1]))
    selected_family = designs[selected][0]

    # 2. Final refit on discovery + validation, one evaluation on the test split.
    fit_idx = np.arange(disc.start, val.stop)

    def test_r2(M):
        return r2(Y[test], fit_predict(M[fit_idx], Y[fit_idx], M[test]))

    r2_abduced = test_r2(designs[selected][1])
    r2_naive = test_r2(designs["naive_linear"][1])
    r2_flex = test_r2(flexible_design(d))

    expected = EXPECTED_FAMILY[archetype]
    return {
        "world": world.world_id,
        "seed": 1000 + i,
        "archetype": archetype.value,
        "ground_truth": world.ground_truth_formula,
        "selected_candidate": selected,
        "selected_family": selected_family,
        "expected_family": expected,
        "recovered": None if expected is None else selected_family == expected,
        "validation_r2": {k: round(v[0], 6) for k, v in scores.items()},
        "test_r2_abduced": r2_abduced,
        "test_r2_naive": r2_naive,
        "test_r2_flexible": r2_flex,
        "delta_naive": r2_abduced - r2_naive,
        "delta_flexible": r2_abduced - r2_flex,
    }


def bootstrap_mean_ci(values, rng):
    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(BOOT_RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main(argv=()):
    null = "--null-control" in argv
    results_path = NULL_RESULTS if null else RESULTS
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    rows = [run_world(i, null=null) for i in range(N_WORLDS)]
    rng = np.random.default_rng(BOOT_SEED)

    scorable = [r for r in rows if r["recovered"] is not None]
    recovered = sum(1 for r in scorable if r["recovered"])
    rec_lo, rec_hi = wilson(recovered, len(scorable))

    d_flex = [r["delta_flexible"] for r in rows]
    d_naive = [r["delta_naive"] for r in rows]
    flex_lo, flex_hi = bootstrap_mean_ci(d_flex, rng)
    naive_lo, naive_hi = bootstrap_mean_ci(d_naive, rng)
    positive_flex = sum(1 for v in d_flex if v > 0)
    pos_lo, pos_hi = wilson(positive_flex, len(rows))

    summary = {
        "protocol_sha256": protocol_sha,
        "n_worlds": len(rows),
        "rows_per_world": N_ROWS,
        "recovery": {
            "recovered": recovered,
            "scorable": len(scorable),
            "rate": recovered / len(scorable),
            "wilson_95": [rec_lo, rec_hi],
        },
        "mean_delta_flexible": float(np.mean(d_flex)),
        "bootstrap_95_flexible": [flex_lo, flex_hi],
        "mean_delta_naive": float(np.mean(d_naive)),
        "bootstrap_95_naive": [naive_lo, naive_hi],
        "fraction_worlds_delta_flexible_positive": {"count": positive_flex, "wilson_95": [pos_lo, pos_hi]},
        "mean_test_r2": {
            "abduced": float(np.mean([r["test_r2_abduced"] for r in rows])),
            "naive": float(np.mean([r["test_r2_naive"] for r in rows])),
            "flexible": float(np.mean([r["test_r2_flexible"] for r in rows])),
        },
        "criteria": {
            "primary_flexible_lower_bound_above_zero": bool(flex_lo > 0),
            "secondary_recovery_lower_bound_above_quarter": bool(rec_lo > 0.25),
        },
    }
    out = {"protocol": "docs/reference/benchmarks/UNKNOWN_MECHANISM_V2_PROTOCOL.md", "summary": summary, "worlds": rows}
    results_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"protocol sha256: {protocol_sha[:16]}")
    print(
        f"recovery: {recovered}/{len(scorable)} = {recovered / len(scorable):.1%} "
        f"(Wilson 95% {rec_lo:.1%} to {rec_hi:.1%})"
    )
    print(f"mean delta R2 vs flexible: {np.mean(d_flex):+.4f} (bootstrap 95% {flex_lo:+.4f} to {flex_hi:+.4f})")
    print(f"mean delta R2 vs naive:    {np.mean(d_naive):+.4f} (bootstrap 95% {naive_lo:+.4f} to {naive_hi:+.4f})")
    print(f"worlds with delta R2 > 0 vs flexible: {positive_flex}/{len(rows)}")
    print(
        f"primary criterion met: {summary['criteria']['primary_flexible_lower_bound_above_zero']}; "
        f"secondary criterion met: {summary['criteria']['secondary_recovery_lower_bound_above_quarter']}"
    )
    print(f"results written to {results_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
