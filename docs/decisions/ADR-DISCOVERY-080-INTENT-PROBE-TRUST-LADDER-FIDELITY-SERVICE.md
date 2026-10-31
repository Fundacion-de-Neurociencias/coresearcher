# ADR-DISCOVERY-080: Intent probe, per-claim trust ladder and statement fidelity as a service

**Status:** Accepted
**Date:** 2026-10-31
**Modules:** [`python/discovery/formal_hypothesis.py`](../../python/discovery/formal_hypothesis.py) (intent probe),
[`python/discovery/formal_trust.py`](../../python/discovery/formal_trust.py),
[`python/discovery/fidelity_service.py`](../../python/discovery/fidelity_service.py),
[`python/discovery/formal_pipeline.py`](../../python/discovery/formal_pipeline.py),
[`python/cli/formal.py`](../../python/cli/formal.py),
[`api/routers/fidelity.py`](../../api/routers/fidelity.py), [`api/routers/hypotheses.py`](../../api/routers/hypotheses.py)
**Builds on:** ADR-DISCOVERY-059 (formal hypotheses), ADR-DISCOVERY-060 (z3 back end), ADR-DISCOVERY-067 (evidence
graph), ADR-DISCOVERY-068 (status, relays, provenance, two-phase CLI), ADR-DISCOVERY-070 (statement fidelity, junk-value
lint)
**Context record:** [`docs/reference/EXTERNAL_RESULTS_PROGRAM.md`](../reference/EXTERNAL_RESULTS_PROGRAM.md)
**Numbering:** 077 is used on master and 078 and 079 by records on open branches, so this record takes 080. The pre-registration record of PR #22 is 081.

## Context

The external-results program (October 2026) left three lessons that were applied by hand in case studies and were not
yet product features:

1. **Existence claims can be vacuous relative to their intent** (lesson 3). A claim can be consistent and falsifiable
   and still hold of an object its author meant to exclude: the zero model, the free theory, a lower dimension.
   `HypothesisEvaluator` reported VACUOUS only when no state is in scope at all.
2. **"Formalized" is a per-claim status** (lesson 4). The program used five rungs, from CLAIMED to
   INDEPENDENTLY_REPRODUCED, but no report carried them, and nothing stopped a NOT_KERNEL_CHECKED theorem from being
   read as checked.
3. **Check the question before the answer** (lesson 1). The ADR-070 range comparison and junk-value lint existed only
   as library functions driven by one case script.

A pre-registration record (ADR-081, PR #22: `trust_ladder.ClaimRecord`, `trivial_witness`) applies the same ideas to one
announced result through a frozen checklist and a hand-kept, dated claim history. This record makes the generic
mechanisms part of every formal report, the API and the CLI.

### Methodology

This record implements three methods of the verification methodology
(`docs/architecture/VERIFICATION_METHODOLOGY.md`, added in PR #23):

- **M1, check the question before the answer:** the fidelity services (section 3);
- **M4, existence and generality claims can be vacuous:** the intent probe (section 1);
- **M7, "formalized" and "verified" are per-claim states:** the trust ladder (section 2).

It also follows M8 (a non-answer never becomes an answer): UNDECIDED fidelity stays a non-verdict, and
NOT_KERNEL_CHECKED never counts as a kernel check.

The October cases (local smoothing, Yang–Mills) were rehearsals. The capabilities are domain-neutral. The intent probe
works on any formal hypothesis, with the same evaluator call. For a biomedical hypothesis such as "high pTau217
predicts decline", the probe holds the biomarker at a constant with no signal. If the predicted effect still holds
there, the biomarker does no work in the claim, and the verdict is VACUOUS_RELATIVE_TO_INTENT. A test covers this
case. The trust ladder grades any statement with a digest. Only the fidelity services are specific to statements
with a paper range and a Lean range.

## Decision

### 1. Intent probe in `HypothesisEvaluator`

- A hypothesis may declare `non_witnesses`: a list of `{label, state}`, where `state` fixes some variables (values
  must lie in their domains or bounds). Each is probed exactly: SATISFIES_CLAIMS (some completion is in scope, meets
  the assumptions and every claim; the full witness state is returned), FORBIDDEN, or OUT_OF_SCOPE. Enumeration and
  z3 give the same outcomes; z3 is used whenever a variable is continuous.
- If a declared non-witness SATISFIES_CLAIMS and the verdict would be FALSIFIABLE or UNFALSIFIABLE, the content
  verdict is **VACUOUS_RELATIVE_TO_INTENT**, with the relay of the same name. `intent_probe.base_verdict` keeps the
  verdict it replaces. VACUOUS and SELF_CONTRADICTORY are stronger findings and are never replaced; the new verdict is
  never merged with VACUOUS.
- `default_probes` adds generic trivial witnesses derived from the variables alone: numeric variables at zero, at
  their lower bounds and at their upper bounds (strings and booleans are never fixed; unfixed variables stay free). A
  default probe that satisfies the claims adds the relay TRIVIAL_WITNESS_SATISFIES_CLAIMS and **never changes the
  verdict**: only the author knows which trivial objects the claim must exclude. The empty scope needs no probe; it is
  the VACUOUS verdict.
- `intent_probe` is in the report body (covered by `output_sha256`) only when non-witnesses were declared or default
  probes requested. `non_witnesses` and `default_probes` enter the input digest only when set. Reports and stored
  runs that do not use them keep their bytes, so the committed OASE demo runs still reproduce.

### 2. Trust ladder (`formal_trust`)

Rungs: CLAIMED → STATEMENT_PUBLIC → STATEMENT_AUDITED → KERNEL_CHECKED → INDEPENDENTLY_REPRODUCED. `assess(evidence)`
recomputes the rung from fields and digests only:

| Rung | Rule (plus every rung below) |
| --- | --- |
| STATEMENT_PUBLIC | `statement.text`, `statement.location`, and `statement.sha256` equal to SHA-256 of the UTF-8 text |
| STATEMENT_AUDITED | an audit of that statement (`statement_sha256` matches) with fidelity EQUIVALENT or STRONGER and `lint_open_unreviewed == 0` |
| KERNEL_CHECKED | `kernel_check.status` exactly KERNEL_CHECKED, a `toolchain`, a 64-hex `file_sha256`, the matching `statement_sha256`, and `axioms` within `propext`, `Quot.sound`, `Classical.choice` |
| INDEPENDENTLY_REPRODUCED | a reproduction that meets the same kernel rules, by a named `checker` other than the first one's |

- Every rung reports `met` and, when not met, the rule that failed. Rungs are not skipped: a kernel check of an
  unaudited statement leaves the claim at STATEMENT_PUBLIC with "needs STATEMENT_AUDITED first".
- NOT_KERNEL_CHECKED is named as a failure reason, never a step. `sorryAx` or a project axiom keeps a check below
  KERNEL_CHECKED, and so does a check with no recorded axiom list.
- `audit_record` builds the audit entry from a fidelity report and a lint report of the same statement, so the audit
  rung is reached from CoResearcher's own sealed reports.
- **In formal reports.** Claims of a formal object supplied by the caller start at STATEMENT_PUBLIC (the predicate
  text is the statement, pinned by its own digest and by the request's input digest). Claims of a formalizer draft
  stay CLAIMED. `claim_evidence` (keyed by claim) can lift them by the same rules. Lean theorems the pipeline states
  are NOT_KERNEL_CHECKED and never lift a claim.
- **Where it appears.** `claim_trust` is in the response of `POST /api/hypotheses/evaluate`, in the `.meta.json`
  sidecar of `formal run` and in the `.analysis.json` of `formal analyze`, and on the hypothesis node of the evidence
  graph. It is a view computed from the response, not part of the response, so it cannot break reproduction. The
  relay CLAIM_BELOW_KERNEL_CHECKED is added wherever a claim is below KERNEL_CHECKED.
- `POST /api/trust/assess` and `coresearcher formal trust --evidence E.json` grade evidence for any claim, including
  external ones.

### 3. Statement fidelity as a service (`fidelity_service`)

- `compare(spec)` wraps `statement_fidelity.compare_ranges` as a sealed report: the ADR-070 body (relation,
  witnesses, methods, division hazards, quantities), `formal_status`, relays (FORMAL_NOT_EMPIRICAL,
  FIDELITY_RANGE_ONLY) and an ADR-068 provenance block (operation `fidelity_compare`). An UNDECIDED relation has
  `formal_status` UNDECIDED: a non-verdict, exit code 10. Optional `integer_values` adds the `cross_check` slice.
- z3 chooses a model by its internal term order, and that order depends on every earlier query in the process. Each
  comparison therefore runs in a fresh z3 context, one at a time. Without this, the same request could return a
  different witness, and so a different `output_sha256`, depending on what the server had computed before.
- `lean_lint(source)` wraps `lean_junk_lint.lint`: findings DISCHARGED or OPEN, optional review notes, the statement
  digest, relays LINT_IS_SYNTACTIC and LEAN_NOT_KERNEL_CHECKED, provenance (operation `lean_lint`).
- API: `POST /api/fidelity/compare`, `POST /api/fidelity/lean-lint`. Both are catalogued DETERMINISTIC and READ_ONLY.
- CLI: `coresearcher formal fidelity --spec S.json` and `coresearcher formal lean-lint --file F.lean` are phase 1 of
  the ADR-068 two-phase convention: they write `.request.json`, `.response.json` and the checksummed `.meta.json`.
  `formal analyze` re-derives them offline (new request kinds `fidelity` and `lean_lint` in `formal_pipeline`), compares
  digests report by report, and refuses or exits 12 exactly as for hypotheses.

## Consequences

- A hypothesis can now say what it is not about, and the verdict says when it fails to exclude it. The OASE adapter
  counts VACUOUS_RELATIVE_TO_INTENT as a formal defect, like VACUOUS.
- Every evaluated claim carries a rung. For claims evaluated by z3 or enumeration the usual rung is STATEMENT_PUBLIC:
  the evaluator decides properties of the formal object, which is not a fidelity audit or a kernel check.
- The trust rules grade evidence; they do not produce it. A recorded kernel check is trusted as recorded (its digests
  are checked for form and consistency, not by re-running Lean). Re-running Lean remains outside this record.
- Default probes are coarse. They are advisory by design, and a satisfied default probe is often intended (a claim
  `x >= 0` is satisfied at zero).
- Fidelity stays range-only; conclusions are not compared (ADR-070).

## Alternatives considered

- **Make default probes change the verdict.** Rejected: "all variables at zero" is the intended witness of many
  claims, and a verdict must not depend on a guess about intent.
- **Store the trust rung inside the formal reports.** Rejected: it would change the bytes of every stored response
  and break run/analyze reproduction of existing runs, and the rung depends on evidence outside the formal object.
  It is a view computed beside the reports.
- **Reuse `trust_ladder.ClaimRecord` (ADR-081).** It records a dated, hand-curated history for one announced result
  and checks only that evidence keys are present. Formal reports need a stateless function of the evidence with
  digest checks. The two use the same rung names, so a claim record's latest step can be cross-checked against
  `formal_trust.assess` once both are merged.
