"""
Exploratory Data Analysis, Visualization, and Hypothesis Testing for AgriStress Analytics.

Written in understandable, student-level Python using Pandas, SciPy, and Matplotlib.
Calculations are transparent and explainable during a university viva.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.orm import Session
from sqlalchemy import func

import matplotlib
# Set headless backend so charts can be generated without a GUI desktop display
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from app.config import OUTPUTS_DIR
from app.models import KCCObservation, CommodityObservation, FuelObservation
from app.data_processing import build_analytical_dataset


# =====================================================================
# 1. DESCRIPTIVE STATISTICS AND OVERVIEWS
# =====================================================================

def get_overview_stats(db: Session) -> Dict[str, Any]:
    """
    Returns high-level metadata across KCC, Commodity, and Fuel records.
    """
    total_queries = db.query(func.sum(KCCObservation.query_count)).scalar() or 0
    comm_count = db.query(func.count(CommodityObservation.id)).scalar() or 0
    fuel_count = db.query(func.count(FuelObservation.id)).scalar() or 0

    kcc_min = db.query(func.min(KCCObservation.observation_date)).scalar()
    kcc_max = db.query(func.max(KCCObservation.observation_date)).scalar()

    states = [s[0] for s in db.query(func.distinct(KCCObservation.state)).all() if s[0]]

    # Check if any synthetic data is present
    has_synth = (
        (db.query(KCCObservation.id).filter(KCCObservation.is_synthetic == True).first() is not None) or
        (db.query(CommodityObservation.id).filter(CommodityObservation.is_synthetic == True).first() is not None)
    )

    return {
        "kcc_total_queries": int(total_queries),
        "commodity_records": int(comm_count),
        "fuel_records": int(fuel_count),
        "date_range": {
            "start": str(kcc_min) if kcc_min else None,
            "end": str(kcc_max) if kcc_max else None,
        },
        "states_covered": states,
        "is_synthetic": has_synth,
    }


def get_descriptive_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes key descriptive statistics (mean, std, median, min, max)
    for numeric analytical variables.
    """
    if df.empty:
        return {
            "sample_period": {"start": None, "end": None},
            "total_observations": 0,
            "descriptive_statistics": [],
            "insights": ["Analytical dataset is empty. Please import data first."]
        }

    numeric_cols = [
        "query_count", "wholesale_price", "retail_price",
        "diesel_price", "price_spread", "commodity_volatility_7d"
    ]

    stats_list = []
    for col in numeric_cols:
        if col in df.columns and df[col].notna().sum() > 0:
            series = df[col].dropna()
            stats_list.append({
                "variable": col,
                "count": int(len(series)),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "median": round(float(series.median()), 2),
                "max": round(float(series.max()), 2)
            })

    start_date = str(df["observation_date"].min()) if "observation_date" in df else None
    end_date = str(df["observation_date"].max()) if "observation_date" in df else None

    # Derive high-level descriptive observations
    insights = []
    if "query_count" in df.columns:
        mean_q = df["query_count"].mean()
        max_q = df["query_count"].max()
        insights.append(f"Average daily KCC query demand is {mean_q:.1f} calls, peaking at {max_q:.0f} calls.")

    if "wholesale_price" in df.columns and df["wholesale_price"].notna().sum() > 0:
        mean_p = df["wholesale_price"].mean()
        insights.append(f"Mean agricultural wholesale price is Rs {mean_p:.2f} per quintal across observations.")

    if "price_spread" in df.columns and df["price_spread"].notna().sum() > 0:
        mean_spread = df["price_spread"].mean()
        insights.append(f"Mean wholesale-to-retail margin spread is Rs {mean_spread:.2f} per quintal where recorded.")

    return {
        "sample_period": {"start": start_date, "end": end_date},
        "total_observations": len(df),
        "descriptive_statistics": stats_list,
        "insights": insights
    }


def get_regional_summary(db: Session) -> List[Dict[str, Any]]:
    """
    Computes query volume statistics broken down by state.
    """
    results = (
        db.query(
            KCCObservation.state,
            func.sum(KCCObservation.query_count).label("total_queries"),
            func.count(func.distinct(KCCObservation.observation_date)).label("days_observed"),
            func.avg(KCCObservation.query_count).label("avg_queries")
        )
        .group_by(KCCObservation.state)
        .all()
    )

    regional = []
    for r in results:
        regional.append({
            "state": r.state,
            "total_queries": int(r.total_queries or 0),
            "observation_days": int(r.days_observed or 0),
            "avg_daily_queries": round(float(r.avg_queries or 0), 2)
        })
    return regional


def get_correlations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes pairwise Pearson and Spearman correlation coefficients between
    KCC query demand and key economic indicators.
    """
    if df.empty or "query_count" not in df.columns:
        return []

    candidate_vars = [
        ("wholesale_price", "Wholesale Commodity Price"),
        ("commodity_price_change", "Commodity Price Daily Change"),
        ("commodity_volatility_7d", "7-Day Commodity Price Volatility"),
        ("price_spread", "Wholesale-Retail Price Spread"),
        ("diesel_price", "Diesel Price Level"),
        ("diesel_price_change", "Diesel Daily Price Change"),
        ("diesel_change_lag7", "7-Day Lagged Diesel Price Change")
    ]

    results = []
    for col, label in candidate_vars:
        if col in df.columns:
            valid_sub = df[["query_count", col]].dropna()
            n = len(valid_sub)
            if n >= 10:
                p_r, _ = stats.pearsonr(valid_sub["query_count"], valid_sub[col])
                s_rho, _ = stats.spearmanr(valid_sub["query_count"], valid_sub[col])

                results.append({
                    "variable_x": "KCC Query Demand",
                    "variable_y": label,
                    "pearson_r": round(float(p_r), 4),
                    "spearman_rho": round(float(s_rho), 4),
                    "sample_size": n,
                    "note": "Linear correlation (Pearson) and rank-order correlation (Spearman)."
                })
    return results


# =====================================================================
# 2. HYPOTHESIS TESTING
# =====================================================================

def run_hypothesis_tests(
    df: pd.DataFrame,
    diesel_shock_threshold_pct: float = 2.0
) -> Dict[str, Any]:
    """
    Conducts defensible econometric hypothesis tests:
      - Hypothesis A: Commodity price movements vs KCC query demand
      - Hypothesis B: Diesel price shocks vs query demand
      - Hypothesis C: Wholesale-to-retail spread vs query demand
    """
    results = []

    # -------------------------------------------------------------
    # Hypothesis A: Commodity Price Movements
    # -------------------------------------------------------------
    hyp_a_null = "Commodity price changes have no statistically detectable association with KCC query demand."
    hyp_a_alt = "Commodity price changes exhibit a statistically detectable linear or rank association with KCC query demand."

    if "commodity_pct_change" in df.columns and "query_count" in df.columns:
        sub_a = df[["query_count", "commodity_pct_change"]].dropna()
        n_a = len(sub_a)
        if n_a >= 15:
            # Pearson test for linear correlation
            r_val, p_val = stats.pearsonr(sub_a["query_count"], sub_a["commodity_pct_change"])
            reject_a = bool(p_val < 0.05)

            if reject_a:
                verdict_a = (
                    f"Reject null hypothesis (r = {r_val:.4f}, p = {p_val:.4e}). "
                    f"There is a statistically significant correlation between commodity price changes "
                    f"and farmer advisory query influx at alpha = 0.05."
                )
            else:
                verdict_a = (
                    f"Fail to reject null hypothesis (r = {r_val:.4f}, p = {p_val:.4f}). "
                    f"No statistically significant linear association was detected between commodity price "
                    f"percentage changes and query demand in this sample."
                )

            results.append({
                "hypothesis_code": "HYP-A",
                "title": "Commodity Price Movements vs Query Demand",
                "null_hypothesis": hyp_a_null,
                "alternative_hypothesis": hyp_a_alt,
                "test_used": "Pearson Correlation Test",
                "sample_size": n_a,
                "test_statistic": round(float(r_val), 4),
                "p_value": round(float(p_val), 5),
                "effect_size": round(float(r_val), 4),
                "significance_level": 0.05,
                "reject_null": reject_a,
                "verdict_plain_english": verdict_a,
                "limitations": "Correlation does not imply economic causation. Seasonal monsoon patterns also influence both prices and queries."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-A",
                "title": "Commodity Price Movements vs Query Demand",
                "null_hypothesis": hyp_a_null,
                "alternative_hypothesis": hyp_a_alt,
                "test_used": "Pearson Correlation Test",
                "sample_size": n_a,
                "test_statistic": None,
                "p_value": None,
                "effect_size": None,
                "significance_level": 0.05,
                "reject_null": False,
                "verdict_plain_english": "Insufficient observations to conduct test reliably.",
                "limitations": "Requires at least 15 matched observation days."
            })

    # -------------------------------------------------------------
    # Hypothesis B: Diesel Fuel Price Shocks
    # -------------------------------------------------------------
    hyp_b_null = "KCC query demand does not differ between diesel price shock days and normal price days."
    hyp_b_alt = "KCC query demand differs significantly during or immediately following diesel price shocks."

    if "diesel_pct_change" in df.columns and "query_count" in df.columns:
        sub_b = df[["query_count", "diesel_pct_change"]].dropna().copy()
        # Define shock day rule: absolute daily change exceeds threshold (e.g. 2.0%)
        # or daily change in top 5% of price adjustments
        sub_b["is_shock"] = sub_b["diesel_pct_change"].abs() >= diesel_shock_threshold_pct

        shock_queries = sub_b[sub_b["is_shock"]]["query_count"]
        normal_queries = sub_b[~sub_b["is_shock"]]["query_count"]

        n_shock = len(shock_queries)
        n_normal = len(normal_queries)

        if n_shock >= 5 and n_normal >= 15:
            # Mann-Whitney U test (non-parametric two-sample test suitable for count data)
            u_stat, p_val_b = stats.mannwhitneyu(shock_queries, normal_queries, alternative="two-sided")
            reject_b = bool(p_val_b < 0.05)

            mean_shock = float(shock_queries.mean())
            mean_normal = float(normal_queries.mean())

            if reject_b:
                verdict_b = (
                    f"Reject null hypothesis (Mann-Whitney U = {u_stat:.1f}, p = {p_val_b:.4e}). "
                    f"Query volume during diesel price shock periods (mean = {mean_shock:.1f}) differed significantly "
                    f"from normal price periods (mean = {mean_normal:.1f})."
                )
            else:
                verdict_b = (
                    f"Fail to reject null hypothesis (Mann-Whitney U = {u_stat:.1f}, p = {p_val_b:.4f}). "
                    f"No statistically significant difference in query influx was observed between "
                    f"shock days (mean = {mean_shock:.1f}) and normal days (mean = {mean_normal:.1f})."
                )

            results.append({
                "hypothesis_code": "HYP-B",
                "title": "Diesel Price Shocks vs Advisory Influx",
                "null_hypothesis": hyp_b_null,
                "alternative_hypothesis": hyp_b_alt,
                "test_used": "Mann-Whitney U Two-Sample Rank Sum Test",
                "sample_size": int(n_shock + n_normal),
                "test_statistic": round(float(u_stat), 2),
                "p_value": round(float(p_val_b), 5),
                "effect_size": round(mean_shock - mean_normal, 2),
                "significance_level": 0.05,
                "reject_null": reject_b,
                "verdict_plain_english": verdict_b,
                "limitations": f"Shock defined as |daily diesel % change| >= {diesel_shock_threshold_pct}%. Only {n_shock} shock days identified."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-B",
                "title": "Diesel Price Shocks vs Advisory Influx",
                "null_hypothesis": hyp_b_null,
                "alternative_hypothesis": hyp_b_alt,
                "test_used": "Mann-Whitney U Test",
                "sample_size": int(n_shock + n_normal),
                "test_statistic": None,
                "p_value": None,
                "effect_size": None,
                "significance_level": 0.05,
                "reject_null": False,
                "verdict_plain_english": f"Too few diesel price shocks detected (found {n_shock} shock days, needed >= 5) to run a robust test.",
                "limitations": "Fuel price revisions in India occur intermittently; a longer sample or lower threshold is needed."
            })

    # -------------------------------------------------------------
    # Hypothesis C: Wholesale-to-Retail Price Spreads
    # -------------------------------------------------------------
    hyp_c_null = "The wholesale-to-retail commodity price spread has no association with KCC query influx."
    hyp_c_alt = "Wider wholesale-to-retail price spreads are associated with higher advisory demand."

    if "price_spread" in df.columns and "query_count" in df.columns:
        sub_c = df[["query_count", "price_spread"]].dropna()
        n_c = len(sub_c)
        if n_c >= 15:
            # Spearman rank correlation (price spreads can have non-normal distributions)
            rho_c, p_val_c = stats.spearmanr(sub_c["query_count"], sub_c["price_spread"])
            reject_c = bool(p_val_c < 0.05)

            if reject_c:
                verdict_c = (
                    f"Reject null hypothesis (Spearman rho = {rho_c:.4f}, p = {p_val_c:.4e}). "
                    f"A statistically significant monotonic association exists between wholesale-retail price spread "
                    f"and farmer advisory inquiries."
                )
            else:
                verdict_c = (
                    f"Fail to reject null hypothesis (Spearman rho = {rho_c:.4f}, p = {p_val_c:.4f}). "
                    f"Price spread variation is not significantly correlated with query influx."
                )

            results.append({
                "hypothesis_code": "HYP-C",
                "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "null_hypothesis": hyp_c_null,
                "alternative_hypothesis": hyp_c_alt,
                "test_used": "Spearman Rank Correlation Test",
                "sample_size": n_c,
                "test_statistic": round(float(rho_c), 4),
                "p_value": round(float(p_val_c), 5),
                "effect_size": round(float(rho_c), 4),
                "significance_level": 0.05,
                "reject_null": reject_c,
                "verdict_plain_english": verdict_c,
                "limitations": "Retail price data is frequently missing in primary mandi feeds; only matched pairs are tested."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-C",
                "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "null_hypothesis": hyp_c_null,
                "alternative_hypothesis": hyp_c_alt,
                "test_used": "Spearman Rank Correlation Test",
                "sample_size": n_c,
                "test_statistic": None,
                "p_value": None,
                "effect_size": None,
                "significance_level": 0.05,
                "reject_null": False,
                "verdict_plain_english": "Retail price observations are unavailable or insufficient to compute price spreads.",
                "limitations": "Agmarknet primarily logs wholesale modal prices; retail prices require supplementary consumer affairs monitoring data."
            })

    return {
        "run_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
        "disclaimer": "All hypothesis tests reflect statistical associations in the observed sample. They do not demonstrate direct economic causation."
    }


# =====================================================================
# 3. VISUALIZATION AND CHART GENERATION
# =====================================================================

def plot_query_demand_over_time(df: pd.DataFrame, output_path: Path):
    """Generates a line plot of daily KCC query demand over time with 14-day rolling average."""
    plt.figure(figsize=(11, 4.5))
    plt.plot(df["observation_date"], df["query_count"], color="#4A90E2", alpha=0.45, label="Daily Query Count")
    rolling_q = df["query_count"].rolling(window=14, min_periods=3).mean()
    plt.plot(df["observation_date"], rolling_q, color="#D0021B", linewidth=2.0, label="14-Day Moving Average")

    plt.title("Kisan Call Centre (KCC) Query Influx Over Time", fontsize=12, fontweight="bold")
    plt.xlabel("Observation Date", fontsize=10)
    plt.ylabel("Query Volume (Incoming Inquiries)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_seasonality(df: pd.DataFrame, output_path: Path):
    """Plots day-of-week and month-of-year query volume patterns to illustrate seasonality."""
    temp_df = df.copy()
    temp_df["day_name"] = temp_df["observation_date"].dt.day_name()
    temp_df["month_name"] = temp_df["observation_date"].dt.strftime("%b")

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Day of week
    dow_stats = temp_df.groupby("day_name")["query_count"].mean().reindex(days_order)
    sns.barplot(x=dow_stats.index, y=dow_stats.values, ax=axes[0], color="#50E3C2")
    axes[0].set_title("Average Queries by Day of Week", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Day of Week")
    axes[0].set_ylabel("Mean Query Count")
    axes[0].tick_params(axis="x", rotation=40)

    # Month of year
    moy_stats = temp_df.groupby("month_name")["query_count"].mean().reindex(months_order)
    sns.barplot(x=moy_stats.index, y=moy_stats.values, ax=axes[1], color="#F5A623")
    axes[1].set_title("Average Queries by Month (Annual Seasonality)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Mean Query Count")
    axes[1].tick_params(axis="x", rotation=40)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_commodity_trends(df: pd.DataFrame, output_path: Path):
    """Plots agricultural commodity wholesale price trends alongside 7-day rolling volatility."""
    fig, ax1 = plt.subplots(figsize=(11, 4.5))

    ax1.plot(df["observation_date"], df["wholesale_price"], color="#2E7D32", label="Wholesale Price (INR/Quintal)")
    ax1.set_xlabel("Date", fontsize=10)
    ax1.set_ylabel("Price (INR/Quintal)", color="#2E7D32", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="#2E7D32")
    ax1.grid(True, linestyle="--", alpha=0.4)

    # Secondary axis for rolling volatility
    if "commodity_volatility_7d" in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(df["observation_date"], df["commodity_volatility_7d"], color="#E65100", linestyle=":", label="7D Price Volatility")
        ax2.set_ylabel("7-Day Volatility (Std Dev)", color="#E65100", fontsize=10)
        ax2.tick_params(axis="y", labelcolor="#E65100")

    plt.title("Commodity Wholesale Price Trajectory and Short-Term Volatility", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_diesel_trends(df: pd.DataFrame, output_path: Path):
    """Plots diesel retail price movements over time."""
    plt.figure(figsize=(11, 4.5))
    plt.plot(df["observation_date"], df["diesel_price"], color="#C2185B", linewidth=1.8, label="Diesel Retail Selling Price (INR/Litre)")
    plt.title("Retail Diesel Price Trajectory (INR/Litre)", fontsize=12, fontweight="bold")
    plt.xlabel("Observation Date", fontsize=10)
    plt.ylabel("Price (INR / Litre)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_price_spread(df: pd.DataFrame, output_path: Path):
    """Plots wholesale versus retail prices and margin spread where available."""
    plt.figure(figsize=(11, 4.5))
    plt.plot(df["observation_date"], df["retail_price"], color="#7B1FA2", label="Retail Price (INR/Qtl)")
    plt.plot(df["observation_date"], df["wholesale_price"], color="#388E3C", label="Wholesale Price (INR/Qtl)")
    
    if "price_spread" in df.columns:
        plt.fill_between(
            df["observation_date"],
            df["wholesale_price"],
            df["retail_price"],
            color="#E1BEE7",
            alpha=0.4,
            label="Wholesale-to-Retail Spread"
        )

    plt.title("Wholesale vs. Retail Price Margins Over Time", fontsize=12, fontweight="bold")
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("INR per Quintal", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_query_vs_economic(df: pd.DataFrame, output_path: Path):
    """Dual-axis plot comparing KCC query demand against wholesale commodity prices."""
    fig, ax1 = plt.subplots(figsize=(11, 4.5))

    ax1.plot(df["observation_date"], df["query_count"].rolling(7, min_periods=2).mean(), color="#1565C0", label="KCC Queries (7D Moving Avg)")
    ax1.set_xlabel("Date", fontsize=10)
    ax1.set_ylabel("KCC Query Demand", color="#1565C0", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="#1565C0")
    ax1.grid(True, linestyle="--", alpha=0.4)

    ax2 = ax1.twinx()
    ax2.plot(df["observation_date"], df["wholesale_price"], color="#FB8C00", linestyle="--", label="Wholesale Price")
    ax2.set_ylabel("Wholesale Price (INR/Quintal)", color="#FB8C00", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="#FB8C00")

    plt.title("Farmer Query Influx vs. Commodity Wholesale Price Movements", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_regional_comparison(db: Session, output_path: Path):
    """Bar chart comparing query demand across registered states."""
    regional = get_regional_summary(db)
    if not regional:
        return

    states = [r["state"] for r in regional]
    totals = [r["total_queries"] for r in regional]

    plt.figure(figsize=(9, 4.5))
    sns.barplot(x=states, y=totals, hue=states, legend=False, palette="viridis")
    plt.title("Total KCC Query Volume Across Regions", fontsize=12, fontweight="bold")
    plt.xlabel("State / Region", fontsize=10)
    plt.ylabel("Total Inquiries Received", fontsize=10)
    plt.tick_params(axis="x", rotation=25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame, output_path: Path):
    """Generates a correlation matrix heatmap across query counts and price variables."""
    cols_to_corr = [
        "query_count", "wholesale_price", "retail_price",
        "diesel_price", "price_spread", "commodity_volatility_7d"
    ]
    existing = [c for c in cols_to_corr if c in df.columns]
    if len(existing) < 2:
        return

    corr_matrix = df[existing].corr(method="pearson")

    # Rename for clean display
    labels_map = {
        "query_count": "KCC Queries",
        "wholesale_price": "Wholesale Price",
        "retail_price": "Retail Price",
        "diesel_price": "Diesel Price",
        "price_spread": "Price Spread",
        "commodity_volatility_7d": "7D Volatility"
    }
    clean_labels = [labels_map.get(c, c) for c in existing]

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        xticklabels=clean_labels,
        yticklabels=clean_labels,
        vmin=-1,
        vmax=1,
        linewidths=0.5
    )
    plt.title("Correlation Matrix: Query Influx and Economic Indicators", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_all_charts(db: Session) -> List[str]:
    """
    Executes all exploratory chart functions and saves PNG images to outputs/charts/.
    Returns a list of generated file paths.
    """
    charts_dir = OUTPUTS_DIR / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    df = build_analytical_dataset(db, export_csv=True)
    if df.empty:
        return []

    generated = []

    # 1. Query demand over time
    p1 = charts_dir / "query_demand_over_time.png"
    plot_query_demand_over_time(df, p1)
    generated.append(str(p1))

    # 2. Seasonality
    p2 = charts_dir / "seasonality_patterns.png"
    plot_seasonality(df, p2)
    generated.append(str(p2))

    # 3. Commodity trends
    p3 = charts_dir / "commodity_price_trends.png"
    plot_commodity_trends(df, p3)
    generated.append(str(p3))

    # 4. Diesel trends
    p4 = charts_dir / "diesel_price_trends.png"
    plot_diesel_trends(df, p4)
    generated.append(str(p4))

    # 5. Price spread
    if "price_spread" in df.columns and df["price_spread"].notna().sum() > 0:
        p5 = charts_dir / "price_spreads.png"
        plot_price_spread(df, p5)
        generated.append(str(p5))

    # 6. Query vs economic
    p6 = charts_dir / "query_vs_economic.png"
    plot_query_vs_economic(df, p6)
    generated.append(str(p6))

    # 7. Regional comparison
    p7 = charts_dir / "regional_queries.png"
    plot_regional_comparison(db, p7)
    generated.append(str(p7))

    # 8. Correlation heatmap
    p8 = charts_dir / "correlation_heatmap.png"
    plot_correlation_heatmap(df, p8)
    generated.append(str(p8))

    return generated


# =====================================================================
# 4. SUMMARY REPORT GENERATION
# =====================================================================

def generate_summary_report(db: Session) -> Dict[str, Any]:
    """
    Builds an analytical summary report, runs hypothesis tests,
    generates all charts, and writes outputs/reports/summary_report.md.
    """
    reports_dir = OUTPUTS_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = build_analytical_dataset(db, export_csv=True)
    stats_data = get_descriptive_summary(df)
    hyp_data = run_hypothesis_tests(df)
    chart_paths = generate_all_charts(db)

    report_path = reports_dir / "summary_report.md"

    md_lines = [
        "# AgriStress Analytics — Research Summary Report",
        f"**Generated At:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
        "## 1. Project Background and Research Scope",
        "This report investigates associations between farmer advisory demand logged through India's",
        "Kisan Call Centre (KCC), agricultural commodity wholesale prices, and retail diesel fuel price adjustments.",
        "> **Methodological Disclaimer:** Observed statistical correlations represent descriptive associations",
        "> within the analyzed sample and do not prove economic causation. Query demand reflects received requests",
        "> rather than direct staffing capacity mandates.\n",
        "## 2. Sample Period and Data Scope",
        f"- **Start Date:** {stats_data['sample_period']['start']}",
        f"- **End Date:** {stats_data['sample_period']['end']}",
        f"- **Total Daily Observations:** {stats_data['total_observations']:,}\n",
        "## 3. Descriptive Statistics",
        "| Variable | Count | Mean | Std Dev | Min | Median | Max |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for item in stats_data["descriptive_statistics"]:
        md_lines.append(
            f"| `{item['variable']}` | {item['count']} | {item['mean']} | {item['std']} | "
            f"{item['min']} | {item['median']} | {item['max']} |"
        )

    md_lines.extend([
        "\n## 4. Hypothesis Testing Results\n"
    ])

    for res in hyp_data["results"]:
        md_lines.extend([
            f"### {res['hypothesis_code']}: {res['title']}",
            f"- **Null Hypothesis (H0):** {res['null_hypothesis']}",
            f"- **Alternative Hypothesis (H1):** {res['alternative_hypothesis']}",
            f"- **Statistical Test:** {res['test_used']} (N = {res['sample_size']})",
            f"- **Test Statistic:** {res['test_statistic']} | **P-Value:** {res['p_value']}",
            f"- **Decision:** {'Reject H0' if res['reject_null'] else 'Fail to Reject H0'} (alpha = {res['significance_level']})",
            f"- **Plain English Verdict:** {res['verdict_plain_english']}",
            f"- **Limitations:** {res['limitations']}\n"
        ])

    md_lines.extend([
        "## 5. Generated Visualizations",
        "The following charts were generated and saved to `outputs/charts/`:"
    ])

    for cp in chart_paths:
        name = Path(cp).name
        md_lines.append(f"- `{name}`")

    md_lines.extend([
        "\n## 6. Research Limitations",
        "- **Data Aggregation:** KCC calls are aggregated daily; intraday spikes during weather emergencies are smoothed out.",
        "- **Fuel Price Granularity:** Diesel prices reflect state/metro reporting rather than specific rural revenue blocks.",
        "- **Synthetic Data Caution:** If demonstration data was used, empirical inferences cannot be generalized to real field conditions."
    ])

    report_content = "\n".join(md_lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return {
        "report_filename": report_path.name,
        "report_path": str(report_path),
        "generated_at": datetime.utcnow().isoformat(),
        "chart_paths": chart_paths,
        "status": "SUCCESS"
    }
