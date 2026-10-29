"""
python/discovery/rule30_reasoning_bridge.py - Wolfram/Python AST to Lean 4 Reasoning Bridge (ADR-DISCOVERY-072).

Integrates the tri-phase mathematical reasoning pipeline for elementary cellular automata:
Phase 1: Python AST / Symbolic Exploration:
         Computes bitmask strip certificates (Erica Jen 1986 generalization) over local configuration strips.
Phase 2: Barrier Filtering (ADR-DISCOVERY-070):
         Tests candidate certificates against linear/additive rules (Rule 90, Rule 150).
         Rejects candidates that hold on Rule 90/150 (Realization Obstruction), ensuring that proof
         progress is structurally driven by Rule 30's non-linear OR interaction.
Phase 3: Formal Lean 4 Kernel Replay:
         Emits structured Lean 4 code targeting `Rule30Submission.lean` and verifies it
         against the official Wolfram Institute `Check.lean` verifier via Mac Studio remote execution.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from python.discovery.cellular_automata_barrier_auditor import (
    CellularAutomataBarrierAuditor,
    CellularBarrierType,
    ElementaryRule,
)


@dataclass(frozen=True)
class CandidateWord:
    """A periodic binary word to be tested for asymptotic exclusion in Rule 30."""
    pattern_str: str          # e.g. "01111111"
    length: int
    bits: int                 # Integer representation (most significant bit first)

    @classmethod
    def from_string(cls, pattern: str) -> CandidateWord:
        clean = pattern.strip()
        length = len(clean)
        bits = int(clean, 2) if clean else 0
        return cls(pattern_str=clean, length=length, bits=bits)

    def to_bool_list(self) -> List[bool]:
        return [ch == "1" for ch in self.pattern_str]


@dataclass
class StripCertificateVerdict:
    """Outcome of exploring and auditing a bitmask strip certificate for word exclusion."""
    word: CandidateWord
    strip_width_K: int
    warmup_k: int
    holds_on_rule30: bool
    holds_on_rule90: bool
    holds_on_rule150: bool
    is_barrier_cleared: bool
    barrier_critique: str
    generated_lean_code: Optional[str] = None
    remote_verification_report: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": {
                "pattern": self.word.pattern_str,
                "length": self.word.length,
                "bits": self.word.bits,
            },
            "strip_width_K": self.strip_width_K,
            "warmup_k": self.warmup_k,
            "holds_on_rule30": self.holds_on_rule30,
            "holds_on_rule90": self.holds_on_rule90,
            "holds_on_rule150": self.holds_on_rule150,
            "is_barrier_cleared": self.is_barrier_cleared,
            "barrier_critique": self.barrier_critique,
            "remote_verification_report": self.remote_verification_report,
        }


class BitmaskStripCertificateExplorer:
    """
    Symbolic state-space explorer for bitmask strip certificates.
    Implements the exact bitmask transition semantics formalized in
    `Ruliology.CellularAutomata.Rule30StripCertificates`.
    """

    @staticmethod
    def strip_step_rule30(K: int, a: bool, z: bool, r: int) -> int:
        """
        One step of a K-cell strip for Rule 30: left ^ (center | right).
        Matches Lean's `stripStep K a z r`.
        """
        left_term = (r << 1) | int(a)
        right_term = r | (r >> 1) | (int(z) << (K - 1))
        return (left_term ^ right_term) % (1 << K)

    @staticmethod
    def strip_step_rule90(K: int, a: bool, z: bool, r: int) -> int:
        """One step of a K-cell strip for linear Rule 90: left ^ right."""
        left_term = (r << 1) | int(a)
        right_term = (r >> 1) | (int(z) << (K - 1))
        return (left_term ^ right_term) % (1 << K)

    @staticmethod
    def strip_step_rule150(K: int, a: bool, z: bool, r: int) -> int:
        """One step of a K-cell strip for linear additive Rule 150: left ^ center ^ right."""
        left_term = (r << 1) | int(a)
        center_term = r
        right_term = (r >> 1) | (int(z) << (K - 1))
        return (left_term ^ center_term ^ right_term) % (1 << K)

    @classmethod
    def image(cls, rule: ElementaryRule, K: int, a: bool, states: Set[int]) -> Set[int]:
        """All successors of strip states for both values of the unknown right boundary cell."""
        step_fn = cls.strip_step_rule30
        if rule == ElementaryRule.RULE_90:
            step_fn = cls.strip_step_rule90
        elif rule == ElementaryRule.RULE_150:
            step_fn = cls.strip_step_rule150

        succ: Set[int] = set()
        for r in states:
            succ.add(step_fn(K, a, False, r))
            succ.add(step_fn(K, a, True, r))
        return succ

    @classmethod
    def apply_word(cls, rule: ElementaryRule, K: int, word: List[bool], states: Set[int]) -> Set[int]:
        """Evolves strip states across a sequence of letters (word)."""
        curr = states
        for a in word:
            curr = cls.image(rule, K, a, curr)
        return curr

    @classmethod
    def evaluate_strip_certificate(
        cls,
        rule: ElementaryRule,
        word: List[bool],
        K: int,
        k_warmup: int,
    ) -> bool:
        """
        Verifies whether (K, k_warmup) forms a sound bitmask strip certificate for `word`:
        1. S0 (reachable after k periods) is an invariant trap: applyWord(w, S0) ⊆ S0.
        2. At every white phase (w[phi] == 0), column 1 (bit 0 of state) is constant across all reachable states.
        """
        full_set = set(range(1 << K))
        s0 = full_set
        for _ in range(k_warmup):
            s0 = cls.apply_word(rule, K, word, s0)

        # Trap check: S_next ⊆ S0
        s_next = cls.apply_word(rule, K, word, s0)
        if not s_next.issubset(s0):
            return False

        # White phase constancy check
        for phi in range(len(word)):
            if word[phi]:
                continue  # Black phase, no restriction on column 1
            s_phi = cls.apply_word(rule, K, word[:phi], s0)
            col1_values = {(r & 1) for r in s_phi}
            if len(col1_values) > 1:
                return False

        return True


class Rule30ReasoningBridge:
    """
    End-to-end reasoning bridge connecting Python AST exploration,
    Barrier Auditing, and Lean 4 formal certification.
    """

    def __init__(self, remote_host: str = "mac_studio") -> None:
        self.explorer = BitmaskStripCertificateExplorer()
        self.barrier_auditor = CellularAutomataBarrierAuditor()
        self.remote_host = remote_host

    def explore_word_certificate(
        self,
        word_pattern: str,
        strip_width_K: int = 5,
        warmup_k: int = 2,
    ) -> StripCertificateVerdict:
        """
        Explores whether a candidate periodic word can be excluded via strip certificates,
        filtering against realization barriers.
        """
        word = CandidateWord.from_string(word_pattern)
        w_bools = word.to_bool_list()

        # Phase 1: Rule 30 evaluation
        holds_r30 = self.explorer.evaluate_strip_certificate(
            ElementaryRule.RULE_30, w_bools, strip_width_K, warmup_k
        )

        # Phase 2: Barrier filter (Rule 90 & Rule 150)
        holds_r90 = self.explorer.evaluate_strip_certificate(
            ElementaryRule.RULE_90, w_bools, strip_width_K, warmup_k
        )
        holds_r150 = self.explorer.evaluate_strip_certificate(
            ElementaryRule.RULE_150, w_bools, strip_width_K, warmup_k
        )

        is_cleared = False
        critique = ""

        if not holds_r30:
            critique = f"Certificate (K={strip_width_K}, k={warmup_k}) fails on Rule 30."
        elif holds_r90 or holds_r150:
            falsifying = []
            if holds_r90:
                falsifying.append("Rule 90")
            if holds_r150:
                falsifying.append("Rule 150")
            critique = (
                f"REALIZATION BARRIER OBSTRUCTION: Certificate holds on {', '.join(falsifying)}. "
                "Because center column is eventually constant on these rules, this certificate "
                "is provably insufficient for non-linear aperiodicity."
            )
        else:
            is_cleared = True
            critique = (
                f"BARRIER CLEARED: Certificate holds on Rule 30 and breaks on Rule 90 and Rule 150. "
                "Structural dependence on non-linear boolean OR interaction confirmed."
            )

        lean_code = None
        if is_cleared:
            lean_code = self.generate_lean_code(word, strip_width_K, warmup_k)

        return StripCertificateVerdict(
            word=word,
            strip_width_K=strip_width_K,
            warmup_k=warmup_k,
            holds_on_rule30=holds_r30,
            holds_on_rule90=holds_r90,
            holds_on_rule150=holds_r150,
            is_barrier_cleared=is_cleared,
            barrier_critique=critique,
            generated_lean_code=lean_code,
        )

    @staticmethod
    def generate_lean_code(word: CandidateWord, K: int, k: int) -> str:
        """Generates sound Lean 4 code declaring and proving word exclusion."""
        bool_list_str = "[" + ", ".join("true" if b == "1" else "false" for b in word.pattern_str) + "]"
        safe_name = f"not_eventually_word_{word.pattern_str}"
        return (
            "import Rule30PrizeKit\n"
            "import Ruliology.CellularAutomata.Rule30StripCertificates\n\n"
            "namespace Rule30Submission\n\n"
            "open Ruliology.CellularAutomata\n"
            "open Ruliology.CellularAutomata.Rule30StripCertificates\n\n"
            f"/-- The periodic word {word.pattern_str} is excluded as an eventual repeating word of Rule 30 center column. -/\n"
            f"theorem {safe_name} :\n"
            f"    ¬ EventuallyWord {bool_list_str} :=\n"
            f"  not_eventually_word_strip {bool_list_str} {K} {k} (by decide)\n"
            "    (by decide) (by decide +kernel)\n\n"
            "end Rule30Submission\n"
        )

    def dispatch_and_verify_remote(
        self,
        verdict: StripCertificateVerdict,
        theorem_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches the generated Lean 4 proof to Mac Studio, executes kernel replay,
        and returns the official JSON verification report.
        """
        if not verdict.is_barrier_cleared or not verdict.generated_lean_code:
            return {
                "verdict": "blocked_by_barrier",
                "error": "Cannot submit proof blocked by realization barriers or failing on Rule 30.",
            }

        name = theorem_name or f"not_eventually_word_{verdict.word.pattern_str}"

        # Write Rule30Submission.lean remotely via ssh
        remote_script = f"""
with open('/Users/neuroia/Rule30PrizeKit/Rule30Submission.lean', 'w') as f:
    f.write('''{verdict.generated_lean_code}''')
"""
        write_res = subprocess.run(
            ["ssh", self.remote_host, "python3", "-"],
            input=remote_script,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if write_res.returncode != 0:
            return {"verdict": "error", "error": f"Failed to write submission: {write_res.stderr}"}

        # Build and check
        check_cmd = (
            f"env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin:/Users/neuroia/.elan/bin "
            f"HOME=/Users/neuroia USER=neuroia /bin/sh -c '"
            f"cd ~/Rule30PrizeKit && lake build Rule30Submission && "
            f"lake env lean --run Check.lean Rule30Submission --claim partial --headline Rule30Submission.{name}'"
        )
        check_res = subprocess.run(
            ["ssh", self.remote_host, check_cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        stdout = check_res.stdout
        # Extract the trailing JSON line
        json_output: Dict[str, Any] = {}
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    json_output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        verdict.remote_verification_report = {
            "exit_code": check_res.returncode,
            "raw_output": stdout[-1000:],
            "parsed_json": json_output,
            "is_verified": json_output.get("verdict") == "pass",
        }

        return verdict.remote_verification_report
