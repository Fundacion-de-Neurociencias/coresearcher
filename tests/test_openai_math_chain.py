"""Tests for the openai/math chain re-run helpers (OPENAI_MATH_CHAIN_PROTOCOL.md)."""

from pathlib import Path

from python.discovery import cited_registry, freeze_service, verification_chain
from python.discovery import openai_math_chain as omc

BIB = r"""
\begin{thebibliography}{9}
\bibitem{LZ} T.-J. Li and W. Zhang, \emph{Comparing tamed and compatible symplectic cones}, CAG 2009.
\end{thebibliography}
"""

TEX = r"""
\begin{corollary}
For every tamed $J$, the cones agree.
\end{corollary}
\begin{proof}
This follows from \cite[Corollary~1.1]{LZ}
and \cite[Lemma~3.2 and proof of Lemma~3.4]{LZ}.
\end{proof}
"""


def test_results_in_splits_compound_locators():
    assert omc.results_in("Lemma~3.2 and proof of Lemma~3.4") == ["Lemma 3.2", "Lemma 3.4"]
    assert omc.results_in("Theorems 2.1, 2.3 and 2.5") == ["Theorem 2.1", "Theorem 2.3", "Theorem 2.5"]
    assert omc.results_in("Section~3, p.~182") == []


def test_occurrences_resolve_titles_and_split_results():
    occs = omc.occurrences({"main.tex": TEX + BIB})
    refs = sorted(o["ref"] for o in occs)
    assert refs == ["Corollary 1.1", "Lemma 3.2", "Lemma 3.4"]
    assert all(o["result"].startswith("comparingtamedandcompatiblesymplecticcones|") for o in occs)
    assert sorted({(o["file"], o["line"]) for o in occs}) == [("main.tex", 6), ("main.tex", 7)]


def _run(context, tmp_path: Path):
    reg = cited_registry.Registry(tmp_path / "registry.json")
    reg.register(
        {
            "id": "LZ09-C1.1",
            "source": "Li-Zhang 2009",
            "statement": "If h = b - 1 the cones agree",
            "hypotheses": [{"text": "h = b - 1", "formal": "h == b - 1", "phrases": ["h = b - 1"]}],
            "conventions": {"sign": "standard orientation"},
        }
    )
    store = freeze_service.FreezeStore(tmp_path / "freezes.json")
    request = omc.chain_request(context, "LZ09-C1.1", "by Corollary 1.1")
    return omc.chain_record(verification_chain.run(request, store, reg))


def test_chain_finds_undischarged_hypothesis(tmp_path):
    context = {
        "id": "o1",
        "variables": [{"name": "h", "domain": [0, 1, 2]}, {"name": "b", "domain": [1, 2, 3]}],
        "assumptions": [],
        "conventions": {"sign": "standard orientation"},
    }
    record = _run(context, tmp_path)
    assert record["formal_status"] == "DECIDED"
    assert record["seams_outcome"] == "FINDINGS"
    assert record["hypotheses"] == [["h = b - 1", "NOT_DISCHARGED"]]


def test_context_without_variables_uses_placeholder_and_stays_incomplete(tmp_path):
    record = _run({"id": "o2", "variables": [], "assumptions": [], "conventions": {}}, tmp_path)
    assert record["formal_status"] == "DECIDED"
    assert record["seams_outcome"] == "INCOMPLETE"


def test_score_defect_requires_resolution_on_corrected_version():
    item = {"id": "M", "group": "revised", "locations": {"a.tex": [[10, 12]]}}
    flag = {"seams_outcome": "FINDINGS", "findings": ["hypothesis not discharged: h = b - 1"]}
    pre = {
        "item": "M",
        "version": "pre",
        "file": "a.tex",
        "line": 11,
        "result": "r|Lemma 1",
        "occ": "o1",
        "chain": flag,
    }
    post_same = dict(pre, version="post", occ="o2")
    post_clear = dict(pre, version="post", occ="o3", chain={"seams_outcome": "CLEAR", "findings": []})
    hit = omc.score_defect(item, [pre, post_clear], ["CHAIN_SEAMS"], 100)
    assert hit["per_check"]["CHAIN_SEAMS"]["verdict"] == "HIT"
    persistent = omc.score_defect(item, [pre, post_same], ["CHAIN_SEAMS"], 100)
    assert persistent["per_check"]["CHAIN_SEAMS"]["verdict"] == "MISS"
    assert persistent["per_check"]["REGISTRY_AUDIT"]["verdict"] == "NOT_ENCODABLE"
    assert persistent["verdict"] == "MISS"


def test_registry_entries_copy_per_bibliography_key():
    written = [
        {
            "status": "WRITTEN",
            "result": "t|Lemma 1",
            "ref": "Lemma 1",
            "entry_id": "X-L1",
            "source": "X",
            "entry": {"statement": "s", "hypotheses": [], "conventions": {}, "variables": {}},
        },
        {"status": "UNAVAILABLE", "result": "u|Lemma 2", "ref": "Lemma 2"},
    ]
    entries = omc.registry_entries(written, {"t|Lemma 1": ["A", "B"]})
    assert [(e["id"], e.get("key")) for e in entries] == [("X-L1", None), ("X-L1.k1", "A"), ("X-L1.k2", "B")]
    assert all("variables" not in e for e in entries)
