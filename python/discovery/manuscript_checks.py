"""
python/discovery/manuscript_checks.py - Generic static checks on LaTeX manuscript sources.

Used by the openai/math revision benchmark (docs/reference/benchmarks/OPENAI_MATH_REVISION_PROTOCOL.md) to ask
whether checks CoResearcher can run today would have flagged a defect before the authors fixed it. The checks are
deliberately generic: no rule mentions a particular manuscript or defect.

Three checks, each returning flags with a file, a line and a normalized key (the key is what is compared between
the pre-fix and the corrected version):

- CITATION: every citation key resolves to a bibliography entry (\\bibitem or a .bib entry), and every link to
  another manuscript of the collection resolves to a manuscript present in the same snapshot.
- IDENTITY: obligation-ledger style check of elementary equalities. Displayed and inline math is parsed in a
  restricted LaTeX fragment (numbers, letters, Greek letters, + - * / ^, \\frac, \\sqrt, \\binom, parentheses).
  Anything outside the fragment is skipped, never guessed. Two tiers:
    STRICT: both sides are closed numbers and differ (exact arithmetic);
    CONTEXT: the sides contain symbols and are not equal as functions (random rational points, then sympy).
      Most such equalities are conditional on the surrounding text, so CONTEXT flags are expected to be noisy.
  Equalities whose left side is a single symbol are read as definitions and skipped.
- EXPONENT: exponent bookkeeping for asymptotic relations (\\asymp, \\sim, \\simeq, \\approx) between monomials:
  the exponent of every symbol must agree on both sides (constants are ignored).

The parser is a static pass, not a reader: a skipped formula is reported as unparsed, not as correct.
"""

from __future__ import annotations

import random
import re
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import sympy

CITATION = "CITATION"
IDENTITY_STRICT = "IDENTITY_STRICT"
IDENTITY_CONTEXT = "IDENTITY_CONTEXT"
EXPONENT = "EXPONENT"


@dataclass
class Flag:
    check: str
    file: str  # Path relative to the manuscript source root.
    line: int  # 1-based.
    key: str  # Normalized content, compared across versions.
    detail: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Coverage:
    formulas: int = 0  # math segments seen
    relations: int = 0  # relation instances (=, \asymp, ...) seen
    parsed: int = 0  # relation instances with both sides in the fragment
    identities_checked: int = 0
    exponent_checked: int = 0
    citations: int = 0
    bibliography_entries: int = 0
    internal_links: int = 0


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


def strip_tex_comments(text: str) -> str:
    """Blanks % comments (not \\%), keeping line structure."""
    out = []
    for line in text.split("\n"):
        i = 0
        while True:
            j = line.find("%", i)
            if j == -1:
                break
            if j > 0 and line[j - 1] == "\\":
                i = j + 1
                continue
            line = line[:j]
            break
        out.append(line)
    return "\n".join(out)


def read_sources(root: Path) -> Dict[str, str]:
    """All .tex, .bib and .bbl files under root, keyed by relative POSIX path."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in (".tex", ".bib", ".bbl"):
            files[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    return files


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# ---------------------------------------------------------------------------
# CITATION
# ---------------------------------------------------------------------------

_CITE = re.compile(r"\\(?:[cC]ite[a-zA-Z]*|[a-z]*cite[a-z]*)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")
_BIBITEM = re.compile(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")
_BIBENTRY = re.compile(r"@\s*[a-zA-Z]+\s*\{\s*([^,\s]+)\s*,")
_INTERNAL = re.compile(r"(?:preprints/|OAI:)([A-Za-z0-9][A-Za-z0-9\-]*?-(?:January|February|March|April|May|June|July|"
                       r"August|September|October|November|December)-\d{1,2}-\d{4})")


def bibliography_keys(files: Dict[str, str]) -> Set[str]:
    keys: Set[str] = set()
    for name, text in files.items():
        body = strip_tex_comments(text) if name.endswith(".tex") else text
        keys.update(k.strip() for k in _BIBITEM.findall(body))
        if name.endswith(".bib"):
            keys.update(k.strip() for k in _BIBENTRY.findall(body))
    return keys


def check_citations(files: Dict[str, str], snapshot_manuscripts: Optional[Set[str]], coverage: Coverage) -> List[Flag]:
    flags: List[Flag] = []
    keys = bibliography_keys(files)
    coverage.bibliography_entries = len(keys)
    for name, text in files.items():
        if not name.endswith(".tex"):
            continue
        body = strip_tex_comments(text)
        for m in _CITE.finditer(body):
            for key in (k.strip() for k in m.group(1).split(",")):
                if not key:
                    continue
                coverage.citations += 1
                if keys and key not in keys:
                    flags.append(Flag(CITATION, name, _line_of(body, m.start()), f"cite:{key}",
                                      f"citation key '{key}' has no bibliography entry"))
    if snapshot_manuscripts is not None:
        for name, text in files.items():
            for m in _INTERNAL.finditer(text):
                coverage.internal_links += 1
                target = m.group(1)
                if target not in snapshot_manuscripts:
                    flags.append(Flag(CITATION, name, _line_of(text, m.start()), f"link:{target}",
                                      f"link to manuscript '{target}' absent from the snapshot"))
    # One flag per (file, line, key).
    seen, unique = set(), []
    for f in flags:
        if (f.file, f.line, f.key) not in seen:
            seen.add((f.file, f.line, f.key))
            unique.append(f)
    return unique


# ---------------------------------------------------------------------------
# Math extraction
# ---------------------------------------------------------------------------

_DISPLAY_ENVS = ("equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*",
                 "eqnarray", "eqnarray*", "flalign", "flalign*")


def math_segments(text: str) -> List[Tuple[int, str]]:
    """(offset, content) of math segments: \\[..\\], $$..$$, $..$, \\(..\\) and display environments.
    Rows of multi-line environments are split on \\\\ and alignment marks removed."""
    body = strip_tex_comments(text)
    segments: List[Tuple[int, str]] = []
    taken = [False] * (len(body) + 1)

    def add(start: int, end: int, content: str) -> None:
        if any(taken[start:end]):
            return
        for i in range(start, end):
            taken[i] = True
        offset = start
        for row in re.split(r"\\\\", content):
            segments.append((offset, row.replace("&", " ")))
            offset += len(row) + 2

    env_names = "|".join(re.escape(e) for e in _DISPLAY_ENVS)
    for m in re.finditer(r"\\begin\{(" + env_names + r")\}(.*?)\\end\{\1\}", body, re.S):
        add(m.start(), m.end(), m.group(2))
    for m in re.finditer(r"\\\[(.*?)\\\]", body, re.S):
        add(m.start(), m.end(), m.group(1))
    for m in re.finditer(r"\$\$(.*?)\$\$", body, re.S):
        add(m.start(), m.end(), m.group(1))
    for m in re.finditer(r"\\\((.*?)\\\)", body, re.S):
        add(m.start(), m.end(), m.group(1))
    for m in re.finditer(r"(?<![\\$])\$([^$]+?)\$(?!\$)", body):
        add(m.start(), m.end(), m.group(1))
    segments.sort()
    return segments


# Relations: '=' chains feed IDENTITY, asymptotic relations feed EXPONENT. Anything else ends a comparable run.
_ASYMPTOTIC = {r"\asymp", r"\sim", r"\simeq", r"\approx"}
_OTHER_RELATIONS = {r"\le", r"\leq", r"\ge", r"\geq", r"\leqslant", r"\geqslant", "<", ">", r"\ne", r"\neq",
                    r"\lesssim", r"\gtrsim", r"\ll", r"\gg", r"\equiv", r"\cong", r"\to", r"\mapsto", r"\in",
                    r"\subset", r"\subseteq", r"\supset", r"\supseteq", r"\coloneqq", ":=", r"\colon", r"\iff",
                    r"\implies", r"\Rightarrow", r"\Longrightarrow", r"\propto", r"\mid", r"\perp", r"\approx_"}

_REL_TOKEN = re.compile(r"(\\[a-zA-Z]+|:=|<|>|=|,|;)")


def relation_chain(content: str) -> List[Tuple[str, str]]:
    """Splits a segment at top-level relations. Returns [(side, relation_after_side)], last relation ''.
    Commas and semicolons at top level end the chain (they separate statements)."""
    parts: List[Tuple[str, str]] = []
    depth = 0
    current = []
    i = 0
    while i < len(content):
        ch = content[i]
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth -= 1
        if depth == 0:
            m = _REL_TOKEN.match(content, i)
            if m:
                tok = m.group(1)
                rel = None
                if tok == "=" or tok in _ASYMPTOTIC or tok in _OTHER_RELATIONS or tok in (",", ";", "<", ">", ":="):
                    rel = tok
                if tok.startswith("\\") and tok not in _ASYMPTOTIC and tok not in _OTHER_RELATIONS:
                    rel = None
                if rel is not None:
                    parts.append(("".join(current), rel))
                    current = []
                    i = m.end()
                    continue
        current.append(ch)
        i += 1
    parts.append(("".join(current), ""))
    return parts


# ---------------------------------------------------------------------------
# Restricted LaTeX -> sympy
# ---------------------------------------------------------------------------

_GREEK = {"alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta", "vartheta", "iota",
          "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega",
          "Gamma", "Delta", "Theta", "Lambda", "Xi", "Sigma", "Upsilon", "Phi", "Psi", "Omega"}
_IGNORED = {r"\left", r"\right", r"\big", r"\Big", r"\bigg", r"\Bigg", r"\bigl", r"\bigr", r"\Bigl", r"\Bigr",
            r"\,", r"\;", r"\!", r"\:", r"\quad", r"\qquad", r"\displaystyle", r"\textstyle", r"\ "}
_TIMES = {r"\cdot", r"\times"}
_FRAC = {r"\frac", r"\dfrac", r"\tfrac"}


class Unparsed(Exception):
    pass


def _tokens(s: str) -> List[str]:
    toks = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace() or ch == "~":
            i += 1
        elif ch == "\\":
            m = re.match(r"\\([a-zA-Z]+|.)", s[i:])
            if not m:
                raise Unparsed("lone backslash")
            toks.append("\\" + m.group(1))
            i += m.end()
        elif ch.isdigit():
            m = re.match(r"\d+(?:\.\d+)?", s[i:])
            toks.append(m.group(0))
            i += m.end()
        else:
            toks.append(ch)
            i += 1
    return [t for t in toks if t not in _IGNORED]


class _Parser:
    """Recursive descent over the restricted fragment. Produces a sympy expression or raises Unparsed."""

    def __init__(self, tokens: Sequence[str]):
        self.t = list(tokens)
        self.i = 0

    def peek(self) -> Optional[str]:
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, expected: Optional[str] = None) -> str:
        tok = self.peek()
        if tok is None or (expected is not None and tok != expected):
            raise Unparsed(f"expected {expected!r}, got {tok!r}")
        self.i += 1
        return tok

    def parse(self) -> sympy.Expr:
        if not self.t:
            raise Unparsed("empty")
        e = self.sum()
        if self.peek() is not None:
            raise Unparsed(f"trailing {self.peek()!r}")
        return e

    def sum(self) -> sympy.Expr:
        sign = 1
        if self.peek() in ("+", "-"):
            sign = -1 if self.take() == "-" else 1
        e = sign * self.product()
        while self.peek() in ("+", "-"):
            op = self.take()
            rhs = self.product()
            e = e + rhs if op == "+" else e - rhs
        return e

    def product(self) -> sympy.Expr:
        e = self.power()
        while True:
            tok = self.peek()
            if tok in _TIMES or tok == "*":
                self.take()
                e = e * self.power()
            elif tok == "/":
                self.take()
                e = e / self.power()
            elif tok is not None and self._starts_atom(tok):
                prev = self.t[self.i - 1]
                # Implicit product. A number after an atom (x 2) and a letter before '(' (f(x)) are ambiguous.
                if tok[0].isdigit():
                    raise Unparsed("number after atom")
                if tok == "(" and (prev.isalpha() or prev.lstrip("\\") in _GREEK or prev == "}"):
                    raise Unparsed("possible function application")
                e = e * self.power()
            else:
                return e

    @staticmethod
    def _starts_atom(tok: str) -> bool:
        return (tok[0].isdigit() or (len(tok) == 1 and tok.isalpha()) or tok in ("(", "[", "{")
                or tok.lstrip("\\") in _GREEK or tok in _FRAC or tok in (r"\sqrt", r"\binom"))

    def power(self) -> sympy.Expr:
        base = self.postfix()
        if self.peek() == "^":
            self.take()
            exp = self.group_or_atom()
            return sympy.Pow(base, exp, evaluate=True)
        return base

    def postfix(self) -> sympy.Expr:
        e = self.atom()
        if self.peek() == "!":
            self.take()
            e = sympy.factorial(e)
        return e

    def group_or_atom(self) -> sympy.Expr:
        if self.peek() == "{":
            return self.braced()
        tok = self.take()
        if tok.isdigit():
            if len(tok) > 1:
                raise Unparsed("unbraced multi-digit exponent")  # x^23 is x^2 3 in TeX
            return sympy.Integer(tok)
        if len(tok) == 1 and tok.isalpha():
            return sympy.Symbol(tok)
        if tok.lstrip("\\") in _GREEK:
            return sympy.Symbol(tok.lstrip("\\"))
        raise Unparsed(f"bad exponent {tok!r}")

    def braced(self) -> sympy.Expr:
        self.take("{")
        start = self.i
        depth = 1
        while depth:
            tok = self.take()
            depth += {"{": 1, "}": -1}.get(tok, 0)
        return _Parser(self.t[start:self.i - 1]).parse()

    def subscript(self) -> str:
        self.take("_")
        if self.peek() == "{":
            self.take("{")
            parts = []
            depth = 1
            while True:
                tok = self.take()
                depth += {"{": 1, "}": -1}.get(tok, 0)
                if depth == 0:
                    break
                parts.append(tok)
            raw = "".join(p.lstrip("\\") for p in parts)
        else:
            raw = self.take().lstrip("\\")
        if not re.fullmatch(r"[A-Za-z0-9+\-]+", raw):
            raise Unparsed("complex subscript")
        return raw

    def atom(self) -> sympy.Expr:
        tok = self.take()
        if tok[0].isdigit():
            if self.peek() is not None and self.peek()[0].isdigit():
                raise Unparsed("adjacent numbers")
            return sympy.Rational(Fraction(tok))
        if tok in ("(", "["):
            close = ")" if tok == "(" else "]"
            start = self.i
            depth = 1
            while depth:
                t = self.take()
                if t in ("(", "["):
                    depth += 1
                elif t in (")", "]"):
                    depth -= 1
                    if depth == 0 and t != close:
                        raise Unparsed("interval or mismatched brackets")
            return _Parser(self.t[start:self.i - 1]).parse()
        if tok == "{":
            self.i -= 1
            return self.braced()
        if tok in _FRAC:
            num = self.braced()
            den = self.braced()
            return num / den
        if tok == r"\sqrt":
            if self.peek() == "[":
                raise Unparsed("nth root")
            return sympy.sqrt(self.braced())
        if tok == r"\binom":
            return sympy.binomial(self.braced(), self.braced())
        name = None
        if len(tok) == 1 and tok.isalpha():
            name = tok
        elif tok.lstrip("\\") in _GREEK:
            name = tok.lstrip("\\")
        if name is None:
            raise Unparsed(f"outside fragment: {tok!r}")
        if self.peek() == "_":
            name = f"{name}_{self.subscript()}"
        if self.peek() == "'":
            raise Unparsed("prime")
        return sympy.Symbol(name)


def to_sympy(latex: str) -> sympy.Expr:
    text = latex.strip().rstrip(".,;:").strip()
    if not text:
        raise Unparsed("empty")
    if re.search(r"\\(text|mathrm|operatorname|mathbf|mathcal|mathbb|mathfrak|hat|bar|tilde|vec|dot|ddot|overline|"
                 r"underline|sum|prod|int|lim|sup|inf|max|min|log|ln|exp|sin|cos|tan|det|dim|deg|ker|dots|ldots|cdots|"
                 r"pm|mp|circ|otimes|oplus|wedge|vee|cup|cap|partial|nabla|infty|langle|rangle|lfloor|rfloor|lceil|"
                 r"rceil|mid|vert|Vert|\||setminus|backslash)\b", text):
        raise Unparsed("outside fragment")
    if "|" in text or "'" in text or "\\{" in text:
        raise Unparsed("outside fragment")
    return _Parser(_tokens(text)).parse()


# ---------------------------------------------------------------------------
# IDENTITY and EXPONENT
# ---------------------------------------------------------------------------

_RNG_SEED = 20261030


def _numeric_differs(a: sympy.Expr, b: sympy.Expr, rng: random.Random) -> Optional[bool]:
    """True if a != b at some random positive rational point, False if equal at all of them, None if undefined."""
    symbols = sorted(a.free_symbols | b.free_symbols, key=str)
    seen_defined = False
    for _ in range(4):
        point = {s: sympy.Rational(rng.randint(2, 97), rng.randint(1, 13)) for s in symbols}
        try:
            va = sympy.nsimplify(a.subs(point)) if symbols else a
            vb = sympy.nsimplify(b.subs(point)) if symbols else b
            diff = sympy.N(va - vb, 30)
        except Exception:
            return None
        if diff.has(sympy.zoo, sympy.nan, sympy.oo, -sympy.oo) or not diff.is_number:
            continue
        if not diff.is_real:
            # Complex values from real-looking input: undefined for this check (roots of negatives etc.).
            continue
        seen_defined = True
        if abs(diff) > sympy.Float("1e-20") * (1 + abs(sympy.N(va, 30))):
            return True
    return False if seen_defined else None


def _is_definition(side: sympy.Expr) -> bool:
    return isinstance(side, sympy.Symbol)


def _monomial(expr: sympy.Expr) -> Optional[Dict[sympy.Symbol, sympy.Expr]]:
    """Exponent map of a monomial c * prod x_i^{e_i} (numeric exponents or symbolic exponents of a symbol base)."""
    expr = sympy.powsimp(expr, force=True)
    powers: Dict[sympy.Symbol, sympy.Expr] = {}
    factors = expr.args if isinstance(expr, sympy.Mul) else (expr,)
    for factor in factors:
        if factor.is_number:
            continue
        base, exp = factor.as_base_exp()
        if not isinstance(base, sympy.Symbol):
            return None
        if base in exp.free_symbols:
            return None
        powers[base] = powers.get(base, 0) + exp
    return powers or None


def _normalize_key(latex: str) -> str:
    return re.sub(r"\s+", "", latex)


def check_math(files: Dict[str, str], coverage: Coverage) -> List[Flag]:
    flags: List[Flag] = []
    rng = random.Random(_RNG_SEED)
    for name, text in sorted(files.items()):
        if not name.endswith(".tex"):
            continue
        body = strip_tex_comments(text)
        for offset, content in math_segments(text):
            coverage.formulas += 1
            chain = relation_chain(content)
            line = _line_of(body, offset)
            for (left, rel), (right, _) in zip(chain, chain[1:]):
                if rel != "=" and rel not in _ASYMPTOTIC:
                    continue
                coverage.relations += 1
                try:
                    a, b = to_sympy(left), to_sympy(right)
                except (Unparsed, RecursionError, ValueError, TypeError, ZeroDivisionError):
                    continue
                except Exception:
                    continue
                coverage.parsed += 1
                key = f"{_normalize_key(left)}{rel}{_normalize_key(right)}"
                if rel == "=":
                    if _is_definition(a):
                        continue
                    coverage.identities_checked += 1
                    closed = not a.free_symbols and not b.free_symbols
                    differs = _numeric_differs(a, b, rng)
                    if differs:
                        try:
                            if sympy.simplify(a - b) == 0:
                                continue
                        except Exception:
                            pass
                        check = IDENTITY_STRICT if closed else IDENTITY_CONTEXT
                        flags.append(Flag(check, name, line, key, f"{a} != {b}"))
                else:
                    ma, mb = _monomial(a), _monomial(b)
                    if ma is None or mb is None:
                        continue
                    coverage.exponent_checked += 1
                    for s in set(ma) | set(mb):
                        if sympy.simplify(ma.get(s, 0) - mb.get(s, 0)) != 0:
                            flags.append(Flag(EXPONENT, name, line, key,
                                              f"exponent of {s}: {ma.get(s, 0)} vs {mb.get(s, 0)} across {rel}"))
                            break
    return flags


def run_all(root: Path, snapshot_manuscripts: Optional[Set[str]] = None) -> Tuple[List[Flag], Coverage, int]:
    """Runs every check on the sources under root. Returns (flags, coverage, number of source lines)."""
    files = read_sources(root)
    coverage = Coverage()
    flags = check_citations(files, snapshot_manuscripts, coverage) + check_math(files, coverage)
    lines = sum(t.count("\n") + 1 for n, t in files.items() if n.endswith(".tex"))
    return flags, coverage, lines


def flag_keys(flags: Iterable[Flag]) -> Set[Tuple[str, str]]:
    return {(f.check, f.key) for f in flags}
