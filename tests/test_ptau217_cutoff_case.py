"""Tests for the plasma p-tau217 cutoff decision rule case (python/discovery/ptau217_cutoff_case.py)."""

from python.discovery import ptau217_cutoff_case as ptau


def test_main_ptau217_hypothesis_is_proved():
    h = ptau.ptau217_hypothesis()
    res = ptau.verdict(h)
    assert res["status"] == "PROVED", res
    assert res["content_verdict"] == "UNFALSIFIABLE"


def test_dropping_separation_or_renal_function_is_refuted():
    # Dropping preserved renal function allows CKD clearance factor to produce false positives in rule-in zone
    h_renal = ptau.ptau217_hypothesis(drop=("preserved_renal_function",))
    res_renal = ptau.verdict(h_renal)
    assert res_renal["status"] == "REFUTED"
    assert "ptau_val" in res_renal["witness"]


def test_necessity_table():
    table = ptau.necessity_table()
    assert table["preserved_renal_function"] == "NECESSARY"
    assert table["biomarker_separation"] == "NECESSARY"
    assert table["ordered_cutoffs"] == "NECESSARY"


def test_cohort_simulation_performance():
    cohort = ptau.simulate_patient_cohort(n_patients=600, amyloid_prevalence=0.35, ckd_prevalence=0.15, rng_seed=42)
    assert len(cohort) == 600

    # With preserved renal function only (filter CKD)
    perf_filtered = ptau.evaluate_two_cutoff_rule(cohort, c_low=0.70, c_high=1.30, filter_ckd=True)
    assert perf_filtered["rule_out_npv"] >= 0.85
    assert perf_filtered["rule_in_ppv"] >= 0.85
    assert perf_filtered["indeterminate_pct"] < 0.40

    # With unadjusted CKD, false positives increase due to reduced peripheral clearance
    perf_all = ptau.evaluate_two_cutoff_rule(cohort, c_low=0.70, c_high=1.30, filter_ckd=False)
    assert perf_all["false_positives"] >= perf_filtered["false_positives"]


if __name__ == "__main__":
    test_main_ptau217_hypothesis_is_proved()
    print("test_main_ptau217_hypothesis_is_proved: PASS")
    test_dropping_separation_or_renal_function_is_refuted()
    print("test_dropping_separation_or_renal_function_is_refuted: PASS")
    test_necessity_table()
    print("test_necessity_table: PASS")
    test_cohort_simulation_performance()
    print("test_cohort_simulation_performance: PASS")
    print("All ptau217 cutoff case tests PASSED successfully!")
