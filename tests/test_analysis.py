"""
Unit tests for exploratory analysis, descriptive statistics, and hypothesis testing.
"""
import numpy as np
import pandas as pd
import pytest

from app.analysis import get_descriptive_summary, run_hypothesis_tests, get_correlations


def test_descriptive_summary_known_values():
    df = pd.DataFrame({
        "observation_date": pd.date_range("2024-01-01", periods=10),
        "query_count": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "wholesale_price": [1000] * 10
    })
    summary = get_descriptive_summary(df)
    assert summary["total_observations"] == 10
    q_stat = next(s for s in summary["descriptive_statistics"] if s["variable"] == "query_count")
    assert q_stat["mean"] == 55.0
    assert q_stat["min"] == 10.0
    assert q_stat["max"] == 100.0


def test_hypothesis_a_perfect_correlation():
    # Construct synthetic dataframe with positive linear correlation
    x = np.linspace(1, 50, 50)
    df = pd.DataFrame({
        "query_count": 100 + (2.5 * x),
        "commodity_pct_change": x
    })
    hyp_res = run_hypothesis_tests(df)
    hyp_a = next(r for r in hyp_res["results"] if r["hypothesis_code"] == "HYP-A")

    assert hyp_a["reject_null"] is True
    assert hyp_a["test_statistic"] > 0.99
    assert hyp_a["p_value"] < 0.0001


def test_hypothesis_b_shock_detection():
    # Create 30 days where shock days have systematically higher queries
    df = pd.DataFrame({
        "query_count": [100] * 25 + [300] * 5,
        "diesel_pct_change": [0.1] * 25 + [3.5] * 5  # 5 shock days > 2%
    })
    hyp_res = run_hypothesis_tests(df, diesel_shock_threshold_pct=2.0)
    hyp_b = next(r for r in hyp_res["results"] if r["hypothesis_code"] == "HYP-B")

    assert hyp_b["sample_size"] == 30
    assert hyp_b["reject_null"] is True


def test_hypothesis_insufficient_sample():
    # Only 3 observations
    df = pd.DataFrame({
        "query_count": [10, 20, 30],
        "commodity_pct_change": [1.0, 2.0, 3.0]
    })
    hyp_res = run_hypothesis_tests(df)
    hyp_a = next(r for r in hyp_res["results"] if r["hypothesis_code"] == "HYP-A")

    assert hyp_a["reject_null"] is False
    assert "Insufficient" in hyp_a["verdict_plain_english"]


def test_get_correlations():
    df = pd.DataFrame({
        "query_count": np.arange(20),
        "wholesale_price": np.arange(20) * 10.0,
        "diesel_price": np.arange(20) + 90.0
    })
    corrs = get_correlations(df)
    assert len(corrs) >= 2
    for c in corrs:
        assert -1.0 <= c["pearson_r"] <= 1.0
        assert -1.0 <= c["spearman_rho"] <= 1.0


def test_hypothesis_result_includes_research_question_and_assumptions():
    df = pd.DataFrame({
        "query_count": list(range(100, 130)),
        "commodity_pct_change": [0.5 * i for i in range(30)]
    })
    res = run_hypothesis_tests(df)
    hyp_a = next(r for r in res["results"] if r["hypothesis_code"] == "HYP-A")
    assert "research_question" in hyp_a
    assert "assumptions" in hyp_a
    assert "limitations" in hyp_a
    assert hyp_a["research_question"] is not None
    assert "autocorrelation" in hyp_a["assumptions"]

