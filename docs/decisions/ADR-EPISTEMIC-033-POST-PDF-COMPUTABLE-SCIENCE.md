# ADR-EPISTEMIC-033: Post-PDF Computable Science & Anti-Slop Cryptographic Verification Invariant

- **Status**: Accepted
- **Date**: 2026-10-04
- **Author**: Dr. Manuel Menéndez González / Fundación de Neurociencias (FdN)
- **Applies to**: Full Ecosystem (CoResearcher, DataAILab, EdiTXT, GeneForge, Neurodiagnoses)
- **Cross-Reference**: `docs/ECOSYSTEM_BOUNDARIES.md`, `ADR-DISCOVERY-010` (RCS), `ADR-DISCOVERY-022` (Paper2Agent MCP).

---

## 🏛️ Foundational Manifesto

> ### *"The PDF is dead as proof of scientific rigor. When generating polished narrative prose costs zero, prose is reduced to noise."*
> ### *"Science is not text; science is the deterministic, reproducible contact between hypothesis and empirical reality."*

---

## 1. Context and Problem Statement: The Academic Slop Inundation

The academic publishing ecosystem is undergoing a terminal structural collapse driven by the **Jevons Paradox of Generative AI**:
1. **Zero-Cost Narrative Generation**: Large language models can produce fluent, publication-grade academic PDFs complete with convincing LaTeX formatting, bibliography citations, and aesthetic figures in seconds.
2. **Breakdown of Human Peer Review**: Traditional journal and arXiv peer-review structures are mathematically incapable of triaging the exponential volume of synthetic manuscripts. Reviewers spend hundreds of uncompensated hours attempting to detect subtle hallucinations, fabricated statistical claims, and data leakage across hundreds of pages.
3. **The Devaluation of Pure Text**: In the 20th century, a well-written paper was an indirect proxy for rigorous laboratory work. In 2026, **prose is cheap; empirical data and deterministic verification are dear**.

---

## 2. Institutional Decision: The Computable Scientific Trinity

CoResearcher, DataAILab, and EdiTXT reject the static PDF as the primary vehicle of scientific truth. We establish the **Anti-Slop Cryptographic Verification Invariant (ADR-EPISTEMIC-033)** across the entire ecosystem:

```
+----------------------------------------------------------------------------------------------------+
|                         THE ANTI-SLOP COMPUTABLE VERIFICATION PIPELINE                             |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ 1. EDITXT: DEFENSIVE PEER-REVIEW SWARM ]                                                        |
|  - Automates first-reader defense against generative slop.                                         |
|  - EpistemicReviewer & ReproducibilityReviewer intercept ungrounded narrative claims.              |
|  - Enforces Kitchenham GUEST Compliance (ADR-EPISTEMIC-029).                                       |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Computable Manuscript & Claims
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ 2. DATAAILAB: REPRODUCIBLE IN-SILICO OS & EVIDENCE LEDGER ]                                     |
|  - Executes statistical models, neural ODEs, and cohort pipelines on physical datasets.            |
|  - Produces immutable, zero-mocking artifacts: ReleaseManifest with SHA-256 data lineage.         |
|  - Binds figures and tables to executable code contracts (Zero Stale Figures).                     |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Empirical Evidence Contract & Data Hashes
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ 3. CORESEARCHER: EPISTEMIC COURT & REALITY CONTACT FIREWALL ]                                   |
|  - Interrogates claims via Paper2Agent MCP Servers (`query_assertion`, `verify_regularity`).       |
|  - Enforces Reality Contact Score: RCS >= 2.0 (Mandatory contact with real physical data).        |
|  - Disregards narrative prose: audits raw data lineage hashes and physical conservation laws.      |
|  - Audits PRs via EpistemicPRAuditor to block synthetic hallucination and statistical p-hacking.   |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Cryptographically Certified DOI
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ IMMUTABLE ZENODO RELEASE / COMPUTABLE CITABLE ARTIFACT ]                                        |
|  - The certified output is not a flat PDF; it is a reproducible, executable container:             |
|    Manuscript + Code + Raw Data Hashes + Verification Verdict + SOM Cryptographic Signature.       |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Concrete Architectural Specifications

### 3.1. The Anti-Slop Gate (`SlopImmunityGate`)
Every incoming manuscript or scientific report submitted to CoResearcher must pass three immutable checks:
1. **Data Lineage Binding**: Every claim citing a statistic ($p$-value, hazard ratio, effect size, enstrophy bound) must link to a citable `SOM-SHA256` lineage hash from DataAILab or an external empirical registry (PDB, UniProt, ChEMBL, ADNI).
2. **Reality Contact Enforcement ($RCS \ge 2.0$)**: Claims supported solely by literature citation without raw data contact or prospective holdout confirmation remain at $RCS = 0$ or $1$ and cannot be promoted to verified scientific invariants.
3. **Interactive Paper2Agent Protocol**: Certified papers must expose executable query endpoints allowing peer agents to probe assumptions dynamically rather than parsing static markdown or PDF prose.

### 3.2. Automated Slop Interception in `EpistemicPRAuditor`
`ScientificEpistemicPRAuditor` is augmented with the `ScientificViolationCategory.SYNTHETIC_SLOP_UNGROUNDED` detector:
- Flags PRs containing descriptive assertions without corresponding empirical data ingestion or mathematical proof DAGs.
- Rejects commits that inflate text volume without increasing state-space reduction ($\Delta \Omega = 0$).

---

## 4. Consequences and Ethical Stance

1. **Restoring Academic Integrity**: Protects researchers from the exhaustion of manual slop filtering by deploying automated, mathematically rigorous epistemic defenses.
2. **Data-Centric Value**: Shifts the academic incentive from "publishing 5 narrative papers per month" to "proving 1 verified, reproducible invariant constraint".
3. **Permanence**: Science published through the Trinity (EdiTXT + DataAILab + CoResearcher) withstands the test of time because its truth is anchored in immutable data, not in transient linguistic eloquence.
