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

### Phase 2. Formalizer on the development set

- **Development set:** the 19 pilot families. Prompts may be changed freely here. Results are exploratory.
- **Model:** one local model on the Legion. The tag, decoding settings (temperature 0, seed 0) and prompt hash
  are recorded as in [FORMALIZER_BENCH_PROTOCOL.md](FORMALIZER_BENCH_PROTOCOL.md).
- **Prose screen:** a scope note often summarizes several results, and the challenge theorem can be a lemma that
  the prose does not state. Family 231 is an example: the prose is about uniform spanning forests, while the
  theorem bounds the tilt covariance of a strongly Rayleigh measure. Before any model run, two readers who do
  not see model outputs mark each family as *determined* if `P` fixes the meaning of `S_ref`, and as
  *underdetermined* otherwise. Only determined families are scored. The number excluded is reported.
- Report: elaboration rate, then step 4a/4b/4c counts on originals and mutants.

**Go/no-go:** at least 30% of determined originals come out *faithful*. Below that, the formalizer is the
bottleneck, and a test run would only measure its failures.

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
