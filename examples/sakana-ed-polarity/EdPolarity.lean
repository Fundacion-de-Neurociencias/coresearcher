import Mathlib

/-!
# Error Diffusion polarity invariance, for any depth and width

Showcase case for CoResearcher (python/discovery/ed_polarity_case.py). Source of the claim: Sakana AI,
"Agentic Scientist", arXiv:2610.18933, appendix G.4 and Table 6.

Dual-stream network, width `w` per stream:

  p_i = f(p_{i-1} W_pp - n_{i-1} W_np + b_p),   n_i = f(n_{i-1} W_nn - p_{i-1} W_pn + b_n).

`sens … t` is the pair (dy/dp, dy/dn) of output sensitivities `t` layers below the output, computed by the chain
rule. Layer parameters are indexed by `t` counting down from the output, so every finite network is a prefix of the
sequences below and the theorems hold for every depth. `dp t k`, `dn t k` are f' at the units whose sensitivities
are `sens … t`; they are free reals, so the result holds for every activation with f' ≥ 0.

Theorems:
* `sens_polarized`: with non-negative weights and f' ≥ 0, dy/dp ≥ 0 and dy/dn ≤ 0 at every depth (polarity
  invariance), by induction on layers.
* `ed_sign_sufficiency`: the ED update -(σ τ) · pre · f'(post) · sign(e) has a non-positive product with the true
  gradient e · τ · pre · f'(post) · s(post) of the loss e²/2, for every weight at every depth.
-/

open Finset

namespace EdPolarity

variable {w : ℕ}

/-- Sensitivities of the output to the units of one layer: (p stream, n stream). -/
abbrev Sens (w : ℕ) := (Fin w → ℝ) × (Fin w → ℝ)

/-- One backward step of the chain rule through a dual-stream layer. `W j k` connects unit `j` of the layer below
to unit `k` of this layer; `dp`, `dn` are f' at this layer's units. -/
def back (Wpp Wnp Wnn Wpn : Fin w → Fin w → ℝ) (dp dn : Fin w → ℝ) (s : Sens w) : Sens w :=
  (fun j => (∑ k, s.1 k * dp k * Wpp j k) - ∑ k, s.2 k * dn k * Wpn j k,
   fun j => (∑ k, s.2 k * dn k * Wnn j k) - ∑ k, s.1 k * dp k * Wnp j k)

/-- Sensitivities `t` layers below the output, starting from `top`. -/
def sens (Wpp Wnp Wnn Wpn : ℕ → Fin w → Fin w → ℝ) (dp dn : ℕ → Fin w → ℝ) (top : Sens w) : ℕ → Sens w
  | 0 => top
  | t + 1 => back (Wpp t) (Wnp t) (Wnn t) (Wpn t) (dp t) (dn t) (sens Wpp Wnp Wnn Wpn dp dn top t)

/-- Polarity invariance at one layer. -/
def Polarized (s : Sens w) : Prop := (∀ k, 0 ≤ s.1 k) ∧ ∀ k, s.2 k ≤ 0

/-- The output y = p_L[i0]: sensitivity 1 to that unit, 0 to every other unit. -/
def outputTop (i0 : Fin w) : Sens w := (fun k => if k = i0 then 1 else 0, fun _ => 0)

theorem outputTop_polarized (i0 : Fin w) : Polarized (outputTop i0) := by
  refine ⟨fun k => ?_, fun k => le_refl 0⟩
  dsimp only [outputTop]
  split_ifs <;> norm_num

theorem back_polarized (Wpp Wnp Wnn Wpn : Fin w → Fin w → ℝ) (dp dn : Fin w → ℝ) (s : Sens w)
    (hWpp : ∀ j k, 0 ≤ Wpp j k) (hWnp : ∀ j k, 0 ≤ Wnp j k) (hWnn : ∀ j k, 0 ≤ Wnn j k)
    (hWpn : ∀ j k, 0 ≤ Wpn j k) (hdp : ∀ k, 0 ≤ dp k) (hdn : ∀ k, 0 ≤ dn k) (hs : Polarized s) :
    Polarized (back Wpp Wnp Wnn Wpn dp dn s) := by
  obtain ⟨hp, hn⟩ := hs
  refine ⟨fun j => ?_, fun j => ?_⟩
  · dsimp only [back]
    have h1 : 0 ≤ ∑ k, s.1 k * dp k * Wpp j k :=
      Finset.sum_nonneg fun k _ => mul_nonneg (mul_nonneg (hp k) (hdp k)) (hWpp j k)
    have h2 : ∑ k, s.2 k * dn k * Wpn j k ≤ 0 := by
      refine Finset.sum_nonpos fun k _ => ?_
      have h := mul_nonneg (mul_nonneg (neg_nonneg.mpr (hn k)) (hdn k)) (hWpn j k)
      linarith [h, show (-s.2 k) * dn k * Wpn j k = -(s.2 k * dn k * Wpn j k) by ring]
    linarith
  · dsimp only [back]
    have h1 : ∑ k, s.2 k * dn k * Wnn j k ≤ 0 := by
      refine Finset.sum_nonpos fun k _ => ?_
      have h := mul_nonneg (mul_nonneg (neg_nonneg.mpr (hn k)) (hdn k)) (hWnn j k)
      linarith [h, show (-s.2 k) * dn k * Wnn j k = -(s.2 k * dn k * Wnn j k) by ring]
    have h2 : 0 ≤ ∑ k, s.1 k * dp k * Wnp j k :=
      Finset.sum_nonneg fun k _ => mul_nonneg (mul_nonneg (hp k) (hdp k)) (hWnp j k)
    linarith

/-- Polarity invariance at every depth, by induction on layers. -/
theorem sens_polarized (Wpp Wnp Wnn Wpn : ℕ → Fin w → Fin w → ℝ) (dp dn : ℕ → Fin w → ℝ) (top : Sens w)
    (hWpp : ∀ t j k, 0 ≤ Wpp t j k) (hWnp : ∀ t j k, 0 ≤ Wnp t j k) (hWnn : ∀ t j k, 0 ≤ Wnn t j k)
    (hWpn : ∀ t j k, 0 ≤ Wpn t j k) (hdp : ∀ t k, 0 ≤ dp t k) (hdn : ∀ t k, 0 ≤ dn t k)
    (htop : Polarized top) : ∀ t, Polarized (sens Wpp Wnp Wnn Wpn dp dn top t) := by
  intro t
  induction t with
  | zero => exact htop
  | succ t ih =>
    exact back_polarized _ _ _ _ _ _ _ (hWpp t) (hWnp t) (hWnn t) (hWpn t) (hdp t) (hdn t) ih

/-- `sg` is the sign of `e`, as in the z3 encoding. -/
theorem sign_mul_nonneg (e sg : ℝ) (h : (0 < e ∧ sg = 1) ∨ (e < 0 ∧ sg = -1) ∨ (e = 0 ∧ sg = 0)) :
    0 ≤ e * sg := by
  rcases h with ⟨he, rfl⟩ | ⟨he, rfl⟩ | ⟨rfl, rfl⟩ <;> nlinarith

/-- ED update times gradient, for a weight into a p-stream unit (stream polarity +1). -/
theorem ed_descent_p (e sg tau x d s : ℝ) (hsg : 0 ≤ e * sg) (hs : 0 ≤ s) :
    (-(1 * tau) * x * d * sg) * (e * tau * x * d * s) ≤ 0 := by
  have h : (-(1 * tau) * x * d * sg) * (e * tau * x * d * s) = -((tau * x * d) ^ 2 * (e * sg) * s) := by ring
  rw [h]
  exact neg_nonpos.mpr (mul_nonneg (mul_nonneg (sq_nonneg _) hsg) hs)

/-- ED update times gradient, for a weight into an n-stream unit (stream polarity -1). -/
theorem ed_descent_n (e sg tau x d s : ℝ) (hsg : 0 ≤ e * sg) (hs : s ≤ 0) :
    (-(-1 * tau) * x * d * sg) * (e * tau * x * d * s) ≤ 0 := by
  have h : (-(-1 * tau) * x * d * sg) * (e * tau * x * d * s) = -((tau * x * d) ^ 2 * (e * sg) * (-s)) := by ring
  rw [h]
  exact neg_nonpos.mpr (mul_nonneg (mul_nonneg (sq_nonneg _) hsg) (neg_nonneg.mpr hs))

/-- Sign sufficiency at every depth: for a weight with entry sign `tau` and presynaptic activity `x` into unit `k`
of the layer `t` below the output, the ED update, which uses only sign(e) and the stream of unit `k`, never has a
positive product with the gradient of e²/2. -/
theorem ed_sign_sufficiency (Wpp Wnp Wnn Wpn : ℕ → Fin w → Fin w → ℝ) (dp dn : ℕ → Fin w → ℝ) (i0 : Fin w)
    (hWpp : ∀ t j k, 0 ≤ Wpp t j k) (hWnp : ∀ t j k, 0 ≤ Wnp t j k) (hWnn : ∀ t j k, 0 ≤ Wnn t j k)
    (hWpn : ∀ t j k, 0 ≤ Wpn t j k) (hdp : ∀ t k, 0 ≤ dp t k) (hdn : ∀ t k, 0 ≤ dn t k)
    (e sg : ℝ) (hsg : (0 < e ∧ sg = 1) ∨ (e < 0 ∧ sg = -1) ∨ (e = 0 ∧ sg = 0))
    (t : ℕ) (k : Fin w) (tau x : ℝ) :
    (-(1 * tau) * x * dp t k * sg) * (e * tau * x * dp t k * (sens Wpp Wnp Wnn Wpn dp dn (outputTop i0) t).1 k) ≤ 0
    ∧ (-(-1 * tau) * x * dn t k * sg) *
        (e * tau * x * dn t k * (sens Wpp Wnp Wnn Wpn dp dn (outputTop i0) t).2 k) ≤ 0 := by
  have hpol := sens_polarized Wpp Wnp Wnn Wpn dp dn (outputTop i0) hWpp hWnp hWnn hWpn hdp hdn
    (outputTop_polarized i0) t
  have he := sign_mul_nonneg e sg hsg
  exact ⟨ed_descent_p e sg tau x _ _ he (hpol.1 k), ed_descent_n e sg tau x _ _ he (hpol.2 k)⟩

end EdPolarity
