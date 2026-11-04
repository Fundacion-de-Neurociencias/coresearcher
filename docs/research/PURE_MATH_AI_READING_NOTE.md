# Reading note: Wolfram, "What's the Future for Pure Math Research in the Age of AI?"

**Status:** reading note. Written on 2026-11-02 from the author's essay of 2026-09-28
(writings.stephenwolfram.com/2026/09/whats-the-future-for-pure-math-research-in-the-age-of-ai). It is an opinion piece
with no data, so its claims are read as positions to weigh, not as results.

## What the essay argues

- **Questions define good mathematics.** Mathematics is judged by the questions it asks; AI can automate the steps
  but the choice of questions stays human.
- **Formalization is the weak link.** A proof assistant can check a proof, but whether the formal statement captures
  what the author meant is the open question. The author reports formalizations that were "proofs" of an easier
  statement.
- **Check results by computing them.** If an AI proposes a solution or a counterexample, one can verify it by a
  computation that does not depend on the AI.
- **Statistical plausibility is not correctness.** Much generated mathematics has the texture of a paper and a low
  chance of being correct.
- **Computational irreducibility** leaves pockets of reducibility where shortcuts exist, and the search space above
  them can only be explored by running the steps.

## What it means for CoResearcher

1. **The formalization gap is the central risk, and we have measured it.** The Lean/Comparator oracle confirms that
   a mutated statement is not provable with the paper's own proof, but it compares the challenge statement with the
   statement the solution proves, not with the prose. This is recorded in
   [section 5b of the oracle protocol](../reference/benchmarks/LEAN_ORACLE_PROTOCOL.md#5b-linux-runs). The Lean-based fidelity
   auditor in section 6 of the same protocol is the proposed answer. It was built and run in phase 2
   ([plan](../reference/benchmarks/LEAN_FIDELITY_AUDITOR_PLAN.md)): its prover works on correct pairs, but local
   formalizers made at most 1 of 13 headline originals faithful, so it is a no-go for now.
2. **Only computed confirmations count.** The counterexample benchmark applies the essay's rule: a proposer (a language
   model) suggests states, and only the exact evaluator's confirmation counts. The proposer's own judgement never does
   ([protocol section 2](../reference/benchmarks/COUNTEREXAMPLE_SEARCH_PROTOCOL.md)).
3. **Plausible text is not evidence.** Our claims register lists negative and mixed results beside positive ones
   (for example the openai/math fidelity auditor at chance, AUROC 0.524). That is the practical answer to the
   "statistical texture" problem.
4. **Search where enumeration fails.** The counterexample corpus sits above the exhaustive threshold (10⁷ states), so
   a search is the only tool there. This is the regime the essay describes, and the benchmark tests it directly.
5. **Shared concepts need a shared record.** An idea only helps if others can check it. Protocols, frozen datasets and
   hashes are the record that lets someone else reproduce a result.

## What not to copy

- **Taste as a criterion.** The essay leans on aesthetic judgement for what is "interesting". CoResearcher's gates do
  not accept an unmeasured criterion, so this stays out of the protocols.
- **Advocacy.** The author works on his own language and tools, and the essay argues for them. Use the arguments, not
  the product claims.
