#!/usr/bin/env python3
"""
ADK-05: Redefined Tithi Pravesha Chart (Annual Lunar Tithi Return)
-----------------------------------------------------------------
Implements Research Paper 05: "Re-defining Tithi Pravesha Chart"
By P.V.R. Narasimha Rao (October 5, 2014).

Core Methodological Principles:
1. Soli-Lunar Month Definition:
   - PVR Discovery: A soli-lunar month is seeded by the New Moon (Sun-Moon conjunction)
     and categorized by the Sun's TROPICAL SIGN at that New Moon moment (Vishnu Purana 2.8).
2. Tithi Return:
   - In the target year, find the New Moon where the tropical Sun occupies the SAME sign
     as at the birth New Moon.
   - Advance until the exact (Moon - Sun) angular distance equals the natal tithi angle.
3. Year Lord (Varadhipati):
   - The Weekday Lord (Vara Lord) at the exact moment of Tithi Pravesha rules the year.
   - Placement in Kendra/Trikona or with benefics brings auspicious fruition of the year.
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

    def get_preceding_new_moon_ut(self, jd_ut: float) -> Tuple[float, float, int]:
        """
        Finds the exact Julian Day (UT) of the New Moon immediately preceding jd_ut,
        and returns (nm_jd_ut, sun_tropical_longitude, sun_tropical_sign).
        """
        s = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
        m = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH)[0][0]
        angle = (m - s) % 360.0
        approx_nm = jd_ut - (angle / 12.1907)
        curr = approx_nm

        for _ in range(25):
            s_pos = swe.calc_ut(curr, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
            m_pos = swe.calc_ut(curr, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
            diff = (m_pos[0][0] - s_pos[0][0]) % 360.0
            if diff > 180.0: diff -= 360.0
            if abs(diff) < 1e-6: break
            curr -= (diff / (m_pos[0][3] - s_pos[0][3]))

        sun_trop = swe.calc_ut(curr, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360.0
        return curr, sun_trop, int(sun_trop // 30.0)

    def find_target_year_new_moon_ut(self, target_year: int, target_tropical_sign: int) -> float:
        """
        Finds the New Moon in the target year where the Sun is in target_tropical_sign.
        """
        # Middle of target sign corresponds approximately to target_tropical_sign * 30 + 15
        # Aries (0) starts March 21 (day 80). Each sign ~ 30.4 days.
        approx_day_of_year = 80 + target_tropical_sign * 30.43
        if approx_day_of_year > 365:
            approx_day_of_year -= 365
        approx_month = int(approx_day_of_year // 30.43) + 1
        approx_day = int(approx_day_of_year % 30.43) + 1
        approx_jd = swe.julday(target_year, max(1, min(12, approx_month)), max(1, min(28, approx_day)), 12.0)

        # Find closest New Moon
        nm_jd, _, nm_sign = self.get_preceding_new_moon_ut(approx_jd)

        # Adjust by lunar months if sign doesn't match
        if nm_sign != target_tropical_sign:
            diff_signs = (target_tropical_sign - nm_sign) % 12
            if diff_signs <= 6:
                nm_jd += (diff_signs * 29.530588)
            else:
                nm_jd -= ((12 - diff_signs) * 29.530588)
            nm_jd, _, nm_sign = self.get_preceding_new_moon_ut(nm_jd + 5.0)

        return nm_jd

    def get_natal_tithi_angle(self, birth_jd_ut: float) -> Tuple[float, float, int]:
        sun = swe.calc_ut(birth_jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
        moon = swe.calc_ut(birth_jd_ut, swe.MOON, swe.FLG_SWIEPH)[0][0]
        diff = (moon - sun) % 360.0
        tithi_no = int(diff / 12.0) + 1
        tithi_progress = (diff % 12.0) / 12.0
        return diff, tithi_progress, tithi_no

    def find_tithi_pravesha_jd_ut(self, birth_jd_ut: float, target_year: int) -> float:
        """
        Finds exact Julian Day (UT) of Tithi Pravesha return in target_year.
        """
        natal_angle, _, _ = self.get_natal_tithi_angle(birth_jd_ut)
        _, _, birth_nm_sign = self.get_preceding_new_moon_ut(birth_jd_ut)

        # 1. Find the New Moon in target year with the same tropical sign
        target_nm_ut = self.find_target_year_new_moon_ut(target_year, birth_nm_sign)

        # 2. Advance from that New Moon until (Moon - Sun) angle equals natal_angle
        curr_ret = target_nm_ut + (natal_angle / 12.1907)
        for _ in range(25):
            s_pos = swe.calc_ut(curr_ret, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
            m_pos = swe.calc_ut(curr_ret, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
            diff = (m_pos[0][0] - s_pos[0][0]) % 360.0
            err = (natal_angle - diff)
            if err > 180.0: err -= 360.0
            elif err < -180.0: err += 360.0
            if abs(err) < 1e-6: break
            curr_ret += (err / (m_pos[0][3] - s_pos[0][3]))

        return curr_ret

    def generate_tp_chart(self, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, birth_second: float,
                          target_year: int,
                          latitude: float, longitude: float,
                          timezone: float = 5.5,
                          place_name: str = "Location") -> Dict[str, Any]:
        """Generates the full Tithi Pravesha chart and evaluates the Year Lord."""
        birth_jd_local = calculate_julian_day(birth_year, birth_month, birth_day,
                                              birth_hour, birth_minute, birth_second)
        birth_jd_ut = birth_jd_local - (timezone / 24.0)

        tp_jd_ut = self.find_tithi_pravesha_jd_ut(birth_jd_ut, target_year)
        natal_angle, t_prog, t_no = self.get_natal_tithi_angle(birth_jd_ut)

        cal_date = swe.revjul(tp_jd_ut)
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
        day_of_week_idx = int(tp_jd_ut + timezone / 24.0 + 1.5) % 7
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
