#!/usr/bin/env python3
"""
Native Multi-Year Annual Chart Multi-Factor Evaluation & LLM Synthesis
======================================================================
Executes comprehensive PVR Multi-Factor Annual Chart Analysis for:
  Native: October 6, 2001 at 16:59:07 IST, Ahmedabad (23.0225° N, 72.5714° E)

Evaluates:
  1. Academic Success / Higher Education (2024, 2025, 2026) -> D-24 Siddhamsa
  2. Career Advancement & Professional Growth (2026, 2027, 2028) -> D-10 Dasamsa
  3. Marriage & Partnership Timing (2027, 2028, 2029) -> D-9 Navamsa

Strictly adheres to P.V.R. Narasimha Rao's Multi-Factor Diagnostic Method:
  - Both Tajaka Varshaphal (Tropical Solar Return) & Tithi Pravesha (Tropical Soli-Lunar Return)
  - Full analysis of D-1 and relevant D-N
  - Evaluates Lagna Lords, House Lords, House Occupants, Raja Yogas, Parivartanas, Samasaptaka
  - Evaluates Year Ruler / Vara Lord dignity and placement
  - Computes holistic Potential Score (0-100%) and potential tier
  - Synthesizes each target horizon via Gemini 3.8 Flash High (port 8090)
"""

import os
import sys
import json
import time

sys.path.insert(0, "/home/opc/mcp_jhora")

from pvr_adk.adks.adk04_tajaka_varshaphal import ADK04TajakaVarshaphal
from pvr_adk.adks.adk05_tithi_pravesha import ADK05TithiPravesha
from pvr_adk.adks.pvr_annual_evaluator import PVRAnnualEvaluator

# Native parameters
NATIVE_PARAMS = {
    "name": "Vishvesh",
    "year": 2001,
    "month": 10,
    "day": 6,
    "hour": 16,
    "minute": 59,
    "second": 7.0,
    "lat": 23.0225,
    "lon": 72.5714,
    "tz": 5.5,
    "place": "Ahmedabad, India"
}

EVALUATION_SPECS = [
    {"topic": "academic_success", "years": [2024, 2025, 2026], "varga": "D24", "title": "Academic Distinction & Higher Learning"},
    {"topic": "career_success", "years": [2026, 2027, 2028], "varga": "D10", "title": "Career Advancement & Executive Authority"},
    {"topic": "marriage", "years": [2027, 2028, 2029], "varga": "D9", "title": "Marriage & Relationship Alliance"}
]

def main():
    print("=" * 80)
    print("PVR MULTI-FACTOR ANNUAL CHART EVALUATION & LLM SYNTHESIS ENGINE")
    print(f"Native: {NATIVE_PARAMS['name']} | Birth: 2001-10-06 16:59:07 IST | {NATIVE_PARAMS['place']}")
    print("=" * 80)

    adk4 = ADK04TajakaVarshaphal()
    adk5 = ADK05TithiPravesha()
    evaluator = PVRAnnualEvaluator()

    all_results = {}

    for spec in EVALUATION_SPECS:
        topic = spec["topic"]
        title = spec["title"]
        varga = spec["varga"]
        years = spec["years"]
        print(f"\n[HORIZON] Topic: {title} ({spec['varga']}) | Target Years: {years}")
        all_results[topic] = {
            "title": title,
            "varga": varga,
            "years_data": {}
        }

        for y in years:
            print(f"  --> Calculating Annual Charts for Year {y}...")
            vp_chart = adk4.generate_varshaphal_chart(
                NATIVE_PARAMS["year"], NATIVE_PARAMS["month"], NATIVE_PARAMS["day"],
                NATIVE_PARAMS["hour"], NATIVE_PARAMS["minute"], NATIVE_PARAMS["second"],
                y, NATIVE_PARAMS["lat"], NATIVE_PARAMS["lon"], NATIVE_PARAMS["tz"], NATIVE_PARAMS["place"]
            )
            tp_chart = adk5.generate_tp_chart(
                NATIVE_PARAMS["year"], NATIVE_PARAMS["month"], NATIVE_PARAMS["day"],
                NATIVE_PARAMS["hour"], NATIVE_PARAMS["minute"], NATIVE_PARAMS["second"],
                y, NATIVE_PARAMS["lat"], NATIVE_PARAMS["lon"], NATIVE_PARAMS["tz"], NATIVE_PARAMS["place"]
            )

            # Combined multi-factor evaluation
            payload = evaluator.evaluate_combined_annual_potential(vp_chart, tp_chart, topic)
            score = payload["potential_score_pct"]
            level = payload["potential_level"]
            print(f"      Potential Score: {score}% ({level})")
            print(f"      Favorable Factors: {len(payload['favorable_indications'])} | Challenging Factors: {len(payload['challenging_indications'])}")

            # LLM Synthesis via Gemini 3.8 Flash High
            print(f"      Invoking Gemini 3.8 Flash High for PVR scholarly synthesis...")
            synthesis = evaluator.interpret_annual_chart_with_llm(payload, NATIVE_PARAMS["name"])
            print(f"      [LLM Synthesis Complete: {len(synthesis)} characters]")

            payload["llm_synthesis"] = synthesis
            all_results[topic]["years_data"][str(y)] = payload

    # Save to JSON
    os.makedirs("/home/opc/mcp_jhora/output_charts", exist_ok=True)
    out_json = "/home/opc/mcp_jhora/output_charts/native_multi_year_annual_evaluations.json"
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[SUCCESS] All multi-year evaluations saved to: {out_json}")

if __name__ == "__main__":
    main()
