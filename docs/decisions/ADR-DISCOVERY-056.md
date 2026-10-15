# ADR-DISCOVERY-056: Socratic Question & Epistemic Inquiry Auditor

## Status
Accepted

## Context
Scientific AI systems frequently focus exclusively on the "answer generation" paradigm. By ingesting prompts and outputting speculative prose, conventional LLM systems inadvertently incentivize confirmation bias, hallucinations, and premature convergence upon narrative consensus.
The EpistemAI / BioBrains initiative (co-founded with Carlos Blanco Velázquez at FIB Hospital Clínico San Carlos & Universidad Complutense de Madrid) emphasized the fundamental counter-thesis:
> *"AI should not serve to generate more answers, but to ask better questions, challenge hypotheses, explore counterfactual scenarios, and expand human thinking capacity."*

While aligned with CoResearcher's `QUESTION_CONSTITUTION.md` and State-Space reduction principle ($\Omega$), this philosophical imperative required an auditable, automated, and mathematically grounded implementation that stress-tests inquiries before hypotheses are generated or resources allocated.

## Decision
We implement `SocraticQuestionAuditor` (`python/discovery/socratic_question_auditor.py`) to systematically audit, score, and refine scientific inquiries:

1. **Constitutional Compliance Gate**:
   - Audits proposed inquiries against `QUESTION_CONSTITUTION.md` Articles I–IV.
   - Enforces canonical ID scheme (`QUESTION-XXXXXX`), mandatory hierarchical ontology paths (`Science/Medicine/...`), and granularity classification (`MACRO`, `MESO`, `MICRO`).

2. **Dialectical Bias & Premise-Smuggling Detection**:
   - Identifies confirmation bias (e.g., questions presupposing proof or superiority a priori).
   - Extracts smuggled premises embedded as deceptive antecedents ("Given that X...", "Because Y...").
   - Categorizes bias into `OBJECTIVE`, `CONFIRMATION_BIASED`, `PREMISE_SMUGGLING`, `TELEOLOGICAL`, `FALSE_DICHOTOMY`, or `TAUTOLOGICAL`.

3. **State-Space Reduction Capacity ($\Delta\Omega$)**:
   - Calculates the theoretical state-space collapse potential $\Delta\Omega \in [0.0, 1.0]$.
   - Heavily penalizes unconstrained macro queries and biased questions that fail to rule out competing hypotheses.

4. **Orthogonal & Adversarial Counter-Question Synthesis**:
   - Automatically generates targeted counter-questions exploring:
     - Epiphenomenon vs. primary causality.
     - Physiological boundary condition breakdown or inversion.
     - Direct premise refutation.

5. **Socratic Canonical Refinement**:
   - Reformulates loaded or premise-smuggled questions into clean, falsifiable, and hypothesis-neutral inquiries.

## Consequences
- **Positive**: Prevents premature resource waste on biased or unfalsifiable questions; elevates question generation to a first-class mathematical filter in the discovery pipeline.
- **Auditable**: All question evaluations are recorded into `ScientificLedger`.
- **Zero Cloud**: Runs locally with deterministic heuristics and optional local AI inference (Laya/LMStudio).
