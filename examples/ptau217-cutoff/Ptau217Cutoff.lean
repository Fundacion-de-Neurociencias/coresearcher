import Mathlib

/-!
# Plasma p-tau217 Two-Cutoff Clinical Decision Rule: Formal Verification

Biomedical showcase case for CoResearcher (python/discovery/ptau217_cutoff_case.py).
Sources: Palmqvist et al. (2024), Ashton et al. (2024), Bateman et al. (2024).

The clinical decision rule defines:
- c_low : ℝ, lower cutoff for rule-out zone
- c_high : ℝ, upper cutoff for rule-in zone
- ptau : ℝ, plasma p-tau217 biomarker concentration
- amyloid : ℕ, amyloid status (0 = negative, 1 = positive)

Theorems:
* `rule_out_sound`: with ordered cutoffs and biomarker separation, ptau ≤ c_low implies amyloid = 0.
* `rule_in_sound`: with ordered cutoffs and monotonic risk, ptau ≥ c_high implies amyloid = 1.
-/

namespace Ptau217Cutoff

/-- Two-cutoff decision rule parameters and physiological assumptions -/
structure BiomarkerProfile where
  c_low : ℝ
  c_high : ℝ
  ptau : ℝ
  amyloid : ℕ
  h_order : c_low < c_high
  h_amyloid_domain : amyloid = 0 ∨ amyloid = 1
  h_separation : (amyloid = 0 → ptau ≤ c_low) ∧ (amyloid = 1 → ptau ≥ c_high)
  h_monotonic : ptau ≥ c_high → amyloid = 1

/-- Rule-out tier safety theorem: a patient with ptau ≤ c_low is amyloid negative -/
theorem rule_out_sound (p : BiomarkerProfile) (h_low : p.ptau ≤ p.c_low) : p.amyloid = 0 := by
  cases p.h_amyloid_domain with
  | inl h0 => exact h0
  | inr h1 =>
    have h_ge : p.ptau ≥ p.c_high := p.h_separation.2 h1
    have h_contra : p.c_high ≤ p.c_low := le_trans h_ge h_low
    have h_lt : p.c_low < p.c_high := p.h_order
    exact False.elim (lt_irrefl p.c_low (lt_of_lt_of_le h_lt h_contra))

/-- Rule-in tier precision theorem: a patient with ptau ≥ p.c_high is amyloid positive -/
theorem rule_in_sound (p : BiomarkerProfile) (h_high : p.ptau ≥ p.c_high) : p.amyloid = 1 := by
  exact p.h_monotonic h_high

end Ptau217Cutoff
