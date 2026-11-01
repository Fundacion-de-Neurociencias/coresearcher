# The verification chain on biomedical hypotheses

**ADR:** [ADR-DISCOVERY-086](../../decisions/ADR-DISCOVERY-086-BIOMEDICAL-DOMAIN-TRANSFER.md), on the chain of
[ADR-DISCOVERY-085](../../decisions/ADR-DISCOVERY-085-FREEZE-LEDGER-CHAIN.md)
**Fixture:** [`biomedical-chain/cases.json`](../../../benchmarks/regression/fixtures/biomedical-chain/cases.json),
regression case `biomedical_chain` ([regression benchmarks](../REGRESSION_BENCHMARKS.md))
**Scope:** formal soundness of the formal objects only. Nothing here judges evidence, sources or clinical validity.

> **Illustrative values only.** Every cutoff, level, unit assignment and range below was chosen to exercise a check.
> None of them is a clinical value, and none should be read as one. The z3 witnesses are the solver's choices, not
> patients.

## 1. What was run

The eight steps of the methodology (section 3 of
[`VERIFICATION_METHODOLOGY.md`](../../architecture/VERIFICATION_METHODOLOGY.md)) were run on three biomedical
hypotheses and their variants:

| Step | Method | What it checks |
| --- | --- | --- |
| 1. freeze | M3 | the discriminating states against the rivals are frozen before any evaluation |
| 2. formalize | M2 | the formal object comes from the caller (SUPPLIED), a controlled-language mechanism (COMPILED) or a formalizer gate |
| 3. fidelity | M1 | the formal object says what the prose says |
| 4. vacuity | M4 | declared non-witnesses, and the domain probes (null biomarker, untreated arm) |
| 5. obligations | M5 | the ADR-076 ledger and its dependency DAG, including the links of a mechanism |
| 6. seams | M6 | cited results, units and the validated population |
| 7. discharge | M8 | every obligation discharged exactly or left OPEN |
| 8. trust ladder | M7 | the weakest-link roll-up |

Commands that reproduce every table:

```bash
coresearcher regression check --case biomedical_chain
```

```bash
coresearcher chain run --request REQUEST.json
```

`REQUEST.json` is any `request` object of the fixture.

## 2. Before block E

On master after block D, the same hypotheses gave:

| Hypothesis | Chain outcome | Why |
| --- | --- | --- |
| pTau217 two-cutoff rule, as in `ptau217_cutoff_case.py` | REFUTED | The rule's guarantees are its claims, and its assumptions entail them, so the claims forbid nothing. The ledger refutes a claim with no content |
| Alzheimer rivals (each against the other two) | OPEN | Fidelity and vacuity are OPEN, and the claims are discharged. Nothing checks whether the explanatory variable does any work |
| Mechanism in prose | BLOCKED at formalize | No formalizer model, and no deterministic path from a mechanism to a formal object |

Nothing checked units. The registry compared "pg/mL" with "ng/L" as a MISMATCH, and every citation had to repeat the
hypothesis's conventions. ADR-086 closes these gaps. The tables below are the chain after it.

## 3. (a) The pTau217 two-cutoff rule

**Restated** (`ptau217_cutoff`). The empirical premise, that the biomarker separates amyloid-PET negative from
positive people after correcting for clearance, is the claim. Ordered cutoffs and preserved renal clearance are
assumptions. The rule-out and rule-in guarantees are consequences. The variables are continuous, so z3 decides
every check.

The biomedical block declares:
- units: ng/L for the biomarker and the cutoffs, mL/min/1.73m^2 for eGFR, and a dimensionless clearance factor;
- conventions: assay A, blood plasma, Aβ PET, maximal Youden index;
- probes: a null-biomarker probe on `ptau_val`, and a population probe for eGFR ≥ 60.

The rule cites an illustrative cutoff entry. That entry is in pg/mL, validated under assay A in plasma against
amyloid PET by the Youden index, with the hypothesis "eGFR ≥ 60".

| Step | State | Outcome |
| --- | --- | --- |
| freeze | DONE | FROZEN (the rival, separation on the measured value without the clearance correction, is WEAKER) |
| formalize | DONE | SUPPLIED |
| fidelity | OPEN | no fidelity spec |
| vacuity | OPEN | vacuity OPEN (no declared non-witness); `probe:null_biomarker[ptau_val]` DISCHARGED_SYMBOLIC |
| obligations | DONE | 9 obligations, DAG acyclic |
| seams | DONE | citation CLEAR; units HOMOGENEOUS; population INSIDE_VALIDATED_POPULATION |
| discharge | DONE | 7 DISCHARGED_SYMBOLIC, 2 OPEN |
| trust ladder | DONE | OPEN at STATEMENT_PUBLIC |

What each seam check found:
- Every convention of the citation MATCHES:
  - pg/mL against ng/L, by unit algebra;
  - "plasma" against "blood plasma", "amyloid PET" against "Aβ PET", and "Youden index" against "maximal Youden
    index", by canonical value.
- The eGFR hypothesis is DISCHARGED by the assumptions.
- Both guarantees are DISCHARGED by z3.

The only open items are fidelity and vacuity. Both need the author: a fidelity spec, and declared non-witnesses.

**Variants:**

| Variant | Outcome | What the chain shows |
| --- | --- | --- |
| `ptau217_cutoff_as_submitted`: the case module's own form | REFUTED | Both claims are REFUTED as claims with no content. The ledger now says why: they follow from the assumptions and belong in `consequences` |
| `ptau217_cutoff_without_renal_assumption` | REFUTED | Both guarantees are REFUTED, with a z3 counterexample: clearance factor 2, ptau_val 1.5 above c_high 1.25, amyloid PET negative. The citation is FINDINGS (eGFR hypothesis NOT_DISCHARGED). The population probe finds states outside eGFR ≥ 60 (OPEN, with a witness). The renal assumption is necessary, as `necessity_table()` found, and now three independent seams of the chain report it |
| `ptau217_cutoff_unit_seam`: c_high in ng/mL, ptau_val and c_low in ng/L | REFUTED | `units` is REFUTED: three predicates compare quantities that differ by a factor of 1000. The citation is FINDINGS, because the entry's pg/mL is not c_high's ng/mL |

## 4. (b) The Alzheimer formal scenario

The three rivals of [ADR-061](../../decisions/ADR-DISCOVERY-061-FORMALIZER-AND-FORMAL-WORKBENCH.md) are a DRAFT pending
scientist review. Each was run against the other two. The null-biomarker probe was run on the variable or variables
that each rival's prose makes explanatory.

| Rival | Probe | Vacuity step | Roll-up |
| --- | --- | --- | --- |
| HYP-TAU-CONNECTOME | hub, tau | hub DISCHARGED_SYMBOLIC; **tau REFUTED** | REFUTED at STATEMENT_PUBLIC |
| HYP-VASCULAR-WMH | wmh | DISCHARGED_SYMBOLIC | OPEN at STATEMENT_PUBLIC |
| HYP-NULL-NONSPECIFIC | tau | DISCHARGED_SYMBOLIC | OPEN at STATEMENT_PUBLIC |

All three pairs are INCOMPARABLE, so each freeze records discriminating states in both directions. Every claim is
DISCHARGED_SYMBOLIC. Fidelity and vacuity are OPEN. Seams are NOT_APPLICABLE, because no result is cited.

**The finding.** The draft formalization of HYP-TAU-CONNECTOME uses tau only as its scope (`tau == 'T+'`). No two
applicable states that differ only in tau are treated differently. A constant tau would say the same, so tau does no
work in the claims. The prose is about "tau spreading rates". ADR-061 already lists spreading rates as not
formalized, and the probe now makes that omission a REFUTED obligation instead of a footnote. This is a finding
about the draft formal object, not about the scientific hypothesis.

## 5. (c) A mechanistic chain from prose

The prose, in the controlled language:

> Amyloid raises plasma pTau217, which drives tau spread, which worsens cognition.

The four nodes have ordinal levels 0..2 (illustrative). The cognitive score is declared higher_is_better. The
grammar reads three links:
- amyloid → pTau217 (+);
- pTau217 → tau spread (+);
- tau spread → cognition: "worsens" on a higher_is_better score, so −.

The default end-to-end prediction is the product of the signs: raising amyloid, with no other root moving, lowers
cognition.

| Step | State | Outcome |
| --- | --- | --- |
| freeze | DONE | FROZEN (the compiled two-world hypothesis) |
| formalize | DONE | COMPILED (a deterministic grammar, one reading) |
| fidelity | OPEN | no fidelity spec; a single deterministic reading is not two readings that agree |
| vacuity | OPEN | vacuity OPEN; `probe:untreated_arm` DISCHARGED_SYMBOLIC (with no root moving, cognition cannot fall) |
| obligations | DONE | 20 obligations: 9 node claims, the prediction, 3 links, 3 signs, compatibility, the untreated arm, fidelity, vacuity |
| seams | NOT_APPLICABLE | no cited results, no units declared |
| discharge | DONE | 18 DISCHARGED_SYMBOLIC, 2 OPEN |
| trust ladder | DONE | OPEN at STATEMENT_PUBLIC |

**Variants:**

| Variant | Outcome | What the chain shows |
| --- | --- | --- |
| `mechanism_sign_seam`: structured links; the last is written with sign `+` and effect "worsens" | REFUTED | `link_sign[2]` is REFUTED: "worsens" on a higher_is_better score is −. The links as written then do not entail the predicted fall in cognition. `consequence[0]` and `mechanism:compatibility` are REFUTED, with the counterexample amyloid 0→1, pTau217 0→1, tau spread 0→1, cognition 0→1 |
| `mechanism_saturated_link`: tau spread has a single level | REFUTED | `link[1]` and `link[2]` are REFUTED: a node with a single level cannot carry the change. Compatibility is REFUTED, because the links forbid the intervention. The prediction holds only vacuously, and compatibility, not the entailment, reports it |
| `mechanism_outside_grammar`: "Amyloid somehow modulates plasma pTau217." | FORMALIZATION_FAILED | The verb is not in the grammar. The chain stops at formalize, every later step is NOT_RUN, and there is no roll-up. Nothing is guessed |

## 6. Per step: what worked, and what stayed a non-verdict

| Step | Worked | Non-verdict or OPEN, and why |
| --- | --- | --- |
| freeze | Every decided run froze its criteria before evaluating. The restated pTau217 rule is BLOCKED against its own freeze once its claim is edited | None |
| formalize | Supplied objects. Mechanisms compiled from controlled prose | FORMALIZATION_FAILED for prose outside the grammar. Free prose still needs the formalizer gate (ADR-064) and a configured model, otherwise BLOCKED |
| fidelity | Nothing new: the service exists (ADR-070) | OPEN everywhere. No run supplied a fidelity spec or a statement audit, and the chain has no independent formal reading of the prose. This is the main residual gap, and closing it is the scientist's act |
| vacuity | Null-biomarker, untreated-arm and population probes decided exactly, with witnesses | Declared non-witnesses: OPEN unless the author declares them |
| obligations | Mechanism links, signs and compatibility as ledger obligations, in an acyclic DAG | A cycle of links is refused as input, not approximated |
| seams | Units by algebra, conventions by vocabulary, cited hypotheses by entailment, the validated population by a probe | A cited hypothesis without a formal predicate stays UNDECIDED (ADR-083) |
| discharge | Every decided obligation is DISCHARGED_SYMBOLIC or REFUTED by enumeration or z3 | None beyond the OPEN items above |
| trust ladder | Weakest-link roll-up | No run passes STATEMENT_PUBLIC: no claim has a statement audit or a kernel check |

## 7. Limits

- **The mechanism encoding.** It is qualitative and acyclic. It decides signs and their composition, not magnitudes,
  timing or feedback.
- **The probes.** They decide properties of the formal object over the declared domains. Whether a cutoff, a
  population or a mechanism is clinically right is outside CoResearcher's scope.
- **The Alzheimer formalizations.** They remain a DRAFT (ADR-061). A REFUTED probe there is a statement about the
  draft.
