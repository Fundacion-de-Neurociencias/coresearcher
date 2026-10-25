"""Reference check for benchmark protocols (offline; the network is simulated)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import check_references as cr  # noqa: E402

WORK = {"id": "https://openalex.org/W123", "title": "Falsifiable hypotheses: a formal view"}


class FakeOpenAlex:
    """Answers by DOI, the way the works endpoint is called. Unknown DOIs return 404."""

    def __init__(self, works: dict):
        self.works = works
        self.calls = []

    def __call__(self, url: str):
        self.calls.append(url)
        doi = url.rsplit("/works/doi:", 1)[-1]
        if doi in self.works:
            return 200, self.works[doi]
        return 404, None


def test_matching_title_is_verified():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    row = cr.check({"key": "R1", "doi": "10.1000/abc", "title": "Falsifiable hypotheses: a formal view"}, fake)
    assert row["status"] == "VERIFIED"
    assert row["openalex_id"] == "W123"


def test_title_comparison_ignores_case_and_punctuation():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    row = cr.check({"key": "R1", "doi": "10.1000/abc", "title": "FALSIFIABLE hypotheses -- a formal view."}, fake)
    assert row["status"] == "VERIFIED"


def test_different_title_under_a_real_doi_is_a_mismatch():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    row = cr.check({"key": "R2", "doi": "10.1000/abc", "title": "A different paper"}, fake)
    assert row["status"] == "MISMATCH"
    assert row["openalex_title"] == WORK["title"]


def test_unknown_doi_is_not_found_and_kept():
    fake = FakeOpenAlex({})
    row = cr.check({"key": "R3", "doi": "10.9999/none", "title": "Any"}, fake)
    assert row["status"] == "NOT_FOUND"
    assert row["openalex_id"] is None


def test_missing_doi_is_reported_not_guessed():
    fake = FakeOpenAlex({})
    row = cr.check({"key": "R4", "doi": None, "title": "No identifier"}, fake)
    assert row["status"] == "NO_DOI"
    assert fake.calls == []


def test_doi_prefixes_are_stripped_before_lookup():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    row = cr.check({"key": "R5", "doi": "https://doi.org/10.1000/abc", "title": WORK["title"]}, fake)
    assert row["status"] == "VERIFIED"
    assert fake.calls == [f"{cr.API}/works/doi:10.1000/abc"]


def test_without_a_title_a_resolving_doi_is_verified_with_a_reason():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    row = cr.check({"key": "R6", "doi": "10.1000/abc", "title": ""}, fake)
    assert row["status"] == "VERIFIED"
    assert "no title" in row["reason"]


def test_summary_counts_every_item():
    fake = FakeOpenAlex({"10.1000/abc": WORK})
    items = [
        {"key": "a", "doi": "10.1000/abc", "title": WORK["title"]},
        {"key": "b", "doi": "10.1000/abc", "title": "Other"},
        {"key": "c", "doi": "10.9999/none", "title": "Any"},
        {"key": "d", "doi": None, "title": "Any"},
    ]
    summary = cr.check_all(items, fake)
    assert summary["total"] == 4
    assert summary["counts"] == {"VERIFIED": 1, "MISMATCH": 1, "NOT_FOUND": 1, "NO_DOI": 1}
    assert [r["key"] for r in summary["items"]] == ["a", "b", "c", "d"]


def test_cli_writes_the_summary(tmp_path, monkeypatch):
    refs = tmp_path / "refs.json"
    refs.write_text(json.dumps([{"key": "a", "doi": None, "title": "x"}]), encoding="utf-8")
    out = tmp_path / "checked.json"
    monkeypatch.setattr(cr, "_default_fetch", FakeOpenAlex({}))
    assert cr.main([str(refs), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["counts"] == {"NO_DOI": 1}
