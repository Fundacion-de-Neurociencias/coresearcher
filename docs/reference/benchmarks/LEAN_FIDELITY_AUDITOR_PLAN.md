# Lean-based statement-fidelity auditor: plan

Status: design, written before any Lean run. Not a pre-registered protocol yet: phase 3 turns it into one.
This expands section 6 of [LEAN_ORACLE_PROTOCOL.md](LEAN_ORACLE_PROTOCOL.md).

## 1. Question

Does a formal Lean statement say what its prose says? The [openai/math pilot](OPENAI_MATH_PILOT_REPORT.md)
showed that `SemanticBijectivityAuditor` cannot answer this for general mathematics. This plan tests whether
Lean itself can, by turning the prose into a second Lean statement and asking Lean whether the two are
equivalent.

## 2. Method

For a family with prose `P` and reference statement `S_ref` (or a mutant `M` in its place):

1. **Context.** Take the family's Comparator challenge file, remove the target theorem and its docstring, and
   keep everything else (imports, namespaces, definitions, `variable` lines). The model can then use the
   file's own names, such as `tiltMean`. It never sees `S_ref` or any mutant.
2. **Autoformalize.** A model writes one Lean statement `S_p` from `P` and the context.
3. **Elaborate.** `theorem candidate : S_p := by sorry`, checked in the context. If this fails, the outcome is
   *abstain*. An abstention is not a verdict on the target.
4. **Compare** `S_p` with the target `T` (`S_ref` or `M`), in this order, with a fixed heartbeat budget:
   - a. `example : (S_p) = (T) := rfl`: the two are definitionally equal.
   - b. `example : (S_p) ↔ (T) := by <fixed tactic script>`: the two are proved equivalent.
   - c. Neither: *not shown*.
5. **Verdict.** *Faithful* if a or b succeeds, *flagged* otherwise. A flag means "not shown equivalent", not
   "refuted". Refuting a direction is not attempted in the first version.

Comparator is not needed: nothing here checks a proof against the paper's solution. Phases 0–2 can therefore
run on any machine with Lean 4 and Mathlib, Windows included. Only the oracle in
[LEAN_ORACLE_PROTOCOL.md](LEAN_ORACLE_PROTOCOL.md) needs Linux.

## 3. Phases

### Phase 0. Environment (no model)

1. Install `elan`. openai/math pins `leanprover/lean4:v4.34.1` in `lean/lean-toolchain`, and `elan` picks it up.
2. Clone openai/math at `1581d4cbdd69a0faf34b2089614fe2a814316a6a`, then run `lake exe cache get` in `lean/`.
   Do not run `lake update`.
3. Run `python scripts/benchmarks/openai_math_lean_fidelity.py env-check --math-root <openai-math>`. The 19
   pilot challenges import only `Mathlib` and carry their own definitions, with proofs already `sorry`, so
   nothing from openai/math has to be built. For each challenge it checks the statement extraction
   (balanced, found once, same theorem name) and elaborates the file with `lake env lean`.

Done when all 19 pass both checks. The output, `docs/reference/benchmarks/lean_fidelity_env_check.json`,
records OS, Lean version and elaboration time per file.

**Windows notes** (found during the first setup, 2026-10-17). None of them changes a pinned file or commit:

- Clone openai/math with `core.longpaths=true` and leave `preprints/` out with a sparse checkout. Some PDF
  paths are longer than Windows allows, and the PDFs are not needed.
- Set `core.autocrlf=false` in the clone before checking out. With Git for Windows' default (`true`), files
  are checked out with CRLF and the dependency patches in `lean/patches/` fail to apply (`iut` first).
- Run `lake exe cache get` with `GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.autocrlf GIT_CONFIG_VALUE_0=false
  GIT_CONFIG_KEY_1=core.longpaths GIT_CONFIG_VALUE_1=true`, so the dependency clones get the same settings
  without touching the global Git configuration.
- `AINTLIB` at `160e4466` has a top-level file named `2026-07-16T07:39:08Z`. Windows does not allow `:` in
  file names, so checkout fails. In `.lake/packages/AINTLIB`, set `core.protectNTFS=false`, exclude that one
  file with a sparse checkout, and check out the pinned commit. The file is not Lean code.
- Lake then warns that the 11 patched dependencies have local changes. This is expected: the changes are the
  patches.

### Phase 0 result (2026-10-17, Windows 11)

Lean 4.34.1, openai/math at `1581d4cb`, Mathlib cache of 8,908 files. Extraction was sound and the challenge
elaborated for 19 of 19 pairs, at about 37 s per file, most of it spent loading Mathlib. Family 277 is the
only statement that differs from the frozen pilot one, as expected after the extraction fix. Negative
control: the pilot mutant F243_M3 fails with `unexpected token '['; expected ','`, the error the oracle
reported, so the harness does detect parse errors.

### Phase 1. Can the comparison step prove equivalences? (no model)

This measures the prover alone, so that a later failure can be attributed to the formalizer or to the prover.
For the target theorem of each of the 19 pilot challenges (the first entry of `theorem_names` in its
Comparator config):

- **Identity control:** `S_ref` against itself. Must succeed. A failure means the harness is broken.
- **Mutant control:** `S_ref` against each mutant that the fixed operators produce from it. Must come out
  *not shown*. If one is proved equivalent, that mutant is label noise, and this must agree with the Lean
  oracle.
- **Sentinel:** `2 + 2 = 4 ↔ 2 + 2 = 5` in every file. It must come out *not shown*. If it does not, or if
  Lean reports an error outside the checks, the whole family is marked untrusted instead of scored.
- **Equivalent rewrites:** meaning-preserving rewrites of `S_ref`, generated by fixed rules: renaming bound
  variables, `a < b` to `b > a`, reordering the arms of `∧` and `∨`, currying `A ∧ B → C` to `A → B → C`,
  and adding `¬ ¬`. The fraction proved equivalent is the **prover recall**. These are the rewrites a correct
  formalizer typically produces.

The tactic script is tuned here, and only here, on the rewrites. Phase 1 fixes it before any model output is
seen. Starting point: `constructor <;> intro h <;> first | exact h | simpa using h | aesop | tauto`, under
`set_option maxHeartbeats 400000`.

**Go/no-go:** prover recall ≥ 0.8 and every mutant control *not shown*. Below that, improve the comparison
before involving a model.

### Phase 1 result (2026-10-17, Windows 11)

Run with `controls`; output in `lean_fidelity_phase1_controls.json`, about 1 min per family with 4 in
parallel. No family was untrusted, and the sentinel failed as expected in all 19 files.

| Check | n | Starting tactic | Tuned tactic |
|---|---|---|---|
| Identity proved | 19 | 19 | 19 |
| Mutants proved equivalent (must be 0) | 49 | 0 | 0 |
| Rewrites proved: rename | 9 | 9 | 9 |
| Rewrites proved: `<` to `>` | 8 | 8 | 8 |
| Rewrites proved: swap ∧/∨ | 6 | 2 | 6 |
| Rewrites proved: curry | 2 | 2 | 2 |
| Rewrites proved: double negation | 19 | 16 | 19 |
| **Prover recall** | 44 | **0.84** | **1.00** |

One tuning step was made: a `simp only [not_not, and_comm, and_left_comm, and_assoc, or_comm, or_left_comm,
or_assoc]` alternative before the two-direction proof. Both versions meet the go criterion, so phase 1 is a
**go**. The tactic is now frozen for phase 2.

Limits of this result:

- The tuned recall is in-sample: the same rewrite rules were used to tune and to measure. A formalizer's
  rewrites will be more varied, so phase 2 measures recall again on real model output.
- Renaming and `<`/`>` are definitional and close with `Iff.rfl`. On the rewrites that need reasoning, the
  starting tactic proved 20 of 27, and the tuned one 27 of 27.
- Curry applied to only 2 statements, and swap to 6. These counts are too small to estimate those rules.
- The mutants were 0 of 49 equivalent. This agrees with the Lean oracle, which rejected every pilot mutant
  against the paper's proof.

### Phase 1, second measurement (2026-10-21): binder order and field arithmetic

Phase 2 showed a prover miss (F186, below): a real candidate that differed from its reference only in binder
order and in how a product with a quotient was written. Phase 1 was therefore extended, and re-measured on the
reference statements only. **No phase 2 candidate was used to tune or re-score anything.**

New rewrite rules, each refused when it cannot be applied safely:

- `implicit_binder`: `∀ (x : T)` to `∀ {x : T}`.
- `swap_binders`: swaps two adjacent binder groups when the second does not use the first.
- `swap_premises`: `A → B → C` to `B → A → C`.
- `mul_comm` and `add_comm`: swap two atomic operands when nothing binds tighter on either side.
- `div_mul`: `(A / B) * C` to `A * C / B`.
- `order_and_arithmetic`: every rule above that applies, in sequence, when at least two do.

Tactic changes, tuned on these rewrites:

1. **A bug fix.** `aesop` that makes progress without closing the goal only warns. `first` then stopped at that
   alternative and never tried the next one; Lean's linter reported them as "never executed". Each alternative
   now ends in `done`, so it fails unless it closes everything. This bug also kept `tauto` from ever running in
   the first measurement.
2. A new last alternative: introduce every binder and premise on both sides, rewrite `≥`/`>` as `≤`/`<`, then
   `apply` the other side and close its premises by `assumption`. If that fails, instantiate the other side with
   `convert h .. using 1` and close the remaining goals by `assumption` or `ring_nf`. `ring_nf` orders atoms
   differently under a binder than for a local variable, which is why `h` is instantiated first.

| Rule | n | Old tactic | New tactic |
|---|---|---|---|
| The five first rules (rename, `<`/`>`, swap ∧/∨, curry, ¬¬) | 44 | 44 | 44 |
| `implicit_binder` | 6 | 6 | 6 |
| `swap_binders` | 3 | 2 | 3 |
| `swap_premises` | 2 | 1 | 2 |
| `mul_comm` | 2 | 0 | 1 |
| `add_comm` | 1 | 0 | 1 |
| `div_mul` | 1 | 0 | 1 |
| `order_and_arithmetic` | 3 | 1 | 3 |
| **Prover recall** | 62 | **54 (0.87)** | **61 (0.98)** |
| Identity proved (must be 19) | 19 | 19 | 19 |
| Mutants proved equivalent (must be 0) | 49 | 0 | 0 |

The remaining miss is F238 `mul_comm` (`32 * C1` to `C1 * 32` inside a square root, in the longest statement of
the set), where the tactic runs out of budget. Tuning stopped there, after three iterations, to avoid fitting
these 62 rewrites. The same caveat as before applies: this recall is in-sample. The new rules were chosen because
of one phase 2 failure, but they were applied and measured only on the reference statements.

One run in between is not reported in the table. In it, Windows Application Control blocked a DLL, so Lean did
not run and produced no output. Every family failed its sentinel and was marked untrusted instead of scored.


- **Development set:** the 19 pilot families. Prompts may be changed freely here. Results are exploratory.
- **Models:** local models on the Legion. Model identity, decoding settings (temperature 0, seed 0) and prompt hash
  are recorded as in [FORMALIZER_BENCH_PROTOCOL.md](FORMALIZER_BENCH_PROTOCOL.md).
- **Headline set (no human screen):** every family that is not a wrapper (see below), 13 of 19. Results are not
  conditioned on any judgment of the prose. A scope note can summarize several results, and the challenge theorem
  can be a lemma the prose does not state; family 231 is an example. Such underdetermined prose can only make an
  original come out *not shown*. It cannot make an original *faithful*, nor make a family discriminating, since
  that needs the original *faithful*. Specificity and the discriminating-family count are therefore **lower
  bounds** on what the formalizer can do when the prose determines the statement.
- **Secondary stratum (mechanical):** `screen-auto` marks a family *numerically anchored* when every number in its
  statement (or wrapper definition), other than 0, 1 and 2, occurs in the prose. It was computed and committed
  before any model output existed ([`auto_screen.json`](lean_fidelity_screen/auto_screen.json)). Results are
  also reported for the anchored families, as a secondary analysis.
- Report: elaboration rate, then step 4a/4b/4c counts on originals and mutants.

**Go/no-go:** at least 30% of the headline originals come out *faithful*. Below that, the formalizer is the
bottleneck, and a test run would only measure its failures.

### Phase 2 preparation (2026-10-17; no model run yet)

**Screen: two human readers replaced (decided 2026-10-17, before any model run).** The first design had two
independent readers mark each family *determined* or *underdetermined*, and scored only the families both marked
determined. Two readers are not available, so that screen no longer gates anything. The headline above needs no
judgment, and reports lower bounds instead. Using one person, or a language model, as the readers was rejected:
one reader gives no agreement measure, and a model judge would bring in the errors this benchmark measures.
`screen-sheet` and `screen-score` remain, with their sheets
([`reader_A.md`](lean_fidelity_screen/reader_A.md), [`reader_B.md`](lean_fidelity_screen/reader_B.md)). If two
readers ever fill them in, blind to model outputs, their result is an extra secondary analysis: agreement,
Cohen's kappa, and the families both marked determined.

**Formalizer input.** `formalize` builds, for each family:

- *Context:* the challenge file without the target theorem, its docstring and its proof, with the line
  `-- [statement to formalize]` in their place. The target statement does not occur in any of the 19 contexts.
- *Prompt* `fidelity-formalize-v1` (SHA-256 `8121656dd978…`): the prose, the context, and the theorem's name.
  The name lets the model pick the right result when the prose describes several. It does not reveal the
  statement, and mutants keep the same name. The model must reply with one `theorem <name> … := by sorry`.
- *Raw outputs* go to a JSONL file (default `private/lean_fidelity/formalize_<model>.jsonl`): one meta line
  (model, endpoint host, prompt version and hash, openai/math commit, temperature 0, seed 0), then one line per
  family with the reply, the parsed statement, a status (`parsed`, `wrong_name`, `no_theorem`, `no_output`) and
  the prompt length. A transport failure is recorded; `--resume` redoes only those families.
- `--dry-run` writes the 19 prompts to `private/lean_fidelity/prompts/` without calling a model. They range from
  about 900 to 8,100 tokens (F331).

**Context length.** Ollama truncates prompts silently to its default context length, which is shorter than the
longest prompts. `formalize --backend ollama` therefore calls Ollama's native API with `num_ctx` (default 32,768)
on every request, and `--backend openai` (LM Studio) expects the model to be loaded with at least that context.
Both record the prompt tokens the model actually read (`prompt_tokens`), and set `context_full` when the prompt
filled the context. A row with `context_full: true` is treated as a failed call.

**Model identity.** Ollama tags are aliases: on this machine, `qwen2.5:latest`, `qwen2.5-coder:7b`,
`qwen3.5:latest` and three `claude-3-5-*` tags all point at the same model (digest `dae161e27b0e`, Qwen2.5 7.6B
Q4_K_M). The meta line therefore records the model digest, and results name the model by what it is, not by its
tag.

**Wrapper statements: excluded from the headline (decided 2026-10-17, before any model run).** In 6
families (115, 144, 174, 245, 275, 365), the conclusion is a single Prop-valued definition of the challenge file,
such as `MainStatement`. That definition stays in the context, so the model can restate its name without
formalizing anything, and the check would then test only the name. These families are **not part of the phase
2 headline**:

- `screen-auto` (and `screen-score`, if readers fill the sheets) lists them in `wrappers_reported_separately` and
  keeps them out of `headline`, which is the set scored for the go/no-go.
- `formalize` marks each output row with `wrapper: true/false`. The model is still run on them, and their
  results are reported in a separate table, with no claim drawn from them.
- Phase 2 therefore scores 13 families. The alternative, removing the definition from the context
  and comparing against its body, was not chosen. It would change the context and the mutants for these
  families, and it is left for phase 3 if 13 proves too few.

**Comparison step.** `compare --responses <formalize output>` writes, for each family, one check file with the
candidate against the original, the candidate against each mutant, and the sentinel, all with the frozen phase 1
tactic. A candidate that does not elaborate makes the family *abstain*. Every check runs with
`set_option autoImplicit false`. `lake env lean` does not apply the project's own setting, and without it an
unknown name in a candidate would become a bound variable and elaborate. Phase 1 was re-run with this header:
the results are unchanged (identity 19/19, mutants 0/49, recall 44/44).

### Phase 2 result (2026-10-17, Legion, Windows 11, RTX 5090 24 GB)

Three formalizers, all at temperature 0 and seed 0 with prompt `fidelity-formalize-v1`. Raw replies and Lean
results are in [`lean_fidelity_phase2/`](lean_fidelity_phase2/).

- **Qwen2.5 7.6B Instruct**, Q4_K_M, through Ollama's native API with `num_ctx` 32,768 (digest
  `dae161e27b0e`, tag `qwen2.5:latest`).
- **Qwen2.5-Coder 7B Instruct** through LM Studio, loaded with a context of 32,768
  (`qwen2.5.1-coder-7b-instruct`).
- **Qwen2.5-Coder 32B Instruct**, Q4_K_M (32.8B), through Ollama's native API with `num_ctx` 12,288 (digest
  `b92d6a0bd47e`, tag `qwen2.5-coder:32b`, 19.85 GB from the Ollama registry). It ran fully on the GPU (22 GB).
  The smaller context fits the longest prompt with room for the reply.

No prompt filled the context (largest: 7,705 tokens). All 38 replies of the 7B models contained a parseable
theorem; the 32B model gave 18 of 19, and in F238 it looped on one expression and never closed the theorem.

| Headline, 13 families | Qwen2.5 7B | Qwen2.5-Coder 7B | Qwen2.5-Coder 32B |
|---|---|---|---|
| Candidate elaborates | 6 | 6 | 7 |
| Original *faithful* | **0** | **0** | **1** (F103) |
| Mutants flagged (of mutants in elaborated families) | 21/21 | 18/18 | 22/22 |
| Discriminating families | 0 | 0 | 1 |
| Numerically anchored (12): faithful | 0 | 0 | 1 |

**Go/no-go: no-go for all three models.** At most 1 of 13 headline originals is faithful, against a threshold
of 30%. As planned, the formalizer is the bottleneck. The prover is not: phase 1 showed it proves the
equivalences that a correct formalizer would produce.

The 32B model's one faithful family is the shortest statement in the set (`L = RL ∧ RL = BPL`). Its closest
miss is F273: the candidate matches the original except that it drops the hypothesis `1 ≤ n` and writes
`η ∈ Set.Icc 0 1` as two inequalities, so it states a different theorem and is correctly flagged. In F190 it
drops `ε` and changes the bound.

Why the candidates fail (headline families):

- **Do not elaborate (7 of 13 for each model):** invented or misnamed identifiers (`log`, `N`,
  `InfiniteDimensional`, `Finset.nonempty`), syntax that is not Lean 4 (`L = RL = BPL`, `∀ c C > 0`), and
  type errors.
- **Elaborate but differ (6 of 13):** a missing hypothesis (F327 drops `[CompleteSpace X]`, so the claim is
  for normed spaces instead of Banach spaces), only part of a conjunction stated (F354), or a different result
  from the prose formalized (F231 states the countable-group result, while the target is the finite lemma; this
  is the underdetermined case described above).

Every mutant was flagged, but this says nothing yet: a candidate that is not equivalent to the original is
not equivalent to its mutants either.

**Wrappers, reported separately (no claim):** Qwen2.5 7B is *faithful* on 4 of 6, and Qwen2.5-Coder 7B and 32B
on 6 of 6. These are mostly the artifact that excluding them was meant to avoid: in 115, 275 and 365 both models restate
the definition's name (`theorem main_nonuniqueness : MainStatement`), and in 144 and 174 they copy the
definition's body from the context.

**Repair rounds (2026-10-18).** `repair` elaborates each candidate alone, in the same context the formalizer saw
(the target theorem is not in it), and feeds Lean's errors on that candidate back to the model, for up to two
rounds (`fidelity-repair-v1`, SHA-256 `428f3b2fb673…`). A reply with no theorem gets a request for one. Nothing
from the comparison with the original or the mutants reaches the model. Replies were capped at 2,048 tokens
(`num_predict`): a first attempt without the cap lost the Ollama server in round 2, when F243 ran for 660 s, so
it was discarded and repeated. In the repeated run there were no transport errors and no full contexts.

| Headline, 13 families | Qwen2.5-Coder 32B | + 2 repair rounds |
|---|---|---|
| Candidate elaborates | 7 | **10** |
| Original *faithful* (frozen tactic) | 1 | 1 |
| Mutants flagged (of mutants in elaborated families) | 22/22 | 33/33 |
| Discriminating families | 1 | 1 |

Repair turned 3 failing candidates into elaborating ones (F186, F238, F246); F243, F277 and F331 still fail after
two rounds. Repair works on names and syntax, which were about half of the failures, but does not by itself make
the statements faithful.

**Manual audit of the flagged repaired candidates.** The repaired F186 candidate is **equivalent** to the
original: it writes `(2^19 / (log n)^2) * log(1/(2ε))` as `2^19 * log(1/(2ε)) / (log n)^2`, writes `2 ≤ n` as
`n ≥ 2`, and orders the binders differently. A hand-written proof (`intro` in each order, `convert … using 1`,
`push_cast`, `ring`) elaborates with no errors; see
[`manual/F186_equivalence.lean`](lean_fidelity_phase2/manual/F186_equivalence.lean). The frozen phase 1 tactic
does not find it, so this *flagged* verdict is a **prover miss**, not a formalizer error. F246 differs for real:
it drops `[DiscreteTopology G]` and adds a topology instance on the boundary. The headline above keeps the
pre-specified rule (1 of 13). With the manual audit, the faithful count is at least 2 of 13, still below 30%.

This is the first evidence that the phase 1 recall of 1.00 does not carry over to real candidates. Binder
reordering and field arithmetic were not among the phase 1 rewrite rules. Both were then added and recall was
measured again in phase 1, never on these candidates (see "Phase 1, second measurement" above: 61 of 62). The
phase 2 candidates have not been re-scored with the new tactic.

**What this means.** The pipeline works end to end and measures what it should, but with general local models
up to 32B there is no fidelity signal to evaluate: going from 7B to 32B moved the headline from 0 to 1 of 13,
and two repair rounds made more candidates elaborate without making more of them faithful.
Moving to phase 3 with these models would only measure their failures. Remaining options, to be decided before
more runs:

- a model trained for Lean 4 autoformalization;
- prompt iterations on this development set, which phase 2 allows (the repair rounds above were the first);
- a stronger comparison step, measured in phase 1 (binder reordering and field arithmetic, see the F186 miss);
- a different auditor output: report *which direction* fails (candidate implies original, or the reverse), so
  that a near miss such as F273 shows up as "stronger" or "weaker" rather than only "not shown".

Any new model or prompt is run on the same 19 families and reported next to these results.

### Phase 3. Pre-registration and test run

1. Freeze the protocol: model tag, prompt hash, tactic script, heartbeat and wall-time limits, the prose screen
   rules, mutation operators (as fixed after the pilot), and the metrics below. Record its SHA-256.
2. Draw a fresh **test set** from the families not used in the pilot, with a new seed fixed in the protocol.
   The size is set from the phase 2 rates, so that ≥ 15 determined families remain per mutation type where
   possible.
3. Run the screen, the mutants, the Lean oracle on the mutants (to drop label noise), then the auditor.
   Report all outcomes, including abstentions and timeouts.

## 4. Metrics (for the phase 3 protocol)

All with 95% Wilson intervals and family-level bootstrap, as in the pilot:

- **Coverage:** fraction of determined families whose `S_p` elaborates.
- **Specificity:** originals judged *faithful*, among those that elaborated.
- **Sensitivity:** mutants *flagged*, by mutation type, among those that elaborated.
- **Discriminating families:** families where the original is *faithful* and every mutant is *flagged*.
  This is the headline figure. Flagging everything already gives sensitivity 1, so sensitivity alone
  says little.
- **Comparison with S1:** the pilot auditor on the same test set.

## 5. Risks

- **Autoformalizing research mathematics is hard.** The custom definitions in the context help, but a 14B
  local model may rarely produce an equivalent statement. Phase 2 measures this before any claim is made.
- **Equivalent but not shown.** Proving `↔` may require unfolding definitions or real mathematics. Phase 1
  measures this ceiling separately.
- **Leakage.** Docstrings, comments or lemma names in the context can give away `S_ref`. The target and its
  docstring are removed. Remaining comments are kept, but each context file is listed in the outputs so that
  leakage can be audited.
- **Statement extraction.** The statement ends at the first `:=` outside brackets. A `let x := ...` without
  brackets inside the type would still cut it. Phase 0 checks that every extracted statement is balanced and
  occurs exactly once in its file.

## 6. Code to write

One script, `scripts/benchmarks/openai_math_lean_fidelity.py`, with subcommands that follow the phases:
`env-check`, `controls` (phase 1), `formalize` (raw model outputs, stored as in the formalizer benchmark),
`compare` (Lean, resumable), and `report` (offline, deterministic). The context building, rewrite rules and
Lean file generation are covered by unit tests that do not need Lean, like the pilot's mutation tests.

## 7. Place in CoResearcher

This auditor is meant to replace a gate that already exists, not to stand alone. These are the modules it
touches (levels from [MODULE_MATURITY.md](../MODULE_MATURITY.md)):

| Module | Level | Relation |
|---|---|---|
| `semantic_bijectivity_auditor` (ADR-DISCOVERY-048) | Tested | The gate this auditor would replace. [Claim 19](../CLAIMS_REGISTER.md) is NOT SUPPORTED after the pilot. |
| `frontier_math_flywheel` (ADR-DISCOVERY-055) | Integrated, API | Uses the bijectivity gate to mark a task `ADMISSIBLE_SOUND` ("bijectively aligned"). That verdict currently rests on an unsupported claim. |
| `result_family_orchestrator` (ADR-DISCOVERY-043) | Tested | Runs the same bijectivity gate on each node of a result family. |
| `lean_formalization_engine` (ADR-DISCOVERY-047) | Tested | Audits Lean source; the flywheel and the orchestrator call it before the bijectivity gate. |
| `formalizer` (ADR-DISCOVERY-061) | Integrated, API | The same OpenAI-compatible client pattern; this auditor adds a native Ollama client with a per-call context and prompt-token check. |
| `formalization_gate` (ADR-DISCOVERY-064) | Integrated, API | Self-consistency over N samples, compared exactly by z3. The phase 1 equivalence check is the Lean counterpart: two Lean candidates agree when Lean proves them equivalent. |
| `formal_lean` (ADR-DISCOVERY-060) | Integrated, API | Exports z3-checked consequences to Lean; it shares the Lean toolchain set up in phase 0. |
| `research_lifecycle` (ADR-DISCOVERY-063) | Integrated, API | Stage gates. A formal statement entering the PROTOCOL stage could be required to pass this fidelity check. |

Integration rules, in order:

1. Nothing is wired in until phase 3 supports a claim. A gate that cannot discriminate (phase 2: 0 of 13
   faithful with 7B formalizers) must not label statements as aligned.
2. Until then, the existing `ADMISSIBLE_SOUND` verdicts from the bijectivity gate should be described as
   unsupported wherever they surface (API responses, reports). That change belongs to its own task.
3. When the auditor is wired in, it reports three outcomes, not two: *faithful*, *flagged* (not shown
   equivalent) and *abstain* (no candidate elaborated). An abstention is never reported as alignment.
