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


def run_hypothesis_tests(df: pd.DataFrame, diesel_shock_threshold_pct: float = 2.0) -> Dict[str, Any]:
    """Runs tests for Hypothesis A (commodity return), B (diesel shocks), and C (price spread)."""
    results = []

    # Hypothesis A: Commodity price movements
    if "commodity_pct_change" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "commodity_pct_change"]].dropna()
        if len(sub) >= 15:
            r, p = stats.pearsonr(sub["query_count"], sub["commodity_pct_change"])
            reject = bool(p < 0.05)
            verdict = f"Reject null hypothesis (r={r:.4f}, p={p:.4f})" if reject else f"Fail to reject null hypothesis (r={r:.4f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-A", "title": "Commodity Price Movements vs Query Demand",
                "null_hypothesis": "Commodity price changes have no linear association with KCC query demand.",
                "alternative_hypothesis": "Commodity price changes are associated with KCC query demand.",
                "test_used": "Pearson Correlation Test", "sample_size": len(sub),
                "test_statistic": round(float(r), 4), "p_value": round(float(p), 5), "effect_size": round(float(r), 4),
                "significance_level": 0.05, "reject_null": reject, "verdict_plain_english": verdict,
                "limitations": "Correlation does not imply economic causation."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-A", "title": "Commodity Price Movements vs Query Demand",
                "null_hypothesis": "No association.", "alternative_hypothesis": "Association exists.",
                "test_used": "Pearson Correlation Test", "sample_size": len(sub),
                "test_statistic": None, "p_value": None, "effect_size": None, "significance_level": 0.05,
                "reject_null": False, "verdict_plain_english": "Insufficient observations to run test.", "limitations": "Need >= 15 points."
            })

    # Hypothesis B: Diesel price shocks
    if "diesel_pct_change" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "diesel_pct_change"]].dropna().copy()
        is_shock = sub["diesel_pct_change"].abs() >= diesel_shock_threshold_pct
        shock_q = sub[is_shock]["query_count"]
        norm_q = sub[~is_shock]["query_count"]
        if len(shock_q) >= 5 and len(norm_q) >= 15:
            u_stat, p = stats.mannwhitneyu(shock_q, norm_q, alternative="two-sided")
            reject = bool(p < 0.05)
            verdict = f"Reject null hypothesis (U={u_stat:.1f}, p={p:.4f})" if reject else f"Fail to reject null hypothesis (U={u_stat:.1f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-B", "title": "Diesel Price Shocks vs Advisory Influx",
                "null_hypothesis": "Query demand is identical during shock and normal fuel price days.",
                "alternative_hypothesis": "Query demand differs significantly during diesel price shocks.",
                "test_used": "Mann-Whitney U Two-Sample Rank Sum Test", "sample_size": len(shock_q) + len(norm_q),
                "test_statistic": round(float(u_stat), 2), "p_value": round(float(p), 5), "effect_size": round(float(shock_q.mean() - norm_q.mean()), 2),
                "significance_level": 0.05, "reject_null": reject, "verdict_plain_english": verdict,
                "limitations": f"Shock defined as |diesel change| >= {diesel_shock_threshold_pct}%."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-B", "title": "Diesel Price Shocks vs Advisory Influx",
                "null_hypothesis": "No difference.", "alternative_hypothesis": "Difference exists.",
                "test_used": "Mann-Whitney U Test", "sample_size": len(shock_q) + len(norm_q),
                "test_statistic": None, "p_value": None, "effect_size": None, "significance_level": 0.05,
                "reject_null": False, "verdict_plain_english": f"Too few diesel price shocks detected ({len(shock_q)} shock days).", "limitations": "Need >= 5 shock days."
            })

    # Hypothesis C: Wholesale-to-retail spread
    if "price_spread" in df.columns and "query_count" in df.columns:
        sub = df[["query_count", "price_spread"]].dropna()
        if len(sub) >= 15:
            rho, p = stats.spearmanr(sub["query_count"], sub["price_spread"])
            reject = bool(p < 0.05)
            verdict = f"Reject null hypothesis (rho={rho:.4f}, p={p:.4f})" if reject else f"Fail to reject null hypothesis (rho={rho:.4f}, p={p:.4f})"
            results.append({
                "hypothesis_code": "HYP-C", "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "null_hypothesis": "Price spread has no rank association with query influx.",
                "alternative_hypothesis": "Price spread is correlated with query influx.",
                "test_used": "Spearman Rank Correlation Test", "sample_size": len(sub),
                "test_statistic": round(float(rho), 4), "p_value": round(float(p), 5), "effect_size": round(float(rho), 4),
                "significance_level": 0.05, "reject_null": reject, "verdict_plain_english": verdict,
                "limitations": "Retail price data is only available for select commodities."
            })
        else:
            results.append({
                "hypothesis_code": "HYP-C", "title": "Wholesale-to-Retail Price Spreads vs Query Influx",
                "null_hypothesis": "No association.", "alternative_hypothesis": "Association exists.",
                "test_used": "Spearman Rank Correlation Test", "sample_size": len(sub),
                "test_statistic": None, "p_value": None, "effect_size": None, "significance_level": 0.05,
                "reject_null": False, "verdict_plain_english": "Retail prices unavailable to calculate spread.", "limitations": "Mandi logs wholesale only."
            })

    return {
        "run_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
        "disclaimer": "Tests demonstrate statistical association in this sample, not economic causation."
    }


# =====================================================================
# CHART FUNCTIONS — SIMPLE AND DIRECT
# =====================================================================

def plot_query_demand_over_time(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4))
    plt.plot(df["observation_date"], df["query_count"], label="Daily Queries", color="#3b82f6", alpha=0.5)
    plt.plot(df["observation_date"], df["query_count"].rolling(14, min_periods=2).mean(), label="14D Average", color="#ef4444", linewidth=2)
    plt.title("Kisan Call Centre (KCC) Query Influx Over Time")
    plt.xlabel("Date")
    plt.ylabel("Query Count")
    plt.legend()
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
    plt.title("Average Query Count by Day of Week")
    plt.xlabel("Day of Week")
    plt.ylabel("Mean Queries")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_commodity_trends(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4))
    plt.plot(df["observation_date"], df["wholesale_price"], label="Wholesale Price (INR/Qtl)", color="#059669")
    plt.title("Commodity Wholesale Price Trend")
    plt.xlabel("Date")
    plt.ylabel("INR / Quintal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_diesel_trends(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4))
    plt.plot(df["observation_date"], df["diesel_price"], label="Diesel Price (INR/Litre)", color="#db2777")
    plt.title("Retail Diesel Price Trajectory")
    plt.xlabel("Date")
    plt.ylabel("INR / Litre")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_price_spread(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(10, 4))
    plt.plot(df["observation_date"], df["retail_price"], label="Retail Price", color="#7c3aed")
    plt.plot(df["observation_date"], df["wholesale_price"], label="Wholesale Price", color="#16a34a")
    if "price_spread" in df.columns:
        plt.fill_between(df["observation_date"], df["wholesale_price"], df["retail_price"], color="#e9d5ff", alpha=0.5, label="Margin Spread")
    plt.title("Wholesale vs Retail Price Spread")
    plt.xlabel("Date")
    plt.ylabel("INR / Quintal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_query_vs_economic(df: pd.DataFrame, output_path: Path):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df["observation_date"], df["query_count"].rolling(7, min_periods=1).mean(), color="#2563eb", label="Queries (7D Avg)")
    ax1.set_ylabel("Daily Queries", color="#2563eb")
    ax2 = ax1.twinx()
    ax2.plot(df["observation_date"], df["wholesale_price"], color="#ea580c", linestyle="--", label="Wholesale Price")
    ax2.set_ylabel("Wholesale Price (INR/Qtl)", color="#ea580c")
    plt.title("Queries vs Wholesale Commodity Prices")
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
    plt.title("Total Inquiries by State")
    plt.xlabel("State")
    plt.ylabel("Total Queries")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame, output_path: Path):
    cols = [c for c in ["query_count", "wholesale_price", "retail_price", "diesel_price", "price_spread", "commodity_volatility_7d"] if c in df.columns]
    if len(cols) < 2:
        return
    plt.figure(figsize=(7, 5))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def generate_all_charts(db: Session) -> List[str]:
    """Generates all 8 analytical charts and saves PNGs into outputs/charts/."""
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
    """Writes a markdown research summary report to outputs/reports/summary_report.md."""
    reports_dir = OUTPUTS_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = build_analytical_dataset(db, export_csv=True)
    stats_data = get_descriptive_summary(df)
    hyp_data = run_hypothesis_tests(df)
    charts = generate_all_charts(db)

    report_path = reports_dir / "summary_report.md"
    lines = [
        "# AgriStress Analytics — Research Summary Report",
        f"Generated At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
        "## 1. Summary Statistics",
        f"- Total Daily Observations: {stats_data['total_observations']}",
        f"- Date Range: {stats_data['sample_period']['start']} to {stats_data['sample_period']['end']}\n",
        "## 2. Hypothesis Testing Results"
    ]
    for r in hyp_data["results"]:
        lines.append(f"- **{r['hypothesis_code']} ({r['title']})**: {r['test_used']} -> {r['verdict_plain_english']}")

    lines.extend([
        "\n## 3. Visualizations Generated",
        *[f"- `{Path(c).name}`" for c in charts],
        "\n## 4. Important Notes",
        "- Correlation does not prove economic causation.",
        "- Advisory stress indicators are project-defined estimates for research demonstration."
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {"report_filename": report_path.name, "report_path": str(report_path), "generated_at": datetime.utcnow().isoformat(), "chart_paths": charts, "status": "SUCCESS"}
