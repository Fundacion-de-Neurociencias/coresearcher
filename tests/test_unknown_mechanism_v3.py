"""Unknown-mechanism benchmark v3: arms, PySR selection and refit (with a stub search), and scoring."""

import sys
from pathlib import Path

import numpy as np
import pytest
import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_unknown_mechanism_v2 as v2  # noqa: E402
import run_unknown_mechanism_v3 as v3  # noqa: E402


@pytest.mark.parametrize("i", [0, 1, 4])
def test_library_arm_is_the_v2_procedure(i):
    _, _, d = v3.world_data(i, null=False)
    assert v3.arm_library(d)["test_r2"] == pytest.approx(v2.run_world(i)["test_r2_abduced"])


def test_ridge_arm_chooses_alpha_on_validation_and_resists_noise():
    _, _, d = v3.world_data(1, null=False)
    real = v3.arm_ridge(d)
    assert real["alpha"] in v3.ALPHAS and real["test_r2"] > 0.5
    _, _, noise = v3.world_data(1, null=True)
    assert v3.arm_ridge(noise)["test_r2"] < 0.1


def synthetic(seed=0, n=240):
    rng = np.random.default_rng(seed)
    X, Z1, Z2 = rng.normal(size=(3, n))
    B = rng.normal(size=(n, 20))
    Y = 2.5 * np.sin(X) + 0.1 * rng.normal(size=n)
    return {
        "X": X,
        "Z1": Z1,
        "Z2": Z2,
        "B": B,
        "Y": Y,
        "disc": slice(0, 60),
        "val": slice(60, 120),
        "test": slice(120, n),
    }


def test_pysr_arm_selects_by_validation_and_refits_constants():
    X = sympy.Symbol("X")
    hall = [(1, sympy.Float(0.1)), (3, sympy.Float(1.0) * X), (4, sympy.Float(2.0) * sympy.sin(X))]
    result = v3.arm_pysr(synthetic(), seed=0, search=lambda *_: hall)
    assert result["complexity"] == 4 and result["constants_refit"]
    assert result["test_r2"] > 0.95 and "sin" in result["equation"]


def test_pysr_arm_survives_equations_that_blow_up():
    X = sympy.Symbol("X")
    hall = [
        (2, sympy.exp(sympy.Float(50.0) * X)),
        (3, sympy.Float(1.0) / (X - X)),
        (4, sympy.Float(2.0) * sympy.sin(X)),
    ]
    result = v3.arm_pysr(synthetic(1), seed=0, search=lambda *_: hall)
    assert "sin" in result["equation"] and np.isfinite(result["test_r2"])


def test_pysr_arm_falls_back_to_the_mean_when_nothing_is_usable():
    X = sympy.Symbol("X")
    result = v3.arm_pysr(synthetic(), seed=0, search=lambda *_: [(3, sympy.Float(1.0) / (X - X))])
    assert result["no_usable_equation"] and result["test_r2"] < 0.05


def rows(arm, null, r2_of):
    sha = v3.protocol_sha()
    return [
        {"protocol_sha256": sha, "arm": arm, "null": null, "world_index": i, "archetype": "A", "test_r2": r2_of(i)}
        for i in range(v2.N_WORLDS)
    ]


def test_score_applies_gate_and_criteria():
    data = (
        rows("L", False, lambda i: 0.8)
        + rows("R", False, lambda i: 0.6 + 0.001 * i)
        + rows("L", True, lambda i: -0.02)
        + rows("R", True, lambda i: 0.2)  # a baseline that "finds" signal in noise fails the gate
    )
    result = v3.score(data)
    assert result["arms"]["L"]["null_gate_passed"] and not result["arms"]["R"]["null_gate_passed"]
    c1 = result["criteria"]["C1"]
    assert c1["met"] and not c1["baseline_better"] and not c1["interpretable"]
    assert result["criteria"]["C2"] == {"status": "not run"}
    assert result["arms"]["P"]["real"]["status"] == "not run"


def test_score_refuses_results_from_another_protocol():
    data = rows("L", False, lambda i: 0.5)
    data[0]["protocol_sha256"] = "0" * 64
    with pytest.raises(SystemExit):
        v3.score(data)
