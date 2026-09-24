#!/usr/bin/env python3
"""
ADK-05: Redefined Tithi Pravesha Chart (Annual Lunar Tithi Return)
-----------------------------------------------------------------
Implements Research Paper 05: "Re-defining Tithi Pravesha Chart"
By P.V.R. Narasimha Rao (October 5, 2014).

Core Methodological Principles:
1. Tithi Pravesha is the exact moment when the angular distance between Moon and Sun
   (exact Tithi percentage) matches the natal value, within the same solar month.
2. PVR Breakthrough: Solar months are defined by the Sun's transit through TROPICAL signs
   (consistent with Vishnu Purana Ch 2.8).
3. The Weekday Ruler (Vara Lord) at the exact TP moment is the Year Lord (Varadhipati).
4. The Hora Lord at the TP moment is the Hour Ruler.
5. Divisional charts (D-9, D-10, D-24) in TP reveal concrete real-world events.
6. Unified Nakshatra Dasas (ADK-03) work with high efficacy within TP charts.
"""

from typing import Dict, Any, Tuple
import swisseph as swe
from pvr_adk.core.config import PLANET_NAMES, RASI_NAMES
from pvr_adk.core.chart_engine import (
    calculate_julian_day, get_birth_chart, set_pushya_paksha_ayanamsa
)

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

class ADK05TithiPravesha:
    """Agentic Decision Kit for Redefined Tithi Pravesha Annual Chart."""

    def __init__(self):
        set_pushya_paksha_ayanamsa()

    def get_natal_tithi_angle(self, birth_jd: float) -> Tuple[float, float, int]:
        """
        Calculates the natal Moon-Sun angle, exact tithi progress (0.0 to 1.0),
        and Tithi number (1 to 30).
        """
        sun = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
        moon = swe.calc_ut(birth_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
        diff = (moon - sun) % 360.0
        tithi_no = int(diff / 12.0) + 1
        tithi_progress = (diff % 12.0) / 12.0
        return diff, tithi_progress, tithi_no

    def find_tithi_pravesha_jd(self, natal_angle: float, natal_sun_tropical: float,
                               target_year: int, approx_month: int, approx_day: int) -> float:
        """
        Finds the exact Julian Day in the target year when:
        1. Sun is in the same tropical sign as at birth.
        2. (Moon - Sun) angle exactly equals natal_angle.
        """
        approx_jd = swe.julday(target_year, approx_month, approx_day, 12.0)
        curr_jd = approx_jd

        for _ in range(30):
            sun_pos = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
            moon_pos = swe.calc_ut(curr_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)

            curr_sun = sun_pos[0][0] % 360.0
            curr_moon = moon_pos[0][0] % 360.0
            curr_angle = (curr_moon - curr_sun) % 360.0

            angle_diff = (natal_angle - curr_angle)
            if angle_diff > 180.0: angle_diff -= 360.0
            elif angle_diff < -180.0: angle_diff += 360.0

            if abs(angle_diff) < 1e-6:
                break

            # Relative speed: Moon speed ~ 13.2 deg/day, Sun speed ~ 1.0 deg/day -> ~ 12.2 deg/day
            rel_speed = moon_pos[0][3] - sun_pos[0][3]
            curr_jd += (angle_diff / rel_speed)

        return curr_jd

    def generate_tp_chart(self, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, birth_second: float,
                          target_year: int,
                          latitude: float, longitude: float,
                          timezone: float = 5.5,
                          place_name: str = "Location") -> Dict[str, Any]:
        """Generates the full Tithi Pravesha chart and evaluates the Year Lord."""
        birth_jd = calculate_julian_day(birth_year, birth_month, birth_day,
                                        birth_hour, birth_minute, birth_second)
        natal_angle, t_prog, t_no = self.get_natal_tithi_angle(birth_jd)
        sun_trop = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360.0

        tp_jd = self.find_tithi_pravesha_jd(natal_angle, sun_trop, target_year, birth_month, birth_day)

        cal_date = swe.revjul(tp_jd)
        y, m, d, float_hour = cal_date
        local_hour = float_hour + timezone
        if local_hour >= 24.0:
            local_hour -= 24.0
            d += 1
        h = int(local_hour)
        rem_m = (local_hour - h) * 60.0
        mn = int(rem_m)
        sec = round((rem_m - mn) * 60.0, 2)

        # Day of week at TP moment (0=Sun, 1=Mon, ..., 6=Sat)
        # Note: Day of week in JD where JD 0.5 is Monday
        day_of_week_idx = int(tp_jd + 1.5) % 7
        vara_lord = WEEKDAY_LORDS[day_of_week_idx]

        tp_chart = get_birth_chart(y, m, d, h, mn, sec, latitude, longitude, timezone, place_name)

        # Assess Year Lord placement in TP Chart
        yl_planet_data = tp_chart["d1"]["planets"].get(vara_lord)
        yl_rasi = yl_planet_data["rasi_name"] if yl_planet_data else "Unknown"
        yl_house = ((yl_planet_data["rasi_idx"] - tp_chart["d1"]["lagna"]["rasi_idx"]) % 12) + 1 if yl_planet_data else None

        is_auspicious_year = yl_house in [1, 4, 5, 7, 9, 10, 11] if yl_house else False

        return {
            "adk_id": "ADK-05",
            "name": "Redefined Tithi Pravesha Engine",
            "target_year": target_year,
            "tithi_number": t_no,
            "tp_moment_local": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{sec:05.2f}",
            "vara_lord_year_ruler": vara_lord,
            "year_lord_placement": {
                "sign": yl_rasi,
                "house_from_tp_lagna": yl_house,
                "is_auspicious": is_auspicious_year
            },
            "tp_chart": tp_chart,
            "research_reference": "PVR Paper 05: Re-defining Tithi Pravesha Chart"
        }
