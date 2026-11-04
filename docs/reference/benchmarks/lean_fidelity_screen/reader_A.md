# Prose screen for the Lean fidelity auditor: reader A

Plan: [LEAN_FIDELITY_AUDITOR_PLAN.md](../LEAN_FIDELITY_AUDITOR_PLAN.md), phase 2. Reader name: 

Source: [openai/math](https://github.com/openai/math) at commit `1581d4cbdd69`, Apache-2.0.

## Rules

For each family, read the prose and the formal statement, then tick exactly one box.

- **determined**: a competent mathematician who reads only the prose, and is told the theorem's name and given
  the definitions in the challenge file, would write a statement with the same mathematical content: the same
  objects, quantifiers, hypotheses, constants and bounds, up to notation. If the prose describes several
  results, it is determined when one of them is this statement and the name is enough to pick it.
- **underdetermined**: the statement contains something the prose does not fix. Examples: it is a lemma the
  prose does not state, it has a constant, bound or hypothesis the prose does not give, or it combines results
  of which the prose mentions only some.

When unsure, choose underdetermined. Decide alone: do not discuss with the other reader and do not look at any
model output. Add a short note when the choice is not obvious.

## F025: Short Egyptian fractions

Challenge file: [lean/ComparatorChallenges/EgyptianFractions.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/EgyptianFractions.lean). Theorem: `egyptian_length_is_minimum`.

**Prose**

> An Egyptian-fraction expansion writes a rational number as a sum of distinct unit fractions. The formalization proves that every $a/b$ with $1\le a<b$ has such an expansion and that the largest minimum length at denominator $b$ is $\Theta(\log\log b)$. If $F(k)$ counts exact $k$-term expansions of $1$, it also proves $\log\log F(k)=\Theta(k)$ and bounds every denominator in such an expansion.
>
> Every integer $m\ge2$ occurs as a denominator in an expansion of $1$, with length eventually at most $(257/\log2+\varepsilon)\log\log m$ for every $\varepsilon>0$; padding can preserve that denominator. If $v(k)$ is the least integer at least $2$ absent from all exact $k$-term expansions of $1$, then eventually $e^{e^{k/600}}\le v(k)\le1+k^{2^{k-1}}$, and $\liminf_{k\to\infty}\log\log v(k)/k\ge\log2/257$.

**Formal statement**

```lean
theorem egyptian_length_is_minimum :
    ∀ a b : ℕ, 1 ≤ a → a < b →
  (∃ n : Fin (egyptianLength a b) → ℕ,
    IsEgyptianExpansion ((a : ℚ) / (b : ℚ)) n) ∧
  (∀ k : ℕ, (∃ n : Fin k → ℕ,
    IsEgyptianExpansion ((a : ℚ) / (b : ℚ)) n) →
    egyptianLength a b ≤ k)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F103: Exact derandomization of logarithmic space: $`\mathsf L=\mathsf{RL}=\mathsf{BPL}`$

Challenge file: [lean/ComparatorChallenges/LogspaceEquality.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/LogspaceEquality.lean). Theorem: `exact_logarithmic_space_derandomization`.

**Prose**

> The formalization proves $\mathsf L=\mathsf{RL}=\mathsf{BPL}$ for binary languages in an explicit Turing-machine model with logarithmic workspace. The randomized classes use polynomial time: $\mathsf{RL}$ never accepts a no-instance and accepts a yes-instance with probability at least $1/2$, while $\mathsf{BPL}$ has acceptance probability at least $2/3$ on yes-instances and at most $1/3$ on no-instances. Thus bounded-error randomness does not enlarge deterministic logarithmic space in this model.
>
> The selected theorem asserts equality of the language classes. The paper's explicit compiler and numerical running-time bounds are not separately stated in this Comparator target.

**Formal statement**

```lean
theorem exact_logarithmic_space_derandomization :
    L = RL ∧ RL = BPL
```

- [ ] determined
- [ ] underdetermined

Note: 

## F115: Sampling and counting contingency tables with arbitrary margins

Challenge file: [lean/ComparatorChallenges/ContingencyTables.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ContingencyTables.lean). Theorem: `boundedSampling`.

**Prose**

> The formalization gives an exact uniform sampler for nonnegative integer contingency tables with arbitrary prescribed row and column sums having equal totals. It terminates almost surely, every halted output is feasible, and each table has exactly the uniform limiting probability. Expected bit complexity is polynomial in the dimensions and the binary length of the margins.
>
> It also gives a sampler with a fixed polynomial time bound on every execution whose total-variation error is at most $2^{-k}$ for requested precision $k\ge1$. The same Comparator file includes the companion approximation scheme for counting tables with individual cell bounds.
>
> The formalization gives a fully polynomial randomized approximation scheme for counting nonnegative integer matrices with prescribed row sums, column sums, and individual entry bounds. Both dimensions may vary, the margins and bounds are binary encoded, and zero entry bounds are allowed. For rational $0<\varepsilon,\delta<1$, the algorithm returns a nonnegative estimate with relative error at most $\varepsilon$ with probability at least $1-\delta$, and returns zero on every execution when no table exists.
>
> The running time is polynomial in the encoded input size, $\varepsilon^{-1}$, and $\log(\delta^{-1})$ on every random tape. The same Comparator file also contains the companion sampling results for tables without cell bounds.

**Formal statement**

```lean
theorem boundedSampling : Algorithms.BoundedSamplingStatement
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def BoundedSamplingStatement : Prop :=
  ∃ (A : Machine) (C d : ℕ), 0 < C ∧
    ∀ (m n : ℕ) (r : Fin m → ℕ) (c : Fin n → ℕ),
      (∑ i, r i) = ∑ j, c j → ∀ k : ℕ, 1 ≤ k →
        let input := encodeSamplingInput r c k
        let t := C * (samplingSize n r k) ^ d
        (∀ bits : Fin t → Bool, ∃ X : Table r c, OutputsTable A input bits X.val) ∧
        (∑ X : Table r c,
          |tableMass A input t X.val - (Fintype.card (Table r c) : ℝ)⁻¹|) / 2 ≤
            ((2 : ℝ) ^ k)⁻¹
```

- [ ] determined
- [ ] underdetermined

Note: 

## F144: Banach’s simple Lebesgue-spectrum problem

Challenge file: [lean/ComparatorChallenges/ThreeTorus.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ThreeTorus.lean). Theorem: `simple_lebesgue_spectrum`.

**Prose**

> Banach's simple Lebesgue-spectrum problem asks for a probability-preserving transformation with simple Lebesgue spectrum on its mean-zero $L^2$ space. The formalization constructs a smooth volume-preserving diffeomorphism of the three-torus with this property. It gives a real-valued cyclic vector whose integer iterates form an orthonormal basis of the entire mean-zero space, and an isometric identification under which the Koopman operator becomes multiplication by the coordinate function on the circle. The transformation is also ergodic.

**Formal statement**

```lean
theorem simple_lebesgue_spectrum : MainConclusion
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def MainConclusion : Prop :=
  ∃ T : Equiv.Perm Torus,
    Smooth T ∧ Smooth T.symm ∧ MeasurePreserving T μ μ ∧
    ∃ f : H₀, IsReal f ∧
    ∃ v : ℤ → H₀,
      (∀ n : ℤ, ∀ᵐ x ∂μ, (v n).1 x = f.1 ((T ^ n) x)) ∧
      Orthonormal ℂ v ∧
      Dense (Submodule.span ℂ (Set.range v) : Set H₀) ∧
      Ergodic T μ ∧
      ∃ W : H₀ ≃ₗᵢ[ℂ] CircleH,
        ∀ g : H₀, ∃ h : H₀,
          (∀ᵐ x ∂μ, h.1 x = g.1 (T x)) ∧
          (∀ᵐ z ∂(AddCircle.haarAddCircle (T := (1 : ℝ))),
            W h z = fourier 1 z * W g z)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F174: Deterministic construction of strong thin spanning trees

Challenge file: [lean/ComparatorChallenges/StrongThinTree.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/StrongThinTree.lean). Theorem: `strongThinTree`.

**Prose**

> The strong thin-tree conjecture asks for spanning trees that cross every cut sparsely relative to the original graph. The formalized result gives one absolute constant $C>0$ such that every finite loopless $k$-edge-connected multigraph with at least two vertices has a spanning tree crossing each nontrivial cut at most $(C/k)$ times the original cut size. Parallel edges remain distinct. No numerical value of $C$ or construction algorithm is asserted.
>
> The strong thin-tree problem asks for a spanning tree that crosses every cut sparsely relative to the original graph. The formalization gives one deterministic polynomial-time algorithm and an absolute constant $C>0$ such that a finite $k$-edge-connected loopless multigraph yields a spanning tree using at most a $C/k$ fraction of the edges of every cut. The input may encode parallel-edge multiplicities in binary, and the running time is polynomial in that binary input length.

**Formal statement**

```lean
theorem strongThinTree : MainStatement
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def MainStatement : Prop :=
  ∃ C : ℝ, 0 < C ∧ ∀ (k : ℕ), 1 ≤ k → ∀ (n m : ℕ), 2 ≤ n →
    ∀ G : MultiGraph n m, G.EdgeConnected k →
      ∃ T : Finset (Fin m), G.SpanningTree T ∧
        ∀ S : Finset (Fin n), S.Nonempty → S ≠ Finset.univ →
          ((G.cut T S).card : ℝ) ≤ (C / (k : ℝ)) * (G.cut Finset.univ S).card
```

- [ ] determined
- [ ] underdetermined

Note: 

## F186: Uniform influence and sharp thresholds for graph and hypergraph properties

Challenge file: [lean/ComparatorChallenges/SharpThreshold.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/SharpThreshold.lean). Theorem: `sharp_threshold_width`.

**Prose**

> The Friedgut–Kalai sharp-threshold conjecture concerns how quickly a nontrivial increasing graph property appears in the independent-edge random graph. For every $n\ge2$, every such property invariant under vertex relabeling, and $0<\varepsilon<1/2$, the formalization proves that the edge-probability interval between probabilities $\varepsilon$ and $1-\varepsilon$ has width at most $2^{19}\log(1/(2\varepsilon))/(\log n)^2$. The constant is uniform over the graph property, $n$, and $\varepsilon$.

**Formal statement**

```lean
theorem sharp_threshold_width :
    ∀ (n : ℕ) (f : GraphConfig n → Bool) (ε : ℝ),
      2 ≤ n → VertexInvariant f → IncreasingGraphProperty f →
      NontrivialGraphProperty f → 0 < ε → ε < (1 / 2 : ℝ) →
      graphQuantile (1 - ε) f - graphQuantile ε f ≤
        ((2 : ℝ) ^ 19 / (Real.log (n : ℝ)) ^ 2) * Real.log (1 / (2 * ε))
```

- [ ] determined
- [ ] underdetermined

Note: 

## F190: Polynomial removal fails for ordered binary matrices

Challenge file: [lean/ComparatorChallenges/MatrixRemoval.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/MatrixRemoval.lean). Theorem: `no_polynomial_removal_bound`.

**Prose**

> The formalized result disproves a polynomial removal bound for one explicit $66\times66$ binary pattern. For every $c,C>0$, there is an $n\times n$ binary matrix at normalized edit distance at least $\varepsilon>0$ from being pattern-free but with fewer than $c\varepsilon^C n^{132}$ induced ordered copies. Row and column indices are independently increasing, and every zero and one entry must match. The construction gives an explicit sequence of such matrices, allowing edits in both directions.

**Formal statement**

```lean
theorem no_polynomial_removal_bound :
    ∀ c C : ℝ, 0 < c → 0 < C →
  ∃ n : ℕ, 1 ≤ n ∧
    ∃ ε : ℝ, 0 < ε ∧ ε < 1 ∧
      ∃ A : BinaryMatrix n,
        fixedDistance A ≥ ε ∧
        (copyCount fixedH A : ℝ) <
          c * Real.rpow ε C * ((n : ℝ) ^ 132)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F231: The free uniform spanning forest is a factor of IID

Challenge file: [lean/ComparatorChallenges/StronglyRayleighDPP.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/StronglyRayleighDPP.lean). Theorem: `finite_strongly_rayleigh_response`.

**Prose**

> The formalization proves that the free uniform spanning forest is a factor of independent identically distributed vertex labels on every infinite connected locally finite simple unweighted graph. One Borel equivariant rule works for all such graphs and uses no distinguished root.
>
> The linked supplements also give equivariant IID sampling for invariant strongly Rayleigh laws on countable groups and existence, uniqueness, and IID-factor results for determinantal laws with Hermitian positive-contraction kernels on countable index sets. These group results require neither amenability nor finite generation, and the kernels need not be trace class.

**Formal statement**

```lean
theorem finite_strongly_rayleigh_response :
    ∀ (F : Type u_1) [Fintype F] [Nonempty F] (μ : ProbabilityMeasure (F → Bool)),
      StronglyRayleighFinite μ →
        (∀ (i j : F) (h : F → ℝ),
          HasDerivAt (fun r : ℝ => tiltMean μ (coordinatePerturb h j r) i)
            (tiltCovariance μ h i j) 0) ∧
        (∀ (i : F) (h : F → ℝ),
          (∑ j : F, |tiltCovariance μ h i j|) ≤
              2 * tiltMean μ h i * (1 - tiltMean μ h i) ∧
            2 * tiltMean μ h i * (1 - tiltMean μ h i) ≤ (1 : ℝ) / 2) ∧
        (∀ (i : F) (h h' : F → ℝ) (D : ℝ),
          0 ≤ D → (∀ j : F, |h j - h' j| ≤ D) →
            |tiltMean μ h i - tiltMean μ h' i| ≤ D / 2)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F238: Optimal logarithmic mixing of the Thorp shuffle

Challenge file: [lean/ComparatorChallenges/ThorpFirstReciprocal.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ThorpFirstReciprocal.lean). Theorem: `first_reciprocal_main`.

**Prose**

> The formalization proves optimal-order mixing of the Thorp shuffle on $2^d$ cards. After $1600d$ complete shuffles, the full permutation law converges in total variation to uniform as $d\to\infty$, uniformly over initial decks. Together with the support lower bound of $2d-O(1)$, this gives mixing time $\Theta(d)=\Theta(\log(2^d))$.
>
> The linked supporting results include frame and conditional-list estimates, regular trace and spectral bounds, signed moments, and full-density $L^2$ control. They also bound reciprocal Specht-dimension sums and give the eight-block Fourier estimate used in the mixing argument.
>
> The formalized supporting result turns bounds on partial-permutation cosets into Fourier bounds. Partition a finite set into $b\ge1$ nonempty blocks, and let $f\ge0$ be a subprobability weight on its symmetric group whose left-coset masses for each block subgroup are at most $B$. For every irreducible unitary representation of dimension $D$ and every $u>0$, both the squared Hilbert–Schmidt norm and squared operator norm of its Fourier transform are at most $bB\,C(u)D^{-1+(u+2)/b}$, where $C(u)$ is the stated symmetric-group degree constant.
>
> The paper's asymptotic conclusion about the product of two random permutations is outside this selected finite estimate.
>
> The formalized results give averaged conditional mixing for half-permutations in the revealed-path model and full-deck mixing for the Thorp shuffle. In particular, the full-deck total-variation distance tends to zero after $16040400d$ steps on $2^d$ cards, uniformly over deterministic initial decks. The conditional estimate is averaged over the actual outside-path law, rather than asserted for each individual environment. The formalization also includes the associated overlay, reset minorization, and two-color conditional constructions.
>
> The formalization covers nine routing and representation estimates for Thorp sweeps: adaptive operator and fourth-trace bounds, Casimir moments, dense truncation, sparse contact, harmonic-cycle contraction, smoothing, and three tail or sparse-saving estimates. They bound routing-density deviations and Fourier operators in dense and sparse regimes, including exponential savings in the level scale and representation dimension.
>
> The conditional high-height estimate requires a sufficiently large cutoff height $J$ that exceeds twice the number $s$ of coordinates in the fixed low block, so $J>2s$. These are the earlier nine statements associated with the paper; its changed later statements and six other result blocks are outside this scope.
>
> The formalization proves uniform representation bounds for one coordinate sweep of the Thorp shuffle. For each irreducible representation of dimension $D$, it chooses a weight between $D^{3/4}$ and $D$ and a Schatten exponent bounded by one absolute constant so that the weighted Schatten moment is at most one. The sweep's operator norm is consequently at most $D^{-c}$ for one absolute $c>0$.
>
> The supporting row–column estimate bounds the total squared overlap over all multiplicity copies on an occupied board, with explicit dependence on the row and column representation dimensions, the global dimension, the number of missing cells, and the number of rows or columns containing the global Young diagram. The paper's full physical-mixing conclusion is outside these selected representation estimates.
>
> The formalization proves a uniform trace-smoothing estimate for coordinate sweeps of the Thorp shuffle on $2^d$ cards. One absolute sweep parameter works for every $d\ge1$: the regular trace is at most $1+(2^d)^{-10}$, and the full permutation law after the corresponding fixed number of sweeps is within $\tfrac12(2^d)^{-5}$ of uniform in total variation, for every initial deck. Thus the selected upper bound uses $O(d)$ physical shuffles.
>
> The formalized result is the weighted compatibility theorem for balanced $A\times D$ rectangles, with $n=AD$ and $\sqrt n/2\le A,D\le2\sqrt n$. For arbitrary nonnegative weights on the row and column permutation groups, the normalized compatibility average is bounded by $\exp(C_0n^{54/100})$ times the product of the marginal $L^{1/\theta}$ factors, where $\theta=1-L/\log\sqrt n>0$ and the constants are absolute. Compatibility means injectivity in every original column. The bounded regular-moment and other moment/rank conclusions are not included.
>
> The formalization gives signed representation estimates for coordinate sweeps of the Thorp shuffle. For every signed occurrence of a Young diagram of size $2^d$, it bounds the logarithm of a fixed-order weighted sweep moment by a small multiple of the signed partition entropy plus an explicit remainder-size budget. The moment order is uniform over the diagrams and decompositions after the two small coefficients are fixed.
>
> The linked supporting angle bound controls the overlap of row, column, and global signed-type projections on an occupied rectangle, with explicit entropy, dimension, and missing-cell factors. These selected estimates support the paper's full-density argument; the full $L^2$ and total-variation mixing conclusion is outside them.
>
> The formalized binary-sweep theorem gives a universal power contraction in every irreducible representation: for sufficiently large $d$, the averaged sweep on $2^d$ slots has operator norm at most $D^{-g}$ in representation dimension $D$, for some $g>0$. The sign expectation is zero, and a fixed number of independent sweeps approaches uniform in total variation from every initial deck. A separate conditional moment estimate covers allowed power-of-two grids and disjoint coordinate-respecting trajectories, with its stated feasibility premise. Physical-shuffle law identification is not included.
>
> The formalization proves the paper's strict four-row permanent inequality. There are constants $4/3<p<2$ and $\varepsilon>0$ such that every probability law on $S_4$ within total-variation distance $\varepsilon$ of uniform, and with exactly uniform coordinate marginals, satisfies the permanent bound by the product of the four $L^p$ row norms for every nonnegative matrix. The exponent and neighborhood are uniform over those laws. The Thorp mixing consequence is outside this selected statement.

**Formal statement**

```lean
theorem first_reciprocal_main :
    (BddAbove (Set.range (fun n : {n : ℕ // 1 ≤ n} => reciprocalFirst n.val)) ∧
    (∀ n : ℕ, 1 ≤ n → reciprocalFirst n ≤ C1) ∧
    Tendsto exceptionalFirst atTop (nhds 0)) ∧
    (∀ (d : ℕ) (_hd : 3 ≤ d)
    (e : Position d ≃ Fin 8 × Fin (2 ^ (d - 3)))
    {E : Type uE} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E]
    (ρ : Representation ℂ (Equiv.Perm (Position d)) E)
    [Representation.IsIrreducible ρ]
    (_ : ∀ g x y, ⟪ρ g x, ρ g y⟫_ℂ = ⟪x, y⟫_ℂ)
    (ν : Equiv.Perm (Position d) → ℝ)
    (_ : ∀ g, 0 ≤ ν g) (_ : ∑ g, ν g = 1)
    (_ : ∀ (i : Fin 8) (g : Equiv.Perm (Position d)),
      ∑ h : Equiv.Perm (Fin (2 ^ (d - 3))),
          ν (g * Block.embedding e (Pi.mulSingle i h)) ≤
        4 * (Fintype.card (Equiv.Perm (Fin (2 ^ (d - 3)))) : ℝ) /
          Fintype.card (Equiv.Perm (Position d))),
    ‖LinearMap.toContinuousLinearMap (Fourier.integrated ρ (fun g => (ν g : ℂ)))‖ ≤
      Real.sqrt (32 * C1) * (Module.finrank ℂ E : ℝ) ^ (-5 / 16 : ℝ))
```

- [ ] determined
- [ ] underdetermined

Note: 

## F243: Separating choiceless counting from polynomial time and witnessed choice

Challenge file: [lean/ComparatorChallenges/ChoicelessPolynomialTime.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ChoicelessPolynomialTime.lean). Theorem: `main`.

**Prose**

> The formalized result separates polynomial time from choiceless polynomial time with counting. It gives an explicit query on finite structures with eight relations that is invariant under isomorphism and decidable in polynomial time, but is not definable in the stated hereditarily finite-set language with cardinality and polynomial bounds on stages and intermediate objects. The query applies to all finite inputs without a promise. The separate witnessed-symmetric-choice result is not included.
>
> The formalization proves that witnessed symmetric choice strictly increases the expressive power of choiceless polynomial time with counting. It constructs one fixed sentence with exactly one witnessed-choice occurrence that gives a Boolean answer on every finite input, while no sentence of the original counting formalism defines the same class of inputs.

**Formal statement**

```lean
theorem main :
    (∀ (A B : Type) [Fintype A] [Fintype B] (S : Input A) (T : Input B),
      S.Iso T → (S.query ↔ T.query)) ∧
    OrdinaryPolynomialTime ∧
    ¬ FullCPT.EvaluationDefinable (fun {_} [_] I => I.query)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F245: Weak normalization implies strong normalization in pure type systems

Challenge file: [lean/ComparatorChallenges/TypeSystemNormalization.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/TypeSystemNormalization.lean). Theorem: `weak_implies_strong`.

**Prose**

> The formalization proves the $\beta$-Barendregt–Geuvers–Klop conjecture for pure type systems: if every legal expression in every valid context has some terminating $\beta$-reduction sequence, then every $\beta$-reduction sequence from every such expression terminates. Reduction is allowed inside type annotations, and the specification may have arbitrary sorts and nonfunctional axioms or rules.

**Formal statement**

```lean
theorem weak_implies_strong {S : Type u} (P : Specification S)
    (h : SystemWeaklyNormalizing P) : SystemStronglyNormalizing P
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def SystemStronglyNormalizing {S : Type u} (P : Specification S) : Prop :=
  ∀ Γ, ValidContext P Γ → ∀ M, Legal P Γ M → StronglyNormalizing M
```

- [ ] determined
- [ ] underdetermined

Note: 

## F246: Cannon's conjecture

Challenge file: [lean/ComparatorChallenges/CannonGeometricAction.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/CannonGeometricAction.lean). Theorem: `cannon`.

**Prose**

> Cannon's conjecture asks whether a hyperbolic group with boundary homeomorphic to the two-sphere acts geometrically on hyperbolic three-space. The formalization proves that such a group admits an isometric action on $\mathbb H^3$ that is proper and cocompact and has finite kernel. Hyperbolicity is expressed through uniformly thin geodesic triangles in a Cayley graph, and the boundary hypothesis is a homeomorphism with $S^2$.

**Formal statement**

```lean
theorem cannon (G : Type u) [Group G] [TopologicalSpace G] [DiscreteTopology G]
    (D : CayleyData G) (hthin : D.ThinTriangles)
    (hsphere : Nonempty (Boundary D ≃ₜ SphereTwo)) :
    ∃ ρ : G →* H3Isom, ProperAction ρ ∧ CocompactAction ρ ∧
      (ρ.ker : Set G).Finite
```

- [ ] determined
- [ ] underdetermined

Note: 

## F273: The entropy photon-number inequality

Challenge file: [lean/ComparatorChallenges/EntropyPhotonNumber.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/EntropyPhotonNumber.lean). Theorem: `entropy_photon_number_inequality`.

**Prose**

> The formalization proves the entropy photon-number inequality for two independent bosonic inputs with finite mean energy and any finite positive number $n$ of modes. Write $N(\rho)=g^{-1}(S(\rho)/n)$, where $S$ is von Neumann entropy and $g(x)=(x+1)\log(x+1)-x\log x$ is the thermal entropy per mode. For a beam splitter of transmissivity $0\le\eta\le1$, its output satisfies $N(\rho_C)\ge\eta N(\rho_A)+(1-\eta)N(\rho_B)$.
>
> Entanglement among modes within either input is allowed. The thermal-attenuator minimum-output-entropy and broadcast-capacity consequences in the paper are outside this selected inequality.

**Formal statement**

```lean
theorem entropy_photon_number_inequality
    (n : ℕ) (hn : 1 ≤ n) (ρA ρB ρC : State n)
    (hA : FiniteEnergy ρA) (hB : FiniteEnergy ρB)
    (η : ℝ) (hη : η ∈ Set.Icc 0 1)
    (hC : IsBeamSplitterOutput η ρA ρB ρC) :
    η * gInv (entropy ρA / n) + (1 - η) * gInv (entropy ρB / n) ≤
      gInv (entropy ρC / n)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F275: QMA-hardness of continuum Coulomb energy

Challenge file: [lean/ComparatorChallenges/ContinuumCoulombHardness.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ContinuumCoulombHardness.lean). Theorem: `unit_coulomb_qmaHard`.

**Prose**

> The formalization proves QMA-hardness of approximating the electronic Coulomb spectral infimum in three-dimensional continuum space when positive integer nuclear charges are encoded in binary. The instances have distinct rational nuclear positions and a unary electron count, and the energy ranges over antisymmetric continuum states and all spin sectors. A deterministic polynomial-time many-one reduction produces the promise gap with threshold separation at least one, while keeping the complete output length polynomial. The same Comparator file also contains the companion unit-charge result.
>
> The formalization proves QMA-hardness of approximating the electronic ground-energy infimum for clamped unit-charge nuclei in the full spinful fermionic continuum. The reduction is deterministic and polynomial time, with rational nuclear positions and separated rational energy thresholds. No orbital basis, magnetic field, additional external potential, or binding premise is part of the input.
>
> The same Comparator file also includes the companion hardness result when positive integer nuclear charges are encoded in binary.

**Formal statement**

```lean
theorem unit_coulomb_qmaHard : QMAHard unitCoulombCodec.encode unitCoulombPromise
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def QMAHard {α : Type} (encoding : α → BitString) (Q : PromiseProblem α) : Prop :=
  ∀ P : PromiseProblem BitString, InQMA P → Nonempty (PolynomialManyOne id encoding P Q)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F277: Threshold repetition for entangled games

Challenge file: [lean/ComparatorChallenges/EntangledGames.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/EntangledGames.lean). Theorem: `threshold_parallel_repetition`.

**Prose**

> The formalization gives exponential threshold parallel repetition for every finite two-player game with arbitrary correlated questions. If its finite-dimensional entangled value is $v<1$, its answer sets are $A,B$, and $0<\delta<1-v$, then the probability of winning at least the fraction $v+\delta$ of $k$ repetitions is at most $\exp(-\kappa\delta^{13}k/(1+\log(|A||B|)))$ for one universal $\kappa>0$. The bound applies to every joint finite-dimensional strategy and to their supremum, without assuming attainment. The separate distribution-dependent cubic bound is outside this scope.

**Formal statement**

```lean
theorem threshold_parallel_repetition :
    ∃ κ₀ : ℝ, 0 < κ₀ ∧
      ∀ (x y a b : ℕ) (G : Game x y a b), entangledValue G < 1 →
      ∀ (δ : ℝ), 0 < δ → δ < 1 - entangledValue G →
      ∀ (k : ℕ), 1 ≤ k →
        (∀ S : RepeatedStrategy x y a b k,
          thresholdProbability G δ S ≤
            Real.exp (-κ₀ * δ ^ 13 / (1 + Real.log (((a + 1) * (b + 1) : ℕ) : ℝ)) * k)) ∧
        thresholdValue (k := k) G δ ≤
          Real.exp (-κ₀ * δ ^ 13 / (1 + Real.log (((a + 1) * (b + 1) : ℕ) : ℝ)) * k)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F327: Markov type characterizes superreflexivity

Challenge file: [lean/ComparatorChallenges/MarkovType.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/MarkovType.lean). Theorem: `hasNontrivialMarkovType_iff_hasEquivalentUCNorm`.

**Prose**

> The formalized result proves that a real Banach space has nontrivial Markov type exactly when it admits an equivalent uniformly convex norm, hence exactly when it is superreflexive. Nontrivial Markov type means a uniform Markov-type bound for some exponent $p>1$ over all finite stationary reversible chains and all positive times. The exponent and equivalent norm may depend on the space, and the zero space is included. Additional formalized consequences concern uniformly smooth renormings and reflexivity of finitely representable spaces.

**Formal statement**

```lean
theorem hasNontrivialMarkovType_iff_hasEquivalentUCNorm [CompleteSpace X] :
    HasNontrivialMarkovType X ↔ HasEquivalentUCNorm X
```

- [ ] determined
- [ ] underdetermined

Note: 

## F331: Reflexive midpoint convexity and diamond distortion

Challenge file: [lean/ComparatorChallenges/ForestSpace.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/ForestSpace.lean). Theorem: `main_theorem`.

**Prose**

> The paper constructs a Banach space whose midpoint geometry is asymptotically uniformly convex even though no equivalent norm is asymptotically uniformly convex in the usual one-sided sense. The formalization proves that the full dual of the specified segment-norm completion is infinite-dimensional, separable, and reflexive; its averaged midpoint modulus is at least $\sqrt{1+t^2/12}-1$ for every $t>0$, while every equivalent norm fails asymptotic uniform convexity. It also proves that an embedding of a depth-$k$ countably branching diamond has distortion at least $\sqrt{1+k/12}$.
>
> The general-forest and word-forest results use the closed span of the coordinate functionals. Their conclusions retain the finite-ancestor and equivalent-norm hypotheses, including the scale $\alpha/(2\beta)$ when $0<\alpha\le\beta$ and the new norm lies between $\alpha$ and $\beta$ times the original norm; they do not identify that span with the full dual or assert reflexivity for every forest.
>
> The paper controls midpoint lenses in Banach spaces defined by tree-segment norms. The formalization proves the following estimate in both the full dual of the finite-height forest space and the coordinate predual of the infinite-tree space. If $x$ is supported on a finite ancestral set $H$, $R\ge0$, and $\|x+y\|,\|x-y\|\le R$, then the part of $y$ outside $H$ has norm at most $2\sqrt{R^2-\|x\|^2}$.
>
> The formalization also covers selected consequences for averaged midpoint moduli and separated families of vectors, together with reflexivity and renorming obstructions. This scope concerns the segment-space results; the companion results on diamond energies remain separate.
>
> The paper studies embeddings of countably branching diamond graphs into Banach spaces built from tree segments. The formalization proves that every embedding of the depth-$k$ diamond with distortion $D$, at any positive scale, satisfies $1+k/4\le D^2$ in either of two spaces: the full dual of the completed finite-height forest space and the closed coordinate span in the dual of the infinite-tree space. The bound applies to all pairs of vertices and is unconditional.
>
> The formalization also contains selected graph deductions under explicit companion assumptions. Twenty-two of those companion inputs are assumed in these deductions; the diamond distortion bound above does not require them.
>
> The paper exhibits a real $L_1$ subspace with positive averaged midpoint convexity but no equivalent asymptotically uniformly convex norm. For every closed infinite-dimensional subspace whose unit ball is precompact in measure and which has the Daugavet property, the formalization computes the moduli at every unit vector: the averaged midpoint modulus is $\max(t/2,t-1)$ and the usual one-sided asymptotic modulus is $\max(0,t-2)$ for every $t>0$. The same formulas hold after taking the infimum over unit vectors, and every equivalent norm fails asymptotic uniform convexity.
>
> The formalization also constructs such a subspace on a countable product of unit intervals and proves that it has the stated measure-precompactness and Daugavet properties, so the modulus formulas apply to an actual example.
>
> The paper constructs Banach spaces from bounded tree potentials and path costs to separate averaged midpoint convexity from asymptotic uniform convexity. For the specified tree-potential completions, the formalization proves completeness, separability, infinite dimension, and an averaged midpoint modulus of at least $\sqrt{1+t^2/4}-1$ for $0<t<1$. No space linearly isomorphic to one of these completions is asymptotically uniformly convex.
>
> The formalization also covers selected path-cost duality and comparison results, clipping and energy estimates, and further renorming obstructions. These retain their stated support, head, and tail hypotheses; the remaining auxiliary assertions of the paper are outside this scope.
>
> The paper forms a real $L_1$ space from the closed span of products of independent multipliers along tree paths. For a positive, nonconstant multiplier of mean one and finite second moment, the formalization proves that this space is infinite-dimensional and has no equivalent asymptotically uniformly convex norm.
>
> For every $t>0$, the averaged midpoint modulus nevertheless has explicit positive lower bounds. If $G$ is a standard real Gaussian, the exponential-multiplier bound is $\frac{7t}{480}\mathbb E[(|G|-20/t)_+]$, where $u_+=\max(u,0)$. For squared-Gaussian multipliers, the bounds are $\frac18\Pr(|G|\ge4\sqrt2(2+\sqrt2)/t)$ and $\frac14\Pr(|G|\ge8\sqrt6/t)$.
>
> The paper constructs three Banach spaces from recursive tree potentials: a root-sum space, a zero-root space, and a joined space. The formalization proves that all three are infinite-dimensional and have no equivalent asymptotically uniformly convex norm. The root-sum and joined spaces have averaged midpoint modulus at least $t^3/128$ for $0<t<1$, and the root-sum modulus is positive for every $t>0$. The zero-root estimate retains its finite ancestral support and tail hypotheses, and the zero-root and joined spaces are reflexive.
>
> The formalization also covers a separated-midpoint result for the joined space and a variable-exponent model with its recursive norm, duality, projections, renorming obstruction, and sixth- and third-order stability estimates. The separation, sequence, support, and head assumptions in these results are essential parts of their statements.

**Formal statement**

```lean
theorem main_theorem :
    (¬FiniteDimensional ℝ (FullDual Vertex)) ∧
    TopologicalSpace.SeparableSpace (FullDual Vertex) ∧
    Reflexive (FullDual Vertex) ∧
    (∀ (α β : ℝ) (R : EquivalentNorm (FullDual Vertex) α β), ¬IsAUC R.N) ∧
    (∀ t : ℝ, 0 < t →
      Real.sqrt (1+t^2/12)-1 ≤ averageModulus (FullDual Vertex) norm t) ∧
    (∀ (k : ℕ) (f : (Diamond.diamond k).V → FullDual Vertex) (C : ℝ),
      Diamond.EmbeddingBound k f C → Real.sqrt (1+(k:ℝ)/12) ≤ C)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F354: The isoperimetric profile of the cubic three-torus

Challenge file: [lean/ComparatorChallenges/CubicTorus.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/CubicTorus.lean). Theorem: `unit_cubic_isoperimetric`.

**Prose**

> The formalization determines the isoperimetric profile and all minimizers in the unit cubic flat three-torus. At every volume $0<V<1$, a minimizer exists, and the minimizers, up to null-set changes, are exactly balls, circular tubes about shortest closed geodesics, coordinate slabs, and their complements in the appropriate volume ranges.
>
> The classification includes all equality cases at the transition volumes $4\pi/81$ and $1/\pi$, and every minimizer has the stated candidate-profile perimeter.

**Formal statement**

```lean
theorem unit_cubic_isoperimetric (V : ℝ) (hV : V ∈ Ioo 0 1) :
    (∃ E : Set Torus, IsMinimizerAt V E) ∧
    (∀ E : Set Torus, IsMinimizerAt V E →
      perimeter E = ENNReal.ofReal (candidateProfile V)) ∧
    (∀ E : Set Torus, IsMinimizerAt V E ↔ StandardRegionAt V E)
```

- [ ] determined
- [ ] underdetermined

Note: 

## F365: Joint metric and connection recovery from one boundary patch

Challenge file: [lean/ComparatorChallenges/Conductivity.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/Conductivity.lean). Theorem: `main_nonuniqueness`.

**Prose**

> The Calderón inverse problem asks whether boundary measurements determine an interior conductivity. The formalized result gives nonuniqueness for bounded measurable scalar conductivities on the ball $B(0,3)\subset\mathbb R^3$: two uniformly positive conductivities differ on a set of positive volume, equal $1$ near the boundary, and have the same full weak Dirichlet-to-Neumann operator. Weak solutions exist uniquely for every boundary trace.

**Formal statement**

```lean
theorem main_nonuniqueness : MainStatement
```

The statement is a named proposition defined in the challenge file. Judge its definition:

```lean
def MainStatement : Prop :=
  ∃ (γ₀ γ₁ : R3 → ℝ) (c C : ℝ) (Λ : DNOperator),
    0 < c ∧ c < C ∧
    Measurable γ₀ ∧ Measurable γ₁ ∧
    MemLp γ₀ ∞ ballMeasure ∧ MemLp γ₁ ∞ ballMeasure ∧
    (∀ᵐ x ∂ballMeasure, c ≤ γ₀ x ∧ γ₀ x ≤ C) ∧
    (∀ᵐ x ∂ballMeasure, c ≤ γ₁ x ∧ γ₁ x ≤ C) ∧
    EqualOneNearBoundary γ₀ ∧ EqualOneNearBoundary γ₁ ∧
    0 < ballMeasure {x | γ₀ x ≠ γ₁ x} ∧
    IsDirichletToNeumann γ₀ Λ ∧ IsDirichletToNeumann γ₁ Λ
```

- [ ] determined
- [ ] underdetermined

Note: 
