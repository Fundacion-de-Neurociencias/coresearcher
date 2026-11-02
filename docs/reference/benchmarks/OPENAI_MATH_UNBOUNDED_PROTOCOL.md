# openai/math time-travel benchmark: unbounded integer variables (ADR-090), pre-registered protocol

Status: frozen before any context was re-encoded. Its SHA-256 is stored in `OPENAI_MATH_UNBOUNDED_PROTOCOL.sha256` and
in the ADR-085 freeze log. The runner (`openai_math_revision_bench.py typed --variant unbounded`) refuses to start if
the file has changed.

## 1. Question

The case-scoped re-measure (`OPENAI_MATH_CASES_RESULTS.md`) showed where most of the remaining findings at defect
locations come from: the citing contexts gave unbounded integers (for example n = 2k) a representative range starting
at 0. A cited hypothesis such as n ≥ 3 was then "not discharged" with a counterexample that the passage itself
excludes.

ADR-090 adds integer variables with optional bounds, possibly unbounded. z3 decides them over the integers, with
`%` and `//` by a positive constant (parity).

**Questions.**

1. With every citing context's variables and assumptions re-encoded blind under the new instructions, do the
   representative-range findings disappear?
2. Does any finding appear or disappear at a defect location for another reason?

Scope: formal soundness only.

## 2. Inputs

- **Unchanged.** Everything frozen for the case-scoped re-measure: the registry `openai_math_cases_registry.json`,
  and the constrained citing contexts' conventions and cases.
- **The only new input.** The `variables` and `assumptions` of all 69 citing contexts, re-encoded from scratch.

## 3. Blind encoding

- **The encoders.** Fresh agent sessions. Their instructions are recorded verbatim in
  `openai_math_chain_procedure/UNBOUNDED_ENCODER_INSTRUCTIONS.md` before any encoder starts.
- **The packets.** The same 69 opaque, shuffled packets as the chain re-run, with no manuscript name, version or
  role. Every third packet goes to the same encoder.
- **Assembly.** `vars-contexts` puts the new variables and assumptions into the constrained contexts, keeping their
  conventions, and writes `openai_math_unbounded_contexts.json`. That file is frozen before the run. The coordinator
  may repair JSON syntax only.

## 4. Run and scoring

- **The run.** `typed --variant unbounded` writes `openai_math_unbounded_results.json`.
- **Scoring and adjudication.** As in the earlier protocols. Results are reported next to the case-scoped re-measure.
- **Regression.** The regression expectations are updated in the same pull request.
