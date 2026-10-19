# ADR-DISCOVERY-068: Auditable formal verdicts — provenance, non-verdict statuses, versioned thresholds, relays, two-phase CLI

**Status:** Accepted
**Date:** 2026-10-19
**Modules:** [`python/discovery/formal_provenance.py`](../../python/discovery/formal_provenance.py),
[`python/discovery/formal_status.py`](../../python/discovery/formal_status.py),
[`python/discovery/formal_thresholds.py`](../../python/discovery/formal_thresholds.py),
[`python/discovery/formal_pipeline.py`](../../python/discovery/formal_pipeline.py),
[`python/cli/formal.py`](../../python/cli/formal.py)
**Amends:** ADR-DISCOVERY-059, 060, 061, 064 (reports and gate gain provenance, relays and a shared status)
**Reuses:** the canonical-JSON digest of ADR-DISCOVERY-067

## Context

The formal layer decides things: whether a hypothesis is vacuous, self-contradictory, unfalsifiable or falsifiable
(ADR-059), how two rivals relate and whether a consequence follows (ADR-060), and whether a formalizer's reading of
prose is stable enough to accept (ADR-061, ADR-064). Until now its reports could not be audited after the fact:

- An `EvaluationReport`, `ComparisonReport`, `ConsequenceReport` or gate result did not say which engine, z3 version,
  solver timeout or input produced it, so a reviewer could not tell whether a quoted verdict came from the object it
  was attributed to.
- Non-verdicts had no common name. A z3 timeout surfaced as a `FormalHypothesisError` (indistinguishable from a
  malformed object), a missing formalizer model as an HTTP 503, a gate split as `FORMALIZATION_AMBIGUOUS`, a Lean
  statement as the string `"NOT_KERNEL_CHECKED"`. Nothing guaranteed that every path kept them out of the verdict.
- The cutoffs (`MAX_STATES`, `SOLVER_TIMEOUT_MS`, gate samples, majority and temperatures) were module constants,
  unrecorded in any report.
- The caveats every formal verdict needs ("formally consistent is not empirically true") lived in prose, not in the
  artifact.
- There was no way to recompute a verdict from stored inputs and compare it with the one claimed.

Google's Open Agentic Science Engine (OASE; `GoogleCloudPlatform/LifeSciences`, `applications/open-agentic-science-
engine`, Apache 2.0) solves exactly these problems for its tools: a two-phase `run`/`analyze` split, checksummed
`.meta.json` sidecars, `.analysis.json` records that refuse to overwrite a differing verdict, versioned thresholds
with an `UNRESOLVED` sentinel, registered relay codes and an exit-code taxonomy (`docs/tool-design-guidance.md`,
`tools/oase/core/provenance.py`, `thresholds.py`, `errors.py`). OASE has no formal hypothesis layer: hypotheses are
prose scored by LLM rubrics and Elo. CoResearcher has that layer. This ADR makes its verdicts auditable in OASE's
terms, so a later `oase formal run/analyze` adapter (in a fork; upstream only with the owner's approval) is a thin
wrapper. OASE's CLI is POSIX-only (it imports `fcntl`); everything here stays cross-platform.

Scope (unchanged): CoResearcher judges formal soundness only. Nothing here grades evidence, sources or citations.

## Decision

### 1. Every formal result carries a provenance block

`EvaluationReport`, `ComparisonReport`, `ConsequenceReport` and `GateResult` gain `provenance`, `mandatory_relays`
and (in `to_dict()`) `formal_status`. Existing fields and their values are unchanged; `body()` returns them alone.

| Field | Content |
| --- | --- |
| `engine`, `engine_version` | `coresearcher` and the package version (installed metadata, else `pyproject.toml`) |
| `operation` | `evaluate`, `compare`, `entails` or `formalize_gate` |
| `backend` | `enumeration`, `smt`, or `mixed` (gate) |
| `z3_version`, `solver_timeout_ms` | the solver and the timeout in force (`null` for pure enumeration) |
| `input_sha256` | digest of `{"operation", formal object(s), request parameters}`; for the gate, of the request, the sample specs and the **raw model outputs** |
| `output_sha256` | digest of `body()`, the verdict without status, relays or provenance |
| `threshold_set`, `thresholds_applied`, `threshold_sources`, `threshold_provenance` | the threshold set used (section 3) |
| `formalizer` (gate only) | `models`, `prompt_version`, `prompt_sha256`, `seeds`, `temperatures` |
| `timestamp`, `python`, `platform` | volatile: describe the run, not the result |

Digests use the ADR-067 convention, now defined once in `formal_provenance.canonical` and used by the evidence graph
too: SHA-256 of JSON with sorted keys, no whitespace, UTF-8, non-JSON values through `str`. The same input under the
same thresholds must give the same `output_sha256`; section 5 checks it.

### 2. One non-verdict vocabulary

`formal_status.FormalStatus`: `DECIDED` is the only status that carries a verdict. The others say why there is none:

| Status | Cause | CLI exit |
| --- | --- | --- |
| `DECIDED` | decided exactly | 0 |
| `UNDECIDED` | z3 returned `unknown` (timeout, incompleteness) — now `SolverUndecided` | 10 |
| `BLOCKED` | missing capability or setting: z3, formalizer model (8) or endpoint (7), a threshold unset (4), or a question over a threshold such as `max_states` — now `ThresholdExceeded` (4) | 4 / 7 / 8 |
| `INVALID_INPUT` | malformed object or request (a refusal: change the input) | 9 |
| `FORMALIZATION_AMBIGUOUS` / `FORMALIZATION_FAILED` | the ADR-064 gate accepted no reading | 11 |
| `NOT_KERNEL_CHECKED` | a Lean theorem was stated, no Lean kernel checked it | n/a |

`SolverUndecided` and `ThresholdExceeded` subclass `FormalHypothesisError`, so every existing `except` and the API's
HTTP 422 keep working; `formal_status.classify` tells them apart and re-raises any exception that is not a known
non-verdict (a bug is never turned into a status). In the gate, a sample or pair the solver could not decide is
marked `UNDECIDED` and never counts as agreement. Existing enums (`ContentVerdict`, `Relation`, `GateStatus`,
`FormalizationStatus`) keep their values; `from_gate_status` maps the gate onto the vocabulary (`CONSISTENT` and
`SINGLE_SAMPLE` are `DECIDED`: a reading was accepted). Exit codes 0–9 follow OASE's taxonomy; 10–12 are the formal
layer's own.

### 3. Versioned thresholds

`formal_thresholds.FORMAL_DEFAULTS` is the set `formal@2026.10.1`: `max_states`, `max_assumptions_for_conflict_search`,
`solver_timeout_ms`, `gate_samples`, `gate_max_samples`, `gate_temperature`, `gate_majority_fraction` (a class wins
when its size is strictly above this fraction of N; 0.5 is the ADR-064 strict majority), `formalizer_temperature`,
`formalizer_seed`, with a provenance string citing where each value comes from. Resolution, most specific last:

1. code defaults, under the version tag (changing a value means bumping it);
2. the project file `.coresearcher/formal_thresholds.json`, found by walking up from the working directory or named
   by `CORESEARCHER_FORMAL_THRESHOLDS`:
   `{"set": "formal", "provenance": "why", "overrides": {"solver_timeout_ms": 30000}}`;
3. per-invocation overrides (`--threshold KEY=VALUE`), recorded with source `flag`.

A value declared `UNRESOLVED`, or set to `null` by an override, raises `ThresholdError` when read; the pipeline
reports `BLOCKED` and never substitutes a number. A malformed file, an unknown key, or overrides without a
`provenance` string raise rather than being skipped. The old constants (`MAX_STATES`, `SOLVER_TIMEOUT_MS`,
`DEFAULT_SAMPLES`, ...) remain as aliases of the defaults; the running code reads the set in force. Every report
records `threshold_set`, `thresholds_applied` and `threshold_sources`.

### 4. Mandatory relays

Caveats are attached as `{"code", "message"}` under `mandatory_relays` (OASE's field), from a registry
(`formal_status.RELAY_CODES`); an unregistered code is rejected.

| Code | Fires on |
| --- | --- |
| `FORMAL_NOT_EMPIRICAL` | every evaluation, comparison and entailment: formally consistent is not empirically true |
| `SMT_FIXED_SIZE_ONLY` | z3 results: valid for the declared variables and bounds only, not a parametric proof |
| `ENUMERATION_DECLARED_DOMAINS_ONLY` | enumeration results: values outside the declared domains were never considered |
| `LEAN_NOT_KERNEL_CHECKED` | a Lean theorem was emitted (`include_lean`, `--lean`) |
| `FORMALIZATION_IS_DRAFT` | the gate accepted a model's reading: stable is not the same as what the prose meant |
| `GATE_SINGLE_SAMPLE` | N = 1: no self-consistency evidence |
| `VACUOUS_ENTAILMENT` | the consequence is entailed only because no applicable state is allowed |
| `ENTAILED_BY_ASSUMPTIONS_ALONE` | the consequence follows without the claims |
| `THRESHOLDS_OVERRIDDEN` | a threshold differs from the versioned default |

OASE's guidance warns that a tool emitting relays only on defects goes out barest on its cleanest, most quotable run.
Here the cleanest verdict is the one most likely to be over-read, so `FORMAL_NOT_EMPIRICAL` and the backend caveat
fire on every decided report.

### 5. Two-phase CLI

```bash
coresearcher formal run --hypothesis H.json --rival R.json --consequence "x <= 6" --out raw/formal
coresearcher formal run --prose "..." --samples 5 --out raw/formal
coresearcher formal analyze raw/formal/F-<digest>.meta.json
coresearcher formal doctor [--probe]
```

- **`run`** (phase 1) builds a request, calls the formalizer and the gate when prose is given, evaluates the formal
  object, compares it with each rival and checks each consequence (`formal_pipeline.compute`). It writes
  `<name>.request.json` (including the formalizer messages), `<name>.response.json` (the raw model outputs and specs,
  and every report) and the sidecar `<name>.meta.json` with OASE's fields: `tool`, `subcommand`, `work_order_id`,
  `cli_version`, `cli_integrity`, `env_version`, `interpreter`, `endpoint`, `parameters`, `timestamp`, `completed`,
  `outputs[{path, sha256, bytes}]`, `warnings`, `mandatory_relays`, `capability_state`, plus the threshold record and
  `formal_status`. Stdout is the three paths. Non-verdicts are written too, with their exit code. A run never
  overwrites an existing run unless `--overwrite`.
- **`analyze`** (phase 2) is offline and deterministic. It checks every declared output against its sha256 (exit 3 on
  a change), then recomputes the response with the same `compute` function — from the stored raw outputs for prose,
  so no model is called — while network connections are refused. It writes `<name>.analysis.json` with OASE's
  analysis fields: `record_type: "analysis"`, `source`, `source_sha256`, `cli_version`, `env_version`, `timestamp`,
  `threshold_set`, `thresholds_applied`, `threshold_sources`, `threshold_provenance`, `metrics`, `assessment`,
  `mandatory_relays`, `written_by`, `work_order_id`, plus `verdict`, `formal_status` and the recomputed `reports`.
  `assessment.reproduces_run` compares run and analysis report by report (`input_sha256`, `output_sha256`,
  `threshold_set`) and on the whole response with volatile fields removed; under unchanged thresholds a mismatch exits
  12. This is the reviewer's mechanical fabrication check: a verdict edited into a response, even with its checksum
  re-forged, does not reproduce. An existing identical analysis is left untouched; a differing one is never replaced
  (exit 9) unless `--overwrite`; `--out` writes a second opinion beside it.
- **`doctor`** reports z3 (with a solver round trip), a Lean binary (theorems remain `NOT_KERNEL_CHECKED` regardless),
  the formalizer configuration with its prompt hash, the threshold set in force and its override file, and the relay
  registry. It exits 8 when z3 does not work.

Field names mirror OASE's sidecar and analysis schema so that `oase formal run/analyze` can call these commands and
pass their records through unchanged; the adapter only maps relay codes into OASE's registry namespace.

## Consequences

- Report dictionaries are larger (status, relays, provenance). Consumers that digest them must ignore the volatile
  provenance fields; `formal_provenance.comparable` and the CLI's `comparable` do so.
- The API returns the new fields automatically (`/api/hypotheses/evaluate`, `/compare`, `/entails`, `/formalize`);
  `/entails` with `include_lean` also attaches `LEAN_NOT_KERNEL_CHECKED`. No route or status code changed.
- Thresholds are read on each solver call so an override file takes effect without a restart; the parsed file is
  cached by path and modification time.
- Not done here: the OASE adapter itself, signing of sidecars, and running Lean in `analyze`.

## Tests

`tests/test_formal_audit.py` covers each guarantee: provenance fields and digests (including the shared ADR-067
canonical form), the status vocabulary and its exit codes (solver timeout, missing model, unreachable endpoint,
unset threshold, `max_states` exceeded, malformed input, Lean), the threshold set (defaults, project file found by
walk-up, flags, malformed files, gate majority and sampling schedule as thresholds), every relay trigger, and the CLI
(`run` sidecar checksums, `analyze` reproducing formal and prose runs offline byte-for-byte on comparable fields,
detection of a fabricated verdict, refusal to overwrite, network refusal, `doctor`).
