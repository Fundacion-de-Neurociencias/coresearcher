# openai/math time-travel benchmark: constrained parameters and cases (ADR-088), pre-registered protocol

Status: frozen before any convention was typed under it. Its SHA-256 is stored in
`OPENAI_MATH_CONSTRAINED_PROTOCOL.sha256` and in the ADR-085 freeze log `openai_math_chain_freezes.json`. The runner
(`scripts/benchmarks/openai_math_revision_bench.py typed --variant constrained`) refuses to start if the file has
changed.

## 1. Question

The typed re-measure (`OPENAI_MATH_TYPED_RESULTS.md`) left decided mismatches at the three withdrawals that were
artefacts:

- a sign compared outside the citing passage's domain (n odd, where the passage has n = 2k);
- a field that recorded which case of a lemma was used, not a convention.

ADR-088 adds two things to a typed convention:

- `where`: conditions on the parameters. Signs are compared only where both sides' conditions hold.
- `cases` and `case`: the cases a cited result covers, and the case a citation uses. A case the cited result does not
  cover is a decided MISMATCH.

**Questions.**

1. Typed blind again under the new schema, are the artefacts gone?
2. What decided mismatches remain, and do any of them reflect a corrected defect?

The typed re-measure found that the withdrawals' error lies in the citing construction, not in a convention of the
cited lemma. This protocol tests that conclusion: if it holds, no decided mismatch should remain at the withdrawals.

Scope: formal soundness only.

## 2. What is unchanged

- **Reused unchanged.** The scoring, encodability and adjudication rules of `OPENAI_MATH_CHAIN_PROTOCOL.md` and
  `OPENAI_MATH_TYPED_PROTOCOL.md`.
- **The base inputs.** The selection, the registry statements and hypotheses, and the citing contexts' variables and
  assumptions of the chain re-run.
- **Typing starts again from the untyped conventions.** The base for both sides is the chain re-run's text
  conventions. The typed re-measure's typed records are not shown to anyone.

## 3. Blind typing

- **The process.** As in sections 3.1 and 3.2 of `OPENAI_MATH_TYPED_PROTOCOL.md`, with fresh agent sessions and the
  instructions recorded in:
  - `openai_math_chain_procedure/CONSTRAINED_ENTRY_INSTRUCTIONS.md`;
  - `openai_math_chain_procedure/CONSTRAINED_CONTEXT_INSTRUCTIONS.md`.

  Both are recorded before any typist starts.
- **Entries.** Split in registry order between two typists.
- **Citing packets.** The same 69 opaque, shuffled packets, with every third packet going to the same typist.
- **Freezing.** Merged into `openai_math_constrained_registry.json` and `openai_math_constrained_contexts.json`. Each
  file is frozen before the next step.

## 4. Run, scoring and reporting

- **The run.** `typed --variant constrained` writes `openai_math_constrained_results.json`.
- **Reporting.** Results are reported next to the chain re-run (strings), ADR-087 on untyped inputs, and the typed
  re-measure.
- **Adjudication.** Every decided MISMATCH at a defect location and elsewhere is read by hand and labelled *reflects the
  defect*, *decided but not the defect*, or *artefact* (with its cause).
- **Regression.** The regression case replays this run, and its expectations are updated in the same pull request.
- **Counts.** With 17 defects, every rate is a count with its Wilson 95% interval.
