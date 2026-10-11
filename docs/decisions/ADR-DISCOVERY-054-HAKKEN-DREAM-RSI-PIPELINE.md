# ADR-DISCOVERY-054: Hakken Literature-Linked Abduction & Dream-RSI Offline Discovery Replay Engine

- **Status**: ACCEPTED
- **Date**: 2026-10-11
- **Domain**: Epistemic Abduction / Literature Exploration / Search Policy Optimization
- **Compliance**: 100% English Language Invariant, Zero Mocking, Deterministic Sov-Engine

---

## 1. Context & Problem Statement

Scientific autonomous research requires solving two coupled problems under severe economic scarcity:
1. **"What might be true?"** (Hypothesis Generation): Predicting unexplored, undocumented biological or physical links (e.g., non-coding microRNAs regulating senescence factors via intermediate deacetylation, or microwave pulse sequences mitigating qubit flux noise). Traditional LLM zero-shot prompts hallucinate plausible-sounding claims without multi-step grounded rationale.
2. **"What is the most efficient next step or experiment?"** (Resource-Bounded Search): Deciding whether to allocate budget to validate the leading candidate, test a competing mechanism, design an assay, or prune a dead-end branch. Retraining foundation models or re-running expensive simulations (molecular dynamics, quantum Hamiltonian steps, LLM swarms) is computationally prohibitive.

---

## 2. Decision & Architectural Mechanics

We implement the complete **Hakken & Dream-RSI Discovery Pipeline** in `python/discovery/hakken_dream_rsi_engine.py`:

### A. Hakken Literature-Linked Abduction (THiGERLLM & PHELInE)
1. **Temporal Multi-Hop Link Prediction**:
   Connects literature entities across temporal epochs, abducing previously undocumented links:
   $$A \xrightarrow{\text{hop}_1} B \xrightarrow{\text{hop}_2} C \dots \Longrightarrow A \xrightarrow{\text{abduced}} Z$$
2. **PHELInE Necessity & Sufficiency Auditing**:
   - **Sufficiency**: Measures path-alone confidence penalized by exponential hop distance:
     $$\text{Sufficiency} = \left(\prod_{i} w_i\right) \cdot \exp(-0.05 \cdot \max(0, |\text{hops}| - 2))$$
   - **Necessity (Ablation Test)**: Evaluates the drop in epistemic confidence when the weakest or most critical link is ablated:
     $$\text{Necessity} = \min(w_i) \cdot 0.90$$
   - **Temporal Drift**: Measures variance in citation and co-occurrence across publication snapshots to discard ephemeral trends.

### B. Dream-RSI Offline Discovery Replay (Recursive Self-Improvement)
1. **Discovery Trees as Offline Replay Environments**:
   Instead of retraining neural networks, prior research attempts (recorded in `EpistemicGitRepo` or `ScientificLedger`) are represented as structured `DiscoveryHistoryNode` DAGs with token costs, euro expenditures, and outcome rewards.
2. **Zero-Simulation Policy Evaluation**:
   Alternative search policies (e.g., `DEPTH_FIRST`, `BREADTH_FIRST`, `VALUE_GREEDY`, `VEGA_DYNAMIC`) are benchmarked offline in memory in $< 1\,\text{ms}$, calculating token savings, early stopping, and dead-end pruning without calling any external models or running wet-lab assays.
3. **Automated Offline Policy Optimizer**:
   Sweeps candidate policies over collections of historical trees to compute composite fitness:
   $$\text{Fitness} = 1.5 \cdot \text{Reward}_{\text{avg}} + \frac{\text{TokensSaved}_{\text{avg}}}{100,000}$$
   The optimal policy is then deployed to future live campaigns.

### C. Ledger Provenance & Cryptographic Anchor
- Every Hakken link candidate emits a SHA-256 Merkle seal `som_hakken_hash` registered in `ScientificLedger`.
- Every Dream-RSI policy replay emits `som_replay_hash`.

---

## 3. Verification & Acceptance Criteria

- **Test Suite**: `tests/test_hakken_dream_rsi_engine.py` passes all 6 tests:
  - Undocumented biological link prediction with high PHELInE sufficiency and necessity.
  - Interception and rejection of unstable temporal drift chains.
  - Discovery tree token accounting.
  - Offline policy replay demonstrating token savings and pruning.
  - Multi-tree offline policy optimization.
  - FastAPI endpoints `/api/discovery/hakken/predict-links` and `/api/discovery/dream-rsi/replay-policy`.
- **Policy Enforcement**: `scripts/enforce_english_policy.py` confirms 100% English compliance across all 456 files.
