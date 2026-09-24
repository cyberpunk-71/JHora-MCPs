#!/usr/bin/env python3
"""
PVR Multi-Method Chain-of-Ask Prediction Engine
-----------------------------------------------
Executes the full chain of ask across all 9 PVR Narasimha Rao research papers.
Strictly uses Pushya-Paksha Ayanamsa and PVR's verified divisional algorithms.
"""

import sys
import json
from typing import Dict, Any, List

sys.path.insert(0, "/home/opc/mcp_jhora")

from pvr_adk.adks.adk_ensemble_orchestrator import PVREnsembleOrchestrator
from pvr_adk.core.chart_engine import get_birth_chart

def run_pvr_prediction(
    birth_year: int, birth_month: int, birth_day: int,
    birth_hour: int, birth_minute: int, birth_second: float,
    latitude: float, longitude: float, timezone: float, place_name: str,
    target_topic: str,
    scan_years: List[int]
) -> Dict[str, Any]:
    orch = PVREnsembleOrchestrator()
    yearly_evaluations = []

    for yr in scan_years:
        res = orch.run_complete_multi_method_prediction(
            birth_year, birth_month, birth_day, birth_hour, birth_minute, birth_second,
            latitude, longitude, timezone, place_name,
            target_topic=target_topic, target_year=yr
        )
        yearly_evaluations.append({
            "year": yr,
            "alignment_score": res["orchestrator_summary"]["overall_alignment_score"],
            "verdict": res["orchestrator_summary"]["alignment_verdict"],
            "reasons": res["convergence_reasons"],
            "stationary_transits": res["chain_of_ask_levels"]["Level_6_Stationary_Transits_In_Vargas"]
        })

    # Sort years by alignment score descending
    yearly_evaluations.sort(key=lambda x: x["alignment_score"], reverse=True)

    base_chart = get_birth_chart(birth_year, birth_month, birth_day, birth_hour, birth_minute, birth_second,
                                 latitude, longitude, timezone, place_name)

    return {
        "native": {
            "birth_date": f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
            "birth_time": f"{birth_hour:02d}:{birth_minute:02d}:{birth_second:05.2f}",
            "place": place_name,
            "ayanamsa": "PUSHYA_PAKSHA",
            "d1_lagna": f"{base_chart['d1']['lagna']['rasi_name']} {base_chart['d1']['lagna']['deg_in_rasi']:.2f}°",
            "d10_lagna": f"{base_chart['vargas']['D10']['lagna']['rasi_name']} {base_chart['vargas']['D10']['lagna']['deg_in_rasi']:.2f}°",
            "d9_lagna": f"{base_chart['vargas']['D9']['lagna']['rasi_name']} {base_chart['vargas']['D9']['lagna']['deg_in_rasi']:.2f}°",
            "d24_lagna": f"{base_chart['vargas']['D24']['lagna']['rasi_name']} {base_chart['vargas']['D24']['lagna']['deg_in_rasi']:.2f}°",
        },
        "target_topic": target_topic,
        "most_aligned_years": yearly_evaluations[:3],
        "all_scanned_years": yearly_evaluations
    }

if __name__ == "__main__":
    # Example: Run for the native born 2001-10-06 at 16:59:07 IST in Ahmedabad
    print("\n" + "="*80)
    print("  PVR MULTI-METHOD CHAIN-OF-ASK PREDICTION: CAREER TIMING (2025 - 2030)")
    print("="*80)
    career = run_pvr_prediction(
        2001, 10, 6, 16, 59, 7.0, 23.0225, 72.5714, 5.5, "Ahmedabad",
        target_topic="career", scan_years=[2025, 2026, 2027, 2028, 2029, 2030]
    )
    print(f"Native: {career['native']['birth_date']} {career['native']['birth_time']} IST, {career['native']['place']}")
    print(f"Ayanamsa: {career['native']['ayanamsa']}")
    print(f"D-1 Lagna: {career['native']['d1_lagna']} | D-10 Lagna: {career['native']['d10_lagna']}")
    print("\nTop Career Window Matches:")
    for m in career["most_aligned_years"]:
        print(f"  * Year {m['year']} -> Alignment Score: {m['alignment_score']} / 100")
        print(f"    Verdict: {m['verdict']}")
        for r in m["reasons"]:
            print(f"      - {r}")

    print("\n" + "="*80)
    print("  PVR MULTI-METHOD CHAIN-OF-ASK PREDICTION: MARRIAGE TIMING (2026 - 2032)")
    print("="*80)
    marriage = run_pvr_prediction(
        2001, 10, 6, 16, 59, 7.0, 23.0225, 72.5714, 5.5, "Ahmedabad",
        target_topic="marriage", scan_years=[2026, 2027, 2028, 2029, 2030, 2031, 2032]
    )
    print("\nTop Marriage Window Matches:")
    for m in marriage["most_aligned_years"]:
        print(f"  * Year {m['year']} -> Alignment Score: {m['alignment_score']} / 100")
        print(f"    Verdict: {m['verdict']}")
        for r in m["reasons"]:
            print(f"      - {r}")
