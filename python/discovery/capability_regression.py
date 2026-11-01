"""
python/discovery/capability_regression.py - Every benchmark is a regression test (ADR-DISCOVERY-084).

Method M9 of docs/architecture/VERIFICATION_METHODOLOGY.md: measure on real errors. Each case below re-runs one of
the October 2026 benchmarks or calibrations offline, from vendored fixtures, and returns its observations: flat
key -> value pairs such as the verdict on one real defect or a false-alarm count. The expected observations are
frozen in benchmarks/regression/expectations.json, whose SHA-256 is pinned in expectations.sha256.

`check()` compares a fresh run with the frozen expectations. Any difference fails, in either direction:

- REGRESSION: an observation got worse (a HIT became NOT_ENCODABLE, a false-alarm count rose, a calibrated answer
  changed);
- IMPROVEMENT: it got better, but the expectation was not updated in the same change, so the gain is not on record;
- CHANGED: it changed with no order between the values (MISS against NOT_ENCODABLE, a new or missing observation);
- FIXTURE_CHANGED: a fixture's bytes differ from the hash recorded with the expectation;
- ERROR: the case could not run. A non-answer is never a pass (M8).

`update()` writes the fresh observations as the new expectations, with a reason, a version bump and a history entry,
so that a deliberate change is a reviewed diff of expectations.json. docs/reference/REGRESSION_BENCHMARKS.md explains
the procedure.
"""

from __future__ import annotations

import copy
import datetime as _dt
import gzip
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent.parent
REGRESSION_DIR = ROOT / "benchmarks" / "regression"
FIXTURES = REGRESSION_DIR / "fixtures"
EXPECTATIONS = REGRESSION_DIR / "expectations.json"
EXPECTATIONS_SHA = REGRESSION_DIR / "expectations.sha256"
SCHEMA = "coresearcher.capability_regression/v1"

PASS = "PASS"
REGRESSION = "REGRESSION"
IMPROVEMENT = "IMPROVEMENT"
CHANGED = "CHANGED"
FIXTURE_CHANGED = "FIXTURE_CHANGED"
ERROR = "ERROR"

# How an observation is ordered. "exact": a calibrated answer, any change is a regression. "higher" and "lower": the
# better direction of a count. "verdict": HIT is better than MISS and NOT_ENCODABLE, which are not ordered.
EXACT, HIGHER, LOWER, VERDICT = "exact", "higher", "lower", "verdict"
_VERDICT_RANK = {"HIT": 1, "MISS": 0, "NOT_ENCODABLE": 0}


class ExpectationsError(ValueError):
    """The expectations file is missing, malformed, or does not match its pinned hash."""


def obs(value: Any, better: str = EXACT) -> Dict[str, Any]:
    return {"value": value, "better": better}


@dataclass
class Case:
    id: str
    title: str
    adr: str
    fixtures: List[str]  # paths relative to the repository root
    run: Callable[[], Dict[str, Dict[str, Any]]]
    notes: str = ""


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def canonical_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def file_sha256(path: Path) -> str:
    """SHA-256 of a fixture. Text is hashed with LF line ends, so a Windows checkout gives the same digest."""
    data = path.read_bytes()
    if path.suffix != ".gz":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _read_json(rel: str) -> Any:
    path = ROOT / rel
    if path.suffix == ".gz":
        return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

TT_DATASET = "docs/reference/benchmarks/openai_math_revision_dataset.json"
TT_FIXTURE = "benchmarks/regression/fixtures/openai_math_time_travel.json.gz"
TT_CHAIN = [
    "docs/reference/benchmarks/openai_math_chain_selection.json",
    "docs/reference/benchmarks/openai_math_chain_registry.json",
    "docs/reference/benchmarks/openai_math_chain_contexts.json",
    "benchmarks/regression/fixtures/openai_math_chain.json.gz",
]
TT_TYPED = [  # The typed re-measure (OPENAI_MATH_TYPED_PROTOCOL.md, ADR-087): same selection and fixture.
    "docs/reference/benchmarks/openai_math_typed_registry.json",
    "docs/reference/benchmarks/openai_math_typed_contexts.json",
]


def _time_travel() -> Dict[str, Dict[str, Any]]:
    from python.discovery import openai_math_time_travel as tt

    dataset = _read_json(TT_DATASET)
    fixture = _read_json(TT_FIXTURE)
    result = tt.replay(dataset["items"], fixture)
    out: Dict[str, Dict[str, Any]] = {}
    for rec in result["items"]:
        if "score" not in rec:
            continue
        out[f"defect/{rec['id']}"] = obs(rec["score"]["verdict"], VERDICT)
        for check in tt.CHECKS[2:]:
            out[f"defect/{rec['id']}/{check}"] = obs(rec["score"]["per_check"][check]["verdict"], VERDICT)
    for check in tt.CHECKS[2:]:
        out[f"hits/{check}"] = obs(result["summary"]["defects"][f"hits_{check}"], HIGHER)
    for group, rate in result["summary"]["false_alarms"].items():
        for check in tt.CHECKS[2:]:
            out[f"false_alarms/{group}/flags/{check}"] = obs(rate["flags"][check], LOWER)
            out[f"false_alarms/{group}/manuscripts_with_flag/{check}"] = obs(rate["manuscripts_with_flag"][check], LOWER)
    # ADR-077 import obligations at each defect location (the obligations the ADR-082 manuscript audit reports).
    items = {i["id"]: i for i in dataset["items"]}
    for item_id, entry in sorted(fixture["items"].items()):
        item = items[item_id]
        if item["group"] not in ("revised", "withdrawn"):
            continue
        found = tt.imports_at(tt.excerpt_files(entry["pre"]), item["locations"])
        for kind in ("CONVENTION_TRANSFER", "HYPOTHESIS_MATCH", "EFFECTIVE_CONSTANT"):
            out[f"imports_at_location/{item_id}/{kind}"] = obs(sum(f[0] == kind for f in found), HIGHER)
    # The re-run with the full chain (OPENAI_MATH_CHAIN_PROTOCOL.md): the manuscript audit with the blind registry
    # entries, and the 8-step chain on every blindly encoded citing context.
    from python.discovery import openai_math_chain as omc

    chain = omc.replay(*[_read_json(f) for f in TT_CHAIN[:3]], _read_json(TT_CHAIN[3]), items, omc.ENCODABLE)
    for item_id, rec in sorted(chain["defects"].items()):
        out[f"chain/defect/{item_id}"] = obs(rec["verdict"], VERDICT)
        for check in omc.CHAIN_CHECKS:
            out[f"chain/defect/{item_id}/{check}"] = obs(rec["per_check"][check]["verdict"], VERDICT)
    for check, buckets in sorted(chain["alarm_load"].items()):
        for bucket, row in sorted(buckets.items()):
            out[f"chain/alarms/{bucket}/flags/{check}"] = obs(row["flags"], LOWER)
    typed = omc.replay(_read_json(TT_CHAIN[0]), *[_read_json(f) for f in TT_TYPED], _read_json(TT_CHAIN[3]), items,
                       omc.ENCODABLE)
    for item_id, rec in sorted(typed["defects"].items()):
        out[f"typed/defect/{item_id}/CHAIN_SEAMS"] = obs(rec["per_check"]["CHAIN_SEAMS"]["verdict"], VERDICT)
    for bucket, row in sorted(typed["alarm_load"]["CHAIN_SEAMS"].items()):
        out[f"typed/alarms/{bucket}/flags/CHAIN_SEAMS"] = obs(row["flags"], LOWER)
    mismatches = [o for o in typed["occurrences"]
                  if any(f.startswith("convention") for f in (o.get("chain") or {}).get("findings", []))]
    out["typed/convention_mismatches/at_location"] = obs(sum(o["at_location"] for o in mismatches), HIGHER)
    out["typed/convention_mismatches/elsewhere"] = obs(sum(not o["at_location"] for o in mismatches), LOWER)
    return out


def _coverage_calibration() -> Dict[str, Dict[str, Any]]:
    from python.discovery import openai_math_coverage as cov
    from python.discovery import statement_fidelity as sf

    out: Dict[str, Dict[str, Any]] = {}
    for claim_id, spec in sorted(cov.hand_specs().items()):
        if claim_id.split(".")[0] not in ("079", "215"):
            continue
        out[f"hand_spec/{claim_id}/relation"] = obs(sf.compare_ranges(spec["spec"]).relation.value)
        out[f"hand_spec/{claim_id}/decides"] = obs(spec["decides"])
    for row in cov.paper_item_calibration():
        out[f"paper_item/{row['item']}/strength"] = obs(row["strength"])
        out[f"paper_item/{row['item']}/has_paper_only_witness"] = obs(row["paper_only_witness"] is not None)
    claims = {c["claim_id"]: c["text"] for c in _read_json("examples/openai-math-coverage/coverage_map.json")["claims"]}
    sources = {
        "079": ("examples/local-smoothing-fidelity/LocalSmoothing.lean", "examples/local-smoothing-fidelity/LocalSmoothing.json"),
        "215": ("examples/o3-continuum-rehearsal/ClassicalON.lean", "examples/o3-continuum-rehearsal/ClassicalON.json"),
    }
    for family, (lean, config) in sources.items():
        source, cfg = _read_text(lean), _read_json(config)
        statements = [t.statement for t in cov.comparator_targets(source, cfg, Path(lean).name)]
        for claim_id in sorted(c for c in claims if c.startswith(family + ".")):
            check = cov.auto_range_check(claims[claim_id], statements)
            out[f"auto_range/{claim_id}"] = obs(None if check is None else check["relation"])
        lint = cov.lint_comparator_file(source, Path(lean).name, cfg["theorem_names"])
        out[f"lint/{family}/findings"] = obs(lint["findings"])
        out[f"lint/{family}/open"] = obs(len(lint["open"]))
    return out


ETH_DIR = "benchmarks/regression/fixtures/eth-378"
ETH_CLAIM = "378.1"
# The exponents compared in the o(1) check. Lean: runtimeScale, with the Comparator's O(1) factor A. The manuscript
# of 2026-10-25: a single log log n.
ETH_LEAN_EXPONENT = "A*n*log(log(n + 16))**2/sqrt(log(n + 16))"
ETH_MANUSCRIPT_EXPONENT = "A*n*log(log(n))/sqrt(log(n))"


def _eth_statement() -> Dict[str, Dict[str, Any]]:
    from python.discovery import asymptotic_forms as af
    from python.discovery import openai_math_coverage as cov

    source = _read_text(f"{ETH_DIR}/SubexponentialSAT.lean")
    cfg = _read_json(f"{ETH_DIR}/SubexponentialSAT.json")
    targets = cov.comparator_targets(source, cfg, "SubexponentialSAT.lean")
    statement = targets[0].statement
    claims = {c["claim_id"]: c["text"] for c in _read_json("examples/openai-math-coverage/coverage_map.json")["claims"]}
    out: Dict[str, Dict[str, Any]] = {"targets": obs(len(targets))}
    check = cov.auto_range_check(claims[ETH_CLAIM], [statement])
    out["auto_range/relation"] = obs(None if check is None else check["relation"])
    out["auto_range/paper"] = obs(None if check is None else check["paper"])
    uniform = af.uniformity(statement, "machine", ["n", "F"])
    out["uniformity/machine_before_inputs"] = obs(uniform["verdict"])
    out["uniformity/binders"] = obs([q for q, _ in uniform["binders"]])
    # The space bound holds at every prefix of the run: a ∀ over the prefix length, bounded by the running time.
    prefix = [names for q, names in uniform["binders"] if q == "∀" and "prefixSteps" in names]
    out["space_bound/at_every_prefix"] = obs(bool(prefix) and "prefixSteps ≤ time" in statement)
    for label, exponent in (("lean", ETH_LEAN_EXPONENT), ("manuscript", ETH_MANUSCRIPT_EXPONENT)):
        fit = af.little_o_exponent(exponent, c="1/2", symbols=["A"])
        out[f"o1/{label}/signed_reading"] = obs(fit["signed_reading"])
        out[f"o1/{label}/nonnegative_reading"] = obs(fit["nonnegative_reading"])
        out[f"o1/{label}/implied_o1_limit"] = obs(fit["implied_o1_limit"])
    lint = cov.lint_comparator_file(source, "SubexponentialSAT.lean", cfg["theorem_names"])
    out["lint/open"] = obs(sorted(f"{f['kind']}:{f['declaration']}" for f in lint["open"]))
    return out


def _ed_polarity() -> Dict[str, Dict[str, Any]]:
    from python.discovery import ed_polarity_case as ed

    out: Dict[str, Dict[str, Any]] = {}
    for depth, width in ((1, 1), (2, 1), (3, 1), (2, 2)):
        out[f"decide/{depth}x{width}"] = obs(ed.decide(depth, width)["status"])
    for depth in (1, 2, 3):
        out[f"necessity/depth{depth}"] = obs(dict(sorted(ed.necessity_table(depth, 1).items())))
    for label, drop in (("weights", ed.ALL_WEIGHTS), ("fprime", ed.ALL_FPRIME)):
        out[f"drop/{label}"] = obs(ed.verdict(ed.ed_hypothesis(2, 1, drop=drop, claims="polarity"))["status"])
    out["transport_rival"] = obs(ed.verdict(ed.transport_hypothesis(2, 1))["status"])
    negative = ed.replay(ed.witness_negative_weight(), *ed.WITNESS_INPUT)
    decreasing = ed.replay(ed.witness_decreasing_activation(), *ed.WITNESS_INPUT)
    out["replay/negative_weight"] = obs(sorted({d["weight"] for d in negative["disagreements"]}))
    out["replay/decreasing_activation"] = obs(len(decreasing["disagreements"]))
    return out


def _local_smoothing() -> Dict[str, Dict[str, Any]]:
    from python.discovery import local_smoothing_case as case
    from python.discovery.statement_fidelity import compare_ranges

    out: Dict[str, Dict[str, Any]] = {}
    for spec in case.RANGE_SPECS:
        out[f"range/{spec.theorem}"] = obs(compare_ranges(spec).relation.value)
    for spec in case.DEVELOPMENT_SPECS:
        out[f"development/{spec.theorem}"] = obs(compare_ranges(spec).relation.value)
    caught = 0
    for mutant in case.MUTANTS:
        relation = compare_ranges(case.mutant_spec(mutant)).relation.value
        out[f"mutant/{mutant['label']}"] = obs(relation)
        caught += relation == mutant["expected"] and relation != "EQUIVALENT"
    out["mutants_caught"] = obs(caught, HIGHER)
    report = case.lint_report()
    out["lint/open"] = obs(sorted(f"{f['theorem']}:{f['kind']}:{f['line']}" for f in report["findings"]
                                  if f["status"] == "OPEN"))
    out["lint/kinds"] = obs(sorted({f["kind"] for f in report["findings"]}))
    return out


def _ym_o3() -> Dict[str, Dict[str, Any]]:
    from python.discovery import o3_continuum_case as o3
    from python.discovery import yang_mills_case as ymc

    out: Dict[str, Dict[str, Any]] = {}
    ym = ymc.case_report()
    out["ym/checklist_sha256"] = obs(ym["checklist"]["sha256"])
    for claim, probe in sorted(ym["self_probe"].items()):
        out[f"ym/self_probe/{claim}"] = obs(probe["outcome"])
    for s in ym["scenarios"]:
        out[f"ym/scenario/{s['id']}"] = obs({"outcome": s["outcome"], "satisfied_by": s["satisfied_by"],
                                             "undetermined": s["undetermined"]})
    out["ym/single_barrier_obligations"] = obs(ym["single_barrier_obligations"])
    out["ym/claim_record_rung"] = obs(ym["claim_record"]["rung"])
    report = o3.case_report()
    out["o3/checklist_sha256"] = obs(report["checklist"]["sha256"])
    out["o3/coverage_counts"] = obs(report["coverage_counts"])
    for name, probe in sorted(report["probes"].items()):
        out[f"o3/probe/{name}"] = obs({"outcome": probe["outcome"], "satisfied_by": probe["satisfied_by"]})
    out["o3/exclusion_lint"] = obs(report["exclusion_lint"]["flag"])
    return out


MA_FIXTURE = "benchmarks/regression/fixtures/manuscript-audit/calibration.json"


def _manuscript_audit() -> Dict[str, Dict[str, Any]]:
    from python.discovery import manuscript_audit as ma

    fx = _read_json(MA_FIXTURE)
    files, registry = fx["files"], fx["registry"]
    out: Dict[str, Dict[str, Any]] = {}
    report = ma.audit(files)
    out["gate"] = obs(report["citation_gate"]["status"])
    out["unresolved"] = obs([u["key"] for u in report["citation_gate"]["unresolved"]])
    out["import_counts"] = obs(report["import_counts"])
    out["hypothesis_outcomes"] = obs(report["hypothesis_outcomes"])
    out["ledger_status"] = obs(report["ledger_status"])
    out["relays"] = obs(sorted(r["code"] for r in report["mandatory_relays"]))

    def lz(f, reg):
        imports = ma.audit(f, registry=reg)["imports"]
        return next(i for i in imports if i["kind"] == "HYPOTHESIS_MATCH" and i["key"] == "LZ")

    unmatched = lz(files, registry)
    out["registry/unstated"] = obs({"outcome": unmatched["outcome"], "missing": unmatched["missing"]})
    stated = dict(files, **{"main.tex": files["main.tex"].replace(fx["stated_hypothesis"]["replace"],
                                                                fx["stated_hypothesis"]["with"])})
    out["registry/stated"] = obs(lz(stated, registry)["outcome"])
    tricky = [dict(registry[0], hypotheses=[{"text": "t", "phrases": [fx["regex_like_phrase"]]}])]
    out["registry/regex_like_phrase"] = obs(lz(files, tricky)["outcome"])
    out["no_bibliography"] = obs(ma.audit({"main.tex": "See \\cite{A}.\n"})["citation_gate"]["status"])
    dep = fx["dependency"]
    report = ma.audit(dep["files"], manuscript_status=dep["manuscript_status"])
    out["dependency/withdrawn"] = obs([[i["kind"], i["outcome"]] for i in report["imports"]])
    out["dependency/link_outside_collection"] = obs(
        ma.audit(dep["files"], collection=dep["collection_without_target"])["citation_gate"]["status"]
    )
    return out


CR_FIXTURE = "benchmarks/regression/fixtures/cited-registry/calibration.json"


def _cited_registry() -> Dict[str, Dict[str, Any]]:
    from python.discovery import cited_registry as cr

    fx = _read_json(CR_FIXTURE)
    out: Dict[str, Dict[str, Any]] = {}

    w = fx["withdrawal"]
    reg = cr.Registry(None)
    entry = reg.register(copy.deepcopy(w["entry"]))
    opposite = cr.cite_check(entry, w["opposite_context"])
    out["withdrawal/opposite/outcome"] = obs(opposite["outcome"])
    out["withdrawal/opposite/conventions"] = obs([c["outcome"] for c in opposite["conventions"]])
    out["withdrawal/opposite/hypotheses"] = obs([h["outcome"] for h in opposite["hypotheses"]])
    matching = cr.cite_check(entry, w["matching_context"])
    out["withdrawal/matching/outcome"] = obs(matching["outcome"])
    out["withdrawal/matching/hypotheses"] = obs([h["outcome"] for h in matching["hypotheses"]])
    out["withdrawal/silent/outcome"] = obs(cr.cite_check(entry, {})["outcome"])
    for node, on in w["dependencies"]:
        reg.depend(node, on)
    out["withdrawal/retraction_flags"] = obs(reg.retract(entry.id, w["retraction"])["flagged"])

    e = fx["eth"]
    reg = cr.Registry(None)
    reg.register(copy.deepcopy(e["entry"]))
    for node, on in e["dependencies"]:
        reg.depend(node, on)
    out["eth/impact"] = obs(reg.impact("ETH")["dependents"])
    out["eth/retraction_flags"] = obs(reg.retract("ETH", e["retraction"], when=e["when"])["flagged"])
    out["eth/effective_rung/dependent"] = obs(reg.effective_rung("corollary-of-X", "KERNEL_CHECKED"))
    out["eth/effective_rung/unrelated"] = obs(reg.effective_rung("unrelated", "KERNEL_CHECKED"))
    out["eth/cite_after_retraction"] = obs(cr.cite_check(reg.get("ETH"), {})["outcome"])

    b = fx["biomarker"]
    reg = cr.Registry(None)
    entry = reg.register(copy.deepcopy(b["entry"]))
    check = cr.cite_check(entry, b["citing"])
    out["biomarker/outcome"] = obs(check["outcome"])
    out["biomarker/mismatched_conventions"] = obs([c["tag"] for c in check["conventions"] if c["outcome"] == cr.MISMATCH])
    out["biomarker/age_hypothesis"] = obs(check["hypotheses"][0]["outcome"])
    wider = dict(b["citing"], conventions=dict(b["citing"]["conventions"], validated_assay="assay A"),
                 assumptions=b["wider_assumptions"])
    out["biomarker/wider_age_hypothesis"] = obs(cr.cite_check(entry, wider)["hypotheses"][0]["outcome"])
    return out


VC_FIXTURE = "benchmarks/regression/fixtures/verification-chain/cases.json"


def _verification_chain() -> Dict[str, Dict[str, Any]]:
    """The composed chain (ADR-085) end to end on a math and a biomedical-style hypothesis, then the freeze against an
    edited hypothesis, which must be BLOCKED with every later step NOT_RUN."""
    from python.discovery import freeze_service, verification_chain

    out: Dict[str, Dict[str, Any]] = {}
    for name, case in sorted(_read_json(VC_FIXTURE)["cases"].items()):
        store = freeze_service.FreezeStore(None)
        result = verification_chain.run(copy.deepcopy(case["request"]), store)
        out[f"{name}/formal_status"] = obs(result["formal_status"])
        out[f"{name}/steps"] = obs([[s["name"], s["state"], s["outcome"]] for s in result["steps"]])
        ledger = result["obligation_ledger"]
        out[f"{name}/obligations"] = obs({o["id"]: o["status"] for o in ledger["claim"]["obligations"]})
        out[f"{name}/rollup"] = obs([ledger["rollup"]["status"], ledger["rollup"]["trust_rung"]])
        out[f"{name}/freeze_sha256"] = obs(result["freeze"]["record"]["sha256"])
        edited = copy.deepcopy(case["request"])
        edited["hypothesis"]["claims"] = case["edited_claims"]
        edited.pop("author")
        edited["freeze"] = {"freeze_id": result["freeze"]["freeze_id"]}
        blocked = verification_chain.run(edited, store)
        out[f"{name}/edited/steps"] = obs([[s["name"], s["state"]] for s in blocked["steps"]])
        out[f"{name}/edited/formal_status"] = obs(blocked["formal_status"])
    return out


BC_FIXTURE = "benchmarks/regression/fixtures/biomedical-chain/cases.json"


def _biomedical_chain() -> Dict[str, Dict[str, Any]]:
    """Block E (ADR-086): the chain on biomedical hypotheses, the pTau217 cutoff rule, the Alzheimer rivals and a
    mechanistic chain from prose, each with its variants. Every step's state, every obligation, the roll-up and the
    domain outcomes are frozen; a case with `edited_claims` is also checked BLOCKED against its own freeze."""
    from python.discovery import freeze_service, verification_chain

    out: Dict[str, Dict[str, Any]] = {}
    for name, case in sorted(_read_json(BC_FIXTURE)["cases"].items()):
        store = freeze_service.FreezeStore(None)
        result = verification_chain.run(copy.deepcopy(case["request"]), store)
        out[f"{name}/formal_status"] = obs(result["formal_status"])
        out[f"{name}/steps"] = obs([[s["name"], s["state"], s["outcome"]] for s in result["steps"]])
        ledger = result["obligation_ledger"]
        if ledger is not None:
            out[f"{name}/obligations"] = obs({o["id"]: o["status"] for o in ledger["claim"]["obligations"]})
            out[f"{name}/rollup"] = obs([ledger["rollup"]["status"], ledger["rollup"]["trust_rung"]])
        domain = result.get("domain") or {}
        if "units" in domain:
            out[f"{name}/units"] = obs({p["where"]: p["outcome"] for p in domain["units"]["predicates"]})
        for rep in domain.get("null_biomarker") or []:
            out[f"{name}/null_biomarker/{rep['biomarker']}"] = obs(rep.get("outcome"))
        if "population" in domain:
            out[f"{name}/population"] = obs(domain["population"].get("outcome"))
        if "untreated_arm" in domain:
            out[f"{name}/untreated_arm"] = obs(domain["untreated_arm"].get("outcome_status"))
        if "mechanism" in domain:
            mech = domain["mechanism"]
            out[f"{name}/mechanism/links"] = obs([[r["link"], r["sign"], r["status"], r["sign_status"]]
                                                  for r in mech["links"]])
            out[f"{name}/mechanism/compatibility"] = obs(mech["compatibility"]["status"])
        cites = (result.get("response") or {}).get("reports", {}).get("citations") or []
        if cites:
            out[f"{name}/citations"] = obs([[c["outcome"], [[k["tag"], k["outcome"]] for k in c["conventions"]],
                                             [h["outcome"] for h in c["hypotheses"]]] for c in cites])
        hypothesis = (result.get("response") or {}).get("formal_hypothesis") or {}
        if result.get("freeze") and not any(v.get("continuous") for v in hypothesis.get("variables") or []):
            # Under z3 the frozen witnesses are the solver's choice, which may differ between platforms; the digest
            # is frozen for enumerated hypotheses only. The BLOCKED check below covers every case.
            out[f"{name}/freeze_sha256"] = obs(result["freeze"]["record"]["sha256"])
        if case.get("edited_claims"):
            edited = copy.deepcopy(case["request"])
            edited["hypothesis"]["claims"] = case["edited_claims"]
            edited.pop("author")
            edited["freeze"] = {"freeze_id": result["freeze"]["freeze_id"]}
            blocked = verification_chain.run(edited, store)
            out[f"{name}/edited/steps"] = obs([[s["name"], s["state"]] for s in blocked["steps"]])
            out[f"{name}/edited/formal_status"] = obs(blocked["formal_status"])
    return out


CASES: Dict[str, Case] = {
    c.id: c
    for c in (
        Case("openai_math_time_travel", "openai/math time-travel benchmark: real corrected defects and false alarms",
             "ADR-DISCOVERY-077", [TT_DATASET, TT_FIXTURE] + TT_CHAIN + TT_TYPED, _time_travel,
             "Excerpts of the pre-fix and corrected sources, verified to reproduce the full run's flags; the full-chain "
             "re-run from its blind registry entries and citing contexts."),
        Case("openai_math_coverage_calibration", "Coverage-map calibration, families 079 and 215",
             "ADR-DISCOVERY-070",
             ["examples/openai-math-coverage/coverage_map.json",
              "examples/local-smoothing-fidelity/LocalSmoothing.lean",
              "examples/local-smoothing-fidelity/LocalSmoothing.json",
              "examples/o3-continuum-rehearsal/ClassicalON.lean",
              "examples/o3-continuum-rehearsal/ClassicalON.json"], _coverage_calibration),
        Case("eth_statement_fidelity", "ETH refutation statement (family 378) as a positive fidelity control",
             "ADR-DISCOVERY-084",
             [f"{ETH_DIR}/SubexponentialSAT.lean", f"{ETH_DIR}/SubexponentialSAT.json",
              "examples/openai-math-coverage/coverage_map.json"], _eth_statement,
             "Includes the o(1) sign subtlety: the Lean bound fits n/(log n)^{1/2+o(1)} only with a signed o(1)."),
        Case("sakana_ed_polarity", "Sakana Error Diffusion polarity case", "ADR-DISCOVERY-059", [], _ed_polarity),
        Case("local_smoothing_fidelity", "Local smoothing statement fidelity", "ADR-DISCOVERY-070",
             ["examples/local-smoothing-fidelity/LocalSmoothing.lean"], _local_smoothing),
        Case("yang_mills_o3_rehearsal", "Yang-Mills pre-registration and the O(3) rehearsal", "ADR-DISCOVERY-081",
             ["examples/yang-mills-preregistration/ym4_existence_checklist.v1.json",
              "examples/o3-continuum-rehearsal/o3_continuum_claim.v1.json",
              "examples/o3-continuum-rehearsal/ClassicalON.lean"], _ym_o3),
        Case("manuscript_audit_calibration", "Manuscript audit calibration", "ADR-DISCOVERY-082", [MA_FIXTURE],
             _manuscript_audit),
        Case("cited_registry_calibration", "Cited-results registry calibrations", "ADR-DISCOVERY-083", [CR_FIXTURE],
             _cited_registry),
        Case("verification_chain", "Composed verification chain on a math and a biomedical-style hypothesis",
             "ADR-DISCOVERY-085", [VC_FIXTURE], _verification_chain,
             "Freeze, formalize, fidelity, vacuity, obligations, seams, discharge, trust ladder; an edited hypothesis "
             "against the freeze must be BLOCKED."),
        Case("biomedical_chain", "Composed chain on biomedical hypotheses: pTau217 cutoff, Alzheimer rivals, a "
             "mechanistic chain", "ADR-DISCOVERY-086", [BC_FIXTURE], _biomedical_chain,
             "Units, conventions, null-biomarker, untreated-arm and population probes, mechanism links and signs. "
             "Illustrative values only, not clinical values."),
    )
}


# ---------------------------------------------------------------------------
# Expectations
# ---------------------------------------------------------------------------


def expectations_sha256(data: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def load_expectations(path: Path = EXPECTATIONS, sha_path: Path = EXPECTATIONS_SHA) -> Dict[str, Any]:
    if not path.exists():
        raise ExpectationsError(f"no expectations file at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ExpectationsError(f"unknown schema {data.get('schema')!r}")
    pinned = sha_path.read_text(encoding="utf-8").split()[0] if sha_path.exists() else None
    digest = expectations_sha256(data)
    if pinned != digest:
        raise ExpectationsError(
            f"expectations.json does not match its pinned SHA-256 ({digest} != {pinned}); "
            "update expectations only through `coresearcher regression update`"
        )
    return data


def run_case(case: Case) -> Dict[str, Any]:
    """A fresh run of one case: observations, fixture hashes and the time it took. Never raises."""
    start = time.perf_counter()
    fixtures = {rel: file_sha256(ROOT / rel) if (ROOT / rel).exists() else None for rel in case.fixtures}
    try:
        observations = case.run()
        error = None
    except Exception as exc:  # A case that cannot run is reported as ERROR, never as a pass.
        observations, error = {}, f"{type(exc).__name__}: {exc}"
    return {"observations": observations, "fixtures": fixtures, "error": error,
            "seconds": round(time.perf_counter() - start, 3)}


def classify(expected: Dict[str, Any], observed: Dict[str, Any]) -> Optional[str]:
    """None when equal, else REGRESSION, IMPROVEMENT or CHANGED."""
    a, b = expected["value"], observed["value"]
    if a == b and expected.get("better") == observed.get("better"):
        return None
    better = expected.get("better", EXACT)
    if better != observed.get("better"):
        return CHANGED
    if better == EXACT:
        return REGRESSION
    if better in (HIGHER, LOWER) and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        up = b > a
        return IMPROVEMENT if up == (better == HIGHER) else REGRESSION
    if better == VERDICT and a in _VERDICT_RANK and b in _VERDICT_RANK:
        if _VERDICT_RANK[a] == _VERDICT_RANK[b]:
            return CHANGED
        return IMPROVEMENT if _VERDICT_RANK[b] > _VERDICT_RANK[a] else REGRESSION
    return CHANGED


def compare_case(case_id: str, expected: Optional[Dict[str, Any]], fresh: Dict[str, Any]) -> Dict[str, Any]:
    differences = []
    if fresh["error"]:
        status = ERROR
    elif expected is None:
        status = CHANGED
        differences.append({"key": "*", "class": CHANGED, "expected": None, "observed": "case has no expectation"})
    else:
        for rel, digest in sorted(fresh["fixtures"].items()):
            if expected.get("fixtures", {}).get(rel) != digest:
                differences.append({"key": f"fixture:{rel}", "class": FIXTURE_CHANGED,
                                    "expected": expected.get("fixtures", {}).get(rel), "observed": digest})
        for rel in sorted(set(expected.get("fixtures", {})) - set(fresh["fixtures"])):
            differences.append({"key": f"fixture:{rel}", "class": FIXTURE_CHANGED,
                                "expected": expected["fixtures"][rel], "observed": None})
        exp_obs, new_obs = expected["observations"], fresh["observations"]
        for key in sorted(set(exp_obs) | set(new_obs)):
            if key not in new_obs or key not in exp_obs:
                differences.append({"key": key, "class": CHANGED, "expected": exp_obs.get(key, {}).get("value"),
                                    "observed": new_obs.get(key, {}).get("value")})
                continue
            klass = classify(exp_obs[key], new_obs[key])
            if klass:
                differences.append({"key": key, "class": klass, "expected": exp_obs[key]["value"],
                                    "observed": new_obs[key]["value"]})
        order = (REGRESSION, FIXTURE_CHANGED, CHANGED, IMPROVEMENT)
        classes = {d["class"] for d in differences}
        status = next((c for c in order if c in classes), PASS)
    return {"case": case_id, "status": status, "error": fresh["error"], "seconds": fresh["seconds"],
            "observations": len(fresh["observations"]), "differences": differences}


def _select(case_ids: Optional[Sequence[str]]) -> List[Case]:
    if not case_ids:
        return list(CASES.values())
    unknown = sorted(set(case_ids) - set(CASES))
    if unknown:
        raise KeyError(f"unknown regression case(s): {', '.join(unknown)}")
    return [CASES[c] for c in case_ids]


def check(case_ids: Optional[Sequence[str]] = None, expectations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the selected cases and compare them with the frozen expectations."""
    data = expectations if expectations is not None else load_expectations()
    results = [compare_case(c.id, data["cases"].get(c.id), run_case(c)) for c in _select(case_ids)]
    statuses = {r["status"] for r in results}
    order = (ERROR, REGRESSION, FIXTURE_CHANGED, CHANGED, IMPROVEMENT)
    return {
        "schema": SCHEMA,
        "expectations_version": data["version"],
        "expectations_sha256": expectations_sha256(data),
        "status": next((s for s in order if s in statuses), PASS),
        "cases": results,
    }


def update(reason: str, case_ids: Optional[Sequence[str]] = None, path: Path = EXPECTATIONS,
           sha_path: Path = EXPECTATIONS_SHA, today: Optional[str] = None) -> Dict[str, Any]:
    """Freeze fresh observations as the expectations of the selected cases (all by default). Refuses a case that
    errors, and refuses an empty reason: the reason is the review record of the change."""
    if not reason or not reason.strip():
        raise ExpectationsError("an update needs a reason")
    if path.exists():
        data = load_expectations(path, sha_path)
    else:
        data = {"schema": SCHEMA, "version": 0, "history": [], "cases": {}}
    selected = _select(case_ids)
    changes = {}
    for case in selected:
        fresh = run_case(case)
        if fresh["error"]:
            raise ExpectationsError(f"case {case.id} could not run: {fresh['error']}")
        old = data["cases"].get(case.id)
        diff = compare_case(case.id, old, fresh)["differences"]
        if diff or old is None:
            changes[case.id] = [{k: d[k] for k in ("key", "class")} for d in diff]
        data["cases"][case.id] = {"title": case.title, "adr": case.adr, "notes": case.notes,
                                  "fixtures": fresh["fixtures"], "observations": fresh["observations"]}
    if not changes:
        return {"version": data["version"], "changed": {}}
    data["version"] += 1
    data["history"].append({"version": data["version"], "date": today or _dt.date.today().isoformat(),
                            "reason": reason.strip(), "changes": changes})
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8",
                    newline="\n")
    sha_path.write_text(f"{expectations_sha256(data)}  {path.name}\n", encoding="utf-8", newline="\n")
    return {"version": data["version"], "changed": changes}


def describe() -> List[Dict[str, Any]]:
    return [{"id": c.id, "title": c.title, "adr": c.adr, "fixtures": c.fixtures, "notes": c.notes}
            for c in CASES.values()]


__all__ = ["CASES", "Case", "ExpectationsError", "check", "update", "describe", "load_expectations", "obs",
           "classify", "compare_case", "run_case"]
