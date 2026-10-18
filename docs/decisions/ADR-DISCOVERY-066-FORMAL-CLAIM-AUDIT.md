# ADR-DISCOVERY-066: Audit template for claimed formal results

**Status:** Accepted
**Date:** 2026-10-18
**Module:** [`python/discovery/research_lifecycle.py`](../../python/discovery/research_lifecycle.py) (template
`formal-claim`)

## Context

Public claims of the form "a model solved problem X, with a Lean proof" raise four questions:

1. Was there undeclared human input?
2. Is the human-readable proof correct, and has it been reviewed?
3. Is the Lean statement a faithful formalization of the problem as posed?
4. Are the prose and Lean solutions equivalent?

Questions 2 to 4 decide whether the result is valid. Question 1 does not. A correct proof is correct whoever wrote
it, so human input bears on attribution and on what the claim shows about the tool's ability, not on validity. This
follows the principal investigator's position (2026-10-18) and the earlier decision that human sign-offs are
recorded but do not gate a project (ADR-DISCOVERY-063, amendment).

CoResearcher has evidence on where machines can and cannot answer these questions:

- **What a machine can check:** whether a proof establishes a formal statement. Comparator accepted 19/19 originals
  and rejected 52/52 mutants on the openai/math pilot (claims register, row 19).
- **What a machine cannot yet check:** whether a statement is faithful to the prose. The automatic fidelity check
  scored AUROC 0.524 on the same pilot, which is chance.

## Decision

A lifecycle template, `formal-claim`, with two separate blocks.

**Validity.** All of these block a release:

| Question | Check | Who can satisfy it |
| --- | --- | --- |
| The proof establishes the formal statement | `execution.proof_checked` | A verifier tool (kernel, Comparator); the prover's own report never counts |
| The statement is faithful to the problem as posed | `controls.statement_fidelity` | An expert review |
| The prose proof is correct | `analysis.prose_review` | Expert or peer review |
| The prose and formal solutions are equivalent | `analysis.equivalence` | An expert review |

The optional check `controls.mutant_rejection` shows that the proof check is not vacuous.

**Provenance.** The check `report.provenance` records who contributed what: people, models and tools. It is
optional and never blocks. The release notes always state it, or say "not declared", and label it as not affecting
validity.

The project also records the original problem, the formal statement, the prose solution, the audit protocol and the
tool versions, each hashed, and it can be shipped as a research package (ADR-DISCOVERY-065).

## Consequences

- An audit gives a separate answer to each validity question, instead of one verdict.
- Three of the four validity questions rest on expert review. That is the honest state of the art: the expert
  checks become automatic only once an automatic fidelity auditor passes a pre-registered benchmark. The one
  designed in LEAN_ORACLE_PROTOCOL.md section 6 has not been built.
- Expert reviews block in this template, unlike optional sign-offs elsewhere. Here they are the evidence of validity,
  not an approval.
