# Case: the problem-solving strategy visible in the openai/math release

**Date:** 2026-10-28. **Status:** case study by the CoResearcher maintainers.
**Scope:** what the released texts show about *how* the results were produced, and what follows for checking such
results. The case does not judge whether any result is correct, and it makes no claim about credit, novelty or the
announcements.

**Module:** [`openai_math_strategy.py`](../../../python/discovery/openai_math_strategy.py). It contains the parsing,
the citation graph, and the coded reading of the ten reasoning summaries.

**Data:** [`corpus_stats.json`](../../../examples/openai-math-strategy/corpus_stats.json). Regenerate it with
`python scripts/cases/openai_math_corpus.py --cache <empty dir> --traces <pdftotext dir>`. The script downloads about
520 files and takes about 1 minute.

**Tests:** [`tests/test_openai_math_strategy.py`](../../../tests/test_openai_math_strategy.py) run offline.

Every claim below carries one of four tags:

- **[stated]**: a released text says it. The text is named.
- **[measured]**: computed from the corpus by the script above.
- **[coded]**: our reading of a reasoning summary. Four readers read the summaries in parallel, and the claims that
  carry the most weight were spot-checked against the text.
- **[inferred]**: our interpretation.

OpenAI describes the model as "unreleased" and "internal". Nothing here is a statement about its architecture or
training.

## 1. Sources

Everything is pinned to commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` of
[github.com/openai/math](https://github.com/openai/math), the same commit as ADR-070.

| Source | What it gives |
|---|---|
| `README.md`, `history.md` | The production process and the release history (fixes, withdrawals) |
| `overview.tex` (SHA-256 `39de58f1…`) | 373 families, 721 manuscripts and 17 disciplines, parsed with `parse_overview` |
| `preprints/*/…/*.bib` (514 directories have one) | Self-citations between manuscripts (`OAI:` keys) |
| `lean/formalization.yaml` (`b8e7072a…`) | Which papers have a formalized main result |
| `reasoning_traces/*.pdf` (10 summaries) | The only direct evidence of the search process |

## 2. The production process as stated

These points are **[stated]** in the README and in history.md:

- The model was posed about 4,000 problems.
- Each result used about three hours of ChatGPT Pro thinking compute on average.
- The output was aggregated into families and manuscripts. Only results meeting "an appropriate level of
  significance" were kept.
- Some outputs build on earlier results.
- About 42% of top-line results are formalized in Lean.
- 14 manuscripts were revised and 3 were withdrawn. The withdrawals followed a sign error in a
  "stabilization-trace cancellation".
- Two of the releases (October 6 and the October 26 additions) are direct model output.

Read together, these describe a **generate, then filter** pipeline. About 4,000 attempts produced 721 manuscripts.
That does not mean about 18% of attempts succeeded, because several manuscripts can come from one problem and one
attempt can feed several manuscripts.

## 3. What the corpus structure shows [measured]

| Quantity | Value |
|---|---|
| Families and manuscripts | 373 and 721. There are 751 preprint directories, the extra ones being earlier versions and withdrawn papers |
| Release dates | Most manuscripts are dated between 2026-09-22 and 2026-10-07. The largest days are Sep 24 (188), Sep 23 (171) and Oct 5 (108) |
| Family sizes | 205 families have one manuscript, 97 have two, 36 have three, and so on up to 14. In total 168 families have more than one manuscript |
| First word of the family description | "Proves" 166, "Constructs" 43, "Resolves" 40, "Disproves" 18 |
| Self-citations | 281 papers cite other OAI papers, with 436 edges in total. 288 of the 436 (66%) stay inside one family |
| Cross-family links | 93 family pairs, of which 15 cross disciplines |
| Direction of citation | 247 to a paper of the same day, 145 to an earlier paper, 44 to a later one |
| Mutual citation | 53 groups of papers that cite each other, of sizes 2 to 5. 39 of them lie within one family |
| Longest citation chain | 6 papers |
| Formalization | 176 papers in 138 of the 373 families (37%) have a formalized result. Among "Disproves"/"Constructs" families the share is 33 of 61 (54%). By discipline it ranges from 5/6 (logic) and 23/41 (TCS) down to 1/18 (topology) |

What this suggests **[inferred]**:

1. **Results are decomposed into companion papers.** Two thirds of the citations stay inside a family, and many are
   mutual. A hard target is split into a lattice of intermediate results, which are drafted and revised together and
   then catalogued as one family. The largest example is the Kähler minimal-model / abundance cluster. Its largest
   connected citation component has 37 papers, and family 034 alone has 14 manuscripts.
2. **The model builds on its own outputs, inside a short window.** 145 of the citations point backward in time. Two
   reasoning summaries show this in the prompt itself. In family 159, Part II says "Use the previous bounds you have
   done" **[stated]**. In family 017, the summary returns to OpenAI's own Catalan-irrationality paper 36 times
   **[measured]**. Cross-discipline reuse is rare: 15 of the 93 family pairs.
3. **Results that can be checked mechanically are formalized first.** Disproofs and constructions are formalized at
   a higher rate than the corpus as a whole (54% against 37%), and so are TCS and combinatorics. Topology and PDE
   lag. The formal layer therefore covers least the results whose difficulty is analytic.
4. **Computation leaves artifacts, but outside the summaries.** 29 preprint directories ship code: Python, C++, or
   certificates (lattice optimality, mutually unbiased bases, matrix multiplication). None of the ten summaries
   describes a numerical experiment **[coded]**, and one prompt (family 221) discourages computer-assisted proofs
   **[stated]**.

## 4. What the ten reasoning summaries show

The summaries are third-person condensations, interleaved with short "VERBATIM EXCERPT" snippets of raw reasoning.
Their lengths differ by a factor of about 15: from 3 sections to 49, and from 1 excerpt to 69 **[measured]**.

### 4.1 Coding table [coded]

| Family | Prompt form | Abandoned routes (approx.) | Pivot | Audit share | Endgame (summarizer) |
|---|---|---|---|---|---|
| 007 two-point Chowla | conjecture / "Prove that" | ~10 | adapt one model paper (Pilatte) | ~0.2 | conditional on named lemmas |
| 017 μ(π) = 2 | goal-driven | ~35 families, 150+ abandon events | interpolation determinant + ampleness | ~0.27 | claimed; vanishing-theorem hypotheses unchecked; a "too strong" warning noted |
| 087 Mahler | yes/no, "prove or disprove" | ~60 | complexified slabs + complex-Hessian positivity + flux (I); Gaussian Riccati profiles (III) | ~0.2 | I complete; III conditional on scalar inequalities |
| 102 BasicSDP / UGC | "prove or refute", refutation criteria fixed | ~30 | nonlinear-vs-linear decoder gadget | ~0.5 | proposed; uniformity "provisionally" accepted |
| 159 Erdős APs | "prove or disprove"; II builds on I | ~30 | negative cross-kernel turns a deficit into an excess | ~0.28 | proposed; a circularity concern left open |
| 197 Kaplansky | "proof or rigorous counterexample", with references and milestones | ~40 | affine-line hypergraph / code construction over F₂ | ~0.45 | counterexample claimed; Linnik and local-lemma dependencies open |
| 221 Mézard–Parisi | "complete rigorous solution", computer discouraged | ~7 | shift of branching depth; squared-difference positivity | ~0.33 | full proof claimed |
| 271 Heisenberg | "prove or refute" | ~12 | determinant / exterior-power stability | ~0.67 | claimed; uniform estimates "claimed" |
| 287 free group factors | "determine whether … and prove" | ~35 | flip to the constructive side via an ergodic-theory analogy; ODE flow | ~0.1 | isomorphism claimed, conditional on flow steps |
| 362 Vlasov–Maxwell | "determine whether … true" | ~6 | signed integration by parts before absolute values | ~0.8 | asserted; key estimates "not established" by the cited theorem |

Aggregates **[coded]**:

- 7 of 10 prompts are decision-form: prove or disprove, determine whether, or resolve.
- 7 of 10 pivots are a **positivity or sign trick**.
- 5 of 10 pivots import a structure from another field.
- The median number of abandoned routes is 30 (range 6–60).
- The median audit share is 0.33.

### 4.2 The common search loop [coded → inferred]

All ten summaries follow the same eight-phase loop, `PHASES` in the module. The amount of time spent in each phase
varies a lot.

1. **The problem is posed as a decision with its conventions fixed [stated in the prompts].** The prompts define
   every object, close loopholes, and say what counts as a refutation. Some forbid "silent restriction to special
   classes" or the failure of one method as a refutation. Some supply references and milestones (family 197). Some
   follow up on the model's own earlier answer (family 159). The model is not asked to *find* problems; it is handed
   precise yes/no targets.
2. **The literature gap is mapped first.** The model names the best known result and the exact estimate that is
   missing. It then reduces the problem to a known criterion:
   - the continuation criterion (362);
   - Flint–Hills ⇔ μ < 5/2 (017);
   - "this implies UGC" (102);
   - the interpolation upper bound (221).
3. **Falsification sweep.** It probes for counterexamples at the boundaries of the hypotheses, as in families 221 and
   159. It runs "proves too much" tests (Liouville numbers in 017; "would be stronger than Mahler" in 087) and tests on
   extremal cases (simplex, orthant, ball, cones in 087). It builds cheating provers against its own tests (102).
4. **Breadth-first route search with named, quantitative kill criteria.** Routes are dropped for specific reasons:
   - a constant is lost;
   - losses compound;
   - an arithmetic cost exceeds an analytic saving;
   - the argument is circular;
   - the route "is just the original problem again".

   The same few meta-obstructions get names and come back: the "volume obstruction" (017), "rare holes" (159),
   "rough generator changes" (287), "the prover adapts to the projection" (102).
5. **Pivot on a structural trick**, often marked in the raw excerpts by "This is big", "Aha!" or "This could
   solve!". Seven of the ten pivots turn a sign-indefinite quantity into a positive one, or cancel it before taking
   absolute values. The signature from the local smoothing anatomy (lift, then positivity, then flux) is one instance
   of this.
6. **Build the architecture.** The model fixes the order of parameters ("choose m before b"), then a budget, then
   explicit constants (62/25 in 017; penalty 1.94 against allowance 1.8 in 087).
7. **Self-audit by re-derivation.** This takes 10–80% of the sections. The audits check normalization, dependency
   order, circularity and scope ("does it prove too much?"). They find and patch real local bugs, for example a
   counting error in 197, a normalization in 362, and a missing factor in 017. **They never overturn the main route.**
   In 017 the model noticed that its method seemed too strong and kept the result anyway.
8. **Claim with named open obligations.** Every summary ends by asserting a resolution or a candidate resolution, and
   every summarizer hedges ("proposed", "claimed", "depends on"). None of the ten reports an external check.

### 4.3 A mismatch worth recording [measured + coded]

For all ten traced families the catalogue description begins "Proves", "Resolves" or "Constructs". The summaries,
however, mostly end conditionally (§4.1). Only 4 of the 10 traced families have a formalized paper: 087, 102, 197
and 362.

The summary describes one run, and the published manuscript may come from further runs, so this is not evidence of
an error. It does mean that the released summaries do not themselves certify the catalogued claims. For those
families, a check must come from outside the summaries.

## 5. The strategy, stated compactly [inferred]

1. **Scale and selection.** Pose thousands of precisely stated decision problems. Spend a fixed budget on each. Keep
   only the significant outputs.
2. **A literature-anchored, breadth-first search.** Every route is killed fast by a quantitative or extremal-case
   test. The obstructions are named and reused.
3. **A strong prior on positivity and sign.** When stuck, look for the step that turns an indefinite quantity into a
   positive one: a lift, a cancellation before absolute values, or a squared difference. A second prior is to import
   a structure from another field.
4. **Composition over time.** Decompose a hard target into companion papers and build on the model's own earlier
   results within days. Revise companions together, which leaves mutual citations.
5. **Self-consistency audits instead of adversarial checks.** The model audits itself heavily but by re-derivation.
   That catches local errors and misses global ones; the withdrawn manuscripts failed on a sign in a cancellation.
6. **External verification afterwards, and partial.** Lean formalization covers 37% of families by our count (the
   README gives about 42% of top-line results). It favours constructions and disproofs.

## 6. Implications for the Fundación and for CoResearcher [inferred]

- **What is replicable.** The protocol is replicable:
  - precise decision prompts with fixed conventions and refutation criteria;
  - a falsification sweep before any construction;
  - kill criteria stated as numbers;
  - an explicit hunt for a positivity or sign pivot;
  - building on earlier outputs.

  None of these needs the model itself. They are a discipline we can impose on any prover, human or AI.
- **Where OpenAI's loop is weakest is where CoResearcher sits.** The model's audits are self-consistency
  re-derivations, and its final claims carry named open obligations. CoResearcher's scope, the formal and
  mathematical soundness of hypotheses, matches that gap exactly. The useful product is an **independent check of the
  named obligations** and of statement fidelity, as in ADR-070. A second re-derivation by the same kind of reasoner
  adds little.
- **The concrete next step is the obligation lists.** For the ten traced families, extract the open obligations each
  summary names. Then match each one to the published manuscript and to the Lean coverage. That gives a checkable
  list of where each claim actually rests.

## 7. Limits

- Ten summaries across 373 families is a small sample, and OpenAI chose which families to summarize. The summaries
  are condensations, not raw transcripts. Counts of abandoned routes and audit shares are approximate codings.
- PDF text extraction loses most inline mathematics (U+FFFD). The coding relies on the prose, which is intact.
- The citation graph covers only the 514 preprint directories that have a `.bib` file. Papers that cite through
  inline `\bibitem` lists are missed, so all citation counts are lower bounds.
- "Formalized" means listed in `formalization.yaml`. Our count (138 of 373 families) is not the same quantity as the
  README's "~42% of top-line results".
