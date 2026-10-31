---
name: formal-hypothesis-verification
description: >
  Decide whether a hypothesis is formally sound — not vacuous, not
  self-contradictory, falsifiable — how it relates to a rival (equivalent,
  stronger, weaker, incomparable, contradictory) and on which states they
  disagree, and whether a stated prediction actually follows. Exact, by z3 or
  exhaustive enumeration, from a formal object stored with the run. Use when
  reviewing hypex hypotheses before a tournament, when two hypotheses look
  like rivals and you need the states that would tell them apart, or when a
  Stage 1 gate requires formal soundness. Do not use to judge evidence,
  citations, novelty or plausibility (use review-rubric and
  citation-verification), or to rank hypotheses (use elo-tournament).
---

## When to use, and when not

Use it to find out what a hypothesis *says*, as logic:

- Pre-tournament review: a hypothesis that is vacuous (applies to nothing),
  self-contradictory (its claims rule out every case it applies to) or
  unfalsifiable (forbids nothing) should not enter a tournament, because Elo
  will happily rank it. Two hypotheses that are CONTRADICTORY cannot both be
  right; two that are EQUIVALENT are one hypothesis entered twice.
- A Stage 1 gate requirement with `evidence_type: formal-soundness`.
- Choosing an experiment: the discriminating states of a comparison are the
  cases where only one rival forbids the outcome.

Do not use it for anything empirical. A formal verdict never says a
hypothesis is true, likely, supported or novel. For evidence and citations
use `citation-verification`; for scoring use `review-rubric`; for ranking
use `elo-tournament`.

## Preconditions

- A hypex `H-NNNN.json`, or an adopted hypothesis set and a `candidate_id`.
- A formal object for it (variables with finite domains or bounds, scope,
  assumptions, claims) authored or confirmed by a researcher, passed with
  `--formal`. Without one, the statement is formalized by the configured
  model; that needs a model (`oase formal doctor`) and every result carries
  `formal.formalization_is_draft`.
- Rivals are formal objects over the same variables.
- Cost: seconds per hypothesis on enumeration; z3 calls are bounded by the
  `solver_timeout_ms` threshold. No lease, no network in `analyze`.

## Tool Invocations

| Question | Run | Writes to |
|---|---|---|
| Is H sound, and how does it relate to a rival? | `oase formal run H-0001.json --formal H-0001.formal.json --rival H-0002.formal.json`<br>`oase formal analyze raw/formal/fm-H-0001_vs_H-0002.meta.json` | `raw/formal/fm-H-0001_vs_H-0002.request.json`<br>`raw/formal/fm-H-0001_vs_H-0002.response.json`<br>`raw/formal/fm-H-0001_vs_H-0002.meta.json`<br>`raw/formal/fm-H-0001_vs_H-0002.analysis.json` |
| Does a prediction follow from H? | `oase formal run H-0001.json --formal H-0001.formal.json --consequence "<predicate>"` | `raw/formal/fm-H-0001.*.json` |
| One candidate of an adopted set | `oase formal run raw/hypotheses/<set>.adopted.json --candidate 2 --formal <object>.json` | `raw/formal/fm-<set>-c2.*.json` |
| What can run here? | `oase formal doctor` | stdout only |

Run `run` before `analyze`. `analyze` re-runs the verdict offline from the
stored formal object and reports whether it reproduces the run.

## Interpretation contract

Cite the `.analysis.json`, never the run's response: the analysis is the
verdict recomputed and checked against the run (`assessment.reproduction`).

**Content verdict** (`assessment.criteria.content_verdict`): VACUOUS,
SELF_CONTRADICTORY and UNFALSIFIABLE are defects of the hypothesis; FALSIFIABLE
is not. The criterion `max_formal_defects` is met only when the defect count is
within the configured value. Quote `thresholds_applied` from the analysis when
a finding needs the number.

**Rivals** (`assessment.verdict.relations`): CONTRADICTORY means no state is
allowed by both; STRONGER/WEAKER mean one forbids everything the other does and
more; INCOMPARABLE means each forbids states the other allows. The
discriminating states are in `assessment.reports.comparisons[].discriminating_examples`
(counts in `forbidden_only_by_a` / `forbidden_only_by_b`): these are the
experiments worth running.

**Falsifiable content.** `min_excluded_fraction_of_applicable` is UNRESOLVED:
there is no published value for how much of its applicable space a hypothesis
must forbid. Do not invent one. Report the fraction from `metrics` without a
pass/fail unless the program has set the threshold in `.oase/thresholds.yaml`.

**Gate and AR.** `assessment.evidence_assessment` is the mapping to an
`oase.evidence-assessment.v1` record: copy `execution_outcome`,
`evidence_status` and `evidence` into the AR. A non-verdict maps to
`execution_outcome: blocked` and `evidence_status: not_assessed`, never to
`contradicted`.

**Mandatory relays.** Every relay in the analysis must reach the finding and
be acted on:

| Relay code | What it obliges |
|---|---|
| `formal.not_empirical` | Fires on every verdict. Never present a formal verdict as support for the hypothesis being true. |
| `formal.smt_fixed_size_only` | Scope the verdict to the declared variables and bounds; no parametric claim. |
| `formal.enumeration_declared_domains_only` | Scope the verdict to the declared domains. |
| `formal.lean_not_kernel_checked` | Present a Lean statement as a claim, not a proof. |
| `formal.formalization_is_draft` | Say the formal object came from a model and is unconfirmed; do not attribute the verdict to the prose until a researcher confirms the reading. |
| `formal.gate_single_sample` | Say there is no self-consistency evidence for the reading. |
| `formal.vacuous_entailment` | Do not report the consequence as a prediction of the hypothesis. |
| `formal.entailed_by_assumptions_alone` | Do not credit the hypothesis with the consequence. |
| `formal.thresholds_overridden` | Quote `threshold_sources` with the verdict. |
| `formal.formalization_ambiguous` | No formal verdict exists. Do not pick, rank or evaluate one of the readings. |
| `formal.formalization_failed` | No formal verdict exists. Do not infer one. |
| `formal.undecided` | Report the question as undecided; it is not evidence of a defect or a refutation. |
| `formal.blocked` | Report the check as blocked; record not_assessed. |
| `formal.not_reproduced` | Treat the run's verdict as unverified; do not cite it. |
| `formal.vacuous_relative_to_intent` | Return the hypothesis with the witness: its claims hold of a declared non-witness. |
| `formal.trivial_witness_satisfies_claims` | Show the satisfied default probe; ask whether the claims should exclude it. |
| `formal.claim_below_kernel_checked` | State each claim's trust rung; never call a claim proved below KERNEL_CHECKED. |
| `formal.fidelity_range_only` | Scope a fidelity relation to the range; conclusions were not compared. |
| `formal.lint_is_syntactic` | Treat OPEN lint findings as questions for a human, not defects. |

**Consequence rules.** A DECIDED defect stops the hypothesis from entering a
tournament as written: return it to its author with the verdict and, for
SELF_CONTRADICTORY, the conflicting assumptions in the report. CONTRADICTORY
rivals go to the tournament as a pair with their discriminating states
attached. EQUIVALENT rivals are merged before the tournament. For any
downstream reader: a formal verdict changes what a hypothesis can be tested
on, not how likely it is.

## Failure modes and the anti-fabrication guard

Do not decide these questions yourself. The verdict is whatever
`oase formal analyze` recorded. If the tool did not run, there is no verdict.
If the engine, z3 or the model is unavailable, report the task as blocked. Do
not estimate, and do not proceed on an assumed result.

Named pathologies:

- **Formal object does not say what the prose says.** The verdict is about the
  object. A sound object attached to the wrong reading proves nothing about
  the hypothesis; check the object against the statement before citing.
- **UNDECIDED read as unfalsifiable** or BLOCKED read as a failed gate. Both
  are non-verdicts (exit 10 and 4/7/8) with `not_assessed`.
- **An ambiguous formalization resolved by picking the majority reading by
  hand.** The tool refuses (exit 9); so must the finding.
- **FALSIFIABLE quoted as "testable" in the review-rubric sense.** It means
  the object forbids some state; feasibility of the experiment is a separate
  axis.
- **A verdict quoted from a run whose analysis says
  `reproduces_run: false`.**
- **Rival compared over different variables.** Relations are only meaningful
  over one state space; the engine refuses mismatched schemas (exit 9).

Upstream: CoResearcher (github.com/Fundacion-de-Neurociencias/coresearcher),
`integrations/oase`, ADR-DISCOVERY-069. Apache License 2.0.
