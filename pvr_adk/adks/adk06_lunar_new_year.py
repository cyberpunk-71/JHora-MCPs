#!/usr/bin/env python3
"""
ADK-06: Redefined Lunar New Year Chart (Chaitra Sukla Pratipada)
---------------------------------------------------------------
Implements Research Paper 06: "Re-defining Lunar New Year Chart"
By P.V.R. Narasimha Rao (October 19, 2014).

Core Methodological Principles:
1. Lunar New Year occurs at the exact conjunction of Sun and Moon in sidereal Pisces
   (Chaitra Sukla Pratipada) using PUSHYA-PAKSHA AYANAMSA.
2. The chart MUST be cast for the capital city of the nation under consideration
   (e.g., New Delhi for India, Washington D.C. for USA).
3. The Weekday Lord (Vara Lord) at the exact conjunction moment becomes King of the year.
4. The placement and relationships of the King and divisional charts (especially D-1, D-10)
   reveal political, financial, and national developments for the year.
"""

from typing import Dict, Any, Tuple
import swisseph as swe
from pvr_adk.core.config import PLANET_NAMES
from pvr_adk.core.chart_engine import get_birth_chart, set_pushya_paksha_ayanamsa

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

CAPITALS = {
    "India": {"lat": 28.6139, "lon": 77.2090, "tz": 5.5, "name": "New Delhi"},
    "USA": {"lat": 38.9072, "lon": -77.0369, "tz": -5.0, "name": "Washington D.C."},
    "UK": {"lat": 51.5074, "lon": -0.1278, "tz": 0.0, "name": "London"}
}

class ADK06LunarNewYear:
    """Agentic Decision Kit for Mundane and National Predictions."""

    def __init__(self):
        set_pushya_paksha_ayanamsa()

    def find_chaitra_pratipada_jd(self, year: int) -> float:
        """
        Finds the exact conjunction of Sun and Moon (0° angle) in March/April of the year.
        """
        approx_jd = swe.julday(year, 3, 25, 12.0)
        curr_jd = approx_jd

        for _ in range(30):
            sun = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
            moon = swe.calc_ut(curr_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)

            diff = (moon[0][0] - sun[0][0]) % 360.0
            if diff > 180.0: diff -= 360.0

            if abs(diff) < 1e-6:
                break

            rel_speed = moon[0][3] - sun[0][3]
            curr_jd -= (diff / rel_speed)

        return curr_jd

    def generate_national_chart(self, year: int, country: str = "India") -> Dict[str, Any]:
        """Generates the Lunar New Year chart for a specific country."""
        cap = CAPITALS.get(country, CAPITALS["India"])
        new_moon_jd = self.find_chaitra_pratipada_jd(year)

        cal_date = swe.revjul(new_moon_jd)
        y, m, d, float_h = cal_date
        local_h = float_h + cap["tz"]
        if local_h >= 24.0:
            local_h -= 24.0
            d += 1
        h = int(local_h)
        rem_m = (local_h - h) * 60.0
        mn = int(rem_m)
        sec = round((rem_m - mn) * 60.0, 2)

        day_of_week = int(new_moon_jd + 1.5) % 7
        king_of_year = WEEKDAY_LORDS[day_of_week]

        chart = get_birth_chart(y, m, d, h, mn, sec, cap["lat"], cap["lon"], cap["tz"], cap["name"])

        return {
            "adk_id": "ADK-06",
            "name": "Redefined Lunar New Year (Chaitra Pratipada) Engine",
            "country": country,
            "capital": cap["name"],
            "year": year,
            "new_moon_utc_jd": new_moon_jd,
            "conjunction_local": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{sec:05.2f}",
            "king_of_year": king_of_year,
            "national_chart": chart,
            "research_reference": "PVR Paper 06: Re-defining Lunar New Year Chart"
        }
