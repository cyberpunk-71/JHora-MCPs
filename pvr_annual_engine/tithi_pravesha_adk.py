"""
ADK-05: Redefined Tithi Pravesha (Annual Soli-Lunar Return Engine)
=================================================================
Implements Research Paper 05: "Re-defining Tithi Pravesha Chart"
By P.V.R. Narasimha Rao.

Key Principles:
  1. Soli-Lunar Month Definition: Preceding New Moon tropical Sun sign (Vishnu Purana 2.8).
  2. Exact Tithi Angle Return: Same (Moon - Sun) angle in the target year.
  3. Year Lord (Varadhipati): Weekday lord at the TP return moment.
  4. Reformed Divisional Charts under Pushya-Paksha Ayanamsa.
"""

from typing import Dict, Any, List, Tuple
import swisseph as swe
from pvr_annual_engine.config import (
    AYANAMSA_ID, RASI_NAMES, PLANET_NAMES, WEEKDAY_LORDS, SIGN_LORDS
)
from pvr_annual_engine.chart_solver import (
    calculate_julian_day_ut, get_natal_tithi_angle, solve_tithi_pravesha_jd_ut,
    compute_sidereal_positions_and_lagna
)
from pvr_annual_engine.divisional_engine import build_varga_chart

class ADK05TithiPravesha:
    """Agentic Decision Kit for Redefined Tithi Pravesha Annual Chart."""

    def generate_tp_chart(self, birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int, birth_second: float,
                          target_year: int,
                          latitude: float, longitude: float,
                          timezone: float = 5.5) -> Dict[str, Any]:
        """
        Generates complete Tithi Pravesha chart, evaluates the Year Lord and Vargas.
        """
        birth_jd_ut = calculate_julian_day_ut(birth_year, birth_month, birth_day,
                                              birth_hour, birth_minute, birth_second, timezone)
        tp_jd_ut = solve_tithi_pravesha_jd_ut(birth_jd_ut, target_year)
        natal_angle, t_prog, t_no = get_natal_tithi_angle(birth_jd_ut)

        cal_date = swe.revjul(tp_jd_ut)
        y, m, d, float_hour = cal_date
        local_h = float_hour + timezone
        if local_h >= 24.0:
            local_h -= 24.0
            d += 1
        h = int(local_h)
        mn = int((local_h - h) * 60.0)
        sec = round(((local_h - h) * 60.0 - mn) * 60.0, 2)

        # Day of week at TP moment (0=Sun, 1=Mon, ..., 6=Sat)
        day_of_week_idx = int(tp_jd_ut + (timezone / 24.0) + 1.5) % 7
        vara_lord = WEEKDAY_LORDS[day_of_week_idx]

        # TP Sidereal Positions
        tp_lagna_deg, tp_planets_d1 = compute_sidereal_positions_and_lagna(tp_jd_ut, latitude, longitude)
        tp_lagna_sign = int(tp_lagna_deg // 30.0)

        # Build Vargas
        d1_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 1)
        d4_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 4)
        d7_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 7)
        d9_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 9)
        d10_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 10)
        d24_chart = build_varga_chart(tp_lagna_deg, tp_planets_d1, 24)

        # Year Lord evaluation in D-1
        yl_tot_deg = tp_planets_d1[vara_lord][0]
        yl_sign = int(yl_tot_deg // 30.0)
        yl_house = ((yl_sign - tp_lagna_sign) % 12) + 1

        is_auspicious = yl_house in [1, 4, 5, 7, 9, 10, 11]

        return {
            "adk_id": "ADK-05",
            "name": "Redefined Tithi Pravesha Engine",
            "target_year": target_year,
            "tithi_number": t_no,
            "tp_moment_utc_jd": tp_jd_ut,
            "tp_moment_local": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{sec:05.2f}",
            "vara_lord_year_ruler": vara_lord,
            "year_lord_placement": {
                "sign": RASI_NAMES[yl_sign],
                "house_from_tp_lagna": yl_house,
                "is_auspicious": is_auspicious,
                "role_summary": f"Vara Lord {vara_lord} rules the year, positioned in house {yl_house} ({RASI_NAMES[yl_sign]})."
            },
            "charts": {
                "D1": d1_chart,
                "D4": d4_chart,
                "D7": d7_chart,
                "D9": d9_chart,
                "D10": d10_chart,
                "D24": d24_chart
            }
        }
