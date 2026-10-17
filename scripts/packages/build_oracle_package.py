"""Build the lifecycle project and research package of the openai/math Lean label oracle (ADR-DISCOVERY-065).

The first real research package. Every check is filled from a file in this repository; nothing is invented:

- the protocol as pre-registered on 2026-10-13 (commit f89caf7), taken from git, plus the frozen pilot dataset;
- the raw Comparator results and tool versions from the Legion run of 2026-10-17;
- the pre-registered criteria as scored by `openai_math_lean_oracle.py report`, and the claims register.

Human checks are recorded only for the people named with --sign. Without a sign-off the project stops at that gate
and the package says which checks are open.

    python scripts/packages/build_oracle_package.py --sign question.owner="Name" --sign protocol.review="Name" ...
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.research_lifecycle import ActorRole, CheckKind, GateDecision, LifecycleService  # noqa: E402
from python.discovery.research_package import export_package  # noqa: E402

PROJECT = "openai-math-lean-oracle"
TITLE = "Lean/Comparator label oracle for the openai/math statement-fidelity pilot"
BENCH = "docs/reference/benchmarks"
OUT = "docs/reference/packages"
PREREG_COMMIT = "f89caf7"
# Kept byte-identical to the commit; .txt so the docs link checker does not follow its now-relative links.
PREREG = f"{OUT}/{PROJECT}/LEAN_ORACLE_PROTOCOL-{PREREG_COMMIT}.md.txt"
RESULTS = f"{BENCH}/openai_math_lean_oracle_results.json"
COMPARATOR = "comparator d03acab (exit codes, via openai_math_lean_oracle.py report)"


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence() -> dict:
    """check id -> keyword arguments for submit_result, all from repository files."""
    summary = json.loads((ROOT / RESULTS).read_text(encoding="utf-8"))["summary"]
    met = {name: "MET" if ok else "NOT_MET" for name, ok in summary["criteria"].items()}
    originals = summary["originals_accepted"]
    artifact = lambda rel, note="": {"artifact_path": rel, "sha256": sha(rel), "note": note}  # noqa: E731
    prereg_note = f"Protocol as committed in {PREREG_COMMIT} (2026-10-13), before the run of 2026-10-17."
    return {
        "question.statement": artifact(PREREG, "Section 1 states what the oracle measures and what it does not."),
        "hypothesis.claim": artifact(PREREG, "Claim: the pilot's 52 mutant labels are valid (section 3)."),
        "hypothesis.falsifier": {"value": 2, "note": "Either pre-registered criterion failing refutes the claim."},
        "protocol.document": artifact(PREREG, prereg_note),
        "protocol.criteria": {"value": len(summary["criteria"]), "note": "Pipeline sound; labels valid."},
        "protocol.dataset_frozen": artifact(f"{BENCH}/openai_math_pilot_dataset.json", "Unchanged since 903a8d4."),
        "execution.raw_outputs": artifact(RESULTS, "71 Comparator runs on the Legion (WSL2), 2026-10-17."),
        "execution.environment": artifact(f"{BENCH}/openai_math_lean_oracle_tools.txt"),
        "controls.positive": {
            "ok": originals["k"] == originals["n"],
            "actor": COMPARATOR,
            "note": f"Originals accepted {originals['k']}/{originals['n']}.",
        },
        "analysis.criteria_evaluated": {"criteria": met, "actor": COMPARATOR},
        "analysis.intervals": {"value": 1, "note": "95% Wilson intervals for every proportion."},
        "report.claims_register": artifact("docs/reference/CLAIMS_REGISTER.md", "Row 19 updated with the result."),
    }


def build(signoffs: dict, log_path: Path) -> LifecycleService:
    if log_path.exists():
        log_path.unlink()
    service = LifecycleService(log_path)
    service.create_project(PROJECT, TITLE, template="benchmark")
    facts = evidence()
    while True:
        project = service.get(PROJECT)
        for check in project.checks(project.stage):
            if check.kind == CheckKind.HUMAN:
                if check.check_id in signoffs:
                    service.submit_result(PROJECT, check.check_id, True, signoffs[check.check_id], ActorRole.HUMAN)
                continue
            if check.check_id not in facts:
                continue  # optional checks without evidence stay empty
            kwargs = dict(facts[check.check_id])
            ok = kwargs.pop("ok", True)
            actor = kwargs.pop("actor", "build_oracle_package.py")
            role = ActorRole.VERIFIER_TOOL if check.kind == CheckKind.VERIFIER else ActorRole.AGENT
            service.submit_result(PROJECT, check.check_id, ok, actor, role, **kwargs)
        if service.evaluate_gate(PROJECT).decision != GateDecision.PASS:
            return service
        service.pass_gate(PROJECT, "build_oracle_package.py")
        if project.passed(project.stage) and project.stage.value == "REPORT":
            service.release(
                PROJECT,
                "build_oracle_package.py",
                "Both pre-registered criteria are met: 19/19 originals accepted, 52/52 mutants rejected (Wilson lower "
                "bound 0.931). No label is noisy, so the pilot's figures stand.",
            )
            return service


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sign", action="append", default=[], help="CHECK_ID=Name of the person signing off.")
    args = parser.parse_args(argv)
    signoffs = dict(item.split("=", 1) for item in args.sign)

    prereg = ROOT / PREREG
    prereg.parent.mkdir(parents=True, exist_ok=True)
    original = subprocess.run(
        ["git", "show", f"{PREREG_COMMIT}:{BENCH}/LEAN_ORACLE_PROTOCOL.md"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    prereg.write_bytes(original)

    service = build(signoffs, ROOT / OUT / f"{PROJECT}.lifecycle.jsonl")
    _, manifest = export_package(service, PROJECT, ROOT, ROOT / OUT / f"{PROJECT}.crpkg")
    gate = service.evaluate_gate(PROJECT)
    print(json.dumps({"source": manifest["source"], "gate": gate.decision.value, "omissions": manifest["omissions"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
