#!/usr/bin/env python3
"""
PVR Saptarshi Titan Engine - Unified CLI
========================================
Modular, parameterized calculation and multi-agent annual convergence engine
implementing P.V.R. Narasimha Rao's research methodology.
"""

import sys
import os
import math
import argparse
import json
from datetime import datetime, timezone, timedelta
import swisseph as swe

sys.path.insert(0, '/home/opc/mcp_jhora')
from pvr_annual_engine.config import (
    AYANAMSA_ID, RASI_NAMES, PLANET_NAMES,
    LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
)
from pvr_annual_engine.chart_solver import (
    calculate_julian_day_ut,
    get_natal_sun_tropical,
    solve_tropical_solar_return_jd,
    solve_tithi_pravesha_jd_ut,
    get_natal_tithi_angle,
    compute_sidereal_positions_and_lagna
)
from pvr_annual_engine.divisional_engine import (
    get_divisional_sign_and_deg,
    build_varga_chart
)
from pvr_annual_engine.tajaka_adk import ADK04TajakaVarshaphal
from pvr_annual_engine.tithi_pravesha_adk import ADK05TithiPravesha
from pvr_annual_engine.annual_convergence_evaluator import PVRAnnualConvergenceEvaluator

swe.set_ephe_path('/usr/share/ephe')
swe.set_sid_mode(AYANAMSA_ID, 0.0, 0.0)

def parse_args():
    parser = argparse.ArgumentParser(description="PVR Saptarshi Titan Engine CLI")
    parser.add_argument("--year", type=int, default=2000, help="Birth year (default: 2000)")
    parser.add_argument("--month", type=int, default=1, help="Birth month (default: 1)")
    parser.add_argument("--day", type=int, default=1, help="Birth day (default: 1)")
    parser.add_argument("--hour", type=int, default=12, help="Birth hour 0-23 (default: 12)")
    parser.add_argument("--minute", type=int, default=0, help="Birth minute 0-59 (default: 0)")
    parser.add_argument("--second", type=float, default=0.0, help="Birth second 0-59 (default: 0.0)")
    parser.add_argument("--lat", type=float, default=28.6139, help="Latitude in decimal degrees (default: 28.6139)")
    parser.add_argument("--lon", type=float, default=77.2090, help="Longitude in decimal degrees (default: 77.2090)")
    parser.add_argument("--tz", type=float, default=5.5, help="Timezone offset from UTC in hours (default: 5.5)")
    parser.add_argument("--target-year", type=int, default=2025, help="Target year for annual analysis (default: 2025)")
    parser.add_argument("--topic", type=str, default="career_success", help="Topic key (default: career_success)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    return parser.parse_args()

def main():
    args = parse_args()
    jd_birth_ut = calculate_julian_day_ut(args.year, args.month, args.day, args.hour, args.minute, args.second, args.tz)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_birth_ut)
    natal_asc_deg, natal_planets_d1 = compute_sidereal_positions_and_lagna(jd_birth_ut, args.lat, args.lon)

    tajaka_adk = ADK04TajakaVarshaphal()
    tp_adk = ADK05TithiPravesha()
    evaluator = PVRAnnualConvergenceEvaluator()

    t_res = tajaka_adk.generate_varshaphal_chart(args.year, args.month, args.day, args.hour, args.minute, args.second, args.target_year, args.lat, args.lon, args.tz)
    tp_res = tp_adk.generate_tp_chart(args.year, args.month, args.day, args.hour, args.minute, args.second, args.target_year, args.lat, args.lon, args.tz)
    conv_res = evaluator.evaluate_combined_annual_potential(t_res, tp_res, args.topic)

    if args.json:
        output = {
            "ayanamsa": f"Pushya-Paksha ({ayanamsa_val:.6f}°)",
            "natal_lagna": round(natal_asc_deg, 2),
            "target_year": args.target_year,
            "topic": args.topic,
            "convergence": conv_res
        }
        print(json.dumps(output, indent=2))
    else:
        print("==========================================================================================")
        print(f"PVR SAPTARSHI TITAN ENGINE - ANNUAL CONVERGENCE (Pushya-Paksha: {ayanamsa_val:.6f}°)")
        print("==========================================================================================")
        print(f"Target Year: {args.target_year} | Topic: {conv_res['topic_title']}")
        print(f"Tajaka Return Date    : {t_res['return_moment_local']} | Muntha: {t_res['muntha']['sign']} (House {t_res['muntha']['house_from_varshaphal_lagna']})")
        print(f"Tithi Pravesha Return : {tp_res['tp_moment_local']} | Vara Lord: {tp_res['vara_lord_year_ruler']} in House {tp_res['year_lord_placement']['house_from_tp_lagna']}")
        print(f"Multi-Factor Potential Score: {conv_res['potential_score_pct']}% ({conv_res['potential_level']})")

if __name__ == "__main__":
    main()
