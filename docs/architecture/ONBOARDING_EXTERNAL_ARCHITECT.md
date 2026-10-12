# Onboarding Guide for External Architects (15 min reading)

Welcome to CoResearcher. If you're reading this, you're joining the team or auditing our code. This document distills what this project is about and what assumptions you should discard before touching a line of code.

## 1. WHAT IS CoResearcher?

CoResearcher is a scientific **Traceability Engine**. It is a piece of infrastructure in charge of observing real-world scientific activity (commits in GitHub, issues, repositories, deposits in Zenodo, papers in PubMed) and converting it into a structured, deterministic and mathematically auditable graph.

Our mission is to always answer a single question:
> "Where is the exact, auditable evidence that supports this claim?"

## 2. What does CoResearcher PRODUCE?

The system is fed by unstructured observations and produces:
- **EvidenceGraphs**: Directed Acyclic Graphs (DAGs) where each statement (`Claim`) is rigidly linked to an exact citation (`Quote`), and is to a verifiable source (`Source`).
- **Provenance Chains**: Cryptographic traceability of who, when and how a claim was extracted.

CoResearcher **never evaluates** the content. It simply immutably certifies that "On line X of commit Y, user Z asserted W."

## 3. What CoResearcher will NEVER do (Your Antipatterns)

To maintain our competitive advantage and not collide with AI giants (DeepMind, OpenAI), CoResearcher has strict architectural prohibitions. **Under no circumstances do you program features that cross these lines:**

❌ **We are not an AI Scientist:** CoResearcher does not propose hypotheses, discover new drugs, or infer new science.
❌ **We are not Editors / Reviewers:** CoResearcher does not say whether a paper is "good" or "bad", nor does it evaluate whether a methodology is correct.
❌ **We do not generate human text:** CoResearcher extracts and outputs JSON structures (graphs). We do not write scientific prose.

*Any Pull Request that attempts to get CoResearcher to comment on the quality of a paper or attempts to deduce a conclusion that is not explicitly cited in a source document will be immediately rejected for violating the Constitution.*

## 4. How does it integrate with EditXT?

The ecosystem has another piece called **EditXT**, which acts as a Scientific Auditor (this does evaluate quality and issue recommendations).
The integration contract is one-way and strict:

1. EditXT sends us an `EvidenceRequest`.
2. CoResearcher scans the repositories and returns an `EvidenceGraph`.
3. **Communication is cut off.**
4. EditXT uses our foolproof graph to generate its own verdicts (Severity, Recommendations, ReviewGraphs). CoResearcher ignores and repudiates any return evaluations coming from EditXT.

---
**Your first task:** Review the document [EVIDENCEGRAPH_SPEC.md](EVIDENCEGRAPH_SPEC.md) to understand how we structure the data we deliver to higher ecosystem applications.