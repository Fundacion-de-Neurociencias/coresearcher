"""Tests for ADR-DISCOVERY-086: the verification chain on biomedical hypotheses and the capabilities it needed.

Every number below is illustrative, chosen to exercise a check; none is a clinical value.
"""

import argparse
import copy
import json
from pathlib import Path

import pytest

from python.cli import biomedical as biomedical_cli
from python.discovery import (
    biomedical_conventions,
    biomedical_domain,
    biomedical_units,
    cited_registry,
    freeze_service,
    hypothesis_ledger,
    mechanistic_chain,
    verification_chain,
)

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "benchmarks" / "regression" / "fixtures" / "biomedical-chain" / "cases.json"

PTAU = {
    "hypothesis_id": "PT",
    "variables": [
        {"name": "ptau", "domain": [0, 1, 2, 3]},
        {"name": "decline", "domain": [0, 1]},
        {"name": "age", "domain": [40, 60, 80]},
    ],
    "scope": "age >= 60",
    "claims": ["ptau < 2 or decline == 1", "ptau >= 2 or decline == 0"],
}
NODES = [
    {"name": "amyloid", "levels": [0, 1, 2]},
    {"name": "ptau217", "levels": [0, 1, 2], "aliases": ["plasma ptau217"]},
    {"name": "tau_spread", "levels": [0, 1, 2], "aliases": ["tau spread"]},
    {"name": "cognition", "levels": [0, 1, 2], "scale_direction": "higher is better"},
]
PROSE = "Amyloid raises plasma pTau217, which drives tau spread, which worsens cognition."


def _statuses(obligations):
    return {o.id: o.status.value for o in obligations}


def _case(name):
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][name]


# --------------------------------------------------------------------------- units


@pytest.mark.parametrize(
    "a, b, outcome",
    [
        ("pg/mL", "ng/L", "SAME"),
        ("pg/mL", "ng/mL", "SAME_DIMENSION"),
        ("mL/min/1.73m^2", "mL/min", "DIFFERENT_DIMENSION"),
        ("years", "y", "SAME"),
        ("mmol/L", "umol/mL", "SAME"),
        ("%", "1", "SAME_DIMENSION"),
        ("SUVR", "centiloid", "DIFFERENT_DIMENSION"),
        ("pg/mL", "pg/(mL", "UNREADABLE"),
    ],
)
def test_unit_algebra(a, b, outcome):
    assert biomedical_units.same_unit(a, b)["outcome"] == outcome


def test_scale_mismatch_names_the_factor():
    assert biomedical_units.same_unit("pg/mL", "ng/mL")["factor"] == pytest.approx(1e-3)


def test_units_check_finds_dimension_and_scale_mismatches():
    h = dict(PTAU, variables=PTAU["variables"] + [{"name": "egfr", "domain": [30, 90]}, {"name": "cut", "domain": [1]}])
    h["claims"] = ["ptau + egfr > 3", "ptau >= cut", "ptau < 2 or decline == 1"]
    report = biomedical_units.check(h, {"ptau": "pg/mL", "egfr": "mL/min/1.73m^2", "cut": "ng/mL"})
    by = {p["where"]: p["outcome"] for p in report["predicates"]}
    assert by == {
        "scope": "NOT_APPLICABLE",
        "claims[0]": "DIMENSION_MISMATCH",
        "claims[1]": "SCALE_MISMATCH",
        "claims[2]": "NOT_APPLICABLE",
    }
    assert report["outcome"] == "FINDINGS"


def test_units_check_products_quotients_and_undeclared_units():
    h = {
        "hypothesis_id": "U",
        "variables": [{"name": n, "continuous": True} for n in ("dose", "w", "c", "k")],
        "claims": ["dose / w >= c", "k > c"],
    }
    report = biomedical_units.check(h, {"dose": "mg", "w": "kg", "c": "mg/kg"})
    by = {p["where"]: p["outcome"] for p in report["predicates"]}
    assert by == {"claims[0]": "HOMOGENEOUS", "claims[1]": "UNDECLARED_UNIT"}
    assert report["outcome"] == "INCOMPLETE"
    with pytest.raises(Exception):
        biomedical_units.check(h, {"nope": "mg"})


# --------------------------------------------------------------------------- conventions


def test_convention_vocabulary_merges_spellings_only():
    assert biomedical_conventions.canonical_tag("assay") == "validated_assay"
    assert biomedical_conventions.compare("matrix", "Cerebrospinal fluid", "CSF")["outcome"] == "MATCH"
    assert biomedical_conventions.compare("matrix", "EDTA plasma", "plasma")["outcome"] == "MISMATCH"
    assert biomedical_conventions.compare("scale_direction", "lower is better", "higher_is_worse")["outcome"] == "MATCH"
    assert (
        biomedical_conventions.compare("cutoff_derivation", "fixed sensitivity 90%", "fixed sensitivity 95%")["outcome"]
        == "MISMATCH"
    )
    assert biomedical_conventions.compare("units", "pg/mL", "ng/L")["compared_by"] == "unit algebra"


def test_registry_compares_units_by_algebra_and_tags_by_alias():
    entry = cited_registry.RegistryEntry(
        id="cut",
        source="illustrative",
        statement="cutoff",
        conventions={"units": "pg/mL", "assay": "assay A", "matrix": "plasma"},
    )
    same = cited_registry.cite_check(
        entry, {"conventions": {"units": "ng/L", "validated_assay": "Assay A", "matrix": "blood plasma"}}
    )
    assert same["outcome"] == "CLEAR"
    scaled = cited_registry.cite_check(
        entry, {"conventions": {"units": "ng/mL", "validated_assay": "assay A", "matrix": "plasma"}}
    )
    row = next(c for c in scaled["conventions"] if c["tag"] == "units")
    assert scaled["outcome"] == "FINDINGS" and row["outcome"] == "MISMATCH" and "0.001" in row["detail"]


def test_citations_inherit_the_hypothesis_conventions_and_the_variable_unit():
    spec = {"units": {"ptau": "ng/L"}, "conventions": {"matrix": "plasma"}}
    items = biomedical_domain.fill_citations(
        [
            {"entry_id": "e", "variable": "ptau"},
            {"entry_id": "f", "conventions": {"matrix": "CSF"}},
            {"entry_id": "g", "context": {"conventions": {}}},
        ],
        spec,
    )
    assert items[0]["conventions"] == {"matrix": "plasma", "units": "ng/L"}
    assert items[1]["conventions"] == {"matrix": "CSF"}
    assert "conventions" not in items[2]


# --------------------------------------------------------------------------- probes


def test_null_biomarker_probe_detects_an_idle_biomarker():
    works, report = biomedical_domain.null_biomarker(PTAU, "ptau", [])
    assert works.status.value == "DISCHARGED_SYMBOLIC" and report["outcome"] == "BIOMARKER_DOES_WORK"
    age_only = dict(PTAU, claims=["age < 80 or decline == 1"])
    idle, report = biomedical_domain.null_biomarker(age_only, "ptau", [])
    assert idle.status.value == "REFUTED" and report["outcome"] == "BIOMARKER_IDLE"


def test_null_biomarker_probe_flags_predictions_that_do_not_rest_on_it():
    h = dict(PTAU, claims=["ptau < 2 or decline == 1", "age < 80 or decline == 1"])
    ob, report = biomedical_domain.null_biomarker(h, "ptau", ["age < 80 or decline == 1", "ptau < 2 or decline == 1"])
    assert ob.status.value == "OPEN"
    assert [p["index"] for p in report["predictions_without_biomarker"]] == [0]


def test_untreated_arm_probe_has_three_outcomes():
    variables = [{"name": "treated", "domain": [0, 1]}, {"name": "decline", "domain": [0, 1]}]
    base = {"hypothesis_id": "T", "variables": variables}
    met = dict(base, claims=["decline == 1"])
    allowed = dict(base, claims=["treated == 0 or decline == 0"])
    forbidden = dict(base, claims=["treated == 1 or decline == 1"])
    status = {}
    for name, h in (("met", met), ("allowed", allowed), ("forbidden", forbidden)):
        ob, _ = biomedical_domain.untreated_arm(h, "treated == 0", "decline == 0" if name != "met" else "decline == 1")
        status[name] = ob.status.value
    assert status == {"met": "REFUTED", "allowed": "OPEN", "forbidden": "DISCHARGED_SYMBOLIC"}


def test_population_probe_finds_states_outside_the_validated_one():
    ob, report = biomedical_domain.population(PTAU, "age >= 50")
    assert ob.status.value == "DISCHARGED_SYMBOLIC"
    wide = dict(PTAU, scope="age >= 40")
    ob, report = biomedical_domain.population(wide, "age >= 50")
    assert ob.status.value == "OPEN" and report["witness"]["age"] == 40


def test_biomedical_spec_is_validated():
    with pytest.raises(biomedical_domain.DomainSpecError):
        biomedical_domain.validate({"probes": {"placebo": {}}})
    with pytest.raises(biomedical_domain.DomainSpecError):
        biomedical_domain.validate({"probes": {"untreated_arm": {"untreated": "x == 0"}}})


# --------------------------------------------------------------------------- mechanistic chains


def test_controlled_prose_compiles_to_signed_links():
    compiled = mechanistic_chain.compile_mechanism({"prose": PROSE, "nodes": NODES})
    assert [(link["from"], link["to"]) for link in compiled["links"]] == [
        ("amyloid", "ptau217"),
        ("ptau217", "tau_spread"),
        ("tau_spread", "cognition"),
    ]
    assert [s["sign"] for s in compiled["link_signs"]] == ["+", "+", "-"]
    assert compiled["prediction"]["sign"] == "-"
    assert compiled["consequences"] == ["not (amyloid_1 > amyloid_0) or (cognition_1 < cognition_0)"]


def test_mechanism_obligations_discharge_a_coherent_chain():
    result = mechanistic_chain.check({"prose": PROSE, "nodes": NODES})
    status = {o["id"]: o["status"] for o in result["obligations"]}
    assert set(status.values()) == {"DISCHARGED_SYMBOLIC"} and "mechanism:compatibility" in status


def test_sign_seam_refutes_the_link_sign_and_the_compatibility():
    links = [
        {"from": "amyloid", "to": "ptau217", "sign": "+"},
        {"from": "ptau217", "to": "cognition", "sign": "+", "effect": "worsens"},
    ]
    result = mechanistic_chain.check(
        {
            "nodes": [n for n in NODES if n["name"] != "tau_spread"],
            "links": links,
            "prediction": {"from": "amyloid", "to": "cognition", "effect": "worsens"},
        }
    )
    status = {o["id"]: o["status"] for o in result["obligations"]}
    assert status["link_sign[1]"] == "REFUTED" and status["mechanism:compatibility"] == "REFUTED"
    assert result["report"]["compatibility"]["counterexamples"]


def test_effect_without_scale_direction_stays_open():
    nodes = [dict(n, scale_direction=None) if n["name"] == "cognition" else n for n in NODES]
    result = mechanistic_chain.check(
        {"prose": PROSE, "nodes": [{k: v for k, v in n.items() if v is not None} for n in nodes]}
    )
    status = {o["id"]: o["status"] for o in result["obligations"]}
    assert status["link_sign[2]"] == "OPEN" and status["link[2]"] == "OPEN"
    assert status["mechanism:compatibility"] == "OPEN"


def test_opposite_paths_do_not_entail_a_prediction():
    nodes = [{"name": n, "levels": [0, 1, 2]} for n in ("a", "b", "c", "d")]
    links = [
        {"from": "a", "to": "b", "sign": "+"},
        {"from": "a", "to": "c", "sign": "-"},
        {"from": "b", "to": "d", "sign": "+"},
        {"from": "c", "to": "d", "sign": "+"},
    ]
    result = mechanistic_chain.check(
        {"nodes": nodes, "links": links, "prediction": {"from": "a", "to": "d", "sign": "+"}}
    )
    assert result["report"]["compatibility"]["status"] == "REFUTED"


def test_saturated_node_refutes_its_links():
    nodes = [dict(n, levels=[0]) if n["name"] == "tau_spread" else n for n in NODES]
    result = mechanistic_chain.check({"prose": PROSE, "nodes": nodes})
    rows = result["report"]["links"]
    assert [r["status"] for r in rows] == ["DISCHARGED_SYMBOLIC", "REFUTED", "REFUTED"]
    assert result["report"]["compatibility"]["status"] == "REFUTED"


def test_malformed_mechanisms_are_refused_and_prose_outside_the_grammar_is_not_guessed():
    with pytest.raises(mechanistic_chain.MechanismError):
        mechanistic_chain.compile_mechanism(
            {
                "nodes": NODES[:2],
                "links": [
                    {"from": "amyloid", "to": "ptau217", "sign": "+"},
                    {"from": "ptau217", "to": "amyloid", "sign": "+"},
                ],
                "prediction": {"from": "amyloid", "to": "ptau217", "sign": "+"},
            }
        )
    with pytest.raises(mechanistic_chain.MechanismError):
        mechanistic_chain.compile_mechanism({"nodes": NODES, "links": [{"from": "amyloid", "to": "x", "sign": "+"}]})
    unread = mechanistic_chain.check({"prose": "Amyloid somehow modulates plasma pTau217.", "nodes": NODES})
    assert unread["formal_status"] == "FORMALIZATION_FAILED"
    unknown = mechanistic_chain.check({"prose": "Amyloid raises plasma neurofilament.", "nodes": NODES})
    assert unknown["formal_status"] == "FORMALIZATION_FAILED" and "neurofilament" in unknown["reason"]


# --------------------------------------------------------------------------- the chain


def test_chain_on_the_restated_ptau217_rule():
    result = verification_chain.run(copy.deepcopy(_case("ptau217_cutoff")["request"]), freeze_service.FreezeStore())
    steps = {s["name"]: (s["state"], s["outcome"]) for s in result["steps"]}
    assert steps["seams"] == ("DONE", "CLEAR, units HOMOGENEOUS, population INSIDE_VALIDATED_POPULATION")
    status = {o["id"]: o["status"] for o in result["obligation_ledger"]["claim"]["obligations"]}
    assert status["consequence[0]"] == status["consequence[1]"] == "DISCHARGED_SYMBOLIC"
    assert status["fidelity"] == "OPEN" and result["outcome"] == "OPEN"


def test_chain_on_the_ptau217_rule_as_submitted_explains_the_empty_claims():
    result = verification_chain.run(
        copy.deepcopy(_case("ptau217_cutoff_as_submitted")["request"]), freeze_service.FreezeStore()
    )
    claim = next(o for o in result["obligation_ledger"]["claim"]["obligations"] if o["id"] == "claim[0]")
    assert claim["status"] == "REFUTED" and "belongs in `consequences`" in claim["discharges"][0]["detail"]["reason"]


def test_chain_compiles_a_mechanism_and_reports_its_obligations():
    request = {"mechanism": {"hypothesis_id": "M", "prose": PROSE, "nodes": NODES}, "author": "t"}
    result = verification_chain.run(request, freeze_service.FreezeStore())
    steps = {s["name"]: s for s in result["steps"]}
    assert steps["formalize"]["outcome"] == "COMPILED" and steps["vacuity"]["outcome"].endswith(
        "probe:untreated_arm DISCHARGED_SYMBOLIC"
    )
    assert steps["obligations"]["detail"]["mechanism"]["mechanism:compatibility"] == "DISCHARGED_SYMBOLIC"
    assert result["domain"]["untreated_arm"]["outcome_status"] == "FORBIDDEN_IN_UNTREATED_ARM"
    assert ["mechanism:compatibility", "link[0]"] in result["obligation_ledger"]["dag"]["edges"]


def test_chain_stops_on_prose_outside_the_grammar():
    request = {"mechanism": {"prose": "Amyloid somehow modulates plasma pTau217.", "nodes": NODES}, "author": "t"}
    result = verification_chain.run(request, freeze_service.FreezeStore())
    assert result["formal_status"] == "FORMALIZATION_FAILED" and result["outcome"] is None
    assert [s["state"] for s in result["steps"]][:3] == ["DONE", "FORMALIZATION_FAILED", "NOT_RUN"]


def test_chain_refuses_malformed_requests():
    store = freeze_service.FreezeStore()
    with pytest.raises(verification_chain.ChainInputError):
        verification_chain.run({"hypothesis": PTAU, "mechanism": {"nodes": NODES}, "author": "t"}, store)
    with pytest.raises(verification_chain.ChainInputError):
        verification_chain.run({"hypothesis": PTAU, "biomedical": {"probes": {"nope": 1}}, "author": "t"}, store)
    with pytest.raises(verification_chain.ChainInputError):
        verification_chain.run(
            {"mechanism": {"nodes": NODES, "links": [{"from": "amyloid", "to": "ptau217"}]}, "author": "t"}, store
        )


def test_chain_without_a_biomedical_block_is_unchanged():
    result = verification_chain.run({"hypothesis": PTAU, "author": "t"}, freeze_service.FreezeStore())
    assert "domain" not in result
    assert {o["id"] for o in result["obligation_ledger"]["claim"]["obligations"]} == {
        "fidelity",
        "vacuity",
        "claim[0]",
        "claim[1]",
    }


def test_ledger_dag_links_probes_to_claims():
    graph = hypothesis_ledger.dag([type("O", (), {"id": i})() for i in ("claim[0]", "probe:population", "units")])
    assert graph["edges"] == [["probe:population", "claim[0]"]] and graph["acyclic"]


# --------------------------------------------------------------------------- API and CLI


def test_api_vocabulary_check_and_mechanism(api_client):
    vocab = api_client.get("/api/biomedical/vocabulary").json()
    assert "matrix" in vocab["kinds"] and "csf" in vocab["values"]["matrix"]
    body = api_client.post(
        "/api/biomedical/check",
        json={
            "hypothesis": PTAU,
            "biomedical": {
                "units": {"ptau": "pg/mL"},
                "probes": {"null_biomarker": ["ptau"], "population": {"validated": "age >= 50"}},
            },
        },
    ).json()
    assert {o["id"]: o["status"] for o in body["obligations"]} == {
        "units": "DISCHARGED_SYMBOLIC",
        "probe:null_biomarker[ptau]": "DISCHARGED_SYMBOLIC",
        "probe:population": "DISCHARGED_SYMBOLIC",
    }
    bad = api_client.post("/api/biomedical/check", json={"hypothesis": PTAU, "biomedical": {"units": {"x": "g"}}})
    assert bad.status_code == 422
    mech = api_client.post("/api/biomedical/mechanism", json={"mechanism": {"prose": PROSE, "nodes": NODES}}).json()
    assert mech["report"]["compatibility"]["status"] == "DISCHARGED_SYMBOLIC"
    cyc = api_client.post(
        "/api/biomedical/mechanism",
        json={
            "mechanism": {
                "nodes": NODES[:2],
                "links": [
                    {"from": "amyloid", "to": "ptau217", "sign": "+"},
                    {"from": "ptau217", "to": "amyloid", "sign": "+"},
                ],
            }
        },
    )
    assert cyc.status_code == 422


def test_api_chain_with_mechanism_and_biomedical_block(api_client):
    body = api_client.post("/api/chain/run", json={"mechanism": {"prose": PROSE, "nodes": NODES}, "author": "t"}).json()
    assert body["formal_status"] == "DECIDED" and body["steps"][1]["outcome"] == "COMPILED"
    body = api_client.post(
        "/api/chain/run",
        json={"hypothesis": PTAU, "author": "t", "biomedical": {"probes": {"null_biomarker": ["ptau"]}}},
    ).json()
    assert body["domain"]["null_biomarker"][0]["outcome"] == "BIOMARKER_DOES_WORK"


def test_cli_check_mechanism_units_and_vocabulary(tmp_path, capsys):
    req = tmp_path / "req.json"
    req.write_text(
        json.dumps(
            {
                "hypothesis": dict(PTAU, scope="age >= 40"),
                "biomedical": {"probes": {"population": {"validated": "age >= 50"}}},
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    ns = argparse.Namespace(biomedical_command="check", request=str(req), out=str(out))
    assert biomedical_cli.main(ns) == 10
    assert json.loads(out.read_text(encoding="utf-8"))["report"]["population"]["witness"]["age"] == 40
    mech = tmp_path / "mech.json"
    mech.write_text(json.dumps({"mechanism": {"prose": PROSE, "nodes": NODES}}), encoding="utf-8")
    assert biomedical_cli.main(argparse.Namespace(biomedical_command="mechanism", request=str(mech), out=None)) == 0
    mech.write_text(json.dumps({"mechanism": {"prose": "Amyloid modulates x.", "nodes": NODES}}), encoding="utf-8")
    assert biomedical_cli.main(argparse.Namespace(biomedical_command="mechanism", request=str(mech), out=None)) == 11
    assert biomedical_cli.main(argparse.Namespace(biomedical_command="units", a="pg/mL", b="ng/mL")) == 1
    assert biomedical_cli.main(argparse.Namespace(biomedical_command="vocabulary")) == 0
    missing = argparse.Namespace(biomedical_command="check", request=str(tmp_path / "none.json"), out=None)
    assert biomedical_cli.main(missing) == 9
    capsys.readouterr()
