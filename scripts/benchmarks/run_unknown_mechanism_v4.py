"""Unknown-mechanism benchmark v4: generating laws outside every arm's hypothesis space, tested by extrapolation.

Protocol: docs/reference/benchmarks/UNKNOWN_MECHANISM_V4_PROTOCOL.md

    python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm O            # oracle form (positive control)
    python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm L            # library selection
    python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm R --null     # tuned ridge, null control
    python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm P            # PySR (needs Julia; Legion)
    python scripts/benchmarks/run_unknown_mechanism_v4.py run --arm E            # local LLM proposals (Legion)
    python scripts/benchmarks/run_unknown_mechanism_v4.py score

`run` appends one JSON line per world to unknown_mechanism_v4_raw.jsonl and skips worlds already recorded under the
same protocol hash. `score` writes unknown_mechanism_v4_results.json.
"""

import argparse
import hashlib
import json
import platform
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_unknown_mechanism_v2 as v2  # noqa: E402
import run_unknown_mechanism_v3 as v3  # noqa: E402

BENCH = ROOT / "docs" / "reference" / "benchmarks"
PROTOCOL = BENCH / "UNKNOWN_MECHANISM_V4_PROTOCOL.md"
RAW = BENCH / "unknown_mechanism_v4_raw.jsonl"
RESULTS = BENCH / "unknown_mechanism_v4_results.json"

N_WORLDS = 100
N_DISC, N_VAL, N_TEST = 60, 60, 120
N_BACKGROUND = 20
OBSERVED = (0.5, 3.0)
EXTRAPOLATION = (3.0, 6.0)
GRID = (0.5, 6.0)  # recovery is judged over the observed and the extrapolation range
NOISE_FRACTION = 0.05
WORLD_SEED, NULL_SEED, PYSR_SEED, LLM_SEED = 41000, 47000, 43000, 45000
BOOT_SEED = 20261018
NULL_GATE = 0.05
RECOVERY_TOLERANCE = 0.1  # in standard deviations of the law on the grid
RECOVERY_SHARE = 0.95
J_LOWER_BOUND = 0.05
VALIDITY_R2, VALIDITY_RECOVERY = 0.9, 0.9
ARCHETYPES = ["LOG_SATURATION", "FRACTIONAL_POWER", "ABS_KINK", "SAWTOOTH"]
ARMS = "OLRPE"

# Arm E (protocol section 4)
LLM_MODEL = "qwen2.5:14b-instruct-q4_K_M"
LLM_TEMPERATURE = 0.7
LLM_CALLS = 5
LLM_FORMULAS_PER_CALL = 4
MAX_FORMULA_CHARS = 200
MAX_CONSTANTS = 6
STARTS = (1.0, 0.5, 2.0)


def protocol_sha() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- worlds


def law(archetype: str, params: dict):
    """The noiseless generating law g(X, Z1) of an archetype, vectorised."""
    a, c = params["a"], params["c"]
    if archetype == "LOG_SATURATION":
        return lambda X, Z1: a * np.log1p(params["b"] * X**2) + c * Z1
    if archetype == "FRACTIONAL_POWER":
        return lambda X, Z1: a * np.power(np.abs(X), params["p"]) + c * Z1
    if archetype == "ABS_KINK":
        return lambda X, Z1: a * np.abs(X - params["t"]) + c * Z1
    if archetype == "SAWTOOTH":
        return lambda X, Z1: a * np.mod(X / params["period"], 1.0) + c * Z1
    raise ValueError(archetype)


def world_params(i: int) -> tuple:
    rng = np.random.default_rng(WORLD_SEED + i)
    archetype = ARCHETYPES[i % len(ARCHETYPES)]
    params = {"a": float(rng.uniform(1.0, 3.0)), "c": float(rng.uniform(0.5, 1.5))}
    if archetype == "LOG_SATURATION":
        params["b"] = float(rng.uniform(0.5, 2.0))
    elif archetype == "FRACTIONAL_POWER":
        params["p"] = float(rng.uniform(0.3, 0.7))
    elif archetype == "ABS_KINK":
        params["t"] = float(rng.uniform(1.0, 2.5))
    else:
        params["period"] = float(rng.uniform(0.6, 1.2))
    return archetype, params, rng


def world_data(i: int, null: bool):
    """Discovery and validation rows from the observed range of X; test rows from the extrapolation range."""
    archetype, params, rng = world_params(i)
    n_seen = N_DISC + N_VAL
    X = np.concatenate([rng.uniform(*OBSERVED, size=n_seen), rng.uniform(*EXTRAPOLATION, size=N_TEST)])
    Z1, Z2 = rng.normal(size=(2, len(X)))
    B = rng.normal(size=(len(X), N_BACKGROUND))
    signal = law(archetype, params)(X, Z1)
    noise_sd = NOISE_FRACTION * float(np.std(signal[:n_seen]))
    Y = signal + rng.normal(scale=noise_sd, size=len(X))
    if null:
        Y = np.random.default_rng(NULL_SEED + i).permutation(Y)
    d = {
        "X": X,
        "Z1": Z1,
        "Z2": Z2,
        "B": B,
        "Y": Y,
        "disc": slice(0, N_DISC),
        "val": slice(N_DISC, n_seen),
        "test": slice(n_seen, n_seen + N_TEST),
    }
    return archetype, params, d


def recovery_grid():
    X = np.linspace(*GRID, 400)
    XX, ZZ = np.meshgrid(X, np.array([-1.0, 0.0, 1.0]))
    return XX.ravel(), ZZ.ravel()


def recovery_fraction(predict_grid, archetype: str, params: dict) -> float:
    """Share of recovery-grid points (B = 0, Z2 = 0) where a fitted predictor is within RECOVERY_TOLERANCE standard
    deviations of the noiseless law. A share is used instead of an RMSE because the sawtooth is discontinuous: an
    almost exact period still puts a few grid points on the wrong side of a jump, which would dominate an RMSE.
    """
    Xg, Zg = recovery_grid()
    truth = law(archetype, params)(Xg, Zg)
    with np.errstate(all="ignore"):
        pred = np.asarray(predict_grid(Xg, Zg), dtype=float)
    if pred.shape != truth.shape:
        return 0.0
    close = np.abs(pred - truth) <= RECOVERY_TOLERANCE * np.std(truth)
    return float(np.mean(np.where(np.isfinite(pred), close, False)))


def _grid_rows(d, Xg, Zg):
    """The world's rows followed by grid rows (Z2 = 0, B = 0), so data-dependent features use the real discovery rows."""
    n = len(Xg)
    return {
        **d,
        "X": np.concatenate([d["X"], Xg]),
        "Z1": np.concatenate([d["Z1"], Zg]),
        "Z2": np.concatenate([d["Z2"], np.zeros(n)]),
        "B": np.vstack([d["B"], np.zeros((n, d["B"].shape[1]))]),
    }


# --------------------------------------------------------------------------- fitting helpers


def refit(predict, x_fit, y_fit, n_constants: int, starts=STARTS):
    """Least squares for the constants of a formula from fixed starting points; returns the best, or None."""
    from scipy.optimize import least_squares

    if n_constants == 0:
        return np.zeros(0)
    best, best_cost = None, np.inf
    for s in starts:

        def residuals(cs):
            with np.errstate(all="ignore"):
                r = predict(x_fit, cs) - y_fit
            return np.where(np.isfinite(r), r, 1e6)

        try:
            sol = least_squares(residuals, np.full(n_constants, s), max_nfev=2000)
        except (ValueError, FloatingPointError, OverflowError):
            continue
        cost = float(np.sum(residuals(sol.x) ** 2))
        if cost < best_cost:
            best, best_cost = sol.x, cost
    return best


def _finite_r2(y, yhat) -> float:
    value = v2.r2(y, yhat) if np.all(np.isfinite(yhat)) else float("-inf")
    return float(value) if np.isfinite(value) else float("-inf")


def _three_inputs(d):
    return np.column_stack([d["X"], d["Z1"], d["Z2"]])


# --------------------------------------------------------------------------- arms


ORACLE_FORMS = {
    "LOG_SATURATION": (3, lambda x, k: k[0] * np.log1p(np.abs(k[1]) * x[:, 0] ** 2) + k[2] * x[:, 1]),
    "FRACTIONAL_POWER": (3, lambda x, k: k[0] * np.power(np.abs(x[:, 0]), k[1]) + k[2] * x[:, 1]),
    "ABS_KINK": (3, lambda x, k: k[0] * np.abs(x[:, 0] - k[1]) + k[2] * x[:, 1]),
}


def _sawtooth(x, k):
    return k[0] * np.mod(x[:, 0] / k[1], 1.0) + k[2] * x[:, 1]


def arm_oracle(d, archetype, params) -> dict:
    """Positive control: the true functional form with unknown constants, fitted on discovery and validation rows.
    The sawtooth period is found by a grid over periods (least squares cannot cross the discontinuities), then refit.
    """
    Y, fit, test = d["Y"], np.arange(0, N_DISC + N_VAL), d["test"]
    x = _three_inputs(d)
    if archetype == "SAWTOOTH":

        def fit_period(period):
            M = np.column_stack([np.mod(x[fit, 0] / period, 1.0), x[fit, 1], np.ones(len(fit))])
            coef, *_ = np.linalg.lstsq(M, Y[fit], rcond=None)
            return float(np.sum((M @ coef - Y[fit]) ** 2)), period, coef

        best = min((fit_period(p) for p in np.linspace(0.3, 2.0, 1701)), key=lambda b: b[0])
        best = min((fit_period(p) for p in np.linspace(best[1] - 0.002, best[1] + 0.002, 401)), key=lambda b: b[0])
        _, period, coef = best
        k = [coef[0], period, coef[1]]
        intercept = coef[2]

        def predict(xx, kk=k, b0=intercept):
            return _sawtooth(xx, kk) + b0

    else:
        n, form = ORACLE_FORMS[archetype]
        k = refit(lambda xx, kk: form(xx, kk[:n]) + kk[n], x[fit], Y[fit], n + 1)

        def predict(xx, kk=k, f=form, m=n):
            return f(xx, kk[:m]) + kk[m]

    grid = lambda Xg, Zg: predict(np.column_stack([Xg, Zg, np.zeros_like(Xg)]))  # noqa: E731
    return {
        "test_r2": _finite_r2(Y[test], predict(x[test])),
        "recovery_share": recovery_fraction(grid, archetype, params),
    }


def arm_library(d, archetype, params) -> dict:
    """v2 library selection (v3 arm L), unchanged; the grid prediction reuses the discovery-split features."""
    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    designs = v2.candidate_designs(d)
    scores = {
        name: (v2.r2(Y[val], v2.fit_predict(M[disc], Y[disc], M[val])), M.shape[1]) for name, (_, M) in designs.items()
    }
    selected = max(scores, key=lambda k: (round(scores[k][0], 12), -scores[k][1]))
    fit = np.arange(disc.start, val.stop)
    M = designs[selected][1]
    coef, *_ = np.linalg.lstsq(M[fit], Y[fit], rcond=None)
    n = len(d["X"])

    def grid(Xg, Zg):
        return v2.candidate_designs(_grid_rows(d, Xg, Zg))[selected][1][n:] @ coef

    return {
        "test_r2": _finite_r2(Y[test], M[test] @ coef),
        "selected": selected,
        "recovery_share": recovery_fraction(grid, archetype, params),
    }


def arm_ridge(d, archetype, params) -> dict:
    """v3 arm R, unchanged: validation-tuned ridge on the 13-term cubic design."""
    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    M = v2.flexible_design(d)
    scores = {a: v2.r2(Y[val], v3._ridge(M[disc], Y[disc], M[val], a)) for a in v3.ALPHAS}
    alpha = max(v3.ALPHAS, key=lambda a: (round(scores[a], 12), a))
    fit = np.arange(disc.start, val.stop)
    n = len(d["X"])

    def grid(Xg, Zg):
        return v3._ridge(M[fit], Y[fit], v2.flexible_design(_grid_rows(d, Xg, Zg))[n:], alpha)

    return {
        "test_r2": _finite_r2(Y[test], v3._ridge(M[fit], Y[fit], M[test], alpha)),
        "alpha": alpha,
        "recovery_share": recovery_fraction(grid, archetype, params),
    }


def arm_pysr(d, archetype, params, seed, search=v3.pysr_search) -> dict:
    """v3 arm P with the v3 configuration, selection and refit; the selected equation is also judged on the grid."""
    result = v3.arm_pysr(d, seed, search=search)
    if result.get("equation") is None:
        result["recovery_share"] = 0.0
        return result
    import sympy

    expr = sympy.sympify(result["equation"])
    predict, c0 = v3._compile(expr)
    X = v3._inputs(d)
    fit = np.arange(0, N_DISC + N_VAL)
    constants = c0
    if len(c0):
        better = _refit_from(predict, X[fit], d["Y"][fit], c0)
        constants = better if better is not None else c0

    def grid(Xg, Zg):
        rows = np.column_stack([Xg, Zg, np.zeros_like(Xg), np.zeros((len(Xg), N_BACKGROUND))])
        return predict(rows, constants)

    result["recovery_share"] = recovery_fraction(grid, archetype, params)
    return result


def _refit_from(predict, x_fit, y_fit, c0):
    from scipy.optimize import least_squares

    def residuals(c):
        with np.errstate(all="ignore"):
            r = predict(x_fit, c) - y_fit
        return np.where(np.isfinite(r), r, 1e6)

    try:
        sol = least_squares(residuals, c0)
    except (ValueError, FloatingPointError, OverflowError):
        return None
    return sol.x if np.sum(residuals(sol.x) ** 2) < np.sum(residuals(c0) ** 2) else None


# ---- arm E: local LLM proposals

LLM_SYSTEM = (
    "You are a scientist looking for the law that generates a measured quantity Y. Propose candidate formulas. "
    "Answer only with formulas, one per line, nothing else."
)
LLM_PROMPT = """Rows are measurements of X, Z1, Z2 and Y. Twenty further variables were measured; the largest absolute
correlation between any of them and Y is {max_bg_corr:.2f}.

Propose up to {k} different candidate formulas for Y as a function of X, Z1 and Z2.
Rules:
- Use SymPy syntax. Any elementary SymPy function is allowed.
- Use free constants named c0, c1, c2, c3, c4, c5 instead of numbers; they will be fitted to the data.
- One formula per line, written as: Y = <formula>

X,Z1,Z2,Y
{rows}
"""

_ALLOWED_NAMES = {
    "X", "Z1", "Z2", "c0", "c1", "c2", "c3", "c4", "c5", "log", "exp", "sqrt", "Abs", "sin", "cos", "tan", "tanh",
    "atan", "sinh", "cosh", "floor", "ceiling", "Mod", "Pow", "Min", "Max", "sign", "pi", "E",
}  # fmt: skip


def llm_prompt(d) -> str:
    disc = d["disc"]
    corr = [abs(float(np.corrcoef(d["B"][disc, k], d["Y"][disc])[0, 1])) for k in range(d["B"].shape[1])]
    rows = "\n".join(
        f"{d['X'][i]:.3f},{d['Z1'][i]:.3f},{d['Z2'][i]:.3f},{d['Y'][i]:.3f}" for i in range(disc.start, disc.stop)
    )
    return LLM_PROMPT.format(max_bg_corr=max(corr), k=LLM_FORMULAS_PER_CALL, rows=rows)


def parse_formulas(text: str) -> list:
    """Formulas from a model answer. Anything outside the whitelist of names, or too long, is dropped."""
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations

    # Only the number constructors the parser itself inserts; every name in a formula is on the whitelist.
    constructors = {n: getattr(sympy, n) for n in ("Integer", "Float", "Rational", "Symbol")}
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*\d.)\s]*)?Y\s*=\s*(.+?)\s*$", line)
        if not m:
            continue
        body = m.group(1).strip().strip("`").replace("^", "**")
        if (
            len(body) > MAX_FORMULA_CHARS
            or "__" in body
            or not set(re.findall(r"[A-Za-z_]\w*", body)) <= _ALLOWED_NAMES
        ):
            continue
        local = {n: getattr(sympy, n) for n in _ALLOWED_NAMES if hasattr(sympy, n)}
        local.update({n: sympy.Symbol(n) for n in ("X", "Z1", "Z2", "c0", "c1", "c2", "c3", "c4", "c5")})
        try:
            expr = parse_expr(
                body, local_dict=local, global_dict=constructors, transformations=standard_transformations
            )
        except Exception:  # noqa: BLE001 - any unparsable answer is dropped, as the protocol says
            continue
        if isinstance(expr, sympy.Expr):
            out.append(expr)
    return out


def _compile_formula(expr):
    import sympy

    inputs = [sympy.Symbol(n) for n in ("X", "Z1", "Z2")]
    constants = sorted((s for s in expr.free_symbols if s.name.startswith("c")), key=lambda s: s.name)
    if len(constants) > MAX_CONSTANTS or not expr.free_symbols <= set(inputs) | set(constants):
        raise ValueError("formula uses unknown symbols or too many constants")
    f = sympy.lambdify([inputs, constants], expr, modules="numpy")

    def predict(x, cs):
        with np.errstate(all="ignore"):
            out = f([x[:, 0], x[:, 1], x[:, 2]], list(cs))
        return np.broadcast_to(np.asarray(out, dtype=float), (x.shape[0],)).copy()

    return predict, len(constants)


def llm_propose(prompt: str, seed: int) -> str:
    from python.discovery.formalizer import ChatClient

    client = ChatClient(model=LLM_MODEL)
    return client.complete(
        [{"role": "system", "content": LLM_SYSTEM}, {"role": "user", "content": prompt}],
        temperature=LLM_TEMPERATURE,
        seed=seed,
    )


def arm_llm(d, archetype, params, world_index, propose=llm_propose) -> dict:
    """Protocol section 4, arm E: proposals from a local model, constants fitted on discovery, chosen on validation."""
    Y, disc, val, test = d["Y"], d["disc"], d["val"], d["test"]
    x = _three_inputs(d)
    prompt = llm_prompt(d)
    formulas = []
    for k in range(LLM_CALLS):
        formulas.extend(parse_formulas(propose(prompt, LLM_SEED + 10 * world_index + k)))
    scored = []
    for expr in dict.fromkeys(formulas):  # duplicates are scored once
        try:
            predict, n = _compile_formula(expr)
            cs = refit(predict, x[disc], Y[disc], n)
            if cs is None:
                continue
            score = _finite_r2(Y[val], predict(x[val], cs))
        except (ValueError, TypeError, KeyError, ZeroDivisionError, AttributeError):
            continue
        scored.append((score, -len(str(expr)), expr, predict, n))
    fit = np.arange(disc.start, val.stop)
    if not scored:
        return {
            "test_r2": _finite_r2(Y[test], np.full(N_TEST, Y[fit].mean())),
            "equation": None,
            "n_formulas": 0,
            "recovery_share": 0.0,
        }
    score, _, expr, predict, n = max(scored, key=lambda s: (round(s[0], 12), s[1]))
    cs = refit(predict, x[fit], Y[fit], n)
    grid = lambda Xg, Zg: predict(np.column_stack([Xg, Zg, np.zeros_like(Xg)]), cs)  # noqa: E731
    return {
        "test_r2": _finite_r2(Y[test], predict(x[test], cs)),
        "equation": str(expr),
        "validation_r2": float(score),
        "n_formulas": len(scored),
        "recovery_share": recovery_fraction(grid, archetype, params),
    }


def run_arm(arm: str, i: int, null: bool) -> dict:
    archetype, params, d = world_data(i, null)
    if arm == "O":
        result = arm_oracle(d, archetype, params)
    elif arm == "L":
        result = arm_library(d, archetype, params)
    elif arm == "R":
        result = arm_ridge(d, archetype, params)
    elif arm == "P":
        result = arm_pysr(d, archetype, params, PYSR_SEED + i)
    else:
        result = arm_llm(d, archetype, params, i)
    return {"archetype": archetype, "params": params, **result}


# --------------------------------------------------------------------------- run / score


def versions(arm: str) -> dict:
    out = {"python": platform.python_version(), "numpy": np.__version__}
    if arm == "P":
        import pysr

        out["pysr"] = pysr.__version__
    if arm == "E":
        out["model"] = LLM_MODEL
    return out


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
            result = run_arm(arm, i, null)
            record = {"protocol_sha256": sha, "arm": arm, "null": null, "world_index": i, "versions": info, **result}
            out.write(json.dumps(record) + "\n")
            out.flush()
            print(f"{arm} {'null' if null else 'real'} world {i}: test R2 {result['test_r2']:.3f}")
    return 0


def wilson(successes: int, trials: int):
    return list(v2.wilson(successes, trials))


def _boot(values, rng):
    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(v2.BOOT_RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def _clip(r2: float) -> float:
    """Test R2 can be minus infinity for a diverging extrapolation; means use a floor of -10 (protocol section 5)."""
    return max(float(r2), -10.0)


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
    complete = {key: len(v) == N_WORLDS for key, v in table.items()}

    arms = {}
    for arm in ARMS:
        entry = {}
        for null in (False, True):
            key, label = (arm, null), ("null" if null else "real")
            if not complete.get(key):
                entry[label] = {"status": "not run" if key not in table else f"incomplete ({len(table[key])} worlds)"}
                continue
            recs = [table[key][i] for i in range(N_WORLDS)]
            r2s = [_clip(r["test_r2"]) for r in recs]
            recovered = [r["recovery_share"] >= RECOVERY_SHARE for r in recs]
            by_arch = {}
            for r, ok in zip(recs, recovered):
                a = by_arch.setdefault(r["archetype"], {"r2": [], "recovered": 0, "worlds": 0})
                a["r2"].append(_clip(r["test_r2"]))
                a["recovered"] += int(ok)
                a["worlds"] += 1
            entry[label] = {
                "mean_test_r2": float(np.mean(r2s)),
                "bootstrap_95": _boot(r2s, rng),
                "recovered": int(sum(recovered)),
                "recovery_wilson_95": wilson(int(sum(recovered)), N_WORLDS),
                "by_archetype": {
                    a: {"mean_test_r2": float(np.mean(v["r2"])), "recovered": v["recovered"], "worlds": v["worlds"]}
                    for a, v in sorted(by_arch.items())
                },
            }
        if "bootstrap_95" in entry.get("null", {}):
            entry["null_gate_passed"] = entry["null"]["bootstrap_95"][1] <= NULL_GATE
        if "recovery_wilson_95" in entry.get("real", {}):
            entry["J_met"] = entry["real"]["recovery_wilson_95"][0] > J_LOWER_BOUND
        arms[arm] = entry

    oracle = arms["O"].get("real", {})
    validity = (
        {"status": "not run"}
        if "mean_test_r2" not in oracle
        else {
            "oracle_mean_test_r2": oracle["mean_test_r2"],
            "oracle_recovered": oracle["recovered"],
            "met": oracle["mean_test_r2"] >= VALIDITY_R2 and oracle["recovered"] >= VALIDITY_RECOVERY * N_WORLDS,
        }
    )
    extrapolation = {}
    for arm in "RPE":
        if not (complete.get(("L", False)) and complete.get((arm, False))):
            extrapolation[f"{arm} - L"] = {"status": "not run"}
            continue
        deltas = [
            _clip(table[(arm, False)][i]["test_r2"]) - _clip(table[("L", False)][i]["test_r2"]) for i in range(N_WORLDS)
        ]
        ci = _boot(deltas, rng)
        extrapolation[f"{arm} - L"] = {"mean_delta_r2": float(np.mean(deltas)), "bootstrap_95": ci}
    return {
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha,
        "validity": validity,
        "arms": arms,
        "extrapolation": extrapolation,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=list(ARMS), required=True)
    r.add_argument("--null", action="store_true")
    r.add_argument("--worlds", default=f"0-{N_WORLDS - 1}", help="Range such as 0-99.")
    sub.add_parser("score")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        lo, hi = (int(x) for x in args.worlds.split("-"))
        return run(args.arm, args.null, range(lo, hi + 1))
    result = score()
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"validity": result["validity"], "extrapolation": result["extrapolation"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
