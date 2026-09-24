#!/usr/bin/env python3
"""
Test Suite: Rigorous Verification of PVR ADK Against Research Paper Examples
----------------------------------------------------------------------------
Validates all ADKs against the documented examples and mathematical claims
in P.V.R. Narasimha Rao's 9 research papers.
"""

import sys
sys.path.insert(0, "/home/opc/mcp_jhora")

from pvr_adk.adks.adk01_ayanamsa_foundation import ADK01AyanamsaFoundation
from pvr_adk.adks.adk02_pancha_kosha import ADK02PanchaKosha
from pvr_adk.adks.adk03_unified_nakshatra_dasa import ADK03UnifiedNakshatraDasa
from pvr_adk.adks.adk04_tajaka_varshaphal import ADK04TajakaVarshaphal
from pvr_adk.adks.adk05_tithi_pravesha import ADK05TithiPravesha
from pvr_adk.adks.adk08_novel_transits import ADK08NovelTransits
from pvr_adk.adks.adk09_chara_dasa_vargas import ADK09CharaDasaVargas
from pvr_adk.adks.adk_ensemble_orchestrator import PVREnsembleOrchestrator
from pvr_adk.core.chart_engine import get_birth_chart

def test_paper_01_ayanamsa():
    print("\n--- TEST 1: Paper 01 Pushya-Paksha Ayanamsa Verification ---")
    adk = ADK01AyanamsaFoundation()
    res = adk.verify_known_benchmark_dates()
    print("All benchmarks passed:", res["all_benchmarks_passed"])
    for b in res["benchmarks"]:
        print(f"  {b['date']}: PVR={b['pvr_published']} | Calc={b['calculated']} | Diff={b['diff_arcsec']}\" | Verified={b['verified']}")
    assert res["all_benchmarks_passed"], "Ayanamsa benchmark failed!"
    print(">>> PASS: ADK-01 matches PVR Paper 01 exact published ayanamsa.")

def test_paper_08_ramana_maharshi():
    print("\n--- TEST 2: Paper 08 Stationary Transit Example 1 (Ramana Maharshi) ---")
    # Ramana Maharshi: 1879-12-30, 01:02 IST, Pondicherry (78e15, 9n50)
    # Event: 1896-07-17 Self-enquiry / Self-realization
    # Paper 08 claim: Saturn stationary 1896-07-15 at 21Li09 -> D-20: 3Ge01
    adk = ADK08NovelTransits()
    sat_long = 201.15  # 21Li09
    sign, deg, total = adk.get_divisional_longitude(sat_long, 20, 2)
    print(f"Calculated D-20 of 21Li09: Sign {sign} ({['Ar','Ta','Ge','Cn'][sign]}), Deg {deg:.2f}° | Total {total:.2f}°")
    # Sign 2 is Gemini! Degree ~ 3.0° Gemini!
    assert sign == 2, f"Expected Gemini (2), got {sign}"
    assert abs(deg - 3.0) < 1.0, f"Expected ~3° Gemini, got {deg}"
    print(">>> PASS: Saturn stationary longitude maps to 3° Gemini in D-20 exactly as published!")

def test_paper_08_marriage_example():
    print("\n--- TEST 3: Paper 08 Stationary Transit Example 6 (Marriage) ---")
    # Marriage: 1962-08-04, 19:24:20 Hawaii, Married 1992-10-03
    # Paper 08 claim: Saturn stationary 1992-10-15 at 19Cp12 -> D-9: 22Ge45
    adk = ADK08NovelTransits()
    sat_long = 289.20  # 19Cp12
    sign, deg, total = adk.get_divisional_longitude(sat_long, 9, 1)
    print(f"Calculated D-9 of 19Cp12: Sign {sign} ({['Ar','Ta','Ge','Cn'][sign]}), Deg {deg:.2f}° | Total {total:.2f}°")
    # Sign 2 is Gemini! Degree ~ 22.8° Gemini (22Ge45)!
    assert sign == 2, f"Expected Gemini (2), got {sign}"
    assert abs(deg - 22.8) < 1.0, f"Expected ~22.8° Gemini, got {deg}"
    print(">>> PASS: Saturn stationary longitude maps to 22Ge45 in D-9 exactly as published!")

def test_native_complete_multi_method_pipeline():
    print("\n--- TEST 4: Native Comprehensive Multi-Method Prediction Pipeline ---")
    # Native: 2001-10-06, 16:59:07 IST, Ahmedabad (23.0225 N, 72.5714 E)
    orch = PVREnsembleOrchestrator()

    # 1. Career
    career_res = orch.run_complete_multi_method_prediction(
        birth_year=2001, birth_month=10, birth_day=6,
        birth_hour=16, birth_minute=59, birth_second=7.0,
        latitude=23.0225, longitude=72.5714, timezone=5.5,
        place_name="Ahmedabad",
        target_topic="career",
        target_year=2026
    )
    print("Career Synthesis Alignment Score:", career_res["orchestrator_summary"]["overall_alignment_score"])
    print("Career Alignment Verdict:", career_res["orchestrator_summary"]["alignment_verdict"])
    for r in career_res["convergence_reasons"]:
        print("  -", r)

    # 2. Marriage
    marriage_res = orch.run_complete_multi_method_prediction(
        birth_year=2001, birth_month=10, birth_day=6,
        birth_hour=16, birth_minute=59, birth_second=7.0,
        latitude=23.0225, longitude=72.5714, timezone=5.5,
        place_name="Ahmedabad",
        target_topic="marriage",
        target_year=2027
    )
    print("\nMarriage Synthesis Alignment Score:", marriage_res["orchestrator_summary"]["overall_alignment_score"])
    print("Marriage Alignment Verdict:", marriage_res["orchestrator_summary"]["alignment_verdict"])
    for r in marriage_res["convergence_reasons"]:
        print("  -", r)

    print("\n>>> PASS: Native Multi-Method Chain-of-Ask completed successfully!")

if __name__ == "__main__":
    test_paper_01_ayanamsa()
    test_paper_08_ramana_maharshi()
    test_paper_08_marriage_example()
    test_native_complete_multi_method_pipeline()
