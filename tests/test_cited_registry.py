"""Cited-results registry and premise retraction (ADR-DISCOVERY-083).

Calibration fixtures:
- openai/math withdrawals: a trace sign imported from a cited lemma under the opposite orientation convention
  (docs/reference/benchmarks/openai_math_revision_dataset.json, group "withdrawn");
- the Exponential Time Hypothesis as a premise (openai/math family 378);
- a biomarker cutoff validated under one assay and population and applied under another.
"""

import argparse
import json

import pytest

from python.cli import registry as registry_cli
from python.discovery import cited_registry as cr
from python.discovery import manuscript_audit, obligation_ledger

X = [{"name": "x", "continuous": True, "lower": -10, "upper": 10}]


@pytest.fixture()
def reg(tmp_path):
    return cr.Registry(tmp_path / "registry.json")


def _trace_lemma(reg):
    return reg.register(
        {
            "id": "trace-lemma",
            "source": "cited trace lemma used by the Weil-eightfold manuscript (openai/math, withdrawn 2026-10-06)",
            "statement": "A reverse stabilization trace contributes sign (-1)^k to the signed double-point count",
            "key": "TraceLemma",
            "locator": "Lemma 2.3",
            "conventions": {
                "sign": {
                    "text": "cusp branches with matching source orientations",
                    "fields": {"cusp_branch_source_orientations": "matching"},
                }
            },
            "hypotheses": [
                {
                    "text": "the cusp branches have matching source orientations",
                    "phrases": ["matching source orientations"],
                }
            ],
        }
    )


# --- M6: conventions and hypotheses at the seams ---------------------------------------------------------------


def test_withdrawal_pattern_sign_convention_mismatch_is_a_finding(reg):
    entry = _trace_lemma(reg)
    context = {
        "conventions": {"sign": {"fields": {"cusp_branch_source_orientations": "opposite"}}},
        "text": "with the opposite source orientations of the cusp branches, by Lemma 2.3 ...",
    }
    check = cr.cite_check(entry, context)
    assert check["outcome"] == cr.FINDINGS
    assert check["conventions"][0]["outcome"] == cr.MISMATCH
    assert any("field cusp_branch_source_orientations" in f for f in check["findings"])
    # The phrase is absent, so the hypothesis is not even stated; it is never treated as discharged.
    assert check["hypotheses"][0]["outcome"] == cr.H_UNDECIDED


def test_untyped_convention_texts_that_differ_are_uncompared_not_findings(reg):
    """ADR-087: a different wording is not evidence of a different convention."""
    entry = _trace_lemma(reg)
    context = {"conventions": {"sign": "the branches of the cusp are oriented oppositely at the source"}}
    check = cr.cite_check(entry, context)
    assert check["conventions"][0]["outcome"] == cr.UNCOMPARED
    assert check["outcome"] == cr.INCOMPLETE and not check["findings"]
    assert "sign" in check["open"]


def test_sign_formulas_are_compared_exhaustively(reg):
    entry = reg.register(
        {
            "id": "trace-sign",
            "source": "s",
            "statement": "t",
            "conventions": {"sign": {"signs": {"reverse_trace": "(-1)**k"}, "params": {"k": [1, 12]}}},
        }
    )
    same = cr.cite_check(entry, {"conventions": {"sign": {"signs": {"reverse_trace": "-(-1)**(k-1)"}}}})
    assert same["conventions"][0]["outcome"] == cr.MATCH and same["outcome"] == cr.CLEAR
    other = cr.cite_check(entry, {"conventions": {"sign": {"signs": {"reverse_trace": "1"}}}})
    assert other["outcome"] == cr.FINDINGS
    item = other["conventions"][0]["items"][0]
    assert item["counterexample"]["at"] == {"k": 1} and item["counterexample"]["cited"] == -1


def test_partial_typed_match_is_open_not_clear(reg):
    """ADR-088: the compared items agree, but the cited side states an orientation the citing side is silent on."""
    entry = reg.register(
        {
            "id": "trace-sign-orient",
            "source": "s",
            "statement": "t",
            "conventions": {
                "sign": {"signs": {"reverse_trace": "(-1)**k"}, "fields": {"branch_orientations": "matching"}}
            },
        }
    )
    check = cr.cite_check(entry, {"conventions": {"sign": {"signs": {"reverse_trace": "(-1)**k"}}}})
    assert check["conventions"][0]["outcome"] == cr.PARTIAL
    assert check["outcome"] == cr.INCOMPLETE
    assert "sign: field branch_orientations (citing side silent)" in check["open"]


def test_case_scoped_hypothesis_applies_only_to_its_case(reg):
    """ADR-089: a citation that uses part (2) of a result is not held to the hypothesis of part (1)."""
    entry = reg.register(
        {
            "id": "two-part",
            "source": "s",
            "statement": "t",
            "conventions": {"indexing": {"text": "parts", "cases": {"part": ["1", "2"]}}},
            "hypotheses": [
                {"text": "part (1) needs x < 0", "formal": "x < 0", "case": {"part": ["1"]}},
                {"text": "x is bounded", "formal": "x <= 10"},
            ],
        }
    )
    context = {"variables": X, "assumptions": ["x > 2"], "conventions": {"indexing": {"case": {"part": "2"}}}}
    check = cr.cite_check(entry, context)
    assert [h["outcome"] for h in check["hypotheses"]] == [cr.H_NOT_APPLICABLE, cr.DISCHARGED]
    assert check["outcome"] == cr.CLEAR
    silent = cr.cite_check(entry, {"variables": X, "assumptions": ["x > 2"]})
    assert silent["hypotheses"][0]["outcome"] == cr.NOT_DISCHARGED  # no case named: the hypothesis is checked


def test_malformed_typed_convention_is_refused(reg):
    with pytest.raises(cr.RegistryError):
        reg.register(
            {"id": "bad", "source": "s", "statement": "t", "conventions": {"sign": {"signs": {"a": "2**x()"}}}}
        )


def test_matching_convention_with_only_a_phrase_is_incomplete_not_clear(reg):
    entry = _trace_lemma(reg)
    context = {
        "conventions": {"sign": "Cusp branches with  matching source orientations"},
        "text": "the branches have matching source orientations, so Lemma 2.3 applies",
    }
    check = cr.cite_check(entry, context)
    assert check["conventions"][0]["outcome"] == cr.MATCH  # case and whitespace are normalized
    assert check["hypotheses"][0]["outcome"] == cr.STATED_IN_TEXT
    assert check["outcome"] == cr.INCOMPLETE
    assert check["formal_status"] == "UNDECIDED"


def test_missing_convention_is_unspecified_never_a_match(reg):
    check = cr.cite_check(_trace_lemma(reg), {})
    assert check["conventions"][0]["outcome"] == cr.UNSPECIFIED
    assert check["outcome"] == cr.INCOMPLETE


def test_formal_hypothesis_discharged_only_by_entailment(reg):
    entry = reg.register(
        {
            "id": "lemma-pos",
            "source": "test",
            "statement": "s",
            "hypotheses": [{"text": "x is positive", "formal": "x > 0"}],
        }
    )
    ok = cr.cite_check(entry, {"variables": X, "assumptions": ["x > 1"]})
    assert ok["outcome"] == cr.CLEAR and ok["hypotheses"][0]["outcome"] == cr.DISCHARGED
    bad = cr.cite_check(entry, {"variables": X, "assumptions": ["x > -1"]})
    assert bad["outcome"] == cr.FINDINGS
    assert bad["hypotheses"][0]["outcome"] == cr.NOT_DISCHARGED
    assert bad["hypotheses"][0]["counterexamples"]
    none = cr.cite_check(entry, {"assumptions": ["x > 1"]})  # no variables declared
    assert none["hypotheses"][0]["outcome"] == cr.H_UNDECIDED and none["outcome"] == cr.INCOMPLETE
    contradictory = cr.cite_check(entry, {"variables": X, "assumptions": ["x > 1", "x < 0"]})
    assert contradictory["hypotheses"][0]["outcome"] == cr.H_UNDECIDED


def test_cite_check_carries_provenance(reg):
    entry = reg.register({"id": "p", "source": "s", "statement": "t"})
    check = cr.cite_check(entry, {})
    assert check["provenance"]["operation"] == "cite_check"
    assert check["provenance"]["input_sha256"] and check["provenance"]["output_sha256"]


def test_ledger_obligation_only_discharged_when_clear_and_formal(reg):
    entry = reg.register(
        {
            "id": "lemma-pos",
            "source": "test",
            "statement": "s",
            "hypotheses": [{"text": "x is positive", "formal": "x > 0"}],
        }
    )
    clear = cr.cite_check(entry, {"variables": X, "assumptions": ["x > 1"]})
    assert cr.to_obligation(clear, "O1", "sec 2").status == obligation_ledger.Status.DISCHARGED_SYMBOLIC
    findings = cr.cite_check(entry, {"variables": X, "assumptions": ["x > -1"]})
    obligation = cr.to_obligation(findings, "O2", "sec 3")
    assert obligation.status == obligation_ledger.Status.OPEN  # a failed transfer is not a refutation


# --- M11: premise retraction -----------------------------------------------------------------------------------


def test_eth_retraction_flags_every_transitive_dependent(reg):
    reg.register(
        {
            "id": "ETH",
            "source": "Impagliazzo-Paturi 2001",
            "kind": "premise",
            "statement": "3-SAT on n variables needs 2^{Omega(n)} time",
            "rung": "STATEMENT_PUBLIC",
        }
    )
    reg.depend("hardness-of-X", "ETH")
    reg.depend("corollary-of-X", "hardness-of-X")
    reg.depend("unrelated", "other-premise")
    impact = reg.impact("ETH")
    assert impact["dependents"] == ["corollary-of-X", "hardness-of-X"]
    out = reg.retract("ETH", "openai/math family 378: deterministic 2^{o(n)} exact #k-SAT", when="2026-10-25")
    assert out["flagged"] == ["corollary-of-X", "hardness-of-X"]
    assert "unrelated" not in reg.flags
    assert reg.get("ETH").status == cr.RETRACTED and reg.get("ETH").version == 2
    assert reg.effective_rung("corollary-of-X", "KERNEL_CHECKED") == "CLAIMED"
    assert reg.effective_rung("unrelated", "KERNEL_CHECKED") == "KERNEL_CHECKED"
    # A retracted premise turns every later citation of it into a finding.
    assert cr.cite_check(reg.get("ETH"), {})["outcome"] == cr.FINDINGS
    reg.reevaluated("hardness-of-X", "re-derived without ETH from a different assumption")
    assert reg.effective_rung("hardness-of-X", "STATEMENT_AUDITED") == "STATEMENT_AUDITED"


def test_withdrawal_propagates_to_manuscripts_that_adapted_the_step(reg):
    _trace_lemma(reg)
    reg.depend("Weil-eightfolds", "trace-lemma")
    reg.depend("Kuga-Satake-K3", "Weil-eightfolds")
    reg.depend("Hodge-products-K3", "Weil-eightfolds")
    out = reg.retract("trace-lemma", "sign of reverse traces is -1 under the opposite source orientation")
    assert out["flagged"] == ["Hodge-products-K3", "Kuga-Satake-K3", "Weil-eightfolds"]


def test_downgrade_must_go_down_and_needs_a_reason(reg):
    reg.register({"id": "T", "source": "s", "statement": "t", "rung": "KERNEL_CHECKED"})
    with pytest.raises(cr.RegistryError):
        reg.retract("T", "  ")
    with pytest.raises(cr.RegistryError):
        reg.retract("T", "why", downgrade_to="INDEPENDENTLY_REPRODUCED")
    out = reg.retract("T", "kernel log lost", downgrade_to="STATEMENT_AUDITED")
    assert out["entry"]["status"] == cr.DOWNGRADED and out["entry"]["rung"] == "STATEMENT_AUDITED"


def test_cycles_are_refused(reg):
    reg.depend("a", "b")
    reg.depend("b", "c")
    with pytest.raises(cr.RegistryError):
        reg.depend("c", "a")
    with pytest.raises(cr.RegistryError):
        reg.depend("a", "a")


# --- Biomedical transfer -----------------------------------------------------------------------------------------


def test_biomarker_cutoff_applied_outside_its_validation_is_flagged(reg):
    entry = reg.register(
        {
            "id": "ptau217-cutoff",
            "source": "illustrative threshold entry (not a clinical value)",
            "kind": "threshold",
            "statement": "plasma pTau217 above the cutoff classifies amyloid positivity",
            "conventions": {
                "validated_assay": "assay A",
                "validated_population": "memory clinic, 55-80 y",
                "units": "pg/mL",
            },
            "hypotheses": [{"text": "age within the validated range", "formal": "age >= 55 and age <= 80"}],
        }
    )
    citing = {
        "conventions": {
            "validated_assay": "assay B",
            "validated_population": "memory clinic, 55-80 y",
            "units": "pg/mL",
        },
        "variables": [{"name": "age", "continuous": True, "lower": 40, "upper": 95}],
        "assumptions": ["age >= 60", "age <= 75"],
    }
    check = cr.cite_check(entry, citing)
    assert check["outcome"] == cr.FINDINGS
    assert [c["tag"] for c in check["conventions"] if c["outcome"] == cr.MISMATCH] == ["validated_assay"]
    assert check["hypotheses"][0]["outcome"] == cr.DISCHARGED
    wider = dict(citing, conventions=dict(citing["conventions"], validated_assay="assay A"), assumptions=["age >= 50"])
    assert cr.cite_check(entry, wider)["hypotheses"][0]["outcome"] == cr.NOT_DISCHARGED


# --- Store integrity, versions, manuscript audit, CLI and API ------------------------------------------------------


def test_store_persists_versions_and_refuses_an_edited_log(tmp_path):
    path = tmp_path / "r.json"
    reg = cr.Registry(path)
    reg.register({"id": "E", "source": "s", "statement": "v1"})
    reg.register({"id": "E", "source": "s", "statement": "v2"})
    again = cr.Registry(path)
    assert again.get("E").statement == "v2" and again.get("E", 1).statement == "v1"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["events"][0]["payload"]["id"] = "tampered"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(cr.RegistryError):
        cr.Registry(path)


def test_entries_feed_the_manuscript_audit(reg):
    _trace_lemma(reg)
    tex = (
        "\\begin{proof} The branches have matching source orientations, "
        "so by \\cite[Lemma 2.3]{TraceLemma} the reverse trace has sign $(-1)^k$. \\end{proof}\n"
    )
    bib = "@article{TraceLemma, title={Traces}}\n"
    report = manuscript_audit.audit({"main.tex": tex, "refs.bib": bib}, reg.as_import_list())
    matches = [i for i in report["imports"] if i["kind"] == "HYPOTHESIS_MATCH"]
    assert matches and matches[0]["outcome"] == "MATCHED"


def test_cli_round_trip(tmp_path, capsys):
    store = tmp_path / "cli.json"
    entry = tmp_path / "entry.json"
    entry.write_text(
        json.dumps({"id": "L", "source": "s", "statement": "t", "hypotheses": [{"text": "pos", "formal": "x > 0"}]}),
        encoding="utf-8",
    )
    context = tmp_path / "ctx.json"
    context.write_text(json.dumps({"variables": X, "assumptions": ["x > -1"]}), encoding="utf-8")

    def run(*argv):
        ns = argparse.Namespace(store=str(store), registry_command=argv[0])
        for k, v in argv[1].items():
            setattr(ns, k, v)
        return registry_cli.main(ns)

    assert run("register", {"entry": str(entry)}) == 0
    assert run("cite-check", {"id": "L", "context": str(context), "version": None}) == registry_cli.EXIT_FINDINGS
    assert run("depend", {"node": "C", "on": "L"}) == 0
    assert run("retract", {"id": "L", "reason": "wrong", "downgrade_to": None, "date": None}) == 0
    assert run("show", {"id": "L", "version": None}) == 0
    assert run("show", {"id": "missing", "version": None}) == registry_cli.EXIT_REFUSED
    capsys.readouterr()


def test_api_register_check_retract_impact(api_client):
    r = api_client.post(
        "/api/registry/entries",
        json={
            "id": "api-lemma",
            "source": "s",
            "statement": "t",
            "hypotheses": [{"text": "pos", "formal": "x > 0"}],
            "conventions": {"sign": {"signs": {"orientation": "1"}}},
        },
    )
    assert r.status_code == 200, r.text
    r = api_client.post(
        "/api/registry/cite-check",
        json={
            "entry_id": "api-lemma",
            "context": {
                "variables": X,
                "assumptions": ["x > 2"],
                "conventions": {"sign": {"signs": {"orientation": "-1"}}},
            },
        },
    )
    assert r.status_code == 200 and r.json()["outcome"] == "FINDINGS"
    assert (
        api_client.post("/api/registry/dependencies", json={"node": "api-claim", "depends_on": "api-lemma"}).status_code
        == 200
    )
    r = api_client.post("/api/registry/entries/api-lemma/retract", json={"reason": "sign convention"})
    assert r.status_code == 200 and r.json()["flagged"] == ["api-claim"]
    assert api_client.get("/api/registry/impact/api-lemma").json()["count"] == 1
    assert api_client.get("/api/registry/entries/nope").status_code == 404
    r = api_client.post("/api/registry/flags/api-claim/reevaluated", json={"note": "re-checked"})
    assert r.status_code == 200
