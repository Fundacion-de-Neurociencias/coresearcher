# ADR-DISCOVERY-085: Freeze service, the obligation ledger as the standard path, and the composed chain

**Status:** Accepted
**Date:** 2026-11-01

**Modules:**
- [`python/discovery/freeze_service.py`](../../python/discovery/freeze_service.py)
- [`python/discovery/hypothesis_ledger.py`](../../python/discovery/hypothesis_ledger.py)
- [`python/discovery/verification_chain.py`](../../python/discovery/verification_chain.py)
- [`python/discovery/hash_chain.py`](../../python/discovery/hash_chain.py) (the ADR-083 event log, now shared)
- [`api/routers/freezes.py`](../../api/routers/freezes.py) (`/api/freezes/*`, `/api/chain/run`)
- [`api/routers/hypotheses.py`](../../api/routers/hypotheses.py) (`obligation_ledger` on `/api/hypotheses/evaluate`)
- [`python/cli/freeze.py`](../../python/cli/freeze.py), [`python/cli/chain.py`](../../python/cli/chain.py),
  [`python/cli/formal.py`](../../python/cli/formal.py) (`--freeze`, `--citations`, `--fidelity-spec`)
- [`tests/test_block_d_freeze_ledger_chain.py`](../../tests/test_block_d_freeze_ledger_chain.py)

**Builds on:**
- ADR-DISCOVERY-063: research lifecycle digests;
- ADR-DISCOVERY-068: status vocabulary, provenance, two-phase CLI;
- ADR-DISCOVERY-076: the obligation ledger;
- ADR-DISCOVERY-080: intent probe, trust ladder, fidelity service;
- ADR-DISCOVERY-082 and ADR-DISCOVERY-083: manuscript audit, cited-results registry;
- ADR-DISCOVERY-084: benchmarks as regression tests.

**Methodology:** block D of [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md), methods M3
(fix the acceptance criteria before seeing the work) and M5 (decompose into obligations, discharge each one
independently), and the composed chain of its section 3.

**Numbering:** 084 is the latest record on master, so this record is 085.

## Context

Blocks A to C made the methods separate capabilities: fidelity and vacuity (ADR-080), seams (ADR-083), regression
(ADR-084). A hypothesis submitted to CoResearcher still went through them only if the caller knew to call each one.
Two methods had no service at all:

- **M3.** The formalizer benchmark, the time-travel benchmark and the Yang–Mills checklist each froze their protocol
  by hand. Lifecycle projects hash artifacts (ADR-063), but nothing let an evaluation say "these are the criteria I
  was given before I looked" and have that checked.
- **M5.** The obligation ledger (ADR-076) existed for the Mahler case. A hypothesis evaluation returned a verdict and
  trust rungs, not the list of obligations its soundness rests on.

## Decision

### 1. Freeze service (M3)

- **What is frozen.** For a hypothesis: its discriminating states against its rivals, computed from the formal objects
  alone, with no observations. These are the states it forbids (an observation of one refutes it) and, per rival,
  the states only one of the two forbids, with the relation. The author may add stated criteria, frozen verbatim. For
  a protocol or checklist: the document.
- **Digests.** They are the lifecycle's own. Criteria use the SHA-256 of canonical JSON (`content_sha256`, as gate
  digests). A document uses the SHA-256 of its bytes (`bytes_sha256`, `sha256_file`, as ARTIFACT checks). A frozen
  protocol therefore has the digest that its `protocol.document` check records and that the lifecycle watcher
  re-checks. A freeze can be anchored to a lifecycle check and is refused if the two digests differ.
  `freeze hypothesis --out` writes the criteria as canonical JSON whose file digest is the freeze's.
- **Record.** Each freeze has an id (`FZ-` and 16 hex digits of its digest), its SHA-256, an author and a time.
  It is an event in a hash-chained log, shared with the registry (`hash_chain`, the ADR-083 style). The time is in
  the event payload, so it is covered by the hash. On load, a store is refused if its chain breaks, if a record no
  longer matches its digest, or if a record differs from its event. Freezing the same content again returns the
  earliest freeze.
- **Verification.** An evaluation that references a freeze verifies it first, against the hypothesis and rivals in
  normal form, or the document's bytes. It never recomputes the criteria, so a solver's choice of witness cannot
  break it. Each of the following is the non-verdict BLOCKED (`FrozenCriteriaChanged`):
  - a record that no longer matches its digest;
  - a digest other than the expected one;
  - an edited hypothesis or rival set;
  - an unknown freeze.

  The API answers 409, and the CLI exits with the new code 13.
- **Non-verdicts.** A solver that cannot decide the criteria freezes nothing. Criteria that were not decided cannot
  be frozen as decided.
- **Exposure.**
  - API: `POST /api/freezes/hypothesis`, `POST /api/freezes/document`, `GET /api/freezes/{id}` and
    `POST /api/freezes/{id}/verify` (read-only).
  - CLI: `coresearcher freeze hypothesis|document|show|verify`.
  - Store: `CORESEARCHER_FREEZE_PATH`. The CLI defaults to `.coresearcher/freezes.json`; the API keeps freezes in
    memory when the variable is unset.

### 2. The obligation ledger as the standard path (M5)

Every hypothesis evaluation returns an ADR-076 ledger beside its report: `POST /api/hypotheses/evaluate`, the
sidecar of `formal run`, the record of `formal analyze`, and the chain. Its obligations:

| Obligation | Discharged by | Notes |
| --- | --- | --- |
| `fidelity`: the formal object says what the prose says | `fidelity_spec` through the fidelity service (ADR-070) | EQUIVALENT or STRONGER is DISCHARGED_SYMBOLIC; WEAKER or INCOMPARABLE is REFUTED. Statement audits supplied in `claim_evidence` count as CERTIFIED_BY_AUTHOR. Otherwise OPEN |
| `vacuity`: no declared non-witness satisfies the claims | the intent probe (ADR-080) | OPEN when no non-witness is declared |
| `claim[i]`: consistent with the rest, and forbids some applicable state | the exact evaluation | REFUTED when the hypothesis is VACUOUS or SELF_CONTRADICTORY, or the claim forbids nothing |
| `observations`, only when given | the exact evaluation | REFUTED by a certain counterexample |
| `cite[i]`: each cited result is used validly | `cite_check` against the hypothesis's own variables, assumptions and scope, with the conventions of the use (ADR-083) | Only CLEAR with every hypothesis entailed is DISCHARGED_SYMBOLIC; a finding stays OPEN, never REFUTED |
| `consequence[i]`: each stated prediction is entailed | exact entailment | Vacuous entailment stays OPEN |

- **Strength of a discharge.** Exhaustive enumeration over declared domains and z3 are decision procedures, so a
  decided obligation is DISCHARGED_SYMBOLIC within its stated scope.
- **Non-verdicts.** If the evaluation is a non-verdict, every obligation is OPEN with the reason. Nothing undecided
  is recorded as decided.
- **Dependencies.** A DAG of the obligations, checked acyclic with no missing premise, is part of the ledger.
- **Roll-up.** The ledger's claim is "the hypothesis, as submitted, is formally sound". It takes the status of its
  weakest obligation (REFUTED dominates).
  - It is reported on the trust ladder as the lowest rung among the hypothesis's claims.
  - That rung is capped at CLAIMED while a cited premise is retracted or downgraded (ADR-083).
  - The relay LEDGER_NOT_PROVED, inside the ledger, says when any obligation is not proved.
- **Backward compatibility.** The ledger is a view computed beside the reports, like `claim_trust`. Every existing
  field of the evaluate response keeps its value.
  - The new request fields (`rivals`, `consequences`, `citations`, `fidelity_spec`, `freeze`) are optional. They
    add response fields (`comparisons`, `consequences`, `citations`, `prose_fidelity`, `freeze_check`) only when
    used.
  - Formal requests record the new fields only when set, so stored runs and their digests still reproduce. The new
    reports (`reports.citations`, `reports.prose_fidelity`) are compared by `formal analyze` report by report.

### 3. The composed chain

`verification_chain.run`, `POST /api/chain/run` and `coresearcher chain run` run section 3 of the methodology as one
flow:

1. freeze (M3);
2. formalize (M2);
3. fidelity (M1);
4. vacuity (M4);
5. obligations (M5);
6. seams (M6);
7. discharge (M8);
8. trust ladder (M7).

**Step states.** Each step reports a state:
- DONE;
- OPEN: nothing decided, nothing failed;
- NOT_APPLICABLE;
- NOT_RUN;
- a non-verdict (BLOCKED, UNDECIDED, INVALID_INPUT, FORMALIZATION_AMBIGUOUS, FORMALIZATION_FAILED).

**A non-verdict stops the chain.** Later steps are NOT_RUN, the chain's `formal_status` is that non-verdict, and the
roll-up stays OPEN or absent. It is never a verdict.

**How the freeze step works.**
- A freeze made earlier is verified, and a mismatch is BLOCKED.
- Otherwise the chain freezes the criteria itself before evaluating. It needs an author, and the relay
  CRITERIA_FROZEN_IN_SAME_RUN says this is weaker than a freeze recorded on an earlier date.
- For prose, the prose request is frozen as a document first. After the gate accepts a reading, the discriminating
  states of that reading are frozen, still before evaluation. A formalizer draft's claims stay CLAIMED.

### 4. Regression

The chain is the ninth case of the block C suite (`verification_chain`, fixture
`benchmarks/regression/fixtures/verification-chain/cases.json`). The expectations are frozen for two hypotheses:
- **Math:** order on 0..6 with three predictions, one of them false, a declared non-witness and an EQUIVALENT
  fidelity spec.
- **Biomedical-style:** pTau217 and decline, with a constant-biomarker non-witness, an age-only rival, and a cutoff
  cited under assay B although it was validated under assay A.

For each, the case records:
- every step's state;
- every obligation's status;
- the roll-up and its rung;
- the freeze digest;
- that the same freeze blocks the hypothesis once its claims are edited.

## Consequences

- A hypothesis's acceptance criteria can be fixed and dated before any evaluation, and an evaluation cannot quietly
  move them. Pre-registration is a checked property, not a sentence in a report.
- Every evaluation names what its soundness rests on and which part is still open. A FALSIFIABLE verdict no longer
  reads as "checked": fidelity without a spec, or vacuity without declared non-witnesses, is visibly OPEN.
- The chain is the single path block E will run on biomedical hypotheses (the pTau217 cutoff, the Alzheimer formal
  scenario).

## Limits

- A freeze proves when criteria were recorded and that they did not change. It does not prove that the author had
  not seen data before freezing, and it does not judge whether the criteria are good.
- Fidelity is OPEN unless the caller supplies a fidelity spec or statement audits. The service does not turn prose
  into a range by itself.
- An unfalsifiable claim is REFUTED in the ledger as a soundness defect of the hypothesis as submitted. A pure
  mathematical identity belongs in `consequences`, where entailment discharges it, not in `claims`.
- The API stores (freezes, registry) are process-wide, with the same limits as ADR-083's registry.
- Scope is formal soundness. Sources, authors and provenance never decide validity, and no generation code is part
  of this record.
