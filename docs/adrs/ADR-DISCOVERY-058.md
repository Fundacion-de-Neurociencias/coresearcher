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
