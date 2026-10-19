# ADR-DISCOVERY-069: `oase formal` — CoResearcher as the formal hypothesis verifier of OASE

**Status:** Accepted
**Date:** 2026-10-19
**Modules:** [`integrations/oase/formal.py`](../../integrations/oase/formal.py),
[`integrations/oase/apply.sh`](../../integrations/oase/apply.sh) and [`apply.py`](../../integrations/oase/apply.py),
[`integrations/oase/skills/formal-hypothesis-verification/SKILL.md`](../../integrations/oase/skills/formal-hypothesis-verification/SKILL.md),
[`integrations/oase/ci/conformance.sh`](../../integrations/oase/ci/conformance.sh)
**Builds on:** ADR-DISCOVERY-068 (provenance, non-verdict statuses, thresholds, relays, two-phase CLI)
**Target:** OASE, `GoogleCloudPlatform/LifeSciences`, `applications/open-agentic-science-engine`, Apache 2.0, pinned at
`b7e5e3576668ba9630f053e93389b21bbc2e67f6` (2026-10-16)

## Context

Google's Open Agentic Science Engine (OASE) runs multi-agent drug-discovery programs. Its tool layer is strict about
provenance: every tool has a phase 1 that records (`.meta.json` sidecar with sha256 of each output) and an offline
phase 2 that decides (`.analysis.json` written through `provenance.write_analysis`, which refuses to replace a
differing verdict), thresholds are named and versioned with an `UNRESOLVED` sentinel, mandatory relays are registered
codes, and exit codes separate answer, refusal and failure. Its hypotheses are prose: hypex scores them with LLM
rubrics and ranks them by Elo. Nothing in OASE checks whether a hypothesis is logically consistent, whether it can be
falsified, or whether two hypotheses contradict each other; there is no z3 or Lean in the tree.

ADR-068 made CoResearcher's formal verdicts auditable in OASE's own terms. This ADR is step 2 of the agreed plan: the
adapter. Step 3 (contacting the OASE team, contributing to their governance issues #194–#198, any upstream pull request
or fork) is the owner's decision and is not taken here. The adapter therefore lives in this repository, under
`integrations/oase/`, and is installed into an OASE checkout by a script. OASE has no plugin mechanism, so installing
means editing its CLI and registries.

Scope is unchanged: CoResearcher judges formal soundness only. The adapter never reads, grades or checks evidence,
citations, data or sources. The hypex `evidence` field is never read.

## Decision

### 1. `oase formal run | analyze | doctor`, written to OASE's contract

`integrations/oase/formal.py` is an OASE command module (`ARTIFACT_CLASS = "formal"`, `THRESHOLD_SET = "formal"`),
copied to `tools/oase/commands/formal.py`.

- **`run`** (phase 1) takes a hypex `H-NNNN.json`, or an `oase.hypothesis-set.v1` artifact with `--candidate`. Only
  `id`, `title` and `statement` are read. The formal object comes from `--formal` (authored or confirmed by a
  researcher); without it the statement is formalized by the configured model and gated for self-consistency
  (ADR-064). Rivals (`--rival`, formal objects over the same variables) are compared; `--consequence` predicates are
  checked for entailment; `--lean` states them as Lean theorems. Identity is checked, not assumed: a formal object
  whose `hypothesis_id` differs from the hypothesis, an unknown or ambiguous `--candidate`, or a rival with the
  hypothesis's own id is refused (exit 9). Two transports:
  - `package` (default): `formal_pipeline.compute` in-process. Stores the raw model outputs, so phase 2 can re-run the
    gate offline.
  - `http`: `POST /api/hypotheses/evaluate`, `/compare`, `/entails` on `CORESEARCHER_URL` through OASE's paced
    `core.http` client; every exchange is stored. Prose is refused on this transport (exit 9): the API does not return
    the raw model outputs, and a formalization that `analyze` cannot re-check is not recorded.

  Outputs, under `ARTIFACT_DIRS["formal"] = "raw/formal"` with a deterministic name `fm-<id>[_vs_<rival>...]`:
  `.request.json` (`oase.formal-request.v1`: the hypothesis, its source path and sha256, the CoResearcher request),
  `.response.json` (`oase.formal-response.v1`: the CoResearcher response and any HTTP exchanges) and the sidecar
  `.meta.json` built with OASE's `provenance.Sidecar` (`outputs[{path, sha256, bytes}]`, parameters, endpoint,
  warnings, `mandatory_relays`, capability state, the OASE and CoResearcher threshold records, `formal_status`).
  Stdout is the three paths. An identical re-run is a cache hit; a different request to the same name is refused
  without `--overwrite`.
- **`analyze`** (phase 2) is offline twice over: `enforce_phase_two` latches OASE's HTTP client, and the adapter
  refuses raw sockets too, because the engine's formalizer client is not OASE's. It checks every declared output
  against its sha256 (exit 3), re-runs the verdict locally with z3 or enumeration from the stored formal object (and
  the gate from the stored raw outputs), compares it with the run report by report (`input_sha256`, `output_sha256`,
  threshold set) and applies `formal@1.0`. It writes `<stem>.analysis.json` through `provenance.write_analysis`, so
  OASE's refusal to replace a differing analysis, `--out` second opinions and cross-work-order protection apply
  unchanged. The assessment carries the verdict, the criteria, the AR mapping (section 5), the reproduction result,
  the reports, the gate and the formal object.
- **`doctor`** reports the engine, z3 (with a solver round trip), Lean, the formalizer model and the HTTP transport;
  the same checks are added to `oase doctor` (`_check_formal_verifier`), as OASE's checklist requires.

The engine is imported, not vendored: CoResearcher installed in the tools environment, or `CORESEARCHER_HOME`.

### 2. Threshold set `formal@1.0`

Declared in `tools/oase/core/thresholds.py`. The engine thresholds (`max_states`,
`max_assumptions_for_conflict_search`, `solver_timeout_ms`, `gate_samples`, `gate_max_samples`, `gate_temperature`,
`gate_majority_fraction`, `formalizer_temperature`, `formalizer_seed`) equal CoResearcher's `formal@2026.10.1`; a test
fails if they drift. Only values that differ (program file, `--solver-timeout-ms`, `--max-states`) reach the engine
as overrides, which fires `formal.thresholds_overridden`; an `UNRESOLVED` engine value reaches it as unset, so the
engine reports BLOCKED instead of using its own default. Two decision thresholds:

| Key | Value | Why |
| --- | --- | --- |
| `max_formal_defects` | 0 | Definitional: VACUOUS, SELF_CONTRADICTORY and UNFALSIFIABLE are defects by the ADR-059 definitions. Compared as `defect_count <= threshold`. |
| `min_excluded_fraction_of_applicable` | `UNRESOLVED` | No published value says how much of its applicable state space a hypothesis must forbid. Reported with `met: null` until a program sets it. |

### 3. Relays

CoResearcher's codes are mapped into OASE's registry namespace (OASE codes are `tool.snake_case` and written as
obligations on the finding), and registered in `provenance.RELAY_CODES`. Every code is emitted from the module, so
OASE's `check_relay_codes.py` finds an emission site for each; the skill's relay table names all of them.

| OASE code | CoResearcher source |
| --- | --- |
| `formal.not_empirical` | `FORMAL_NOT_EMPIRICAL` (every decided report) |
| `formal.smt_fixed_size_only` | `SMT_FIXED_SIZE_ONLY` |
| `formal.enumeration_declared_domains_only` | `ENUMERATION_DECLARED_DOMAINS_ONLY` |
| `formal.lean_not_kernel_checked` | `LEAN_NOT_KERNEL_CHECKED` |
| `formal.formalization_is_draft` | `FORMALIZATION_IS_DRAFT` |
| `formal.gate_single_sample` | `GATE_SINGLE_SAMPLE` |
| `formal.vacuous_entailment` | `VACUOUS_ENTAILMENT` |
| `formal.entailed_by_assumptions_alone` | `ENTAILED_BY_ASSUMPTIONS_ALONE` |
| `formal.thresholds_overridden` | `THRESHOLDS_OVERRIDDEN` |
| `formal.formalization_ambiguous` | status `FORMALIZATION_AMBIGUOUS` |
| `formal.formalization_failed` | status `FORMALIZATION_FAILED` |
| `formal.undecided` | status `UNDECIDED` |
| `formal.blocked` | status `BLOCKED` |
| `formal.not_reproduced` | `analyze` could not reproduce the run under the same thresholds |

Each OASE relay record keeps `coresearcher_code`, so a reviewer can trace it to the engine's report. A CoResearcher
code without a mapping raises instead of being dropped.

### 4. Exit codes: a non-verdict is never a negative

| Outcome | OASE exit | Note |
| --- | --- | --- |
| DECIDED, including a decided defect | 0 | A negative answer is an answer. |
| INVALID_INPUT, identity mismatch, ambiguous candidate | 9 `Refusal` | Change the input. |
| FORMALIZATION_AMBIGUOUS / FAILED | 9 `Refusal` | OASE: "the ambiguous case is a refusal by construction"; the tool never picks a reading. |
| BLOCKED by a threshold or `max_states` | 4 `ThresholdError` | |
| BLOCKED, formalizer endpoint unreachable | 7 `EndpointUnavailable` | |
| BLOCKED, engine, z3 or model missing | 8 `DependencyError` | |
| Checksum mismatch, missing output | 3 `ArtifactError` | |
| UNDECIDED (solver gave up) | 10 `FormalUndecided` | OASE has no code for it; 0 and 9 would each send the caller the wrong way. |
| `analyze` does not reproduce the run | 12 `FormalNotReproduced` | Same code as ADR-068. |
| Phase 2 attempted the network | 1 `PhaseContractError` | OASE's own. |

Artifacts are written before the exit, as OASE does for refusals: the record says what was not decided and why.

### 5. Mapping to an evidence-assessment record (AR)

`assessment.evidence_assessment` in the analysis is the AR mapping, so a gate never re-derives it:

| Analysis | `execution_outcome` | `evidence_status` |
| --- | --- | --- |
| DECIDED, no defect | `completed` | `supported` |
| DECIDED, defect | `completed` | `contradicted` |
| any non-verdict | `blocked` | `not_assessed` |

`evidence` carries `artifact_path` and `artifact_sha256` (the response the analysis read), `evidence_type:
formal-soundness`, `metric_name: defect_count`, `metric_units: count`, `threshold_set: formal@1.0` and `method`
(`coresearcher-enumeration` or `coresearcher-smt`).

### 6. Installer

`apply.sh <OASE_DIR>` (a wrapper for `apply.py`) edits five files and adds two, each edit anchored on a line of the
pinned commit and idempotent; a missing anchor stops it with exit 2 instead of guessing. `--dry-run` prints the
unified diff and writes nothing. It copies `formal.py`; imports it in `cli.py` and adds `cli.add_command(formal)` after
the last registration, before `enforce_phase_two(cli)`; registers `ARTIFACT_DIRS["formal"]`, the `formal@1.0` set and
the relay codes; adds the doctor check; adds the skill; and grants it in the `hypex-reflection`,
`scientific-reviewer` and `science-program-lead` templates. The granted URI points to this repository
(`--skill-uri` overrides it), because OASE resolves skill URIs remotely and a skill that exists only on disk does not
exist for provisioning.

### 7. Skill and the two documented uses

`skills/formal-hypothesis-verification/SKILL.md` follows OASE's skill guidance §4: routing description with a
negative clause, when to use, preconditions, an invocation table with output paths, an interpretation contract that
names every relay and what it obliges, and the anti-fabrication guard with named pathologies. It cites thresholds by
name only, and carries the "do not invent" instruction for the UNRESOLVED one.

- **(a) Pre-tournament review.** `hypex-reflection` runs `oase formal run/analyze` on each hypothesis with a formal
  object before the tournament. A decided defect (vacuous, self-contradictory, unfalsifiable) returns the hypothesis to
  its author; CONTRADICTORY rivals enter as a pair with their discriminating states; EQUIVALENT ones are merged.
- **(b) Stage 1 gate.** [`integrations/oase/gate/GP-001.formal-soundness.json`](../../integrations/oase/gate/GP-001.formal-soundness.json)
  is an example gate policy: `REQ-001` is a `scientific_cutoff` with `evidence_type: formal-soundness`,
  `threshold_set: formal@1.0`, `threshold_key: max_formal_defects`, `direction: below` (inclusive, stated in the
  description) and `method_required: [coresearcher-enumeration, coresearcher-smt]`; `REQ-002` is a
  `prioritization_heuristic` on the UNRESOLVED key. An AR cites the `.analysis.json` by copying
  `assessment.evidence_assessment` (`demo/make_assessment.py` shows it); both validate with OASE's
  `validate_policy` / `validate_assessment`, match through `match_assessment_to_requirement`, and freeze into a
  snapshot whose `unresolved` lists the open threshold.

### 8. Demo

[`integrations/oase/demo/`](../../integrations/oase/demo/REPORT.md): four illustrative hypex hypotheses about TREM2
agonism (labelled `[Illustrative]`, with an explicit "no literature consulted" evidence entry), run end to end in an
OASE checkout at the pinned commit with `apply.sh` applied. The committed artifacts and the report show a target
hypothesis and its rival decided FALSIFIABLE and INCOMPARABLE with the discriminating experiment named, two evolved
variants decided SELF_CONTRADICTORY and UNFALSIFIABLE, and a prose run without a model recorded as BLOCKED /
`not_assessed`.

## Tests and CI

- `tests/test_oase_adapter.py` (every platform): the installer's edits on synthetic anchors (idempotent, valid Python,
  registration before `enforce_phase_two`, moved anchor stops, dry run writes nothing); `formal@1.0` equals the engine
  defaults; every CoResearcher relay and non-verdict has a registered OASE code; the skill has the six sections and
  names every relay; the committed demo artifacts match their checksums and their verdicts recompute with CoResearcher
  alone (same report digests on Windows and Linux); the gate ARs are rebuilt exactly from the analyses.
- `integrations/oase/tests/test_oase_formal.py` (POSIX, inside OASE): the real CLI in a fresh program directory —
  conformant options, registry and doctor; decided verdicts and their AR mapping; cache hit and overwrite refusal;
  adopted-set candidates; identity and schema refusals; UNDECIDED (exit 10), BLOCKED (exit 8, 4) and ambiguous
  formalization (exit 9) mapped to `not_assessed`; prose through the gate with a fake model, re-checked offline;
  tampered output (exit 3); a fabricated verdict with a re-forged checksum (exit 12, `formal.not_reproduced`);
  network refusal in phase 2; second-opinion and overwrite rules; program and flag thresholds; the HTTP transport
  against the real CoResearcher API in-process; hypex schema validation of the demo inputs; the gate example; and a
  replay of the committed demo artifacts.
- CI job `oase-conformance` (Linux): clones OASE at the pinned commit, installs its locked requirements, runs
  `check_relay_codes.py` and `check_threshold_names.py` on the pristine tree, applies the adapter (dry run, apply,
  re-apply), runs them again and fails on any problem the adapter introduces; then OASE's
  `test_artifact_dirs_completeness`, `test_cli_option_conformance`, `test_comparable_field_coverage`,
  `test_skill_frontmatter`, `test_tools_list`, `test_policy`, `test_artifact_dirs`, `test_doctor_project`, and the
  adapter's tests. Both OASE checkers already report problems in upstream files at the pinned commit (2 and 10), so the
  gate is "no new problem and none mentioning the adapter", not exit 0; a checker that cannot run (exit 2) fails the
  job. On Windows the OASE-side tests skip with that reason; they are never reported as passed.

## Consequences

- An OASE checkout with the adapter is "dirty": its sidecars and analyses carry `cli_modified: true` and OASE prints its
  uncommitted-modifications warning (suppressible with `OASE_NO_DIRTY_WARNING=1`). That is accurate until the module
  is upstream.
- `check_skill_uris.py` is not part of the gate: its check 3 needs the skill on the ref the template names, which is
  this repository's `master` after merge, not the OASE checkout.
- The formalizer prose path was exercised with a fake model in tests and with no model in the demo (BLOCKED); a live
  local-model run in OASE was not part of this change.
- Not done here, by design: anything outward (OASE issues #194–#198, an upstream pull request, a fork). The adapter
  file carries an Apache-2.0 header so that, if the owner decides to contribute it, its license matches OASE's.
