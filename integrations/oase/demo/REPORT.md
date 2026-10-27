# `oase formal` demo: a Stage 1 target hypothesis, its rival, and two evolved variants

> **Illustrative.** The four hypotheses below were written for this demo from a plausible Stage 1 target hypothesis
> (TREM2 agonism in amyloid pathology). They are not claims of CoResearcher, of the Fundación or of OASE, no literature
> was consulted, and each hypex record says so in its `evidence` entry. The formal check never reads that field.

Run on 2026-10-19 in an OASE checkout at `b7e5e35` (GoogleCloudPlatform/LifeSciences) with
[`apply.sh`](../apply.sh) applied, by [`run_demo.sh`](run_demo.sh). Every command and its exit code is in
[`artifacts/run_demo.log`](artifacts/run_demo.log); the artifacts are under [`artifacts/raw/formal/`](artifacts/raw/formal/)
exactly as OASE wrote them (checksums in each `.meta.json` match the committed bytes).

## Inputs

| Id | Hypothesis (prose, abridged) | Formal object, in one line |
| --- | --- | --- |
| H-0001 | Early on, a TREM2 agonist reduces neuritic dystrophy when TREM2 works, and does nothing when it is lost. | scope `stage == 'early'`; normal + agonist ⇒ `decrease`; loss + agonist ⇒ `none` |
| H-0002 (rival) | TREM2 agonism does nothing early and helps late. | normal + agonist + early ⇒ `none`; normal + agonist + late ⇒ `decrease` |
| H-0003 (hypex `combine` of 1 and 2) | In TREM2 loss-of-function carriers the agonist reduces dystrophy, although their microglia cannot respond to it. | scope loss + agonist; assumption loss ⇒ `none`; claim `decrease` |
| H-0004 (hypex `simplify` of 1) | Agonism "modulates" dystrophy: it may decrease, stay unchanged or increase. | claim `dystrophy_change in ('decrease', 'none', 'increase')` |

All four share one state space (stage × TREM2 function × treatment × dystrophy change = 24 states) and the assumption
that vehicle is the reference (`none` against itself). The objects are in [`inputs/`](inputs/); the hypex records
validate against `hypothesis.schema.json`.

## Verdicts (`.analysis.json`, recomputed offline and reproduced)

| Run | Verdict | Applicable / forbidden states | `max_formal_defects` | AR mapping |
| --- | --- | --- | --- | --- |
| [`fm-H-0001_vs_H-0002`](artifacts/raw/formal/fm-H-0001_vs_H-0002.analysis.json) | FALSIFIABLE; INCOMPARABLE with H-0002 | 8 / 4 | met | completed / supported |
| [`fm-H-0002`](artifacts/raw/formal/fm-H-0002.analysis.json) | FALSIFIABLE | 16 / 4 | met | completed / supported |
| [`fm-H-0003`](artifacts/raw/formal/fm-H-0003.analysis.json) | SELF_CONTRADICTORY | 2 / 2 | not met | completed / contradicted |
| [`fm-H-0004`](artifacts/raw/formal/fm-H-0004.analysis.json) | UNFALSIFIABLE | 16 / 0 | not met | completed / contradicted |
| [`blocked/fm-H-0001`](artifacts/raw/formal/blocked/fm-H-0001.analysis.json) (prose, no model configured) | BLOCKED, no verdict | — | `met: null` | blocked / not_assessed |

Every decided analysis carries `formal.not_empirical` and `formal.enumeration_declared_domains_only`: none of this says
any hypothesis is true, and it holds for the declared domains only. `min_excluded_fraction_of_applicable` is UNRESOLVED
in `formal@1.0`, so the fraction each hypothesis forbids (0.5, 0.25, 1.0, 0.0) is reported without a pass/fail.

- **H-0003 is self-contradictory.** It applies only to loss-of-function carriers on agonist; its own assumption says
  those cases show no change; its claim requires a decrease. Both applicable states are forbidden: no possible
  observation is consistent with it. It reads as a bold, mechanistic, testable hypothesis.
- **H-0004 is unfalsifiable.** Its claim allows every value of the outcome, so it forbids none of its 16 applicable
  states. It reads as the cautious, nuanced one.
- **The prose run without a model is BLOCKED (exit 8)** and its analysis maps to `not_assessed`. It is not a failed
  gate and not evidence against H-0001.

## What separates the rivals

H-0001 and H-0002 are both falsifiable and neither implies the other (INCOMPARABLE: 3 states forbidden only by H-0001,
3 only by H-0002, 1 by both). The discriminating states, from `assessment.reports.comparisons[0].discriminating_examples`:

| stage | TREM2 | treatment | dystrophy change | forbidden by |
| --- | --- | --- | --- | --- |
| early | normal | agonist | decrease | H-0002 |
| early | normal | agonist | none | H-0001 |
| early | loss | agonist | decrease | H-0001 |
| early | loss | agonist | increase | H-0001 |
| late | normal | agonist | none | H-0002 |

So one arm decides between them: **early stage, functional TREM2, agonist vs vehicle**. A decrease refutes H-0002; no
change refutes H-0001. The late-stage arm tests only H-0002, and the loss-of-function arm only H-0001.

The prediction both runs were asked about, "early, functional TREM2, agonist: dystrophy does not increase", is entailed
by **both** (`follows_from_claims: true` in each). It is a fine prediction and a useless experiment for choosing
between them.

## What an Elo tournament could not tell

No tournament was run for this demo; the point is structural, about what an Elo record contains. An Elo rating is a
summary of pairwise preferences between prose, judged on rubric axes. Nothing in that record:

- distinguishes H-0003's contradiction from boldness, or H-0004's emptiness from caution. A rubric judge scoring
  testability reads prose, and both read as testable. A rating cannot be "undefined"; each of them would get one.
- says that H-0001 and H-0002 are INCOMPARABLE rather than one refining the other, or which experiment separates them.
  A gap in rating says one was preferred, not where they disagree.
- flags that the shared prediction cannot discriminate: both hypotheses would be credited with it.
- is recomputable. A rating depends on the judge's samples; the formal verdict is recomputed offline by
  `oase formal analyze` and checked against the run report by report (`reproduces_run: true` for every decided run
  here).

Conversely, nothing here says which hypothesis is more plausible, novel or important; that remains the tournament's and
the reviewers' job. The formal check decides what each hypothesis can be tested on, before the tournament spends
matches on hypotheses that cannot lose (H-0004) or cannot win (H-0003).

## Stage 1 gate

[`../gate/GP-001.formal-soundness.json`](../gate/GP-001.formal-soundness.json) has `REQ-001`, a `scientific_cutoff`
with `evidence_type: formal-soundness`, `threshold_set: formal@1.0`, `threshold_key: max_formal_defects`. The three
assessment records in [`artifacts/gate/`](artifacts/gate/) were produced by [`make_assessment.py`](make_assessment.py),
which copies `assessment.evidence_assessment` from each analysis and cites it by path and sha256: AR-001 (H-0001)
`supported`, AR-002 (H-0003) `contradicted`, AR-003 (prose, no model) `blocked` / `not_assessed`. All three validate
with OASE's `validate_assessment` and match REQ-001 by `evidence_type`; AR-003 leaves the requirement unevaluated
rather than failed.
