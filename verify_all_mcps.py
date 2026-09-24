#!/usr/bin/env python3
"""
Master Verification Suite for PyJHora 6-MCP Server Architecture.
Executes and validates all tools across all 6 MCP servers against real chart data.
"""
import sys
import json
import time

# Import all 6 MCP servers
from mcp_panchanga_ephemeris import server as server1
from mcp_vargas_lagnas import server as server2
from mcp_strengths_ashtakavarga import server as server3
from mcp_dasha_engine import server as server4
from mcp_yogas_doshas import server as server5
from mcp_transits_annual_match import server as server6

def run_verification():
    print("=" * 80)
    print("  PYJHORA 6-MCP SERVER SUITE: END-TO-END VERIFICATION & BENCHMARK")
    print("=" * 80)
    
    # Test Chart 1: PVR Narasimha Rao Textbook Example (April 9, 2000, 17:55:00 EDT, Boston, MA)
    chart1 = {
        "year": 2000, "month": 4, "day": 9,
        "hour": 17, "minute": 55, "second": 0.0,
        "latitude": 42.3601, "longitude": -71.0589, "timezone_offset": -4.0,
        "place_name": "Boston, MA",
        "ayanamsa_mode": "LAHIRI",
        "divisional_chart_factor": 1,
        "target_year": 2026, "target_month": 9, "target_day": 23,
        "target_age_years": 24,
        "boy_nakshatra_number": 12, "boy_pada_number": 3,
        "girl_nakshatra_number": 15, "girl_pada_number": 1
    }
    
    servers = [
        ("MCP 1: Panchanga & Ephemeris", server1, [
            "get_panchanga_details",
            "get_inauspicious_periods",
            "get_auspicious_periods",
            "get_calendar_details",
            "get_planetary_ephemeris"
        ]),
        ("MCP 2: Divisional Charts, Lagnas & Arudhas", server2, [
            "get_divisional_chart",
            "get_varga_chart_detailed_vision",
            "get_all_divisional_charts_summary",
            "get_special_lagnas",
            "get_upagrahas",
            "get_arudha_padas",
            "get_argala_virodhargala",
            "get_planetary_aspects"
        ]),
        ("MCP 3: Planetary Strengths & Ashtakavarga", server3, [
            "get_shadbala_breakdown",
            "get_vimsopaka_and_vargeeya_bala",
            "get_bhava_bala",
            "get_ashtakavarga_matrices",
            "get_shodhaya_pindas_and_reductions"
        ]),
        ("MCP 4: Dasha & Timing Engine", server4, [
            "get_vimsottari_dasha",
            "get_nakshatra_dashas",
            "get_narayana_dasa",
            "get_chara_dasa",
            "get_kalachakra_dasa",
            "get_annual_dashas"
        ]),
        ("MCP 5: Vedic Yogas, Doshas & Sphutas", server5, [
            "detect_all_yogas",
            "detect_raja_yogas",
            "detect_doshas",
            "get_sphutas_and_sensitive_points"
        ]),
        ("MCP 6: Transits, Tajaka & Match Engine", server6, [
            "calculate_tajaka_varshaphal",
            "calculate_tajaka_sahams",
            "calculate_tajaka_yogas",
            "calculate_tithi_pravesha_chart_detailed_vision",
            "calculate_kundali_match",
            "calculate_longevity_estimates"
        ])
    ]
    
    total_tools = 0
    passed_tools = 0
    failed_tools = 0
    start_time = time.time()
    
    for s_name, s_obj, tool_list in servers:
        print(f"\n[{s_name}] ({len(tool_list)} tools registered)")
        for tool_name in tool_list:
            total_tools += 1
            try:
                t0 = time.time()
                res = s_obj.call_tool_direct(tool_name, chart1)
                elapsed_ms = (time.time() - t0) * 1000
                
                status = res.get("status")
                if status == "success":
                    passed_tools += 1
                    print(f"  ✓ {tool_name:<38} [OK] ({elapsed_ms:.1f}ms)")
                else:
                    failed_tools += 1
                    print(f"  ✗ {tool_name:<38} [FAILED: status={status}]")
            except Exception as e:
                failed_tools += 1
                print(f"  ✗ {tool_name:<38} [ERROR: {str(e)}]")
                
    total_elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"  VERIFICATION SUMMARY:")
    print(f"    Total MCP Servers: 6")
    print(f"    Total Tools Tested: {total_tools}")
    print(f"    Passed: {passed_tools} / {total_tools} (100.0%)" if failed_tools == 0 else f"    Passed: {passed_tools}, Failed: {failed_tools}")
    print(f"    Total Test Duration: {total_elapsed:.2f} seconds")
    print("=" * 80)
    
    if failed_tools > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_verification()
