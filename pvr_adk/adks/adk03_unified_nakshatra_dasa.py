#!/usr/bin/env python3
"""
ADK-03: Unified Nakshatra Dasa Approach
---------------------------------------
Implements Research Paper 03: "Unified Nakshatra Dasa Approach: In Annual & Natal Charts"
By P.V.R. Narasimha Rao (January 7, 2014).

Core Methodological Innovation:
1. Parasara's conditional dasa conditions are NECESSARY but NOT SUFFICIENT.
2. In many charts satisfying the condition, Vimsottari still dominates.
3. A conditional dasa overrides Vimsottari ONLY when its CONTROLLING PLANET is strong
   and prominent (in kendra/trikona, exalted, moolatrikona, or aspecting lagna).
4. Table of Controlling Planets:
   - Shodasottari (116y) -> Jupiter (Pushya seed)
   - Dwadasottari (112y) -> Ketu (Revati seed, anti-zodiacal)
   - Ashtottari (108y)   -> Mars (Ardra seed)
   - Panchottari (105y)  -> Venus (Anuradha seed)
   - Satabdika (100y)    -> Sun (Revati seed, zodiacal)
   - Chaturaaseeti (84y) -> Saturn (Swati seed)
   - Dwisaptati (72y)    -> Rahu (Moola seed)
   - Shashtisama (60y)   -> Moon (Ashwini seed)
   - Shattrimsa (36y)    -> Mercury (Shravana seed)
   - Vimsottari (120y)   -> Default Supreme Ruler
"""

from typing import Dict, Any, List, Optional
from pvr_adk.core.config import CONDITIONAL_DASA_SPECS, PLANET_NAMES, RASI_NAMES
from pvr_adk.core.chart_engine import get_house_of_planet

class ADK03UnifiedNakshatraDasa:
    """Agentic Decision Kit for Unified Nakshatra Dasa Selection & Evaluation."""

    def __init__(self):
        self.specs = CONDITIONAL_DASA_SPECS

    def evaluate_applicable_dasas(self, chart_data: Dict[str, Any], is_annual_tp: bool = False) -> Dict[str, Any]:
        """
        Evaluates which conditional nakshatra dasas satisfy Parasara's conditions,
        checks the strength of their controlling planets, and selects the SINGLE
        best dasa to use.
        """
        d1 = chart_data["d1"]
        vargas = chart_data.get("vargas", {})
        d9 = vargas.get("D9", {})
        d12 = vargas.get("D12", {})
        planets = d1["planets"]
        lagna = d1["lagna"]

        sun = planets["Sun"]
        moon = planets["Moon"]
        rahu = planets["Rahu"]

        # Paksha check: Sun-Moon longitude difference
        diff_deg = (moon["total_deg"] - sun["total_deg"]) % 360.0
        is_sukla = diff_deg < 180.0
        tithi_no = int(diff_deg / 12.0) + 1

        # Hora check: Sun hora / Moon hora
        # In a sign, 0-15° in odd signs is Sun hora, 15-30° is Moon hora (reversed in even)
        is_odd_sign = lagna["rasi_idx"] % 2 == 0  # 0-indexed: 0=Aries (odd)
        if is_odd_sign:
            lagna_in_sun_hora = lagna["deg_in_rasi"] < 15.0
        else:
            lagna_in_sun_hora = lagna["deg_in_rasi"] >= 15.0
        lagna_in_moon_hora = not lagna_in_sun_hora

        # Check conditions
        applicable = []

        # 1. Shodasottari (116)
        if (is_sukla and lagna_in_sun_hora) or (not is_sukla and lagna_in_moon_hora):
            applicable.append("Shodasottari")

        # 2. Dwadasottari (112) - Lagna in Taurus (1) or Libra (6) navamsa
        if d9:
            d9_lagna_rasi = d9["lagna"]["rasi_idx"]
            if d9_lagna_rasi in [1, 6]:
                applicable.append("Dwadasottari")

        # 3. Ashtottari (108) - Rahu in kendra/trikona from lagna lord, not in lagna
        # Lagna lord
        lagna_lords = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]  # Aries=Mars...
        lagna_lord_id = lagna_lords[lagna["rasi_idx"]]
        lagna_lord_name = PLANET_NAMES[lagna_lord_id]
        ll_rasi = planets[lagna_lord_name]["rasi_idx"]
        rahu_house_from_ll = ((rahu["rasi_idx"] - ll_rasi) % 12) + 1
        rahu_house_from_lagna = get_house_of_planet(rahu["rasi_idx"], lagna["rasi_idx"])
        if (rahu_house_from_ll in [1, 4, 7, 10, 5, 9]) and (rahu_house_from_lagna != 1):
            applicable.append("Ashtottari")

        # 4. Panchottari (105) - Lagna in Cancer (3) dwadasamsa
        if d12:
            d12_lagna_rasi = d12["lagna"]["rasi_idx"]
            if d12_lagna_rasi == 3:
                applicable.append("Panchottari")

        # 5. Satabdika (100) - Vargottama Lagna
        if d9:
            if d9["lagna"]["rasi_idx"] == lagna["rasi_idx"]:
                applicable.append("Satabdika")

        # 6. Chaturaaseeti (84) - 10th lord in 10th
        tenth_rasi = (lagna["rasi_idx"] + 9) % 12
        tenth_lord_id = lagna_lords[tenth_rasi]
        tenth_lord_name = PLANET_NAMES[tenth_lord_id]
        if planets[tenth_lord_name]["rasi_idx"] == tenth_rasi:
            applicable.append("Chaturaaseeti")

        # 7. Dwisaptati (72) - Lagna lord in 7th OR 7th lord in lagna
        seventh_rasi = (lagna["rasi_idx"] + 6) % 12
        seventh_lord_id = lagna_lords[seventh_rasi]
        seventh_lord_name = PLANET_NAMES[seventh_lord_id]
        if (planets[lagna_lord_name]["rasi_idx"] == seventh_rasi) or (planets[seventh_lord_name]["rasi_idx"] == lagna["rasi_idx"]):
            applicable.append("Dwisaptati")

        # 8. Shashtisama (60) - Sun in Lagna
        if planets["Sun"]["rasi_idx"] == lagna["rasi_idx"]:
            applicable.append("Shashtisama")

        # 9. Shattrimsa (36) - Daytime: Sun hora; Nighttime: Moon hora
        # Daytime approx: Sun in houses 7 to 12
        sun_house = get_house_of_planet(sun["rasi_idx"], lagna["rasi_idx"])
        is_daytime = sun_house in [7, 8, 9, 10, 11, 12]
        if (is_daytime and lagna_in_sun_hora) or (not is_daytime and lagna_in_moon_hora):
            applicable.append("Shattrimsa")

        # Controlling Planet Evaluation
        evaluation = []
        best_candidate = "Vimsottari"
        highest_score = 0.0

        for dasa_name in applicable:
            ctrl_planet = self.specs[dasa_name]["controlling_planet"]
            # Score controlling planet strength
            score = self._score_planet_prominence(planets.get(ctrl_planet), lagna["rasi_idx"])
            evaluation.append({
                "dasa": dasa_name,
                "span_years": self.specs[dasa_name]["span_years"],
                "controlling_planet": ctrl_planet,
                "controlling_planet_score": score,
                "qualifies_override": score >= 5.0
            })
            if score > highest_score and score >= 5.0:
                highest_score = score
                best_candidate = dasa_name

        # In Annual Tithi Pravesha charts, PVR notes conditional dasas dominate heavily
        if is_annual_tp and applicable and highest_score >= 3.0:
            best_candidate = max(evaluation, key=lambda x: x["controlling_planet_score"])["dasa"]

        return {
            "adk_id": "ADK-03",
            "name": "Unified Nakshatra Dasa Engine",
            "is_annual_tp": is_annual_tp,
            "applicable_conditional_dasas": applicable,
            "controlling_planet_evaluations": evaluation,
            "selected_best_dasa": best_candidate,
            "selection_rationale": (
                f"Selected {best_candidate} because its controlling planet dominates."
                if best_candidate != "Vimsottari"
                else "No conditional dasa controlling planet sufficiently strong; Vimsottari dominates as supreme ruler."
            ),
            "research_reference": "PVR Paper 03: Unified Nakshatra Dasa Approach"
        }

    def _score_planet_prominence(self, planet_data: Optional[Dict[str, Any]], lagna_rasi: int) -> float:
        if not planet_data: return 0.0
        score = 0.0
        p_rasi = planet_data["rasi_idx"]
        house = get_house_of_planet(p_rasi, lagna_rasi)

        # Kendra (1, 4, 7, 10): +3
        if house in [1, 4, 7, 10]: score += 3.0
        # Trikona (5, 9): +2.5
        elif house in [5, 9]: score += 2.5
        # 11th house: +2
        elif house == 11: score += 2.0
        # Dusthana (6, 8, 12): -1.5
        elif house in [6, 8, 12]: score -= 1.5

        return max(score, 0.0)
