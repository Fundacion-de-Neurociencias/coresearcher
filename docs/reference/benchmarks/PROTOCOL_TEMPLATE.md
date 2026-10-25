# Benchmark protocol template

Status: template. Copy it to a new file named `<NAME>_PROTOCOL.md` before any run. A protocol is frozen once its first
measurement exists: its SHA-256 is recorded with every raw result, and scoring refuses results produced under another
hash. Sections 1 to 6 follow the existing protocols. Sections 7 and 8 are required for every protocol written after
2026-10-25, because they come from the review of ScientistTwo (arXiv:2609.19644, Nam et al., 2026): acceptance rules that
ignore attribution, and results that were selected on the set they report, are the two failures we want to rule out.

## 1. Question

One paragraph. State the question as a comparison or a rule that can come out false.

## 2. What is not claimed

Name what the result does not show. For generated artefacts, say explicitly that a high score is not correctness.

## 3. Materials and rules fixed in advance

Models with exact tags and digests, data with hashes, prompts with hashes, seeds, budgets. Nothing here changes after a
result is seen.

## 4. Procedure

Numbered steps. Each step states its input, its output file, and the hash of that output.

## 5. Metrics

Each metric with its denominator. Rates always come with the number of items they are computed on.

## 6. Pre-registered criteria

Each criterion is a threshold on an interval or on a count, written before the run. A criterion not met is reported as
not met.

## 7. Attribution

Required when the protocol claims that a mechanism, component or method produces an effect.

- Each claimed mechanism has a comparison arm that removes it and keeps everything else fixed (for example, C3 against
  C4 in the inspiration protocol, criterion M).
- Acceptance requires the effect to be attributable to the mechanism. A gain that the ablation traces to generic
  settings (more compute, a larger budget, a training control, an evaluation detail) does not count as a contribution of
  the mechanism, even when the headline metric moves.
- If no comparison arm can be run, the protocol says so and reports the effect as not attributed.

## 8. Integrity checks

Each check is part of the procedure, not an afterthought, and each one records its outcome in the results file.

- **Selection and reporting are separate.** Any choice among candidates (the best idea, the best prompt, the best
  configuration) uses a selection set that is not part of the reported set. If the same set is used, the result is
  labelled exploratory and no criterion is read from it.
- **Re-run.** A reported number is reproduced from the released code and data by a run that does not share the author's
  session. The hash of the re-run output is recorded.
- **Judge independence.** The judge that decides the final result does not take part in generation, refinement or
  selection. When a judge from the same model family is unavoidable, the protocol says so and reports the agreement.
- **References.** Every cited work that the protocol relies on has a DOI or an identifier that resolves to a work with the
  same title (`scripts/benchmarks/check_references.py`). Items that cannot be checked are listed, not dropped.
- **Protocol immutability.** The protocol file hash in the results equals the hash of the file at the commit that
  produced them.

## 9. Reporting

For every arm: denominator, rate or score with its interval, the random-reference or null control where one exists, the
number of unparsed or invalid outputs, the exact model and prompt hashes, and the outcome of each check in section 8.

## 10. Known limitations, stated in advance

Each limitation that could change the sign or the size of a result.

## 11. Revision history

Dated entries. A change after the first measurement starts a new protocol file with a new hash.
