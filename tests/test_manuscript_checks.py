"""Tests for python/discovery/manuscript_checks.py and the revision benchmark scoring (synthetic inputs only)."""

import importlib.util
from pathlib import Path

import pytest

from python.discovery import manuscript_checks as mc

ROOT = Path(__file__).resolve().parent.parent


def _bench():
    spec = importlib.util.spec_from_file_location(
        "revision_bench", ROOT / "scripts/benchmarks/openai_math_revision_bench.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(tmp_path, files):
    for name, text in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------- parser


@pytest.mark.parametrize(
    "latex,expected",
    [
        (r"\frac{6}{4}", "3/2"),
        (r"2^{4}", "16"),
        (r"(n+1)^2", "(n + 1)**2"),
        (r"\binom{5}{2}", "10"),
        (r"24n^2+2", "24*n**2 + 2"),
        (r"x_{1}+x_2", "x_1 + x_2"),
        (r"\sqrt{2}\cdot\sqrt{8}", "4"),
    ],
)
def test_fragment_parses(latex, expected):
    assert str(mc.to_sympy(latex)) == expected


@pytest.mark.parametrize("latex", [r"f(x)", r"\int_0^1 x", r"|x|", r"\dim X", r"x^{23}y'", r"[0,1)", r"x^23"])
def test_outside_fragment_is_skipped(latex):
    with pytest.raises(mc.Unparsed):
        mc.to_sympy(latex)


def test_relation_chain_splits_at_top_level():
    chain = mc.relation_chain(r"a = b \le c, d \asymp e")
    assert [r for _, r in chain] == ["=", r"\le", ",", r"\asymp", ""]


def test_comments_are_blanked_but_escaped_percent_kept():
    assert mc.strip_tex_comments("a % b\n50\\% c") == "a \n50\\% c"


# ---------------------------------------------------------------- checks


def test_strict_identity_flags_false_arithmetic_only(tmp_path):
    root = _write(tmp_path, {"a.tex": "We have $2+3=6$ and $2+3=5$ and \\[ (a+b)^2 = a^2+2ab+b^2. \\]\n"})
    flags, cov, _ = mc.run_all(root)
    strict = [f for f in flags if f.check == mc.IDENTITY_STRICT]
    assert [f.key for f in strict] == ["2+3=6"]
    assert not [f for f in flags if f.check == mc.IDENTITY_CONTEXT]
    assert cov.identities_checked == 3


def test_context_identity_and_definitions(tmp_path):
    root = _write(tmp_path, {"a.tex": "Let $m = 2k+1$. Then $I + m = 0$.\n"})
    flags, _, _ = mc.run_all(root)
    assert [f.check for f in flags] == [mc.IDENTITY_CONTEXT]  # the definition m = 2k+1 is skipped
    assert flags[0].line == 1


def test_exponent_balance(tmp_path):
    root = _write(tmp_path, {"a.tex": "$N^{d-1} N \\asymp N^{d}$ and $R^2 \\sim R^{3}$.\n"})
    flags, cov, _ = mc.run_all(root)
    assert [f.check for f in flags] == [mc.EXPONENT]
    assert "R" in flags[0].detail
    assert cov.exponent_checked == 2


def test_citation_resolution(tmp_path):
    root = _write(
        tmp_path,
        {
            "main.tex": "See \\cite{A,B} and \\cite[Thm.~2]{C}.\n"
            "\\href{https://x/preprints/Some-paper-October-1-2026/p.pdf}{x}\n",
            "refs.bib": "@article{A, title={a}}\n@book{C,\n title={c}}\n",
        },
    )
    flags, cov, _ = mc.run_all(root, snapshot_manuscripts={"Other-paper-October-1-2026"})
    keys = sorted(f.key for f in flags if f.check == mc.CITATION)
    assert keys == ["cite:B", "link:Some-paper-October-1-2026"]
    assert cov.citations == 3 and cov.bibliography_entries == 2


def test_citation_check_silent_without_bibliography(tmp_path):
    root = _write(tmp_path, {"main.tex": "See \\cite{A}.\n"})
    flags, _, _ = mc.run_all(root)
    assert flags == []


# ---------------------------------------------------------------- benchmark scoring


def test_changed_locations_ignore_dates_and_edition_links(tmp_path):
    bench = _bench()
    pre = _write(tmp_path / "pre", {"m.tex": "\\date{May 1, 2026}\nkeep\nold claim\nkeep\n"})
    post = _write(tmp_path / "post", {"m.tex": "\\date{May 9, 2026}\nkeep\nnew claim\nkeep\n"})
    assert bench.changed_locations(pre, post) == {"m.tex": [3]}


def test_score_requires_location_and_resolution():
    bench = _bench()
    item = {"locations": {"m.tex": [[10, 12]]}, "encodable": ["CITATION"], "family_has_lean": False}
    flag = {"check": "CITATION", "file": "m.tex", "line": 13, "key": "cite:X", "detail": ""}
    far = dict(flag, line=40, key="cite:Y")
    pre = {"flags": [flag, far], "tex_lines": 100}
    fixed = bench.score(item, pre, {"flags": []})
    assert fixed["verdict"] == "HIT" and fixed["per_check"]["CITATION"]["resolved_at_location"] == 1
    persisted = bench.score(item, pre, {"flags": [flag]})
    assert persisted["verdict"] == "MISS"
    assert persisted["per_check"]["IDENTITY_STRICT"]["verdict"] == "NOT_ENCODABLE"
    assert persisted["per_check"]["lean_junk_lint"]["verdict"] == "NOT_ENCODABLE"
