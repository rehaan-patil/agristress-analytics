"""
========================================================================================
AGRISTRESS ANALYTICS — FARMER-FRIENDLY RECOMMENDATION ENGINE
========================================================================================

Translates econometric and forecasting analytics into simple, understandable,
and actionable guidance for ordinary farmers in plain English.

Core Principles:
1. Deliver practical conclusions and next steps, not complex mathematical formulas.
2. Avoid technical jargon (no p-values, correlations, SARIMAX, standard deviations).
3. Ground every recommendation strictly in evidence present in the dataset.
4. Avoid unsupported prescriptions (no chemical doses, fertilizer recipes, or rigid
   "sell now / hold" commands).
5. State clear limitations, data provenance, and toll-free assistance channels.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from app.config import OUTPUTS_DIR


def analyze_commodity_trend(df: pd.DataFrame, commodity_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes recent wholesale commodity price trajectory in plain terms.
    Compares the most recent 7 observed days against the previous 7 days (or baseline).
    """
    comm_label = commodity_name if commodity_name else "agricultural produce"
    if df.empty or "wholesale_price" not in df.columns or df["wholesale_price"].dropna().empty:
        return {
            "available": False,
            "headline": f"Wholesale price records are currently unavailable for {comm_label}.",
            "detail": "No recent market price observations were found in the supplied dataset.",
            "action": f"Check today's modal price directly at your nearest APMC mandi notice board or call KCC.",
            "direction": "UNKNOWN",
            "pct_change": 0.0
        }

    valid_prices = df[["observation_date", "wholesale_price"]].dropna().sort_values("observation_date")
    if len(valid_prices) < 3:
        return {
            "available": False,
            "headline": f"Insufficient price records for {comm_label}.",
            "detail": f"Only {len(valid_prices)} price observations exist, which is not enough to establish a trend.",
            "action": "Consult your local agricultural extension officer for prevailing mandi rates.",
            "direction": "INSUFFICIENT",
            "pct_change": 0.0
        }

    # Split into recent 7-day window vs prior window
    window = min(7, len(valid_prices) // 2)
    recent_series = valid_prices.iloc[-window:]
    prior_series = valid_prices.iloc[-2 * window:-window] if len(valid_prices) >= 2 * window else valid_prices.iloc[:-window]

    recent_avg = float(recent_series["wholesale_price"].mean())
    prior_avg = float(prior_series["wholesale_price"].mean()) if not prior_series.empty else recent_avg
    latest_price = float(valid_prices["wholesale_price"].iloc[-1])

    if prior_avg > 0:
        pct_change = round(((recent_avg - prior_avg) / prior_avg) * 100.0, 1)
    else:
        pct_change = 0.0

    recent_start = str(pd.to_datetime(recent_series["observation_date"].min()).date())
    recent_end = str(pd.to_datetime(recent_series["observation_date"].max()).date())

    # Documented threshold: +/- 5.0% change over the window
    if pct_change <= -5.0:
        direction = "FALLING"
        headline = f"Recorded wholesale {comm_label} prices have declined recently."
        detail = (
            f"Between {recent_start} and {recent_end}, average wholesale prices dropped by roughly "
            f"{abs(pct_change):.1f}% (from around Rs {prior_avg:.0f} to Rs {recent_avg:.0f} per quintal). "
            f"The latest recorded price is Rs {latest_price:.0f} per quintal."
        )
        meaning = (
            f"Mandi arrivals may be heavy or buyer demand has softened in recorded markets. "
            f"Taking produce to the first available mandi without checking local rates may result in lower returns."
        )
        actions = [
            f"Compare today's prices across 2 or 3 nearby APMC mandis before loading produce; neighbouring markets often vary by Rs 100–300 per quintal.",
            f"If your crop is non-perishable (such as dry onions or grains) and you have dry, safe storage, consider whether delaying sale fits your financial situation.",
            f"Do not rush into distress selling without checking whether local government minimum support price (MSP) or procurement centres are open in your district."
        ]
    elif pct_change >= 5.0:
        direction = "RISING"
        headline = f"Recorded wholesale {comm_label} prices have improved recently."
        detail = (
            f"Between {recent_start} and {recent_end}, average wholesale prices rose by approximately "
            f"{pct_change:.1f}% (from around Rs {prior_avg:.0f} to Rs {recent_avg:.0f} per quintal). "
            f"The latest recorded price is Rs {latest_price:.0f} per quintal."
        )
        meaning = (
            f"Buyer demand is strong or market arrivals have tightened in recorded markets. "
            f"However, sharp price rises can attract heavy supply from surrounding areas over the next few days."
        )
        actions = [
            f"Confirm current spot prices with a trusted local trader or mandi board before transporting, as high prices can quickly fluctuate when new arrivals enter.",
            f"Factor in transport charges and loading fees before choosing between a local market and a distant city mandi.",
            f"Grade and clean your produce carefully; well-graded lots consistently secure the upper end of the price band during rising markets."
        ]
    else:
        direction = "STABLE"
        headline = f"Recorded wholesale {comm_label} prices have remained relatively steady."
        detail = (
            f"Recent wholesale prices averaged approximately Rs {recent_avg:.0f} per quintal "
            f"(ranging between Rs {valid_prices['wholesale_price'].iloc[-window:].min():.0f} and "
            f"Rs {valid_prices['wholesale_price'].iloc[-window:].max():.0f} per quintal). "
            f"Recent movement was modest ({pct_change:+.1f}%)."
        )
        meaning = (
            f"The market has not experienced sharp short-term price swings in recorded mandis."
        )
        actions = [
            f"Follow your normal harvesting schedule based on crop maturity and local weather conditions.",
            f"Check daily mandi arrivals in the morning before dispatching to avoid afternoon market gluts."
        ]

    return {
        "available": True,
        "direction": direction,
        "pct_change": pct_change,
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions,
        "recent_avg_price": round(recent_avg, 2),
        "latest_price": round(latest_price, 2),
        "period": f"{recent_start} to {recent_end}"
    }


def analyze_spread_trend(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates whether the difference between wholesale mandi price and retail consumer price
    is unusually wide or normal, when matching retail data is present.
    """
    if (
        df.empty
        or "price_spread" not in df.columns
        or df["price_spread"].dropna().empty
        or "retail_price" not in df.columns
        or df["retail_price"].dropna().empty
    ):
        return {
            "available": False,
            "headline": "Wholesale-to-retail price comparison is not available.",
            "detail": "Retail consumer price records are not included in this dataset. We do not invent estimated consumer prices.",
            "action": None
        }

    sub = df[["observation_date", "wholesale_price", "retail_price", "price_spread"]].dropna().sort_values("observation_date")
    if len(sub) < 5:
        return {
            "available": False,
            "headline": "Insufficient retail price observations to compare margins.",
            "detail": "Too few matching wholesale and retail records exist in this sample.",
            "action": None
        }

    recent_sub = sub.iloc[-7:]
    recent_wholesale = float(recent_sub["wholesale_price"].mean())
    recent_retail = float(recent_sub["retail_price"].mean())
    recent_spread = float(recent_sub["price_spread"].mean())
    hist_spread_mean = float(sub["price_spread"].mean())

    if recent_wholesale > 0:
        retail_margin_pct = (recent_spread / recent_wholesale) * 100.0
    else:
        retail_margin_pct = 0.0

    # Wide spread condition: spread > historical mean by 20% OR retail margin > 35%
    if recent_spread > (hist_spread_mean * 1.20) and recent_spread > 500.0:
        status = "WIDE"
        headline = "The gap between mandi wholesale prices and city retail prices is currently wide."
        detail = (
            f"In recorded markets, wholesale prices average Rs {recent_wholesale:.0f} per quintal while "
            f"consumer retail prices average Rs {recent_retail:.0f} per quintal—a difference of Rs {recent_spread:.0f} per quintal "
            f"({retail_margin_pct:.0f}% above wholesale)."
        )
        meaning = (
            "A wide spread means city consumers are paying substantially more than what farmers receive at the mandi gate. "
            "This difference reflects handling, packaging, transportation, middleman margins, and retailer overheads. "
            "It does not automatically mean higher profit for the farmer."
        )
        actions = [
            "If your village has a Farmer Producer Organization (FPO) or collective marketing group, consider selling through them to reduce intermediary handling losses.",
            "Where feasible, look into local weekly farmers' markets (Apni Mandi / Rythu Bazaar / Shetkari Mandi) where produce can be sold directly to consumers for a better share of the final rupee."
        ]
    else:
        status = "NORMAL"
        headline = "The wholesale-to-retail price spread is within typical ranges."
        detail = (
            f"Wholesale prices average Rs {recent_wholesale:.0f}/quintal and retail averages Rs {recent_retail:.0f}/quintal "
            f"(margin spread of Rs {recent_spread:.0f}/quintal)."
        )
        meaning = "Price transmission between mandi and retail outlets appears consistent with standard local handling costs."
        actions = [
            "Focus on clean sorting and grading at the field level, which helps command the best price tier within standard mandi margins."
        ]

    return {
        "available": True,
        "status": status,
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions,
        "recent_spread": round(recent_spread, 2),
        "recent_wholesale": round(recent_wholesale, 2),
        "recent_retail": round(recent_retail, 2)
    }


def analyze_fuel_trend(df: pd.DataFrame, shock_threshold_pct: float = 1.0) -> Dict[str, Any]:
    """
    Evaluates whether diesel fuel prices have increased and could impact transport costs.
    """
    if df.empty or "diesel_price" not in df.columns or df["diesel_price"].dropna().empty:
        return {
            "available": False,
            "headline": "Fuel price records are not available.",
            "detail": "Diesel price observations are not included in this dataset.",
            "action": None
        }

    sub = df[["observation_date", "diesel_price"]].dropna().sort_values("observation_date")
    if len(sub) < 3:
        return {
            "available": False,
            "headline": "Insufficient fuel price records.",
            "detail": "Too few fuel observations exist to determine transport cost trends.",
            "action": None
        }

    latest_diesel = float(sub["diesel_price"].iloc[-1])
    prior_diesel = float(sub["diesel_price"].iloc[-min(14, len(sub))])
    change_pct = ((latest_diesel - prior_diesel) / prior_diesel) * 100.0 if prior_diesel > 0 else 0.0

    recent_diff = sub["diesel_price"].diff()
    recent_shocks = int((recent_diff.abs() >= (prior_diesel * (shock_threshold_pct / 100.0))).iloc[-14:].sum()) if len(sub) >= 14 else 0

    if change_pct >= shock_threshold_pct:
        status = "INCREASED"
        headline = "Retail diesel prices have increased recently."
        detail = (
            f"Retail diesel is currently recorded at approximately Rs {latest_diesel:.2f} per litre "
            f"(up {change_pct:.1f}% over recent weeks)."
        )
        meaning = (
            "Higher diesel prices typically lead hired tractor and truck operators to increase transport freight rates. "
            "Transporting produce to a distant market will cost more per bag."
        )
        actions = [
            "Get a firm transport rate quote before loading produce, and calculate whether a higher price at a distant mandi will truly cover the additional fuel and freight expense.",
            "If possible, coordinate with neighbouring farmers to share a single vehicle load and split the hiring cost."
        ]
    elif change_pct <= -shock_threshold_pct:
        status = "DECREASED"
        headline = "Retail diesel prices have decreased slightly."
        detail = f"Retail diesel is recorded at approximately Rs {latest_diesel:.2f} per litre ({change_pct:.1f}% over recent weeks)."
        meaning = "Transport operational costs have eased slightly, though freight rates often adjust with a delay."
        actions = [
            "Verify standard local vehicle hiring rates with fellow growers before agreeing to transportation charges."
        ]
    elif recent_shocks > 0:
        status = "REVISED"
        headline = "Recent diesel price revisions have been observed."
        detail = (
            f"Retail diesel is recorded at approximately Rs {latest_diesel:.2f} per litre, with intermittent price adjustments over recent weeks."
        )
        meaning = "Fuel prices have fluctuated recently. Transport operators may adjust freight quotes on short notice."
        actions = [
            "Check current local vehicle hiring rates with fellow growers before agreeing to transportation charges."
        ]
    else:
        status = "STABLE"
        headline = "Diesel fuel prices have remained steady."
        detail = f"Retail diesel is stable at approximately Rs {latest_diesel:.2f} per litre."
        meaning = "Fuel-driven transport expenses have not experienced significant sudden changes in recorded areas."
        actions = [
            "Transport produce according to your customary logistics arrangement."
        ]

    return {
        "available": True,
        "status": status,
        "latest_diesel": round(latest_diesel, 2),
        "change_pct": round(change_pct, 1),
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions
    }


def analyze_advisory_demand(forecast_res: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Translates KCC query forecasting and advisory-stress classification into practical advice.
    """
    if not forecast_res or "stress_assessment" not in forecast_res:
        return {
            "available": False,
            "headline": "Advisory service demand forecast is unavailable.",
            "detail": "Sufficient time-series history was not available to project farmer call volumes.",
            "action": None
        }

    stress = forecast_res.get("stress_assessment", {})
    category = str(stress.get("category", "Normal")).upper()
    horizon = forecast_res.get("horizon_days", 14)
    model = forecast_res.get("model_name", "Baseline")

    predictions = forecast_res.get("predictions", [])
    if predictions:
        pred_means = [p["predicted_demand"] for p in predictions]
        avg_forecast = float(np.mean(pred_means))
    else:
        avg_forecast = float(stress.get("historical_baseline_mean", 0.0))

    base_mean = float(stress.get("historical_baseline_mean", 0.0))

    if category == "HIGH":
        headline = "Unusually high farmer advisory demand is expected in this region."
        detail = (
            f"Over the next {horizon} days, our demand model projects elevated inquiry volumes "
            f"(averaging around {avg_forecast:.0f} daily calls, compared to the normal baseline of {base_mean:.0f} calls)."
        )
        meaning = (
            "Many farmers in your area are likely facing similar weather, market, or crop management challenges. "
            "Advisory phone lines and local extension offices may experience higher call volumes and longer waiting times during mid-day hours."
        )
        actions = [
            "If you need guidance on market alternatives, crop protection, or government schemes, dial Kisan Call Centre (Toll-Free 1800-180-1551) early in the morning (7:00 AM – 9:00 AM) to connect with an expert faster.",
            "You can also reach out in person to your local Gram Panchayat Agriculture Assistant (Krishi Sahayak / Kisan Salahkar) for localized support."
        ]
    elif category == "ELEVATED":
        headline = "Moderately elevated demand for agricultural information is expected."
        detail = (
            f"Forecasted call activity over the next {horizon} days ({avg_forecast:.0f} calls/day) "
            f"is above typical historical levels ({base_mean:.0f} calls/day)."
        )
        meaning = (
            "More farmers than usual are seeking guidance regarding seasonal tasks or market conditions."
        )
        actions = [
            "Reach out to Kisan Call Centre (1800-180-1551) ahead of urgent field operations rather than waiting until the last moment."
        ]
    else:
        headline = "Advisory support lines are operating under normal conditions."
        detail = (
            f"Expected inquiry demand ({avg_forecast:.0f} calls/day) is within standard historical parameters "
            f"(baseline: {base_mean:.0f} calls/day)."
        )
        meaning = "Advisory infrastructure is not under operational strain in this region."
        actions = [
            "Kisan Call Centre (1800-180-1551) is readily accessible for any routine crop, seed, or fertilizer questions."
        ]

    return {
        "available": True,
        "category": category,
        "avg_forecast": round(avg_forecast, 1),
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions
    }


def generate_farmer_recommendations(
    df: pd.DataFrame,
    forecast_res: Optional[Dict[str, Any]] = None,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    quality: Optional[Dict[str, Any]] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Main entry point: Evaluates all available data modules and creates both Markdown (.md)
    and plain text (.txt) farmer-friendly advisory reports.
    """
    if output_dir is None:
        reports_dir = OUTPUTS_DIR / "reports"
    else:
        reports_dir = Path(output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Evaluate individual modules
    comm_analysis = analyze_commodity_trend(df, commodity_name=commodity)
    spread_analysis = analyze_spread_trend(df)
    fuel_analysis = analyze_fuel_trend(df)
    advisory_analysis = analyze_advisory_demand(forecast_res)

    # 2. Geography, Commodity, and Temporal Context
    region_label = state if state else "Multi-State Region (Overall Sample)"
    commodity_label = commodity if commodity else "Major Agricultural Commodities"

    if quality and quality.get("sample_start") and quality.get("sample_end"):
        period_label = f"{quality['sample_start']} to {quality['sample_end']}"
        is_synthetic = bool(quality.get("is_synthetic", False))
    elif not df.empty and "observation_date" in df.columns:
        period_label = f"{df['observation_date'].min().date()} to {df['observation_date'].max().date()}"
        is_synthetic = bool(df.get("is_synthetic", [False]).iloc[0]) if "is_synthetic" in df else False
    else:
        period_label = "Current Observation Window"
        is_synthetic = False

    # 3. Detect Combined Multiple Changes
    combined_alert = None
    if (
        comm_analysis.get("direction") == "FALLING"
        and fuel_analysis.get("status") == "INCREASED"
    ):
        combined_alert = (
            "SPECIAL CAUTION (Simultaneous Price Drop & Fuel Hike):\n"
            "Both declining commodity prices and rising diesel fuel costs are recorded at the same time. "
            "Do NOT dispatch produce to distant city mandis without confirming in advance that the price "
            "difference will cover the higher transport hiring rates. Prioritize selling at nearby markets "
            "or pooling transport loads with neighbours."
        )

    # 4. Synthesize Top Actionable Steps (Consolidate into 3-4 clear priorities)
    recommended_steps: List[str] = []
    
    # Priority 1: Commodity market action
    if comm_analysis.get("actions"):
        recommended_steps.append(comm_analysis["actions"][0])

    # Priority 2: Fuel / Transport or Spread alternative
    if fuel_analysis.get("status") == "INCREASED" and fuel_analysis.get("actions"):
        recommended_steps.append(fuel_analysis["actions"][0])
    elif spread_analysis.get("status") == "WIDE" and spread_analysis.get("actions"):
        recommended_steps.append(spread_analysis["actions"][0])
    elif len(comm_analysis.get("actions", [])) > 1:
        recommended_steps.append(comm_analysis["actions"][1])

    # Priority 3: Advisory Support
    if advisory_analysis.get("actions"):
        recommended_steps.append(advisory_analysis["actions"][0])
    else:
        recommended_steps.append(
            "For individual crop protection, weather alerts, or market advice, call the Kisan Call Centre (Toll-Free 1800-180-1551)."
        )

    # Ensure uniqueness while preserving order
    seen = set()
    deduped_steps = []
    for step in recommended_steps:
        if step not in seen:
            seen.add(step)
            deduped_steps.append(step)
    recommended_steps = deduped_steps[:4]

    # 5. Build Markdown Advisory Document
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    md_lines = [
        "# Agricultural Information and Market Advisory",
        "",
        f"**Region:** {region_label}  ",
        f"**Commodity:** {commodity_label}  ",
        f"**Information Period:** {period_label}  ",
        f"**Report Generated:** {now_str}  ",
        "",
        "---",
        "",
        "## 1. What is Happening?",
        "",
        f"**Market Price Movement:** {comm_analysis['headline']}",
        f"{comm_analysis['detail']}",
        ""
    ]

    if spread_analysis["available"]:
        md_lines.extend([
            f"**Wholesale vs Retail Margin:** {spread_analysis['headline']}",
            f"{spread_analysis['detail']}",
            ""
        ])

    if fuel_analysis["available"]:
        md_lines.extend([
            f"**Transport & Fuel Expenses:** {fuel_analysis['headline']}",
            f"{fuel_analysis['detail']}",
            ""
        ])

    if advisory_analysis["available"]:
        md_lines.extend([
            f"**Advisory Service Influx:** {advisory_analysis['headline']}",
            f"{advisory_analysis['detail']}",
            ""
        ])

    if combined_alert:
        md_lines.extend([
            "> [!WARNING]",
            f"> **{combined_alert.replace(chr(10), ' ')}**",
            ""
        ])

    md_lines.extend([
        "---",
        "",
        "## 2. What This Means For You",
        "",
        f"- {comm_analysis.get('meaning', 'Review local prices before making marketing decisions.')}"
    ])

    if spread_analysis.get("available") and spread_analysis.get("meaning"):
        md_lines.append(f"- {spread_analysis['meaning']}")

    if fuel_analysis.get("available") and fuel_analysis.get("meaning"):
        md_lines.append(f"- {fuel_analysis['meaning']}")

    if advisory_analysis.get("available") and advisory_analysis.get("meaning"):
        md_lines.append(f"- {advisory_analysis['meaning']}")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Recommended Next Steps",
        ""
    ])

    for idx, act in enumerate(recommended_steps, start=1):
        md_lines.append(f"{idx}. {act}")

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. How Certain is This Information?",
        ""
    ])

    if is_synthetic:
        md_lines.extend([
            "- **Data Provenance:** This advisory was generated from a **synthetic demonstration dataset** created for local student testing and research illustration.",
            "- **Important Notice:** The numbers reflect simulated demonstration patterns and should **not** be used as investment or financial advice for real farming operations."
        ])
    else:
        md_lines.extend([
            "- **Data Provenance:** This advisory was generated from recorded operational observations.",
            "- **Coverage:** Market conditions reflect reporting mandis and may vary by specific APMC yard or village."
        ])

    md_lines.extend([
        "- **Forecasts are Estimates:** Future demand and price estimates are mathematical projections based on historical patterns, not guaranteed outcomes. Sudden weather events, government policy changes, or localized road closures can rapidly change conditions.",
        "",
        "---",
        "",
        "## 5. Important Limitations (What We Do NOT Prescribe)",
        "",
        "- **No Prescriptions:** This system analyzes market and advisory trends. It does **not** know your individual farm debt, soil type, crop variety, field storage facilities, or cash flow needs.",
        "- **No Agronomic Recipes:** We do **not** prescribe chemical pesticide dosages, fertilizer applications, or irrigation schedules. For crop protection, plant disease diagnosis, or soil treatment, contact a qualified agronomist at your nearest Krishi Vigyan Kendra (KVK) or telephone the Kisan Call Centre at **1800-180-1551** (Toll-Free, 6:00 AM to 10:00 PM daily).",
        "",
        "---",
        "*AgriStress Analytics — Simple, Actionable Farmer Advisory Output*"
    ])

    md_content = "\n".join(md_lines)
    md_path = reports_dir / "farmer_advisory.md"
    md_path.write_text(md_content, encoding="utf-8")

    # 6. Build Plain Text Version (.txt) for SMS/WhatsApp/Terminal
    txt_lines = [
        "========================================================================",
        "             AGRICULTURAL INFORMATION AND MARKET ADVISORY",
        "========================================================================",
        f"Region:             {region_label}",
        f"Commodity:          {commodity_label}",
        f"Information Period: {period_label}",
        f"Generated At:       {now_str}",
        "------------------------------------------------------------------------",
        "",
        "1. WHAT IS HAPPENING?",
        f"  * Price:    {comm_analysis['headline']}",
        f"              {comm_analysis['detail']}",
    ]
    if spread_analysis["available"]:
        txt_lines.append(f"  * Margin:   {spread_analysis['headline']}")
    if fuel_analysis["available"]:
        txt_lines.append(f"  * Fuel:     {fuel_analysis['headline']}")
    if advisory_analysis["available"]:
        txt_lines.append(f"  * Advisory: {advisory_analysis['headline']}")

    if combined_alert:
        txt_lines.extend([
            "",
            "  *** ALERT: Simultaneous falling prices and rising fuel costs! ***",
            "  Avoid long-distance transport without guaranteed buyer commitments."
        ])

    txt_lines.extend([
        "",
        "2. WHAT THIS MEANS FOR YOU:",
        f"  * {comm_analysis.get('meaning', 'Check current prices before selling.')}",
    ])
    if fuel_analysis.get("available") and fuel_analysis.get("status") == "INCREASED":
        txt_lines.append(f"  * {fuel_analysis['meaning']}")

    txt_lines.extend([
        "",
        "3. RECOMMENDED NEXT STEPS:",
    ])
    for idx, act in enumerate(recommended_steps, start=1):
        txt_lines.append(f"  {idx}. {act}")

    txt_lines.extend([
        "",
        "4. ASSISTANCE & SUPPORT:",
        "  * Kisan Call Centre (Toll-Free): 1800-180-1551 (6:00 AM - 10:00 PM)",
        "  * Contact your local village Krishi Sahayak or nearest KVK agronomist.",
        "",
        "5. IMPORTANT NOTICE:",
        f"  * Data Provenance: {'SYNTHETIC DEMO DATA' if is_synthetic else 'OPERATIONAL DATA'}.",
        "  * Estimates are not guaranteed future prices. Farm decisions depend on local conditions.",
        "========================================================================"
    ])

    txt_content = "\n".join(txt_lines)
    txt_path = reports_dir / "farmer_advisory.txt"
    txt_path.write_text(txt_content, encoding="utf-8")

    return {
        "report_md_path": str(md_path),
        "report_txt_path": str(txt_path),
        "region": region_label,
        "commodity": commodity_label,
        "period": period_label,
        "is_synthetic": is_synthetic,
        "price_direction": comm_analysis.get("direction"),
        "price_headline": comm_analysis["headline"],
        "price_pct_change": comm_analysis.get("pct_change", 0.0),
        "fuel_status": fuel_analysis.get("status"),
        "spread_status": spread_analysis.get("status"),
        "advisory_stress": advisory_analysis.get("category"),
        "recommended_steps": recommended_steps,
        "combined_alert": combined_alert,
        "status": "SUCCESS"
    }
