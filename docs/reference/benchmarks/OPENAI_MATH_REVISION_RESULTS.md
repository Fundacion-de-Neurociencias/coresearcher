# openai/math revision benchmark ("time travel"): results

Protocol: `OPENAI_MATH_REVISION_PROTOCOL.md`. Its SHA-256,
`e4a309bc10cff2c898956aa4f064a6a6a4a97629ff1cbf5e57386f34cd845cfd`, was frozen in commit `8d7d636` before
the run. Data: `openai_math_revision_dataset.json` (SHA-256 `257501b1…`) and
`openai_math_revision_results.json`. Script: `scripts/benchmarks/openai_math_revision_bench.py`.

## 1. Question and answer

The October 7, 2026 release of `openai/math` revised 14 manuscripts and withdrew 3. The question: would the
checks CoResearcher can run today have flagged those 17 defects on the source as it stood before the fix?

**Mostly no.**

- **One defect was really detected.** In *Exact BSD from low Selmer corank*, the citation check flags an
  unresolved key.
- **One HIT under the protocol is a chance coincidence** (section 3).
- **The other 15 defects are NOT_ENCODABLE**: they lie outside the language of every check that exists today.

| Outcome | Defects | Share (Wilson 95%) |
| --- | --- | --- |
| HIT under the protocol | 2 | 2/17 (0.03–0.34) |
| HIT that reflects the defect | 1 | 1/17 (0.01–0.27) |
| MISS | 0 | 0/17 |
| NOT_ENCODABLE | 15 | 15/17 |

That is the result. It ranks the mechanisms to build next (section 5). With 17 defects, none of these rates is
a performance claim.

## 2. What the release corrected

All 17 fixes are in one commit. Every pre-fix edition stays in the tree under its earlier date, and its git tree
is identical at both commits.

- `PRE`: `adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- `POST`: `301488868beec11bfd897168433b0a64f5258559`

| Group | Defect type (from `history.md`, version notes and diffs) | n |
| --- | --- | --- |
| Withdrawn: Weil eightfolds; Kuga–Satake for K3; products of K3 | A sign imported from a cited stabilization-trace lemma is wrong under the paper's orientation convention. The signed double-point count is −2m rather than 0, so the hypothesis of the cancellation theorem fails. The two K3 papers adapt the same step. | 3 |
| Lipschitz heights / Ashkin–Teller | Repaired probabilistic arguments: crossing, boundary attachment, conditioning, convergence. | 4 |
| Kähler MMP / abundance | Expanded positivity and contraction arguments. Inputs from companion papers are stated with their hypotheses. | 6 |
| *Taming implies compatibility* | The corollary asserted the cone identity K^t = K^c + H^-, citing Li–Zhang, Cor. 1.1, without that result's hypothesis. The fix restricts it to h_J^- = b_2^+ − 1 and adds a four-torus example of strict inclusion. | 1 |
| *Deforming hypersymplectic* | Removed a dependency on that cone comparison. | 1 |
| *Incompressible Box Transport* | "Effective" projection and decay estimates were asserted with a sketch. The fix gives explicit constants. | 1 |
| *Exact BSD from low Selmer corank* | A citation to a removed supporting manuscript. In the source the key `\cite{Dv}` has no bibliography entry. | 1 |

The protocol defines 13 more new editions as citation updates: only their links to revised companions change.
They serve as a near-null group.

## 3. Per-defect results

Columns, in order:

- **CIT, ID-S, ID-C, EXP**: the citation, identity-strict, identity-context and exponent checks.
- **Lean**: `statement_fidelity` and `lean_junk_lint`.
- **Flags at location**: pre-fix flags within ±2 lines of a changed line, summed over checks.

| Defect | CIT | ID-S | ID-C | EXP | Lean | Flags at location | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Exact BSD from low Selmer corank | **HIT** | NE | NE | NE | NE | 1 | **HIT** |
| Uniform real Lipschitz surfaces | NE | NE | HIT\* | NE | NE | 1 | HIT\* |
| Weil eightfolds (withdrawn) | NE | NE | NE | NE | NE | 0 | NE |
| Kuga–Satake for K3 (withdrawn) | NE | NE | NE | NE | NE | 0 | NE |
| Products of K3 (withdrawn) | NE | NE | NE | NE | NE | 0 | NE |
| Taming implies compatibility | NE | NE | NE | NE | NE† | 0 | NE |
| Deforming hypersymplectic | NE | NE | NE | NE | NE | 0 | NE |
| Incompressible Box Transport | NE | NE | NE | NE | NE† | 0 | NE |
| Weighted Lipschitz heights GFF | NE | NE | NE | NE | NE | 0 | NE |
| Two-arc Lipschitz heights GFF | NE | NE | NE | NE | NE | 0 | NE |
| Ashkin–Teller currents | NE | NE | NE | NE | NE | 0 | NE |
| Conditional good minimal models | NE | NE | NE | NE | NE | 0 | NE |
| Finite ordinary MMP | NE | NE | NE | NE | NE | 0 | NE |
| Log abundance | NE | NE | NE | NE | NE | 0 | NE |
| Numerical semiampleness | NE | NE | NE | NE | NE | 0 | NE |
| Termination, generalized canonical flips | NE | NE | NE | NE | NE | 0 | NE |
| Termination, generalized log canonical flips | NE | NE | NE | NE | NE | 0 | NE |

NE = NOT_ENCODABLE.

**The real hit.** `sections/01-introduction.tex:134` reads `methods of \cite{B,C,Dv}`, and the source has no entry
`Dv`. The corrected edition drops the key. The chance baseline is 0.0007 expected location matches, so this
match is not luck.

**\* The chance hit.** It qualifies as a HIT under section 6 of the protocol, but it says nothing about the
defect.

- The flag is `sections/geometry.tex:867`, the equation `r_j-r_{j+1}=10Q_jr_j`. It recalls a correct definition
  of the radius sequence. The context tier flags it only because, out of context, it is not an identity.
- The flag "resolved" only because the fix rewrote the multiscale-separation passage around it.
- This revision's location covers 1115 of 6408 source lines, about 17% of the manuscript, and the chance
  baseline expects at least one context flag there.

It is counted as a protocol HIT and adjudicated as chance.

**† Lean checks.** Families 342 and 376 have Lean notes, so the Lean checks could run on them. Neither Lean
statement covers the corrected claim:

- Note 342 formalizes only the main taming-implies-compatibility theorem, not the cone corollary.
- Note 376 formalizes the computation statements, not the prose estimates.

`lean_junk_lint` ran on their Comparator files:

- Taming: 2 OPEN findings.
- Incompressible: 43 OPEN, 33 of them in `NavierStokesVelocity.lean`.

None can sit at a `.tex` defect location.

**Withdrawals: why NOT_ENCODABLE is the honest label.**

- The displayed arithmetic is internally consistent. In the Weil paper, with m = −I(f_1), the identity
  I(f_1) + m = 0 holds.
- The error is the value +1 assigned to a reverse trace. It comes from `(-1)^k` with k = 4, imported from
  [EEMS, Lemma 3.2] under a different orientation convention.
- No identity or exponent check can see a convention mismatch.
- The Kuga–Satake passage `I+m(-1)^l=0` lies outside the restricted fragment: `m(` reads as a possible
  function application, so it was skipped. Even parsed, it would be a context flag, not evidence of the sign
  error.

## 4. False alarms

These are flags left in place by the authors' fix, or raised on never-revised manuscripts. The corrected
versions and the controls give the alarm load each check would put on a reviewer.

| Check | Persistent on 14 corrected (per 1000 lines) | 13 citation-update pairs | 17 never-revised controls | Manuscripts flagged (corrected / citation / controls) |
| --- | --- | --- | --- | --- |
| CITATION | 0 (0.000) | 0 (0.000) | 0 (0.000) | 0 / 0 / 0 |
| IDENTITY_STRICT | 5 (0.057) | 11 (0.160) | 3 (0.062) | 2 / 5 / 3 |
| IDENTITY_CONTEXT | 324 (3.669) | 435 (6.343) | 237 (4.902) | 14 / 13 / 17 |
| EXPONENT | 11 (0.125) | 11 (0.160) | 7 (0.145) | 5 / 6 / 3 |
| `lean_junk_lint` OPEN | — | — | 1,184 over the 8 controls with Lean notes (771 in one file, `ThorpRouting.lean`) | — |

Source sizes: 88,298 lines (corrected), 68,578 (citation updates), 48,350 (controls).

The citation check gave **one hit and zero false alarms**: it checked 3,409 citations and 155 internal links
over the pre-fix sources of all 47 units.

Every IDENTITY_STRICT and EXPONENT flag, on all units, was read by hand. **None is a mathematical error.** All
are notation the restricted fragment misreads:

- **Superscripts that are indices, not powers.** `H^0=0` and `O^0=0` are a cohomology group and a sheaf,
  `F^0=0` is a filtration step, and `h^0=3` is a dimension.
- **Equalities that hold in a stated ring.** `-1=1` in characteristic 2, `2=0` mod 2, `1=0` in a zero ring.
- **`\simeq` and `\sim` as isomorphism or equivalence**, not asymptotics: `U\simeq U_X`, `i\sim j`, `B_p\sim-H_p`.

The context tier flags every manuscript, at 3.7–6.3 flags per 1000 lines. Almost all of these are conditional
equations, as the protocol anticipated. Without local-definition context the tier is unusable.

Coverage: 109,843 math segments and 21,800 `=`/asymptotic relations were seen. Of the relations, 5,366 (25%)
parsed in the fragment, 1,206 were identity-checked and 32 exponent-checked.

## 5. Mechanisms to build next

The ranking weighs how many of the 17 real defects a mechanism would plausibly have flagged at the defect's
location, how severe those defects were, and how tractable the mechanism is.

1. **Convention-typed import of cited lemmas (sign and orientation ledger).**
   - *Motivated by*: the 3 withdrawals, the only defects that invalidated whole papers.
   - *What it does*: every time a proof imports a sign, a count or a normalization from a cited lemma (here, the
     double-point sign of a stabilization trace from [EEMS, Lemma 3.2]), the obligation ledger gets an
     obligation "convention transfer: source convention → target convention", with both conventions typed
     (orientation of the source branches, signed double-point convention).
   - *What it would have caught*: the obligation stays OPEN until discharged. It would have raised exactly the
     passage the withdrawal notice names.
   - *Tractability*: high. It is extraction plus an OPEN obligation, not a proof.
2. **Registry of cited theorems with hypotheses, and matching at each application.**
   - *Motivated by*: Taming (Li–Zhang, Cor. 1.1 applied without h_J^- = b_2^+ − 1), the 6 Kähler revisions whose
     fixes state the hypotheses of their inputs, and Deforming.
   - *What it does*: each `\cite[Theorem X]{key}` used as a proof step becomes an obligation "the hypotheses of
     [key, X] hold here". It is discharged against a registry entry whose hypotheses are written as predicates
     (in the `formal_hypothesis` language where they are arithmetic, for example
     h_J^- = b_2^+ − 1 or b^+ = 3), and stays OPEN otherwise.
   - *What it would have caught*: the cone corollary as a hypothesis mismatch, given a Li–Zhang entry.
   - *Coverage*: up to 8 of 17 defects.
3. **Cross-manuscript dependency graph with revision propagation.**
   - *Motivated by*: Kuga–Satake and products of K3 (both depend on the Weil construction), Deforming (depends on
     the Taming corollary), Exact BSD (cites a removed manuscript), and the 13 citation updates.
   - *What it does*: once a claim is refuted or withdrawn, every manuscript that imports it is flagged at the
     import site.
   - *Limits*: it does not find the first error.
   - *Value*: it turns 1 found error into 3 flagged papers. It also generalizes today's citation check, the only
     check that hit here, from "key resolves" to "cited result still stands".
4. **Small-instance counterexample search for universal cohomological or linear-algebraic claims.**
   - *Motivated by*: Taming. The fix's four-torus example of strict inclusion shows that the pre-fix cone
     identity is false.
   - *What it does*: universal claims about cones in H^2 with an intersection form are finite-dimensional
     statements on a test manifold. A z3 or linear-programming search over standard examples (T^4, K3 lattice,
     CP^2 blow-ups) can refute them.
   - *Coverage*: narrow (1 defect), but it refutes rather than flags.
5. **Obligations for effective constants.**
   - *Motivated by*: Incompressible Box Transport.
   - *What it does*: any claim labelled effective, computable or explicit requires each constant in its proof to
     have a closed expression. A proof that leaves C_{α,L}, O(·) or "converges absolutely" as the effective
     content is flagged.
   - *Evidence*: the fix replaced exactly such a sketch with S_L = (1 + 52(L/2π)^4)^{1/2}.
6. **Notation-aware identity checking.**
   - *Motivated by*: the false-alarm analysis rather than any defect.
   - *What it needs*: read `\simeq` as isomorphism unless both sides are asymptotic quantities; treat a
     superscript on a known object symbol (H, O, F, h) as an index; respect a stated characteristic; take
     local definitions ("Set m = |I|", "Put m = −I(f_1)") as context for the identity check, so that conditional
     equations are entailed rather than flagged.
   - *Limits*: this would make the identity and exponent checks usable. It would still not have caught any of
     these 17 defects. On this corpus, errors do not sit in displayed elementary algebra.
7. **Repair detection for probabilistic and birational arguments.**
   - *Motivated by*: the 4 Lipschitz/Ashkin–Teller revisions, Finite ordinary MMP and Log abundance (argument gaps).
   - *Status*: no near-term static mechanism. The options are formalization of the step (the Lean oracle route)
     or adjudicated step-level critique, both outside this benchmark's tools.

Keep, as a standing gate, **citation resolution**: one real hit and zero false alarms over 47 units, at
negligible cost.

## 6. Deviations from the protocol

- **Code changes after the freeze commit.** No protocol text, dataset entry, location, encodability judgement or
  scoring rule was changed. The runner and the identity check were changed as follows:
  1. JSON files are written with LF line endings, so the recorded hashes match the committed bytes.
  2. Each git call has a 600 s timeout with retries. A lazy blob fetch of one Lean file hung, so the Lean files
     were also pre-fetched through a sparse checkout.
  3. Random-point evaluation in the identity check moved from exact substitution to `evalf(30, subs=…)`, with
     the same 1e-20 relative tolerance. Closed numeric powers with an exponent above 10^4 are treated as
     unparsed, and `sympy.simplify` is skipped when the difference has more than 80 operations.
- **Why change 3 was needed.** Exact substitution into powers with symbolic exponents (`n^{n}`) built integers
  with millions of digits and hung the run indefinitely on a control (*Beyond the square-root exponent*).
- **What was seen before the changes.** Two interrupted runs printed per-defect verdict lines, which were visible
  before these changes; no false-alarm table was produced. The changes respond to the hang, not to those lines.
- **Withdrawal locations.** They were set by hand from the withdrawal notices, as the protocol states, before
  any check was run.

## 7. Reproduction

```bash
python scripts/benchmarks/openai_math_revision_bench.py dataset   # rebuilds the dataset from git history
python scripts/benchmarks/openai_math_revision_bench.py run       # refuses to run if the protocol hash changed
python -m pytest tests/test_manuscript_checks.py
```

The script makes a blobless clone under `private/cache/` (git-ignored) and materializes only the 74 manuscript
directories of the dataset. On Windows, the sparse-worktree paths exceed MAX_PATH. The script reads them through
`\\?\` paths, and clones with `core.longpaths=true`.
