"""
========================================================================================
AGRISTRESS ANALYTICS — ACTIONABLE FARMER DECISION-SUPPORT ADVISORY ENGINE
========================================================================================

Translates econometric and forecasting analytics into simple, understandable,
and actionable decision support for farmers in plain language.

Core Design & Trust Principles:
1. Deliver specific, practical next steps connected to empirical evidence.
2. Avoid technical jargon (no p-values, correlations, SARIMAX, standard deviations).
3. Ground every claim strictly in validated observations; never fabricate numbers.
4. Avoid unsupported prescriptions (no chemical doses, fertilizer recipes, or rigid
   "sell now / hold" commands).
5. Highlight uncertainty, data freshness, and missing information (e.g. transport costs).
6. Support multi-market APMC comparisons when market-level records are present.
7. Support plain English (baseline), Hindi, and Marathi templates deterministically.
8. Provide verified official contact channels: Kisan Call Centre Toll-Free 1800-180-1551
   (operational 6:00 AM to 10:00 PM all 7 days of the week).
"""
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from app.config import OUTPUTS_DIR


# --------------------------------------------------------------------------------------
# Verified Official Agricultural Services Reference
# --------------------------------------------------------------------------------------
VERIFIED_ASSISTANCE = {
    "kcc_toll_free": "1800-180-1551",
    "kcc_hours": "6:00 AM to 10:00 PM, all 7 days of the week",
    "kcc_authority": "Department of Agriculture & Farmers Welfare, Ministry of Agriculture, Govt. of India",
    "kcc_portal": "mkisan.gov.in / dackkms.gov.in",
    "verification_date": "October 2026"
}


# --------------------------------------------------------------------------------------
# Multilingual Template Definitions (Plain English, Hindi, Marathi)
# --------------------------------------------------------------------------------------
UI_STRINGS = {
    "en": {
        "title": "FARMER MARKET AND INFORMATION ADVISORY",
        "region_label": "Region",
        "commodity_label": "Commodity",
        "period_label": "Data period",
        "freshness_label": "Data freshness",
        "priority_label": "Advisory Priority",
        "confidence_label": "Confidence & Uncertainty",
        "situation_hdr": "Situation in one sentence",
        "meaning_hdr": "What this means for your decision",
        "steps_hdr": "Recommended next steps",
        "check_hdr": "What to check before acting",
        "market_hdr": "Market Comparison (APMC Mandis)",
        "evidence_hdr": "Evidence behind this advice",
        "limits_hdr": "Limits of this advisory",
        "priority_now": "Action to consider now",
        "priority_check": "Check before deciding",
        "priority_none": "No clear signal",
        "helpline_msg": "Kisan Call Centre (Toll-Free): 1800-180-1551 (6:00 AM to 10:00 PM daily)",
        "local_support": "Consult your local Gram Panchayat Krishi Sahayak or nearest Krishi Vigyan Kendra (KVK).",
        "msp_msg": "Check whether local government Minimum Support Price (MSP) or procurement centres are active for your crop.",
        "fpo_msg": "Explore collective marketing via a local Farmer Producer Organization (FPO) or weekly direct farmers' market (Apni Mandi / Shetkari Mandi) to reduce intermediary costs.",
        "transport_pool_msg": "Get a firm transport freight quote in advance; consider pooling a vehicle load with neighbouring growers to share hiring expenses.",
        "no_mandi_data": "Market-level comparison across neighbouring mandis is not available in this dataset. The figures represent regional or state-level aggregates. Local APMC records are required before deciding between mandis.",
        "check_transport": "**Transport & Handling Expenses:** Obtain a firm quotation from a local vehicle operator before choosing between mandis. A higher price in a distant city may not cover the extra freight.",
        "check_perishability": "**Crop Perishability:** Highly perishable produce (such as ripe tomatoes) cannot be stored without refrigeration. Evaluate on-farm storage viability before deciding to delay sale.",
        "check_grading": "**Moisture & Quality Grading:** Mandi traders bid based on lot cleanliness, size sorting, and moisture content. Graded produce commands the upper end of the price range.",
        "check_cash": "**Immediate Cash Requirements:** Weigh storage and delayed sale against personal cash needs for input repayment, labor wages, or household expenses."
    },
    "hi": {
        "title": "किसान बाज़ार एवं सूचना सलाह (FARMER MARKET AND INFORMATION ADVISORY)",
        "region_label": "क्षेत्र (Region)",
        "commodity_label": "फसल (Commodity)",
        "period_label": "आंकड़ों की अवधि (Data period)",
        "freshness_label": "आंकड़ों की ताज़गी (Data freshness)",
        "priority_label": "सलाह प्राथमिकता (Advisory Priority)",
        "confidence_label": "विश्वसनीयता एवं अनिश्चितता (Confidence & Uncertainty)",
        "situation_hdr": "एक वाक्य में सद्यस्थिति (Situation in one sentence)",
        "meaning_hdr": "आपके निर्णय के लिए इसका क्या अर्थ है (What this means for your decision)",
        "steps_hdr": "अनुशंसित अगले कदम (Recommended next steps)",
        "check_hdr": "कदम उठाने से पहले क्या जांचें (What to check before acting)",
        "market_hdr": "मंडी भाव तुलना (Market Comparison)",
        "evidence_hdr": "इस सलाह के पीछे के प्रमाण (Evidence behind this advice)",
        "limits_hdr": "इस सलाह की सीमाएं (Limits of this advisory)",
        "priority_now": "तत्काल विचार योग्य कदम (Action to consider now)",
        "priority_check": "निर्णय से पूर्व जांचें (Check before deciding)",
        "priority_none": "कोई असामान्य संकेत नहीं (No clear signal)",
        "helpline_msg": "किसान कॉल सेंटर (टोल-फ्री): 1800-180-1551 (सुबह 6:00 से रात 10:00 बजे तक)",
        "local_support": "स्थानीय कृषि सहायक या निकटतम कृषि विज्ञान केंद्र (KVK) से संपर्क करें।",
        "msp_msg": "जांचें कि क्या आपके जिले में सरकारी न्यूनतम समर्थन मूल्य (MSP) या खरीद केंद्र चालू हैं।",
        "fpo_msg": "बिचौलियों के खर्च घटाने के लिए स्थानीय किसान उत्पादक संगठन (FPO) या साप्ताहिक किसान बाज़ार के माध्यम से बिक्री पर विचार करें।",
        "transport_pool_msg": "गाड़ी बुक करने से पहले भाड़े का पक्का भाव लें; खर्च बांटने के लिए पड़ोसी किसानों के साथ मिलकर माल भेजने पर विचार करें।",
        "no_mandi_data": "इस डेटासेट में अलग-अलग मंडियों के स्तर का डेटा उपलब्ध नहीं है। ये आंकड़े राज्य/क्षेत्रीय औसत हैं। मंडी चुनने से पहले स्थानीय भाव अवश्य जांचें।",
        "check_transport": "**परिवहन एवं तुलाई खर्च:** मंडी चुनने से पहले स्थानीय वाहन चालक से पक्का भाड़ा तय करें। दूर की मंडी का ऊंचा भाव अतिरिक्त भाड़े में डूब सकता है।",
        "check_perishability": "**फसल की जीवन अवधि (नाशवंतता):** जल्द खराब होने वाली फसलें बिना कोल्ड स्टोरेज के नहीं रखी जा सकतीं। बिक्री टालने से पहले खेत या घर पर भंडारण की सुरक्षा जांचें।",
        "check_grading": "**छंटाई एवं ग्रेडिंग:** मंडी में भाव माल की सफाई, आकार और नमी पर निर्भर करता है। साफ और ग्रेडेड माल को अधिकतम भाव मिलता है।",
        "check_cash": "**तत्काल नकदी आवश्यकता:** अगली बुवाई, खाद-बीज के भुगतान या मजदूरी के लिए तुरंत पैसे की जरूरत को ध्यान में रखकर ही भंडारण का निर्णय लें।"
    },
    "mr": {
        "title": "शेतकरी बाज़ार व माहिती सल्ला (FARMER MARKET AND INFORMATION ADVISORY)",
        "region_label": "विभाग (Region)",
        "commodity_label": "शेतमाल (Commodity)",
        "period_label": "माहितीचा कालावधी (Data period)",
        "freshness_label": "माहितीचे ताजेपण (Data freshness)",
        "priority_label": "सल्ला प्राधान्य (Advisory Priority)",
        "confidence_label": "विश्वासार्हता आणि अनिश्चितता (Confidence & Uncertainty)",
        "situation_hdr": "एका वाक्यात सद्यस्थिती (Situation in one sentence)",
        "meaning_hdr": "तुमच्या निर्णयासाठी याचा अर्थ काय (What this means for your decision)",
        "steps_hdr": "पुढील शिफारस केलेल्या कृती (Recommended next steps)",
        "check_hdr": "निर्णय घेण्यापूर्वी काय तपासावे (What to check before acting)",
        "market_hdr": "बाजारभाव तुलना (Market Comparison)",
        "evidence_hdr": "या सल्ल्यामागील पुरावे (Evidence behind this advice)",
        "limits_hdr": "या सल्ल्याच्या मर्यादा (Limits of this advisory)",
        "priority_now": "आता विचार करण्यासारखी कृती (Action to consider now)",
        "priority_check": "निर्णय घेण्यापूर्वी तपासा (Check before deciding)",
        "priority_none": "कोणताही असामान्य संकेत नाही (No clear signal)",
        "helpline_msg": "किसान कॉल सेंटर (टोल-फ्री): 1800-180-1551 (सकाळी 6:00 ते रात्री 10:00 पर्यंत)",
        "local_support": "आपल्या गावातील कृषी सहाय्यक किंवा नजीकच्या कृषी विज्ञान केंद्राशी (KVK) संपर्क साधा.",
        "msp_msg": "आपल्या भागात हमीभाव (MSP) खरेदी केंद्र सुरू आहे का ते तपासा.",
        "fpo_msg": "मध्यस्थांचा खर्च कमी करण्यासाठी स्थानिक शेतकरी उत्पादक कंपनी (FPO) किंवा आठवडी शेतकरी बाजारात विक्रीचा विचार करा.",
        "transport_pool_msg": "वाहतूक भाडे अगोदर पक्के करा; भाड्याचा खर्च विभागण्यासाठी शेजारील शेतकऱ्यांसोबत एकत्र वाहन भाड्याने घेण्याचा विचार करा.",
        "no_mandi_data": "या माहितीमध्ये स्वतंत्र बाजार समित्यांचा (APMC) तपशील उपलब्ध नाही. हे आकडे राज्य/विभागीय सरासरी दर्शवतात. प्रत्यक्ष मंडई निवडण्यापूर्वी स्थानिक भाव नक्की तपासा.",
        "check_transport": "**वाहतूक व हमाली खर्च:** बाजार समिती निवडण्यापूर्वी स्थानिक गाडी मालकाकडून पक्के भाडे ठरवा. लांबच्या बाजारातील जादा भाव वाढीव भाड्यात खर्च होऊ नये.",
        "check_perishability": "**मालाचा टिकाऊपणा:** नाशवंत शेतमाल (उदा. टोमॅटो) जास्त दिवस ठेवता येत नाही. विक्री लांबणीवर टाकण्यापूर्वी सुरक्षित साठवणुकीची खात्री करा.",
        "check_grading": "**प्रतवारी व स्वच्छता:** मालाची प्रतवारी, आकार आणि ओलावा यावर व्यापारी बोली लावतात. प्रतवारी केलेल्या चांगल्या मालाला वरचा भाव मिळतो.",
        "check_cash": "**तातडीची पैशांची गरज:** उधार परतफेड, मजुरी किंवा घरखर्च यासाठी लागणाऱ्या पैशांचा विचार करूनच शेतमाल साठवण्याचा निर्णय घ्यावा."
    }
}


def get_freshness_assessment(
    latest_date_val: Optional[Any],
    ref_date: Optional[date] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Evaluates data recency against a reference date (defaulting to latest available or today).
    Flags stale/historical data with an explicit warning.
    """
    if latest_date_val is None:
        return {
            "status": "UNKNOWN",
            "is_recent": False,
            "days_ago": None,
            "latest_date_str": "Unknown",
            "statement": "Observation date is unavailable. Confirm today's local spot rates before acting."
        }

    try:
        if isinstance(latest_date_val, str):
            parsed_latest = pd.to_datetime(latest_date_val).date()
        elif hasattr(latest_date_val, "date"):
            parsed_latest = latest_date_val.date()
        else:
            parsed_latest = latest_date_val
    except Exception:
        return {
            "status": "UNKNOWN",
            "is_recent": False,
            "days_ago": None,
            "latest_date_str": str(latest_date_val),
            "statement": "Could not determine exact observation date."
        }

    if ref_date is None:
        ref_date = datetime.utcnow().date()

    days_ago = (ref_date - parsed_latest).days
    latest_str = str(parsed_latest)

    # If within 7 days of reference date, consider recent; otherwise historical/stale
    if days_ago <= 7 and days_ago >= 0:
        is_recent = True
        status = "RECENT"
        if lang == "hi":
            statement = f"हालिया आंकड़े (दर्ज तिथि: {latest_str})। ध्यान दें कि मंडी भाव और आवक प्रतिदिन बदलते हैं।"
        elif lang == "mr":
            statement = f"ताजी आकडेवारी (नोंद दिनांक: {latest_str}). बाजारभाव व आवक दररोज बदलू शकतात याची नोंद घ्या."
        else:
            statement = f"Recent observations (recorded on {latest_str}). Mandi spot rates and arrivals fluctuate daily."
    else:
        is_recent = False
        status = "HISTORICAL"
        abs_days = abs(days_ago)
        if lang == "hi":
            statement = f"[ऐतिहासिक आंकड़े] अंतिम दर्ज: {latest_str}, {abs_days} दिन पूर्व। बाज़ार की स्थिति बदल चुकी हो सकती है। माल भेजने से पहले आज के स्थानीय भाव अवश्य जांचें।"
        elif lang == "mr":
            statement = f"[जुनी आकडेवारी] शेवटची नोंद: {latest_str}, {abs_days} दिवसांपूर्वी. प्रत्यक्ष निर्णय घेण्यापूर्वी आजचे स्थानिक बाजारभाव नक्की तपासा."
        else:
            statement = f"[HISTORICAL DATA] Latest record: {latest_str}, {abs_days} days prior. Market conditions may have changed significantly. Confirm current local spot prices before deciding."

    return {
        "status": status,
        "is_recent": is_recent,
        "days_ago": days_ago,
        "latest_date_str": latest_str,
        "statement": statement
    }


def analyze_commodity_trend(
    df: pd.DataFrame,
    commodity_name: Optional[str] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Analyzes recent wholesale commodity price trajectory in plain terms.
    Compares the most recent 7 observed days against the preceding 7-day period.
    Never invents unverified price gaps or rigid 'sell/hold' commands.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])
    comm_label = commodity_name if commodity_name else "agricultural produce"

    if df.empty or "wholesale_price" not in df.columns or df["wholesale_price"].dropna().empty:
        return {
            "available": False,
            "direction": "UNKNOWN",
            "pct_change": 0.0,
            "headline": f"Wholesale price records are currently unavailable for {comm_label}.",
            "detail": "No recent market price observations were found in the supplied dataset.",
            "meaning": "Local market pricing information is needed before making marketing decisions.",
            "actions": [
                f"Check today's modal price directly at your nearest APMC mandi notice board or telephone KCC (1800-180-1551)."
            ],
            "recent_avg": 0.0,
            "prior_avg": 0.0,
            "latest_price": 0.0,
            "latest_date": None,
            "period": "N/A"
        }

    valid_prices = df[["observation_date", "wholesale_price"]].dropna().sort_values("observation_date")
    if len(valid_prices) < 3:
        return {
            "available": False,
            "direction": "INSUFFICIENT",
            "pct_change": 0.0,
            "headline": f"Insufficient price records for {comm_label}.",
            "detail": f"Only {len(valid_prices)} price observations exist, which is not enough to establish a reliable comparison.",
            "meaning": "Sparse price records cannot indicate whether market rates are rising, falling, or steady.",
            "actions": [
                "Consult your local agricultural extension officer or APMC yard for prevailing mandi rates."
            ],
            "recent_avg": 0.0,
            "prior_avg": 0.0,
            "latest_price": float(valid_prices["wholesale_price"].iloc[-1]) if not valid_prices.empty else 0.0,
            "latest_date": str(valid_prices["observation_date"].iloc[-1]) if not valid_prices.empty else None,
            "period": "N/A"
        }

    # Window of up to 7 observed days vs preceding 7 observed days
    window = min(7, len(valid_prices) // 2)
    recent_series = valid_prices.iloc[-window:]
    prior_series = (
        valid_prices.iloc[-2 * window:-window]
        if len(valid_prices) >= 2 * window
        else valid_prices.iloc[:-window]
    )

    recent_avg = float(recent_series["wholesale_price"].mean())
    prior_avg = float(prior_series["wholesale_price"].mean()) if not prior_series.empty else recent_avg
    recent_min = float(recent_series["wholesale_price"].min())
    recent_max = float(recent_series["wholesale_price"].max())
    latest_price = float(valid_prices["wholesale_price"].iloc[-1])
    latest_date_val = valid_prices["observation_date"].iloc[-1]

    if prior_avg > 0:
        pct_change = round(((recent_avg - prior_avg) / prior_avg) * 100.0, 1)
    else:
        pct_change = 0.0

    recent_start = str(pd.to_datetime(recent_series["observation_date"].min()).date())
    recent_end = str(pd.to_datetime(recent_series["observation_date"].max()).date())
    prior_start = str(pd.to_datetime(prior_series["observation_date"].min()).date()) if not prior_series.empty else recent_start
    prior_end = str(pd.to_datetime(prior_series["observation_date"].max()).date()) if not prior_series.empty else recent_end

    # Threshold: +/- 5.0% change over the window
    if pct_change <= -5.0:
        direction = "FALLING"
        if lang == "hi":
            headline = f"दर्ज मंडियों में {comm_label} के थोक भाव में हाल ही में गिरावट आई है।"
            detail = (
                f"{recent_start} से {recent_end} के बीच, थोक भाव औसतन ₹{recent_avg:.0f} प्रति क्विंटल रहे, "
                f"जबकि पिछले 7 दिनों ({prior_start} से {prior_end}) में औसत ₹{prior_avg:.0f} प्रति क्विंटल था। "
                f"यह {abs(pct_change):.1f}% की गिरावट है। अंतिम दर्ज भाव ₹{latest_price:.0f} प्रति क्विंटल है।"
            )
            meaning = (
                "दर्ज मंडियों में आवक अधिक होने या मांग कम होने के संकेत हैं। "
                "आज की ताज़ा आवक और भाव जाने बिना माल मंडी ले जाने पर कम रिटर्न का जोखिम हो सकता है।"
            )
            actions = [
                f"माल लोड करने से पहले जिस मंडी में जा रहे हैं वहां के आज के ताज़ा भाव और आवक की पुष्टि करें; भाड़ा और तुलाई खर्च घटाकर मिलने वाले शुद्ध लाभ की तुलना करें।",
                f"यदि आपकी फसल गैर-नाशवंत है (जैसे सूखी प्याज या अनाज) और आपके पास सुरक्षित सूखा भंडारण है, तो अपनी आर्थिक स्थिति के अनुसार तुरंत बेचने के बजाय अस्थायी भंडारण के विकल्प का मूल्यांकन करें।",
                t["msp_msg"]
            ]
        elif lang == "mr":
            headline = f"नोंदणीकृत बाजारात {comm_label}च्या घाऊक भावात अलीकडे घट झाली आहे."
            detail = (
                f"{recent_start} ते {recent_end} दरम्यान, घाऊक भाव सरासरी ₹{recent_avg:.0f} प्रति क्विंटल होते, "
                f"तर मागील ७ दिवसांत ({prior_start} ते {prior_end}) सरासरी ₹{prior_avg:.0f} प्रति क्विंटल होती. "
                f"ही {abs(pct_change):.1f}% ची घट आहे. शेवटचा नोंदवलेला भाव ₹{latest_price:.0f} प्रति क्विंटल आहे."
            )
            meaning = (
                "नोंदणीकृत मंडयांमध्ये आवक वाढल्यामुळे किंवा खरेदीदारांची मागणी कमी झाल्यामुळे दर घसरलेले असू शकतात. "
                "आजचे ताजे भाव आणि आवक तपासल्याशिवाय शेतमाल मंडईत नेल्यास अपेक्षेपेक्षा कमी परतावा मिळण्याचा धोका असतो."
            )
            actions = [
                f"शेतमाल भरण्यापूर्वी आपण ज्या बाजार समितीत जाणार आहात तिथले आजचे प्रत्यक्ष भाव व आवक तपासा; वाहतूक आणि हमाली खर्च वजा करून प्रत्यक्ष हातात किती रक्कम राहील ते पहा.",
                f"शेतमाल टिकणारा असेल (उदा. कांदा किंवा धान्य) आणि सुरक्षित साठवणूक उपलब्ध असेल, तर स्वतःच्या गरजेनुसार काही दिवस थांबणे शक्य आहे का याचा विचार करा.",
                t["msp_msg"]
            ]
        else:
            headline = f"Recorded wholesale {comm_label} prices have declined recently."
            detail = (
                f"Between {recent_start} and {recent_end}, wholesale prices averaged ₹{recent_avg:.0f} per quintal, "
                f"compared with ₹{prior_avg:.0f} in the preceding period ({prior_start} to {prior_end}). "
                f"This is a change of {pct_change:.1f}%. The latest single-day observation is ₹{latest_price:.0f} per quintal."
            )
            meaning = (
                "Buyer demand in recorded mandis may have softened or arrivals have increased. "
                "Dispatching produce to the first available mandi without checking current arrivals and spot rates risks lower net returns."
            )
            actions = [
                f"Before dispatching, check today's modal price and arrival volume at the specific mandi you are considering. Factor in transport and handling expenses to determine your expected net return.",
                f"If your crop is non-perishable (such as dry onions or grains) and you have dry, safe storage, evaluate whether storing produce temporarily is financially viable compared to immediate sale.",
                t["msp_msg"]
            ]

    elif pct_change >= 5.0:
        direction = "RISING"
        if lang == "hi":
            headline = f"दर्ज मंडियों में {comm_label} के थोक भाव में हाल ही में सुधार देखा गया है।"
            detail = (
                f"{recent_start} से {recent_end} के बीच, थोक भाव औसतन ₹{recent_avg:.0f} प्रति क्विंटल रहे, "
                f"जबकि पिछले 7 दिनों में औसत ₹{prior_avg:.0f} था (+{pct_change:.1f}% की वृद्धि)। "
                f"अंतिम दर्ज भाव ₹{latest_price:.0f} प्रति क्विंटल है।"
            )
            meaning = (
                "दर्ज मंडियों में मांग मजबूत है। हालांकि, ऊंचे भाव देखकर अन्य जिलों से भी अचानक भारी आवक आ सकती है, "
                "जिससे अगले कुछ दिनों में भाव तेज़ी से बदल सकते हैं। यह मानकर न चलें कि ऊंचा भाव लगातार बना रहेगा।"
            )
            actions = [
                f"माल भेजने से पहले स्थानीय व्यापारी या मंडी बोर्ड से आज के हाजिर भाव की पुष्टि करें, क्योंकि भारी आवक आने पर भाव तुरंत गिर सकते हैं।",
                f"माल की छंटाई (grading) और सफाई पर ध्यान दें; तेजी के बाज़ार में अच्छी गुणवत्ता वाले माल को भाव के ऊपरी स्तर का लाभ मिलता है।",
                f"दूर की मंडी में जाने से पहले अतिरिक्त वाहन भाड़े और समय का हिसाब लगाएं।"
            ]
        elif lang == "mr":
            headline = f"नोंदणीकृत बाजारात {comm_label}च्या घाऊक भावात अलीकडे सुधारणा झाली आहे."
            detail = (
                f"{recent_start} ते {recent_end} दरम्यान, घाऊक भाव सरासरी ₹{recent_avg:.0f} प्रति क्विंटल होते, "
                f"तर मागील ७ दिवसांत सरासरी ₹{prior_avg:.0f} होती (+{pct_change:.1f}% वाढ). "
                f"शेवटचा नोंदवलेला भाव ₹{latest_price:.0f} प्रति क्विंटल आहे."
            )
            meaning = (
                "नोंदणीकृत मंडयांमध्ये खरेदीदारांची मागणी चांगली आहे. तथापि, भाव वाढल्यामुळे इतर भागातूनही अचानक मोठी आवक होऊ शकते, "
                "ज्यामुळे दर पुढील काही दिवसांत बदलू शकतात. भाव कायम चढेच राहतील असे गृहीत धरू नका."
            )
            actions = [
                f"शेतमाल पाठवण्यापूर्वी स्थानिक व्यापारी किंवा बाजार समितीकडून आजच्या प्रत्यक्ष दराची खात्री करा.",
                f"मालाची प्रतवारी (grading) आणि स्वच्छता नीट करा; वाढत्या बाजारात चांगल्या प्रतीच्या मालाला वरचा भाव मिळतो.",
                f"लांबच्या बाजारपेठेत माल पाठवण्यापूर्वी जादा वाहतूक खर्च आणि वेळेचा विचार करा."
            ]
        else:
            headline = f"Recorded wholesale {comm_label} prices have improved recently."
            detail = (
                f"Between {recent_start} and {recent_end}, wholesale prices averaged ₹{recent_avg:.0f} per quintal, "
                f"compared with ₹{prior_avg:.0f} in the preceding period ({prior_start} to {prior_end}). "
                f"This is a change of +{pct_change:.1f}%. The latest single-day observation is ₹{latest_price:.0f} per quintal."
            )
            meaning = (
                "Buyer demand has strengthened in recorded mandis. However, sharp price increases often attract sudden heavy inflows of produce from other districts, which can depress prices quickly. Do not assume high prices will persist indefinitely."
            )
            actions = [
                f"Confirm current spot rates with a trusted local trader or mandi board before loading produce, as prices can fluctuate as new daily arrivals enter the yard.",
                f"Grade and sort your produce carefully; clean, well-graded lots consistently command the upper boundary of the price band during rising markets.",
                f"Factor in transport and handling charges before choosing between a nearby local market and a distant city mandi."
            ]

    else:
        direction = "STABLE"
        if lang == "hi":
            headline = f"दर्ज मंडियों में {comm_label} के थोक भाव सामान्य रूप से स्थिर बने हुए हैं।"
            detail = (
                f"हाल के 7 दिनों में थोक भाव औसतन लगभग ₹{recent_avg:.0f} प्रति क्विंटल रहे (₹{recent_min:.0f} से ₹{recent_max:.0f} के दायरे में)। "
                f"पिछले समय की तुलना में बदलाव मामूली ({pct_change:+.1f}%) रहा।"
            )
            meaning = "दर्ज मंडियों में किसी बड़े अल्पकालिक उतार-चढ़ाव के संकेत नहीं हैं।"
            actions = [
                f"फसल की परिपक्वता और स्थानीय मौसम के अनुसार अपनी सामान्य कटाई और बिक्री योजना का पालन करें।",
                f"दोपहर के बाज़ार की भीड़ और जाम से बचने के लिए सुबह के समय मंडी आवक की जानकारी लें।"
            ]
        elif lang == "mr":
            headline = f"नोंदणीकृत बाजारात {comm_label}चे घाऊक भाव तुलनेने स्थिर आहेत."
            detail = (
                f"गेल्या ७ दिवसांत घाऊक भाव सरासरी साधारण ₹{recent_avg:.0f} प्रति क्विंटल राहिले (₹{recent_min:.0f} ते ₹{recent_max:.0f} दरम्यान). "
                f"मागील कालावधीच्या तुलनेत बदल किरकोळ ({pct_change:+.1f}%) होता."
            )
            meaning = "नोंदणीकृत मंडयांमध्ये अल्प मुदतीत अचानक मोठी भावबदल झालेली नाही."
            actions = [
                f"पिकाची पक्वता आणि स्थानिक हवामानाचा अंदाज घेऊन नेहमीच्या नियोजनानुसार काढणी व विक्री करा.",
                f"दुपारच्या गर्दीत दर गडगडणे टाळण्यासाठी सकाळीच आवक तपासून माल बाजारात न्या."
            ]
        else:
            headline = f"Recorded wholesale {comm_label} prices have remained relatively steady."
            detail = (
                f"Wholesale prices averaged approximately ₹{recent_avg:.0f} per quintal over the latest 7-day period "
                f"(ranging between ₹{recent_min:.0f} and ₹{recent_max:.0f} per quintal). "
                f"Movement compared with the prior period was modest ({pct_change:+.1f}%)."
            )
            meaning = "Wholesale prices have not experienced sudden short-term price swings in recorded mandis."
            actions = [
                f"Follow your customary harvesting schedule based on crop maturity and local weather conditions.",
                f"Check daily mandi arrivals before dispatching to avoid peak arrival hours."
            ]

    return {
        "available": True,
        "direction": direction,
        "pct_change": pct_change,
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions,
        "recent_avg": round(recent_avg, 2),
        "prior_avg": round(prior_avg, 2),
        "recent_min": round(recent_min, 2),
        "recent_max": round(recent_max, 2),
        "latest_price": round(latest_price, 2),
        "latest_date": str(pd.to_datetime(latest_date_val).date()) if latest_date_val is not None else None,
        "period": f"{recent_start} to {recent_end}"
    }


def analyze_market_comparison(
    db: Optional[Any] = None,
    df: Optional[pd.DataFrame] = None,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Computes an empirical market-level comparison table across distinct APMC mandis
    when market records are available.
    If only state-level averages or a single market exist, clearly explains that
    local market data is required rather than fabricating mandi recommendations.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])
    market_rows: List[Dict[str, Any]] = []

    # 1. Try querying DB if available
    if db is not None:
        try:
            from app.models import CommodityObservation
            q = db.query(
                CommodityObservation.market,
                CommodityObservation.district,
                CommodityObservation.state,
                CommodityObservation.observation_date,
                CommodityObservation.wholesale_price
            ).filter(CommodityObservation.market.isnot(None))

            if commodity:
                q = q.filter(CommodityObservation.commodity == commodity)
            if state:
                q = q.filter(CommodityObservation.state == state)

            records = q.all()
            if records:
                m_df = pd.DataFrame(
                    records,
                    columns=["market", "district", "state", "observation_date", "wholesale_price"]
                )
                m_df["wholesale_price"] = pd.to_numeric(m_df["wholesale_price"], errors="coerce")
                m_df = m_df.dropna(subset=["wholesale_price", "market"])
                m_df["observation_date"] = pd.to_datetime(m_df["observation_date"])

                # Group by market and find latest observation
                for m_name, group in m_df.groupby("market"):
                    latest_idx = group["observation_date"].idxmax()
                    latest_row = group.loc[latest_idx]
                    market_rows.append({
                        "market": str(m_name).strip(),
                        "location": str(latest_row.get("district") or latest_row.get("state") or "").strip(),
                        "date": str(latest_row["observation_date"].date()),
                        "price": float(latest_row["wholesale_price"])
                    })
        except Exception:
            market_rows = []

    # 2. If no DB records found, try DataFrame
    if not market_rows and df is not None and "market" in df.columns:
        valid_m = df.dropna(subset=["market", "wholesale_price"])
        if not valid_m.empty:
            for m_name, group in valid_m.groupby("market"):
                group_sorted = group.sort_values("observation_date") if "observation_date" in group.columns else group
                latest_row = group_sorted.iloc[-1]
                obs_d = (
                    str(pd.to_datetime(latest_row["observation_date"]).date())
                    if "observation_date" in latest_row and pd.notna(latest_row["observation_date"])
                    else "Recent"
                )
                market_rows.append({
                    "market": str(m_name).strip(),
                    "location": str(latest_row.get("district") or latest_row.get("state") or "").strip(),
                    "date": obs_d,
                    "price": float(latest_row["wholesale_price"])
                })

    # Evaluate whether we have >= 2 comparable markets
    distinct_markets = {r["market"] for r in market_rows if r["market"] and r["market"].lower() != "none"}

    if len(distinct_markets) < 2:
        return {
            "available": False,
            "markets_count": len(distinct_markets),
            "table_md": None,
            "table_txt": None,
            "reason": t["no_mandi_data"]
        }

    # Calculate comparison relative to group average
    avg_price = float(np.mean([r["price"] for r in market_rows]))
    sorted_rows = sorted(market_rows, key=lambda x: x["price"], reverse=True)

    # Format Markdown and Plain text tables
    md_lines = [
        "| Market (APMC) | Location | Latest Price (₹/Quintal) | As Of Date | Difference vs Avg (₹/Quintal) |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    txt_lines = [
        f"  {'Market':<20} | {'Location':<14} | {'Price (Rs/q)':<12} | {'Date':<10} | {'Diff vs Avg':<12}",
        "  " + "-" * 76
    ]

    for r in sorted_rows:
        diff = r["price"] - avg_price
        diff_str = f"{diff:+.0f}"
        loc = r["location"] if r["location"] else "-"
        md_lines.append(f"| {r['market']} | {loc} | ₹{r['price']:.0f} | {r['date']} | {diff_str} |")
        txt_lines.append(f"  {r['market']:<20} | {loc:<14} | Rs {r['price']:<9.0f} | {r['date']:<10} | {diff_str:<12}")

    disclaimer = (
        "Note: Differences shown above reflect gross mandi quotes. They do not account for transport, octroi/toll, "
        "loading/unloading charges, or shrinkage in transit. A higher quoted price at a distant market may not yield "
        "a higher net return once vehicle hiring charges and travel time are deducted."
    )
    md_lines.append("")
    md_lines.append(f"> [!NOTE]\n> {disclaimer}")
    txt_lines.append("  " + disclaimer)

    return {
        "available": True,
        "markets_count": len(sorted_rows),
        "group_avg_price": round(avg_price, 2),
        "table_md": "\n".join(md_lines),
        "table_txt": "\n".join(txt_lines),
        "records": sorted_rows,
        "reason": None
    }


def analyze_spread_trend(df: pd.DataFrame, lang: str = "en") -> Dict[str, Any]:
    """
    Evaluates whether the difference between wholesale mandi price and retail consumer price
    is wide or normal, explaining the spread in plain language without claiming unfair practices
    or confusing it with farmer profit.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])

    if (
        df.empty
        or "price_spread" not in df.columns
        or df["price_spread"].dropna().empty
        or "retail_price" not in df.columns
        or df["retail_price"].dropna().empty
    ):
        return {
            "available": False,
            "status": "UNAVAILABLE",
            "headline": "Wholesale-to-retail price spread information is not available.",
            "detail": "Consumer retail prices are not included in this dataset. We do not invent estimated retail prices.",
            "meaning": "Mandi wholesale prices only are analyzed; consumer price margins cannot be calculated.",
            "actions": []
        }

    sub = df[["observation_date", "wholesale_price", "retail_price", "price_spread"]].dropna().sort_values("observation_date")
    if len(sub) < 5:
        return {
            "available": False,
            "status": "INSUFFICIENT",
            "headline": "Insufficient retail price observations to compare margins.",
            "detail": "Too few matching wholesale and retail records exist in this sample to evaluate spread stability.",
            "meaning": "Sparse consumer price observations cannot determine whether market transmission is wide or normal.",
            "actions": []
        }

    recent_sub = sub.iloc[-min(7, len(sub)):]
    recent_wholesale = float(recent_sub["wholesale_price"].mean())
    recent_retail = float(recent_sub["retail_price"].mean())
    recent_spread = float(recent_sub["price_spread"].mean())
    hist_spread_mean = float(sub["price_spread"].mean())

    retail_margin_pct = (recent_spread / recent_wholesale) * 100.0 if recent_wholesale > 0 else 0.0

    # Wide spread condition: spread > historical mean by 20% AND spread > 500 Rs/quintal
    if recent_spread > (hist_spread_mean * 1.20) and recent_spread > 500.0:
        status = "WIDE"
        if lang == "hi":
            headline = "मंडी थोक भाव और शहर के खुदरा भाव के बीच का अंतर (Spread) वर्तमान में काफी चौड़ा है।"
            detail = (
                f"दर्ज आंकड़ों में, थोक भाव औसतन ₹{recent_wholesale:.0f} प्रति क्विंटल है, जबकि खुदरा भाव "
                f"औसतन ₹{recent_retail:.0f} प्रति क्विंटल है—दोनों के बीच ₹{recent_spread:.0f} प्रति क्विंटल का अंतर है "
                f"(थोक भाव से लगभग {retail_margin_pct:.0f}% अधिक)।"
            )
            meaning = (
                "चौड़े अंतर का अर्थ है कि शहर के उपभोक्ता जो कीमत चुका रहे हैं और किसान को जो मंडी भाव मिल रहा है, उसमें बड़ा फासला है। "
                "इस अंतर में छंटाई, पैकेजिंग, परिवहन, रास्ते की बर्बादी और व्यापारियों का मार्जिन शामिल होता है। "
                "इसका अर्थ किसान का अधिक मुनाफा बिल्कुल नहीं होता।"
            )
            actions = [t["fpo_msg"]]
        elif lang == "mr":
            headline = "बाजार समितीतील घाऊक भाव आणि शहरातील किरकोळ भाव यातील तफावत (Spread) सध्या मोठी आहे."
            detail = (
                f"नोंदणीकृत माहितीनुसार, घाऊक भाव सरासरी ₹{recent_wholesale:.0f} प्रति क्विंटल आणि किरकोळ भाव "
                f"₹{recent_retail:.0f} प्रति क्विंटल आहे—यामध्ये ₹{recent_spread:.0f} प्रति क्विंटलचा फरक आहे "
                f"({retail_margin_pct:.0f}% तफावत)."
            )
            meaning = (
                "मोठ्या तफावतीचा अर्थ असा की शहरातील ग्राहक जास्त पैसे मोजत आहेत, मात्र शेतकऱ्याला मिळणारा भाव तुलनेने कमी आहे. "
                "या फरकामध्ये वाहतूक, पॅकिंग, साठवणूक, नुकसान व किरकोळ विक्रेत्यांचा खर्च समाविष्ट असतो. "
                "याचा अर्थ शेतकऱ्याला जास्त नफा मिळतो असा होत नाही."
            )
            actions = [t["fpo_msg"]]
        else:
            headline = "The gap between mandi wholesale prices and city retail prices is currently wide."
            detail = (
                f"In recorded markets, wholesale prices average ₹{recent_wholesale:.0f} per quintal while "
                f"consumer retail prices average ₹{recent_retail:.0f} per quintal—a difference of ₹{recent_spread:.0f} per quintal "
                f"({retail_margin_pct:.0f}% above wholesale)."
            )
            meaning = (
                "A wide spread means city consumers are paying substantially more than what farmers receive at the mandi gate. "
                "This difference reflects handling, packaging, transportation, middleman margins, spoilage, and retailer overheads. "
                "It does not represent higher profit for the farmer."
            )
            actions = [t["fpo_msg"]]
    else:
        status = "NORMAL"
        headline = "The wholesale-to-retail price spread is within typical ranges."
        detail = (
            f"Wholesale prices average ₹{recent_wholesale:.0f}/quintal and retail averages ₹{recent_retail:.0f}/quintal "
            f"(margin spread of ₹{recent_spread:.0f}/quintal)."
        )
        meaning = "Price transmission between mandi wholesale and retail outlets appears consistent with standard handling and transportation margins."
        actions = []

    return {
        "available": True,
        "status": status,
        "headline": headline,
        "detail": detail,
        "meaning": meaning,
        "actions": actions,
        "recent_spread": round(recent_spread, 2),
        "recent_wholesale": round(recent_wholesale, 2),
        "recent_retail": round(recent_retail, 2),
        "retail_margin_pct": round(retail_margin_pct, 1)
    }


def analyze_fuel_trend(
    df: pd.DataFrame,
    shock_threshold_pct: float = 1.0,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Evaluates whether diesel fuel prices have increased and could impact transport costs.
    Provides actionable cost awareness without inventing specific rupee expenses per quintal.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])

    if df.empty or "diesel_price" not in df.columns or df["diesel_price"].dropna().empty:
        return {
            "available": False,
            "status": "UNAVAILABLE",
            "headline": "Fuel price records are not available in this dataset.",
            "detail": "Diesel price observations are not included.",
            "meaning": "Transport fuel trends cannot be estimated from this dataset.",
            "actions": []
        }

    sub = df[["observation_date", "diesel_price"]].dropna().sort_values("observation_date")
    if len(sub) < 3:
        return {
            "available": False,
            "status": "INSUFFICIENT",
            "headline": "Insufficient fuel price records.",
            "detail": "Too few fuel observations exist to determine a reliable trend.",
            "meaning": "Fuel price movement cannot be confirmed.",
            "actions": []
        }

    latest_diesel = float(sub["diesel_price"].iloc[-1])
    prior_diesel = float(sub["diesel_price"].iloc[-min(14, len(sub))])
    change_pct = ((latest_diesel - prior_diesel) / prior_diesel) * 100.0 if prior_diesel > 0 else 0.0

    if change_pct >= shock_threshold_pct:
        status = "INCREASED"
        if lang == "hi":
            headline = "खुदरा डीजल के भाव में हाल ही में बढ़ोतरी दर्ज की गई है।"
            detail = (
                f"खुदरा डीजल वर्तमान में लगभग ₹{latest_diesel:.2f} प्रति लीटर दर्ज है "
                f"(हाल के सप्ताहों में {change_pct:+.1f}% की वृद्धि)।"
            )
            meaning = (
                "डीजल के दाम बढ़ने से आमतौर पर ट्रैक्टर व पिकअप-ट्रक संचालक माल भाड़े में बढ़ोतरी कर देते हैं। "
                "दूर की मंडी में माल ले जाने पर प्रति बोरी भाड़ा अधिक लग सकता है।"
            )
            actions = [t["transport_pool_msg"]]
        elif lang == "mr":
            headline = "किरकोळ डिझेलच्या दरात अलीकडे वाढ नोंदवली गेली आहे."
            detail = (
                f"किरकोळ डिझेलचा दर सध्या साधारण ₹{latest_diesel:.2f} प्रति लिटर आहे "
                f"(मागील आठवड्यांच्या तुलनेत {change_pct:+.1f}% वाढ)."
            )
            meaning = (
                "डिझेल महागल्याने ट्रॅक्टर किंवा टेम्पो चालक वाहतूक भाड्यात वाढ करू शकतात. "
                "लांबच्या बाजार समितीत शेतमाल नेल्यास प्रति गोणी वाहतूक खर्च वाढू शकतो."
            )
            actions = [t["transport_pool_msg"]]
        else:
            headline = "Retail diesel prices have increased recently."
            detail = (
                f"Retail diesel is currently recorded at approximately ₹{latest_diesel:.2f} per litre "
                f"(up {change_pct:.1f}% over recent weeks)."
            )
            meaning = (
                "Higher diesel prices typically lead hired tractor and truck operators to increase transport freight rates. "
                "Transporting produce to distant markets will take a larger share of sales proceeds."
            )
            actions = [t["transport_pool_msg"]]
    elif change_pct <= -shock_threshold_pct:
        status = "DECREASED"
        headline = "Retail diesel prices have decreased slightly."
        detail = f"Retail diesel is recorded at approximately ₹{latest_diesel:.2f} per litre ({change_pct:.1f}% over recent weeks)."
        meaning = "Transport operating costs have eased slightly, though local vehicle hiring quotes often adjust with a delay."
        actions = []
    else:
        status = "STABLE"
        headline = "Diesel fuel prices have remained steady."
        detail = f"Retail diesel is stable at approximately ₹{latest_diesel:.2f} per litre."
        meaning = "Fuel-driven transport expenses have not experienced significant sudden changes in recorded areas."
        actions = []

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


def analyze_advisory_demand(
    forecast_res: Optional[Dict[str, Any]],
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Translates KCC query forecasting into practical communication guidance.
    Frames query demand around advisory helpline access, never claiming crop disease
    or agricultural catastrophe without evidence.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])

    if not forecast_res or "stress_assessment" not in forecast_res:
        return {
            "available": False,
            "category": "UNAVAILABLE",
            "headline": "Advisory service demand forecast is unavailable.",
            "detail": "Time-series records were not available to project farmer inquiry call volumes.",
            "meaning": "Call centre line load cannot be estimated.",
            "actions": [
                f"Kisan Call Centre ({VERIFIED_ASSISTANCE['kcc_toll_free']}) remains accessible for routine agricultural questions."
            ]
        }

    stress = forecast_res.get("stress_assessment", {})
    category = str(stress.get("category", "Normal")).upper()
    horizon = forecast_res.get("horizon_days", 14)
    base_mean = float(stress.get("historical_baseline_mean", 0.0))

    predictions = forecast_res.get("predictions", [])
    if predictions:
        pred_means = [p["predicted_demand"] for p in predictions]
        avg_forecast = float(np.mean(pred_means))
    else:
        avg_forecast = base_mean

    if category == "HIGH":
        if lang == "hi":
            headline = "इस क्षेत्र में कृषि परामर्श हेल्पलाइन पर अधिक कॉल आने का अनुमान है।"
            detail = (
                f"आगामी {horizon} दिनों में किसान पूछताछ की संख्या अधिक रहने का अनुमान है "
                f"(औसतन लगभग {avg_forecast:.0f} कॉल प्रतिदिन, सामान्य औसत {base_mean:.0f} की तुलना में)।"
            )
            meaning = (
                "आपके क्षेत्र के कई किसान इस समय बाज़ार भाव, मौसम या मौसमी फसल प्रबंधन को लेकर जानकारी तलाश रहे हैं। "
                "हेल्पलाइन पर दोपहर के समय अधिक प्रतीक्षा समय हो सकता है।"
            )
            actions = [
                f"फसल सलाह या सरकारी योजनाओं की जानकारी के लिए किसान कॉल सेंटर (टोल-फ्री: {VERIFIED_ASSISTANCE['kcc_toll_free']}, समय: {VERIFIED_ASSISTANCE['kcc_hours']}) पर संपर्क करें।"
            ]
        elif lang == "mr":
            headline = "या भागात कृषी सल्ला हेल्पलाईनवर फोनचे प्रमाण वाढण्याचा अंदाज आहे."
            detail = (
                f"पुढील {horizon} दिवसांत शेतकऱ्यांच्या विचारणांचे प्रमाण अधिक राहण्याचा अंदाज आहे "
                f"(दररोज सरासरी साधारण {avg_forecast:.0f} कॉल्स, सामान्य सरासरी {base_mean:.0f} च्या तुलनेत)."
            )
            meaning = (
                "आपल्या भागातील अनेक शेतकरी सध्या हंगामी कामे, बाजारपेठ किंवा हवामानाविषयी माहिती घेत आहेत. "
                "हेल्पलाईनवर दुपारच्या वेळेत थोडी प्रतीक्षा करावी लागू शकते."
            )
            actions = [
                f"पीक सल्ला किंवा शासकीय योजनांच्या माहितीसाठी किसान कॉल सेंटरला (टोल-फ्री: {VERIFIED_ASSISTANCE['kcc_toll_free']}, वेळ: {VERIFIED_ASSISTANCE['kcc_hours']}) संपर्क साधा."
            ]
        else:
            headline = "Higher volume of farmer advisory queries is anticipated in this region."
            detail = (
                f"Over the next {horizon} days, our demand model projects elevated inquiry volumes "
                f"(averaging around {avg_forecast:.0f} daily calls, compared to the normal baseline of {base_mean:.0f} calls)."
            )
            meaning = (
                "Many farmers in your area may be addressing similar seasonal, weather, or market questions. "
                "Advisory phone lines and extension offices may experience higher inquiry volumes during mid-day hours."
            )
            actions = [
                f"For personalized crop advice, weather updates, or scheme guidance, contact Kisan Call Centre (Toll-Free {VERIFIED_ASSISTANCE['kcc_toll_free']}, {VERIFIED_ASSISTANCE['kcc_hours']}) or your local Krishi Sahayak."
            ]

    elif category == "ELEVATED":
        headline = "Moderately elevated demand for agricultural advice is expected."
        detail = (
            f"Forecasted query activity over the next {horizon} days ({avg_forecast:.0f} calls/day) "
            f"is moderately above typical historical baseline levels ({base_mean:.0f} calls/day)."
        )
        meaning = "A moderate increase in agricultural information inquiries is expected across regional advisory lines."
        actions = [
            f"Reach out to Kisan Call Centre (Toll-Free {VERIFIED_ASSISTANCE['kcc_toll_free']}) ahead of urgent field operations rather than waiting until the last moment."
        ]
    else:
        if lang == "hi":
            headline = "कृषि परामर्श हेल्पलाइन सामान्य रूप से संचालित हो रही है।"
            detail = (
                f"अनुमानित कॉल संख्या ({avg_forecast:.0f} कॉल/दिन) सामान्य ऐतिहासिक दायरे में है "
                f"(सामान्य औसत: {base_mean:.0f} कॉल/दिन)।"
            )
            meaning = "हेल्पलाइन पर कोई असामान्य भीड़ या दबाव नहीं है।"
            actions = [
                f"फसल, बीज या खाद से संबंधित सामान्य प्रश्नों के लिए किसान कॉल सेंटर (टोल-फ्री: {VERIFIED_ASSISTANCE['kcc_toll_free']}) पर संपर्क कर सकते हैं।"
            ]
        elif lang == "mr":
            headline = "कृषी सल्ला हेल्पलाईन सामान्य क्षमतेने कार्यरत आहे."
            detail = (
                f"अंदाजित विचारणा संख्या ({avg_forecast:.0f} कॉल्स/दिवस) नेहमीच्या सरासरी मर्यादेत आहे "
                f"(सामान्य सरासरी: {base_mean:.0f} कॉल्स/दिवस)."
            )
            meaning = "हेल्पलाईनवर सध्या कोणत्याही प्रकारची अतिरिक्त गर्दी नाही."
            actions = [
                f"पीक, बियाणे किंवा खतांसंबंधी नियमित माहितीसाठी किसान कॉल सेंटरवर (टोल-फ्री: {VERIFIED_ASSISTANCE['kcc_toll_free']}) संपर्क साधता येईल."
            ]
        else:
            headline = "Agricultural advisory support lines are operating under normal conditions."
            detail = (
                f"Expected inquiry demand ({avg_forecast:.0f} calls/day) is within standard historical parameters "
                f"(baseline: {base_mean:.0f} calls/day)."
            )
            meaning = "Advisory support lines are not experiencing unusual congestion in this region."
            actions = [
                f"Kisan Call Centre (Toll-Free {VERIFIED_ASSISTANCE['kcc_toll_free']}) is readily available for routine crop, seed, or fertilizer questions."
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


def determine_advisory_priority(
    comm_analysis: Dict[str, Any],
    fuel_analysis: Dict[str, Any],
    spread_analysis: Dict[str, Any],
    advisory_analysis: Dict[str, Any],
    freshness: Dict[str, Any],
    lang: str = "en"
) -> Dict[str, str]:
    """
    Transparently categorizes the advisory priority and explains uncertainty
    using defensible, rule-based logic without arbitrary scores.
    """
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])

    price_dir = comm_analysis.get("direction", "STABLE")
    fuel_stat = fuel_analysis.get("status", "STABLE")
    spread_stat = spread_analysis.get("status", "NORMAL")
    adv_cat = advisory_analysis.get("category", "NORMAL")
    is_recent = freshness.get("is_recent", False)

    # 1. Action to consider now: Significant price movement or fuel increase supported by recent data
    if is_recent and (price_dir in ["FALLING", "RISING"] or fuel_stat == "INCREASED"):
        priority = t["priority_now"]
        if price_dir == "FALLING" and fuel_stat == "INCREASED":
            confidence = (
                "Recent data confirms simultaneous wholesale price drops and fuel price increases. "
                "Transport expenses to distant mandis will take a higher share of sales proceeds. "
                "Confirm local spot prices and freight costs before dispatching."
            )
        elif price_dir == "FALLING":
            confidence = (
                "Recent observations indicate declining mandi prices. While these figures reflect recent days, "
                "daily arrival surges can cause further price swings. Check today's spot arrivals locally."
            )
        elif price_dir == "RISING":
            confidence = (
                "Recent observations show strengthening wholesale rates. Be aware that sharp increases often "
                "attract sudden inflows from other districts within 24 to 48 hours."
            )
        else:
            confidence = (
                "Recent observations show rising fuel prices. Confirm firm vehicle hiring quotes before agreeing to transport."
            )

    # 2. Check before deciding: Market moved but data is historical, or wide spread, or elevated queries
    elif (price_dir in ["FALLING", "RISING"] or fuel_stat == "INCREASED") or spread_stat == "WIDE" or adv_cat in ["HIGH", "ELEVATED"]:
        priority = t["priority_check"]
        if not is_recent and (price_dir in ["FALLING", "RISING"] or fuel_stat == "INCREASED"):
            confidence = (
                f"Data freshness alert: Market movement was observed in historical records ({freshness.get('latest_date_str')}). "
                "Because prices and fuel rates fluctuate, current local spot prices and freight quotes must be confirmed before acting."
            )
        elif spread_stat == "WIDE":
            confidence = (
                "Wholesale-to-retail spread is wide, but local retail channels and direct marketing options vary by village."
            )
        else:
            confidence = (
                "Advisory call volumes are projected to be elevated, which indicates seasonal information interest but does not predict individual prices."
            )

    # 3. No clear signal: Stable market, normal fuel, normal query volumes
    else:
        priority = t["priority_none"]
        if not is_recent:
            confidence = (
                f"Historical baseline: Recorded observations showed stable prices and standard conditions (as of {freshness.get('latest_date_str')}). "
                "Current market spot prices should be confirmed locally before making marketing commitments."
            )
        else:
            confidence = (
                "Recent observations show relatively stable commodity prices and fuel rates with standard query volumes. "
                "No unusual market disruption is indicated by the current data."
            )


    return {
        "priority": priority,
        "confidence": confidence
    }


def generate_farmer_recommendations(
    df: pd.DataFrame,
    forecast_res: Optional[Dict[str, Any]] = None,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    quality: Optional[Dict[str, Any]] = None,
    output_dir: Optional[Path] = None,
    db: Optional[Any] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Main entry point: Generates structured, evidence-grounded farmer decision support
    in Markdown (.md) and plain text (.txt).
    """
    if lang not in ["en", "hi", "mr"]:
        lang = "en"
    t = UI_STRINGS[lang]

    if output_dir is None:
        reports_dir = OUTPUTS_DIR / "reports"
    else:
        reports_dir = Path(output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Evaluate individual modules
    comm_analysis = analyze_commodity_trend(df, commodity_name=commodity, lang=lang)
    market_comp = analyze_market_comparison(db=db, df=df, state=state, commodity=commodity, lang=lang)
    spread_analysis = analyze_spread_trend(df, lang=lang)
    fuel_analysis = analyze_fuel_trend(df, lang=lang)
    advisory_analysis = analyze_advisory_demand(forecast_res, lang=lang)

    # 2. Geography, Commodity, and Temporal Context
    region_label = state if state else "Multi-State Region (Overall Sample)"
    commodity_label = commodity if commodity else "Agricultural Produce (General)"

    # Determine date period & latest observation date
    latest_comm_date = comm_analysis.get("latest_date")
    if quality and quality.get("sample_start") and quality.get("sample_end"):
        period_label = f"{quality['sample_start']} to {quality['sample_end']}"
    elif not df.empty and "observation_date" in df.columns:
        d_min = pd.to_datetime(df["observation_date"].min()).date()
        d_max = pd.to_datetime(df["observation_date"].max()).date()
        period_label = f"{d_min} to {d_max}"
    else:
        period_label = "Current Observation Window"

    # Evaluate data freshness
    freshness = get_freshness_assessment(latest_comm_date, lang=lang)

    # Determine provenance classification
    prov_type = quality.get("provenance_type") if quality else None
    if not prov_type:
        is_synth = bool(quality.get("is_synthetic", False)) if quality else False
        prov_type = "SYNTHETIC" if is_synth else "UNVERIFIED"

    if prov_type == "SYNTHETIC":
        prov_label = "Synthetic Demonstration Data (generated deterministically for research and testing)"
        prov_warning = (
            "Notice: These figures reflect synthetic demonstration data created for offline testing. "
            "They illustrate analytical methods and should not be used for real-world financial commitments."
        )
    elif prov_type == "VERIFIED_REAL":
        prov_label = "Verified Real-World Observations (imported from official reporting portals)"
        prov_warning = (
            "Notice: Figures represent verified historical records from reporting APMC yards and government portals."
        )
    else:
        prov_label = "Unverified / User-Supplied Data (provided via local CSV without independent verification)"
        prov_warning = (
            "Notice: Figures were imported from user-supplied CSV files without independent verification. "
            "Verify accuracy with local APMC market authorities before making financial commitments."
        )

    # 3. Determine Advisory Priority and Plain-Language Confidence
    priority_info = determine_advisory_priority(
        comm_analysis=comm_analysis,
        fuel_analysis=fuel_analysis,
        spread_analysis=spread_analysis,
        advisory_analysis=advisory_analysis,
        freshness=freshness,
        lang=lang
    )

    # 4. Synthesize Recommended Next Steps (Strictly Numbered 1, 2, 3...)
    # Ensure every step is useful, non-empty, and unique
    raw_steps: List[str] = []

    # Step 1: Immediate Commodity Marketing Action
    if comm_analysis.get("actions"):
        raw_steps.append(comm_analysis["actions"][0])
    else:
        raw_steps.append("Check prevailing spot modal prices at your local APMC notice board before dispatching.")

    # Step 2: Cost / Logistics / Storage / Marketing Alternative
    if fuel_analysis.get("status") == "INCREASED" and fuel_analysis.get("actions"):
        raw_steps.append(fuel_analysis["actions"][0])
    elif spread_analysis.get("status") == "WIDE" and spread_analysis.get("actions"):
        raw_steps.append(spread_analysis["actions"][0])
    elif len(comm_analysis.get("actions", [])) > 1:
        raw_steps.append(comm_analysis["actions"][1])
    else:
        raw_steps.append(t["msp_msg"])

    # Step 3: Verified Official Advisory Contact
    if advisory_analysis.get("actions"):
        raw_steps.append(advisory_analysis["actions"][0])
    else:
        raw_steps.append(
            f"For individual crop protection or market advice, contact Kisan Call Centre (Toll-Free {VERIFIED_ASSISTANCE['kcc_toll_free']}, {VERIFIED_ASSISTANCE['kcc_hours']})."
        )

    # Clean and deduplicate while strictly preserving order
    recommended_steps: List[str] = []
    seen = set()
    for s in raw_steps:
        cleaned = str(s).strip()
        # Remove any leading digits or bullets if already present
        if cleaned and cleaned[0].isdigit() and len(cleaned) > 2 and cleaned[1] in [".", ")"]:
            cleaned = cleaned[2:].strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            recommended_steps.append(cleaned)

    # 5. Build Markdown Advisory Report
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    md_lines = [
        f"# {t['title']}",
        "",
        f"**{t['region_label']}:** {region_label}  ",
        f"**{t['commodity_label']}:** {commodity_label}  ",
        f"**{t['period_label']}:** {period_label}  ",
        f"**{t['freshness_label']}:** {freshness['statement']}  ",
        f"**{t['priority_label']}:** `{priority_info['priority']}`  ",
        f"**{t['confidence_label']}:** {priority_info['confidence']}  ",
        "",
        "---",
        "",
        f"## {t['situation_hdr']}",
        "",
        f"{comm_analysis['headline']}",
        "",
        f"{comm_analysis['detail']}",
        "",
        "---",
        "",
        f"## {t['meaning_hdr']}",
        "",
        f"- {comm_analysis['meaning']}"
    ]

    if fuel_analysis.get("available") and fuel_analysis.get("status") == "INCREASED":
        md_lines.append(f"- **Transport Cost Impact:** {fuel_analysis['meaning']}")
    if spread_analysis.get("available") and spread_analysis.get("status") == "WIDE":
        md_lines.append(f"- **Price Spread Context:** {spread_analysis['meaning']}")
    if advisory_analysis.get("available") and advisory_analysis.get("category") in ["HIGH", "ELEVATED"]:
        md_lines.append(f"- **Advisory Demand:** {advisory_analysis['meaning']}")

    md_lines.extend([
        "",
        "---",
        "",
        f"## {t['steps_hdr']}",
        ""
    ])

    for idx, step_text in enumerate(recommended_steps, start=1):
        md_lines.append(f"{idx}. {step_text}")

    md_lines.extend([
        "",
        "---",
        "",
        f"## {t['check_hdr']}",
        "",
        f"- {t['check_transport']}",
        f"- {t['check_perishability']}",
        f"- {t['check_grading']}",
        f"- {t['check_cash']}",
        "",
        "---",
        "",
        f"## {t['market_hdr']}",
        ""
    ])

    if market_comp["available"]:
        md_lines.append(market_comp["table_md"])
    else:
        md_lines.append(f"> [!NOTE]\n> {market_comp['reason']}")

    md_lines.extend([
        "",
        "---",
        "",
        f"## {t['evidence_hdr']}",
        "",
        f"- **Wholesale Price Observation:** 7-day average of ₹{comm_analysis.get('recent_avg', 0):.0f}/quintal vs preceding period average of ₹{comm_analysis.get('prior_avg', 0):.0f}/quintal ({comm_analysis.get('pct_change', 0):+.1f}% change, period: {comm_analysis.get('period', 'N/A')}).",
        f"- **Diesel Price Observation:** Latest recorded diesel is ₹{fuel_analysis.get('latest_diesel', 0):.2f}/Litre ({fuel_analysis.get('change_pct', 0):+.1f}% recent change).",
        f"- **Wholesale-Retail Spread:** {'₹' + str(int(spread_analysis.get('recent_spread', 0))) + '/quintal (' + str(spread_analysis.get('retail_margin_pct', 0)) + '% above wholesale)' if spread_analysis['available'] else 'Not available in dataset'}.",
        f"- **Advisory Query Demand:** Projected daily query volume of {advisory_analysis.get('avg_forecast', 0):.0f} inquiries/day (category: {advisory_analysis.get('category', 'NORMAL')}).",
        f"- **Data Provenance:** {prov_label}.",
        "",
        "---",
        "",
        f"## {t['limits_hdr']}",
        "",
        "- **No Chemical or Agronomic Prescriptions:** This advisory analyzes market observations and query demand. It does NOT prescribe chemical pesticide dosages, fertilizer applications, or plant pathology treatments. Consult your local Krishi Vigyan Kendra (KVK) agronomist for crop health management.",
        "- **No Guaranteed Future Prices:** Statistical projections and recent trends do not guarantee tomorrow's market clearing rates. Road closures, sudden weather changes, or sudden arrival surges can rapidly alter spot prices.",
        f"- **Data Freshness Limitation:** {freshness['statement']}",
        f"- **{prov_warning}**",
        f"- **Verified Official Support:** Kisan Call Centre Toll-Free **{VERIFIED_ASSISTANCE['kcc_toll_free']}** ({VERIFIED_ASSISTANCE['kcc_hours']}). Gram Panchayat Krishi Sahayak offices provide localized in-person assistance.",
        "",
        "---",
        f"*AgriStress Analytics — Farmer Decision-Support Advisory (Generated: {now_str})*"
    ])

    md_content = "\n".join(md_lines)
    md_path = reports_dir / "farmer_advisory.md"
    md_path.write_text(md_content, encoding="utf-8")

    # If Hindi or Marathi requested, also write language-specific markdown file
    if lang != "en":
        lang_md_path = reports_dir / f"farmer_advisory_{lang}.md"
        lang_md_path.write_text(md_content, encoding="utf-8")

    # 6. Build Plain Text Version (.txt) for Terminal/SMS/WhatsApp
    txt_lines = [
        "=" * 72,
        f"      {t['title']}",
        "=" * 72,
        f"Region:             {region_label}",
        f"Commodity:          {commodity_label}",
        f"Data Period:        {period_label}",
        f"Data Freshness:     {freshness['statement']}",
        f"Advisory Priority:  {priority_info['priority']}",
        "-" * 72,
        "",
        "1. SITUATION IN ONE SENTENCE:",
        f"  * {comm_analysis['headline']}",
        f"    {comm_analysis['detail']}",
        "",
        "2. WHAT THIS MEANS FOR YOUR DECISION:",
        f"  * {comm_analysis['meaning']}",
    ]

    if fuel_analysis.get("available") and fuel_analysis.get("status") == "INCREASED":
        txt_lines.append(f"  * Transport: {fuel_analysis['meaning']}")
    if spread_analysis.get("available") and spread_analysis.get("status") == "WIDE":
        txt_lines.append(f"  * Price Gap: {spread_analysis['meaning']}")

    txt_lines.extend([
        "",
        "3. RECOMMENDED NEXT STEPS:",
    ])
    for idx, step_text in enumerate(recommended_steps, start=1):
        txt_lines.append(f"  {idx}. {step_text}")

    txt_lines.extend([
        "",
        f"4. {t['check_hdr'].upper()}:",
        f"  * {t['check_transport'].replace('**', '')}",
        f"  * {t['check_perishability'].replace('**', '')}",
        f"  * {t['check_grading'].replace('**', '')}",
        f"  * {t['check_cash'].replace('**', '')}",
        "",
        f"5. {t['market_hdr'].upper()}:",
    ])

    if market_comp["available"]:
        txt_lines.append(market_comp["table_txt"])
    else:
        txt_lines.append(f"  * {market_comp['reason']}")

    txt_lines.extend([
        "",
        "6. OFFICIAL ASSISTANCE & HELPLINE:",
        f"  * Kisan Call Centre (Toll-Free): {VERIFIED_ASSISTANCE['kcc_toll_free']} ({VERIFIED_ASSISTANCE['kcc_hours']})",
        "  * Local Support: Gram Panchayat Krishi Sahayak or nearest Krishi Vigyan Kendra (KVK).",
        "",
        "7. LIMITATIONS & PROVENANCE:",
        f"  * Provenance: {prov_label}",
        "  * Not an individual farm prescription. Estimates are not guaranteed future prices.",
        "=" * 72
    ])

    txt_content = "\n".join(txt_lines)
    txt_path = reports_dir / "farmer_advisory.txt"
    txt_path.write_text(txt_content, encoding="utf-8")

    if lang != "en":
        lang_txt_path = reports_dir / f"farmer_advisory_{lang}.txt"
        lang_txt_path.write_text(txt_content, encoding="utf-8")

    return {
        "report_md_path": str(md_path),
        "report_txt_path": str(txt_path),
        "region": region_label,
        "commodity": commodity_label,
        "period": period_label,
        "freshness": freshness,
        "provenance_type": prov_type,
        "provenance_label": prov_label,
        "priority": priority_info["priority"],
        "confidence": priority_info["confidence"],
        "price_direction": comm_analysis.get("direction"),
        "price_headline": comm_analysis["headline"],
        "price_pct_change": comm_analysis.get("pct_change", 0.0),
        "recent_avg_price": comm_analysis.get("recent_avg", 0.0),
        "prior_avg_price": comm_analysis.get("prior_avg", 0.0),
        "latest_price": comm_analysis.get("latest_price", 0.0),
        "fuel_status": fuel_analysis.get("status"),
        "spread_status": spread_analysis.get("status"),
        "advisory_stress": advisory_analysis.get("category"),
        "recommended_steps": recommended_steps,
        "market_comparison_available": market_comp["available"],
        "market_comparison_count": market_comp.get("markets_count", 0),
        "lang": lang,
        "status": "SUCCESS"
    }
