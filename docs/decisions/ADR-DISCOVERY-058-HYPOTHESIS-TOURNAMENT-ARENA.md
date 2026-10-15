# ADR-DISCOVERY-058: Hypothesis Tournament Arena & Multi-Agent Elo Ranking

## Status
Accepted

## Context
In 2026, Google DeepMind, Google Research, and Google Labs published **Co-Scientist** in *Nature* ("A multi-agent AI partner to accelerate research"), establishing an "Idea Tournament" paradigm inspired by AlphaGo and AlphaStar. Their empirical validation in laboratories across Stanford (liver fibrosis), MIT (ALS), and Cambridge demonstrated that comparing scientific hypotheses pairwise in structured tournaments is vastly more reliable and discriminative than asking LLMs for arbitrary scalar scores (1-10), which suffer from hallucinated rating drift and consensus bias.

However, while Co-Scientist operates on commercial cloud models, our institutional ecosystem requires:
1. Sovereign, on-premise execution (Zero-Cloud ADR-030).
2. Non-generative physical and formal evaluation axes (conservation laws, Lean 4, thermodynamic consistency).
3. Immutable Merkle auditability in `ScientificLedger`.

## Decision
We implement `HypothesisEloTournamentOrchestrator` and `PairwiseDebateEngine` (`python/discovery/hypothesis_tournament_arena.py`):

1. **Multi-Agent Pairwise Debate Match (`PairwiseDebateEngine`)**:
   - Hypotheses $H_A$ and $H_B$ are compared pairwise along 4 non-generative epistemic axes:
     - `EVIDENCE_GROUNDING` (30% weight): Depth of biological linkage to UniProt, ChEMBL, and literature networks.
     - `PHYSICAL_CONSISTENCY` (30% weight): Compliance with conservation laws and absence of holonomy defects.
     - `STATE_SPACE_REDUCTION` (25% weight): Volume $\Delta\Omega$ of unviable parameter space eliminated.
     - `FALSIFIABILITY_PARSIMONY` (15% weight): Popperian empirical testability and Occam parsimony penalty.
2. **Dynamic Elo Rating System**:
   - Uses standard logistic expectation curves:
     $$E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}$$
   - Updates ratings iteratively with adaptive K-factors ($K=32.0$), maintaining accurate win/loss/draw records.
3. **Tournament Scheduling & Cryptographic Sealing**:
   - Orchestrates round-robin and top-K ladders.
   - Sells the resulting leaderboard and matches into `ScientificLedger` with SHA-256 seal `tournament_hash`.
4. **REST API Integration (`api/routers/discovery.py`)**:
   - Exposes `POST /api/discovery/tournament/debate-match`
   - Exposes `POST /api/discovery/tournament/run-tournament`

## Consequences
- **Positive**: Displaces narrative bias with formal comparative ranking; ensures the top hypotheses promoted to wet-lab protocols or Medicalia clinical guidelines have survived exhaustive adversarial debate.
- **Sovereignty**: Runs 100% locally on local hardware without cloud dependence.

## Review (2026-10-15)

This ADR was added in a separate session. A review of the code found these gaps between the text above and the
implementation. The ADR text is kept unchanged as the original record.

- **The axis scores are inputs, not evaluations.** `evidence_score`, `physical_consistency_score`,
  `delta_omega_potential` and `falsifiability_score` are supplied by the caller. Nothing in the arena consults
  UniProt or ChEMBL, conservation laws, holonomy or Omega.
- **A "debate" is a weighted difference of those four numbers** (weights 0.30/0.30/0.25/0.15, draw margin 0.05,
  both hand-set and unvalidated). There is no multi-agent or adversarial exchange.
- **Elo adds no information.** Because each match is decided by the fixed scores, the ranking is determined by the
  weighted score itself; the Elo update only adds dependence on match order. This reproduces the scalar-scoring
  problem the Context section cites as the motivation.
- **Not implemented:** top-K ladders and adaptive K-factors (K is a constant).
- **Scope.** The evidence-grounding axis grades sources and evidence, which the owner has placed outside
  CoResearcher's formal scope.
- **Fixed in review:** both endpoints now require the API key, and inputs are bounded (scores in [0, 1], at most
  50 candidates and 10 rounds), since the cost grows with rounds x candidates² and the endpoints were unauthenticated.

A formal alternative is `HypothesisEvaluator.compare` (ADR-DISCOVERY-059), which decides the logical relation between
two hypotheses (equivalent, stronger, weaker, incomparable or contradictory) from their content rather than from
supplied scores.
