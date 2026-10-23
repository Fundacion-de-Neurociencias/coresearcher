import Mathlib

/-!
# Plasma p-tau217 Two-Cutoff Clinical Decision Rule: Formal Verification

Biomedical showcase case for CoResearcher (python/discovery/ptau217_cutoff_case.py).
Sources: Palmqvist et al. 2024 (PMID: 39068545); Ashton et al. 2024 (PMID: 38252443).

Status: ILLUSTRATIVE / THEOREM_SPECIFICATION (aligned with verified Python Z3 assumptions).

The clinical decision rule defines:
- c_low : ℝ, lower cutoff for rule-out zone
- c_high : ℝ, upper cutoff for rule-in zone
- ptau : ℝ, plasma p-tau217 biomarker concentration
- clearance_factor : ℝ, renal clearance scaling factor (> 1 in renal impairment)
- amyloid : ℕ, amyloid status (0 = negative, 1 = positive)

Theorems:
* `rule_out_sound`: with ordered cutoffs, biomarker separation and preserved renal clearance,
  ptau ≤ c_low implies amyloid = 0.
* `rule_in_sound`: under biomarker separation and preserved renal clearance,
  ptau ≥ c_high implies amyloid = 1.
-/

namespace Ptau217Cutoff

/-- Two-cutoff decision rule parameters and physiological assumptions -/
structure BiomarkerProfile where
  c_low : ℝ
  c_high : ℝ
  ptau : ℝ
  clearance_factor : ℝ
  amyloid : ℕ
  h_order : c_low < c_high
  h_amyloid_domain : amyloid = 0 ∨ amyloid = 1
  h_renal : clearance_factor = 1
  h_separation : (amyloid = 0 → (ptau / clearance_factor) ≤ c_low) ∧
                 (amyloid = 1 → (ptau / clearance_factor) ≥ c_high)

/-- Rule-out tier safety theorem: a patient with ptau ≤ c_low is amyloid negative under normal renal function -/
theorem rule_out_sound (p : BiomarkerProfile) (h_low : p.ptau ≤ p.c_low) : p.amyloid = 0 := by
  cases p.h_amyloid_domain with
  | inl h0 => exact h0
  | inr h1 =>
    have h_ge_scaled : (p.ptau / p.clearance_factor) ≥ p.c_high := p.h_separation.2 h1
    have h_cf : p.clearance_factor = 1 := p.h_renal
    rw [h_cf, div_one] at h_ge_scaled
    have h_contra : p.c_high ≤ p.c_low := le_trans h_ge_scaled h_low
    have h_lt : p.c_low < p.c_high := p.h_order
    exact False.elim (lt_irrefl p.c_low (lt_of_lt_of_le h_lt h_contra))

/-- Rule-in tier precision theorem: a patient with ptau ≥ c_high is amyloid positive under normal renal function -/
theorem rule_in_sound (p : BiomarkerProfile) (h_high : p.ptau ≥ p.c_high) : p.amyloid = 1 := by
  cases p.h_amyloid_domain with
  | inr h1 => exact h1
  | inl h0 =>
    have h_le_scaled : (p.ptau / p.clearance_factor) ≤ p.c_low := p.h_separation.1 h0
    have h_cf : p.clearance_factor = 1 := p.h_renal
    rw [h_cf, div_one] at h_le_scaled
    have h_contra : p.c_high ≤ p.c_low := le_trans h_high h_le_scaled
    have h_lt : p.c_low < p.c_high := p.h_order
    exact False.elim (lt_irrefl p.c_low (lt_of_lt_of_le h_lt h_contra))

end Ptau217Cutoff
