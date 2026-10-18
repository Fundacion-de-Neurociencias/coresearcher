"""Unknown-mechanism benchmark v4: worlds, recovery, arms (with stub searchers) and scoring.

Every test uses world indices 1000 and above, which are not part of the benchmark (protocol section 2).
"""

import sys
from pathlib import Path

import numpy as np
import pytest
import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_unknown_mechanism_v4 as v4  # noqa: E402

TEST_WORLDS = range(1000, 1008)  # two of each archetype


def test_worlds_are_deterministic_and_split_by_range():
    a1, p1, d1 = v4.world_data(1000, null=False)
    a2, p2, d2 = v4.world_data(1000, null=False)
    assert a1 == a2 and p1 == p2 and np.array_equal(d1["Y"], d2["Y"])
    seen = d1["X"][: v4.N_DISC + v4.N_VAL]
    test = d1["X"][d1["test"]]
    assert seen.min() >= v4.OBSERVED[0] and seen.max() <= v4.OBSERVED[1]
    assert test.min() >= v4.EXTRAPOLATION[0] and test.max() <= v4.EXTRAPOLATION[1]
    assert [v4.world_data(i, False)[0] for i in range(1000, 1004)] == v4.ARCHETYPES
    _, _, null = v4.world_data(1000, null=True)
    assert sorted(null["Y"]) == pytest.approx(sorted(d1["Y"])) and not np.array_equal(null["Y"], d1["Y"])


@pytest.mark.parametrize("i", TEST_WORLDS)
def test_oracle_recovers_the_law_and_extrapolates(i):
    archetype, params, d = v4.world_data(i, null=False)
    result = v4.arm_oracle(d, archetype, params)
    assert result["test_r2"] > 0.9 and result["recovery_share"] >= v4.RECOVERY_SHARE


def test_recovery_share_rejects_a_near_miss_and_accepts_the_truth():
    archetype, params, _ = v4.world_data(1003, null=False)  # SAWTOOTH
    g = v4.law(archetype, params)
    assert v4.recovery_fraction(g, archetype, params) == 1.0
    flat = lambda X, Z: params["a"] * 0.5 + params["c"] * Z  # noqa: E731 - the sawtooth replaced by its mean
    assert v4.recovery_fraction(flat, archetype, params) < 0.5
    diverging = lambda X, Z: np.full_like(X, np.inf)  # noqa: E731
    assert v4.recovery_fraction(diverging, archetype, params) == 0.0


def test_library_and_ridge_run_and_cannot_express_a_kink():
    archetype, params, d = v4.world_data(1002, null=False)  # ABS_KINK
    for arm in (v4.arm_library, v4.arm_ridge):
        result = arm(d, archetype, params)
        assert np.isfinite(result["test_r2"]) and 0.0 <= result["recovery_share"] <= 1.0


def test_pysr_arm_with_a_stub_search_is_judged_on_the_grid():
    archetype, params, d = v4.world_data(1001, null=False)  # FRACTIONAL_POWER
    X = sympy.Symbol("X")
    hall = [(1, sympy.Float(1.0)), (3, sympy.Float(1.0) * X), (5, sympy.Float(1.0) * X + sympy.Float(0.1) * X**2)]
    result = v4.arm_pysr(d, archetype, params, seed=0, search=lambda *_: hall)
    assert result["equation"] is not None and result["recovery_share"] < v4.RECOVERY_SHARE


def test_formula_parser_keeps_whitelisted_sympy_and_drops_the_rest():
    text = "\n".join(
        [
            "Here are my candidates:",
            "Y = c0*log(1 + c1*X**2) + c2*Z1",
            "1. Y = c0*Abs(X - c1) + c2*Z1",
            "Y = __import__('os').system('ls')",
            "Y = c0*X.__class__",
            "Y = c0*open(X)",
            "Y = c0*X^c1 + c2*Z1",
            "Y = " + "X+" * 120 + "X",
        ]
    )
    X, Z1, c0, c1, c2 = sympy.symbols("X Z1 c0 c1 c2")
    expected = [c0 * sympy.log(1 + c1 * X**2) + c2 * Z1, c0 * sympy.Abs(X - c1) + c2 * Z1, c0 * X**c1 + c2 * Z1]
    assert v4.parse_formulas(text) == expected


def test_llm_arm_recovers_when_the_right_form_is_proposed():
    archetype, params, d = v4.world_data(1000, null=False)  # LOG_SATURATION
    answers = iter(
        ["Y = c0*X + c1*Z1", "Y = c0*log(1 + c1*X**2) + c2*Z1 + c3", "nothing useful", "Y = c0", "Y = c0*X**2"]
    )
    prompts = []

    def propose(prompt, seed):
        prompts.append((prompt, seed))
        return next(answers)

    result = v4.arm_llm(d, archetype, params, 1000, propose=propose)
    assert "log" in result["equation"] and result["recovery_share"] >= v4.RECOVERY_SHARE
    assert [s for _, s in prompts] == [v4.LLM_SEED + 10 * 1000 + k for k in range(v4.LLM_CALLS)]
    prompt = prompts[0][0]
    assert "log" not in prompt and "Abs" not in prompt and "Mod" not in prompt  # no function is suggested
    assert prompt.count("\n") > v4.N_DISC


def test_llm_arm_falls_back_to_the_mean_without_usable_formulas():
    archetype, params, d = v4.world_data(1000, null=False)
    result = v4.arm_llm(d, archetype, params, 1000, propose=lambda *_: "I cannot help with that.")
    assert result["equation"] is None and result["recovery_share"] == 0.0


def rows(arm, null, r2, share):
    sha = v4.protocol_sha()
    return [
        {
            "protocol_sha256": sha,
            "arm": arm,
            "null": null,
            "world_index": i,
            "archetype": v4.ARCHETYPES[i % 4],
            "test_r2": r2(i),
            "recovery_share": share(i),
        }
        for i in range(v4.N_WORLDS)
    ]


def test_score_applies_validity_gate_and_jump_criterion():
    data = (
        rows("O", False, lambda i: 0.98, lambda i: 1.0)
        + rows("O", True, lambda i: -1.0, lambda i: 0.0)
        + rows("L", False, lambda i: 0.2, lambda i: 0.1)
        + rows("L", True, lambda i: -0.5, lambda i: 0.0)
        + rows("E", False, lambda i: 0.6 if i % 4 else float("-inf"), lambda i: 1.0 if i % 10 == 0 else 0.0)
    )
    result = v4.score(data)
    assert result["validity"]["met"]
    assert result["arms"]["O"]["J_met"] and result["arms"]["O"]["null_gate_passed"]
    assert not result["arms"]["L"]["J_met"]
    e = result["arms"]["E"]
    assert e["real"]["recovered"] == 10 and e["J_met"] == (e["real"]["recovery_wilson_95"][0] > v4.J_LOWER_BOUND)
    assert e["real"]["mean_test_r2"] == pytest.approx((75 * 0.6 + 25 * -10) / 100)
    assert result["extrapolation"]["E - L"]["mean_delta_r2"] < 0
    assert result["arms"]["P"]["real"] == {"status": "not run"}


def test_score_refuses_results_from_another_protocol():
    data = rows("L", False, lambda i: 0.5, lambda i: 0.0)
    data[0]["protocol_sha256"] = "0" * 64
    with pytest.raises(SystemExit):
        v4.score(data)
