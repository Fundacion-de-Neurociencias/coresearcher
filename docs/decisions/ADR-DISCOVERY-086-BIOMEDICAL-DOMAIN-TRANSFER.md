# ADR-DISCOVERY-086: Biomedical domain transfer of the verification chain

**Status:** Accepted
**Date:** 2026-11-01

**Modules:**
- [`python/discovery/biomedical_units.py`](../../python/discovery/biomedical_units.py)
- [`python/discovery/biomedical_conventions.py`](../../python/discovery/biomedical_conventions.py)
- [`python/discovery/biomedical_domain.py`](../../python/discovery/biomedical_domain.py)
- [`python/discovery/mechanistic_chain.py`](../../python/discovery/mechanistic_chain.py)
- [`python/discovery/verification_chain.py`](../../python/discovery/verification_chain.py) (`mechanism`, `biomedical`)
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py) (convention vocabulary)
- [`python/discovery/hypothesis_ledger.py`](../../python/discovery/hypothesis_ledger.py) (domain obligations)
- [`api/routers/biomedical.py`](../../api/routers/biomedical.py) (`/api/biomedical/*`)
- [`python/cli/biomedical.py`](../../python/cli/biomedical.py) (`coresearcher biomedical …`)
- [`tests/test_block_e_biomedical.py`](../../tests/test_block_e_biomedical.py)

**Builds on:**
- ADR-DISCOVERY-059: formal hypothesis objects;
- ADR-DISCOVERY-061: the formalizer and formal workbench, with the Alzheimer formal scenario;
- ADR-DISCOVERY-076: the obligation ledger;
- ADR-DISCOVERY-080: intent probe, trust ladder;
- ADR-DISCOVERY-083: cited-results registry;
- ADR-DISCOVERY-084: benchmarks as regression tests;
- ADR-DISCOVERY-085: freeze service, ledger, composed chain.

**Methodology:** block E of [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md), all
methods, carried to biomedical hypotheses.

**Case:** [`BIOMEDICAL_CHAIN.md`](../reference/cases/BIOMEDICAL_CHAIN.md) shows every step on every hypothesis.

**Numbering:** 085 is the latest record on master, so this record is 086.

## Context

Block D made the eight-step chain one flow. Block E ran it on biomedical hypotheses to find what it could not yet
check. Three hypotheses were run on the chain as it stood on master:

- **(a) The pTau217 two-cutoff rule** (`ptau217_cutoff_case.py`): **REFUTED.** Its claims are the rule's two
  guarantees, and the assumptions entail them. Claims without content of their own are refuted by the ADR-085 ledger.
  Two things were missing:
  - the hypothesis's shape for a decision rule (premises as claims, guarantees as consequences);
  - any check of units, of the cutoff's validated conditions, or of the population the rule applies to.
- **(b) The Alzheimer formal scenario** (three rivals, ADR-061): **OPEN** on fidelity and vacuity, with the claims
  discharged. Nothing checked whether the variable each rival calls explanatory does any work in its claims.
- **(c) A mechanistic chain written as prose** ("amyloid raises plasma pTau217, which drives tau spread, which
  worsens cognition"): **BLOCKED.** No formalizer model was configured, and there was no deterministic path from a
  mechanism to a formal object. No obligation existed for a link, for the sign of an effect, or for the compatibility
  of the links with the end-to-end prediction.

Two smaller gaps sat across all three:
- **Unit comparison.** The registry compared units by string, so "pg/mL" against "ng/L" was a MISMATCH.
- **Repeated conventions.** "assay" and "validated_assay" were different tags. Every citation had to repeat the
  hypothesis's conventions.

## Decision

### 1. Units and dimensional homogeneity (`biomedical_units`)

- **Reading units.** A unit string is read into a scale and base dimensions:
  - mass, volume and amount, with SI prefixes;
  - time, from seconds to years;
  - length;
  - enzyme and international units;
  - percent;
  - unknown symbols (SUVR, centiloid, points), each as its own dimension.
- **Comparing two units.** The result is one of:
  - SAME (pg/mL and ng/L);
  - SAME_DIMENSION, with the factor (pg/mL and ng/mL, 0.001);
  - DIFFERENT_DIMENSION;
  - UNREADABLE.
- **Checking a hypothesis.** Unit inference walks the expression tree of every scope, assumption, claim and
  consequence:
  - comparisons, sums and differences need the same unit;
  - products and quotients combine units;
  - a numeric literal takes the unit of what it meets.
- **Outcomes per predicate:** HOMOGENEOUS, DIMENSION_MISMATCH, SCALE_MISMATCH, UNDECLARED_UNIT or NOT_APPLICABLE.
  NOT_APPLICABLE means that no two quantities with units meet.

### 2. A convention vocabulary for the registry (`biomedical_conventions`)

The kinds are:
- `validated_assay` (alias `assay`);
- `platform`;
- `matrix`;
- `units`;
- `validated_population` (alias `population`);
- `reference_standard`;
- `scale_direction`;
- `cutoff_derivation`.

`cited_registry.check_conventions` compares tags under their canonical names, and compares values as follows:
- **Units** by unit algebra. A different scale is a MISMATCH that names the factor.
- **Matrix, reference standard, scale direction and cutoff derivation** by canonical value. The synonym tables merge
  spellings of the same thing only: "cerebrospinal fluid" is CSF, and "lower is better" is higher_is_worse. EDTA
  plasma stays distinct from plasma, and a fixed sensitivity of 90% stays distinct from one of 95%.
- **Anything else** by normalized string, as before.

### 3. Domain probes and the units obligation (`biomedical_domain`)

A `biomedical` block can declare three things: `units` per variable, the hypothesis's own `conventions`, and
`probes`. Its obligations join the ADR-085 ledger:

| Obligation | Decided by | Status |
| --- | --- | --- |
| `units` | Unit algebra over every predicate | DISCHARGED_SYMBOLIC when homogeneous; REFUTED on a dimension or scale mismatch; OPEN on an undeclared unit |
| `probe:null_biomarker[b]` | Exact two-copy search for two applicable states that differ only in `b`, one allowed and one forbidden | REFUTED when there are none: a constant would do as well, so the biomarker does no work. OPEN when a stated prediction follows from the claims that do not mention `b`, because that prediction does not test the biomarker. DISCHARGED_SYMBOLIC otherwise |
| `probe:untreated_arm` | Exact satisfiability and entailment inside the untreated arm | REFUTED when the untreated arm must show the predicted outcome; OPEN when it may; DISCHARGED_SYMBOLIC when it cannot |
| `probe:population` | Exact satisfiability of scope and assumptions outside the validated population | OPEN with a witness when the hypothesis applies outside it. This is a transfer defect, like a convention mismatch (ADR-083), not a refutation. DISCHARGED_SYMBOLIC otherwise |

Enumeration and z3 decide every probe. A solver non-verdict leaves the obligation OPEN with the reason. Each use of a
cited result inherits the hypothesis's conventions, plus the unit of the `variable` it names. Conventions written on
the use itself win.

### 4. Mechanistic chains as obligation templates (`mechanistic_chain`)

**What a mechanism is.** Nodes, each with ordered levels or a continuous range, and optionally a unit and a scale
direction. Signed links between the nodes. An end-to-end prediction.

**The encoding.** The mechanism compiles to an ADR-059 hypothesis in two worlds: X_0 (baseline) and X_1 (after an
intervention). Each node with parents follows the sign semantics of a signed influence graph:
- if no parent moves, the node does not move;
- if the parents push it one way, it moves that way;
- if the parents push it opposite ways, it is unconstrained.

The prediction is a consequence: moving the source up, with the other root nodes fixed, moves the target in the
predicted direction.

**Obligations.**
- `link[i]`: the link admits a change of its source. A node with a single level, or no room to move, REFUTES the link.
- `link_sign[i]`: the declared sign agrees with the effect. "worsens" on a higher_is_better score means "-". A
  contradiction is REFUTED. An effect without a declared scale direction is OPEN.
- `mechanism:compatibility`: the links together admit the intervention and entail the prediction. A sign that does
  not compose, or two paths of opposite sign, is REFUTED, with counterexamples.

The ledger DAG makes compatibility depend on every link and every sign. The untreated arm (no root node moves) is
probed automatically against the predicted outcome.

**Controlled prose.** `parse_prose` reads a restricted language: "A raises B, which drives C, which worsens D."
- Each verb fixes either a sign or an effect.
- Each noun phrase must be a declared node name or alias.
- It is a deterministic grammar with one reading, not a model. A sentence outside it, or an unknown noun phrase, is
  FORMALIZATION_FAILED, never a guess (M8).

### 5. Wiring

- **Chain.** `verification_chain.run`, `POST /api/chain/run` and `coresearcher chain run` accept a `mechanism`
  instead of a hypothesis or prose, and a `biomedical` block. The steps report the new obligations as follows:
  - formalize: COMPILED;
  - vacuity: the probes, beside the declared non-witnesses;
  - obligations: the mechanism's links;
  - seams: units and the validated population, beside the cited results.
- **No block, no change.** Requests without either key produce the ADR-085 result unchanged. The nine earlier
  regression cases still pass.
- **API:**
  - `POST /api/biomedical/check` (units and probes of one hypothesis);
  - `POST /api/biomedical/mechanism` (compile and decide a mechanism);
  - `GET /api/biomedical/vocabulary`.
- **CLI:** `coresearcher biomedical check|mechanism|units|vocabulary`. The exit codes are:
  - 0: all discharged;
  - 1: a REFUTED obligation;
  - 10: something OPEN;
  - 11: prose outside the grammar;
  - 9: refused input.
- **Ledger message.** A claim the scope and assumptions already entail is still REFUTED, as ADR-085 decided. Its
  reason now says that it follows from them, and that a guarantee derived from premises belongs in `consequences`,
  with the premises as claims.

### 6. Regression

`biomedical_chain` is the tenth case of the block C suite, with fixture
`benchmarks/regression/fixtures/biomedical-chain/cases.json`. It holds eleven hypotheses:
- pTau217 restated, as submitted, without the renal assumption, and with a unit seam;
- the three Alzheimer rivals;
- the mechanism from prose, with a sign seam, with a saturated node, and outside the grammar.

For each hypothesis, the case freezes:
- every step's state;
- every obligation;
- the roll-up;
- the unit, probe, mechanism and citation outcomes;
- for enumerated hypotheses, the freeze digest.

The restated pTau217 rule is also checked BLOCKED against its own freeze after an edit. Freeze digests of hypotheses
decided by z3 are not frozen: their witnesses are the solver's choice and may differ between platforms.

## Consequences

- A biomedical hypothesis can now be checked for what M6 calls seams. The checks cover:
  - units, which earlier passed unexamined;
  - the conditions a cited cutoff was validated under;
  - the population the hypothesis applies to;
  - the direction of a scale.
- M4's biomedical failures are now checked properties of the formal object, with exact witnesses: an idle
  biomarker, and an outcome the untreated arm already shows.
- A mechanism stated as a chain of effects is a ledger of independent link obligations, and the trust ladder shows
  exactly which link fails.
- The draft Alzheimer formalization of HYP-TAU-CONNECTOME is shown to make tau a scope selector only: the
  null-biomarker probe on tau is REFUTED. This is a fidelity finding about the draft, which ADR-061 already lists as
  pending review. It is not a finding about the scientific hypothesis.

## Limits

- **Fidelity stays OPEN on every run.** The chain still has no independent formal reading of the scientist's prose to
  compare with. A compiled mechanism is one deterministic reading, not two that agree. Fidelity needs a fidelity spec
  or a statement audit from the scientist.
- **Mechanism scope.** The encoding is qualitative (signs) and acyclic. It has no magnitudes, no time and no
  feedback. A cycle is refused, not approximated.
- **Units.** The unit table is small and explicit. An unknown symbol is its own dimension, so two different scales
  are never silently comparable. A literal adopts its partner's unit, so the numeric value of a cutoff is not checked
  against any reference.
- **Probes.** Probes decide properties of the formal object over its declared domains. Whether a population, a cutoff
  or a mechanism is clinically right is never judged. Every value in the fixtures and the case document is
  illustrative.
- **Scope.** Formal soundness only. Provenance never decides validity, and no generation code is part of this record.
