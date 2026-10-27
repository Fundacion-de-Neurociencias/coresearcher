"""The `oase formal` adapter, checked without OASE (ADR-DISCOVERY-069).

OASE is POSIX-only (it imports fcntl), so everything that needs an OASE checkout runs in the CI job
`oase-conformance` (integrations/oase/tests). These tests run everywhere: the installer's edits on
synthetic anchors, the consistency of the threshold set, relay registry, skill and code, and the
committed demo artifacts, recomputed here with CoResearcher alone.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path

import pytest

from python.discovery import formal_pipeline, formal_provenance, formal_thresholds
from python.discovery.formal_status import RELAY_CODES as CR_RELAYS

ADAPTER = Path(__file__).resolve().parents[1] / "integrations" / "oase"
DEMO = ADAPTER / "demo"
FORMAL = DEMO / "artifacts" / "raw" / "formal"
STATUS_RELAYS = ("UNDECIDED", "BLOCKED", "FORMALIZATION_AMBIGUOUS", "FORMALIZATION_FAILED")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


apply = _load("oase_apply", ADAPTER / "apply.py")
make_assessment = _load("oase_make_assessment", DEMO / "make_assessment.py")


def _adapter_mapping() -> dict:
    """The CoResearcher -> OASE relay mapping, read from formal.py (which imports OASE and cannot load here)."""
    tree = ast.parse((ADAPTER / "formal.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_oase_code")
    assign = next(n for n in fn.body if isinstance(n, ast.Assign) and n.targets[0].id == "mapping")
    return ast.literal_eval(assign.value)


def _declared_set() -> dict:
    captured = {}
    namespace = {
        "_declare": lambda name, version, provenance, values: captured.update(
            name=name, version=version, provenance=provenance, values=values
        ),
        "UNRESOLVED": "UNRESOLVED",
    }
    exec(apply.THRESHOLD_BLOCK, namespace)  # The literal block apply.py inserts into thresholds.py.
    return captured


# ---------------------------------------------------------------------------
# Installer
# ---------------------------------------------------------------------------

CLI = "from .commands.faers import faers\nfrom .common import x\n\ncli.add_command(a)\ncli.add_command(b)\n\nenforce_phase_two(cli)\n"
CONTEXT = 'ARTIFACT_DIRS: dict[str, str] = {\n    "admet": "raw/admet",\n}\n\n\ndef f():\n    pass\n'
THRESHOLDS = (
    "x = 1\n\n# Warnings that must reach the report whenever these sets are applied.\nMANDATORY_ADVISORIES = {}\n"
)
PROVENANCE = 'RELAY_CODES: dict[str, str] = {\n    "a.b": "c",\n}\n'
DOCTOR = "def _check_phase_two_contract(report):\n    pass\n\n\ndef run(report):\n    _check_hypothesis_strategies(report)\n    _check_phase_two_contract(report)\n"
TEMPLATE = 'skills:\n  - uri: "https://example.org/skills/a"\n  - uri: "https://example.org/skills/b"\n'


@pytest.mark.parametrize(
    "fn,text",
    [
        (apply.patch_cli, CLI),
        (apply.patch_context, CONTEXT),
        (apply.patch_thresholds, THRESHOLDS),
        (apply.patch_provenance, PROVENANCE),
        (apply.patch_doctor, DOCTOR),
    ],
)
def test_each_edit_is_idempotent_and_valid_python(fn, text):
    once = fn(text)
    assert once != text
    assert fn(once) == once
    ast.parse(once)


def test_cli_edit_registers_before_the_phase_two_walk():
    out = apply.patch_cli(CLI)
    assert out.index("cli.add_command(formal)") < out.index("enforce_phase_two(cli)")
    assert out.index("cli.add_command(b)") < out.index("cli.add_command(formal)")
    assert "from .commands.formal import formal\n" in out


def test_registry_edits_land_inside_their_literals():
    ns = {"UNRESOLVED": object(), "_declare": lambda *a, **k: None}
    exec(apply.patch_context(CONTEXT), ns)
    assert ns["ARTIFACT_DIRS"]["formal"] == "raw/formal"
    exec(apply.patch_provenance(PROVENANCE), ns)
    assert set(apply.RELAYS) <= set(ns["RELAY_CODES"]) and ns["RELAY_CODES"]["a.b"] == "c"
    assert ns["RELAY_CODES"]["formal.not_reproduced"] == apply.RELAYS["formal.not_reproduced"]


def test_template_grant_is_appended_once():
    out = apply.patch_template(TEMPLATE, apply.DEFAULT_SKILL_URI, "t")
    assert out.endswith(f'  - uri: "{apply.DEFAULT_SKILL_URI}"\n')
    assert apply.patch_template(out, apply.DEFAULT_SKILL_URI, "t") == out


def test_a_moved_anchor_stops_the_install():
    with pytest.raises(apply.AnchorError):
        apply.patch_cli("cli.add_command(a)\n")
    with pytest.raises(apply.AnchorError):
        apply.patch_doctor("def f():\n    pass\n")


def test_dry_run_writes_nothing(tmp_path, capsys):
    oase = tmp_path / "oase"
    files = {
        "tools/oase/cli.py": CLI,
        "tools/oase/core/context.py": CONTEXT,
        "tools/oase/core/thresholds.py": THRESHOLDS,
        "tools/oase/core/provenance.py": PROVENANCE,
        "tools/oase/commands/doctor.py": DOCTOR,
        **{f"templates/{t}/scion-agent.yaml": TEMPLATE for t in apply.TEMPLATES},
    }
    for rel, text in files.items():
        (oase / rel).parent.mkdir(parents=True, exist_ok=True)
        (oase / rel).write_text(text, encoding="utf-8")
    assert apply.main(["--oase", str(oase), "--dry-run"]) == 0
    diff = capsys.readouterr().out
    assert "+cli.add_command(formal)" in diff and "+++ b/tools/oase/commands/formal.py" in diff
    assert not (oase / "tools/oase/commands/formal.py").exists()
    assert (oase / "tools/oase/cli.py").read_text(encoding="utf-8") == CLI
    assert apply.main(["--oase", str(oase)]) == 0
    assert (oase / "skills/formal-hypothesis-verification/SKILL.md").is_file()
    capsys.readouterr()
    assert apply.main(["--oase", str(oase)]) == 0
    assert "already applied" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Thresholds, relays and skill agree with the engine and with each other
# ---------------------------------------------------------------------------


def test_threshold_set_engine_values_equal_coresearcher_defaults():
    declared = _declared_set()
    assert (declared["name"], declared["version"]) == ("formal", "1.0")
    values = declared["values"]
    for key, value in formal_thresholds.FORMAL_DEFAULTS.values.items():
        assert values[key] == value, f"{key}: formal@1.0 would silently override the engine"
    assert values["max_formal_defects"] == 0
    assert values["min_excluded_fraction_of_applicable"] == "UNRESOLVED"


def test_every_coresearcher_relay_and_non_verdict_has_a_registered_oase_code():
    mapping = _adapter_mapping()
    assert set(CR_RELAYS) | set(STATUS_RELAYS) == set(mapping)
    assert set(mapping.values()) | {"formal.not_reproduced"} == set(apply.RELAYS)
    assert all(re.fullmatch(r"formal\.[a-z_]+", code) for code in apply.RELAYS)


def test_skill_has_the_six_sections_and_names_every_relay():
    text = (ADAPTER / "skills" / "formal-hypothesis-verification" / "SKILL.md").read_text(encoding="utf-8")
    front, body = text.split("---\n", 2)[1:]
    assert "description:" in front and "Do not use" in front
    headings = re.findall(r"^## (.+)$", body, flags=re.M)
    assert headings == [
        "When to use, and when not",
        "Preconditions",
        "Tool Invocations",
        "Interpretation contract",
        "Failure modes and the anti-fabrication guard",
    ]
    assert "Do not decide these questions yourself" in body
    table = re.findall(r"^\| `(formal\.[a-z_]+)` \|", body, flags=re.M)
    assert sorted(table) == sorted(apply.RELAYS)
    assert "UNRESOLVED" in body and "Do not invent one" in body
    assert len(body.splitlines()) < 200
    # Scope: a formal check never grades evidence or citations.
    formal_py = (ADAPTER / "formal.py").read_text(encoding="utf-8")
    assert '["evidence"]' not in formal_py and '.get("evidence")' not in formal_py


# ---------------------------------------------------------------------------
# The committed demo
# ---------------------------------------------------------------------------

DEMO_EXPECTED = {
    "fm-H-0001_vs_H-0002": ("DECIDED", "FALSIFIABLE", "supported"),
    "fm-H-0002": ("DECIDED", "FALSIFIABLE", "supported"),
    "fm-H-0003": ("DECIDED", "SELF_CONTRADICTORY", "contradicted"),
    "fm-H-0004": ("DECIDED", "UNFALSIFIABLE", "contradicted"),
    "blocked/fm-H-0001": ("BLOCKED", None, "not_assessed"),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("stem", sorted(DEMO_EXPECTED))
def test_demo_artifacts_match_their_checksums_and_the_report(stem):
    meta = _json(FORMAL / f"{stem}.meta.json")
    for entry in meta["outputs"]:
        data = (FORMAL / stem).parent.joinpath(entry["path"]).read_bytes()
        assert formal_provenance.sha256_bytes(data) == entry["sha256"], entry["path"]
        assert len(data) == entry["bytes"]
    record = _json(FORMAL / f"{stem}.analysis.json")
    status, verdict, evidence = DEMO_EXPECTED[stem]
    a = record["assessment"]
    assert a["formal_status"] == status
    assert a["criteria"]["content_verdict"] == verdict
    assert a["evidence_assessment"]["evidence_status"] == evidence
    assert record["threshold_set"] == "formal@1.0"
    assert "formal.not_empirical" in [r["code"] for r in record["mandatory_relays"]] or status != "DECIDED"


@pytest.mark.parametrize("stem", [s for s, e in DEMO_EXPECTED.items() if e[0] == "DECIDED"])
def test_demo_verdicts_recompute_with_coresearcher_alone(stem):
    """The stored formal request, recomputed on this platform, gives the same report digests."""
    request = _json(FORMAL / f"{stem}.request.json")["coresearcher_request"]
    stored = _json(FORMAL / f"{stem}.response.json")["coresearcher_response"]
    response = formal_pipeline.compute(request)
    assert formal_pipeline.report_digests(response) == formal_pipeline.report_digests(stored)


def test_rival_comparison_names_the_discriminating_experiment():
    a = _json(FORMAL / "fm-H-0001_vs_H-0002.analysis.json")["assessment"]
    comparison = a["reports"]["comparisons"][0]
    assert comparison["relation"] == "INCOMPARABLE"
    forbidden_by = {
        json.dumps(e["state"], sort_keys=True): e["forbidden_by"] for e in comparison["discriminating_examples"]
    }
    early_normal_agonist = {"stage": "early", "trem2_function": "normal", "treatment": "agonist"}
    assert (
        forbidden_by[json.dumps({**early_normal_agonist, "dystrophy_change": "decrease"}, sort_keys=True)] == "H-0002"
    )
    assert forbidden_by[json.dumps({**early_normal_agonist, "dystrophy_change": "none"}, sort_keys=True)] == "H-0001"


@pytest.mark.parametrize("n,stem", [("001", "fm-H-0001_vs_H-0002"), ("002", "fm-H-0003"), ("003", "blocked/fm-H-0001")])
def test_gate_assessments_are_built_from_the_analyses(n, stem):
    analysis = Path("raw/formal") / f"{stem}.analysis.json"
    committed = _json(DEMO / "artifacts" / "gate" / f"gate-AR-{n}.json")
    rebuilt = make_assessment.build(DEMO / "artifacts" / analysis, f"AR-{n}")
    rebuilt["evidence"]["analysis_path"] = analysis.as_posix()
    assert rebuilt == committed
    if committed["execution_outcome"] != "completed":
        assert committed["evidence_status"] == "not_assessed"


def test_gate_policy_example_names_the_formal_threshold_set():
    gp = _json(ADAPTER / "gate" / "GP-001.formal-soundness.json")
    cutoff = gp["requirements"][0]
    assert cutoff["type"] == "scientific_cutoff"
    assert cutoff["evidence_type"] == "formal-soundness"
    assert (cutoff["threshold_set"], cutoff["threshold_key"]) == ("formal@1.0", "max_formal_defects")
    assert _declared_set()["values"][gp["requirements"][1]["threshold_key"]] == "UNRESOLVED"
