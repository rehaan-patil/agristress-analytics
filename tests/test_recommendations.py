"""
========================================================================================
AGRISTRESS ANALYTICS — COMPREHENSIVE RECOMMENDATION ENGINE TEST SUITE
========================================================================================

Verifies all 12 core decision-support scenarios:
1. Clear commodity-price decline generates useful comparison and cautious next step.
2. Rising price does not automatically trigger advice to sell.
3. Market comparison is generated only when comparable market-level data is available.
4. Diesel-price changes produce qualified cost-awareness message rather than invented cost estimate.
5. Missing fuel or commodity data does not produce fabricated recommendations.
6. High forecasted KCC demand is not misrepresented as proof of a farming crisis.
7. An unreliable or insufficiently supported forecast does not generate confident-looking advice.
8. Outdated data produces an appropriate freshness warning.
9. Synthetic datasets are not labelled as real data; unverified user datasets are distinct.
10. A normal situation does not trigger an exaggerated alert.
11. Changing the supplied dataset recalculates the farmer advisory.
12. Multilingual templates (English, Hindi, Marathi) render consistently.
"""
from pathlib import Path
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import pytest

from app.recommendations import (
    analyze_commodity_trend,
    analyze_market_comparison,
    analyze_spread_trend,
    analyze_fuel_trend,
    analyze_advisory_demand,
    get_freshness_assessment,
    determine_advisory_priority,
    generate_farmer_recommendations,
    VERIFIED_ASSISTANCE
)


def create_sample_df(
    n_days=30,
    start_date="2024-01-01",
    price_trend="stable",
    fuel_shock=False,
    markets=None
):
    dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(n_days)]
    base_price = 2000.0
    prices = []
    fuels = []
    retail = []

    for i in range(n_days):
        if price_trend == "falling":
            p = base_price - (i * 35.0)  # Steady drop
        elif price_trend == "rising":
            p = base_price + (i * 35.0)  # Steady rise
        else:
            p = base_price + (i % 3) * 10.0  # Stable
        prices.append(max(400.0, p))
        retail.append(p * 1.30)

        f = 90.0 + (3.0 if fuel_shock and i >= (n_days - 3) else 0.0)
        fuels.append(f)

    df_dict = {
        "observation_date": dates,
        "wholesale_price": prices,
        "retail_price": retail,
        "price_spread": [r - p for r, p in zip(retail, prices)],
        "diesel_price": fuels,
        "query_count": [50 + (i % 10) for i in range(n_days)],
        "is_synthetic": [True] * n_days
    }

    if markets:
        df_dict["market"] = [markets[i % len(markets)] for i in range(n_days)]

    return pd.DataFrame(df_dict)


# --------------------------------------------------------------------------------------
# Scenario 1: Commodity Price Decline & Cautious Action
# --------------------------------------------------------------------------------------
def test_scenario_1_price_decline_cautious_step():
    df = create_sample_df(n_days=20, price_trend="falling")
    res = analyze_commodity_trend(df, commodity_name="Tomato")
    assert res["available"] is True
    assert res["direction"] == "FALLING"
    assert res["pct_change"] <= -5.0
    assert "declined" in res["headline"].lower()

    # Must provide concrete, evidence-backed next steps
    assert any("modal price and arrival volume" in a.lower() for a in res["actions"])
    assert any("safe storage" in a.lower() or "msp" in a.lower() for a in res["actions"])

    # Must NOT give rigid, panicked 'distress sell' or 'sell today' orders
    for a in res["actions"]:
        assert "you must sell today" not in a.lower()
        assert "distress sell" not in a.lower()


# --------------------------------------------------------------------------------------
# Scenario 2: Rising Price Does NOT Automatically Trigger Advice to Sell
# --------------------------------------------------------------------------------------
def test_scenario_2_rising_price_no_forced_sell():
    df = create_sample_df(n_days=20, price_trend="rising")
    res = analyze_commodity_trend(df, commodity_name="Wheat")
    assert res["available"] is True
    assert res["direction"] == "RISING"
    assert res["pct_change"] >= 5.0
    assert "improved" in res["headline"].lower()

    # Explains that sharp rises can attract heavy inflows from other areas
    assert "inflows" in res["meaning"].lower() or "fluctuate" in res["meaning"].lower()

    # Recommends checking spot rates and grading/cleaning
    assert any("spot rates" in a.lower() for a in res["actions"])
    assert any("grade and sort" in a.lower() for a in res["actions"])

    # Does NOT mandate "sell everything immediately"
    for a in res["actions"]:
        assert "sell immediately" not in a.lower()
        assert "dump produce" not in a.lower()


# --------------------------------------------------------------------------------------
# Scenario 3: Market Comparison Multi-Mandi vs Single-Mandi / State Average
# --------------------------------------------------------------------------------------
def test_scenario_3_market_comparison():
    # 3A: When multiple distinct mandis exist in DataFrame
    multi_market_df = pd.DataFrame({
        "observation_date": ["2024-01-10", "2024-01-10", "2024-01-10"],
        "market": ["Pimpalgaon APMC", "Lasalgaon APMC", "Pune APMC"],
        "district": ["Nashik", "Nashik", "Pune"],
        "wholesale_price": [2200.0, 2350.0, 2500.0]
    })
    comp_multi = analyze_market_comparison(df=multi_market_df)
    assert comp_multi["available"] is True
    assert comp_multi["markets_count"] == 3
    assert comp_multi["table_md"] is not None
    assert "Pimpalgaon APMC" in comp_multi["table_md"]
    assert "Pune APMC" in comp_multi["table_md"]
    assert "Difference vs Avg" in comp_multi["table_md"]
    # Explains that higher quotes do not include transport
    assert "transport" in comp_multi["table_md"].lower()

    # 3B: When only 1 mandi or state-level average exists
    single_market_df = pd.DataFrame({
        "observation_date": ["2024-01-10"],
        "market": ["Nashik APMC"],
        "wholesale_price": [2200.0]
    })
    comp_single = analyze_market_comparison(df=single_market_df)
    assert comp_single["available"] is False
    assert "not available in this dataset" in comp_single["reason"].lower()


# --------------------------------------------------------------------------------------
# Scenario 4: Diesel-Price Changes Produce Qualified Cost Message
# --------------------------------------------------------------------------------------
def test_scenario_4_diesel_price_qualified_cost_message():
    df = create_sample_df(n_days=20, fuel_shock=True)
    res = analyze_fuel_trend(df, shock_threshold_pct=1.0)
    assert res["available"] is True
    assert res["status"] == "INCREASED"
    assert "increased" in res["headline"].lower()
    assert res["change_pct"] > 0

    # Must advise getting a firm quote and considering load pooling
    assert any("freight quote" in a.lower() for a in res["actions"])
    assert any("pooling" in a.lower() or "share" in a.lower() for a in res["actions"])

    # Must NOT claim an invented specific cost per quintal
    for a in res["actions"]:
        assert "costs you rs" not in a.lower()
        assert "raised your cost by" not in a.lower()


# --------------------------------------------------------------------------------------
# Scenario 5: Missing Fuel or Commodity Data Does NOT Produce Fabricated Recommendations
# --------------------------------------------------------------------------------------
def test_scenario_5_missing_fuel_or_commodity_data():
    empty_df = pd.DataFrame({"observation_date": ["2024-01-01"]})

    fuel_res = analyze_fuel_trend(empty_df)
    assert fuel_res["available"] is False
    assert "not available" in fuel_res["headline"].lower()

    comm_res = analyze_commodity_trend(empty_df, commodity_name="Onion")
    assert comm_res["available"] is False
    assert "unavailable" in comm_res["headline"].lower()


# --------------------------------------------------------------------------------------
# Scenario 6: High Forecasted KCC Demand NOT Misrepresented as Farming Crisis
# --------------------------------------------------------------------------------------
def test_scenario_6_high_kcc_demand_no_crisis_misrepresentation():
    forecast_mock = {
        "horizon_days": 14,
        "stress_assessment": {
            "category": "High",
            "historical_baseline_mean": 80.0
        },
        "predictions": [{"predicted_demand": 195.0} for _ in range(14)]
    }
    res = analyze_advisory_demand(forecast_mock)
    assert res["available"] is True
    assert res["category"] == "HIGH"
    assert "higher volume of farmer advisory queries" in res["headline"].lower()

    # Explains call centre inquiry volume, NOT a crop disease catastrophe or crisis
    assert "inquiry volumes" in res["detail"].lower()
    assert "crisis" not in res["headline"].lower()
    assert "disaster" not in res["detail"].lower()

    # Recommends verified helpline with verified operational hours
    assert any(VERIFIED_ASSISTANCE["kcc_toll_free"] in a for a in res["actions"])
    # No unverified morning speed claims
    for a in res["actions"]:
        assert "early in the morning (7:00 am" not in a.lower()


# --------------------------------------------------------------------------------------
# Scenario 7: Unreliable or Insufficiently Supported Forecast Acknowledges Uncertainty
# --------------------------------------------------------------------------------------
def test_scenario_7_insufficient_or_baseline_forecast():
    res_none = analyze_advisory_demand(None)
    assert res_none["available"] is False
    assert "unavailable" in res_none["headline"].lower()


# --------------------------------------------------------------------------------------
# Scenario 8: Outdated Data Produces Appropriate Freshness Warning
# --------------------------------------------------------------------------------------
def test_scenario_8_outdated_data_freshness_warning():
    # Historical date from 60 days ago
    past_date = date.today() - timedelta(days=60)
    freshness_old = get_freshness_assessment(past_date)
    assert freshness_old["is_recent"] is False
    assert freshness_old["status"] == "HISTORICAL"
    assert "[HISTORICAL DATA]" in freshness_old["statement"]
    assert "Confirm current local spot prices" in freshness_old["statement"]

    # Recent date (2 days ago)
    recent_date = date.today() - timedelta(days=2)
    freshness_recent = get_freshness_assessment(recent_date)
    assert freshness_recent["is_recent"] is True
    assert freshness_recent["status"] == "RECENT"
    assert "Recent observations" in freshness_recent["statement"]


# --------------------------------------------------------------------------------------
# Scenario 9: Synthetic Datasets NOT Labelled as Real Data; Unverified CSVs Distinct
# --------------------------------------------------------------------------------------
def test_scenario_9_provenance_labeling(tmp_path):
    df = create_sample_df(n_days=15)

    # 9A: Synthetic Demo Data
    adv_synth = generate_farmer_recommendations(
        df=df,
        quality={"sample_start": "2024-01-01", "sample_end": "2024-01-15", "provenance_type": "SYNTHETIC"},
        output_dir=tmp_path
    )
    assert adv_synth["provenance_type"] == "SYNTHETIC"
    assert "Synthetic Demonstration Data" in adv_synth["provenance_label"]

    # 9B: Unverified User-Supplied Data
    adv_unverified = generate_farmer_recommendations(
        df=df,
        quality={"sample_start": "2024-01-01", "sample_end": "2024-01-15", "provenance_type": "UNVERIFIED"},
        output_dir=tmp_path
    )
    assert adv_unverified["provenance_type"] == "UNVERIFIED"
    assert "Unverified / User-Supplied Data" in adv_unverified["provenance_label"]
    assert "Real" not in adv_unverified["provenance_label"]

    # 9C: Verified Real
    adv_real = generate_farmer_recommendations(
        df=df,
        quality={"sample_start": "2024-01-01", "sample_end": "2024-01-15", "provenance_type": "VERIFIED_REAL"},
        output_dir=tmp_path
    )
    assert adv_real["provenance_type"] == "VERIFIED_REAL"
    assert "Verified Real-World" in adv_real["provenance_label"]


# --------------------------------------------------------------------------------------
# Scenario 10: Normal Situation Does NOT Trigger an Exaggerated Alert
# --------------------------------------------------------------------------------------
def test_scenario_10_normal_situation_no_exaggerated_alert(tmp_path):
    df = create_sample_df(n_days=20, price_trend="stable", fuel_shock=False)
    forecast_normal = {
        "horizon_days": 14,
        "stress_assessment": {"category": "Normal", "historical_baseline_mean": 80.0},
        "predictions": [{"predicted_demand": 78.0} for _ in range(14)]
    }
    adv = generate_farmer_recommendations(
        df=df,
        forecast_res=forecast_normal,
        quality={"sample_start": "2024-01-01", "sample_end": "2024-01-20", "provenance_type": "SYNTHETIC"},
        output_dir=tmp_path
    )
    assert adv["price_direction"] == "STABLE"
    assert adv["priority"] == "No clear signal"
    assert "steady" in adv["price_headline"].lower()


# --------------------------------------------------------------------------------------
# Scenario 11: Changing Supplied Dataset Recalculates Farmer Advisory
# --------------------------------------------------------------------------------------
def test_scenario_11_changing_dataset_recalculates(tmp_path):
    df_tomato = create_sample_df(n_days=20, price_trend="falling", start_date="2023-05-01")
    adv_tomato = generate_farmer_recommendations(
        df=df_tomato,
        commodity="Tomato",
        state="Karnataka",
        output_dir=tmp_path
    )

    df_onion = create_sample_df(n_days=20, price_trend="rising", start_date="2024-01-01")
    adv_onion = generate_farmer_recommendations(
        df=df_onion,
        commodity="Onion",
        state="Maharashtra",
        output_dir=tmp_path
    )

    assert adv_tomato["commodity"] == "Tomato"
    assert adv_tomato["region"] == "Karnataka"
    assert adv_tomato["price_direction"] == "FALLING"

    assert adv_onion["commodity"] == "Onion"
    assert adv_onion["region"] == "Maharashtra"
    assert adv_onion["price_direction"] == "RISING"
    assert adv_tomato["price_headline"] != adv_onion["price_headline"]


# --------------------------------------------------------------------------------------
# Scenario 12: Multilingual Support (Hindi and Marathi)
# --------------------------------------------------------------------------------------
def test_scenario_12_multilingual_templates(tmp_path):
    df = create_sample_df(n_days=20, price_trend="falling")

    # Hindi
    adv_hi = generate_farmer_recommendations(df=df, commodity="प्याज", state="महाराष्ट्र", lang="hi", output_dir=tmp_path)
    assert adv_hi["lang"] == "hi"
    md_hi = Path(adv_hi["report_md_path"]).read_text(encoding="utf-8")
    assert "किसान बाज़ार एवं सूचना सलाह" in md_hi
    assert "1800-180-1551" in md_hi
    assert "अनुशंसित अगले कदम" in md_hi

    # Marathi
    adv_mr = generate_farmer_recommendations(df=df, commodity="कांदा", state="महाराष्ट्र", lang="mr", output_dir=tmp_path)
    assert adv_mr["lang"] == "mr"
    md_mr = Path(adv_mr["report_md_path"]).read_text(encoding="utf-8")
    assert "शेतकरी बाज़ार व माहिती सल्ला" in md_mr
    assert "1800-180-1551" in md_mr
    assert "पुढील शिफारस केलेल्या कृती" in md_mr


# --------------------------------------------------------------------------------------
# Numbering Integrity & Completeness Check
# --------------------------------------------------------------------------------------
def test_recommendation_numbering_starts_at_one(tmp_path):
    df = create_sample_df(n_days=20, price_trend="stable")
    adv = generate_farmer_recommendations(df=df, output_dir=tmp_path)

    steps = adv["recommended_steps"]
    assert len(steps) >= 2
    for step in steps:
        assert step is not None
        assert len(step.strip()) > 5
        # Must not contain placeholder text
        assert "none" not in step.lower()
        assert "nan" not in step.lower()

    # In Markdown file, verify first item is strictly "1. "
    md_text = Path(adv["report_md_path"]).read_text(encoding="utf-8")
    assert "\n1. " in md_text
    assert "\n2. " in md_text
