# ADR-DISCOVERY-002: Strict Separation Generator ≠ Verifier (Solver / Verifier)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Governed Execution  
**Domain**: Multi-Agent Scientific Rigor

---

## 1. Context

One of the deadliest epistemic biases in automated scientific reasoning is **self-contained confirmation bias**:
```
Agent Generates Hypotheses → Same Agent Searches for Evidence → Same Agent Validates and Concludes Success
```
When the hypothesis generator evaluates his own creation, he systematically tends to select complacent evidence, ignore counterexamples, relax the rigor of the tests, and overestimate the significance of his findings.

---

## 2. Architectural Decision

1. **Mandatory Separation of Roles**:
   - It is prohibited for the agent who formulates a hypothesis to be the same one who evaluates its validity or exclusively designs its falsification tests.
   - The architecture is formally bifurcated into two classes of decoupled and independent agents:
     * **Discovery Agent (Proposer / Solver)**: Formulates hypotheses, proposes mechanisms, designs thought experiments and identifies analogies between domains.
     * **Scientific Auditor Agent (Verifier / Falsifier)**: Actively attempts to demolish the hypothesis, formulates counter-evidence, searches for negative control data, evaluates boundary conditions and audits violations of biological or physical constraints.

2. **Functional Incompatibility at Runtime**:
   - Every research pipeline must include an asynchronous *handoff* with a blind or adversarial protocol towards the Scientific Auditor.
   - No hypothesis can be graduated to a higher confidence level without an independent falsification audit signed by an Auditor Agent.

---

## 3. Consequences

### Positive
- Eradication of self-validation bias.
- Early detection of fragile or over-adjusted hypotheses to previous literature.
- Increase in scientific reproducibility and resistance to external evaluations.

### Negatives / Trade-offs
- Intentional duplication of calls to models and agents, increasing the cost of inference.
- Greater latency in the consolidation of epistemic trajectories.