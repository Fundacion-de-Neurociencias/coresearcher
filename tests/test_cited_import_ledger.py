"""Tests for python/discovery/cited_import_ledger.py and scripts/checks/citation_gate.py (synthetic inputs only)."""

import importlib.util
from pathlib import Path

from python.discovery import cited_import_ledger as cil
from python.discovery import obligation_ledger

ROOT = Path(__file__).resolve().parent.parent

TRACE = r"""
\begin{proof}
Remove the center of the ball.
We use the stabilization traces of \cite[Lemma~3.2]{eems}. In source dimension $2k$, a trace
has one double point of sign $(-1)^{k-1}$; the reverse trace has sign $(-1)^k$.
\end{proof}
"""

CONE = r"""
\begin{corollary}\label{cor:cones}
Let $X,J$ be as above. Then $K^t = K^c + H^-$.
\end{corollary}
\begin{proof}
The cone comparison \cite[Corollary~1.1]{LZ} gives the cone identity.
\end{proof}
"""

REGISTRY = {
    "LZ": [
        cil.CitedResult(
            key="LZ",
            locator="Corollary 1.1",
            statement="K^t = K^c + H^- for tamed J on a four-manifold",
            hypotheses=[
                cil.Hypothesis("compatible cone nonempty", r"compatible|K\^c"),
                cil.Hypothesis("h_J^- = b^+ - 1", r"h_J\^-\s*=\s*b"),
            ],
        )
    ]
}


def test_convention_transfer_at_imported_sign():
    imports = cil.scan({"t.tex": TRACE})
    conv = [i for i in imports if i.kind == cil.CONVENTION_TRANSFER]
    assert [(i.key, i.line, i.environment) for i in conv] == [("eems", 4, "proof")]


def test_hypothesis_match_without_registry_is_no_entry():
    imports = cil.scan({"c.tex": CONE})
    hyp = [i for i in imports if i.kind == cil.HYPOTHESIS_MATCH]
    assert len(hyp) == 1 and hyp[0].outcome == cil.NO_ENTRY and hyp[0].line == 6


def test_hypothesis_match_reports_missing_hypothesis():
    hyp = [i for i in cil.scan({"c.tex": CONE}, registry=REGISTRY) if i.kind == cil.HYPOTHESIS_MATCH]
    assert hyp[0].outcome == cil.UNMATCHED
    assert hyp[0].missing == ["h_J^- = b^+ - 1"]
    stated = CONE.replace("Let $X,J$ be as above.", "Let $X,J$ be as above with $h_J^- = b^+ - 1$.")
    hyp = [i for i in cil.scan({"c.tex": stated}, registry=REGISTRY) if i.kind == cil.HYPOTHESIS_MATCH]
    assert hyp[0].outcome == cil.MATCHED


def test_citation_in_plain_text_is_not_an_import():
    imports = cil.scan({"i.tex": r"Li and Zhang compared the cones \cite[Theorem~1.2]{LZ}." + "\n"})
    assert not [i for i in imports if i.kind == cil.HYPOTHESIS_MATCH]


def test_effective_constant():
    text = "The bound is effective. Its constant $C_{\\alpha,L}$ depends only on $L$.\n"
    imports = cil.scan({"e.tex": text})
    assert [i.kind for i in imports] == [cil.EFFECTIVE_CONSTANT]
    assert not cil.scan({"e.tex": "The bound is effective with constant $S_L=(1+52L^4)^{1/2}$.\n"})


def test_dependency_and_propagation():
    a, b, c = "A-paper-May-1-2026", "B-paper-May-2-2026", "C-paper-May-3-2026"
    files = {"refs.bib": f"@misc{{x, howpublished={{OAI:{a}}}}}\n"}
    dep = cil.scan(files, manuscript_status={a: "withdrawn"})
    assert [(i.kind, i.key, i.outcome) for i in dep] == [(cil.DEPENDENCY, a, "withdrawn")]
    links = {b: {a}, c: {b}, a: set()}
    assert cil.propagate(links, {a: "withdrawn"}) == {b: [a], c: [a]}


def test_ledger_view_keeps_every_import_open():
    imports = cil.scan({"t.tex": TRACE, "c.tex": CONE}, registry=REGISTRY)
    claim = cil.to_claim("C1", "main theorem", imports)
    assert claim.status == obligation_ledger.Status.OPEN
    assert any("h_J^- = b^+ - 1" in o.statement for o in claim.obligations)


def test_citation_gate(tmp_path):
    spec = importlib.util.spec_from_file_location("citation_gate", ROOT / "scripts/checks/citation_gate.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    ok = tmp_path / "ok"
    ok.mkdir()
    (ok / "m.tex").write_text("\\cite{A}\n\\bibitem{A} a\n", encoding="utf-8")
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "m.tex").write_text("\\cite{A,Dv}\n\\bibitem{A} a\n", encoding="utf-8")
    assert gate.gate([str(ok)]) == 0
    assert gate.gate([str(ok), str(bad)]) == 1
