"""
python/discovery/trivial_witness_probe.py - Trivial-witness / vacuity probe for Comparator statements (ADR-DISCOVERY-070).

`lean_junk_lint` lists sites where a total-function convention could make a statement weaker than it reads. This
probe asks the sharper question: is the statement *easy for the wrong reason*? It has three stages.

1. **Arithmetic consistency (here, z3, no Lean).** The explicit numeric hypotheses of a target (binders such as
   `(hn : 3 ≤ n)`, antecedents `2 ≤ p →`, `∀ ε > 0,`), read from its statement and, for a `theorem main : P`, from
   the body of the definition `P`, must be jointly satisfiable. If they are not, the target is vacuously true. An
   UNSAT answer names the clashing atoms; letters reused in separate sub-statements can clash spuriously, so UNSAT is
   a candidate for review, not a verdict.
2. **Cheap tactics (Lean).** Each target's `sorry` is replaced by a fixed, heartbeat-bounded menu of cheap tactics
   (`trivial`, `simp_all`, `aesop`, ...), with no import of the solution. A target closed this way and free of
   `sorryAx` is TRIVIALLY_PROVABLE: its content cannot be what the headline claims. The same menu is tried on
   `False` under the target's binders, which detects contradictory hypotheses that z3 cannot read.
3. **Degenerate witnesses (Lean, written per case).** For an OPEN lint finding, two lemmas: (D1) if the junk branch
   fires, the target holds trivially; (D2) the junk branch cannot fire under the target's hypotheses. D1 proved and
   D2 proved closes the finding; D1 proved and D2 not proved leaves a concrete vacuity question.

Stages 2 and 3 only generate Lean files and parse Lean's output; they run where the openai/math Lean project is built
(Linux, see docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md). Nothing is executed from the corpus by this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

import z3

from python.discovery import lean_junk_lint
from python.discovery.openai_math_coverage import _atoms


class ArithmeticVerdict(str, Enum):
    SATISFIABLE = "SATISFIABLE"
    UNSAT_CANDIDATE = "UNSAT_CANDIDATE"  # Clashing hypothesis atoms: vacuous, or letters reused across sub-statements.
    NO_ATOMS = "NO_ATOMS"
    UNDECIDED = "UNDECIDED"


class LeanOutcome(str, Enum):
    PROVED = "PROVED"  # Elaborated without error and without sorryAx.
    NOT_PROVED = "NOT_PROVED"  # An error in the probe declaration: the menu did not close it (inconclusive).
    NOT_RUN = "NOT_RUN"


TACTIC_MENU = [
    "trivial",
    "decide",
    "rfl",
    "simp",
    "simp_all",
    "norm_num",
    "positivity",
    "aesop",
    "(intros; trivial)",
    "(intros; simp_all)",
    "(intros; aesop)",
    "(exact fun _ => trivial)",
]
HEARTBEATS = 40000


# ---------------------------------------------------------------------------
# Stage 1: arithmetic consistency of the explicit hypotheses
# ---------------------------------------------------------------------------

_BINDER_HYP = re.compile(r"\(\s*\w+\s*:\s*([^():]*?(?:≤|<|≥|>)[^():]*?)\s*\)")
_ANTECEDENT = re.compile(r"([\w./ -]+(?:\s*(?:≤|<|≥|>)\s*[\w./ -]+)+)\s*→")  # `-` keeps `-2 < t` negative.
_BOUNDED_FORALL = re.compile(r"∀\s*(\w)\s*(≤|<|≥|>)\s*(-?\d+(?:\s*/\s*\d+)?)\s*,")


def _unwrap(text: str) -> str:
    text = re.sub(r"\(\s*(\w)\s*:\s*[ℝℚℂℕℤ]\s*\)", r"\1", text)
    return re.sub(r"\(\s*(-?\d+)\s*:\s*[ℝℚℕℤ]\s*\)", r"\1", text)


def integer_letters(text: str) -> set:
    """One-letter variables bound as ℕ or ℤ (in a binder group or a `∀ x : ℕ`)."""
    found = set()
    for names, _ in re.findall(r"[({]\s*([^(){}:]+?)\s*:\s*(ℕ|ℤ)\s*[)}]", text):
        found.update(n for n in names.split() if len(n) == 1)
    found.update(re.findall(r"∀\s*\(?\s*(\w)\s*:\s*(?:ℕ|ℤ)", text))
    return found


def natural_letters(text: str) -> set:
    found = set()
    for names in re.findall(r"[({]\s*([^(){}:]+?)\s*:\s*ℕ\s*[)}]", text):
        found.update(n for n in names.split() if len(n) == 1)
    found.update(re.findall(r"∀\s*\(?\s*(\w)\s*:\s*ℕ", text))
    return found


def hypothesis_atoms(statement: str) -> List[Tuple[str, str, str]]:
    """(letter, op, number) hypotheses: binder hypotheses, antecedents of `→`, and `∀ x > c,` binders."""
    text = _unwrap(statement)
    atoms: List[Tuple[str, str, str]] = []
    for body in _BINDER_HYP.findall(text):
        atoms += _atoms(body)
    for body in _ANTECEDENT.findall(text):
        atoms += _atoms(body)
    for var, op, num in _BOUNDED_FORALL.findall(text):
        atoms += _atoms(f"{var} {op} {num}")
    return list(dict.fromkeys(atoms))


def expanded_statement(source: str, theorem_short: str) -> str:
    """The theorem's statement, followed by the body of the Prop definition it names when it is `theorem t : P`."""
    declarations = lean_junk_lint.parse_declarations(source)
    by_short = {d.name.rstrip(".").split(".")[-1]: d for d in declarations}
    theorem = by_short.get(theorem_short)
    if theorem is None:
        return ""
    text = theorem.text
    cut = text.find(":=")
    header = text if cut < 0 else text[:cut]
    target = re.search(r":\s*([\w.']+)(?:\.\{[^}]*\})?\s*$", header.strip())
    if target and target.group(1).split(".")[-1] in by_short:
        definition = by_short[target.group(1).split(".")[-1]]
        if definition.kind in ("def", "abbrev"):
            header += "\n" + definition.text
    return header


def arithmetic_check(statement: str, timeout_ms: int = 10000) -> Dict[str, Any]:
    """Are the explicit numeric hypotheses jointly satisfiable? (letters typed ℕ/ℤ are z3 Ints, ℕ ones ≥ 0)."""
    atoms = hypothesis_atoms(statement)
    if not atoms:
        return {"verdict": ArithmeticVerdict.NO_ATOMS.value, "atoms": []}
    integers, naturals = integer_letters(statement), natural_letters(statement)
    symbols = {v: (z3.Int(f"v{i}") if v in integers else z3.Real(f"v{i}"))
               for i, v in enumerate(sorted({a[0] for a in atoms}))}
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)
    for v in naturals & set(symbols):
        solver.add(symbols[v] >= 0)
    tracked = {}
    for i, (v, op, num) in enumerate(atoms):
        if "/" in num:
            p, q = (int(x) for x in num.split("/"))
            value = z3.Q(p, q)
        else:
            value = z3.RealVal(num) if "." in num else z3.IntVal(int(num))
        lhs = symbols[v]
        if z3.is_int(lhs) and not z3.is_int(value):
            lhs = z3.ToReal(lhs)
        expr = {">=": lhs >= value, "<=": lhs <= value, ">": lhs > value, "<": lhs < value}[op]
        label = z3.Bool(f"a{i}")
        tracked[str(label)] = (v, op, num)
        solver.assert_and_track(expr, label)
    result = solver.check()
    out: Dict[str, Any] = {"atoms": [" ".join(a) for a in atoms], "integer": sorted(integers & set(symbols))}
    if result == z3.sat:
        return out | {"verdict": ArithmeticVerdict.SATISFIABLE.value}
    if result == z3.unsat:
        core = [" ".join(tracked[str(c)]) for c in solver.unsat_core()]
        return out | {"verdict": ArithmeticVerdict.UNSAT_CANDIDATE.value, "clash": core}
    return out | {"verdict": ArithmeticVerdict.UNDECIDED.value, "reason": solver.reason_unknown()}


# ---------------------------------------------------------------------------
# Stage 2: cheap-tactic probes as Lean files
# ---------------------------------------------------------------------------


def _menu() -> str:
    """The tactic block that replaces `sorry`: heartbeat-bounded, first tactic that closes the goal wins."""
    return f"set_option maxHeartbeats {HEARTBEATS} in\n    first\n      " + "\n      ".join(f"| {t}" for t in TACTIC_MENU)


def _theorem_span(source: str, short: str) -> Optional[Tuple[int, int]]:
    """Character span of `theorem short ... := by sorry` (the whole declaration)."""
    match = re.search(rf"(?m)^theorem\s+{re.escape(short)}(?=[\s.:({{\[])", source)
    if match is None:
        return None
    end = source.find("sorry", match.end())
    if end < 0:
        return None
    return match.start(), end + len("sorry")


def binders_and_type(declaration: str) -> Tuple[str, str]:
    """Splits `theorem name binders : type := ...` at the first top-level `:` after the name."""
    head = declaration.split(":=", 1)[0]
    name_end = re.match(r"theorem\s+[^\s:({\[.]+(?:\.[^\s:({\[.]+)*(?:\.\{[^}]*\})?", head)
    rest = head[name_end.end():] if name_end else head
    depth = 0
    for i, ch in enumerate(rest):
        if ch in "([{⦃⟨":
            depth += 1
        elif ch in ")]}⦄⟩":
            depth -= 1
        elif ch == ":" and depth == 0 and not rest[i:].startswith(":="):
            return rest[:i].strip(), rest[i + 1:].strip()
    return rest.strip(), ""


@dataclass
class ProbeFile:
    probe_id: str
    challenge: str  # Path of the challenge file, relative to lean/ComparatorChallenges.
    theorem: str
    mode: str  # "trivial" (prove the target) or "inconsistent" (prove False under its binders).
    module_path: str  # Where to write it, relative to lean/.
    text: str
    declaration: str  # Name to look for in Lean's output.


def cheap_tactic_probes(source: str, challenge: str, theorem_names: Sequence[str]) -> List[ProbeFile]:
    """Probe files for every target of one challenge file: one 'trivial' and, when it has binders, one 'inconsistent'."""
    probes = []
    stem = challenge.replace("/", "__").removesuffix(".lean")
    for name in theorem_names:
        short = name.split(".")[-1]
        span = _theorem_span(source, short)
        if span is None:
            continue
        declaration = source[span[0]:span[1]]
        trivial = declaration.replace("sorry", _menu(), 1)
        probes.append(
            ProbeFile(
                probe_id=f"{stem}:{short}:trivial",
                challenge=challenge,
                theorem=name,
                mode="trivial",
                module_path=f"ComparatorChallenges/Probes/{stem}__{short}__trivial.lean",
                text=source[: span[0]] + trivial + f"\n\n#print axioms {short}\n" + source[span[1]:],
                declaration=short,
            )
        )
        binders, _ = binders_and_type(declaration)
        if binders:
            probe_name = f"{short}_probe_inconsistent"
            example = f"\n\ntheorem {probe_name} {binders} : False := by\n  {_menu()}\n\n#print axioms {probe_name}\n"
            text = source[: span[1]] + example + source[span[1]:]
            probes.append(
                ProbeFile(
                    probe_id=f"{stem}:{short}:inconsistent",
                    challenge=challenge,
                    theorem=name,
                    mode="inconsistent",
                    module_path=f"ComparatorChallenges/Probes/{stem}__{short}__inconsistent.lean",
                    text=text,
                    declaration=probe_name,
                )
            )
    return probes


def parse_lean_output(output: str, declaration: str) -> LeanOutcome:
    """PROVED when Lean reports no error and the axiom list of `declaration` has no sorryAx.

    Other targets in the same file keep their `sorry`; that is a warning, not an error, and their axioms are not read.
    """
    if re.search(r":\d+:\d+: error", output):
        return LeanOutcome.NOT_PROVED
    axioms = re.search(rf"'[^']*{re.escape(declaration)}' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",
                       output)
    if axioms is None:
        return LeanOutcome.NOT_PROVED
    return LeanOutcome.NOT_PROVED if "sorryAx" in (axioms.group(2) or "") else LeanOutcome.PROVED


# ---------------------------------------------------------------------------
# Stage 3: degenerate-witness probes written per case
# ---------------------------------------------------------------------------


@dataclass
class DegenerateCase:
    case_id: str
    challenge: str
    theorem: str
    lint_sites: List[str]
    question: str
    lemmas: Dict[str, str]  # D1 / D2 name -> Lean text appended inside the challenge namespace.
    reading: str  # What an agent concluded by reading, before any Lean run.
    expected: Dict[str, str] = field(default_factory=dict)


CLASSICAL_ON = DegenerateCase(
    case_id="215-classical-on-degenerate-measure",
    challenge="ClassicalON.lean",
    theorem="OAI.ClassicalON.main",
    lint_sites=[
        "sphereProbability line 26: INVERSE of (surface Set.univ)",
        "partition line 36: BOCHNER_INTEGRAL",
        "correlation line 40: BOCHNER_INTEGRAL",
        "correlation line 41: DIVISION by partition",
    ],
    question=(
        "If the sphere's total surface measure were 0 or ∞, sphereProbability would be the zero measure, partition "
        "would be 0 and correlation = 0 / 0 = 0, so `0 ≤ correlation ≤ A e^{-m|x-y|}` would hold for every graph: "
        "the decay statement would be empty. Does that branch fire for n ≥ 3?"
    ),
    lemmas={
        "D1_degenerate_implies_target": """
/-- Probe D1: with a zero single-spin law the target holds trivially (A = m = 1). -/
theorem probe_degenerate_implies_target (h : ∀ n, sphereProbability n = 0) : ExponentialDecay := by
  intro n hn β hβ
  refine ⟨1, 1, one_pos, ?_⟩
  intro G b hb x y
  haveI : Nonempty G.vertices := ⟨x⟩
  have hz : referenceLaw n G = 0 := by
    apply Measure.measure_univ_eq_zero.mp
    rw [referenceLaw, Measure.pi_univ]
    exact Finset.prod_eq_zero (Finset.mem_univ x) (by simp [h])
  simp only [correlation, partition, hz, integral_zero_measure, zero_div]
  exact ⟨le_rfl, by positivity⟩

#print axioms probe_degenerate_implies_target
""",
        "D2_law_is_probability": """
/-- Probe D2: for n ≥ 3 the single-spin law is a probability measure, so the degenerate branch cannot fire. -/
theorem probe_law_is_probability (n : ℕ) (hn : 3 ≤ n) : sphereProbability n Set.univ = 1 := by
  have hpos : 0 < n := by omega
  have h0 : (volume : Measure (EuclideanSpace ℝ (Fin n))).toSphere Set.univ ≠ 0 := by
    rw [Measure.toSphere_apply_univ]
    simp [finrank_euclideanSpace, hpos.ne', (Metric.measure_ball_pos volume (0 : EuclideanSpace ℝ (Fin n))
      one_pos).ne']
  have htop : (volume : Measure (EuclideanSpace ℝ (Fin n))).toSphere Set.univ ≠ ⊤ := by
    rw [Measure.toSphere_apply_univ]
    exact ENNReal.mul_ne_top (by simp) measure_ball_lt_top.ne
  simp only [sphereProbability, Measure.smul_apply, smul_eq_mul]
  exact ENNReal.inv_mul_cancel h0 htop

#print axioms probe_law_is_probability
""",
    },
    reading=(
        "Believed not vacuous: for n ≥ 3 the unit sphere has finite positive surface measure, so the law is a "
        "probability measure and partition = ∫ exp(...) > 0; the integrands are continuous on a compact space. "
        "Agent reading, not machine-checked."
    ),
    expected={"D1_degenerate_implies_target": "PROVED", "D2_law_is_probability": "PROVED"},
)

CASES = [CLASSICAL_ON]


def degenerate_probe_files(case: DegenerateCase, source: str) -> List[ProbeFile]:
    """One file per lemma: the challenge source with the lemma inserted before the namespace closes."""
    closing = source.rfind(f"end {case.theorem.split('.')[-2]}")
    insert_at = closing if closing >= 0 else len(source)
    files = []
    for key, lemma in case.lemmas.items():
        declaration = re.search(r"theorem\s+(\w+)", lemma).group(1)
        files.append(
            ProbeFile(
                probe_id=f"{case.case_id}:{key}",
                challenge=case.challenge,
                theorem=case.theorem,
                mode=key,
                module_path=f"ComparatorChallenges/Probes/{case.case_id.replace('-', '_')}__{key}.lean",
                text=source[:insert_at] + lemma + "\n" + source[insert_at:],
                declaration=declaration,
            )
        )
    return files
