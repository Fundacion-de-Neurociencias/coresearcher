# openai/math time-travel benchmark: typed conventions (ADR-087), pre-registered protocol

Status: frozen before any convention was typed. Its SHA-256 is stored in `OPENAI_MATH_TYPED_PROTOCOL.sha256` and
in the ADR-085 freeze log `openai_math_chain_freezes.json`. The runner
(`scripts/benchmarks/openai_math_revision_bench.py typed`) refuses to start if the file has changed.

## 1. Question

The full-chain re-run (`OPENAI_MATH_CHAIN_RESULTS.md`) ranked first among the next gaps the semantic comparison of
conventions. There, the seams step compared conventions as strings, so it flagged about a third of all citations
wherever they were. ADR-087 makes a convention typed: named fields compared as atoms, and named sign quantities
compared as integer formulas over declared parameter ranges. Two untyped texts that differ are now UNCOMPARED, a
non-verdict, not a MISMATCH.

**Questions.**

1. With conventions typed blind on both sides, how much of the chain's alarm load disappears?
2. Does any defect become a decided convention MISMATCH at its location? In particular, do any of the three
   withdrawals, whose notices name a sign imported under the wrong orientation convention?

Scope: formal soundness only.

## 2. What is unchanged

- **Inputs reused unchanged.** Everything frozen for the chain re-run:
  - the dataset, the selection, the registry statements and hypotheses;
  - the citing contexts' variables and assumptions;
  - the scoring rules, the encodability judgements and the adjudication labels of `OPENAI_MATH_CHAIN_PROTOCOL.md`.
- **The only input that changes.** The `conventions` of each registry entry and of each citing context.
- **The code that changes.** `typed_conventions` and its use in `cited_registry.check_conventions` (ADR-087). The
  `REGISTRY_AUDIT` check does not read conventions, so its verdicts are expected to stay the same. Any change is
  reported.

## 3. Blind typing

### 3.1 Registry conventions

- **Typists.** Fresh agent sessions that know nothing of this benchmark. Each receives the registry entries alone
  (source, locator, statement, hypotheses, text conventions, the writer's notes) and may re-read the cited work. The
  instructions are recorded verbatim in `openai_math_chain_procedure/TYPED_ENTRY_INSTRUCTIONS.md` before any typist
  starts.
- **The task.** For each convention tag, keep the text and add:
  - `fields`, for named choices the statement depends on (for example the orientation of each branch, the direction
    of a homotopy, the lattice spacing);
  - `signs`, for every sign or normalization the statement fixes as a function of integer parameters, with `params`
    giving the parameters' ranges.

  Names are chosen by the typist and listed with a one-line meaning.
- **Limits.** A typist may add a tag the text conventions missed, if the cited statement depends on it. It may not
  change the statement or the hypotheses.
- **Assembly.** `typed-registry` merges the records into `openai_math_typed_registry.json`, which is frozen before any
  context is typed.

### 3.2 Citing conventions

- **Typists.** Fresh agent sessions, with instructions recorded in
  `openai_math_chain_procedure/TYPED_CONTEXT_INSTRUCTIONS.md`.
- **Packets.** The same 69 opaque, shuffled packets as the chain re-run (seed 20261102), with the entry's typed
  conventions in place of its text conventions.
- **The task.** For each tag of the entry, give the passage's own convention with the same field names and sign
  quantity names, only where the passage states or fixes it. A field or sign the passage does not fix is left out.
- **Assembly.** `typed-contexts` merges the records into `openai_math_typed_contexts.json`, which is frozen before the
  run.

Packets are divided among typists in shuffled order: every third packet goes to the same typist. The coordinator may
repair JSON syntax only. Each repair is listed.

## 4. Run and scoring

- `typed` runs the same flow as `chain`, writing `openai_math_typed_results.json`.
- Per-defect verdicts and the alarm load are scored as in sections 6 and 7 of the chain protocol, and are reported
  side by side with:
  - the first run (1/17);
  - the chain re-run as frozen (expectations v4);
  - the chain re-run's untyped inputs under ADR-087 semantics. This isolates the effect of the code from the effect of
    the typing.
- **Adjudication.** Every HIT and every MISMATCH at a defect location is read by hand. It is labelled *decided and
  reflects the defect*, *decided but not the defect*, or *coincidence*.
- **Regression.** The `openai_math_time_travel` regression case replays the typed run as well. Its expectations are
  updated in the same pull request.
- **Counts.** With 17 defects, every rate is a count with its Wilson 95% interval.
