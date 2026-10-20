# Falsifiability: exact measure against rubric score, pre-registered pilot

Status: drafted on 2026-10-20, before any measurement under this protocol. Nothing here has been run. The script will
record this file's SHA-256 with every raw result, and scoring refuses results produced under a different protocol
hash.

Motivation. DiscoveryRSI (arXiv:2610.23839) reports that its largest gain across self-improvement rounds is in
falsifiability, measured with an automated rubric whose judge is a language model. CoResearcher's formal evaluator can
decide falsifiability exactly for hypotheses written in its formal format (ADR-DISCOVERY-059, ADR-DISCOVERY-068): a
hypothesis is UNFALSIFIABLE when no state is forbidden, VACUOUS when no state is in scope, and it reports the fraction
of the declared state space it excludes. This pilot tests whether the two measures agree, and whether an exact measure
can be used in place of the rubric where it applies.

## 1. Questions

- **Q1 (agreement).** On formalizable hypotheses, does the exact falsifiability verdict agree with the rubric's
  falsifiability judgment?
- **Q2 (informativeness).** Does a hypothesis that the exact measure calls falsifiable also exclude a non-trivial part
  of the state space, or can a falsifiable hypothesis be falsifiable only in an uninformative way?
- **Q3 (trade-off).** When revisions raise the exact falsifiability measure, do they lower a rated quality that the
  exact measure cannot see (importance)?

## 2. Scope and non-claims

- The exact measure applies only to hypotheses in the formal format. It says nothing about hypotheses that cannot be
  formalized, and the pilot reports how many were excluded and why.
- Exact falsifiability is not validity. A falsifiable hypothesis can be false, and an unfalsifiable one can be true.
- The formalization step (ADR-DISCOVERY-061) is itself a source of error. This pilot measures agreement under the
  pinned formalizer and its self-consistency gate (ADR-DISCOVERY-064). It does not measure formalization fidelity,
  which ADR-DISCOVERY-066 records as at chance (AUROC 0.524).

## 3. Materials

### 3.1 Hypotheses

Up to 300 hypotheses drawn with seed `62000` from the existing hypothesis atlas of the formal workbench, stratified by
the four life-science domains and by round (base, round 1, round 2 of DiscoveryRSI-style revisions, when available).
Each is given a random identifier. The atlas snapshot is recorded by hash.

### 3.2 Formalization

Each natural-language hypothesis is formalized by the pinned formalizer (model tag recorded) and kept only if it passes
the self-consistency gate. Hypotheses that do not pass are recorded as **excluded before measurement**, with the
reason. The exclusion rate is reported as a result in its own right.

### 3.3 Rubric scores

Each hypothesis receives the rubric falsifiability score (1–10) from the rubric judge used in DFM-Bench-style
evaluation, with three independent reviews, the median taken as the score. The judge is a model that is not among the
systems being compared. Its name and version are fixed before any run.

## 4. Exact measure

For each formalized hypothesis, the evaluator produces:

- the content verdict (FALSIFIABLE, UNFALSIFIABLE, VACUOUS or SELF_CONTRADICTORY);
- the fraction of the applicable state space that is forbidden, `excluded_fraction_of_applicable`.

A hypothesis is **exact-falsifiable** if its verdict is FALSIFIABLE. It is **informative** if, in addition, its
forbidden fraction of the applicable states is at least 0.05. The threshold 0.05 is fixed here; it is not tuned to the
data.

## 5. Analysis

### 5.1 Q1: agreement

- The rubric score is dichotomized at the median of the sample. Hypotheses above the median are rubric-falsifiable.
- Agreement between exact-falsifiable and rubric-falsifiable is reported as Cohen's kappa, with a bootstrap interval
  over hypotheses (10 000 resamples, seed `62001`), and as the Spearman correlation between the exact forbidden
  fraction and the rubric score, with its interval.
- With N ≈ 200 analysed hypotheses, the Wilson half-width for a proportion near 0.5 is about 0.07. Q1 is therefore read
  as an estimate of agreement to within about ±0.07, not as a fine comparison.

### 5.2 Q2: informativeness

- Among exact-falsifiable hypotheses, the share that are informative is reported with a Wilson interval.
- The disagreements are read by a domain expert, blind to the exact measure, and classified as one of: the rubric
  over-rewards a testable-looking plan; the exact measure counts a trivially falsifiable rule; the formalization lost
  content; or other (described).

### 5.3 Q3: trade-off

- Among revision pairs (parent, child) from the same branch, the change in exact forbidden fraction is compared with
  the change in the rated importance (from the human-rated criteria, where available), with a cluster bootstrap over
  branches.
- A revision that increases the exact measure while decreasing importance is counted as a trade-off instance. Their
  share is reported with its interval.

## 6. Criteria fixed in advance

- **Agreement (A).** Lower bound of the 95 % interval of kappa in Q1 is above 0.40. Below that, the exact measure is
  not used in place of the rubric for any claim.
- **Informativeness (I).** At least 70 % of exact-falsifiable hypotheses are informative. If not, the exact measure is
  reported only together with its forbidden fraction, never as a binary falsifiability label.
- **Trade-off (T).** Reported descriptively. No threshold is set, because the sign and size of the trade-off is what
  the pilot is meant to measure.

## 7. Known limitations, stated in advance

- The pilot uses hypotheses that the formal format can express. Hypotheses that are rich in prose, mechanism or
  context may be systematically excluded, and the excluded share is reported for that reason.
- Finite-domain exact measures depend on the declared domain and its discretization. A different discretization can
  change the forbidden fraction. The pilot fixes the discretization in the formal file and reports it with every
  result.
- Three rubric reviews from models of one family are correlated; the median is not three independent opinions. The
  DFM-Bench authors state this explicitly.
- Human calibration of the rubric is pending in DiscoveryRSI, and this pilot does not supply it. Its Q3 uses human
  ratings only where they exist.

## 8. Relation to other protocols

This pilot does not change the criteria of the unknown-mechanism benchmarks (v2 to v4) or of the counterexample search
benchmark. It uses the formal evaluator as those benchmarks do: exact over the declared states, with no sampling.
