# ADR-DISCOVERY-071: Rule 30 Periodic Word Exclusion Engine

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-23

## Context
A central open challenge in the Wolfram Rule 30 prize problems is determining whether the center column can become periodic, or if specific periodic sequences $w$ can emerge in localized spatial configurations. Generating brute-force state trajectories suffers from exponential state explosion ($2^N$). Formal mathematical pruning requires proving that certain words $w = 10^q$ are systematically excluded by the cellular automaton's local update algebra.

## Architectural Decision
We implement **`Rule30PeriodicWordExclusionEngine`** in `python/discovery/rule30_word_exclusion.py`:
1. **Jen's Theorem Contradiction Propagation**:
   - Exploits left-cone speed-1 propagation where $s_{i, t+1} = s_{i-1, t} \oplus (s_{i, t} \lor s_{i+1, t})$.
   - Traces deterministic pre-image constraints backwards to detect algebraic parity contradictions.
2. **Periodic Word Target Auditing**:
   - Encapsulates target word candidates $w \in \{0, 1\}^L$ and evaluates relaxed finite strip realizations.
3. **Formal Contradiction Certification**:
   - Produces formal mathematical certificates demonstrating impossibility of infinite periodic extension for target words.

## Consequences
- Reduces search spaces prior to Lean 4 formalization.
- Directly feeds `Rule30ReasoningBridge` (ADR-DISCOVERY-072).
