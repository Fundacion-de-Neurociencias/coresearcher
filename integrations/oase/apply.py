"""Install the `oase formal` adapter into an OASE checkout (called by apply.sh).

OASE has no plugin mechanism, so the adapter is installed by editing seven of
its files and adding two. Every edit is anchored on a line that exists at the
pinned commit and is idempotent: applying twice changes nothing the second
time, and an anchor that is missing stops the install instead of guessing a
place. `--dry-run` prints the unified diff and writes nothing.

    python3 integrations/oase/apply.py --oase <checkout>/applications/open-agentic-science-engine [--dry-run]
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED_COMMIT = "b7e5e3576668ba9630f053e93389b21bbc2e67f6"
SKILL = "formal-hypothesis-verification"
DEFAULT_SKILL_URI = (
    "https://github.com/Fundacion-de-Neurociencias/coresearcher/tree/master/" f"integrations/oase/skills/{SKILL}"
)
TEMPLATES = ("hypex-reflection", "scientific-reviewer", "science-program-lead")
MARKER = "coresearcher formal adapter"


class AnchorError(RuntimeError):
    """The OASE file no longer looks like the pinned commit; nothing is guessed."""


# Relay codes: OASE code -> obligation (OASE writes relays as instructions).
RELAYS = {
    "formal.not_empirical": (
        "Do not cite a formal verdict as support for the hypothesis being true. "
        "FALSIFIABLE, consistent or entailed describes the formal object; whether "
        "its premises hold in the world is a separate, empirical question."
    ),
    "formal.smt_fixed_size_only": (
        "Scope the verdict to the declared variables and bounds. Decided by z3 for "
        "those only; do not generalize it to other sizes or to a parametric claim."
    ),
    "formal.enumeration_declared_domains_only": (
        "Scope the verdict to the declared finite domains. Values outside them " "were never considered."
    ),
    "formal.lean_not_kernel_checked": (
        "Report the Lean 4 statement as a claim, not a proof. No Lean kernel " "checked it."
    ),
    "formal.formalization_is_draft": (
        "State that the formal object came from a language model and is a draft "
        "until a researcher confirms it says what the prose meant. Do not attribute "
        "the verdict to the prose hypothesis before that."
    ),
    "formal.gate_single_sample": (
        "State that the formalizer was sampled once: there is no self-consistency " "evidence for this reading."
    ),
    "formal.vacuous_entailment": (
        "Do not report this consequence as a prediction of the hypothesis. It is "
        "entailed only because no applicable state is allowed."
    ),
    "formal.entailed_by_assumptions_alone": (
        "Do not credit the hypothesis with this consequence. It follows from the "
        "domains, scope and assumptions without the claims."
    ),
    "formal.thresholds_overridden": (
        "Quote threshold_sources with the verdict: at least one engine threshold " "differs from the versioned default."
    ),
    "formal.formalization_ambiguous": (
        "Report that the formalizer produced disagreeing readings. Do not evaluate, "
        "rank or pick one: the hypothesis has no formal verdict until a reading is "
        "confirmed."
    ),
    "formal.formalization_failed": (
        "Report that no valid formal object was produced. There is no formal " "verdict; do not infer one."
    ),
    "formal.undecided": (
        "Report the question as undecided. The solver gave up; this is not evidence "
        "that the hypothesis is unsound, unfalsifiable or refuted."
    ),
    "formal.blocked": (
        "Report the check as blocked by a missing capability or threshold. Nothing "
        "was assessed: record not_assessed, never a negative."
    ),
    "formal.not_reproduced": (
        "Treat the run's verdict as unverified. Re-analysis from the stored "
        "artifacts did not reproduce it under the same thresholds."
    ),
    "formal.vacuous_relative_to_intent": (
        "Return the hypothesis to its author with the witness in intent_probe: "
        "its claims hold of an object it declared it must exclude."
    ),
    "formal.trivial_witness_satisfies_claims": (
        "Show the satisfied default probe with the verdict and ask whether the "
        "claims were meant to exclude it. It does not change the verdict."
    ),
    "formal.claim_below_kernel_checked": (
        "State each claim's trust rung from claim_trust. Do not call a claim "
        "checked or proved unless its rung is KERNEL_CHECKED or higher."
    ),
    "formal.fidelity_range_only": (
        "Scope the fidelity relation to the hypothesis range. Conclusions were "
        "not compared and the transcriptions were taken as given."
    ),
    "formal.lint_is_syntactic": (
        "Treat OPEN findings as questions for a human, not defects, and read "
        "each DISCHARGED reason before relying on it."
    ),
}


def _relay_block() -> str:
    lines = [f"    # --- formal ({MARKER}, ADR-DISCOVERY-069) ---"]
    for code, message in RELAYS.items():
        lines.append(f"    {json.dumps(code)}: (")
        words, line = message.split(), ""
        chunks = []
        for word in words:
            if len(line) + len(word) + 1 > 66:
                chunks.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        chunks.append(line)
        for i, chunk in enumerate(chunks):
            text = chunk + (" " if i < len(chunks) - 1 else "")
            lines.append(f"        {json.dumps(text)}")
        lines.append("    ),")
    return "\n".join(lines) + "\n"


THRESHOLD_BLOCK = f"""# --- formal ({MARKER}, ADR-DISCOVERY-069) ----------------------
# CoResearcher's formal soundness verdicts. The engine thresholds bound the
# computation and equal CoResearcher's versioned set formal@2026.10.1; a
# different value here reaches the engine as an override and fires
# formal.thresholds_overridden. max_formal_defects is definitional: a
# VACUOUS, SELF_CONTRADICTORY or UNFALSIFIABLE object is a defect by the
# ADR-DISCOVERY-059 definitions, and a sound object has none. How much of the
# applicable state space a hypothesis must forbid has no published value, so
# min_excluded_fraction_of_applicable is UNRESOLVED.
_declare(
    "formal",
    "1.0",
    provenance=(
        "CoResearcher formal@2026.10.1 (ADR-DISCOVERY-068): max_states and "
        "max_assumptions_for_conflict_search are engineering caps (ADR-059); "
        "solver_timeout_ms per z3 call, a timeout is UNDECIDED (ADR-060); gate_* "
        "from the ADR-064 self-consistency gate and its N=3/5/7 ablation; "
        "formalizer_* frozen decoding of the ADR-061 benchmark. "
        "max_formal_defects: definitional (ADR-059 content verdicts). "
        "min_excluded_fraction_of_applicable: no defensible published value."
    ),
    values={{
        "max_states": 2_000_000,
        "max_assumptions_for_conflict_search": 12,
        "solver_timeout_ms": 10_000,
        "gate_samples": 5,
        "gate_max_samples": 7,
        "gate_temperature": 0.7,
        "gate_majority_fraction": 0.5,
        "formalizer_temperature": 0.0,
        "formalizer_seed": 0,
        "max_formal_defects": 0,
        "min_excluded_fraction_of_applicable": UNRESOLVED,
    }},
)

"""

DOCTOR_FUNCTION = f'''def _check_formal_verifier(report: Report) -> None:
    """CoResearcher formal verifier behind `oase formal` ({MARKER})."""
    from .formal import capability_checks

    for name, ok, detail, remedy, kind in capability_checks():
        status = OK if ok else WARN
        report.add(name, status, detail, remedy, kind=CAPABILITY if kind == "capability" else CAVEAT)


'''


def _insert_before(text: str, anchor: str, block: str, where: str) -> str:
    index = text.find(anchor)
    if index < 0:
        raise AnchorError(f"{where}: anchor not found: {anchor.strip()!r}")
    return text[:index] + block + text[index:]


def _insert_after_line(text: str, anchor: str, block: str, where: str) -> str:
    index = text.find(anchor)
    if index < 0:
        raise AnchorError(f"{where}: anchor not found: {anchor.strip()!r}")
    end = text.index("\n", index) + 1
    return text[:end] + block + text[end:]


def patch_cli(text: str) -> str:
    if "from .commands.formal import formal" in text:
        return text
    text = _insert_after_line(
        text, "from .commands.faers import faers", "from .commands.formal import formal\n", "cli.py"
    )
    # Before enforce_phase_two(cli): the walk guards what is registered when it runs.
    last = text.rfind("\ncli.add_command(")
    guard = text.find("\nenforce_phase_two(cli)")
    if last < 0 or guard < 0 or last > guard:
        raise AnchorError("cli.py: no cli.add_command(...) line before enforce_phase_two(cli)")
    end = text.index("\n", last + 1) + 1
    return text[:end] + "cli.add_command(formal)\n" + text[end:]


def patch_context(text: str) -> str:
    if '"formal": "raw/formal"' in text:
        return text
    start = text.find("ARTIFACT_DIRS: dict[str, str] = {")
    if start < 0:
        raise AnchorError("core/context.py: ARTIFACT_DIRS literal not found")
    close = text.find("\n}\n", start)
    return text[: close + 1] + '    "formal": "raw/formal",\n' + text[close + 1 :]


def patch_thresholds(text: str) -> str:
    if '_declare(\n    "formal",' in text:
        return text
    return _insert_before(
        text,
        "# Warnings that must reach the report whenever these sets are applied.",
        THRESHOLD_BLOCK,
        "core/thresholds.py",
    )


def patch_provenance(text: str) -> str:
    if '"formal.not_empirical"' in text:
        return text
    return _insert_after_line(text, "RELAY_CODES: dict[str, str] = {", _relay_block(), "core/provenance.py")


def patch_doctor(text: str) -> str:
    if "_check_formal_verifier" in text:
        return text
    text = _insert_after_line(
        text,
        "    _check_hypothesis_strategies(report)\n",
        "    _check_formal_verifier(report)\n",
        "commands/doctor.py",
    )
    return _insert_before(text, "def _check_phase_two_contract(", DOCTOR_FUNCTION, "commands/doctor.py")


def patch_template(text: str, uri: str, where: str) -> str:
    line = f'  - uri: "{uri}"\n'
    if line in text:
        return text
    last = text.rfind('\n  - uri: "')
    if last < 0:
        raise AnchorError(f"{where}: no skills list")
    end = text.index("\n", last + 1) + 1
    return text[:end] + line + text[end:]


def plan(oase: Path, skill_uri: str) -> list[tuple[Path, str | None, str]]:
    """(path, current content or None for a new file, new content) for every change."""
    edits = [
        ("tools/oase/cli.py", patch_cli),
        ("tools/oase/core/context.py", patch_context),
        ("tools/oase/core/thresholds.py", patch_thresholds),
        ("tools/oase/core/provenance.py", patch_provenance),
        ("tools/oase/commands/doctor.py", patch_doctor),
    ]
    out = []
    for rel, fn in edits:
        path = oase / rel
        if not path.is_file():
            raise AnchorError(f"{rel} does not exist; is {oase} an OASE engine directory?")
        old = path.read_text(encoding="utf-8")
        out.append((path, old, fn(old)))
    for template in TEMPLATES:
        path = oase / "templates" / template / "scion-agent.yaml"
        old = path.read_text(encoding="utf-8")
        out.append((path, old, patch_template(old, skill_uri, str(path.relative_to(oase)))))
    copies = [
        (HERE / "formal.py", oase / "tools/oase/commands/formal.py"),
        (HERE / "skills" / SKILL / "SKILL.md", oase / "skills" / SKILL / "SKILL.md"),
    ]
    for src, dest in copies:
        old = dest.read_text(encoding="utf-8") if dest.is_file() else None
        out.append((dest, old, src.read_text(encoding="utf-8")))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--oase", required=True, type=Path, help="OASE engine directory")
    parser.add_argument("--dry-run", action="store_true", help="print the diff, write nothing")
    parser.add_argument("--skill-uri", default=DEFAULT_SKILL_URI, help="URI granted in the templates")
    args = parser.parse_args(argv)
    oase = args.oase.resolve()
    try:
        changes = plan(oase, args.skill_uri)
    except (AnchorError, OSError) as exc:
        print(f"apply: {exc}", file=sys.stderr)
        return 2
    changed = [(p, old, new) for p, old, new in changes if old != new]
    if args.dry_run:
        for path, old, new in changed:
            rel = path.relative_to(oase).as_posix()
            sys.stdout.writelines(
                difflib.unified_diff(
                    (old or "").splitlines(keepends=True),
                    new.splitlines(keepends=True),
                    fromfile="/dev/null" if old is None else f"a/{rel}",
                    tofile=f"b/{rel}",
                )
            )
        print(f"# {len(changed)} file(s) would change", file=sys.stderr)
        return 0
    for path, _old, new in changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8", newline="\n")
        print(f"patched {path.relative_to(oase).as_posix()}")
    if not changed:
        print("already applied; nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
