"""Question bank and reference corpus for the hypothesis inspiration protocol (offline; the network is simulated)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import build_question_bank as qb  # noqa: E402
import build_reference_corpus as rc  # noqa: E402


def test_question_bank_has_fifty_unique_questions_per_domain():
    vocabulary = json.loads(qb.VOCABULARY.read_text(encoding="utf-8"))
    questions = qb.build(vocabulary)
    assert len(questions) == 50 * len(vocabulary["domains"])
    per_domain = {}
    for q in questions:
        per_domain[q["domain"]] = per_domain.get(q["domain"], 0) + 1
    assert set(per_domain.values()) == {50}
    assert len({q["text"] for q in questions}) == len(questions)


def test_question_bank_is_deterministic_and_uses_the_template():
    vocabulary = json.loads(qb.VOCABULARY.read_text(encoding="utf-8"))
    first, second = qb.build(vocabulary), qb.build(vocabulary)
    assert first == second
    assert all(q["text"].startswith("Does ") and q["text"].endswith("?") for q in first)
    assert all(q["exposure"] in json.dumps(vocabulary) for q in first)


def test_committed_question_bank_matches_the_vocabulary_it_was_built_from():
    bank = json.loads(qb.BANK.read_text(encoding="utf-8"))
    assert bank["vocabulary_sha256"] == qb._sha256(qb.VOCABULARY)
    assert bank["questions"] == qb.build(json.loads(qb.VOCABULARY.read_text(encoding="utf-8")))


def test_abstract_is_rebuilt_in_order_from_the_inverted_index():
    assert rc.abstract_text({"Tau": [0, 4], "spreads": [1], "along": [2], "hubs": [3]}) == "Tau spreads along hubs Tau"
    assert rc.abstract_text(None) == ""


def test_window_is_inclusive_and_rejects_missing_dates():
    window = {"from": "2025-04-01", "to": "2026-10-14"}
    assert rc.in_window("2025-04-01", window) and rc.in_window("2026-10-14", window)
    assert not rc.in_window("2026-10-15", window) and not rc.in_window(None, window)


class FakeOpenAlex:
    """Answers the three request shapes the corpus builder uses."""

    def __init__(self, extra_citers=0):
        self.extra_citers = extra_citers
        self.calls = []
        self.works = {
            "W1": {
                "id": "https://openalex.org/W1",
                "title": "Anchor",
                "publication_date": "2025-01-01",
                "referenced_works": ["https://openalex.org/W2", "https://openalex.org/W3"],
            },
            "W2": {
                "id": "https://openalex.org/W2",
                "title": "Ref in window",
                "publication_date": "2025-06-01",
                "abstract_inverted_index": {"tau": [0], "spreads": [1]},
            },
            "W3": {"id": "https://openalex.org/W3", "title": "Ref out of window", "publication_date": "2023-01-01"},
            "W4": {"id": "https://openalex.org/W4", "title": "Citer", "publication_date": "2026-02-01"},
        }

    def __call__(self, url, params):
        self.calls.append((url, dict(params)))
        if url.endswith("/works") and "search" in params:
            return {"results": [{"id": "https://openalex.org/W1", "title": "Anchor", "publication_date": "2025-01-01"}]}
        if url.endswith("/works") and str(params.get("filter", "")).startswith("openalex:"):
            ids = params["filter"].split(":", 1)[1].split("|")
            return {"results": [self.works[i] for i in ids if i in self.works]}
        if url.endswith("/works") and str(params.get("filter", "")).startswith("cites:"):
            citers = [self.works["W4"]] + [
                {"id": f"https://openalex.org/W{100 + i}", "title": "c", "publication_date": "2025-09-01"}
                for i in range(self.extra_citers)
            ]
            size, page = params["per-page"], params["page"]
            return {"results": citers[(page - 1) * size : page * size]}
        if "/works/" in url:
            return self.works[url.rsplit("/", 1)[-1]]
        raise AssertionError(f"unexpected request {url} {params}")


@pytest.fixture
def isolated_inspiration(tmp_path, monkeypatch):
    for name in ("ANCHORS", "CORPUS"):
        monkeypatch.setattr(rc, name, tmp_path / f"{name.lower()}.json")
    monkeypatch.setattr(rc, "QUERIES", rc.QUERIES)
    return tmp_path


def test_anchors_are_frozen_once_per_domain(isolated_inspiration):
    fake = FakeOpenAlex()
    payload = rc.select_anchors(fake)
    assert set(payload["anchors"]) == set(json.loads(rc.QUERIES.read_text(encoding="utf-8"))["queries"])
    assert all(v[0]["id"] == "W1" for v in payload["anchors"].values())
    assert rc.ANCHORS.exists() and payload["queries_sha256"] == rc._sha256(rc.QUERIES)


def test_corpus_keeps_only_in_window_works_once_each(isolated_inspiration):
    fake = FakeOpenAlex()
    rc.select_anchors(fake)
    summary = rc.build_corpus(fake)
    rows = [json.loads(line) for line in rc.CORPUS.read_text(encoding="utf-8").splitlines()]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert "W3" not in ids  # outside the window
    assert {"W2", "W4"} <= set(ids)
    w2 = next(r for r in rows if r["id"] == "W2")
    assert w2["source"] == "reference" and w2["abstract"] == "tau spreads" and w2["anchor"] == "W1"
    assert summary["works"] == len(rows) and len(summary["sha256"]) == 64


def test_corpus_requires_anchors_first(isolated_inspiration):
    with pytest.raises(SystemExit):
        rc.build_corpus(FakeOpenAlex())


def test_citations_are_paged_by_number_and_stop_at_the_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "PAGE", 3)
    fake = FakeOpenAlex(extra_citers=6)  # 7 citing works in total
    assert [w["id"] for w in rc._citing(fake, "W1", cap=5)] == [
        f"https://openalex.org/W{i}" for i in [4, 100, 101, 102, 103]
    ]
    pages = [params["page"] for url, params in fake.calls if params.get("filter", "").startswith("cites:")]
    assert pages == [1, 2]  # stops after the second page, which is past the cap
    sizes = {params["per-page"] for _, params in fake.calls if "cites:" in params.get("filter", "")}
    assert sizes == {3}  # one page size throughout
    assert all(
        params.get("sort") == "cited_by_count:desc" for _, params in fake.calls if "cites:" in params.get("filter", "")
    )
