"""Tests for the openai/math strategy case (python/discovery/openai_math_strategy.py). Offline: no network."""

import json
from pathlib import Path

from python.discovery import openai_math_strategy as oms

STATS = Path(__file__).resolve().parent.parent / "examples" / "openai-math-strategy" / "corpus_stats.json"

OVERVIEW = r"""
\cataloguesection{Number theory}{1}
\resultentry{001}{A {nested} title}{Proves something about $\{x\}$.}{\href{https://github.com/openai/math/blob/main/preprints/Paper-A-September-24-2026/paper.pdf}{A}\enspace\href{https://github.com/openai/math/blob/main/preprints/Paper-B-October-5-2026/main.pdf}{B}}
\cataloguesection{Algebra}{2}
\resultentry{002}{Second}{Disproves a conjecture.}{\href{https://github.com/openai/math/blob/main/preprints/Paper-C-September-23-2026/paper.pdf}{C}}
"""


def test_parse_overview_handles_nested_braces_and_disciplines():
    fams = oms.parse_overview(OVERVIEW)
    assert [f["num"] for f in fams] == ["001", "002"]
    assert fams[0]["title"] == "A {nested} title"
    assert fams[0]["discipline"] == "Number theory" and fams[1]["discipline"] == "Algebra"
    assert [m["date"] for m in fams[0]["manuscripts"]] == ["September 24", "October 5"]
    assert fams[1]["lead_verb"] == "Disproves"


def test_citation_edges_read_oai_keys_and_drop_self_citations():
    bib = "howpublished = {OpenAI Math Release preprint OAI:Paper-B-October-5-2026}"
    self_bib = "OAI:Paper-A-September-24-2026"
    edges = oms.citation_edges({"Paper-A-September-24-2026": [bib, self_bib]})
    assert edges == {"Paper-A-September-24-2026": {"Paper-B-October-5-2026"}}


def test_scc_and_longest_chain():
    edges = {"a": {"b"}, "b": {"a", "c"}, "c": {"d"}, "e": set()}
    comps = oms.strongly_connected_components(edges)
    assert {frozenset(c) for c in comps if len(c) > 1} == {frozenset({"a", "b"})}
    assert oms.longest_chain(edges) == 3  # {a,b} -> c -> d


def test_corpus_stats_on_a_toy_corpus():
    fams = oms.parse_overview(OVERVIEW)
    edges = {"Paper-B-October-5-2026": {"Paper-A-September-24-2026", "Paper-C-September-23-2026"}}
    stats = oms.corpus_stats(fams, edges, {"Paper-C-September-23-2026"}, dirs_with_bib=1)
    c = stats["citations"]
    assert c["edges"] == 2 and c["intra_family_edges"] == 1 and c["cross_discipline_pairs"] == 1
    assert c["direction"] == {"earlier": 2}
    assert stats["formalization"]["families_with_formalized_paper"] == 1
    assert stats["formalization"]["negative_or_constructive_formalized"] == 1


def test_trace_coding_is_complete_and_consistent():
    assert len(oms.TRACES) == 10
    assert len({t["family"] for t in oms.TRACES}) == 10
    for t in oms.TRACES:
        assert 0 <= t["audit_share"] <= 1 and t["abandoned_routes"] > 0
        assert t["pivot"] and t["endgame"] and t["opening"]
    agg = oms.trace_aggregates()
    assert agg["positivity_or_sign_pivot"] == 7
    assert agg["builds_on_own_output"] == 2
    assert agg["decision_form_prompts"] >= 7


def test_committed_stats_match_the_code_and_the_pinned_commit():
    stats = json.loads(STATS.read_text(encoding="utf-8"))
    assert stats["commit"] == oms.COMMIT
    assert stats["families"] == 373 and stats["manuscripts"] == 721
    assert stats["traces"] == oms.trace_aggregates()
    c = stats["citations"]
    assert c["intra_family_edges"] <= c["edges"] and c["cross_discipline_pairs"] <= c["cross_family_pairs"]
    assert sum(c["direction"].values()) == c["edges"]
    counts = stats["trace_text_counts"]
    assert set(counts) == {t["file"] for t in oms.TRACES}
    assert counts["irrationality-exponent-of-pi"]["verbatim_excerpts"] == 69
