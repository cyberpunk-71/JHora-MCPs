#!/usr/bin/env python3
"""
ADK-07: Transits and Nakshatra Dasa Progression
-----------------------------------------------
Implements Research Paper 07: "Transits and Nakshatra Dasa Progression"
By P.V.R. Narasimha Rao (December 20, 2014).

Core Methodological Principles:
1. Dynamic Progression: Dasa lord does not just govern a period abstractly;
   its planetary ray progresses proportionally across the zodiac during its Mahadasa span.
2. Transit Activation: Transits of slow-moving planets (Jupiter, Saturn, Rahu)
   over or aspecting the progressed dasa point trigger the fruition of the dasa promise.
3. Conjunction with natal sensitive points (Lagna, Karaka, House Lords) during the transit
   marks the exact month and week of event manifestation.
"""

from typing import Dict, Any, List
import swisseph as swe
from pvr_adk.core.config import PLANET_NAMES, RASI_NAMES
from pvr_adk.core.chart_engine import set_pushya_paksha_ayanamsa

class ADK07DasaProgression:
    """Agentic Decision Kit for Dynamic Dasa Progression & Transit Synchronization."""

    def __init__(self):
        set_pushya_paksha_ayanamsa()

    def calculate_progressed_dasa_point(self, dasa_lord_natal_deg: float,
                                         dasa_start_jd: float, dasa_end_jd: float,
                                         current_jd: float, total_progression_arc: float = 360.0) -> float:
        """
        Calculates the progressed longitude of the Dasa lord on a given date.
        """
        if current_jd < dasa_start_jd or current_jd > dasa_end_jd:
            return dasa_lord_natal_deg

        fraction = (current_jd - dasa_start_jd) / (dasa_end_jd - dasa_start_jd)
        progressed_deg = (dasa_lord_natal_deg + fraction * total_progression_arc) % 360.0
        return progressed_deg

    def evaluate_transit_trigger(self, progressed_deg: float, transit_jd: float,
                                  trigger_planets: List[str] = ["Jupiter", "Saturn"]) -> Dict[str, Any]:
        """
        Checks whether transit planets are conjoining or closely aspecting the progressed point.
        """
        set_pushya_paksha_ayanamsa()
        swe_map = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Mars": swe.MARS}
        hits = []

        for p_name in trigger_planets:
            p_id = swe_map.get(p_name)
            if p_id is None: continue
            pos = swe.calc_ut(transit_jd, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
            t_long = pos[0][0] % 360.0

            # Direct conjunction check
            diff = abs(t_long - progressed_deg)
            if diff > 180.0: diff = 360.0 - diff

            if diff <= 3.5:  # within 3.5 degrees
                hits.append({
                    "transit_planet": p_name,
                    "transit_longitude": round(t_long, 2),
                    "aspect_type": "Conjunction",
                    "orb_degrees": round(diff, 2),
                    "is_active_trigger": True
                })

            # Check 7th house aspect
            opp_diff = abs((t_long + 180.0) % 360.0 - progressed_deg)
            if opp_diff > 180.0: opp_diff = 360.0 - opp_diff
            if opp_diff <= 3.5:
                hits.append({
                    "transit_planet": p_name,
                    "transit_longitude": round(t_long, 2),
                    "aspect_type": "Opposition (7th aspect)",
                    "orb_degrees": round(opp_diff, 2),
                    "is_active_trigger": True
                })

        return {
            "adk_id": "ADK-07",
            "name": "Dasa Progression & Transit Trigger",
            "progressed_degree": round(progressed_deg, 2),
            "progressed_rasi": RASI_NAMES[int(progressed_deg // 30)],
            "transit_triggers": hits,
            "has_activation": len(hits) > 0,
            "research_reference": "PVR Paper 07: Transits and Nakshatra Dasa Progression"
        }
