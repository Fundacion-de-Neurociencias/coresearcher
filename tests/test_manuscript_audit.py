"""Tests for ADR-DISCOVERY-082: the manuscript audit as a service, in the two-phase CLI and in the API."""

import argparse
import json
from pathlib import Path

import pytest

from python.cli import formal as formal_cli
from python.discovery import formal_pipeline, manuscript_audit
from python.discovery.formal_hypothesis import FormalHypothesisError

# A trace-sign import inside a proof, a cited corollary applied in a proof, and a citation with no entry.
# A blank line separates the two proofs: the frozen ADR-077 sentence window stops at a paragraph break, not at
# \end{proof} (a known limitation recorded in ADR-082).
MAIN = r"""
\begin{corollary}\label{cor:cones}
Let $X,J$ be as above. Then $K^t = K^c + H^-$.
\end{corollary}
\begin{proof}
The cone comparison \cite[Corollary~1.1]{LZ} gives the cone identity.
\end{proof}

\begin{proof}
We use the stabilization traces of \cite[Lemma~3.2]{eems}. In source dimension $2k$, a trace
has one double point of sign $(-1)^{k-1}$; the reverse trace has sign $(-1)^k$.
\end{proof}
The starting constructions are in \cite{B,Dv}.
"""
BIB = "@article{LZ, title={a}}\n@article{eems, title={b}}\n@article{B, title={c}}\n"
FILES = {"main.tex": MAIN, "refs.bib": BIB}
REGISTRY = [
    {
        "key": "LZ",
        "locator": "Corollary 1.1",
        "statement": "K^t = K^c + H^- for tamed J",
        "hypotheses": [{"text": "h_J^- = b^+ - 1", "phrases": ["h_J^- = b^+ - 1", "h_J^-=b^+-1"]}],
    }
]


def _codes(report):
    return {r["code"] for r in report["mandatory_relays"]}


def test_audit_reports_gate_imports_and_relays():
    report = manuscript_audit.audit(FILES)
    gate = report["citation_gate"]
    assert gate["status"] == "FAIL" and [u["key"] for u in gate["unresolved"]] == ["cite:Dv"]
    assert report["import_counts"]["CONVENTION_TRANSFER"] == 1
    assert report["import_counts"]["HYPOTHESIS_MATCH"] == 2
    assert report["hypothesis_outcomes"] == {"MATCHED": 0, "UNMATCHED": 0, "NO_ENTRY": 2}
    assert report["ledger_status"] == "OPEN" and report["open_obligations"] == len(report["imports"])
    assert report["formal_status"] == "DECIDED"
    assert _codes(report) == {"IMPORTS_ARE_LEXICAL", "IMPORT_OBLIGATIONS_OPEN", "CITATIONS_UNRESOLVED"}
    assert report["provenance"]["operation"] == "manuscript_audit"


def test_registry_hypotheses_are_literal_phrases():
    report = manuscript_audit.audit(FILES, registry=REGISTRY)
    lz = next(i for i in report["imports"] if i["kind"] == "HYPOTHESIS_MATCH" and i["key"] == "LZ")
    assert lz["outcome"] == "UNMATCHED" and lz["missing"] == ["h_J^- = b^+ - 1"]
    stated = dict(FILES, **{"main.tex": MAIN.replace("as above.", "as above with $h_J^- = b^+ - 1$.")})
    imports = manuscript_audit.audit(stated, registry=REGISTRY)["imports"]
    lz = next(i for i in imports if i["kind"] == "HYPOTHESIS_MATCH" and i["key"] == "LZ")
    assert lz["outcome"] == "MATCHED"
    # A phrase is never a regular expression: "(a+)+$" matches only itself.
    tricky = [dict(REGISTRY[0], hypotheses=[{"text": "t", "phrases": ["(a+)+$"]}])]
    imports = manuscript_audit.audit(FILES, registry=tricky)["imports"]
    lz = next(i for i in imports if i["kind"] == "HYPOTHESIS_MATCH" and i["key"] == "LZ")
    assert lz["outcome"] == "UNMATCHED"


def test_no_bibliography_is_a_non_verdict():
    report = manuscript_audit.audit({"main.tex": "See \\cite{A}.\n"})
    assert report["citation_gate"]["status"] == "NO_BIBLIOGRAPHY"
    assert report["formal_status"] == "UNDECIDED" and report["undecided_reasons"]


def test_dependencies_and_collection_links():
    files = {"main.tex": "x\n", "refs.bib": "@misc{w, howpublished={OAI:Weil-paper-May-1-2026}}\n"}
    report = manuscript_audit.audit(files, manuscript_status={"Weil-paper-May-1-2026": "withdrawn"})
    assert [(i["kind"], i["outcome"]) for i in report["imports"]] == [("DEPENDENCY", "withdrawn")]
    missing = manuscript_audit.audit(files, collection=["Other-paper-May-2-2026"])
    assert missing["citation_gate"]["status"] == "FAIL"


def test_audit_is_deterministic_and_validates_input():
    a, b = manuscript_audit.audit(FILES), manuscript_audit.audit(dict(reversed(list(FILES.items()))))
    assert a["provenance"]["output_sha256"] == b["provenance"]["output_sha256"]
    for bad in ({}, {"main.py": "x"}, {"refs.bib": BIB}):
        with pytest.raises(FormalHypothesisError):
            manuscript_audit.audit(bad)
    with pytest.raises(FormalHypothesisError):
        manuscript_audit.audit(FILES, registry=[{"key": "LZ", "locator": "C1", "hypotheses": [{"text": "t"}]}])


def test_claim_trust_view_keeps_prose_claims_claimed():
    view = manuscript_audit.claim_trust(manuscript_audit.audit(FILES), "main theorem")
    assert view["claim_trust"][0]["rung"] == "CLAIMED"
    assert {r["code"] for r in view["mandatory_relays"]} == {"CLAIM_BELOW_KERNEL_CHECKED"}


# ---------------------------------------------------------------------------
# Two-phase CLI
# ---------------------------------------------------------------------------


def _cli(argv):
    parser = argparse.ArgumentParser()
    formal_cli.add_parser(parser.add_subparsers(dest="command"))
    return formal_cli.main(parser.parse_args(argv))


def _sources(tmp_path: Path) -> Path:
    src = tmp_path / "paper" / "build"
    (src / "sections").mkdir(parents=True)
    (src / "sections" / "main.tex").write_text(MAIN, encoding="utf-8")
    (src / "refs.bib").write_text(BIB, encoding="utf-8")
    (src / "notes.txt").write_text("not a source", encoding="utf-8")
    return src


def test_formal_manuscript_is_two_phase(tmp_path, capsys):
    out = tmp_path / "raw"
    assert _cli(["formal", "manuscript", "--dir", str(_sources(tmp_path)), "--out", str(out), "--name", "ms"]) == 0
    meta = json.loads((out / "ms.meta.json").read_text(encoding="utf-8"))
    assert meta["subcommand"] == "formal manuscript" and "files" not in meta["parameters"]
    assert meta["claim_trust"][0]["rung"] == "CLAIMED"
    request = json.loads((out / "ms.request.json").read_text(encoding="utf-8"))
    assert sorted(request["files"]) == ["refs.bib", "sections/main.tex"]
    capsys.readouterr()
    assert _cli(["formal", "analyze", str(out / "ms.meta.json")]) == 0
    assert "manuscript_audit.citation_gate=FAIL" in capsys.readouterr().out
    analysis = json.loads((out / "ms.analysis.json").read_text(encoding="utf-8"))
    assert analysis["assessment"]["reproduces_run"] is True
    assert [d["report"] for d in formal_pipeline.report_digests(analysis)] == ["manuscript_audit"]


def test_formal_manuscript_refuses_missing_or_empty_directories(tmp_path):
    out = str(tmp_path / "raw")
    assert _cli(["formal", "manuscript", "--dir", str(tmp_path / "missing"), "--out", out]) == 3
    (tmp_path / "empty").mkdir()
    assert _cli(["formal", "manuscript", "--dir", str(tmp_path / "empty"), "--out", out]) == 9


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


def test_api_manuscript_audit(api_client):
    body = api_client.post("/api/manuscripts/audit", json={"files": FILES, "registry": REGISTRY}).json()
    assert body["citation_gate"]["status"] == "FAIL"
    assert body["hypothesis_outcomes"]["UNMATCHED"] == 1
    assert body["claim_trust"][0]["rung"] == "CLAIMED"
    assert api_client.post("/api/manuscripts/audit", json={"files": {"a.py": "x"}}).status_code == 422


def test_manuscript_audit_is_catalogued_as_read_only_and_deterministic(api_client):
    catalogue = {(c["method"], c["path"]): c for c in api_client.get("/api/capabilities").json()["capabilities"]}
    entry = catalogue[("POST", "/api/manuscripts/audit")]
    assert entry["operationClass"] == "READ_ONLY" and entry["determinism"] == "DETERMINISTIC"
