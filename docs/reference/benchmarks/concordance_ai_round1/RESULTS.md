# AI-expert concordance, round 1: results

**Freeze record:** [FREEZE.md](FREEZE.md). The tasks, the Claude Science text, CoResearcher's sealed answers and the
second judge's answers were all hashed and committed before any comparison. **Reply received:**
[claude_science_reply.md](claude_science_reply.md), rendered in English with the answer values unchanged (the Spanish original is archived privately, SHA-256 `021d8830…`). **Report:**
[concordance_report.json](concordance_report.json).

This is **AI-expert concordance, not human validation** (owner decision of 2026-11-01).

## Agreement with CoResearcher's formal answers

| Question | n | Claude Science | Second judge (qwen2.5:14b, other family) |
| --- | ---: | --- | --- |
| Q1 logical form | 20 | 20/20, κ = 1.00 | 16/20, κ = 0.62 |
| Q2 premise conflict | 20 | 20/20, κ = 1.00 | 19/20, κ = 0.77 |
| Q2 conflicting set | 20 | 20/20 | 19/20 |
| Q3 refutation | 18 | 18/18, κ = 1.00 | 8/18, κ = 0.25 |
| Q3 refuting rows | 18 | 18/18 | 16/18 |
| Q4 comparison with the rival | 8 | 8/8, κ = 1.00 | 2/8, κ = 0.02 |

Claude Science agrees with CoResearcher on all 104 answers. Its two lowest-confidence answers (AIR1-13 and AIR1-20,
confidence 4) still match, and the reply names the reading each one depends on.

## Disagreements, classified

Claude Science has none. All 24 disagreements of the second judge were read by hand by the maintainers. Each is a
judge error that its own rationale shows, not a CoResearcher error:

- **Q4 direction swapped** (AIR1-01, 02, 03: WEAKER answered as STRONGER). This is the classic error of comparing
  the claims instead of the situations each claim forbids.
- **"Refuted" downgraded to "possibly refuted"** although the row reports every variable (9 of 18 Q3 tasks). In
  AIR1-02 the rationale says the row "does not provide information about the wetland drying out", but the row
  reports `dry`.
- **Q1 slips:** VACUOUS taken for SELF_CONTRADICTORY (AIR1-05, 16), a tautology taken for FALSIFIABLE (AIR1-06),
  and a plain "only if" taken for SELF_CONTRADICTORY (AIR1-09).
- **Rival comparisons**: two INCOMPARABLE cases answered as CONTRADICTORY (AIR1-09, 10), and one STRONGER answered
  as EQUIVALENT (AIR1-11).
- **Observation rows treated as premises** in Q2 (AIR1-01, "row 2").

No disagreement exposed a formalization gap or a CoResearcher error.

## Reading

- On these tasks CoResearcher's formal verdicts are exactly what a strong AI expert reads from the same words. A
  smaller model from another family disagrees mostly where the reasoning is hardest: comparing what two hypotheses
  forbid, and deciding refutation from rows. Those are the places where a formal check adds the most over an
  unaided reader.
- **Ceiling effect.** The tasks come from the formalizer benchmark sets and are worded clearly, with gold-checked
  formal objects. Perfect agreement shows the formal reading matches the expert reading on well-posed hypotheses.
  It says nothing about messy research prose, where the formalizer (ADR-093) is the limiting step.
- **Same family.** Claude Science and parts of the maintainers' tooling share a model family. The second judge shows
  that agreement is not automatic, but a human panel remains the stronger test if one ever becomes available.
- **Deviation.** The reply was relayed as a Spanish table, not as the JSON with rationales. The answer values are
  unchanged. Only the per-answer rationales are missing.

## Next round

The next round should use messier prose, written by someone other than the maintainers or taken from published
abstracts, and should send CoResearcher's own formalization through the formalizer rather than the gold object. That
makes the formalizer part of what is measured.
