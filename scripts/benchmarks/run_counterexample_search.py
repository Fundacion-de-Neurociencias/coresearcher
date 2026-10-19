"""Counterexample search benchmark: can a proposer find refuting states that an exact point check confirms?

Protocol: docs/reference/benchmarks/COUNTEREXAMPLE_SEARCH_PROTOCOL.md

    python scripts/benchmarks/run_counterexample_search.py run --arm E            # exact evaluator (control)
    python scripts/benchmarks/run_counterexample_search.py run --arm R            # random search (null)
    python scripts/benchmarks/run_counterexample_search.py run --arm P            # language-model proposer (Legion)
    python scripts/benchmarks/run_counterexample_search.py score

`run` appends one JSON line per item to counterexample_raw.jsonl and skips items already recorded under the same
protocol hash. `score` writes counterexample_results.json.
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery import formal_thresholds  # noqa: E402
from python.discovery.formal_hypothesis import (  # noqa: E402
    FormalHypothesisError,
    Predicate,
    ThresholdExceeded,
    hypothesis_from_dict,
)

BENCH = ROOT / "docs" / "reference" / "benchmarks"
PROTOCOL = BENCH / "COUNTEREXAMPLE_SEARCH_PROTOCOL.md"
RAW = BENCH / "counterexample_raw.jsonl"
RESULTS = BENCH / "counterexample_results.json"
TRUTH = BENCH / "counterexample_truth.json"

N_ITEMS = 200
N_CORRECT = 100
N_VARIABLES = 7
DOMAIN = tuple(range(10))
BUDGET = 50
CALLS = 5
STATES_PER_CALL = 10
GEN_SEED, RANDOM_SEED, PROPOSER_SEED = 51000, 53000, 55000
BOOT_SEED = 20261019
BOOT_RESAMPLES = 10_000
VALIDITY_FALSE_DETECTIONS = 0
PROPOSER_MODEL = "qwen2.5:14b-instruct-q4_K_M"
PROPOSER_TEMPERATURE = 0.7
ARMS = "ERP"


def protocol_sha() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def variable_names():
    return [f"v{k}" for k in range(N_VARIABLES)]


# --------------------------------------------------------------------------- corpus


def make_item(i: int) -> dict:
    """One item. Correct items have only implied claims; planted items add one claim that is violated."""
    rng = random.Random(GEN_SEED + i)
    lo = rng.randint(0, 4)
    hi = rng.randint(lo + 3, 9)
    assumption = f"v0 >= {lo} and v0 <= {hi}"
    claims = [f"v0 >= {lo} and v0 <= {hi}", "v1 >= 0"]
    planted = i >= N_CORRECT
    pattern = None
    if planted:
        a = rng.randint(lo, hi)
        j = rng.randint(1, N_VARIABLES - 1)
        b = rng.randint(0, 9)
        pattern = {"v0": a, f"v{j}": b}
        claims.append(f"not (v0 == {a} and v{j} == {b})")
    return {
        "index": i,
        "planted": planted,
        "variables": [{"name": n, "domain": list(DOMAIN)} for n in variable_names()],
        "assumptions": [assumption],
        "claims": claims,
        "pattern": pattern,
    }


def corpus():
    return [make_item(i) for i in range(N_ITEMS)]


def item_prompt(item: dict, k: int) -> str:
    domain = ", ".join(str(v) for v in DOMAIN)
    lines = [
        "A hypothesis constrains a finite set of variables. Every variable takes a value in {" + domain + "}.",
        "States are assignments of all variables. A state is relevant when it satisfies the assumptions.",
        "The hypothesis claims that every relevant state satisfies every claim.",
        "",
        "Variables: " + ", ".join(v["name"] for v in item["variables"]),
        "Assumptions: " + " ; ".join(item["assumptions"]),
        "Claims: " + " ; ".join(item["claims"]),
        "",
        f"Propose up to {STATES_PER_CALL} candidate states that might break a claim. Answer only with one JSON object per "
        "line, assigning every variable a value from the domain, for example "
        + json.dumps({n: 0 for n in variable_names()})
        + f". This is attempt {k + 1} of {CALLS}; give different states from earlier attempts.",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- point check


def _predicates(item: dict):
    names = variable_names()
    return [Predicate(a, names) for a in item["assumptions"]], [Predicate(c, names) for c in item["claims"]]


def check_state(item: dict, state, predicates=None) -> tuple:
    """Exact check of one state. Returns (status, violated claims). status is CONFIRMED, NOT_RELEVANT, NOT_A_STATE
    or HOLDS. Only CONFIRMED counts as a counterexample."""
    names = variable_names()
    if not isinstance(state, dict) or set(state) != set(names):
        return "NOT_A_STATE", []
    if any(not isinstance(state[n], int) or isinstance(state[n], bool) or state[n] not in DOMAIN for n in names):
        return "NOT_A_STATE", []
    assumptions, claims = predicates or _predicates(item)
    if not all(a.evaluate(state) for a in assumptions):
        return "NOT_RELEVANT", []
    violated = [c.expression for c in claims if not c.evaluate(state)]
    return ("CONFIRMED", violated) if violated else ("HOLDS", [])


def parse_states(text: str) -> list:
    """One candidate state per line, read as JSON. Anything else is dropped and counted by the caller."""
    states, dropped = [], 0
    for line in text.splitlines():
        line = line.strip().rstrip(",")
        if not line.startswith("{"):
            continue
        try:
            states.append(json.loads(line))
        except json.JSONDecodeError:
            dropped += 1
    return states, dropped


# --------------------------------------------------------------------------- arms


def exact_arm(item: dict) -> dict:
    """The exact evaluator as it stands: it builds the hypothesis and enumerates every state."""
    spec = {"hypothesis_id": f"CE-{item['index']}", "variables": item["variables"], "assumptions": item["assumptions"],
            "claims": item["claims"]}  # fmt: skip
    try:
        hypothesis_from_dict(spec)
        status = "DECIDED"
    except ThresholdExceeded:
        status = "BLOCKED"
    except FormalHypothesisError:
        status = "INVALID"
    return {"status": status, "budget_used": 0, "candidates": 0, "confirmed": 0, "detected": False}


def random_arm(item: dict, seed: int) -> dict:
    rng = random.Random(seed)
    predicates = _predicates(item)
    candidates = [{n: rng.choice(DOMAIN) for n in variable_names()} for _ in range(BUDGET)]
    return score_candidates(item, candidates, predicates, budget_used=BUDGET)


def proposer_arm(item: dict, propose) -> dict:
    """`propose(prompt, seed)` returns the model's text. Injectable so tests need no model."""
    predicates = _predicates(item)
    candidates, dropped = [], 0
    for k in range(CALLS):
        states, bad = parse_states(propose(item_prompt(item, k), PROPOSER_SEED + 10 * item["index"] + k))
        dropped += bad
        candidates.extend(states[:STATES_PER_CALL])
    candidates = candidates[:BUDGET]
    result = score_candidates(item, candidates, predicates, budget_used=len(candidates))
    result["unparsed_lines"] = dropped
    return result


def score_candidates(item, candidates, predicates, budget_used: int) -> dict:
    counts = {"CONFIRMED": 0, "HOLDS": 0, "NOT_RELEVANT": 0, "NOT_A_STATE": 0}
    first = None
    for state in candidates:
        status, violated = check_state(item, state, predicates)
        counts[status] += 1
        if status == "CONFIRMED" and first is None:
            first = {"state": state, "violated": violated}
    return {
        "status": "DECIDED_BY_SEARCH",
        "budget_used": budget_used,
        "candidates": len(candidates),
        "confirmed": counts["CONFIRMED"],
        "detected": first is not None,
        "outcomes": counts,
        "first_counterexample": first,
    }


def run_arm(arm: str, item: dict, propose=None) -> dict:
    if arm == "E":
        return exact_arm(item)
    if arm == "R":
        return random_arm(item, RANDOM_SEED + item["index"])
    if propose is None:
        from python.discovery.formalizer import ChatClient

        client = ChatClient(model=PROPOSER_MODEL)

        def propose(prompt, seed):
            return client.complete([{"role": "user", "content": prompt}], temperature=PROPOSER_TEMPERATURE, seed=seed)

    return proposer_arm(item, propose)


# --------------------------------------------------------------------------- run / score


def load_raw():
    if not RAW.exists():
        return []
    return [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()]


def versions(arm: str) -> dict:
    out = {"python": sys.version.split()[0], "threshold_max_states": formal_thresholds.get("max_states")}
    if arm == "P":
        out["model"] = PROPOSER_MODEL
        out["temperature"] = PROPOSER_TEMPERATURE
    return out


def run(arm: str, worlds, propose=None) -> int:
    sha = protocol_sha()
    done = {r["item_index"] for r in load_raw() if r["arm"] == arm and r["protocol_sha256"] == sha}
    items = corpus()
    info = versions(arm)
    with RAW.open("a", encoding="utf-8") as out:
        for i in worlds:
            if i in done:
                continue
            item = items[i]
            result = run_arm(arm, item, propose)
            record = {
                "protocol_sha256": sha,
                "arm": arm,
                "item_index": i,
                "planted": item["planted"],
                "versions": info,
                **result,
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            print(f"{arm} item {i} ({'planted' if item['planted'] else 'correct'}): detected {result['detected']}")
    return 0


def write_truth() -> None:
    TRUTH.write_text(
        json.dumps(
            {
                "seed": GEN_SEED,
                "items": [{"index": x["index"], "planted": x["planted"], "pattern": x["pattern"]} for x in corpus()],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _boot(values, rng):
    import numpy as np

    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(BOOT_RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def _wilson(successes: int, trials: int):
    import math

    if trials == 0:
        return [float("nan"), float("nan")]
    z = 1.959963984540054
    p = successes / trials
    centre = (p + z * z / (2 * trials)) / (1 + z * z / trials)
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / (1 + z * z / trials)
    return [centre - half, centre + half]


def score(rows=None) -> dict:
    import numpy as np

    sha = protocol_sha()
    rows = rows if rows is not None else load_raw()
    stale = {r["protocol_sha256"] for r in rows} - {sha}
    if stale:
        raise SystemExit(f"Raw results were produced under another protocol version: {sorted(stale)}")
    table = {}
    for r in rows:
        table.setdefault(r["arm"], {})[r["item_index"]] = r
    complete = {arm: len(table.get(arm, {})) == N_ITEMS for arm in ARMS}

    arms = {}
    for arm in ARMS:
        if not complete[arm]:
            arms[arm] = {"status": "not run" if arm not in table else f"incomplete ({len(table[arm])} items)"}
            continue
        recs = [table[arm][i] for i in range(N_ITEMS)]
        planted = [r for r in recs if r["planted"]]
        correct = [r for r in recs if not r["planted"]]
        hits = sum(r["detected"] for r in planted)
        arms[arm] = {
            "detection_planted": hits / len(planted),
            "detection_planted_wilson_95": _wilson(hits, len(planted)),
            "false_detection_correct": sum(r["detected"] for r in correct) / len(correct),
            "false_detections_correct": int(sum(r["detected"] for r in correct)),
            "proposals": int(sum(r["candidates"] for r in recs)),
            "confirmed": int(sum(r["confirmed"] for r in recs)),
            "confirmation_rate": (sum(r["confirmed"] for r in recs) / max(1, sum(r["candidates"] for r in recs))),
        }

    rng = np.random.default_rng(BOOT_SEED)
    detected = {
        arm: np.array([table[arm][i]["detected"] for i in range(N_ITEMS) if table[arm][i]["planted"]], float)
        for arm in ARMS
        if complete[arm]
    }
    criteria = {}
    if complete["R"] and complete["P"]:
        diff = detected["P"] - detected["R"]
        criteria["A"] = {"comparison": "P - R", "mean": float(diff.mean()), "bootstrap_95": _boot(diff, rng)}
    if complete["E"] and complete["P"]:
        diff = detected["P"] - detected["E"]
        criteria["S"] = {"comparison": "P - E", "mean": float(diff.mean()), "bootstrap_95": _boot(diff, rng)}
    validity = (
        {"status": "not run"}
        if not complete["P"] and not complete["R"]
        else {
            "false_detections_correct": {arm: arms[arm]["false_detections_correct"] for arm in ARMS if complete[arm]},
            "met": all(
                arms[arm]["false_detections_correct"] == VALIDITY_FALSE_DETECTIONS for arm in ARMS if complete[arm]
            ),
        }
    )
    if criteria.get("A"):
        criteria["A"]["met"] = criteria["A"]["bootstrap_95"][0] > 0
    if criteria.get("S"):
        criteria["S"]["met"] = criteria["S"]["bootstrap_95"][0] > 0
    return {"protocol_sha256": sha, "validity": validity, "arms": arms, "criteria": criteria}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=list(ARMS), required=True)
    r.add_argument("--worlds", default=f"0-{N_ITEMS - 1}", help="Range such as 0-199.")
    sub.add_parser("corpus", help="Write the planted-pattern truth file (read by scoring only).")
    sub.add_parser("score")
    args = parser.parse_args(argv)
    if args.cmd == "corpus":
        write_truth()
        print(f"Wrote {TRUTH.relative_to(ROOT)}")
        return 0
    if args.cmd == "run":
        lo, hi = (int(x) for x in args.worlds.split("-"))
        return run(args.arm, range(lo, hi + 1))
    result = score()
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"validity": result["validity"], "criteria": result["criteria"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
