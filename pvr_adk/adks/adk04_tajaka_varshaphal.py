#!/usr/bin/env python3
"""
ADK-04: Redefined Tajaka Varshaphal (Annual Tropical Solar Return)
-----------------------------------------------------------------
Implements Research Paper 04: "Re-defining Tajaka Varshaphal Charts"
By P.V.R. Narasimha Rao (June 15, 2014).

Core Methodological Innovation:
1. Classical Mistake: Astrologers use sidereal solar return (365.256 days).
2. PVR Breakthrough: Vishnu Purana (Ch 2.8) proves solar years are seasonal (tropical).
   The Tajaka Varshaphal chart MUST be cast when the Sun returns to his EXACT NATAL
   TROPICAL LONGITUDE (mean tropical year = 365.242 days).
3. At that exact tropical moment, all planetary positions are computed using
   PUSHYA-PAKSHA AYANAMSA and reformed divisional charts (D-10 method 3, D-24 method 2).
4. The annual chart is judged using standard Parasara principles across Rasi and Vargas.
"""

from typing import Dict, Any, Tuple
import swisseph as swe
from pvr_adk.core.config import AYANAMSA_ID, SOLAR_RETURN_TYPE
from pvr_adk.core.chart_engine import (
    calculate_julian_day, get_birth_chart, set_pushya_paksha_ayanamsa
)

class ADK04TajakaVarshaphal:
    """Agentic Decision Kit for Redefined Tropical Solar Return Varshaphal."""

    def __init__(self):
        set_pushya_paksha_ayanamsa()

    def get_natal_sun_tropical(self, birth_jd: float) -> float:
        """Returns the natal tropical longitude of the Sun."""
        res = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)
        return res[0][0] % 360.0

    def find_annual_solar_return_jd(self, natal_sun_tropical: float, target_year: int,
                                     birth_month: int, birth_day: int) -> float:
        """
        Finds the exact Julian Day when the Sun reaches the exact natal tropical longitude
        in the target year using high-precision Newton-Raphson / binary search.
        """
        approx_jd = swe.julday(target_year, birth_month, birth_day, 12.0)
        curr_jd = approx_jd

        for _ in range(25):
            sun_pos = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
            curr_long = sun_pos[0][0] % 360.0
            sun_speed = sun_pos[0][3] if sun_pos[0][3] != 0.0 else 0.9856  # degrees per day

            diff = (natal_sun_tropical - curr_long)
            if diff > 180.0: diff -= 360.0
            elif diff < -180.0: diff += 360.0

            if abs(diff) < 1e-7:  # sub-arcsecond precision
                break

            curr_jd += (diff / sun_speed)

        return curr_jd

    def generate_varshaphal_chart(self, birth_year: int, birth_month: int, birth_day: int,
                                  birth_hour: int, birth_minute: int, birth_second: float,
                                  target_year: int,
                                  latitude: float, longitude: float,
                                  timezone: float = 5.5,
                                  place_name: str = "Location") -> Dict[str, Any]:
        """
        Generates complete annual Varshaphal chart for the target year.
        """
        birth_jd = calculate_julian_day(birth_year, birth_month, birth_day,
                                        birth_hour, birth_minute, birth_second)
        sun_trop = self.get_natal_sun_tropical(birth_jd)
        return_jd = self.find_annual_solar_return_jd(sun_trop, target_year, birth_month, birth_day)

        # Convert return_jd back to Gregorian date and time
        cal_date = swe.revjul(return_jd)
        y, m, d, float_hour = cal_date
        # Adjust UTC to local time
        local_hour_float = float_hour + timezone
        if local_hour_float >= 24.0:
            local_hour_float -= 24.0
            d += 1  # approximate day increment
        h = int(local_hour_float)
        rem_m = (local_hour_float - h) * 60.0
        mn = int(rem_m)
        sec = round((rem_m - mn) * 60.0, 2)

        # Generate complete Pushya-Paksha chart for the return moment
        annual_chart = get_birth_chart(y, m, d, h, mn, sec, latitude, longitude, timezone, place_name)

        return {
            "adk_id": "ADK-04",
            "name": "Redefined Tajaka Varshaphal (Tropical Solar Return)",
            "solar_return_type": SOLAR_RETURN_TYPE,
            "target_year": target_year,
            "natal_sun_tropical_degree": sun_trop,
            "return_moment_utc_jd": return_jd,
            "return_moment_local": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{sec:05.2f}",
            "annual_chart": annual_chart,
            "research_reference": "PVR Paper 04: Re-defining Tajaka Varshaphal Charts"
        }
