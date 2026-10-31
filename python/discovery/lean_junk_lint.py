"""
python/discovery/lean_junk_lint.py - Junk-value lint for Lean statement files (ADR-DISCOVERY-070).

Mathlib makes partial operations total by returning a default ("junk") value: the Bochner integral of a
non-integrable function is 0, `deriv` of a non-differentiable function is 0, x / 0 = 0 in a field,
`ENNReal.toReal ∞ = 0`, a real `⨆` over an empty or unbounded family is 0, and `Real.rpow 0 0 = 1`. A statement
that silently lands on a junk value can be weaker than it reads, or vacuous: a bound by `C * eLpNorm f` is
empty when the norm is ∞.

This is a static pass, not a type checker. It
1. splits the file into declarations (comments blanked, line numbers kept);
2. lists every site of a total-function convention in each declaration;
3. for every theorem, follows the definitions it uses (by name, transitively) and asks whether the theorem's own
   text discharges each site: Schwartz data, a MemLp hypothesis or conjunct, a positivity hypothesis on a
   divisor, an `if x = ∞` guard, an ℝ≥0∞ codomain where the convention is exact.

A site no rule discharges is OPEN: a fidelity question for a human, not a defect. Discharges are syntactic and
say which text discharged them; a reviewer should still read them. The pass reports, it never edits.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Set, Tuple


class JunkKind(str, Enum):
    BOCHNER_INTEGRAL = "BOCHNER_INTEGRAL"  # ∫ of a non-integrable function is 0.
    DERIV = "DERIV"  # deriv of a non-differentiable function is 0.
    DIVISION = "DIVISION"  # x / 0 = 0 in a field (ℝ≥0∞: x / 0 = ∞ for x ≠ 0).
    INVERSE = "INVERSE"  # 0⁻¹ = 0 in a field.
    TO_REAL = "TO_REAL"  # ENNReal.toReal ∞ = 0.
    SUPREMUM = "SUPREMUM"  # Real ⨆ over an empty or unbounded family is 0.
    RPOW = "RPOW"  # Real.rpow: 0 ^ 0 = 1, negative bases go through Complex.
    INFINITE_RHS = "INFINITE_RHS"  # eLpNorm X ≤ C * eLpNorm Y holds trivially when eLpNorm Y = ∞.


class Status(str, Enum):
    DISCHARGED = "DISCHARGED"
    OPEN = "OPEN"


_EXPLANATION = {
    JunkKind.BOCHNER_INTEGRAL: "Bochner ∫ is 0 when the integrand is not integrable",
    JunkKind.DERIV: "deriv is 0 where the function is not differentiable",
    JunkKind.DIVISION: "x / 0 = 0 in ℝ",
    JunkKind.INVERSE: "0⁻¹ = 0 in ℝ",
    JunkKind.TO_REAL: "ENNReal.toReal ∞ = 0",
    JunkKind.SUPREMUM: "a real ⨆ over an empty or unbounded family is 0",
    JunkKind.RPOW: "Real.rpow has 0 ^ 0 = 1 and junk values at negative bases",
    JunkKind.INFINITE_RHS: "a bound by C * ∞ holds for every left-hand side",
}

_DECL = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|nonrec)\s+)*"
    r"(def|abbrev|theorem|lemma|instance)\s+([^\s:({\[]+)"
)
_BOUNDARY = re.compile(r"^\s*(end|namespace|section|open|noncomputable section)\b")
_NUMERAL = re.compile(r"^\(?\s*\d+(?:\.\d+)?\s*(?::\s*[^()]+)?\)?$")
_CAST = re.compile(r"\((\w+) : [^()]+\)")


@dataclass
class Declaration:
    kind: str
    name: str
    start: int  # 1-based line numbers.
    end: int
    text: str  # Comment-free source of the declaration.

    @property
    def short(self) -> str:
        return self.name.split(".")[-1]

    @property
    def header(self) -> str:
        """The signature: everything before the first `:=` (the whole text for a theorem stated with `:= by`)."""
        return self.text.split(":=", 1)[0]


@dataclass
class Site:
    kind: JunkKind
    declaration: str
    line: int
    snippet: str
    operand: str = ""  # Divisor, toReal argument, rpow base and exponent, or right-hand side norm argument.


@dataclass
class Finding:
    theorem: str
    kind: str
    declaration: str
    line: int
    snippet: str
    operand: str
    status: str
    discharged_by: str
    explanation: str
    review: Optional[str] = None  # Filled by a human (or a case file) for OPEN findings and non-obvious discharges.


@dataclass
class LintReport:
    file: str
    declarations: List[str]
    sites: List[Dict]
    findings: List[Finding] = field(default_factory=list)

    def open_findings(self) -> List[Finding]:
        return [f for f in self.findings if f.status == Status.OPEN.value]

    def to_dict(self) -> Dict:
        return {
            "file": self.file,
            "declarations": self.declarations,
            "sites": self.sites,
            "findings": [asdict(f) for f in self.findings],
            "open": len(self.open_findings()),
        }


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def strip_comments(source: str) -> str:
    """Blanks `--` and (nested) `/- -/` comments, keeping newlines so line numbers survive."""
    out: List[str] = []
    i, depth, n = 0, 0, len(source)
    while i < n:
        two = source[i : i + 2]
        if two == "/-":
            depth += 1
            out.append("  ")
            i += 2
        elif depth and two == "-/":
            depth -= 1
            out.append("  ")
            i += 2
        elif depth:
            out.append("\n" if source[i] == "\n" else " ")
            i += 1
        elif two == "--":
            j = source.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


def parse_declarations(source: str) -> List[Declaration]:
    lines = strip_comments(source).split("\n")
    starts: List[Tuple[int, str, str]] = []
    boundaries: Set[int] = set()
    for index, line in enumerate(lines):
        match = _DECL.match(line)
        if match:
            starts.append((index, match.group(1), match.group(2)))
        elif _BOUNDARY.match(line):
            boundaries.add(index)
    declarations = []
    for k, (index, kind, name) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        stop = min([b for b in boundaries if index < b < stop] + [stop])
        text = "\n".join(lines[index:stop]).rstrip()
        declarations.append(Declaration(kind, name, index + 1, index + text.count("\n") + 1, text))
    return declarations


def _balanced_after(text: str, start: int, apply: bool = True) -> str:
    """The operand starting at `start`: a parenthesised group, or an identifier (with its arguments if `apply`)."""
    i = start
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == "(":
        depth = 0
        for j in range(i, len(text)):
            depth += text[j] == "("
            depth -= text[j] == ")"
            if depth == 0:
                return text[i : j + 1]
        return text[i:]
    pattern = r"[\w.'₀-₉]+(?:\s+\((?:[^()]|\([^()]*\))*\))?" if apply else r"[\w.'₀-₉]+"
    match = re.match(pattern, text[i:])
    return match.group(0) if match else ""


def _balanced_before(text: str, end: int) -> str:
    """The operand ending just before `end`: a parenthesised group or an identifier."""
    i = end - 1
    while i >= 0 and text[i].isspace():
        i -= 1
    if i >= 0 and text[i] == ")":
        depth = 0
        for j in range(i, -1, -1):
            depth += text[j] == ")"
            depth -= text[j] == "("
            if depth == 0:
                return text[j : i + 1]
        return text[: i + 1]
    match = re.search(r"[\w.'‖]+$", text[: i + 1])
    return match.group(0) if match else ""


def natural_binders(declaration: Declaration) -> Set[str]:
    """Variables the declaration binds with type ℕ (powers by them are Monoid.npow, total and exact)."""
    names: Set[str] = set()
    for match in re.finditer(r"[({]([^(){}:]+) : ℕ[)}]|∀ ([^:,]+?) : ℕ,", declaration.text):
        names.update((match.group(1) or match.group(2)).split())
    return names


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def find_sites(declaration: Declaration) -> List[Site]:
    text = declaration.text
    lines = text.splitlines()
    naturals = natural_binders(declaration)
    sites: List[Site] = []

    def add(kind: JunkKind, offset: int, operand: str = "") -> None:
        index = text[:offset].count(chr(10))
        sites.append(
            Site(kind, declaration.name, declaration.start + index, lines[index].strip()[:120], _flat(operand))
        )

    for match in re.finditer(r"∫(?!⁻)", text):
        add(JunkKind.BOCHNER_INTEGRAL, match.start())
    for match in re.finditer(r"\bderiv\b", text):
        add(JunkKind.DERIV, match.start())
    for match in re.finditer(r"(?<![/-])/(?![-/])", text):
        add(JunkKind.DIVISION, match.start(), _balanced_after(text, match.end()))
    for match in re.finditer(r"⁻¹", text):
        add(JunkKind.INVERSE, match.start(), _balanced_before(text, match.start()))
    for match in re.finditer(r"\.toReal\b", text):
        add(JunkKind.TO_REAL, match.start(), _balanced_before(text, match.start()))
    for match in re.finditer(r"ENNReal\.toReal\s", text):
        add(JunkKind.TO_REAL, match.start(), _balanced_after(text, match.end()))
    for match in re.finditer(r"⨆|⨅|\bsSup\b|\biSup\b", text):
        add(JunkKind.SUPREMUM, match.start())
    for match in re.finditer(r"\^", text):
        exponent = _balanced_after(text, match.end(), apply=False)
        bare = exponent.strip("() ")
        if re.fullmatch(r"\d+", bare) or bare in naturals:
            continue  # Natural-number powers are Monoid.npow, total and exact.
        add(JunkKind.RPOW, match.start(), f"{_balanced_before(text, match.start())} ^ {exponent}")
    for match in re.finditer(r"\*\s*eLpNorm\s", text):
        add(JunkKind.INFINITE_RHS, match.start(), _balanced_after(text, match.end(), apply=False))
    return sites


# ---------------------------------------------------------------------------
# Theorem context and discharge rules
# ---------------------------------------------------------------------------


@dataclass
class _Context:
    theorem: Declaration
    premises: List[str]
    conclusion: str
    binders: Dict[str, str]  # Variable -> type text.
    lower: Dict[str, Tuple[Fraction, bool]]  # Variable -> (bound, strict) from simple premises "c ≤ x" / "c < x".


def _split_top(text: str, separator: str) -> List[str]:
    parts, depth, current = [], 0, []
    for ch in text:
        depth += ch in "([{"
        depth -= ch in ")]}"
        if ch == separator and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return parts


def _context(theorem: Declaration) -> _Context:
    statement = theorem.header.split(":", 1)[1] if ":" in theorem.header else theorem.header
    statement = re.sub(r"\s+", " ", statement)
    segments = _split_top(statement, "→")
    binders: Dict[str, str] = {}
    for match in re.finditer(r"∀ ([^:,]+?) : ([^,]+),", statement):
        for name in match.group(1).split():
            binders[name] = match.group(2).strip()
    lower: Dict[str, Tuple[Fraction, bool]] = {}
    for segment in segments[:-1]:
        fact = _CAST.sub(r"\1", segment.split(",")[-1].strip())
        match = re.fullmatch(r"(\d+) (<|≤) (\w+)", fact)
        if match:
            lower[match.group(3)] = (Fraction(match.group(1)), match.group(2) == "<")
    return _Context(theorem, segments[:-1], segments[-1], binders, lower)


def _nonzero(operand: str, ctx: _Context, naturals: Set[str] = frozenset()) -> Optional[str]:
    """Why `operand` cannot be zero under the theorem's premises, or None. `naturals` are ℕ-typed exponents."""
    core = _CAST.sub(r"\1", operand).strip()
    while core.startswith("(") and core.endswith(")") and _balanced_after(core, 0) == core:
        core = core[1:-1].strip()
    core = re.sub(r"\.toReal$", "", core)
    if re.fullmatch(r"\d+(?:\.\d+)?(?: : .+)?", core):
        return "nonzero numeral" if Fraction(core.split(":")[0].strip()) != 0 else None
    names = set(re.findall(r"[^\W\d][\w.']*", core))
    if names and names <= {"Real.pi"} | naturals and not re.search(r"[-/]", core):
        return "positive constant (products and natural powers of positive numerals and π)"
    simple = re.fullmatch(r"(\w+)(?:\.toReal)?(?:\s*-\s*(\d+))?", core)
    if simple:
        name, shift = simple.group(1), Fraction(simple.group(2) or 0)
        if name in ctx.lower:
            bound, strict = ctx.lower[name]
            if bound > shift or (strict and bound >= shift):
                relation = "<" if strict else "≤"
                return f"premise {bound} {relation} {name}"
    return None


def _ennreal(declaration: Declaration) -> bool:
    return "ℝ≥0∞" in declaration.header.rsplit(":", 1)[-1] or "∫⁻" in declaration.text


def _discharge(site: Site, owner: Declaration, ctx: _Context) -> Tuple[Status, str]:
    text = re.sub(r"\s+", " ", ctx.theorem.header)
    schwartz = [v for v, t in ctx.binders.items() if t.startswith("SchwartzMap")]
    memlp_premise = [p for p in ctx.premises if "MemLp" in p]
    ennreal = {v for v, t in ctx.binders.items() if t.startswith("ℝ≥0∞")}
    if site.kind == JunkKind.BOCHNER_INTEGRAL:
        if schwartz:
            return (
                Status.DISCHARGED,
                f"Schwartz data ({', '.join(schwartz)} : SchwartzMap); integrand is the datum times a bounded or polynomially bounded symbol",
            )
        if memlp_premise:
            return Status.DISCHARGED, f"MemLp premise ({memlp_premise[0].strip()[:60]}) on a finite measure"
        return Status.OPEN, ""
    if site.kind == JunkKind.DERIV:
        if re.search(r"Differentiable|HasDerivAt|ContDiff", text):
            return Status.DISCHARGED, "differentiability premise or conjunct"
        return Status.OPEN, ""
    if site.kind in (JunkKind.DIVISION, JunkKind.INVERSE):
        if site.kind == JunkKind.DIVISION and (
            _ennreal(owner) and re.match(r"(volume|ENNReal\.ofReal)\b", site.operand)
        ):
            return Status.DISCHARGED, "ℝ≥0∞ division: x / 0 = ∞ for x ≠ 0, never a collapse to 0"
        if site.kind == JunkKind.INVERSE and site.operand.strip("() ") in ennreal:
            return Status.DISCHARGED, "ℝ≥0∞ inverse is exact (∞⁻¹ = 0, 0⁻¹ = ∞)"
        reason = _nonzero(site.operand, ctx, natural_binders(owner))
        if reason:
            return Status.DISCHARGED, reason
        if re.search(r"∫⁻? \w+ in Set\.Ioi \(?0", owner.text) and re.search(r"\bofReal r\b|\br\b", site.operand):
            return Status.DISCHARGED, "integration over Set.Ioi 0 keeps the divisor positive"
        return Status.OPEN, ""
    if site.kind == JunkKind.TO_REAL:
        argument = site.operand
        bare = argument.strip("() ")
        if re.search(rf"if {re.escape(bare)} = ∞", owner.text):
            return Status.DISCHARGED, f"guarded by `if {bare} = ∞`"
        inner = re.fullmatch(r"\(?\s*(\w+)⁻¹\s*\)?", argument)
        if inner and inner.group(1) in ctx.lower:
            bound, strict = ctx.lower[inner.group(1)]
            if bound > 0 or strict:
                return Status.DISCHARGED, f"{inner.group(1)}⁻¹ < ∞ since premise bounds {inner.group(1)} away from 0"
        return Status.OPEN, ""
    if site.kind == JunkKind.SUPREMUM:
        if "ℝ≥0∞" in owner.header:
            return Status.DISCHARGED, "ℝ≥0∞ is a complete lattice: an unbounded ⨆ is ∞, not 0"
        return Status.OPEN, ""
    if site.kind == JunkKind.RPOW:
        base, _, exponent = site.operand.rpartition(" ^ ")
        exponent = exponent.strip("() ")
        if re.search(r"∫⁻|‖ₑ|ENNReal\.", base):
            return Status.DISCHARGED, "ℝ≥0∞ power: total and exact"
        if re.match(r"\(?\s*1 \+ ", base):
            return Status.DISCHARGED, "base ≥ 1"
        bare = base.strip("() ")
        if re.fullmatch(r"\w+", bare) and bare in ctx.lower and _nonzero(base, ctx):
            return Status.DISCHARGED, f"positive base ({_nonzero(base, ctx)})"
        if re.fullmatch(r"\w+", exponent) and re.search(rf"max \(.*\) 0 < {exponent}\b|\b0 < {exponent}\b", text):
            return Status.DISCHARGED, f"exponent {exponent} > 0 by premise, so 0 ^ {exponent} = 0"
        return Status.OPEN, ""
    if site.kind == JunkKind.INFINITE_RHS:
        argument = site.operand.strip()
        core = argument.strip("() ")
        if core in schwartz:
            return Status.DISCHARGED, f"Schwartz datum {core} has finite Lp norms"
        target = re.escape(argument)
        if re.search(rf"MemLp {target}", ctx.conclusion):
            return Status.DISCHARGED, "explicit MemLp conjunct for the same function"
        if re.search(rf"MemLp {target}", " ".join(ctx.premises)):
            return Status.DISCHARGED, "MemLp premise for the same function"
        return Status.OPEN, ""
    return Status.OPEN, ""


_IDENT = re.compile(r"[\w']+")
_TOKENS: Dict[Tuple[int, str], Set[str]] = {}


def _tokens(declaration: Declaration) -> Set[str]:
    """Maximal [\\w']+ runs of the declaration text, cached: a name made of such characters occurs as a whole
    identifier (the regex test below) exactly when it is one of these runs."""
    key = (id(declaration), declaration.text)
    if key not in _TOKENS:
        if len(_TOKENS) > 50000:
            _TOKENS.clear()
        _TOKENS[key] = set(_IDENT.findall(declaration.text))
    return _TOKENS[key]


def _uses(declaration: Declaration, others: Sequence[Declaration]) -> List[Declaration]:
    tokens = _tokens(declaration)
    used = []
    for d in others:
        if d is declaration:
            continue
        if _IDENT.fullmatch(d.short):
            if d.short in tokens:
                used.append(d)
        elif re.search(rf"(?<![\w']){re.escape(d.short)}(?![\w'])", declaration.text):
            used.append(d)
    return used


def lint(source: str, file: str = "<string>", reviews: Optional[Dict[Tuple[str, str, int], str]] = None) -> LintReport:
    """Lints a Lean statement file. `reviews` maps (theorem, kind, line) to a human note attached to the finding."""
    declarations = parse_declarations(source)
    by_name = {d.name: d for d in declarations}
    sites = {d.name: find_sites(d) for d in declarations}
    report = LintReport(
        file=file,
        declarations=[f"{d.kind} {d.name} (lines {d.start}-{d.end})" for d in declarations],
        sites=[asdict(s) | {"kind": s.kind.value} for d in declarations for s in sites[d.name]],
    )
    for theorem in (d for d in declarations if d.kind in ("theorem", "lemma")):
        closure: List[Declaration] = [theorem]
        frontier = [theorem]
        while frontier:
            current = frontier.pop()
            for used in _uses(current, declarations):
                if used not in closure:
                    closure.append(used)
                    frontier.append(used)
        ctx = _context(theorem)
        for owner in sorted(closure, key=lambda d: d.start):
            for site in sites[owner.name]:
                status, why = _discharge(site, by_name[owner.name], ctx)
                review = (reviews or {}).get((theorem.name, site.kind.value, site.line))
                report.findings.append(
                    Finding(
                        theorem=theorem.name,
                        kind=site.kind.value,
                        declaration=owner.name,
                        line=site.line,
                        snippet=site.snippet,
                        operand=site.operand,
                        status=status.value,
                        discharged_by=why,
                        explanation=_EXPLANATION[site.kind],
                        review=review,
                    )
                )
    return report
