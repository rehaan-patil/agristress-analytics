"""
Exploratory Analysis, Visualization, and Hypothesis Testing for AgriStress Analytics.
Written in student-friendly, readable Python using Pandas, SciPy, and Matplotlib.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.orm import Session
from sqlalchemy import func

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from app.config import OUTPUTS_DIR
from app.models import KCCObservation, CommodityObservation, FuelObservation
from app.data_processing import build_analytical_dataset


def get_overview_stats(db: Session) -> Dict[str, Any]:
    """Returns total counts, dates, and regions across all imported tables."""
    queries = db.query(func.sum(KCCObservation.query_count)).scalar() or 0
    comm = db.query(func.count(CommodityObservation.id)).scalar() or 0
    fuel = db.query(func.count(FuelObservation.id)).scalar() or 0
    min_d = db.query(func.min(KCCObservation.observation_date)).scalar()
    max_d = db.query(func.max(KCCObservation.observation_date)).scalar()
    states = [s[0] for s in db.query(func.distinct(KCCObservation.state)).all() if s[0]]
    is_synth = db.query(KCCObservation.id).filter(KCCObservation.is_synthetic == True).first() is not None

    return {
        "kcc_total_queries": int(queries),
        "commodity_records": int(comm),
        "fuel_records": int(fuel),
        "date_range": {"start": str(min_d) if min_d else None, "end": str(max_d) if max_d else None},
        "states_covered": states,
        "is_synthetic": is_synth
    }


def get_descriptive_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates mean, std, median, min, and max for each numerical variable."""
    if df.empty:
        return {"sample_period": {"start": None, "end": None}, "total_observations": 0, "descriptive_statistics": [], "insights": ["No data."]}

    numeric_cols = ["query_count", "wholesale_price", "retail_price", "diesel_price", "price_spread", "commodity_volatility_7d"]
    stats_list = []
    for col in numeric_cols:
        if col in df.columns and df[col].notna().sum() > 0:
            s = df[col].dropna()
            stats_list.append({
                "variable": col,
                "count": int(len(s)),
                "mean": round(float(s.mean()), 2),
                "std": round(float(s.std()), 2),
                "min": round(float(s.min()), 2),
                "median": round(float(s.median()), 2),
                "max": round(float(s.max()), 2)
            })

    start_date = str(df["observation_date"].min()) if "observation_date" in df else None
    end_date = str(df["observation_date"].max()) if "observation_date" in df else None
    insights = [f"Analyzed {len(df)} daily observations from {start_date} to {end_date}."]
    if "query_count" in df.columns:
        insights.append(f"Average daily KCC query demand is {df['query_count'].mean():.1f} calls.")

    return {
        "sample_period": {"start": start_date, "end": end_date},
        "total_observations": len(df),
        "descriptive_statistics": stats_list,
        "insights": insights
    }


def get_regional_summary(db: Session) -> List[Dict[str, Any]]:
    """Calculates query counts grouped by state."""
    rows = (
        db.query(
            KCCObservation.state,
            func.sum(KCCObservation.query_count).label("total_queries"),
            func.count(func.distinct(KCCObservation.observation_date)).label("days_observed"),
            func.avg(KCCObservation.query_count).label("avg_queries")
        )
        .group_by(KCCObservation.state)
        .all()
    )
    return [
        {
            "state": r.state,
            "total_queries": int(r.total_queries or 0),
            "observation_days": int(r.days_observed or 0),
            "avg_daily_queries": round(float(r.avg_queries or 0), 2)
        }
        for r in rows
    ]


def get_correlations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Computes linear Pearson and rank Spearman correlation against KCC query demand."""
    if df.empty or "query_count" not in df.columns:
        return []

    variables = [
        ("wholesale_price", "Wholesale Commodity Price"),
        ("commodity_price_change", "Commodity Price Daily Change"),
        ("commodity_volatility_7d", "7-Day Commodity Price Volatility"),
        ("price_spread", "Wholesale-Retail Price Spread"),
        ("diesel_price", "Diesel Price Level"),
        ("diesel_price_change", "Diesel Daily Price Change"),
        ("diesel_change_lag7", "7-Day Lagged Diesel Price Change")
    ]
    results = []
    for col, label in variables:
        if col in df.columns:
            sub = df[["query_count", col]].dropna()
            if len(sub) >= 10:
                p_r, _ = stats.pearsonr(sub["query_count"], sub[col])
                s_rho, _ = stats.spearmanr(sub["query_count"], sub[col])
                results.append({
                    "variable_x": "KCC Query Demand",
                    "variable_y": label,
                    "pearson_r": round(float(p_r), 4),
                    "spearman_rho": round(float(s_rho), 4),
                    "sample_size": len(sub),
                    "note": "Linear correlation (Pearson) and rank correlation (Spearman)."
                })
    return results


def run_hypothesis_tests(df: pd.DataFrame, diesel_shock_threshold_pct: float = 1.0) -> Dict[str, Any]:
    """
    Executes formal econometric tests for Hypotheses A, B, and C.
    Reports research question, hypotheses, test statistic, p-value, effect size,
    assumptions (including time-series autocorrelation), and limitations.
    """
    results = []

    # -------------------------------------------------------------
    # Hypothesis A: Commodity Price Movements vs Information Demand
    # -------------------------------------------------------------
    if "commodity_pct_change" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "commodity_pct_change"]].dropna()
        if len(sub) >= 15:
            r, p = stats.pearsonr(sub["query_count"], sub["commodity_pct_change"])
            reject = bool(p < 0.05)
            verdict = f"Reject null hypothesis (r={r:.4f}, p={p:.4f})" if reject else f"Fail to reject null hypothesis (r={r:.4f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-A",
                "title": "Commodity Price Movements vs Query Demand",
                "research_question": "Do day-to-day percentage changes in wholesale commodity prices linearly correlate with KCC advisory query volume?",
                "null_hypothesis": "Daily commodity percentage changes have no linear correlation with farmer query volume (r = 0).",
                "alternative_hypothesis": "Daily commodity percentage changes are linearly correlated with farmer query volume (r != 0).",
                "test_used": "Pearson Linear Correlation Test",
                "sample_size": len(sub),
                "test_statistic": round(float(r), 4),
                "p_value": round(float(p), 5),
                "effect_size": round(float(r), 4),
                "significance_level": 0.05,
                "reject_null": reject,
                "verdict_plain_english": verdict,
                "assumptions": "Assumes linear relationship and bivariate normality. Time-series autocorrelation can artificially narrow standard errors.",
                "limitations": "Linear correlation does not imply causality; price shocks may have delayed non-linear effects not captured by contemporaneous Pearson r."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-A",
                "title": "Commodity Price Movements vs Query Demand",
                "research_question": "Do commodity price changes associate with query volume?",
                "null_hypothesis": "No correlation.",
                "alternative_hypothesis": "Correlation exists.",
                "test_used": "Pearson Linear Correlation Test",
                "sample_size": len(sub),
                "test_statistic": None, "p_value": None, "effect_size": None,
                "significance_level": 0.05, "reject_null": False,
                "verdict_plain_english": "Insufficient observations to run test.",
                "assumptions": "Requires >= 15 paired observations.",
                "limitations": "Insufficient sample."
            })

    # -------------------------------------------------------------
    # Hypothesis B: Diesel Fuel Price Shocks vs Advisory Influx
    # -------------------------------------------------------------
    if "diesel_pct_change" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "diesel_pct_change"]].dropna().copy()
        is_shock = sub["diesel_pct_change"].abs() >= diesel_shock_threshold_pct
        shock_q = sub[is_shock]["query_count"]
        norm_q = sub[~is_shock]["query_count"]

        if len(shock_q) >= 5 and len(norm_q) >= 15:
            u_stat, p = stats.mannwhitneyu(shock_q, norm_q, alternative="two-sided")
            reject = bool(p < 0.05)
            mean_diff = float(shock_q.mean() - norm_q.mean())
            verdict = f"Reject null hypothesis (U={u_stat:.1f}, p={p:.4f}, mean shock diff={mean_diff:+.1f} queries)" if reject else f"Fail to reject null hypothesis (U={u_stat:.1f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-B",
                "title": "Diesel Price Shocks vs Advisory Influx",
                "research_question": "Do days experiencing sudden retail diesel price revisions trigger significantly different farmer call volumes than normal days?",
                "null_hypothesis": "KCC query distribution on fuel shock days is identical to non-shock days.",
                "alternative_hypothesis": "KCC query distribution differs significantly on fuel shock days.",
                "test_used": "Mann-Whitney U Non-Parametric Rank Sum Test",
                "sample_size": len(shock_q) + len(norm_q),
                "test_statistic": round(float(u_stat), 2),
                "p_value": round(float(p), 5),
                "effect_size": round(mean_diff, 2),
                "significance_level": 0.05,
                "reject_null": reject,
                "verdict_plain_english": verdict,
                "assumptions": "Does not assume normal distribution. Assumes independence of observations between groups.",
                "limitations": f"Shock defined as |daily diesel change| >= {diesel_shock_threshold_pct}%. Identified {len(shock_q)} shock days vs {len(norm_q)} baseline days."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-B",
                "title": "Diesel Price Shocks vs Advisory Influx",
                "research_question": "Do diesel price shocks trigger advisory demand shifts?",
                "null_hypothesis": "Query demand is identical during shock and normal fuel days.",
                "alternative_hypothesis": "Query demand differs significantly during diesel price shocks.",
                "test_used": "Mann-Whitney U Test",
                "sample_size": len(shock_q) + len(norm_q),
                "test_statistic": None, "p_value": None, "effect_size": None,
                "significance_level": 0.05, "reject_null": False,
                "verdict_plain_english": f"Too few diesel price shocks detected ({len(shock_q)} shock days with |change| >= {diesel_shock_threshold_pct}%).",
                "assumptions": "Requires >= 5 shock days and >= 15 normal days.",
                "limitations": "Fuel price revisions occur intermittently in administered pricing regimes."
            })

    # -------------------------------------------------------------
    # Hypothesis C: Wholesale-to-Retail Price Spreads vs Advisory Demand
    # -------------------------------------------------------------
    if "price_spread" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "price_spread"]].dropna()
        if len(sub) >= 15:
            rho, p = stats.spearmanr(sub["query_count"], sub["price_spread"])
            reject = bool(p < 0.05)
            verdict = f"Reject null hypothesis (rho={rho:.4f}, p={p:.4f})" if reject else f"Fail to reject null hypothesis (rho={rho:.4f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-C",
                "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "research_question": "Is the spread between wholesale mandi price and retail consumer price monotonically associated with farmer query demand?",
                "null_hypothesis": "There is no monotonic rank association between price spread and KCC query demand (rho = 0).",
                "alternative_hypothesis": "Price spread and KCC query demand are monotonically associated (rho != 0).",
                "test_used": "Spearman Rank-Order Correlation Test",
                "sample_size": len(sub),
                "test_statistic": round(float(rho), 4),
                "p_value": round(float(p), 5),
                "effect_size": round(float(rho), 4),
                "significance_level": 0.05,
                "reject_null": reject,
                "verdict_plain_english": verdict,
                "assumptions": "Monotonic relationship; does not assume linear bivariate normality.",
                "limitations": "Wholesale-retail spread is observable only where matching commodity retail observations exist."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-C",
                "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "research_question": "Does wholesale-retail spread associate with queries?",
                "null_hypothesis": "No monotonic correlation.",
                "alternative_hypothesis": "Monotonic correlation exists.",
                "test_used": "Spearman Rank-Order Correlation Test",
                "sample_size": len(sub),
                "test_statistic": None, "p_value": None, "effect_size": None,
                "significance_level": 0.05, "reject_null": False,
                "verdict_plain_english": "Retail price data unavailable to calculate spread.",
                "assumptions": "Requires matched wholesale and retail price records.",
                "limitations": "Wholesale mandi logs do not always record consumer retail prices."
            })

    return {
        "run_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
        "disclaimer": "Tests demonstrate statistical association in this sample, not economic causation."
    }


# =====================================================================
# TABLE EXPORT FUNCTIONS — CSV OUTPUTS IN outputs/tables/
# =====================================================================

def save_analysis_tables(df: pd.DataFrame, db: Session) -> Dict[str, str]:
    """
    Saves clean CSV tables for descriptive stats, correlations, hypotheses,
    and regional summaries into outputs/tables/.
    """
    tables_dir = OUTPUTS_DIR / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    saved = {}

    # 1. Descriptive statistics table
    stats_data = get_descriptive_summary(df)
    if stats_data["descriptive_statistics"]:
        df_stats = pd.DataFrame(stats_data["descriptive_statistics"])
        path_stats = tables_dir / "descriptive_statistics.csv"
        df_stats.to_csv(path_stats, index=False)
        saved["descriptive_statistics"] = str(path_stats)

    # 2. Correlation table
    corrs = get_correlations(df)
    if corrs:
        df_corrs = pd.DataFrame(corrs)
        path_corrs = tables_dir / "correlations.csv"
        df_corrs.to_csv(path_corrs, index=False)
        saved["correlations"] = str(path_corrs)

    # 3. Hypothesis testing table
    hyp = run_hypothesis_tests(df)
    if hyp["results"]:
        df_hyp = pd.DataFrame(hyp["results"])
        path_hyp = tables_dir / "hypothesis_tests.csv"
        df_hyp.to_csv(path_hyp, index=False)
        saved["hypothesis_tests"] = str(path_hyp)

    # 4. Regional summary table
    reg = get_regional_summary(db)
    if reg:
        df_reg = pd.DataFrame(reg)
        path_reg = tables_dir / "regional_summary.csv"
        df_reg.to_csv(path_reg, index=False)
        saved["regional_summary"] = str(path_reg)

    return saved


# =====================================================================
# CHART FUNCTIONS — SIMPLE AND DIRECT
# =====================================================================

def plot_query_demand_over_time(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4.5))
    plt.plot(df["observation_date"], df["query_count"], label="Daily KCC Queries", color="#3b82f6", alpha=0.5)
    plt.plot(df["observation_date"], df["query_count"].rolling(14, min_periods=2).mean(), label="14-Day Rolling Average", color="#ef4444", linewidth=2)
    plt.title("Kisan Call Centre (KCC) Query Influx Over Time")
    plt.xlabel("Date")
    plt.ylabel("Inquiry Volume")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_seasonality(df: pd.DataFrame, output_path: Path):
    temp = df.copy()
    temp["day"] = temp["observation_date"].dt.day_name()
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    avg_by_day = temp.groupby("day")["query_count"].mean().reindex(days_order)

    plt.figure(figsize=(8, 4))
    sns.barplot(x=avg_by_day.index, y=avg_by_day.values, color="#10b981")
    plt.title("Average KCC Query Volume by Day of Week")
    plt.xlabel("Day of Week")
    plt.ylabel("Mean Inquiries")
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_commodity_trends(df: pd.DataFrame, output_path: Path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(df["observation_date"], df["wholesale_price"], label="Wholesale Mandi Price", color="#059669")
    ax1.set_ylabel("Price (INR/Quintal)")
    ax1.set_title("A. Agricultural Commodity Wholesale Price Movement")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend()

    if "commodity_volatility_7d" in df.columns:
        ax2.plot(df["observation_date"], df["commodity_volatility_7d"], label="7-Day Rolling Volatility (Std Dev)", color="#d97706")
        ax2.set_ylabel("Volatility (INR)")
        ax2.set_title("B. 7-Day Rolling Price Volatility")
        ax2.grid(True, linestyle=":", alpha=0.5)
        ax2.legend()

    ax2.set_xlabel("Date")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_diesel_trends(df: pd.DataFrame, output_path: Path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(df["observation_date"], df["diesel_price"], label="Retail Diesel Price", color="#db2777")
    ax1.set_ylabel("INR / Litre")
    ax1.set_title("A. Retail Diesel Price Trajectory")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend()

    if "diesel_pct_change" in df.columns:
        ax2.bar(df["observation_date"], df["diesel_pct_change"], color="#9333ea", width=1.0, label="Daily Revision %")
        ax2.axhline(1.5, color="red", linestyle=":", label="Shock Threshold (+1.5%)")
        ax2.axhline(-1.5, color="red", linestyle=":", label="Shock Threshold (-1.5%)")
        ax2.set_ylabel("Daily Change (%)")
        ax2.set_title("B. Daily Diesel Price Shocks (%)")
        ax2.grid(True, linestyle=":", alpha=0.5)
        ax2.legend(fontsize=8)

    ax2.set_xlabel("Date")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_price_spread(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4.5))
    plt.plot(df["observation_date"], df["retail_price"], label="Consumer Retail Price", color="#7c3aed")
    plt.plot(df["observation_date"], df["wholesale_price"], label="Wholesale Mandi Price", color="#16a34a")
    if "price_spread" in df.columns:
        plt.fill_between(df["observation_date"], df["wholesale_price"], df["retail_price"], color="#e9d5ff", alpha=0.5, label="Wholesale-Retail Margin Spread")
    plt.title("Wholesale Mandi vs Consumer Retail Price Spread")
    plt.xlabel("Date")
    plt.ylabel("Price (INR/Quintal)")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_query_vs_economic(df: pd.DataFrame, output_path: Path):
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.plot(df["observation_date"], df["query_count"].rolling(7, min_periods=1).mean(), color="#2563eb", label="KCC Queries (7D Moving Avg)")
    ax1.set_ylabel("Daily Inquiries", color="#2563eb")
    ax1.set_xlabel("Date")

    ax2 = ax1.twinx()
    ax2.plot(df["observation_date"], df["wholesale_price"], color="#ea580c", linestyle="--", label="Wholesale Price (INR/Qtl)")
    ax2.set_ylabel("Wholesale Price (INR/Qtl)", color="#ea580c")

    plt.title("Farmer Information Demand vs Wholesale Commodity Price Movements")
    plt.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_regional_comparison(db: Session, output_path: Path):
    reg = get_regional_summary(db)
    if not reg:
        return
    states = [r["state"] for r in reg]
    totals = [r["total_queries"] for r in reg]

    plt.figure(figsize=(8, 4))
    sns.barplot(x=states, y=totals, hue=states, legend=False, palette="Blues_r")
    plt.title("Cumulative Farmer Information Inquiries by State")
    plt.xlabel("State")
    plt.ylabel("Total Inquiries")
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame, output_path: Path):
    cols = [c for c in ["query_count", "wholesale_price", "retail_price", "diesel_price", "price_spread", "commodity_volatility_7d"] if c in df.columns]
    if len(cols) < 2:
        return
    labels = {
        "query_count": "KCC Queries",
        "wholesale_price": "Wholesale Price",
        "retail_price": "Retail Price",
        "diesel_price": "Diesel Price",
        "price_spread": "Price Spread",
        "commodity_volatility_7d": "7D Volatility"
    }
    sub = df[cols].rename(columns=labels)
    plt.figure(figsize=(7, 5.5))
    sns.heatmap(sub.corr(), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, cbar_kws={'label': 'Pearson Correlation (r)'})
    plt.title("Econometric Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def generate_all_charts(db: Session) -> List[str]:
    """Generates all exploratory analytical charts and saves PNGs into outputs/charts/."""
    charts_dir = OUTPUTS_DIR / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    df = build_analytical_dataset(db, export_csv=True)
    if df.empty:
        return []

    chart_files = [
        (plot_query_demand_over_time, "query_demand_over_time.png"),
        (plot_seasonality, "seasonality_patterns.png"),
        (plot_commodity_trends, "commodity_price_trends.png"),
        (plot_diesel_trends, "diesel_price_trends.png"),
        (plot_price_spread, "price_spreads.png"),
        (plot_query_vs_economic, "query_vs_economic.png"),
        (plot_correlation_heatmap, "correlation_heatmap.png"),
    ]
    paths = []
    for func_plot, fname in chart_files:
        p = charts_dir / fname
        func_plot(df, p)
        paths.append(str(p))

    p_reg = charts_dir / "regional_queries.png"
    plot_regional_comparison(db, p_reg)
    paths.append(str(p_reg))

    return paths


def generate_summary_report(db: Session) -> Dict[str, Any]:
    """
    Compiles a complete, readable markdown research report in outputs/reports/summary_report.md.
    Contains descriptive statistics, hypothesis test breakdowns, forecasting metrics,
    and student viva defense explanations.
    """
    from app.data_processing import get_data_quality_report
    from app.forecasting import generate_forecast

    reports_dir = OUTPUTS_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = build_analytical_dataset(db, export_csv=True)
    quality = get_data_quality_report(db, df)
    stats_data = get_descriptive_summary(df)
    corrs = get_correlations(df)
    hyp_data = run_hypothesis_tests(df)
    fc = generate_forecast(db, horizon_days=14, use_sarimax=True)
    charts = generate_all_charts(db)
    tables = save_analysis_tables(df, db)

    report_path = reports_dir / "summary_report.md"

    # Build Markdown document
    lines = [
        "# AgriStress Analytics — Comprehensive Research Summary Report",
        "",
        f"**Date Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        "**Research Topic:** Econometric and Spatial-Temporal Analysis of Farmer Information Demand: Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress  ",
        f"**Data Provenance:** {'SYNTHETIC DEMONSTRATION DATASET (Offline Development & Testing)' if quality['is_synthetic'] else 'REAL OPERATIONAL DATASET'}  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Problem Formulation",
        "",
        "Agricultural advisory infrastructure, such as India's Kisan Call Centre (KCC) toll-free network, experiences sudden surges in farmer inquiries during periods of market stress. When commodity mandi prices crash, input diesel prices rise sharply, or the margin spread between farmgate wholesale and consumer retail prices expands, farmers face compressed operating margins and seek information regarding market alternatives, storage viability, and government price support.",
        "",
        "This project models daily farmer information demand against key economic and input indicators to:",
        "1. Quantify linear and rank associations between commodity price changes, fuel shocks, wholesale-retail spreads, and KCC call volumes.",
        "2. Formally test three economic hypotheses using SciPy and Statsmodels.",
        "3. Provide out-of-sample time-series demand forecasting using Seasonal Naive baseline and SARIMAX(1,1,1)(1,1,0)[7].",
        "4. Construct a transparent, project-defined **Agricultural Advisory Stress Indicator** to classify expected call centre operational load.",
        "",
        "---",
        "",
        "## 2. Dataset Coverage, Provenance & Quality",
        "",
        f"- **Sample Date Range:** {quality.get('sample_start')} to {quality.get('sample_end')}",
        f"- **Total Calendar Days:** {quality.get('total_calendar_days')}",
        f"- **Observed Query Days:** {quality.get('observed_query_days')}",
        f"- **Unrecorded / Zero Query Days:** {quality.get('zero_or_unrecorded_days')} ({quality.get('missingness_percentage')}%)",
        f"- **Data Quality Assessment:** {quality.get('quality_status')}",
        "",
        "**Quality & Missingness Handling Notes:**",
    ]

    for note in quality.get("quality_notes", []):
        lines.append(f"- {note}")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Descriptive Statistics",
        "",
        "| Variable | Count | Mean | Std Dev | Min | Median | Max | Units |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |"
    ])

    unit_map = {
        "query_count": "Calls / Day",
        "wholesale_price": "INR / Quintal",
        "retail_price": "INR / Quintal",
        "diesel_price": "INR / Litre",
        "price_spread": "INR / Quintal",
        "commodity_volatility_7d": "INR (7D Std)"
    }

    for s in stats_data.get("descriptive_statistics", []):
        u = unit_map.get(s["variable"], "")
        lines.append(f"| `{s['variable']}` | {s['count']:,} | {s['mean']:.2f} | {s['std']:.2f} | {s['min']:.2f} | {s['median']:.2f} | {s['max']:.2f} | {u} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Econometric Correlation Analysis",
        "",
        "| Variable Pair | Pearson $r$ | Spearman $\\rho$ | Sample Size ($N$) | Interpretation |",
        "| :--- | :---: | :---: | :---: | :--- |"
    ])

    for c in corrs:
        interp = "Weak correlation"
        if abs(c["pearson_r"]) > 0.4:
            interp = "Moderate correlation"
        if abs(c["pearson_r"]) > 0.7:
            interp = "Strong correlation"
        lines.append(f"| KCC Demand vs {c['variable_y']} | {c['pearson_r']:.4f} | {c['spearman_rho']:.4f} | {c['sample_size']} | {interp} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Formal Hypothesis Testing Results",
        ""
    ])

    for h in hyp_data["results"]:
        status_label = "REJECT NULL HYPOTHESIS" if h["reject_null"] else "FAIL TO REJECT NULL HYPOTHESIS"
        badge = "🔴" if h["reject_null"] else "⚪"
        lines.extend([
            f"### {badge} {h['hypothesis_code']}: {h['title']}",
            f"- **Research Question:** {h.get('research_question', 'N/A')}",
            f"- **Null Hypothesis ($H_0$):** {h['null_hypothesis']}",
            f"- **Alternative Hypothesis ($H_1$):** {h['alternative_hypothesis']}",
            f"- **Statistical Test Used:** {h['test_used']} ($N = {h['sample_size']}$)",
            f"- **Test Statistic:** `{h['test_statistic']}` | **p-value:** `{h['p_value']}` | **Significance Level ($\\\\alpha$):** {h['significance_level']}",
            f"- **Outcome:** **{status_label}**",
            f"- **Plain English Verdict:** {h['verdict_plain_english']}",
            f"- **Statistical Assumptions:** {h.get('assumptions', 'Standard test assumptions.')}",
            f"- **Research Limitations:** {h['limitations']}",
            ""
        ])

    lines.extend([
        "---",
        "",
        "## 6. Time-Series Forecasting & Model Validation",
        "",
        f"- **Model Selected:** `{fc['model_name']}`",
        f"- **Evaluation Methodology:** Chronological Train/Test Holdout Split (avoiding future data leakage)",
        f"- **Train Period:** {fc.get('train_start')} to {fc.get('train_end')}",
        f"- **Test Period:** {fc.get('test_start')} to {fc.get('test_end')}",
        f"- **Forecast Horizon:** {fc['horizon_days']} Days",
        "",
        "### Out-of-Sample Holdout Performance Comparison",
        "",
        "| Forecasting Model | MAE (Calls) | RMSE (Calls) | Zero-Safe MAPE (%) | Status |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ])

    base_m = fc.get("baseline_metrics", {})
    lines.append(f"| Seasonal Naive Baseline (7-Day Lag) | {base_m.get('mae', 'N/A')} | {base_m.get('rmse', 'N/A')} | {base_m.get('mape', 'N/A')}% | Benchmark |")
    lines.append(f"| SARIMAX(1,1,1)(1,1,0)[7] | {fc.get('mae', 'N/A')} | {fc.get('rmse', 'N/A')} | {fc.get('mape', 'N/A')}% | **Selected Model** |")

    stress = fc["stress_assessment"]
    lines.extend([
        "",
        "---",
        "",
        "## 7. Agricultural Advisory Stress Indicator",
        "",
        f"- **Operational Stress Category:** `{stress['category'].upper()}`",
        f"- **Historical Baseline Mean:** {stress['historical_baseline_mean']:.1f} inquiries/day",
        f"- **Elevated Stress Threshold:** >= {stress['elevated_threshold']:.1f} inquiries/day (Historical Mean + 0.75 * Std Dev)",
        f"- **High Advisory Stress Threshold:** >= {stress['high_threshold']:.1f} inquiries/day (Historical Mean + 1.75 * Std Dev)",
        f"- **Interpretation:** {stress['explanation']}",
        f"- **Important Operational Disclaimer:** *{stress['disclaimer']}*",
        "",
        "---",
        "",
        "## 8. Artifacts Generated",
        "",
        "### Charts (`outputs/charts/`):",
        *[f"- `outputs/charts/{Path(c).name}`" for c in charts],
        "- `outputs/charts/forecast_evaluation.png` (2-Panel Out-of-Sample Holdout Validation & Future Horizon Forecast)",
        "- `outputs/charts/actual_vs_predicted.png` (Detailed Out-of-Sample Test Comparison)",
        "",
        "### Tables (`outputs/tables/`):",
        *[f"- `{v}`" for v in tables.values()],
        "- `outputs/forecasts/forecast_predictions.csv`",
        "- `outputs/forecasts/forecast_evaluation_metrics.csv`",
        "",
        "---",
        "",
        "## 9. Viva Voce Defense & Methodology Guide for Engineering Students",
        "",
        "1. **Why SARIMAX(1,1,1)(1,1,0)[7]?**",
        "   - Non-seasonal $(1,1,1)$ models autoregression (yesterday's queries influence today), first-differencing eliminates non-stationarity, and moving-average captures short-term shocks.",
        "   - Seasonal $(1,1,0)[7]$ accounts for the weekly 7-day cyclical agricultural pattern (farmers call heavily during weekdays and significantly less on Sundays).",
        "2. **Why compare with a Seasonal Naive baseline?**",
        "   - In time-series research, complex models like SARIMAX must be justified by outperforming a standard benchmark (last week's same-day observation: $y_{t-7}$).",
        "3. **What are the limitations of Pearson Correlation on Time-Series?**",
        "   - Daily time-series data often exhibit serial autocorrelation. Ordinary correlation tests assume independent and identically distributed (i.i.d.) observations, which can inflate test statistics. Therefore, correlation indicates statistical association in this sample, not economic causation.",
        "4. **How are mandi closures and holidays handled?**",
        "   - Mandis are closed on Sundays and gazetted holidays. Commodity wholesale prices are held constant (forward-filled) to preserve continuity without inventing synthetic trade volumes.",
        "",
        "---",
        "*AgriStress Analytics — Automated Academic Research Pipeline Output*"
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "report_filename": report_path.name,
        "report_path": str(report_path),
        "generated_at": datetime.utcnow().isoformat(),
        "chart_paths": charts,
        "status": "SUCCESS"
    }
