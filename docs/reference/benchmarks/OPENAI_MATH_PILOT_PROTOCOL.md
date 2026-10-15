# openai/math statement-fidelity pilot: pre-registered protocol

Status: written before the pilot was run. The SHA-256 of this file is stored with every result.

## 1. Purpose

A pilot of Task A (statement fidelity) on 20 formalized results from `openai/math`. It has two goals:

1. **Feasibility.** Can prose/Lean pairs be extracted and mutated automatically and reproducibly?
2. **First measurement.** How well does `SemanticBijectivityAuditor` (ADR-DISCOVERY-048) flag a formal
   statement that no longer matches its prose description?

A pilot of this size can show that the pipeline works and estimate an effect roughly. It cannot support a
precise performance claim.

## 2. Source (frozen)

- Repository: `https://github.com/openai/math` (Apache-2.0), commit
  `1581d4cbdd69a0faf34b2089614fe2a814316a6a`. All files are read at this commit.
- Unit: a result family listed in `CONTENTS.md` with a `([Lean](lean/docs/NNN.md))` link (242 families at this commit).
- **Prose side:** the `## Scope` section of `lean/docs/NNN.md`. It describes what the formalization proves,
  which is narrower than the family summary and therefore the fair counterpart of the formal statement.
- **Formal side:** the first Comparator statement linked in that note (`lean/ComparatorChallenges/*.lean`).
  These files hold the reference statement with `sorry` in place of the proof.

## 3. Sampling

- Eligible: families whose scope note has a non-empty `## Scope` section and links at least one
  `ComparatorChallenges/*.lean` file containing a `theorem`.
- Sample: 20 families drawn with `random.Random(20261013).sample` from the eligible list sorted by family number.
- No family is inspected, excluded or replaced after the draw. Families whose files cannot be parsed are
  reported as extraction failures, not replaced.

## 4. Labels and mutations

Each original pair has label **match** (0). Each mutant has label **mismatch** (1). Mutations edit the
theorem statement only (the text between `theorem` and `:= by`). Each one is applied when its pattern is present:

| Code | Mutation |
| --- | --- |
| M1 | Change the first numeric literal `n` to `n + 1` |
| M2 | Swap the first order relation (`<` ↔ `≤`, `>` ↔ `≥`) |
| M3 | Swap the first quantifier (`∀` ↔ `∃`) |
| M4 | Remove the last explicit hypothesis binder `(name : type)` of the signature |
| M5 | Negate the conclusion: `¬ (conclusion)` |

The labels hold by construction: after a mutation, the formal statement no longer states what the prose
describes. **No Lean toolchain is used in this pilot** (none is installed here). Lean or Comparator
confirmation that each mutant differs from the proved statement is deferred to the full benchmark.

## 5. Systems compared

- **S1, CoResearcher:** `SemanticBijectivityAuditor.extract_prose_specifications(scope, title)`,
  `extract_lean_specifications(lean, theorem_name)` and `audit_bijective_alignment(...)`.
  Flagged = `not is_bijective`; score = `drift_score`.
- **B0, always-match:** never flags. Sensitivity 0, specificity 1 by definition.
- **B1, numeric consistency:** flags when the Lean statement contains a numeric literal that does not appear
  in the prose. Score = number of such literals.

## 6. Metrics and uncertainty

- Sensitivity (mutants flagged), specificity (originals not flagged), per system and per mutation type,
  with 95% Wilson intervals.
- AUROC of the score (Mann–Whitney form, ties count one half), with a 95% bootstrap interval that
  resamples **families** (2,000 resamples, seed `20261013`), because the mutants of one family are not independent.
- Null control: the same AUROC with labels permuted within each family (seed `7013`).

## 7. Pre-registered criteria

- **Feasibility:** at least 18 of 20 families yield a parseable pair, and at least 3 mutation types apply to
  at least 15 of those pairs.
- **Hypothesis H1 (S1 performance):** the lower bound of the family-bootstrap interval for S1's AUROC is above 0.5.
- The result is reported whichever way it goes. The code under test is frozen at the CoResearcher commit
  recorded in the results.

## 8. Known limitations (stated in advance)

- Mutations are syntactic and cover only some error kinds. Real errors (withdrawn or corrected manuscripts)
  belong to Task B.
- The auditor's extractors target analysis vocabulary (derivative orders, Sobolev spaces, dimensions). A low
  score on general mathematics would measure that scope limit, not a bug.
- CoResearcher tests and modules already mention `openai/math`. No family is used for tuning here.
