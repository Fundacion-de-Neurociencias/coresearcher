"""Unknown-mechanism benchmark v3: library selection against tuned ridge and PySR, with a pre-registered null gate.

Protocol: docs/reference/benchmarks/UNKNOWN_MECHANISM_V3_PROTOCOL.md

    python scripts/benchmarks/run_unknown_mechanism_v3.py run --arm L            # library selection (numpy)
    python scripts/benchmarks/run_unknown_mechanism_v3.py run --arm R --null     # tuned ridge, null control
    python scripts/benchmarks/run_unknown_mechanism_v3.py run --arm P            # PySR (needs Julia; Legion)
    python scripts/benchmarks/run_unknown_mechanism_v3.py score

`run` appends one JSON line per world to unknown_mechanism_v3_raw.jsonl and skips worlds already recorded under the
same protocol hash, so it can be interrupted and resumed. `score` writes unknown_mechanism_v3_results.json.
"""

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_unknown_mechanism_v2 as v2  # noqa: E402

BENCH = ROOT / "docs" / "reference" / "benchmarks"
PROTOCOL = BENCH / "UNKNOWN_MECHANISM_V3_PROTOCOL.md"
RAW = BENCH / "unknown_mechanism_v3_raw.jsonl"
RESULTS = BENCH / "unknown_mechanism_v3_results.json"
ALPHAS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0]
BOOT_SEED = 20261017
NULL_GATE = 0.05
PYSR_CONFIG = dict(
    niterations=40,
    populations=15,
    population_size=33,
    maxsize=20,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["sin", "cos", "exp", "square"],
    deterministic=True,
    parallelism="serial",
)
INPUT_NAMES = ["X", "Z_1", "Z_2"] + [f"B_{k}" for k in range(1, 21)]


def protocol_sha() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def world_data(i: int, null: bool):
    archetype = v2.ARCHETYPES[i % len(v2.ARCHETYPES)]
    world = v2.BlindWorldGenerator.generate_world(i, archetype, n=v2.N_ROWS)
    d = v2.build_splits(world)
    if null:
        d["Y"] = np.random.default_rng(7000 + i).permutation(d["Y"])
    return archetype, world, d


# --------------------------------------------------------------------------- arms


def arm_library(d) -> dict:
    """v2 sections 3-4, unchanged."""
    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    designs = v2.candidate_designs(d)
    scores = {
        name: (v2.r2(Y[val], v2.fit_predict(M[disc], Y[disc], M[val])), M.shape[1]) for name, (_, M) in designs.items()
    }
    selected = max(scores, key=lambda k: (round(scores[k][0], 12), -scores[k][1]))
    fit = np.arange(disc.start, val.stop)
    M = designs[selected][1]
    return {"test_r2": v2.r2(Y[test], v2.fit_predict(M[fit], Y[fit], M[test])), "selected": selected}


def _ridge(design_train, y_train, design_eval, alpha):
    mean = design_train[:, 1:].mean(axis=0)
    std = design_train[:, 1:].std(axis=0)
    std[std == 0] = 1.0
    A = np.column_stack([np.ones(len(design_train)), (design_train[:, 1:] - mean) / std])
    B = np.column_stack([np.ones(len(design_eval)), (design_eval[:, 1:] - mean) / std])
    penalty = alpha * np.eye(A.shape[1])
    penalty[0, 0] = 0.0  # intercept not penalised
    coef = np.linalg.solve(A.T @ A + penalty, A.T @ y_train)
    return B @ coef


def arm_ridge(d) -> dict:
    """Protocol section 4, arm R. Standardisation uses the rows the model is fitted on."""
    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    M = v2.flexible_design(d)
    scores = {a: v2.r2(Y[val], _ridge(M[disc], Y[disc], M[val], a)) for a in ALPHAS}
    alpha = max(ALPHAS, key=lambda a: (round(scores[a], 12), a))  # ties go to the larger alpha
    fit = np.arange(disc.start, val.stop)
    return {"test_r2": v2.r2(Y[test], _ridge(M[fit], Y[fit], M[test], alpha)), "alpha": alpha}


def _inputs(d):
    return np.column_stack([d["X"], d["Z1"], d["Z2"], d["B"]])


def pysr_search(X_disc, y_disc, seed):
    """Run PySR on the discovery split. Returns its hall of fame as (complexity, sympy expression) pairs."""
    from pysr import PySRRegressor

    model = PySRRegressor(**PYSR_CONFIG, random_state=seed, progress=False, verbosity=0, temp_equation_file=True)
    model.fit(X_disc, y_disc, variable_names=INPUT_NAMES)
    return [(int(row.complexity), row.sympy_format) for row in model.equations_.itertuples()]


def _compile(expr):
    """Split an equation into a callable f(inputs, constants) and its starting constants."""
    import sympy

    symbols = [sympy.Symbol(n) for n in INPUT_NAMES]
    floats = sorted(expr.atoms(sympy.Float), key=lambda f: str(f))
    params = [sympy.Symbol(f"c{k}") for k in range(len(floats))]
    template = expr.xreplace(dict(zip(floats, params)))
    f = sympy.lambdify([symbols, params], template, modules="numpy")

    def predict(X, constants):
        with np.errstate(all="ignore"):
            out = f([X[:, k] for k in range(X.shape[1])], list(constants))
        return np.broadcast_to(np.asarray(out, dtype=float), (X.shape[0],)).copy()

    return predict, np.array([float(v) for v in floats])


def arm_pysr(d, seed, search=pysr_search) -> dict:
    """Protocol section 4, arm P. `search` is injectable so the selection and refit logic can be tested offline."""
    from scipy.optimize import least_squares

    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    X = _inputs(d)
    hall = search(X[disc], Y[disc], seed)
    scored = []
    for complexity, expr in hall:
        try:  # an equation that cannot be compiled or evaluated (e.g. a literal division by zero) is skipped
            predict, c0 = _compile(expr)
            score = v2.r2(Y[val], predict(X[val], c0))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue
        scored.append((score if np.isfinite(score) else -np.inf, -complexity, complexity, expr, predict, c0))
    fit = np.arange(disc.start, val.stop)
    if not scored:  # protocol section 4: no usable equation -> predict the fitting-rows mean, flagged
        test_r2 = v2.r2(Y[test], np.full(test.stop - test.start, Y[fit].mean()))
        return {"test_r2": float(test_r2), "equation": None, "no_usable_equation": True}
    best = max(scored, key=lambda s: (round(s[0], 12), s[1]))
    _, _, complexity, expr, predict, c0 = best
    constants, refit = c0, False
    if len(c0):

        def residuals(c):
            r = predict(X[fit], c) - Y[fit]
            return np.where(np.isfinite(r), r, 1e6)

        try:
            solution = least_squares(residuals, c0)
            if np.sum(residuals(solution.x) ** 2) < np.sum(residuals(c0) ** 2):
                constants, refit = solution.x, True
        except (ValueError, FloatingPointError):
            pass
    test_r2 = v2.r2(Y[test], predict(X[test], constants))
    return {
        "test_r2": float(test_r2) if np.isfinite(test_r2) else float("-inf"),
        "equation": str(expr),
        "complexity": complexity,
        "constants_refit": refit,
        "validation_r2": float(best[0]),
    }


def versions(arm: str) -> dict:
    out = {"python": platform.python_version(), "numpy": np.__version__}
    if arm == "P":
        import pysr

        out["pysr"] = pysr.__version__
    return out


# --------------------------------------------------------------------------- run / score


def load_raw():
    if not RAW.exists():
        return []
    return [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]


def run(arm: str, null: bool, worlds) -> int:
    sha = protocol_sha()
    done = {(r["arm"], r["null"], r["world_index"]) for r in load_raw() if r["protocol_sha256"] == sha}
    info = versions(arm)
    with RAW.open("a", encoding="utf-8") as out:
        for i in worlds:
            if (arm, null, i) in done:
                continue
            archetype, world, d = world_data(i, null)
            result = {"L": arm_library, "R": arm_ridge}[arm](d) if arm in "LR" else arm_pysr(d, 3000 + i)
            record = {
                "protocol_sha256": sha,
                "arm": arm,
                "null": null,
                "world_index": i,
                "world": world.world_id,
                "archetype": archetype.value,
                "versions": info,
                **result,
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            print(f"{arm} {'null' if null else 'real'} world {i}: test R2 {result['test_r2']:.3f}")
    return 0


def _boot(values, rng):
    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(v2.BOOT_RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def score(rows=None) -> dict:
    sha = protocol_sha()
    rows = rows if rows is not None else load_raw()
    stale = {r["protocol_sha256"] for r in rows} - {sha}
    if stale:
        raise SystemExit(f"Raw results were produced under another protocol version: {sorted(stale)}")
    rng = np.random.default_rng(BOOT_SEED)
    table = {}
    for r in rows:
        table.setdefault((r["arm"], r["null"]), {})[r["world_index"]] = r
    complete = {key: len(v) == v2.N_WORLDS for key, v in table.items()}

    arms = {}
    for arm in "LRP":
        entry = {}
        for null in (False, True):
            key = (arm, null)
            label = "null" if null else "real"
            if not complete.get(key):
                entry[label] = {"status": "not run" if key not in table else f"incomplete ({len(table[key])} worlds)"}
                continue
            r2s = [table[key][i]["test_r2"] for i in range(v2.N_WORLDS)]
            by_arch = {}
            for i in range(v2.N_WORLDS):
                by_arch.setdefault(table[key][i]["archetype"], []).append(table[key][i]["test_r2"])
            entry[label] = {
                "mean_test_r2": float(np.mean(r2s)),
                "bootstrap_95": _boot(r2s, rng),
                "by_archetype": {a: float(np.mean(v)) for a, v in sorted(by_arch.items())},
            }
        if "bootstrap_95" in entry.get("null", {}):
            entry["null_gate_passed"] = entry["null"]["bootstrap_95"][1] <= NULL_GATE
        arms[arm] = entry

    comparisons = {}
    for baseline, criterion in (("R", "C1"), ("P", "C2")):
        if not (complete.get(("L", False)) and complete.get((baseline, False))):
            comparisons[criterion] = {"status": "not run"}
            continue
        deltas = [
            table[("L", False)][i]["test_r2"] - table[(baseline, False)][i]["test_r2"] for i in range(v2.N_WORLDS)
        ]
        ci = _boot(deltas, rng)
        gates = [arms[a].get("null_gate_passed") for a in ("L", baseline)]
        comparisons[criterion] = {
            "comparison": f"L - {baseline}",
            "mean_delta_r2": float(np.mean(deltas)),
            "bootstrap_95": ci,
            "met": ci[0] > 0,
            "baseline_better": ci[1] < 0,
            "interpretable": all(g is True for g in gates),
            "null_gates": {"L": gates[0], baseline: gates[1]},
        }
    return {"protocol": str(PROTOCOL.relative_to(ROOT)), "protocol_sha256": sha, "arms": arms, "criteria": comparisons}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=["L", "R", "P"], required=True)
    r.add_argument("--null", action="store_true")
    r.add_argument("--worlds", default=f"0-{v2.N_WORLDS - 1}", help="Range such as 0-99.")
    sub.add_parser("score")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        lo, hi = (int(x) for x in args.worlds.split("-"))
        return run(args.arm, args.null, range(lo, hi + 1))
    result = score()
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["criteria"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
